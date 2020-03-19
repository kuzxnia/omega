from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from omega.app import create_app
from omega.extensions import db

from .celery import manager as celery_manager
from .database import manager as database_manager
from .server import Server
from .shell import Shell
from .watch import manager as watch_manager


def _create_app():
    app = create_app()
    app.migrate = Migrate(app, db)
    return app


manager = Manager(_create_app)
manager.add_command("shell", Shell())
manager.add_command("runserver", Server(host="0.0.0.0"))
manager.add_command("migrate", MigrateCommand)
manager.add_command("celery", celery_manager)
manager.add_command("db", database_manager)
manager.add_command("watch", watch_manager)
