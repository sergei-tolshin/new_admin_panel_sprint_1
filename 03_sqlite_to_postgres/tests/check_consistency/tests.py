import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor


def check_consistency(sqlite_con: sqlite3.Connection, pg_con: _connection):

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
        created: datetime = field(compare=False)
        modified: datetime = field(compare=False)

    @dataclass
    class Genre:
        id: str
        name: str
        description: str
        created: datetime = field(compare=False)
        modified: datetime = field(compare=False)

    @dataclass
    class Person:
        id: str
        full_name: str
        birth_date: date = field(compare=False, default=None)
        created: datetime = field(compare=False, default=datetime.now())
        modified: datetime = field(compare=False, default=datetime.now())

    @dataclass
    class GenreFilmWork:
        id: str
        film_work_id: str
        genre_id: str
        created: datetime = field(compare=False)

    @dataclass
    class PersonFilmWork:
        id: str
        film_work_id: str
        person_id: str
        role: str
        created: datetime = field(compare=False)

    tableclasses = {
        "film_work": FilmWork,
        "genre": Genre,
        "person": Person,
        "genre_film_work": GenreFilmWork,
        "person_film_work": PersonFilmWork
    }

    sqlite_con.row_factory = sqlite3.Row
    sl_cur = sqlite_con.cursor()
    pg_cur = pg_con.cursor()

    sl_tables = []
    sl_cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    sl_tables = [table[0] for table in sl_cur.fetchall()]

    pg_tables = []
    pg_cur.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'content'
                """)
    pg_tables = [table[0] for table in pg_cur.fetchall()]

    if set(sl_tables) == set(pg_tables):
        print('Названия и количество таблиц совпадают.')
    else:
        print('Ошибка проверки количества и названий таблиц.')

    def sl_records(table):
        sl_cur.execute(f"SELECT * FROM {table}")
        for row in sl_cur:
            yield row

    def get_pg_record(table, id):
        try:
            pg_cur.execute(f"SELECT * FROM content.{table} WHERE id='{id}'")
            return pg_cur.fetchone()
        except psycopg2.DatabaseError as error:
            print("Ошибка при работе с PostgreSQL", error)

    for table in sl_tables:
        print(f"Таблица '{table}':")
        sl_cur.execute(f"SELECT count(*) FROM {table}")
        sl_count = sl_cur.fetchone()[0]

        try:
            pg_cur.execute(f"SELECT count(*) FROM content.{table}")
            pg_count = pg_cur.fetchone()[0]
        except psycopg2.DatabaseError as error:
            print("Ошибка при работе с PostgreSQL", error)
            break

        if sl_count == pg_count:
            print("-- Проверка целосности данных - ОК")
            print("-- Проверка содержимого записей:")
            record_error = False
            for record in sl_records(table):
                sl_record = tableclasses[table](*record)
                try:
                    pg_record = tableclasses[table](
                        **get_pg_record(table, sl_record.id))
                except Exception as error:
                    print(f"Ошибка {error=}")
                    break

                if sl_record != pg_record:
                    record_error = True
                    print(f"---- Ошибка данных с id:'{sl_record.id}'"
                          f" в таблице '{table}'")
            if record_error is False:
                print("---- Все записи из PostgreSQL присутствуют с такими же"
                      "значениями полей, как и в SQLite")
        else:
            print("-- Проверка целосности данных - Ошибка")


if __name__ == '__main__':
    sqlite_db = 'db.sqlite'
    dsl = {'dbname': 'movies_database', 'user': 'app',
           'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}
    with sqlite3.connect(sqlite_db) as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        check_consistency(sqlite_conn, pg_conn)
