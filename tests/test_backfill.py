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

from pytest import mark as m

from ml_warehouse.backfill.pac_bio import (
    get_rows,
    backfill_product_metrics,
    backfill_rw_metrics,
)
from ml_warehouse.schema import PacBioRun, PacBioRunWellMetrics, PacBioProductMetrics


@m.describe("Getting run information from tables")
class TestGetRows:
    @m.context("When provided with a date range")
    @m.it("Gets only rows in that date range")
    def test_get_rows_range(self, mlwh_session):
        expected_rows = [
            (
                "81230",
                "B1",
            ),
        ]

        assert (
            get_rows(
                session=mlwh_session,
                start_date=datetime(2021, 4, 1),
                end_date=datetime(2021, 4, 10),
            )
            == expected_rows
        )
        assert (
            get_rows(
                session=mlwh_session,
                start_date=datetime(2030, 1, 1),
                end_date=datetime(2035, 1, 1),
            )
            == []
        )

    @m.context("When provided with a set of column names")
    @m.it("Gets only those columns")
    def test_get_rows_specific_columns(self, mlwh_session):
        expected_rows = [
            (
                "81230",
                "B1",
                "CACACGCGCGCTATATT",
                None,
            ),
            (
                "81876",
                "A1",
                None,
                None,
            ),
            (
                "83472",
                "A1",
                "CACATATCAGAGTGCG",
                None,
            ),
        ]

        actual_rows = get_rows(
            session=mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            columns=[
                PacBioRun.pac_bio_run_name,
                PacBioRun.well_label,
                PacBioRun.tag_sequence,
                PacBioRun.tag2_sequence,
            ],
        )
        assert [row in actual_rows for row in expected_rows]

    @m.context("When provided with columns to exclude")
    @m.it("Returns only rows where those columns are null")
    def test_get_rows_exclude(self, mlwh_session):
        expected_rows = [
            (
                "81876",
                "A1",
                None,
                None,
            ),
        ]

        actual_rows = get_rows(
            session=mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            columns=[
                PacBioRun.pac_bio_run_name,
                PacBioRun.well_label,
                PacBioRun.tag_sequence,
                PacBioRun.tag2_sequence,
            ],
            exclude=[PacBioRun.tag_sequence],
        )
        assert [row in actual_rows for row in expected_rows]

        assert (
            get_rows(
                session=mlwh_session,
                start_date=datetime(2021, 1, 1),
                end_date=datetime(2022, 1, 1),
                columns=[
                    PacBioRun.pac_bio_run_name,
                    PacBioRun.well_label,
                    PacBioRun.tag_sequence,
                    PacBioRun.tag2_sequence,
                ],
                exclude=[PacBioRun.tag_sequence, PacBioRun.well_label],
            )
            == []
        )


@m.describe("Backfilling run well metrics table")
class TestBackfillRWMetrics:
    @m.context("When run as a dry-run")
    @m.it("Logs ids without committing them to the database")
    def test_backfill_rw_metrics_dry_run(self, mlwh_session, capsys):
        log_messages = [
            "Backfilling id for "
            "{'run_name': '83472', 'well_label': 'A1', "
            "'product_id': '66c508d6dfd78c1ab82e26d26061fe141e5d33ac3b9cada6d6fe951e22ec2432'}",
            "{'run_name': '81230', 'well_label': 'B1', "
            "'product_id': '6b7deecc9bc720214d50545e1cfd8466ca33b5d3c8b6b2305eafbfa0cdad88ac'}",
        ]
        backfill_rw_metrics(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            dry_run=True,
        )
        expected_rows = [
            (None,),
            (None,),
            ("fb76b33a8beb37f0da6da9577c67ea5d0c654121997cc195b9e83c0834d69e58",),
        ]

        logs = capsys.readouterr().out
        for message in log_messages:
            assert message in logs

        actual_rows = get_rows(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            columns=[PacBioRunWellMetrics.id_pac_bio_product],
        )
        for row in expected_rows:
            assert row in actual_rows

    @m.context("When run without dry-run")
    @m.it("Commits changes to the database")
    def test_backfill_rw_metrics(self, mlwh_session, caplog):
        expected_rows = [
            "fb76b33a8beb37f0da6da9577c67ea5d0c654121997cc195b9e83c0834d69e58",
            "66c508d6dfd78c1ab82e26d26061fe141e5d33ac3b9cada6d6fe951e22ec2432",
            "6b7deecc9bc720214d50545e1cfd8466ca33b5d3c8b6b2305eafbfa0cdad88ac",
        ]
        backfill_rw_metrics(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
        )

        actual_rows = get_rows(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            columns=[PacBioRunWellMetrics.id_pac_bio_product],
        )
        for row in expected_rows:
            assert row in actual_rows


@m.describe("Backfilling product metrics table")
class TestBackfillProductMetrics:
    @m.context("When run as a dry-run")
    @m.it("Logs ids without committing them to the database")
    def test_backfill_product_metrics_dry_run(self, mlwh_session, capsys):
        log_messages = [
            "Backfilling id for "
            "{'run_name': '83472', 'well_label': 'A1', 'tag_sequence': 'CACATATCAGAGTGCG', 'tag2_sequence': None, "
            "'product_id': 'f339abe4ff45c10c3bce6e6fa6bdd242dd432fd3ce57a068de4655edbdf053aa'}",
            "{'run_name': '81230', 'well_label': 'B1', 'tag_sequence': 'CACACGCGCGCTATATT', 'tag2_sequence': None, "
            "'product_id': '4f5d77a89eb07b56104e940ff3aca80d4cf7b869af4a8d9a3f2515942dda6077'}",
        ]
        expected_rows = [
            (None,),
            (None,),
        ]
        backfill_product_metrics(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            dry_run=True,
        )
        logs = capsys.readouterr().out
        for message in log_messages:
            assert message in logs

        actual_rows = get_rows(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            columns=[PacBioProductMetrics.id_pac_bio_product],
        )
        for row in expected_rows:
            assert row in actual_rows

    @m.context("When run without dry-run")
    @m.it("Commits changes to the database")
    def test_backfill_product_metrics(self, mlwh_session, caplog):
        expected_rows = [
            "f339abe4ff45c10c3bce6e6fa6bdd242dd432fd3ce57a068de4655edbdf053aa",
            "4f5d77a89eb07b56104e940ff3aca80d4cf7b869af4a8d9a3f2515942dda6077",
        ]
        backfill_product_metrics(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
        )

        actual_rows = get_rows(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            columns=[PacBioProductMetrics.id_pac_bio_product],
        )
        for row in expected_rows:
            assert row in actual_rows
