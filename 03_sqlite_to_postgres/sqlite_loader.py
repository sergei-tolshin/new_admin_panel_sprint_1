from tableclasses import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class SQLiteLoader(object):
    def __init__(self, connection):
        self.packet_size = 100  # количество записей в пакете
        self.cursor = connection.cursor()
        self.tableclasses = {
            "film_work": FilmWork,
            "genre": Genre,
            "person": Person,
            "genre_film_work": GenreFilmWork,
            "person_film_work": PersonFilmWork
        }

    def list_tables(self):
        return self.query("SELECT name FROM sqlite_master WHERE type='table'")

    def query(self, sql, one=False, size=None):
        return self.query_one(sql) if one else self.query_many(sql, size)

    def query_one(self, sql):
        cur = self.cursor.execute(sql)
        return cur.fetchone()

    def query_many(self, sql, size=None):
        cur = self.cursor.execute(sql)
        if size:
            while rows := cur.fetchmany(size):
                yield rows
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
        for table in self.tables:
            if not self.tableclasses.get(table):
                continue
            data[table] = {"packets": [], "count_rows": self.count(table)}
            packets = self.read(table, self.packet_size)
            for packet in packets:
                data[table]["packets"].append(
                    [self.tableclasses[table](*_) for _ in packet])
        return data
