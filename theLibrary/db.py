import sqlite3
import click
import bcrypt
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

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
    db.execute("INSERT INTO users VALUES ('root', ?, ?)", (password, username))
    db.commit()

    click.echo('Initialized the database.')


@click.command('test-db')
@with_appcontext
def testdb():
    db = get_db()
    db.executescript('''
INSERT INTO
  books (isbn, title, total)
VALUES
  ('978-7-12115-535-2', 'C++ Primer', 5);
INSERT INTO
  books (isbn, title, total)
VALUES
  (
    '978-0-87779-906-1',
    'The Merriam-Webster Dictionary of Synonyms and Antonyms',
    2
  );
INSERT INTO
  entries (user_id, type, book_id, detail)
VALUES
  ('root', 'N', 1, 'Amount: 5');
INSERT INTO
  entries (user_id, type, book_id, detail)
VALUES
  ('root', 'N', 2, 'Amount: 2');
    ''')
    db.commit()
    click.echo('Added books.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(testdb)
