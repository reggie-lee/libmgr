#!/bin/python3
import sqlite3
import bcrypt

conn = sqlite3.connect('library.db')
c = conn.cursor()

c.executescript(open('schema.sql').read())
conn.commit()

password = bcrypt.hashpw(str.encode(
    input('Enter root password: ')), bcrypt.gensalt())

c.execute("INSERT INTO users VALUES ('root', ?, 'Admin')", [password])
conn.commit()

c.close()
conn.close()
