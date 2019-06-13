from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import bcrypt
from theLibrary.auth import login_required, permission_required
from theLibrary.db import get_db

import theLibrary.alerts as alerts
import re

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


@bp.route('/search', defaults={'page': 0})
@bp.route('/search/<int:page>')
def search(page):
    # TODO
    query = request.args.get('query')
    keywords = '%' + '%'.join(re.sub(r'[^\w]', ' ', query).split()) + '%'

    booklist = None
    if 'search' in g:
        booklist = g.search.get(keywords)
    else:
        g.search = {}

    if booklist is None:
        db = get_db()
        g.search[keywords] = booklist = db.execute(
            'SELECT id, isbn, title, (SELECT COUNT(*) FROM subbooks WHERE book_id = books.id) AS total, (SELECT COUNT(*) FROM account WHERE (SELECT book_id FROM subbooks WHERE id = account.sub_id) = books.id) AS borrowed FROM books WHERE title LIKE ?',
            (keywords,)
        ).fetchall()
    pages = -(-len(booklist) // 10)
    booklist = booklist[page * 10:page * 10 + 10]

    return render_template('search.html', query=query, booklist=booklist, page=page, pages=pages)


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
        flash(alerts.error('User not found.'))
        return redirect(url_for('library.index'))


@bp.route('/user', methods=('GET', 'POST'))
@login_required
def my_profile():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        username = request.form['username']
        db = get_db()
        error = None

        if not userid:
            error = 'User ID cannot be empty'
        elif userid != g.user['id'] and db.execute('SELECT EXISTS(SELECT 1 FROM users WHERE id=?)', [userid]).fetchone()[0]:
            error = 'User @{} already registered.'.format(userid)

        if error is None:
            if len(password) > 0:
                db.execute(
                    'UPDATE users SET password = ? WHERE id = ?',
                    (bcrypt.hashpw(password.encode(),
                                   bcrypt.gensalt()), g.user['id'])
                )

            db.execute(
                'UPDATE users SET (id, username) = (?, ?) WHERE id = ?',
                (userid, username, g.user['id'])
            )
            db.commit()
            flash(alerts.success('User information updated.'))
            return redirect('@' + userid)

        flash(alerts.error(error))

    return redirect('@' + g.user['id'])


@bp.route('/bookshelf')
@login_required
def bookshelf():
    db = get_db()
    booklist = db.execute(
        "SELECT books.id, account.sub_id, books.isbn, books.title, account.due, (julianday(account.due) - julianday('now')) AS time_left FROM account JOIN books ON user_id = ? AND (SELECT book_id FROM subbooks WHERE id = account.sub_id) = books.id",
        (g.user['id'],)
    ).fetchall()
    return render_template('user/bookshelf.html', booklist=booklist)


@bp.route('/return/<int:subid>')
@login_required
def return_book(subid):
    db = get_db()
    msg = None
    if not db.execute(
        'SELECT EXISTS(SELECT 1 FROM account WHERE sub_id = ? AND user_id = ?)',
        (subid, g.user['id'])
    ).fetchone()[0]:
        msg = alerts.error('Book not borrowed.')

    else:
        db.execute(
            'DELETE FROM account WHERE sub_id = ? AND user_id = ?',
            (subid, g.user['id'])
        )
        db.commit()
        msg = alerts.success('Book returned.')

    flash(msg)
    return redirect(url_for('library.bookshelf'))


@bp.route('/explore', defaults={'page': 0})
@bp.route('/explore/<int:page>')
def explore(page):
    db = get_db()
    booklist = get_db().execute(
        'SELECT id, isbn, title, (SELECT COUNT(*) FROM subbooks WHERE book_id = books.id) AS total, (SELECT COUNT(*) FROM account WHERE (SELECT book_id FROM subbooks WHERE id = account.sub_id) = books.id) AS borrowed FROM books LIMIT 10 * ?, 10',
        (page,)
    ).fetchall()
    pages = -(-db.execute(
        'SELECT COUNT(*) FROM books'
    ).fetchone()[0] // 10)

    return render_template('explore.html', booklist=booklist, page=page, pages=pages)


@bp.route('/book/<int:bookid>')
def book(bookid):
    db = get_db()
    book = db.execute(
        'SELECT * FROM books WHERE id = ?', (bookid,)
    ).fetchone()
    subbooks = db.execute(
        'SELECT id, location, (SELECT user_id FROM account WHERE sub_id = subbooks.id) AS borrower FROM subbooks WHERE book_id = ?',
        (bookid,)
    )
    return render_template('book.html', book=book, subbooks=subbooks)


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
@permission_required(least=0)
def sub_borrow(bookid, subid):
    db = get_db()
    if db.execute('SELECT EXISTS(SELECT 1 FROM account WHERE sub_id=?)', (subid,)).fetchone()[0]:
        flash(alerts.error('Book already borrowed.'))
        return redirect(url_for('library.borrow', bookid=bookid))

    db.execute(
        "INSERT INTO account (sub_id, user_id) VALUES (?, ?)",
        (subid, g.user['id'])
    )
    db.commit()
    flash(alerts.success('Successfully borrowed the book.'))
    return redirect(url_for('library.borrow', bookid=bookid))
