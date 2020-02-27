from flask_script import Manager

from omega.app import create_celery_app
from omega.task.worker import celery

manager = Manager(help="Perform operations related to the Celery task queue")


@manager.command
def runworker():
    """ Runs the Celery background worker process """
    create_celery_app()
    celery.worker_main(["omega.task", "--loglevel=INFO"])
