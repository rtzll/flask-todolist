# -*- coding: utf-8 -*-

import unittest
import json

from flask import url_for

from app import create_app, db
from app.models import  User, Todo


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
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return User.query.filter_by(username=username).first()

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

        response = self.client.get(url_for('api.get_users'))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['users'], [])

    def test_not_found(self):
        response = self.client.get('/api/not/found')
        self.assertEqual(response.status_code, 404)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['error'], 'Not found')

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
        post_response = self.client.post(url_for('api.add_todolist'),
                                    headers=self.get_headers(),
                                    data=json.dumps({'title': 'todolist'}))
        self.assertEqual(post_response.status_code, 201)

        # the expected id of the todolist is 1, as it is the first to be added
        response = self.client.get(url_for('api.get_todolist', id=1))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['todolist']['title'], 'todolist')

    def test_add_user_todolist(self):
        pass

    def test_add_todolist_todo(self):
        pass

    def test_add_todo(self):
        pass

    # test api get calls
    def test_get_users(self):
        username = 'adam'
        new_user = self.add_user(username)
        response = self.client.get(url_for('api.get_users'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['users'][0]['user']['username'],
                         username)

    def test_get_user(self):
        username = 'adam'
        new_user = self.add_user(username)
        response = self.client.get(url_for('api.get_user', username=username))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['user']['username'], username)

    def test_get_anon_todolists(self):
        pass

    def test_get_user_todolists(self):
        pass

    def test_get_anon_todolist_todos(self):
        pass

    def test_get_user_todolist_todos(self):
        pass
