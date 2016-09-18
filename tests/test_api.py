# -*- coding: utf-8 -*-

import json
import unittest
from datetime import datetime

from flask_testing import TestCase
from flask import url_for

from app import create_app, db
from app.models import User, Todo, TodoList


class TodolistAPITestCase(TestCase):

    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def assert404Response(self, response):
        self.assert_404(response)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['error'], 'Not found')

    def assert400Response(self, response):
        self.assert_400(response)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['error'], 'Bad Request')

    def assert500Response(self, response):
        self.assert_500(response)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['error'], 'Internal Server Error')

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

    def test_main_route(self):
        response = self.client.get(url_for('api.get_routes'))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue('users' in json_response)
        self.assertTrue('todolists' in json_response)

    def test_not_found(self):
        response = self.client.get('/api/not/found')
        self.assert404Response(response)

    # test api post calls
    def test_add_user(self):
        username = 'adam'
        post_response = self.add_user_through_json_post(username)
        self.assertEqual(post_response.headers['Content-Type'],
                         'application/json')
        self.assert_status(post_response, 201)

        response = self.client.get(url_for('api.get_users'))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['users'][0]['user']['username'],
                         username)

    def test_add_user_only_using_the_username(self):
        user_data = {'username': 'adam'}
        response = self.client.post(url_for('api.add_user'),
                                    headers=self.get_headers(),
                                    data=json.dumps(user_data))
        self.assert500Response(response)

    def test_add_user_only_using_the_username_and_email(self):
        user_data = {'username': 'adam', 'email': 'adam@example.com'}
        response = self.client.post(url_for('api.add_user'),
                                    headers=self.get_headers(),
                                    data=json.dumps(user_data))
        self.assert500Response(response)

    def test_add_user_with_to_long_username(self):
        user_data = {
            'username': 65 * 'a',
            'email':  'adam@example.com',
            'password': 'correcthorsebatterystaple',
        }
        response = self.client.post(url_for('api.add_user'),
                                    headers=self.get_headers(),
                                    data=json.dumps(user_data))
        self.assert500Response(response)

    def test_add_user_with_invalid_username(self):
        user_data = {
            'username': 'not a valid username',
            'email':  'adam@example.com',
            'password': 'correcthorsebatterystaple',
        }
        response = self.client.post(url_for('api.add_user'),
                                    headers=self.get_headers(),
                                    data=json.dumps(user_data))
        self.assert500Response(response)

    def test_add_user_without_username(self):
        user_data = {
            'username': '',
            'email':  'adam@example.com',
            'password': 'correcthorsebatterystaple',
        }
        response = self.client.post(url_for('api.add_user'),
                                    headers=self.get_headers(),
                                    data=json.dumps(user_data))
        self.assert500Response(response)

    def test_add_user_with_invalid_email(self):
        user_data = {
            'username': 'adam',
            'email':  'adamexample.com',
            'password': 'correcthorsebatterystaple',
        }
        response = self.client.post(url_for('api.add_user'),
                                    headers=self.get_headers(),
                                    data=json.dumps(user_data))
        self.assert500Response(response)

    def test_add_user_withoout_email(self):
        user_data = {
            'username': 'adam',
            'email':  '',
            'password': 'correcthorsebatterystaple',
        }
        response = self.client.post(url_for('api.add_user'),
                                    headers=self.get_headers(),
                                    data=json.dumps(user_data))
        self.assert500Response(response)

    def test_add_user_with_too_long_email(self):
        user_data = {
            'username': 'adam',
            'email':  53 * 'a' + '@example.com',
            'password': 'correcthorsebatterystaple',
        }
        response = self.client.post(url_for('api.add_user'),
                                    headers=self.get_headers(),
                                    data=json.dumps(user_data))
        self.assert500Response(response)

    def test_add_user_without_password(self):
        user_data = {
            'username': 'adam',
            'email':  'adam@example.com',
            'password': '',
        }
        response = self.client.post(url_for('api.add_user'),
                                    headers=self.get_headers(),
                                    data=json.dumps(user_data))
        self.assert500Response(response)

    def test_add_user_with_extra_fields(self):
        user_data = {
            'username': 'adam',
            'email': 'adam@example.com',
            'password': 'correcthorsebatterystaple',
            'extra-field': 'will be ignored'
        }
        post_response = self.client.post(url_for('api.add_user'),
                                         headers=self.get_headers(),
                                         data=json.dumps(user_data))
        self.assertEqual(post_response.headers['Content-Type'],
                         'application/json')
        self.assert_status(post_response, 201)

        response = self.client.get(url_for('api.get_users'))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['users'][0]['user']['username'],
                         'adam')

    def test_add_user_only_using_the_username_and_password(self):
        user_data = {
            'username': 'adam', 'password': 'correcthorsebatterystaple'
        }
        response = self.client.post(url_for('api.add_user'),
                                    headers=self.get_headers(),
                                    data=json.dumps(user_data))
        self.assert500Response(response)

    def test_add_todolist(self):
        post_response = self.client.post(
            url_for('api.add_todolist'),
            headers=self.get_headers(),
            data=json.dumps({'title': 'todolist'})
        )
        self.assert_status(post_response, 201)

        # the expected id of the todolist is 1, as it is the first to be added
        response = self.client.get(url_for('api.get_todolist', todolist_id=1))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['todolist']['title'], 'todolist')

    def test_add_todolist_without_title(self):
        response = self.client.post(
            url_for('api.add_todolist'),
            headers=self.get_headers()
        )
        # opposed to the form, the title is a required argument
        self.assert500Response(response)

    def test_add_todolist_with_too_long_title(self):
        response = self.client.post(
            url_for('api.add_todolist'),
            headers=self.get_headers(),
            data=json.dumps({'title': 129 * 't'})
        )
        self.assert500Response(response)

    def test_add_user_todolist(self):
        username = 'adam'
        self.add_user(username)
        post_response = self.client.post(
            url_for('api.add_user_todolist', username=username),
            headers=self.get_headers(),
            data=json.dumps({'title': 'todolist'})
        )
        self.assert_status(post_response, 201)

        response = self.client.get(url_for('api.get_user_todolists',
                                           username=username))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))

        # check title, creator are set correctly and a total of one todolist
        self.assertEqual(json_response['todolists'][0]['title'], 'todolist')
        self.assertEqual(json_response['todolists'][0]['creator'], username)
        self.assertEqual(len(json_response['todolists']), 1)

    def test_add_user_todolist_when_user_does_not_exist(self):
        username = 'adam'
        post_response = self.client.post(
            url_for('api.add_user_todolist', username=username),
            headers=self.get_headers(),
            data=json.dumps({'title': 'todolist'})
        )
        self.assert404Response(post_response)

    def test_add_user_todolist_todo(self):
        username = 'adam'
        todolist_title = 'new todolist'
        self.add_user(username)
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
        self.assert_status(post_response, 201)

        response = self.client.get(url_for('api.get_user_todolist_todos',
                                           username=username,
                                           todolist_id=new_todolist.id))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))

        # check title, creator are set correctly and a total of one todo
        self.assertEqual(json_response['todos'][0]['description'], 'new todo')
        self.assertEqual(json_response['todos'][0]['creator'], username)
        self.assertEqual(len(json_response['todos']), 1)

    def test_add_user_todolist_todo_when_todolist_does_not_exist(self):
        username = 'adam'
        self.add_user(username)

        post_response = self.client.post(
            url_for('api.add_user_todolist_todo',
                    username=username, todolist_id=1),
            headers=self.get_headers(),
            data=json.dumps({
                'description': 'new todo',
                'creator': username,
                'todolist_id': 1
            })
        )
        self.assert404Response(post_response)

    def test_add_user_todolist_todo_without_todo_data(self):
        username = 'adam'
        todolist_title = 'new todolist'
        self.add_user(username)
        new_todolist = self.add_todolist(todolist_title, username)

        post_response = self.client.post(
            url_for('api.add_user_todolist_todo',
                    username=username, todolist_id=new_todolist.id),
            headers=self.get_headers()
        )
        self.assert500Response(post_response)

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
        self.assert_status(post_response, 201)

        response = self.client.get(url_for('api.get_todolist_todos',
                                           todolist_id=new_todolist.id))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))

        # check title, creator are set correctly and a total of one todo
        self.assertEqual(json_response['todos'][0]['description'], 'new todo')
        self.assertEqual(json_response['todos'][0]['creator'], None)
        self.assertEqual(len(json_response['todos']), 1)

    def test_add_todolist_todo_when_todolist_does_not_exist(self):
        post_response = self.client.post(
            url_for('api.add_todolist_todo', todolist_id=1),
            headers=self.get_headers(),
            data=json.dumps({
                'description': 'new todo',
                'creator': 'null',
                'todolist_id': 1
            })
        )
        self.assert404Response(post_response)

    def test_add_todolist_todo_without_todo_data(self):
        new_todolist = TodoList().save()
        post_response = self.client.post(
            url_for('api.add_todolist_todo', todolist_id=new_todolist.id),
            headers=self.get_headers()
        )
        self.assert500Response(post_response)

    # test api get calls
    def test_get_users(self):
        username = 'adam'
        self.add_user(username)
        response = self.client.get(url_for('api.get_users'))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['users'][0]['user']['username'],
                         username)

    def test_get_users_when_no_users_exist(self):
        response = self.client.get(url_for('api.get_users'))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['users'], [])

    def test_get_user(self):
        username = 'adam'
        self.add_user(username)
        response = self.client.get(url_for('api.get_user', username=username))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['user']['username'], username)

    def test_get_user_when_user_does_not_exist(self):
        username = 'adam'
        response = self.client.get(url_for('api.get_user', username=username))
        self.assert404Response(response)

    def test_get_todolists(self):
        username = 'adam'
        todolist_title = 'new todolist '
        self.add_user(username)
        self.add_todolist(todolist_title + '1', username)
        self.add_todolist(todolist_title + '2', username)

        response = self.client.get(url_for('api.get_todolists'))
        self.assert_200(response)

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
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['todolists'], [])
        self.assertEqual(len(json_response['todolists']), 0)

    def test_get_user_todolists(self):
        username = 'adam'
        todolist_title = 'new todolist '
        self.add_user(username)
        self.add_todolist(todolist_title + '1', username)
        self.add_todolist(todolist_title + '2', username)

        response = self.client.get(url_for('api.get_user_todolists',
                                           username=username))
        self.assert_200(response)

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
        self.add_user(username)
        response = self.client.get(url_for('api.get_user_todolists',
                                           username=username))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['todolists'], [])
        self.assertEqual(len(json_response['todolists']), 0)

    def test_get_todolist_todos(self):
        todolist_title = 'new todolist'
        new_todolist = self.add_todolist(todolist_title)

        self.add_todo('first', new_todolist.id)
        self.add_todo('second', new_todolist.id)

        response = self.client.get(url_for('api.get_todolist_todos',
                                           todolist_id=new_todolist.id))
        self.assert_200(response)

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
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['todos'], [])
        self.assertEqual(len(json_response['todos']), 0)

    def test_get_user_todolist_todos(self):
        username = 'adam'
        todolist_title = 'new todolist'
        self.add_user(username)
        new_todolist = self.add_todolist(todolist_title, username)

        self.add_todo('first', new_todolist.id, username)
        self.add_todo('second', new_todolist.id, username)

        response = self.client.get(url_for('api.get_user_todolist_todos',
                                           username=username,
                                           todolist_id=new_todolist.id))
        self.assert_200(response)

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
        self.add_user(username)

        response = self.client.get(url_for('api.get_user_todolist_todos',
                                           username=username, todolist_id=1))
        self.assert404Response(response)

    def test_get_user_todolist_todos_when_todolist_has_no_todos(self):
        username = 'adam'
        todolist_title = 'new todolist'
        self.add_user(username)
        new_todolist = self.add_todolist(todolist_title, username)

        response = self.client.get(url_for('api.get_user_todolist_todos',
                                           username=username,
                                           todolist_id=new_todolist.id))
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['todos'], [])
        self.assertEqual(len(json_response['todos']), 0)

    def test_get_different_user_todolist_todos(self):
        first_username = 'adam'
        second_username = 'ben'
        todolist_title = 'new todolist'
        first_user = self.add_user(first_username)
        self.add_user(second_username)
        new_todolist = self.add_todolist(todolist_title, second_username)

        self.add_todo('first', new_todolist.id, second_username)
        self.add_todo('second', new_todolist.id, second_username)

        response = self.client.get(url_for('api.get_user_todolist_todos',
                                           username=first_user,
                                           todolist_id=new_todolist.id))
        self.assert404Response(response)

    def test_get_user_todolist(self):
        username = 'adam'
        todolist_title = 'new todolist'
        self.add_user(username)
        new_todolist = self.add_todolist(todolist_title, username)

        response = self.client.get(url_for('api.get_user_todolist',
                                           username=username,
                                           todolist_id=new_todolist.id))
        self.assert_200(response)

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
        self.add_user(username)
        response = self.client.get(url_for('api.get_user_todolist',
                                           username=username,
                                           todolist_id=1))
        self.assert404Response(response)

    # test api put call
    def test_update_todo_status_to_finished(self):
        todolist = self.add_todolist('new todolist')
        todo = self.add_todo('first', todolist.id)
        self.assertFalse(todo.is_finished)

        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        self.client.put(
            url_for('api.update_todo_status', todo_id=todo.id),
            headers=self.get_headers(),
            data=json.dumps({'todo': {'is_finished': True,
                                      'finished_at': now}})
        )

        todo = Todo.query.get(todo.id)
        self.assertTrue(todo.is_finished)
        self.assertEqual(
            todo.finished_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            now
        )

    def test_update_todo_status_to_open(self):
        todolist = self.add_todolist('new todolist')
        todo = self.add_todo('first', todolist.id)
        todo.finished()
        self.assertTrue(todo.is_finished)

        self.client.put(
            url_for('api.update_todo_status', todo_id=todo.id),
            headers=self.get_headers(),
            data=json.dumps({'todo': {'is_finished': False}})
        )
        todo = Todo.query.get(todo.id)
        self.assertFalse(todo.is_finished)
        self.assertTrue(todo.finished_at is None)

    def test_change_todolist_title(self):
        todolist = self.add_todolist('new todolist')

        response = self.client.put(
            url_for('api.change_todolist_title', todolist_id=todolist.id),
            headers=self.get_headers(),
            data=json.dumps({'todolist': {'title': 'changed title'}})
        )
        self.assert_200(response)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['todolist']['title'], 'changed title')

    def test_change_todolist_title_too_long_title(self):
        todolist = self.add_todolist('new todolist')

        response = self.client.put(
            url_for('api.change_todolist_title', todolist_id=todolist.id),
            headers=self.get_headers(),
            data=json.dumps({'title': 129 * 't'})
        )
        self.assert_500(response)

    def test_change_todolist_title_empty_title(self):
        todolist = self.add_todolist('new todolist')

        response = self.client.put(
            url_for('api.change_todolist_title', todolist_id=todolist.id),
            headers=self.get_headers(),
            data=json.dumps({'title': ''})
        )
        self.assert_500(response)

    def test_change_todolist_title_without_title(self):
        todolist = self.add_todolist('new todolist')

        response = self.client.put(
            url_for('api.change_todolist_title', todolist_id=todolist.id),
            headers=self.get_headers()
        )
        self.assert_500(response)

    # test api delete calls
    @unittest.skip('because acquiring admin rights is currently an issue')
    def test_delete_user(self):
        user = self.add_user('adam')
        user_id = user.id

        response = self.client.delete(
            url_for('api.delete_user', user_id=user_id),
            headers=self.get_headers(),
            data=json.dumps({'user_id': user_id})
        )
        self.assert_200(response)

        response = self.client.get(url_for('api.get_user', user_id=user_id))
        self.assert_404(response)

    @unittest.skip('because acquiring admin rights is currently an issue')
    def test_delete_todolist(self):
        todolist = self.add_todolist('new todolist')
        todolist_id = todolist.id

        response = self.client.delete(
            url_for('api.delete_todolist', todolist_id=todolist_id),
            headers=self.get_headers(),
            data=json.dumps({'todolist_id': todolist_id})
        )
        self.assert_200(response)

        response = self.client.get(
            url_for('api.get_todolist', todolist_id=todolist_id)
        )
        self.assert_404(response)

    @unittest.skip('because acquiring admin rights is currently an issue')
    def test_delete_todo(self):
        # we need admin rights for this test
        todolist = self.add_todolist('new todolist')
        todo = self.add_todo('new todo', todolist.id)
        todo_id = todo.id

        response = self.client.delete(
            url_for('api.delete_todo', todo_id=todo_id),
            headers=self.get_headers(),
            data=json.dumps({'todo_id': todo_id})
        )
        self.assert_200(response)

        response = self.client.get(
            url_for('api.get_todo', todo_id=todo_id)
        )
        self.assert_404(response)
