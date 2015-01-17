# -*- coding: utf-8 -*-

from flask.ext.script import Manager
from app import create_app, db


app = create_app('testing')
manager = Manager(app)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def initdb():
    """Creates all database tables."""
    db.create_all()


@manager.command
def dropdb():
    """Drops all database tables."""
    db.drop_all()


if __name__ == '__main__':
    manager.run()
