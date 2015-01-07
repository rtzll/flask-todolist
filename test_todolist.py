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


def test_no_user(client):
    user_resp = client.get('/user/1')
    assert b'No user here' in user_resp.data


def test_no_todo(client):
    todo_resp = client.get('/todo/1')
    assert b'No ToDo here' in todo_resp.data


def test_first_user(client):
    tony = todolist.User("Tony" "tony@email.me")
    client.db.session.commit(tony)
    user_resp = client.get('/user/1')
    assert b'Tony' in user_resp.data


def test_first_todo(client):
    tony = todolist.User("Tony" "tony@email.me")
    todo = todolist.Todo("Read all the emails.", tony)
