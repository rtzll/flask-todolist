# -*- coding: utf-8 -*-

import unittest

from flask import current_app

from app import create_app, db
from app.models import  User, Todo


class TodolistTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
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

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

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
        todo_description = 'Read a book about TDD'
        new_todo = self.add_todo(todo_description, some_user)
        self.assertTrue(new_todo.description == 'Read a book about TDD')
        self.assertTrue(new_todo.creator_id == some_user.id)
