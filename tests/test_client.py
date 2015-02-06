# -*- coding: utf-8 -*-

import unittest

from flask import url_for

from app import create_app, db
from app.models import  User, Todo


class TodolistClientTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register_user(self, name):
        response = self.client.post(url_for('auth.register'), data={
            'username': name,
            'email': name +'@example.com',
            'password': 'correcthorsebatterystaple',
            'password_confirmation': 'correcthorsebatterystaple'
        })
        return response

    def login_user(self, name):
        response = self.client.post(url_for('auth.login'), data={
            'email_or_username': name + '@example.com',
            'password': 'correcthorsebatterystaple'
        })
        return response

    def register_and_login(self, name):
        response = self.register_user(name)
        self.assertEqual(response.status_code, 302)
        response = self.login_user(name)
        self.assertEqual(response.status_code, 302)

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue(b'Todolists' in response.data)

    def test_register_page(self):
        response = self.client.get(url_for('auth.register'))
        self.assertTrue(b'Already registerd?' in response.data)

    def test_login_page(self):
        response = self.client.get(url_for('auth.login'))
        self.assertTrue(b'New user?' in response.data)

    def test_overview_redirect_if_user_not_logged_in(self):
        response = self.client.get(url_for('main.todolist_overview'))
        # expect redirect to index, because user is not logged in
        self.assertEqual(response.status_code, 302)

    def test_overview_redirect_if_user_logged_in(self):
        self.register_and_login('adam')
        response = self.client.get(url_for('main.todolist_overview'))
        # expect not redirect as user is logged in
        self.assertEqual(response.status_code, 200)

    def test_register_and_login_and_logout(self):
        # register a new account
        response = self.register_user('adam')
        # expect redirect to login
        self.assertEqual(response.status_code, 302)

        # login with the new account
        response = self.login_user('adam')
        # expect redirect to index
        self.assertEqual(response.status_code, 302)

        # logout
        response = self.client.get(url_for('auth.logout'),
                                   follow_redirects=True)
        # follow redirect to index
        self.assertEqual(response.status_code, 200)
