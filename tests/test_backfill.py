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

from pytest import mark as m

from ml_warehouse.backfill.pac_bio import (
    get_rows,
    backfill_product_metrics,
    backfill_rw_metrics,
)
from datetime import datetime

from ml_warehouse.schema import PacBioRun, PacBioRunWellMetrics, PacBioProductMetrics
import logging


@m.describe("Getting run information from tables")
class TestGetRows:
    @m.context("When provided with a date range")
    @m.it("Gets only rows in that date range")
    def test_get_rows_range(self, mlwh_session):
        expected_rows = [
            {
                "cost_code": "S4773",
                "id_lims": "Traction",
                "id_pac_bio_run_lims": "28",
                "id_pac_bio_tmp": "16207",
                "id_sample_tmp": "4237953",
                "id_study_tmp": "5735",
                "last_updated": "2020-03-13 15:46:06",
                "library_created_at": None,
                "pac_bio_library_tube_id_lims": "103",
                "pac_bio_library_tube_legacy_id": "999",
                "pac_bio_library_tube_name": "DTOL8493629",
                "pac_bio_library_tube_uuid": "f284c87f-57ae-4624-baa6-2688bc5c1f72",
                "pac_bio_run_name": "TRACTION-RUN-28",
                "pac_bio_run_uuid": "5d406d89-18f6-4fa8-8b8-93aab251c22f",
                "plate_barcode": "plate_barcode placeholder",
                "plate_uuid_lims": "d23ea49c-5ff7-4210-b295-0224419f3dbf",
                "recorded_at": "2020-03-13 15:46:06",
                "tag_identifier": "bc1022_BAK8B_OA",
                "tag_sequence": "CACTCACGTGTGATATT",
                "tag_set_id_lims": "1",
                "tag_set_name": "Sequel_16_barcodes_v3",
                "well_label": "B1",
                "well_uuid_lims": "e4e76495-adc5-4b5d-9c05-db3fe72b754c",
            },
            {
                "cost_code": "S4773",
                "id_lims": "SQSCP",
                "id_pac_bio_run_lims": "81230",
                "id_pac_bio_tmp": "20300",
                "id_sample_tmp": "5490195",
                "id_study_tmp": "5735",
                "last_updated": "2021-04-09 13:00:40",
                "library_created_at": None,
                "pac_bio_library_tube_id_lims": "NT1667187Q",
                "pac_bio_library_tube_legacy_id": "40356040",
                "pac_bio_library_tube_name": "DN787408U-C2",
                "pac_bio_library_tube_uuid": "f284c87f-57ae-4624-baa6-2688bc5c1f72",
                "pac_bio_run_name": "81230",
                "pac_bio_run_uuid": "5d406d89-18f6-4fa8-8b8-93aab251c22f",
                "plate_barcode": "DN799664B",
                "plate_uuid_lims": "9422f314-9933-11eb-bdb9-fa163eea3084",
                "recorded_at": "2021-04-09 13:00:40",
                "tag_identifier": "1017",
                "tag_sequence": "CACACGCGCGCTATATT",
                "tag_set_id_lims": "1",
                "tag_set_name": "Sequel_16_barcodes_v3",
                "well_label": "B1",
                "well_uuid_lims": "942eb05a-9933-11eb-bdb9-fa163eea3084",
            },
        ]

        assert (
            get_rows(
                session=mlwh_session,
                start_date=datetime(2020, 2, 28),
                end_date=datetime(2021, 4, 9, 14),
                columns=[PacBioRun],
            )
            == expected_rows
        )
        assert get_rows(
            session=mlwh_session,
            start_date=datetime(2030, 1, 1),
            end_date=datetime(2035, 1, 1),
            columns=[PacBioRun],
        ) == [{}]

    @m.context("When provided with a set of column names")
    @m.it("Gets only those columns")
    def test_get_rows_specific_columns(self, mlwh_session):
        expected_rows = [
            {
                "pac_bio_run_name": "81230",
                "well_label": "B1",
                "tag_sequence": "CACACGCGCGCTATATT",
                "tag2_sequence": None,
            },
            {
                "pac_bio_run_name": "81876",
                "well_label": "A1",
                "tag_sequence": None,
                "tag2_sequence": None,
            },
            {
                "pac_bio_run_name": "83472",
                "well_label": "A1",
                "tag_sequence": None,
                "tag2_sequence": None,
            },
        ]

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
            )
            == expected_rows
        )

    @m.context("When provided with columns to exclude")
    @m.it("Returns only rows where those columns are null")
    def test_get_rows_exclude(self, mlwh_session):
        expected_rows = [
            {
                "pac_bio_run_name": "81876",
                "well_label": "A1",
                "tag_sequence": None,
                "tag2_sequence": None,
            },
            {
                "pac_bio_run_name": "83472",
                "well_label": "A1",
                "tag_sequence": None,
                "tag2_sequence": None,
            },
        ]

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
                exclude=PacBioRun.tag_sequence,
            )
            == expected_rows
        )
        assert get_rows(
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
        ) == [{}]


