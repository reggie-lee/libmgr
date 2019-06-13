#!/bin/python3
# TODO
import sqlite3

db = sqlite3.connect('instance/library.db')

db.executescript(open('tests/books.sql').read())
db.commit()

for book_id in range(1, 1001):
    db.execute(
        'INSERT INTO subbooks (book_id) VALUES (?)',
        (book_id,)
    )
db.commit()
