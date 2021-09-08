from datetime import timedelta

from pytest import mark as m

from tests.ml_warehouse_fixture import EARLY, LATE, LATEST, mlwh_session


# Stop IDEs "optimizing" away this import
_ = mlwh_session
