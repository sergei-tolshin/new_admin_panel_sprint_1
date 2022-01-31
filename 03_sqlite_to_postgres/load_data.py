import sqlite3
from dataclasses import asdict, dataclass
from datetime import date, datetime

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    @dataclass
    class FilmWork:
        id: str
        title: str
        description: str
        creation_date: date
        certificate: str
        file_path: str
        rating: float
        type: str
        created: datetime
        modified: datetime

    @dataclass
    class Genre:
        id: str
        name: str
        description: str
        created: datetime
        modified: datetime

    @dataclass
    class Person:
        id: str
        full_name: str
        birth_date: date
        created: datetime
        modified: datetime

    @dataclass
    class GenreFilmWork:
        id: str
        film_work_id: str
        genre_id: str
        created: datetime

    @dataclass
    class PersonFilmWork:
        id: str
        film_work_id: str
        person_id: str
        role: str
        created: datetime

    class SQLiteLoader(object):
        def __init__(self, connection):
            self.packet_size = 100
            self.cursor = connection.cursor()
            self.tableclasses = {
                "film_work": FilmWork,
                "genre": Genre,
                "person": Person,
                "genre_film_work": GenreFilmWork,
                "person_film_work": PersonFilmWork
            }

        def list_tables(self):
            return self.query("""
                SELECT name FROM sqlite_master WHERE type='table'
                """)

        def query(self, sql, one=False, size=None):
            return self.query_one(sql) if one else self.query_many(sql, size)

        def query_one(self, sql):
            cur = self.cursor.execute(sql)
            return cur.fetchone()

        def query_many(self, sql, size=None):
            cur = self.cursor.execute(sql)
            if size:
                while True:
                    rows = cur.fetchmany(size)
                    if rows:
                        yield rows
                    else:
                        break
            else:
                for row in cur:
                    yield [row]

        def query_for(self, table):
            return f"SELECT * from {table}"

        def read(self, table, size=None):
            return self.query(self.query_for(table), size=size)

        def count(self, table):
            count = self.query(f"SELECT count(*) FROM {table}", one=True)
            return count[0]

        @property
        def tables(self):
            return [table[0][0] for table in self.list_tables()]

        def load_movies(self):
            data = {}
            try:
                for table in self.tables:
                    if self.tableclasses.get(table):
                        data[table] = {"packets": [],
                                       "count_rows": self.count(table)}
                        packets = self.read(table, self.packet_size)
                        for packet in packets:
                            data[table]["packets"].append(
                                [self.tableclasses[table](*_) for _ in packet])
                return data
            except sqlite3.Error as error:
                print("Ошибка при работе с SQLite", error)
            except BaseException as error:
                print(f"Ошибка в SQLiteLoader {error=}")
            finally:
                if self.cursor:
                    self.cursor.close()

    class PostgresSaver(object):

        class Table(object):
            def __init__(self, cursor, name):
                self.cursor = cursor
                self._name = name
                self._columns = self._load_columns()

            def _load_columns(self):
                self.cursor.execute(f"""
                    SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{self.name}'
                    """)
                return [column[0] for column in self.cursor.fetchall()]

            @property
            def name(self):
                return self._name

            @property
            def columns(self):
                return self._columns

        def __init__(self, pg_conn):
            self.cursor = pg_conn.cursor()

        def list_tables(self):
            self.cursor.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'content'
                """)
            return self.cursor.fetchall()

        def insert(self, table, columns, args, data):
            values = ",".join(self.cursor.mogrify(
                f"({args})",
                asdict(item)).decode() for item in data
            )
            self.cursor.execute(f"""
                INSERT INTO content.{table} ({columns}) VALUES {values}
                """)

        def count(self, table):
            self.cursor.execute(f"SELECT count(*) FROM content.{table}")
            return self.cursor.fetchone()[0]

        @property
        def tables(self):
            return (self.Table(self.cursor, t[0]) for t in self.list_tables())

        def save_all_data(self, data):
            try:
                for table in self.tables:
                    if data.get(table.name):
                        self.cursor.execute(f"TRUNCATE content.{table.name}")

                        columns = ",".join(table.columns)
                        args = ",".join(
                            [f"%({col})s" for col in table.columns])
                        packets = data[table.name]["packets"]
                        count = data[table.name]["count_rows"]
                        for packet in packets:
                            self.insert(table.name, columns, args, packet)
                        print(f"В таблицу '{table.name}' загружено "
                              f"{self.count(table.name)} из {count} записей")
            except psycopg2.DatabaseError as error:
                print("Ошибка при работе с PostgreSQL", error)
            except Exception as error:
                print(f"Ошибка в PostgresSaver {error=}")
            finally:
                if self.cursor:
                    self.cursor.close()

    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    data = sqlite_loader.load_movies()
    postgres_saver.save_all_data(data)


if __name__ == '__main__':
    dsl = {'dbname': 'movies_database', 'user': 'app',
           'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
