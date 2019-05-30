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
        readonly = True
        if user['id'] == g.user['id']:
            readonly = False
        return render_template('profile.html', user=user, readonly=readonly)
    else:
        abort(500)


@bp.route('/user', methods=('GET', 'POST'))
@login_required
def my_profile():
    if request.method == 'POST':
        userid = request.form['userid']
        username = request.form['username']
        db = get_db()
        error = None

        if not userid:
            error = 'User ID cannot be empty'
        elif userid != g.user['id'] and db.execute('SELECT EXISTS(SELECT 1 FROM users WHERE id=?)', [userid]).fetchone()[0]:
            error = 'User @{} already registered.'.format(userid)

        if error is None:
            db.execute(
                'UPDATE users SET (id, username) = (?, ?) WHERE id = ?',
                (userid, username, g.user['id'])
            )
            db.commit()
            flash('User information updated.')
            return redirect('@' + userid)

        flash(error)

    return redirect('@' + g.user['id'])


@bp.route('/explore')
def explore():
    return render_template('explore.html', booklist=get_db().execute('SELECT isbn, title, total, borrowed FROM books').fetchall())
