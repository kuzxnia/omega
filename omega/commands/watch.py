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


@manager.command
def fetch_currency():
    tasks.fetch_currency()  # .delay()


@manager.command
def fetch_scopes_of_delivery():
    tasks.fetch_scopes_of_delivery()  # .delay()


@manager.command
def fetch_watch_conditions():
    tasks.fetch_watch_conditions()  # .delay()
