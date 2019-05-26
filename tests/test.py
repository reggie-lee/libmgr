#!/bin/python3
from theLibrary.db import get_db

db = get_db()

db.executescript(open('test.sql').read())
db.commit()
