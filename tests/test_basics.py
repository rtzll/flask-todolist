import unittest

from flask import current_app

from app import create_app, db
from app.models import Todo, TodoList, User


class TodolistTestCase(unittest.TestCase):
    def setUp(self):
        """
        Sets the application.

        Args:
            self: (todo): write your description
        """
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.username_adam = "adam"
        self.shopping_list_title = "shopping list"
        self.read_todo_description = "Read a book about TDD"

    def tearDown(self):
        """
        Remove all database

        Args:
            self: (todo): write your description
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @staticmethod
    def add_user(username):
        """
        Add a user.

        Args:
            username: (str): write your description
        """
        user_data = {
            "email": username + "@example.com",
            "username": username,
            "password": "correcthorsebatterystaple",
        }
        user = User.from_dict(user_data)
        return User.query.filter_by(username=user.username).first()

    @staticmethod
    def add_todo(description, user, todolist_id=None):
        """
        Add a new todoist.

        Args:
            description: (str): write your description
            user: (str): write your description
            todolist_id: (str): write your description
        """
        todo_data = {
            "description": description,
            "todolist_id": todolist_id or TodoList().save().id,
            "creator": user.username,
        }
        read_todo = Todo.from_dict(todo_data)
        return Todo.query.filter_by(id=read_todo.id).first()

    def test_app_exists(self):
        """
        Check if app exists

        Args:
            self: (todo): write your description
        """
        self.assertTrue(current_app is not None)

    def test_app_is_testing(self):
        """
        Check if the current app is app.

        Args:
            self: (todo): write your description
        """
        self.assertTrue(current_app.config["TESTING"])

    def test_password_setter(self):
        """
        Set the password password.

        Args:
            self: (todo): write your description
        """
        u = User(password="correcthorsebatterystaple")
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        """
        Get a password is enabled.

        Args:
            self: (todo): write your description
        """
        u = User(password="correcthorsebatterystaple")
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        """
        Test if a verification verification verification.

        Args:
            self: (todo): write your description
        """
        u = User(password="correcthorsebatterystaple")
        self.assertTrue(u.verify_password("correcthorsebatterystaple"))
        self.assertFalse(u.verify_password("incorrecthorsebatterystaple"))

    def test_password_salts_are_random(self):
        """
        Generate a random password.

        Args:
            self: (todo): write your description
        """
        u = User(password="correcthorsebatterystaple")
        u2 = User(password="correcthorsebatterystaple")
        self.assertNotEqual(u.password_hash, u2.password_hash)

    def test_adding_new_user(self):
        """
        Test if the user is a new.

        Args:
            self: (todo): write your description
        """
        new_user = self.add_user(self.username_adam)
        self.assertEqual(new_user.username, self.username_adam)
        self.assertEqual(new_user.email, self.username_adam + "@example.com")

    def test_adding_new_todo_without_user(self):
        """
        Test todo of the new_todo

        Args:
            self: (todo): write your description
        """
        todo = Todo(
            description=self.read_todo_description, todolist_id=TodoList().save().id
        ).save()
        todo_from_db = Todo.query.filter_by(id=todo.id).first()

        self.assertEqual(todo_from_db.description, self.read_todo_description)
        self.assertIsNone(todo_from_db.creator)

    def test_adding_new_todo_with_user(self):
        """
        Test for new consumer todo.

        Args:
            self: (todo): write your description
        """
        some_user = self.add_user(self.username_adam)
        new_todo = self.add_todo(self.read_todo_description, some_user)
        self.assertEqual(new_todo.description, self.read_todo_description)
        self.assertEqual(new_todo.creator, some_user.username)

    def test_closing_todo(self):
        """
        Test if a new todo

        Args:
            self: (todo): write your description
        """
        some_user = self.add_user(self.username_adam)
        new_todo = self.add_todo(self.read_todo_description, some_user)
        self.assertFalse(new_todo.is_finished)
        new_todo.finished()
        self.assertTrue(new_todo.is_finished)
        self.assertEqual(new_todo.description, self.read_todo_description)
        self.assertEqual(new_todo.creator, some_user.username)

    def test_reopen_closed_todo(self):
        """
        Acknowledge that ack.

        Args:
            self: (todo): write your description
        """
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
        """
        Test if two lists of the two lists of the first one.

        Args:
            self: (todo): write your description
        """
        some_user = self.add_user(self.username_adam)
        first_todo = self.add_todo(self.read_todo_description, some_user)
        second_todo = self.add_todo(self.read_todo_description, some_user)

        self.assertEqual(first_todo.description, second_todo.description)
        self.assertEqual(first_todo.creator, second_todo.creator)
        self.assertNotEqual(first_todo.id, second_todo.id)

    def test_adding_new_todolist_without_user(self):
        """
        Test if a new todoolist.

        Args:
            self: (todo): write your description
        """
        todolist = TodoList(self.shopping_list_title).save()
        todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

        self.assertEqual(todolist_from_db.title, self.shopping_list_title)
        self.assertIsNone(todolist_from_db.creator)

    def test_adding_new_todolist_with_user(self):
        """
        Test if a new title.

        Args:
            self: (todo): write your description
        """
        user = self.add_user(self.username_adam)
        todolist = TodoList(
            title=self.shopping_list_title, creator=user.username
        ).save()
        todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

        self.assertEqual(todolist_from_db.title, self.shopping_list_title)
        self.assertEqual(todolist_from_db.creator, user.username)

    def test_adding_two_todolists_with_the_same_title(self):
        """
        Test if two lists are the same.

        Args:
            self: (todo): write your description
        """
        user = self.add_user(self.username_adam)
        ftodolist = TodoList(
            title=self.shopping_list_title, creator=user.username
        ).save()
        first_todolist = TodoList.query.filter_by(id=ftodolist.id).first()
        stodolist = TodoList(
            title=self.shopping_list_title, creator=user.username
        ).save()
        second_todolist = TodoList.query.filter_by(id=stodolist.id).first()

        self.assertEqual(first_todolist.title, second_todolist.title)
        self.assertEqual(first_todolist.creator, second_todolist.creator)
        self.assertNotEqual(first_todolist.id, second_todolist.id)

    def test_adding_todo_to_todolist(self):
        """
        Updates the information about a list of lists.

        Args:
            self: (todo): write your description
        """
        user = self.add_user(self.username_adam)
        todolist = TodoList(
            title=self.shopping_list_title, creator=user.username
        ).save()
        todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

        todo_description = "A book about TDD"
        todo = self.add_todo(todo_description, user, todolist_from_db.id)

        self.assertEqual(todolist_from_db.todo_count, 1)
        self.assertEqual(todolist.title, self.shopping_list_title)
        self.assertEqual(todolist.creator, user.username)
        self.assertEqual(todo.todolist_id, todolist_from_db.id)
        self.assertEqual(todolist.todos.first(), todo)

    def test_counting_todos_of_todolist(self):
        """
        Updates the number of tasks in the database.

        Args:
            self: (todo): write your description
        """
        user = self.add_user(self.username_adam)
        todolist = TodoList(
            title=self.shopping_list_title, creator=user.username
        ).save()
        todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

        todo_description = "A book about TDD"
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
        """
        Delete the given user.

        Args:
            self: (todo): write your description
        """
        user = self.add_user(self.username_adam)
        user_id = user.id
        user.delete()
        self.assertIsNone(User.query.get(user_id))

    def test_delete_todolist(self):
        """
        Deletes a list of tables.

        Args:
            self: (todo): write your description
        """
        todolist = TodoList(self.shopping_list_title).save()
        todolist_id = todolist.id
        todolist.delete()
        self.assertIsNone(TodoList.query.get(todolist_id))

    def test_delete_todo(self):
        """
        Updates the list of a todo

        Args:
            self: (todo): write your description
        """
        todolist = TodoList(self.shopping_list_title).save()
        todo = Todo("A book about TDD", todolist.id).save()
        self.assertEqual(todolist.todo_count, 1)
        todo_id = todo.id
        todo.delete()
        self.assertIsNone(Todo.query.get(todo_id))
        self.assertEqual(todolist.todo_count, 0)
