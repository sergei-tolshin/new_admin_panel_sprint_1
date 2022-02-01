from dataclasses import dataclass
from datetime import date, datetime


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
