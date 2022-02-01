import argparse
import logging
import sqlite3

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from postgres_saver import PostgresSaver
from sqlite_loader import SQLiteLoader

logging.basicConfig(filename="logger.log", level=logging.INFO)
log = logging.getLogger()

parser = argparse.ArgumentParser()

parser.add_argument("sldb", help="Path to file name SQLite")
parser.add_argument("dbname", help="PostgeSQL database name ")
parser.add_argument("user", help="PostgeSQL user")
parser.add_argument("password", help="PostgeSQL password")
parser.add_argument("--host", help="PostgeSQL host", default="127.0.0.1")
parser.add_argument("--port", help="PostgeSQL port", default=5432)

args = parser.parse_args()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    data = sqlite_loader.load_movies()
    postgres_saver.save_all_data(data)


if __name__ == '__main__':
    dsl = {'dbname': args.dbname,
           'user': args.user,
           'password': args.password,
           'host': args.host,
           'port': args.port
           }
    try:
        with sqlite3.connect(args.sldb) as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn)
    except sqlite3.Error:
        log.exception('SQLite')
    except psycopg2.DatabaseError:
        log.exception('PostgreSQL')
    except Exception:
        log.exception('load_from_sqlite')
    finally:
        sqlite_conn.close()
        pg_conn.close()
