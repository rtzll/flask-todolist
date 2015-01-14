# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from todolist import create_app, db, User, Todo


class TodolistTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

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

    def add_todo(self, description, user):
        todo_data = {
            'description': description,
            'creator_id': user.id
        }
        read_todo = Todo(**todo_data)
        db.session.add(read_todo)
        db.session.commit()
        return Todo.query.filter_by(id=read_todo.id).first()

    def test_password_setter(self):
        u = User(password='correcthorsebatterystaple')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='correcthorsebatterystaple')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='correcthorsebatterystaple')
        self.assertTrue(u.verify_password('correcthorsebatterystaple'))
        self.assertFalse(u.verify_password('incorrecthorsebatterystaple'))

    def test_password_salts_are_random(self):
        u = User(password='correcthorsebatterystaple')
        u2 = User(password='correcthorsebatterystaple')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_adding_new_user(self):
        username = 'adam'
        new_user = self.add_user(username)
        self.assertTrue(new_user.username == username)
        self.assertTrue(new_user.email == username + '@example.com')

    def test_adding_new_todo(self):
        some_user = self.add_user('adam')
        assert some_user is not None
        todo_description = 'Read a book about TDD'
        new_todo = self.add_todo(todo_description, some_user)
        self.assertTrue(new_todo.description == 'Read a book about TDD')
        self.assertTrue(new_todo.creator_id == some_user.id)


class TodolistClientTestCase(unittest.TestCase):
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
            'password': 'correcthorsebatterystaple',
            'password_confirmation': 'correcthorsebatterystaple'
        })
        self.assertTrue(response.status_code == 302)
        self.assertTrue(
            b'You successfully registered. Welcome!' in response.data
        )

    def test_login(self):
        # login with the new account
        response = self.client.post(url_for('login'), data={
            'email': 'john@example.com',
            'password': 'correcthorsebatterystaple'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)

    def test_logout(self):
        # login with the new account
        response = self.client.post(url_for('login'), data={
            'email': 'john@example.com',
            'password': 'correcthorsebatterystaple'
        }, follow_redirects=True)
        # log out
        response = self.client.get(url_for('logout'), follow_redirects=True)
        self.assertTrue(b'You have been logged out' in response.data)


if __name__ == '__main__':
    unittest.main()
