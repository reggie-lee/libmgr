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


@click.command('test-db')
@with_appcontext
def testdb():
    db = get_db()
    db.executescript('''
INSERT INTO
  books (isbn, title)
VALUES
  ('978-7-12115-535-2', 'C++ Primer');
INSERT INTO subbooks (book_id) VALUES (1);
INSERT INTO subbooks (book_id) VALUES (1);
INSERT INTO subbooks (book_id) VALUES (1);
INSERT INTO subbooks (book_id) VALUES (1);
INSERT INTO subbooks (book_id) VALUES (1);
INSERT INTO
  books (isbn, title)
VALUES
  (
    '978-0-87779-906-1',
    'The Merriam-Webster Dictionary of Synonyms and Antonyms'
  );
INSERT INTO subbooks (book_id) VALUES (2);
INSERT INTO subbooks (book_id) VALUES (2);
INSERT INTO
  account (sub_id, user_id)
VALUES
  (1, 'root');
INSERT INTO
  account (sub_id, user_id)
VALUES
  (6, 'root');
INSERT INTO
  account (sub_id, user_id)
VALUES
  (7, 'root');
    ''')
    db.commit()
    click.echo('Added books.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(testdb)
