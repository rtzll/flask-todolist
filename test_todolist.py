# -*- coding: utf-8 -*-

import pytest

import os
import todolist
import tempfile

import manage

@pytest.fixture
def client(request):
    db_fd, todolist.app.config['DATABASE'] = tempfile.mkstemp()
    todolist.app.config['TESTING'] = True
    client = todolist.app.test_client()
    with todolist.app.app_context():
        manage.initdb()

    def teardown():
        os.close(db_fd)
        os.unlink(todolist.app.config['DATABASE'])
    request.addfinalizer(teardown)

    return client

def test_empty_db(client):
    user_resp = client.get('/user/1')
    todo_resp = client.get('/todo/1')
    assert b'No user here' in user_resp
    assert b'No todo here' in todo_resp
    assert 0 == 1
