-- Расширения для генерации UUID
CREATE EXTENSION "uuid-ossp";
-- Cхема 'content' 
CREATE SCHEMA IF NOT EXISTS content;
-- Таблица 'Кинопроизведения'
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE,
    modified TIMESTAMP WITH TIME ZONE
);
-- Таблица 'Жанры'
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created TIMESTAMP WITH TIME ZONE,
    modified TIMESTAMP WITH TIME ZONE
);
-- Таблица 'Персонажи'
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE,
    modified TIMESTAMP WITH TIME ZONE
);
-- Таблица 'Жанры фильма'
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid NOT NULL,
    film_work_id uuid NOT NULL,
    created TIMESTAMP WITH TIME ZONE
);
-- Таблица 'Персонажи фильма'
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL,
    film_work_id uuid NOT NULL,
    role TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS film_work_creation_date_rating_idx ON content.film_work (creation_date, rating);
CREATE INDEX IF NOT EXISTS film_work_creation_date_type_idx ON content.film_work (creation_date, type);
CREATE UNIQUE INDEX IF NOT EXISTS genre_name_idx ON content.genre (name);
CREATE UNIQUE INDEX IF NOT EXISTS person_full_name_idx ON content.person (full_name);
CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre_idx ON content.genre_film_work (film_work_id, genre_id);
CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_idx ON content.person_film_work (film_work_id, person_id, role);