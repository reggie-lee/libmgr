# theLibrary

## Requirement

- python3
- flask (Python3 package)
- bcrypt (Python3 package)

## Setup

First initialize the database.

```shell
FLASK_APP=theLibrary flask init-db
```

If you want some test data, run

```shell
./tests/test.py
```

Then run the server.

```shell
FLASK_APP=theLibrary flask run
```

You can also run it with a WSGI server. For example, `Waitress`:

```shell
waitress-serve --call 'theLibrary:create_app'
```
