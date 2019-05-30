import bcrypt
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from theLibrary.auth import login_required, permission_required
from theLibrary.db import get_db

bp = Blueprint('librarian', __name__)


@bp.route('/librarian')
@login_required
@permission_required
def librarian():
    userlist = get_db().execute('SELECT * FROM users')
    return render_template('librarian/librarian.html', userlist=userlist)


@bp.route('/librarian/edit/user@<orid>', methods=('GET', 'POST'))
@login_required
@permission_required
def edit_user(orid):
    db = get_db()
    if not db.execute('SELECT EXISTS(SELECT 1 FROM users WHERE id=?)', [orid]).fetchone()[0]:
        abort(500)

    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        username = request.form['username']

        error = None

        if not userid:
            error = 'User ID cannot be empty'
        elif userid != orid and db.execute('SELECT EXISTS(SELECT 1 FROM users WHERE id=?)', [userid]).fetchone()[0]:
            error = 'User @{} already registered.'.format(userid)

        if error is None:
            if len(password) > 0:
                db.execute(
                    'UPDATE users SET password = ? WHERE id = ?',
                    (bcrypt.hashpw(password.encode(), bcrypt.gensalt()), orid)
                )

            db.execute(
                'UPDATE users SET (id, username) = (?, ?) WHERE id = ?',
                (userid, username, orid)
            )
            db.commit()
            flash('User information updated.')
            return redirect('/librarian/edit/user@' + userid)

        flash(error)

    user = get_db().execute(
        "SELECT * FROM users WHERE id=?", [orid]
    ).fetchone()
    return render_template('librarian/edituser.html', user=user)
