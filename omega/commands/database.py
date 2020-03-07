import logging

from flask_script import Manager, prompt_bool
from omega.extensions import db

log = logging.getLogger(__name__)

manager = Manager(help="Perform database operations")


@manager.command
def create():
    """ Initialize the database by creating the necessary tables and indices """
    log.info("Initializing database, creating tables")
    db.create_all()
    # add statuses based on consts


@manager.command
def drop():
    """ Drops database tables """

    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()
