#!/bin/python3
import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(16),
        DATABASE=os.path.join(app.instance_path, 'library.db')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from theLibrary import db
    db.init_app(app)

    from theLibrary import auth, library, librarian
    app.register_blueprint(auth.bp)
    app.register_blueprint(library.bp)
    app.register_blueprint(librarian.bp)

    app.add_url_rule('/', endpoint='index')

    return app
