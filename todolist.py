from app import create_app
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app("development")


@app.cli.command()
def test():
    """Runs the unit tests."""
    import pytest

    raise SystemExit(pytest.main(["-v"]))


@app.cli.command()
def fill_db():
    """Fills database with random data.
    By default 10 users, 40 todolists and 160 todos.
    WARNING: will delete existing data. For testing purposes only.
    """
    from utils.fake_generator import FakeGenerator

    FakeGenerator().start()  # side effect: deletes existing data
