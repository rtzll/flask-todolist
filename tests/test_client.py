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

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue(b'Todolists' in response.data)

    def test_register(self):
        # register a new account
        response = self.client.post(url_for('auth.register'), data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'correcthorsebatterystaple',
            'password_confirmation': 'correcthorsebatterystaple'
        })
        self.assertTrue(response.status_code == 200)

    def test_login(self):
        # login with the new account
        response = self.client.post(url_for('auth.login'), data={
            'email': 'john@example.com',
            'password': 'correcthorsebatterystaple'
        })
        self.assertTrue(response.status_code == 200)

    def test_logout(self):
        # login with the new account
        response = self.client.post(url_for('auth.login'), data={
            'email': 'john@example.com',
            'password': 'correcthorsebatterystaple'
        }, follow_redirects=True)
        # log out
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
