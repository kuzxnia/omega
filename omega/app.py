import sys

from flask import Flask
from flask.logging import default_handler

from config import config_by_name
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

    def add_logging_handlers(self):
        import logging
        import logging.config

        # Set general log level
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.disable_existing_loggers = False

        # Add log file handler (if configured)
        path = self.config.get("LOGFILE")
        if path:
            handler = logging.handlers.RotatingFileHandler(path, "a", 10000, 4)
        else:
            handler = logging.StreamHandler(sys.stdout)

        handler.setLevel(logging.INFO)

        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )
        handler.setFormatter(file_formatter)

        self.logger.addHandler(handler)
        self.logger.removeHandler(default_handler)

    def add_celery(self):
        from omega.extensions import celery

        celery.init_app(self)


def create_app(*args, **kw):
    app = Omega(*args, **kw)
    app.add_logging_handlers()
    app.add_sqlalchemy()

    register_endpoints(app)

    return app


def create_celery_app(*args, **kw):
    app = create_app("omega.worker", *args, **kw)
    app.add_celery()
    return app
