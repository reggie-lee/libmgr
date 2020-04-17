import bcrypt
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from theLibrary.auth import login_required, permission_required
from theLibrary.db import get_db
import theLibrary.alerts as alerts

bp = Blueprint('librarian', __name__)


@bp.route('/librarian')
@permission_required(least=1)
def librarian():
    userlist = get_db().execute('SELECT * FROM users')
    return render_template('librarian/librarian.html', userlist=userlist)


@bp.route('/librarian/add/book', methods=('GET', 'POST'))
def add_book():
    if request.method == 'POST':
        db = get_db()
        db.execute(
            '''INSERT INTO books (
                isbn,
                language,
                title,
                publisher,
                shape,
                summary,
                othertitles,
                subject,
                author
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                request.form['isbn'],
                request.form['language'],
                request.form['title'],
                request.form['publisher'],
                request.form['shape'],
                request.form['summary'],
                request.form['othertitles'],
                request.form['subject'],
                request.form['author']
            )
        )
        db.commit()
        bookid = db.execute(
            'SELECT seq FROM sqlite_sequence WHERE name="books"'
        ).fetchone()[0]
        flash(alerts.success('Successfully added.'))
        return redirect(url_for('librarian.edit_book', bookid=bookid))

    return render_template('librarian/addbook.html')


@bp.route('/librarian/add/subbook/<bookid>', methods=('POST',))
@permission_required(least=1)
def add_subbook(bookid):
    db = get_db()
    amount = int(request.form['amount'])
    for _ in range(0, amount):
        db.execute(
            'INSERT INTO subbooks (book_id, location) VALUES (?, ?)',
            (bookid, request.form['location'])
        )
    db.commit()

    flash(alerts.success('Successfully added.'))
    return redirect(url_for('librarian.edit_book', bookid=bookid))


@bp.route('/librarian/edit/user@<orid>', methods=('GET', 'POST'))
@permission_required(least=1)
def edit_user(orid):
    db = get_db()
    if not db.execute('SELECT EXISTS(SELECT 1 FROM users WHERE id=?)', [orid]).fetchone()[0]:
        abort(500)

    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        permission = request.form['permission']

        error = None

        if not orid:
            error = 'User ID cannot be empty'

        if error is None:
            if len(password) > 0:
                db.execute(
                    'UPDATE users SET password = ? WHERE id = ?',
                    (bcrypt.hashpw(password.encode(), bcrypt.gensalt()), orid)
                )

            if permission is not None:
                db.execute(
                    'UPDATE users SET permission = ? WHERE id = ?',
                    (int(permission), orid)
                )

            db.execute(
                'UPDATE users SET username = ? WHERE id = ?',
                (username, orid)
            )
            db.commit()
            flash(alerts.success('User information updated.'))
            if orid == session['id']:
                session['username'] = username
            return redirect('/librarian/edit/user@' + orid)

        flash(alerts.error(error))

    user = get_db().execute(
        "SELECT * FROM users WHERE id=?", [orid]
    ).fetchone()
    return render_template('librarian/edituser.html', user=user)


@bp.route('/librarian/edit/book/<bookid>', methods=('GET', 'POST'))
@permission_required(least=1)
def edit_book(bookid):
    db = get_db()
    if not db.execute('SELECT EXISTS(SELECT 1 FROM books WHERE id=?)', [bookid]).fetchone()[0]:
        flash(alerts.error('No such book.'))
        return redirect(url_for('library.explore'))

    if request.method == 'POST':
        db.execute(
            '''UPDATE books SET (
                isbn,
                language,
                title,
                publisher,
                shape,
                summary,
                othertitles,
                subject,
                author
            ) = (?, ?, ?, ?, ?, ?, ?, ?, ?) WHERE id = ?''',
            (
                request.form['isbn'],
                request.form['language'],
                request.form['title'],
                request.form['publisher'],
                request.form['shape'],
                request.form['summary'],
                request.form['othertitles'],
                request.form['subject'],
                request.form['author'],
                bookid
            )
        )
        db.commit()
        flash(alerts.success('Successfully updated.'))
        return redirect(url_for('librarian.edit_book', bookid=bookid))

    book = db.execute(
        'SELECT * FROM books WHERE id = ?', (bookid,)
    ).fetchone()
    subbooks = db.execute(
        'SELECT id, location, (SELECT user_id FROM account WHERE sub_id = subbooks.id) AS borrower FROM subbooks WHERE book_id = ?',
        (bookid,)
    )
    return render_template('librarian/editbook.html', book=book, subbooks=subbooks)
