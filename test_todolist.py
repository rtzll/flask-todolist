# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from todolist import create_app, db, User

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('index'))
        self.assertTrue(b'Todolists' in response.data)

    def test_register(self):
        # register a new account
        response = self.client.post(url_for('register'), data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat',
            'password_confirmation': 'cat'
        })
        self.assertTrue(response.status_code == 302)

    def test_login(self):
        # login with the new account
        response = self.client.post(url_for('login'), data={
            'email': 'john@example.com',
            'password': 'cat'
        }, follow_redirects=True)
        self.assertTrue(
            b'You have not confirmed your account yet' in response.data)

    def test_logout(self):
        # login with the new account
        response = self.client.post(url_for('login'), data={
            'email': 'john@example.com',
            'password': 'cat'
        }, follow_redirects=True)
        # log out
        response = self.client.get(url_for('logout'), follow_redirects=True)
        self.assertTrue(b'You have been logged out' in response.data)


if __name__ == '__main__':
    unittest.main()
