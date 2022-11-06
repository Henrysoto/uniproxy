DROP TABLE IF EXISTS camera;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS project;
DROP TABLE IF EXISTS util;

CREATE TABLE camera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    ip TEXT NOT NULL,
    name TEXT NOT NULL,
    username TEXT,
    password TEXT,
    online INTEGER,
    url TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE util (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur TEXT UNIQUE NOT NULL,
    phrase TEXT NOT NULL,
    connected TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);