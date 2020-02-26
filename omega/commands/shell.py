from flask import current_app
from flask_script import Shell as BaseShell

from omega import extensions, model


def make_context():
    return dict(app=current_app, model=model, db=extensions.db)


class Shell(BaseShell):
    def __init__(self, *args, **kw):
        super(Shell, self).__init__(make_context=make_context, *args, **kw)
