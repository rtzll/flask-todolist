# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy

from app import create_app, db

app = create_app('development')


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def fill_db():
    """Fill database with random data.
    By default 100 users, 400 todolists and 1600 todos.
    WARNING: will delete existing data. For testing purposes only.
    """
    from utils.fake_generator import FakeGenerator
    FakeGenerator().start()  # side effect: deletes existing data


if __name__ == '__main__':
    manager.run()
