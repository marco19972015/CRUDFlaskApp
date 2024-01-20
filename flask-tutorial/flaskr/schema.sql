-- Dropping a table helps avoid a possible error if the table exists
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
    -- Make id primary key and have it auto increment
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Type text, can't be null
    username TEXT UNIQUE NOT NULL,
    -- Type text, can't be null
    password TEXT NOT NULL
);

CREATE TABLE post (
    -- id is the primary key, have it auto increment
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Type int, can't be null
    author_id INTEGER NOT NULL,
    -- When the post was created, have the default be the current time
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- Type text, can't be null
    title TEXT NOT NULL,
    -- Type text, can't be null
    body TEXT NOT NULL,
    -- Make a connection to the user table through post-auther_id and user-id
    FOREIGN KEY (authoer_id) REFERENCES user (id)
);