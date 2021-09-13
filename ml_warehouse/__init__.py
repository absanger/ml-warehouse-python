# -*- coding: utf-8 -*-
#
# Copyright © 2020 Genome Research Ltd. All rights reserved.
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
# @author Keith James <kdj@sanger.ac.uk>

import os
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ml_warehouse.ml_warehouse_schema import Base


class ConfigurationError(Exception):
    """Exception raised for errors in the configuration or environment."""

    def __init__(self, message: str):
        self.message = message


def _init_mlwh_db():
    uri = os.environ.get("MLWH_URI")
    if not uri:
        return None

    engine = create_engine(uri, echo=False)
    Base.metadata.create_all(engine)

    return sessionmaker(bind=engine)


# Could use scoped_session to get thread-local sessions and avoid this. See
# https://docs.sqlalchemy.org/en/13/orm/contextual.html#\
# sqlalchemy.orm.scoping.scoped_session


wh_lock = threading.Lock()
WHSession = _init_mlwh_db()


def get_wh_session() -> Session:
    """Get a new SQL session for the ML warehouse database from the factory.
    This function ensures thread safe access to the SQLAlchemy database engine.

    Returns: Session

    """
    if WHSession is None:
        raise ConfigurationError(
            "The MLWH_URI environment is variable not "
            "set. This should be set to the database "
            "connection URI of the ML warehouse"
        )

    with wh_lock:
        return WHSession()
