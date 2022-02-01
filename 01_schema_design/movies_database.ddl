-- Расширения для генерации UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Cхема 'content' 
CREATE SCHEMA IF NOT EXISTS content;

-- Таблица 'Кинопроизведения'
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modified TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица 'Жанры'
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modified TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица 'Персонажи'
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modified TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица 'Жанры фильма'
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    genre_id uuid NOT NULL REFERENCES content.genre ON DELETE CASCADE,
    film_work_id uuid NOT NULL REFERENCES content.film_work ON DELETE CASCADE,
    created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (genre_id, film_work_id)
);

-- Таблица 'Персонажи фильма'
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id uuid NOT NULL REFERENCES content.person ON DELETE CASCADE,
    film_work_id uuid NOT NULL REFERENCES content.film_work ON DELETE CASCADE,
    role TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (person_id, film_work_id, role)
);


CREATE INDEX IF NOT EXISTS film_work_creation_date_rating_idx ON content.film_work (creation_date, rating);
CREATE INDEX IF NOT EXISTS film_work_creation_date_type_idx ON content.film_work (creation_date, type);

CREATE UNIQUE INDEX IF NOT EXISTS genre_name_idx ON content.genre (name);
CREATE UNIQUE INDEX IF NOT EXISTS person_full_name_idx ON content.person (full_name);
CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre_idx ON content.genre_film_work (film_work_id, genre_id);
CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_idx ON content.person_film_work (film_work_id, person_id, role);