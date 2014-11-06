from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
import os

from hie_connect.hie import app, db
import hie_connect.models

app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()