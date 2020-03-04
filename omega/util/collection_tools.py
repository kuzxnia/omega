import logging

log = logging.getLogger(__name__)


def row2dict(row):
    return {
        column.name: str(getattr(row, column.name)) for column in row.__table__.columns
    }


def copy_to(obj, data, excluded_props=None):
    if not excluded_props:
        excluded_props = []

    for key, value in data.items():
        if key not in excluded_props:
            setattr(obj, key, value)
    return obj
