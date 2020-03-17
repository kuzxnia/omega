import logging
import logging.config
import sys

from config import config_by_name
from flask import Flask
from omega.routes import register_endpoints


class Omega(Flask):
    # response_class = JsonResponse

    def __init__(self, name="omega", config_name="dev", *args, **kw):
        # Create Flask instance
        super(Omega, self).__init__(name, *args, **kw)

        # Load default settings and from environment variable
        self.config.from_object(config_by_name[config_name])

    def add_sqlalchemy(self):
        """ Create and configure SQLAlchemy extension """
        from omega.extensions import db

        db.init_app(self)

    def add_cache(self):
        """ Create and attach Cache extension """
        from omega.extensions import cache

        cache.init_app(self)

    def logging_config(self):
        self.logger.propagate = False
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": sys.stdout,
                }
            },
            "root": {"level": logging.DEBUG, "handlers": ["console"]},
            "loggers": {
                "default": {"level": logging.DEBUG, "handlers": ["console"]},
                "omega": {"level": logging.DEBUG, "handlers": ["console"]},
            },
        }

    def add_celery(self):
        from omega.worker import celery

        celery.init_app(self)


def create_app(*args, **kw):
    app = Omega(*args, **kw)
    logging.config.dictConfig(app.logging_config())

    with app.app_context():
        app.add_sqlalchemy()
        register_endpoints(app)

    return app


def create_celery_app(*args, **kw):
    app = create_app("omega.worker", *args, **kw)
    app.add_celery()
    return app
