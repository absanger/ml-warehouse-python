from datetime import timedelta

from pytest import mark as m

from tests.ml_warehouse_fixture import EARLY, LATE, LATEST, mlwh_session
from ml_warehouse.ml_warehouse_schema_new import Study


# Stop IDEs "optimizing" away this import
_ = mlwh_session


@m.describe("Querying the ML Warehouse")
class TestMLWarehouseQueries(object):
    @m.it("Successfully retrieves record of study")
    def test_retrieve_study(self, mlwh_session):

        all_studies = mlwh_session.query(Study).all()

        assert len(all_studies) > 0

    def test_retrieve_iseq_flowcell(self, mlwh_session):

        pass
