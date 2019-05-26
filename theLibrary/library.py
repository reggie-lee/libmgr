from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from theLibrary.auth import login_required
from theLibrary.db import get_db

bp = Blueprint('library', __name__)


@bp.route('/')
def index():
    username = 'Anon'
    if g.user:
        if g.user['username']:
            username = g.user['username']
        else:
            username = '@' + g.user['id']
    return render_template('index.html', name=username)


@bp.route('/@<userid>')
def profile(userid):
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id=?", [userid]
    ).fetchone()
    if user:
        return render_template('profile.html', id=user['id'], name=user['username'], password=user['password'])
    else:
        abort(500)


@bp.route('/user')
def my_profile():
    return redirect('@' + g.user['id'])

@bp.route('/explore')
def explore():
    return render_template('explore.html', booklist=get_db().execute('SELECT isbn, title, total, borrowed FROM books').fetchall())
