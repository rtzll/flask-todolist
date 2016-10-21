# -*- coding: utf-8 -*-

import unittest

from flask import current_app

from app import create_app, db
from app.models import User, Todo, TodoList


class TodolistTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.username_adam = 'adam'
        self.shopping_list_title = 'shopping list'
        self.read_todo_description = 'Read a book about TDD'

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @staticmethod
    def add_user(username):
        user_data = {
            'email': username + '@example.com',
            'username': username,
            'password': 'correcthorsebatterystaple'
        }
        user = User.from_dict(user_data)
        return User.query.filter_by(username=user.username).first()

    @staticmethod
    def add_todo(description, user, todolist_id=None):
        todo_data = {
            'description': description,
            'todolist_id': todolist_id or TodoList().save().id,
            'creator': user.username
        }
        read_todo = Todo.from_dict(todo_data)
        return Todo.query.filter_by(id=read_todo.id).first()

    def test_app_exists(self):
        self.assertTrue(current_app is not None)

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
        self.assertNotEqual(u.password_hash, u2.password_hash)

    def test_adding_new_user(self):
        new_user = self.add_user(self.username_adam)
        self.assertEqual(new_user.username, self.username_adam)
        self.assertEqual(new_user.email, self.username_adam + '@example.com')

    def test_adding_new_todo_without_user(self):
        todo = Todo(description=self.read_todo_description,
                    todolist_id=TodoList().save().id).save()
        todo_from_db = Todo.query.filter_by(id=todo.id).first()

        self.assertEqual(todo_from_db.description, self.read_todo_description)
        self.assertIsNone(todo_from_db.creator)

    def test_adding_new_todo_with_user(self):
        some_user = self.add_user(self.username_adam)
        new_todo = self.add_todo(self.read_todo_description, some_user)
        self.assertEqual(new_todo.description, self.read_todo_description)
        self.assertEqual(new_todo.creator, some_user.username)

    def test_closing_todo(self):
        some_user = self.add_user(self.username_adam)
        new_todo = self.add_todo(self.read_todo_description, some_user)
        self.assertFalse(new_todo.is_finished)
        new_todo.finished()
        self.assertTrue(new_todo.is_finished)
        self.assertEqual(new_todo.description, self.read_todo_description)
        self.assertEqual(new_todo.creator, some_user.username)

    def test_reopen_closed_todo(self):
        some_user = self.add_user(self.username_adam)
        new_todo = self.add_todo(self.read_todo_description, some_user)
        self.assertFalse(new_todo.is_finished)
        new_todo.finished()
        self.assertTrue(new_todo.is_finished)
        new_todo.reopen()
        self.assertFalse(new_todo.is_finished)
        self.assertEqual(new_todo.description, self.read_todo_description)
        self.assertEqual(new_todo.creator, some_user.username)

    def test_adding_two_todos_with_the_same_description(self):
        some_user = self.add_user(self.username_adam)
        first_todo = self.add_todo(self.read_todo_description, some_user)
        second_todo = self.add_todo(self.read_todo_description, some_user)

        self.assertEqual(first_todo.description, second_todo.description)
        self.assertEqual(first_todo.creator, second_todo.creator)
        self.assertNotEqual(first_todo.id, second_todo.id)

    def test_adding_new_todolist_without_user(self):
        todolist = TodoList(self.shopping_list_title).save()
        todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

        self.assertEqual(todolist_from_db.title, self.shopping_list_title)
        self.assertIsNone(todolist_from_db.creator)

    def test_adding_new_todolist_with_user(self):
        user = self.add_user(self.username_adam)
        todolist = TodoList(title=self.shopping_list_title,
                            creator=user.username).save()
        todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

        self.assertEqual(todolist_from_db.title, self.shopping_list_title)
        self.assertEqual(todolist_from_db.creator, user.username)

    def test_adding_two_todolists_with_the_same_title(self):
        user = self.add_user(self.username_adam)
        ftodolist = TodoList(title=self.shopping_list_title,
                             creator=user.username).save()
        first_todolist = TodoList.query.filter_by(id=ftodolist.id).first()
        stodolist = TodoList(title=self.shopping_list_title,
                             creator=user.username).save()
        second_todolist = TodoList.query.filter_by(id=stodolist.id).first()

        self.assertEqual(first_todolist.title,
                         second_todolist.title)
        self.assertEqual(first_todolist.creator, second_todolist.creator)
        self.assertNotEqual(first_todolist.id, second_todolist.id)

    def test_adding_todo_to_todolist(self):
        user = self.add_user(self.username_adam)
        todolist = TodoList(title=self.shopping_list_title,
                            creator=user.username).save()
        todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

        todo_description = 'A book about TDD'
        todo = self.add_todo(todo_description, user, todolist_from_db.id)

        self.assertEqual(todolist_from_db.todo_count, 1)
        self.assertEqual(todolist.title, self.shopping_list_title)
        self.assertEqual(todolist.creator, user.username)
        self.assertEqual(todo.todolist_id, todolist_from_db.id)
        self.assertEqual(todolist.todos.first(), todo)

    def test_counting_todos_of_todolist(self):
        user = self.add_user(self.username_adam)
        todolist = TodoList(title=self.shopping_list_title,
                            creator=user.username).save()
        todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

        todo_description = 'A book about TDD'
        todo = self.add_todo(todo_description, user, todolist_from_db.id)

        self.assertEqual(todolist.title, self.shopping_list_title)
        self.assertEqual(todolist.creator, user.username)
        self.assertEqual(todo.todolist_id, todolist_from_db.id)
        self.assertEqual(todolist.todos.first(), todo)

        self.assertEqual(todolist_from_db.finished_count, 0)
        self.assertEqual(todolist_from_db.open_count, 1)

        todo.finished()

        self.assertEqual(todolist_from_db.finished_count, 1)
        self.assertEqual(todolist_from_db.open_count, 0)

    # test delete functions
    def test_delete_user(self):
        user = self.add_user(self.username_adam)
        user_id = user.id
        user.delete()
        self.assertIsNone(User.query.get(user_id))

    def test_delete_todolist(self):
        todolist = TodoList(self.shopping_list_title).save()
        todolist_id = todolist.id
        todolist.delete()
        self.assertIsNone(TodoList.query.get(todolist_id))

    def test_delete_todo(self):
        todolist = TodoList(self.shopping_list_title).save()
        todo = Todo('A book about TDD', todolist.id).save()
        self.assertEqual(todolist.todo_count, 1)
        todo_id = todo.id
        todo.delete()
        self.assertIsNone(Todo.query.get(todo_id))
        self.assertEqual(todolist.todo_count, 0)
