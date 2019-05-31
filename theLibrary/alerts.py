from flask import Markup


def success(msg):
    return Markup('''<div class="alert alert-success alert-dismissible fade show">
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    <strong>Success:</strong> {}</div>'''.format(msg))


def error(msg):
    return Markup('''<div class="alert alert-danger alert-dismissible fade show">
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    <strong>Error:</strong> {}</div>'''.format(msg))
