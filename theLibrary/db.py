import sqlite3
import click
import bcrypt
from flask import current_app, g
from flask.cli import with_appcontext


def db_search(text, keywords):
    # TODO
    return 0


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.create_function("search", 2, db_search)
        g.db.execute('PRAGMA foreign_keys = ON')

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()

    db = get_db()
    username = input('Enter root name: ')
    password = bcrypt.hashpw(
        str.encode(input('Enter root password: ')),
        bcrypt.gensalt()
    )
    db.execute(
        "INSERT INTO users VALUES ('root', ?, ?, 1)",
        (password, username)
    )
    db.commit()

    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
