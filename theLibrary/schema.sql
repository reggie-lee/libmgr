DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS subbooks;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS log;
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  password TEXT NOT NULL,
  username TEXT NOT NULL,
  permission INTEGER DEFAULT 0
);
CREATE TABLE books (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  isbn TEXT NOT NULL,
  location TEXT DEFAULT NULL,
  language TEXT DEFAULT NULL,
  title TEXT DEFAULT NULL,
  publisher TEXT DEFAULT NULL,
  shape TEXT DEFAULT NULL,
  summary TEXT DEFAULT NULL,
  othertitles DEFAULT NULL,
  subject TEXT DEFAULT NULL,
  author TEXT DEFAULT NULL
);
CREATE TABLE subbooks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  book_id INTEGER NOT NULL,
  location TEXT DEFAULT NULL,
  FOREIGN KEY (book_id) REFERENCES books(id)
);
CREATE TABLE account (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sub_id INTEGER NOT NULL UNIQUE,
  user_id TEXT NOT NULL,
  due TIMESTAMP NOT NULL DEFAULT (DATETIME('now', '+1 month', 'localtime')),
  FOREIGN KEY (sub_id) REFERENCES subbooks(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TIMESTAMP NOT NULL DEFAULT (DATETIME('now', 'localtime')),
  user_id TEXT NOT NULL,
  detail TEXT DEFAULT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);