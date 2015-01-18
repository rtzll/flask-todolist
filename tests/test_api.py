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

    def add_user(self, username):
        user_data = {
            'email': username + '@example.com',
            'username': username,
            'password': 'correcthorsebatterystaple'
        }
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return User.query.filter_by(username=username).first()

    def test_json_response_is_not_empty_after_adding_a_user(self):
        new_user = self.add_user('new_user')
        response = self.client.get(url_for('api.get_users'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['users'] != [])

    def test_new_user_shows_in_json_response(self):
        username = 'adam'
        new_user = self.add_user(username)
        response = self.client.get(url_for('api.get_users'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['users'][0]['username'] == username)
