DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS entries;
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
  author TEXT DEFAULT NULL,
  total INTEGER CHECK (total >= 0),
  borrowed INTEGER CHECK (
    borrowed >= 0
    AND borrowed <= total
  ) DEFAULT 0
);
CREATE TABLE entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  type TEXT CHECK(type IN ('B', 'R', 'N', 'D')),
  book_id INTEGER NOT NULL,
  user_id TEXT NOT NULL,
  detail TEXT DEFAULT NULL,
  FOREIGN KEY (book_id) REFERENCES books(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);