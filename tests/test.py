#!/bin/python3
#TODO
import sqlite3

db = sqlite3.connect('instance/library.db')

db.executescript(open('tests/books.sql').read())
db.commit()
