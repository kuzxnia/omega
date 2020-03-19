from functools import wraps

from flask.globals import _app_ctx_stack


def copy_current_app_context(func):
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError(
            "This decorator can only be used at local scopes "
            "when a app context is on the stack. Usefull in "
            "working with greenlets."
        )

    @wraps(func)
    def wrapper(*args, **kwargs):
        with top:
            return func(*args, **kwargs)
    return wrapper
