import os
import subprocess

PW = os.environ["MYSQL_PW"]
USER = os.environ["MYSQL_USER"]
HOST = os.environ["MYSQL_HOST"]
PORT = os.environ["MYSQL_PORT"]
DBNAME = os.environ["MYSQL_DBNAME"]

url = "mysql+pymysql://{user}:{passw}@{host}:{port}/{db}?charset=utf8mb4".format(
    user = USER,
    passw = PW,
    host = HOST,
    port = PORT,
    db = DBNAME
)

subprocess.run(
    [
        "sqlacodegen",
        url
    ]
)