@m.describe("Backfilling run well metrics table")
class TestBackfillRWMetrics:
    @m.context("When run as a dry-run")
    @m.it("Logs ids without committing them to the database")
    def test_backfill_rw_metrics_dry_run(self, mlwh_session, caplog):
        caplog.at_level(logging.INFO)
        log_messages = [
            "Backfilling id for "
            "{'run_name': '81876','well_label': 'A1', "
            "'product_id': '5829713f0e5e1b7541786bb2bdc6fe81cae3ba11d5aa63bde22fafec4f1af9c6'}",
            "{'run_name': '83472','well_label': 'A1', "
            "'product_id': '66c508d6dfd78c1ab82e26d26061fe141e5d33ac3b9cada6d6fe951e22ec2432'}",
            "{'run_name': '81230','well_label': 'B1', "
            "'product_id': '6b7deecc9bc720214d50545e1cfd8466ca33b5d3c8b6b2305eafbfa0cdad88ac'}",
        ]
        expected_rows = [{"id_pac_bio_product": None} for i in range(3)]
        backfill_rw_metrics(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            dry_run=True,
        )
        for message in log_messages:
            assert message in caplog.text

        rows = get_rows(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            columns=[PacBioRunWellMetrics.id_pac_bio_product],
        )
        assert rows == expected_rows

    @m.context("When run without dry-run")
    @m.it("Commits changes to the database")
    def test_backfill_rw_metrics(self, mlwh_session, caplog):
        caplog.at_level(logging.INFO)
        expected_rows = [
            {
                "id_pac_bio_product": "5829713f0e5e1b7541786bb2bdc6fe81cae3ba11d5aa63bde22fafec4f1af9c6"
            },
            {
                "id_pac_bio_product": "66c508d6dfd78c1ab82e26d26061fe141e5d33ac3b9cada6d6fe951e22ec2432"
            },
            {
                "id_pac_bio_product": "6b7deecc9bc720214d50545e1cfd8466ca33b5d3c8b6b2305eafbfa0cdad88ac"
            },
        ]
        backfill_rw_metrics(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            dry_run=True,
        )

        rows = get_rows(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            columns=[PacBioRunWellMetrics.id_pac_bio_product],
        )
        assert rows == expected_rows


@m.describe("Backfilling product metrics table")
class TestBackfillProductMetrics:
    @m.context("When run as a dry-run")
    @m.it("Logs ids without committing them to the database")
    def test_backfill_rw_metrics_dry_run(self, mlwh_session, caplog):
        caplog.at_level(logging.INFO)
        log_messages = [
            "Backfilling id for "
            "{'run_name': '81876','well_label': 'A1', 'tag_sequence': None, 'tag2_sequence': None, "
            "'product_id': '5829713f0e5e1b7541786bb2bdc6fe81cae3ba11d5aa63bde22fafec4f1af9c6'}",
            "{'run_name': '83472','well_label': 'A1', 'tag_sequence': None, 'tag2_sequence': None, "
            "'product_id': '66c508d6dfd78c1ab82e26d26061fe141e5d33ac3b9cada6d6fe951e22ec2432'}",
            "{'run_name': '81230','well_label': 'B1', 'tag_sequence': None, 'tag2_sequence': None, "
            "'product_id': '6b7deecc9bc720214d50545e1cfd8466ca33b5d3c8b6b2305eafbfa0cdad88ac'}",
        ]
        expected_rows = [{"id_pac_bio_product": None} for i in range(3)]
        backfill_rw_metrics(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            dry_run=True,
        )
        for message in log_messages:
            assert message in caplog.text

        rows = get_rows(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            columns=[PacBioRunWellMetrics.id_pac_bio_product],
        )
        assert rows == expected_rows

    @m.context("When run without dry-run")
    @m.it("Commits changes to the database")
    def test_backfill_rw_metrics(self, mlwh_session, caplog):
        caplog.at_level(logging.INFO)
        expected_rows = [
            {
                "id_pac_bio_product": "5829713f0e5e1b7541786bb2bdc6fe81cae3ba11d5aa63bde22fafec4f1af9c6"
            },
            {
                "id_pac_bio_product": "66c508d6dfd78c1ab82e26d26061fe141e5d33ac3b9cada6d6fe951e22ec2432"
            },
            {
                "id_pac_bio_product": "6b7deecc9bc720214d50545e1cfd8466ca33b5d3c8b6b2305eafbfa0cdad88ac"
            },
        ]
        backfill_rw_metrics(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            dry_run=True,
        )

        rows = get_rows(
            mlwh_session,
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 1, 1),
            columns=[PacBioRunWellMetrics.id_pac_bio_product],
        )
        assert rows == expected_rows
