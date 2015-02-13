# -*- coding: utf-8 -*-

import unittest
import json

from flask import url_for

from app import create_app, db
from app.models import  User, Todo, TodoList


class TodolistAPITestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def assert404Response(self, response):
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['error'], 'Not found')

    @staticmethod
    def setup_new_user(username):
        user_data = {
            'username': username,
            'email': username + '@example.com',
            'password': 'correcthorsebatterystaple'
        }
        return user_data

    @staticmethod
    def get_headers():
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def add_user(self, username):
        user_data = self.setup_new_user(username)
        User(**user_data).save()
        return User.query.filter_by(username=username).first()

    @staticmethod
    def add_todolist(title, username=None):
        todolist = TodoList(title=title, creator=username).save()
        return TodoList.query.filter_by(id=todolist.id).first()

    def add_todo(self, description, todolist_id, username=None):
        todolist = TodoList.query.filter_by(id=todolist_id).first()
        todo = Todo(description=description, todolist_id=todolist.id,
                    creator=username).save()
        return Todo.query.filter_by(id=todo.id).first()

    def add_user_through_json_post(self, username):
        user_data = self.setup_new_user(username)
        return self.client.post(url_for('api.add_user'),
                                headers=self.get_headers(),
                                data=json.dumps(user_data))

    # test for errors
    def test_bad_request(self):
        post_response = self.client.post(url_for('api.add_user'),
                                         headers=self.get_headers(), data='')
        self.assertEqual(post_response.status_code, 400)

        json_response = json.loads(post_response.data.decode('utf-8'))
        self.assertEqual(json_response['error'], 'Bad Request')

    def test_not_found(self):
        response = self.client.get('/api/not/found')
        self.assert404Response(response)

    # test api post calls
    def test_add_user(self):
        username = 'adam'
        post_response = self.add_user_through_json_post(username)
        self.assertEqual(post_response.headers['Content-Type'],
                         'application/json')
        self.assertEqual(post_response.status_code, 201)

        response = self.client.get(url_for('api.get_users'))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['users'][0]['user']['username'],
                         username)

    def test_add_todolist(self):
        post_response = self.client.post(
            url_for('api.add_todolist'),
            headers=self.get_headers(),
            data=json.dumps({'title': 'todolist'})
        )
        self.assertEqual(post_response.status_code, 201)

        # the expected id of the todolist is 1, as it is the first to be added
        response = self.client.get(url_for('api.get_todolist', todolist_id=1))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['todolist']['title'], 'todolist')

    def test_add_user_todolist(self):
        username = 'adam'
        new_user = self.add_user(username)
        post_response = self.client.post(
            url_for('api.add_user_todolist', username=username),
            headers=self.get_headers(),
            data=json.dumps({'title': 'todolist'})
        )
        self.assertEqual(post_response.status_code, 201)

        response = self.client.get(url_for('api.get_user_todolists',
                                           username=username))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        # check title, creator are set correctly and a total of one todolist
        self.assertEqual(json_response['todolists'][0]['title'], 'todolist')
        self.assertEqual(json_response['todolists'][0]['creator'], username)
        self.assertEqual(len(json_response['todolists']), 1)

    def test_add_user_todolist_todo(self):
        username = 'adam'
        todolist_title = 'new todolist'
        new_user = self.add_user(username)
        new_todolist = self.add_todolist(todolist_title, username)

        post_response = self.client.post(
            url_for('api.add_user_todolist_todo',
                    username=username, todolist_id=new_todolist.id),
            headers=self.get_headers(),
            data=json.dumps({
                'description': 'new todo',
                'creator': username,
                'todolist_id': new_todolist.id
            })
        )
        self.assertEqual(post_response.status_code, 201)

        response = self.client.get(url_for('api.get_user_todolist_todos',
                                           username=username,
                                           todolist_id=new_todolist.id))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        # check title, creator are set correctly and a total of one todo
        self.assertEqual(json_response['todos'][0]['description'], 'new todo')
        self.assertEqual(json_response['todos'][0]['creator'], username)
        self.assertEqual(len(json_response['todos']), 1)

    def test_add_todolist_todo(self):
        new_todolist = TodoList().save()  # todolist with default title

        post_response = self.client.post(
            url_for('api.add_todolist_todo', todolist_id=new_todolist.id),
            headers=self.get_headers(),
            data=json.dumps({
                'description': 'new todo',
                'creator': 'null',
                'todolist_id': new_todolist.id
            })
        )
        self.assertEqual(post_response.status_code, 201)

        response = self.client.get(url_for('api.get_todolist_todos',
                                           todolist_id=new_todolist.id))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        # check title, creator are set correctly and a total of one todo
        self.assertEqual(json_response['todos'][0]['description'], 'new todo')
        self.assertEqual(json_response['todos'][0]['creator'], None)
        self.assertEqual(len(json_response['todos']), 1)

    # test api get calls
    def test_get_users(self):
        username = 'adam'
        new_user = self.add_user(username)
        response = self.client.get(url_for('api.get_users'))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['users'][0]['user']['username'],
                         username)

    def test_get_users_when_no_users_exist(self):
        response = self.client.get(url_for('api.get_users'))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['users'], [])

    def test_get_user(self):
        username = 'adam'
        new_user = self.add_user(username)
        response = self.client.get(url_for('api.get_user', username=username))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['user']['username'], username)

    def test_get_user_when_user_does_not_exist(self):
        username = 'adam'
        response = self.client.get(url_for('api.get_user', username=username))
        self.assert404Response(response)

    def test_get_todolists(self):
        username = 'adam'
        todolist_title = 'new todolist '
        new_user = self.add_user(username)
        first_todolist = self.add_todolist(todolist_title + '1', username)
        second_todolist = self.add_todolist(todolist_title + '2', username)

        response = self.client.get(url_for('api.get_todolists'))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['todolists'][0]['title'],
                         'new todolist 1')
        self.assertEqual(json_response['todolists'][0]['creator'], username)
        self.assertEqual(json_response['todolists'][1]['title'],
                         'new todolist 2')
        self.assertEqual(json_response['todolists'][1]['creator'], username)
        self.assertEqual(len(json_response['todolists']), 2)

    def test_get_todolists_when_no_todolists_exist(self):
        response = self.client.get(url_for('api.get_todolists'))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['todolists'], [])
        self.assertEqual(len(json_response['todolists']), 0)

    def test_get_user_todolists(self):
        username = 'adam'
        todolist_title = 'new todolist '
        new_user = self.add_user(username)
        first_todolist = self.add_todolist(todolist_title + '1', username)
        second_todolist = self.add_todolist(todolist_title + '2', username)

        response = self.client.get(url_for('api.get_user_todolists',
                                           username=username))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['todolists'][0]['title'],
                         'new todolist 1')
        self.assertEqual(json_response['todolists'][0]['creator'], username)
        self.assertEqual(json_response['todolists'][1]['title'],
                         'new todolist 2')
        self.assertEqual(json_response['todolists'][1]['creator'], username)
        self.assertEqual(len(json_response['todolists']), 2)

    def test_get_user_todolists_when_user_does_not_exist(self):
        username = 'adam'
        response = self.client.get(url_for('api.get_user_todolists',
                                           username=username))
        self.assert404Response(response)

    def test_get_user_todolists_when_user_has_no_todolists(self):
        username = 'adam'
        new_user = self.add_user(username)
        response = self.client.get(url_for('api.get_user_todolists',
                                           username=username))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['todolists'], [])
        self.assertEqual(len(json_response['todolists']), 0)

    def test_get_todolist_todos(self):
        todolist_title = 'new todolist'
        new_todolist = self.add_todolist(todolist_title)

        first_todo = self.add_todo('first', new_todolist.id)
        second_todo = self.add_todo('second', new_todolist.id)

        response = self.client.get(url_for('api.get_todolist_todos',
                                           todolist_id=new_todolist.id))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['todos'][0]['description'], 'first')
        self.assertEqual(json_response['todos'][0]['creator'], None)
        self.assertEqual(json_response['todos'][1]['description'], 'second')
        self.assertEqual(json_response['todos'][1]['creator'], None)
        self.assertEqual(len(json_response['todos']), 2)

    def test_get_todolist_todos_when_todolist_does_not_exist(self):
        response = self.client.get(url_for('api.get_todolist_todos',
                                           todolist_id=1))
        self.assert404Response(response)

    def test_get_todolist_todos_when_todolist_has_no_todos(self):
        todolist_title = 'new todolist'
        new_todolist = self.add_todolist(todolist_title)
        response = self.client.get(url_for('api.get_todolist_todos',
                                           todolist_id=new_todolist.id))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['todos'], [])
        self.assertEqual(len(json_response['todos']), 0)

    def test_get_user_todolist_todos(self):
        username = 'adam'
        todolist_title = 'new todolist'
        new_user = self.add_user(username)
        new_todolist = self.add_todolist(todolist_title, username)

        first_todo = self.add_todo('first', new_todolist.id, username)
        second_todo = self.add_todo('second', new_todolist.id, username)

        response = self.client.get(url_for('api.get_user_todolist_todos',
                                           username=username,
                                           todolist_id=new_todolist.id))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['todos'][0]['description'], 'first')
        self.assertEqual(json_response['todos'][0]['creator'], username)
        self.assertEqual(json_response['todos'][1]['description'], 'second')
        self.assertEqual(json_response['todos'][1]['creator'], username)
        self.assertEqual(len(json_response['todos']), 2)

    def test_get_user_todolist_todos_when_user_does_not_exist(self):
        username = 'adam'
        response = self.client.get(url_for('api.get_user_todolist_todos',
                                           username=username, todolist_id=1))
        self.assert404Response(response)

    def test_get_user_todolist_todos_when_todolist_does_not_exist(self):
        username = 'adam'
        new_user = self.add_user(username)

        response = self.client.get(url_for('api.get_user_todolist_todos',
                                           username=username, todolist_id=1))
        self.assert404Response(response)

    def test_get_user_todolist_todos_when_todolist_has_no_todos(self):
        username = 'adam'
        todolist_title = 'new todolist'
        new_user = self.add_user(username)
        new_todolist = self.add_todolist(todolist_title, username)

        response = self.client.get(url_for('api.get_user_todolist_todos',
                                           username=username,
                                           todolist_id=new_todolist.id))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['todos'], [])
        self.assertEqual(len(json_response['todos']), 0)

    def test_get_user_todolist_todos_when_todolist_does_not_belong_to_user(self):
        first_username = 'adam'
        second_username = 'ben'
        todolist_title = 'new todolist'
        first_user = self.add_user(first_username)
        second_user = self.add_user(second_username)
        new_todolist = self.add_todolist(todolist_title, second_username)

        first_todo = self.add_todo('first', new_todolist.id, second_username)
        second_todo = self.add_todo('second', new_todolist.id, second_username)

        response = self.client.get(url_for('api.get_user_todolist_todos',
                                            username=first_user,
                                           todolist_id=new_todolist.id))
        self.assert404Response(response)

    def test_get_user_todolist(self):
        username = 'adam'
        todolist_title = 'new todolist'
        new_user = self.add_user(username)
        new_todolist = self.add_todolist(todolist_title, username)

        response = self.client.get(url_for('api.get_user_todolist',
                                           username=username,
                                           todolist_id=new_todolist.id))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['todolist']['title'], todolist_title)
        self.assertEqual(json_response['todolist']['creator'], username)

    def test_get_user_todolist_when_user_does_not_exist(self):
        username = 'adam'
        response = self.client.get(url_for('api.get_user_todolist',
                                           username=username,
                                           todolist_id=1))
        self.assert404Response(response)

    def test_get_user_todolist_when_todolist_does_not_exist(self):
        username = 'adam'
        new_user = self.add_user(username)
        response = self.client.get(url_for('api.get_user_todolist',
                                           username=username,
                                           todolist_id=1))
        self.assert404Response(response)
