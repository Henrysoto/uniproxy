DROP TABLE IF EXISTS camera;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS util;

CREATE TABLE camera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    username TEXT,
    password TEXT,
    token TEXT,
    url TEXT
);

CREATE TABLE item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    online INTEGER NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (camera_id) REFERENCES camera (id),
    FOREIGN KEY (author_id) REFERENCES util (id)
);

CREATE TABLE util (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur TEXT UNIQUE NOT NULL,
    phrase TEXT NOT NULL,
    droits INTEGER NOT NULL,
    connected TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);