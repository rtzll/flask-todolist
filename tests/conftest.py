from contextlib import contextmanager

import pytest
from flask import template_rendered, url_for as flask_url_for

from app import create_app, db as _db


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def url_for(app):
    def _url_for(*args, **kwargs):
        with app.test_request_context():
            return flask_url_for(*args, **kwargs)

    return _url_for


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append(template.name)

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def templates(app):
    with captured_templates(app) as recorded:
        yield recorded
