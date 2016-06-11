# -*- coding: utf-8 -*-

from app import create_app, db

app = create_app('development')


@app.cli.command()
def test():
    """Runs the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def fill_db():
    """Fills database with random data.
    By default 10 users, 40 todolists and 160 todos.
    WARNING: will delete existing data. For testing purposes only.
    """
    from utils.fake_generator import FakeGenerator
    FakeGenerator().start()  # side effect: deletes existing data
