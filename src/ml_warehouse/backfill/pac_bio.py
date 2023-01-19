# -*- coding: utf-8 -*-
#
# Copyright © 2023 Genome Research Ltd. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# @author Michael Kubiak <mk35@sanger.ac.uk>

from datetime import datetime
from typing import List

import structlog
from npg_id_generation.pac_bio import PacBioEntity
from sqlalchemy import Column, select, update, bindparam, join
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from ml_warehouse.schema import PacBioRun, PacBioRunWellMetrics, PacBioProductMetrics


log = structlog.get_logger(__name__)


def get_rows(
    session: Session,
    start_date: datetime,
    end_date: datetime,
    columns: List[Column] = [PacBioRun.pac_bio_run_name, PacBioRun.well_label],
    exclude: List[Column] = None,
) -> list[Row]:
    """Returns the specified fields from joined rows of PacBioRun,
    PacBioRunWellMetrics and PacBioProductMetrics.

    Arguments:
        session:    Sqlalchemy Session object used to perform queries.
        start_date: The datetime to begin from when backfilling.
        end_date:   The datetime to end at when backfilling.
        columns:    A list of columns to return.
                    Optional, defaults to run name and well label.
        exclude:    A list of columns to exclude, if these have a value,
                    that row will not be returned.
                    Optional, defaults to excluding none.

    Returns: sqlalchemy Result object
    """

    query = (
        select(*columns)
        .select_from(
            join(
                PacBioRun,
                PacBioProductMetrics,
                PacBioRun.id_pac_bio_tmp == PacBioProductMetrics.id_pac_bio_tmp,
            ).join(
                PacBioRunWellMetrics,
                PacBioProductMetrics.id_pac_bio_rw_metrics_tmp
                == PacBioRunWellMetrics.id_pac_bio_rw_metrics_tmp,
            )
        )
        .filter(
            PacBioRun.recorded_at > start_date,
            PacBioRun.recorded_at < end_date,
        )
    )
    if exclude:
        for column in exclude:
            query = query.filter(column == None)
    log.debug(f"Running select query {query}")
    return session.execute(query).all()


def backfill_rw_metrics(
    session: Session,
    start_date: datetime,
    end_date: datetime,
    dry_run: bool = False,
):
    """Backfills id product values in the run well metrics table between
    the provided dates.

    Arguments:
        session:    Sqlalchemy Session object used to perform queries.
        start_date: The datetime to begin from when backfilling.
        end_date:   The datetime to end at when backfilling.
        dry_run:    Dry run flag. Optional, defaults to false.

    """
    rows = get_rows(
        session,
        start_date,
        end_date,
        columns=[
            PacBioRun.pac_bio_run_name.label("run_name"),
            PacBioRun.well_label.label("well_label"),
        ],
        exclude=[PacBioRunWellMetrics.id_pac_bio_product],
    )
    log.info(f"{len(rows)} rows found requiring backfill")
    ids = []
    for row in rows:
        entity = PacBioEntity(run_name=row.run_name, well_label=row.well_label)
        ids.append(
            {
                "run_name": row.run_name,
                "well": row.well_label,
                "pid": entity.hash_product_id(),
            }
        )
        log.info(f"Backfilling id for {ids[-1]}")
    query = (
        update(PacBioRunWellMetrics)
        .where(
            PacBioRunWellMetrics.id_pac_bio_rw_metrics_tmp
            == PacBioProductMetrics.id_pac_bio_rw_metrics_tmp,
            PacBioProductMetrics.id_pac_bio_tmp == PacBioRun.id_pac_bio_tmp,
            PacBioRun.pac_bio_run_name == bindparam("run_name"),
            PacBioRun.well_label == bindparam("well"),
        )
        .values(id_pac_bio_product=bindparam("pid"))
        .execution_options(synchronize_session=False)
    )
    log.debug(f"Running update query {query} with values {ids}")
    if not dry_run:
        session.execute(query, ids)
        session.commit()


def backfill_product_metrics(
    session: Session,
    start_date: datetime,
    end_date: datetime,
    dry_run: bool = False,
):
    """Backfills id product values in the product metrics table between
    the provided dates.

    Arguments:
        session:    Sqlalchemy Session object used to perform queries.
        start_date: The datetime to begin from when backfilling.
        end_date:   The datetime to end at when backfilling.
        dry_run:    Dry run flag. Optional, defaults to false.

    """
    rows = get_rows(
        session,
        start_date,
        end_date,
        columns=[
            PacBioRun.pac_bio_run_name.label("run_name"),
            PacBioRun.well_label.label("well_label"),
            PacBioRun.tag_sequence.label("tag1"),
            PacBioRun.tag2_sequence.label("tag2"),
        ],
        exclude=[PacBioProductMetrics.id_pac_bio_product],
    )
    log.info(f"{len(rows)} rows found requiring backfill")
    ids = []
    for row in rows:
        tags = ",".join(filter(None, [row.tag1, row.tag2]))
        if not tags:
            tags = None
        entity = PacBioEntity(
            run_name=row.run_name, well_label=row.well_label, tags=tags
        )
        ids.append(
            {
                "run_name": row.run_name,
                "well": row.well_label,
                "tag1": row.tag1,
                "tag2": row.tag2,
                "pid": entity.hash_product_id(),
            }
        )
        log.info(f"Backfilling id for {ids[-1]}")
    query = (
        update(PacBioProductMetrics)
        .where(
            PacBioProductMetrics.id_pac_bio_tmp == PacBioRun.id_pac_bio_tmp,
            PacBioRun.pac_bio_run_name == bindparam("run_name"),
            PacBioRun.well_label == bindparam("well"),
            PacBioRun.tag_sequence == bindparam("tag1"),
            PacBioRun.tag2_sequence == bindparam("tag2"),
        )
        .values(id_pac_bio_product=bindparam("pid"))
        .execution_options(synchronize_session=False)
    )
    log.debug(f"Running update query {query} with values {ids}")
    if not dry_run:
        session.execute(query, ids)
        session.commit()
