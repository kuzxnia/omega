from omega.task.worker import celery
from celery.utils.log import get_task_logger

log = get_task_logger(__name__)


@celery.task
def fetch_watch_offers_since(date_from):
    pass


@celery.task
def fetch_watch_types():
    pass


@celery.task
def fetch_watch_brands():
    pass
