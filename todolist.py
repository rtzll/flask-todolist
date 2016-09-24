# -*- coding: utf-8 -*-

from app import create_app

app = create_app('development')


@app.cli.command()
def test():
    """Runs the unit tests."""
    import unittest
    import sys
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.errors or result.failures:
        sys.exit(1)


@app.cli.command()
def fill_db():
    """Fills database with random data.
    By default 10 users, 40 todolists and 160 todos.
    WARNING: will delete existing data. For testing purposes only.
    """
    from utils.fake_generator import FakeGenerator
    FakeGenerator().start()  # side effect: deletes existing data
