import logging

from flask_script import Manager
from omega.worker import tasks

log = logging.getLogger(__name__)

manager = Manager(help="Perform watch operations")


@manager.command
def fetch_watch_offers_since(date_from=None):
    tasks.fetch_watch_offers_since.delay(date_from)


@manager.command
def fetch_watch_types():
    tasks.fetch_watch_types()  # .delay()


@manager.command
def fetch_watch_brands():
    tasks.fetch_watch_brands()  # .delay()
