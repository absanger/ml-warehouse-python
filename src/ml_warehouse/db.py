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

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def mlwh_session() -> sessionmaker:
    """Provide a connection to ml warehouse.

    Returns: sqlalchemy Session

    """
    user = os.environ.get("MYSQL_USER")
    db = os.environ.get("MYSQL_DBNAME")
    password = os.environ.get("MYSQL_PW")
    host = os.environ.get("MYSQL_HOST")
    port = os.environ.get("MYSQL_PORT")

    if None in (user, db, password, host, port):
        raise MissingVarException(
            'Environment variables "MYSQL_USER", '
            '"MYSQL_DBNAME", "MYSQL_PW", "MYSQL_HOST" '
            'and "MYSQL_PORT" must be set'
        )

    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"
    engine = create_engine(url, future=True)
    session_maker = sessionmaker(engine)

    return session_maker


class MissingVarException(Exception):
    """Exception raised when a required environment varible is not set"""

    pass
