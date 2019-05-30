import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import bcrypt

from theLibrary.db import get_db

bp = Blueprint('auth', __name__)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def permission_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user['permission'] == 0:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def loggedin():
    userid = session.get('userid')

    if userid is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM users WHERE id=?", [userid]
        ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        username = request.form['username']
        db = get_db()
        error = None

        if not userid:
            error = 'User ID cannot be empty'
        elif not password:
            error = 'Password cannot be empty'
        elif db.execute('SELECT EXISTS(SELECT 1 FROM users WHERE id=?)', [userid]).fetchone()[0]:
            error = 'User @{} already registered.'.format(userid)

        if error is None:
            db.execute(
                'INSERT INTO users (id, password, username) VALUES (?, ?, ?)',
                (userid, bcrypt.hashpw(password.encode(), bcrypt.gensalt()), username)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM users WHERE id=?", [userid]
        ).fetchone()

        if user is None:
            error = 'User not found.'
        elif not bcrypt.checkpw(password.encode(), user['password']):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['userid'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
