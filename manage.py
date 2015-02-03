# -*- coding: utf-8 -*-

from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy

from app import create_app, db


app = create_app('development')
manager = Manager(app)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def fill_db():
    from fake_generator import FakeGenerator
    FakeGenerator().generate_fake_data()


if __name__ == '__main__':
    manager.run()
