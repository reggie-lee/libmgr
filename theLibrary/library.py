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


@bp.route('/bookshelf')
@login_required
def bookshelf():
    db = get_db()
    booklist = db.execute(
        'SELECT books.id, books.isbn, books.title, account.due FROM account JOIN books ON user_id = ? AND (SELECT book_id FROM subbooks WHERE id = account.sub_id) = books.id',
        (g.user['id'],)
    ).fetchall()
    return render_template('user/bookshelf.html', booklist=booklist)


@bp.route('/explore')
def explore():
    return render_template(
        'explore.html',
        booklist=get_db().execute(
            'SELECT id, isbn, title, (SELECT COUNT(*) FROM subbooks WHERE book_id = books.id) AS total, (SELECT COUNT(*) FROM account WHERE (SELECT book_id FROM subbooks WHERE id = account.sub_id) = books.id) AS borrowed FROM books'
        ).fetchall()
    )


@bp.route('/borrow/<int:bookid>')
def borrow(bookid):
    db = get_db()
    book = db.execute(
        'SELECT id, title FROM books WHERE id = ?', (bookid,)).fetchone()
    subbooks = db.execute(
        'SELECT id, location, (SELECT user_id FROM account WHERE sub_id = subbooks.id) AS borrower FROM subbooks WHERE book_id = ?',
        (bookid,)
    )
    return render_template('user/borrow.html', book=book, subbooks=subbooks)


@bp.route('/borrow/<int:bookid>/<int:subid>')
def sub_borrow(bookid, subid):
    return "TODO"
