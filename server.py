#!/bin/python3
from flask import Flask, abort, request, make_response, redirect, url_for, render_template
import sqlite3
import bcrypt
app = Flask(__name__)

#index = open('server/index.html').read()
conn = sqlite3.connect('library.db', check_same_thread=False)


@app.route("/")
def index():
    uid = request.cookies.get('userid')
    if uid:
        c = conn.cursor()
        username = c.execute(
            "SELECT username FROM users WHERE id=?", [uid]).fetchone()
        c.close()
        return render_template('newindex.html', name=username[0])
    else:
        return render_template('newindex.html', name='anon')


@app.route("/user")
def userprofile():
    uid = request.cookies.get('userid')
    if uid:
        c = conn.cursor()
        username, password = c.execute(
            "SELECT username, password FROM users WHERE id=?", [uid]).fetchone()
        c.close()
        return render_template('profile.html', id=uid, name=username, password=password)
    else:
        return redirect(url_for('login'))


@app.route("/booklist")
def booklist():
    c = conn.cursor()
    l = c.execute("SELECT * FROM books").fetchall()
    c.close()
    return render_template('booklist.html', blist=l)


@app.route("/login", methods=('GET', 'POST'))
def login():
    if request.method == 'GET':
        if request.cookies.get('userid'):
            return redirect(url_for('userprofile'))
        return render_template('newlogin.html')

    uid = request.form['userid']
    passw = request.form['password']
    c = conn.cursor()
    password = c.execute(
        "SELECT password FROM users WHERE id=?", [uid]).fetchone()
    c.close()

    if not password:
        return "User not found."

    if not bcrypt.checkpw(str.encode(passw), password[0]):
        return "Wrong password."

    resp = make_response(render_template('newsuccess.html', id=uid))
    resp.set_cookie('userid', uid, max_age=2592000)
    return resp


if __name__ == "__main__":
    app.run()

conn.commit()
conn.close()
