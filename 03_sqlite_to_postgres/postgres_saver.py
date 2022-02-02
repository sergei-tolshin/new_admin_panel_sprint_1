import logging
from dataclasses import asdict

import psycopg2.extras

log = logging.getLogger()


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
                WHERE table_schema = 'content' ORDER BY table_name
                """)
        return self.cursor.fetchall()

    def insert(self, table, columns, args, data):
        psycopg2.extras.execute_batch(self.cursor, f"""
                INSERT INTO content.{table} ({columns}) VALUES ({args})
                """, [asdict(item) for item in data])

    def count(self, table):
        self.cursor.execute(f"SELECT count(*) FROM content.{table}")
        return self.cursor.fetchone()[0]

    @property
    def tables(self):
        return (self.Table(self.cursor, t[0]) for t in self.list_tables())

    def save_all_data(self, data):
        for table in self.tables:
            if not data.get(table.name):
                continue
            self.cursor.execute(f"TRUNCATE content.{table.name} CASCADE")
            columns = ",".join(table.columns)
            args = ",".join([f"%({col})s" for col in table.columns])
            packets = data[table.name]["packets"]
            count = data[table.name]["count_rows"]
            for packet in packets:
                self.insert(table.name, columns, args, packet)
            log.info(f"Table '{table.name}' loaded with "
                     f"{self.count(table.name)} of {count} records")
