import json
import unittest

from flask import url_for
from flask_login import login_user
from flask_testing import TestCase

from app import create_app, db
from app.models import Todo, TodoList, User


class TodolistAPITestCase(TestCase):
    def create_app(self):
        return create_app("testing")

    def setUp(self):
        db.create_all()
        self.username_alice = "alice"

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def assert404Response(self, response):
        self.assert_404(response)
        json_response = json.loads(response.data.decode("utf-8"))
        self.assertEqual(json_response["error"], "Not found")

    def assert400Response(self, response):
        self.assert_400(response)
        json_response = json.loads(response.data.decode("utf-8"))
        self.assertEqual(json_response["error"], "Bad Request")

    @staticmethod
    def setup_new_user(username):
        user_data = {
            "username": username,
            "email": username + "@example.com",
            "password": "correcthorsebatterystaple",
        }
        return user_data

    @staticmethod
    def get_headers():
        return {"Accept": "application/json", "Content-Type": "application/json"}

    def add_user(self, username):
        user_data = self.setup_new_user(username)
        User.from_dict(user_data)
        return User.query.filter_by(username=username).first()

    @staticmethod
    def add_todolist(title, username=None):
        todolist = TodoList(title=title, creator=username).save()
        return TodoList.query.filter_by(id=todolist.id).first()

    def add_todo(self, description, todolist_id, username=None):
        todolist = TodoList.query.filter_by(id=todolist_id).first()
        todo = Todo(
            description=description, todolist_id=todolist.id, creator=username
        ).save()
        return Todo.query.filter_by(id=todo.id).first()

    def add_user_through_json_post(self, username):
        user_data = self.setup_new_user(username)
        return self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )

    def create_admin(self):
        new_user = self.setup_new_user("admin")
        new_user["is_admin"] = True
        return User.from_dict(new_user)

    def test_main_route(self):
        response = self.client.get(url_for("api.get_routes"))
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        self.assertTrue("users" in json_response)
        self.assertTrue("todolists" in json_response)

    def test_not_found(self):
        response = self.client.get("/api/not/found")
        self.assert404Response(response)

    # test api post calls
    def test_add_user(self):
        post_response = self.add_user_through_json_post(self.username_alice)
        self.assertEqual(post_response.headers["Content-Type"], "application/json")
        self.assert_status(post_response, 201)

        response = self.client.get(url_for("api.get_users"))
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        users = json_response["users"]
        self.assertEqual(users[0]["username"], self.username_alice)

    def test_add_user_only_using_the_username(self):
        user_data = {"username": self.username_alice}
        response = self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )
        self.assert400Response(response)

    def test_add_user_only_using_the_username_and_email(self):
        user_data = {
            "username": self.username_alice,
            "email": self.username_alice + "@example.com",
        }
        response = self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )
        self.assert400Response(response)

    def test_add_user_with_to_long_username(self):
        user_data = {
            "username": 65 * "a",
            "email": self.username_alice + "@example.com",
            "password": "correcthorsebatterystaple",
        }
        response = self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )
        self.assert400Response(response)

    def test_add_user_with_invalid_username(self):
        user_data = {
            "username": "not a valid username",
            "email": self.username_alice + "@example.com",
            "password": "correcthorsebatterystaple",
        }
        response = self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )
        self.assert400Response(response)

    def test_add_user_without_username(self):
        user_data = {
            "username": "",
            "email": self.username_alice + "@example.com",
            "password": "correcthorsebatterystaple",
        }
        response = self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )
        self.assert400Response(response)

    def test_add_user_with_invalid_email(self):
        user_data = {
            "username": self.username_alice,
            "email": self.username_alice + "example.com",
            "password": "correcthorsebatterystaple",
        }
        response = self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )
        self.assert400Response(response)

    def test_add_user_withoout_email(self):
        user_data = {
            "username": self.username_alice,
            "email": "",
            "password": "correcthorsebatterystaple",
        }
        response = self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )
        self.assert400Response(response)

    def test_add_user_with_too_long_email(self):
        user_data = {
            "username": self.username_alice,
            "email": 53 * "a" + "@example.com",
            "password": "correcthorsebatterystaple",
        }
        response = self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )
        self.assert400Response(response)

    def test_add_user_without_password(self):
        user_data = {
            "username": self.username_alice,
            "email": self.username_alice + "@example.com",
            "password": "",
        }
        response = self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )
        self.assert400Response(response)

    def test_add_user_with_extra_fields(self):
        user_data = {
            "username": self.username_alice,
            "email": self.username_alice + "@example.com",
            "password": "correcthorsebatterystaple",
            "extra-field": "will be ignored",
        }
        post_response = self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )
        self.assertEqual(post_response.headers["Content-Type"], "application/json")
        self.assert_status(post_response, 201)

        response = self.client.get(url_for("api.get_users"))
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        self.assertEqual(json_response["users"][0]["username"], self.username_alice)

    def test_add_user_only_using_the_username_and_password(self):
        user_data = {
            "username": self.username_alice,
            "password": "correcthorsebatterystaple",
        }
        response = self.client.post(
            url_for("api.add_user"),
            headers=self.get_headers(),
            data=json.dumps(user_data),
        )
        self.assert400Response(response)

    def test_add_todolist(self):
        post_response = self.client.post(
            url_for("api.add_todolist"),
            headers=self.get_headers(),
            data=json.dumps({"title": "todolist"}),
        )
        self.assert_status(post_response, 201)

        # the expected id of the todolist is 1, as it is the first to be added
        response = self.client.get(url_for("api.get_todolist", todolist_id=1))
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        self.assertEqual(json_response["title"], "todolist")

    def test_add_todolist_without_title(self):
        response = self.client.post(
            url_for("api.add_todolist"), headers=self.get_headers()
        )
        # opposed to the form, the title is a required argument
        self.assert400Response(response)

    def test_add_todolist_with_too_long_title(self):
        response = self.client.post(
            url_for("api.add_todolist"),
            headers=self.get_headers(),
            data=json.dumps({"title": 129 * "t"}),
        )
        self.assert400Response(response)

    def test_add_user_todolist(self):
        self.add_user(self.username_alice)
        post_response = self.client.post(
            url_for("api.add_user_todolist", username=self.username_alice),
            headers=self.get_headers(),
            data=json.dumps({"title": "todolist"}),
        )
        self.assert_status(post_response, 201)

        response = self.client.get(
            url_for("api.get_user_todolists", username=self.username_alice)
        )
        self.assert_200(response)
        json_response = json.loads(response.data.decode("utf-8"))

        # check title, creator are set correctly and a total of one todolist
        todolists = json_response["todolists"]
        self.assertEqual(todolists[0]["title"], "todolist")
        self.assertEqual(todolists[0]["creator"], self.username_alice)
        self.assertEqual(len(todolists), 1)

    def test_add_user_todolist_when_user_does_not_exist(self):
        post_response = self.client.post(
            url_for("api.add_user_todolist", username=self.username_alice),
            headers=self.get_headers(),
            data=json.dumps({"title": "todolist"}),
        )
        self.assert404Response(post_response)

    def test_add_user_todolist_todo(self):
        todolist_title = "new todolist"
        self.add_user(self.username_alice)
        new_todolist = self.add_todolist(todolist_title, self.username_alice)

        post_response = self.client.post(
            url_for(
                "api.add_user_todolist_todo",
                username=self.username_alice,
                todolist_id=new_todolist.id,
            ),
            headers=self.get_headers(),
            data=json.dumps(
                {
                    "description": "new todo",
                    "creator": self.username_alice,
                    "todolist_id": new_todolist.id,
                }
            ),
        )
        self.assert_status(post_response, 201)

        response = self.client.get(
            url_for(
                "api.get_user_todolist_todos",
                username=self.username_alice,
                todolist_id=new_todolist.id,
            )
        )
        self.assert_200(response)
        json_response = json.loads(response.data.decode("utf-8"))

        # check title, creator are set correctly and a total of one todo
        todos = json_response["todos"]
        self.assertEqual(todos[0]["description"], "new todo")
        self.assertEqual(todos[0]["creator"], self.username_alice)
        self.assertEqual(len(todos), 1)

    def test_add_user_todolist_todo_when_todolist_does_not_exist(self):
        self.add_user(self.username_alice)
        post_response = self.client.post(
            url_for(
                "api.add_user_todolist_todo",
                username=self.username_alice,
                todolist_id=1,
            ),
            headers=self.get_headers(),
            data=json.dumps(
                {
                    "description": "new todo",
                    "creator": self.username_alice,
                    "todolist_id": 1,
                }
            ),
        )
        self.assert404Response(post_response)

    def test_add_user_todolist_todo_without_todo_data(self):
        todolist_title = "new todolist"
        self.add_user(self.username_alice)
        new_todolist = self.add_todolist(todolist_title, self.username_alice)

        post_response = self.client.post(
            url_for(
                "api.add_user_todolist_todo",
                username=self.username_alice,
                todolist_id=new_todolist.id,
            ),
            headers=self.get_headers(),
        )
        self.assert400Response(post_response)

    def test_add_todolist_todo(self):
        new_todolist = TodoList().save()  # todolist with default title

        post_response = self.client.post(
            url_for("api.add_todolist_todo", todolist_id=new_todolist.id),
            headers=self.get_headers(),
            data=json.dumps(
                {
                    "description": "new todo",
                    "creator": "null",
                    "todolist_id": new_todolist.id,
                }
            ),
        )
        self.assert_status(post_response, 201)
        response = self.client.get(
            url_for("api.get_todolist_todos", todolist_id=new_todolist.id)
        )
        self.assert_200(response)
        json_response = json.loads(response.data.decode("utf-8"))

        # check title, creator are set correctly and a total of one todo
        todos = json_response["todos"]
        self.assertEqual(todos[0]["description"], "new todo")
        self.assertEqual(todos[0]["creator"], None)
        self.assertEqual(len(todos), 1)

    def test_add_todolist_todo_when_todolist_does_not_exist(self):
        post_response = self.client.post(
            url_for("api.add_todolist_todo", todolist_id=1),
            headers=self.get_headers(),
            data=json.dumps(
                {"description": "new todo", "creator": "null", "todolist_id": 1}
            ),
        )
        self.assert404Response(post_response)

    def test_add_todolist_todo_without_todo_data(self):
        new_todolist = TodoList().save()
        post_response = self.client.post(
            url_for("api.add_todolist_todo", todolist_id=new_todolist.id),
            headers=self.get_headers(),
        )
        self.assert400Response(post_response)

    # test api get calls
    def test_get_users(self):
        self.add_user(self.username_alice)
        response = self.client.get(url_for("api.get_users"))
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        self.assertEqual(json_response["users"][0]["username"], self.username_alice)

    def test_get_users_when_no_users_exist(self):
        response = self.client.get(url_for("api.get_users"))
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        self.assertEqual(json_response["users"], [])

    def test_get_user(self):
        self.add_user(self.username_alice)
        response = self.client.get(
            url_for("api.get_user", username=self.username_alice)
        )
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        self.assertEqual(json_response["username"], self.username_alice)

    def test_get_user_when_user_does_not_exist(self):
        response = self.client.get(
            url_for("api.get_user", username=self.username_alice)
        )
        self.assert404Response(response)

    def test_get_todolists(self):
        todolist_title = "new todolist "
        self.add_user(self.username_alice)
        self.add_todolist(todolist_title + "1", self.username_alice)
        self.add_todolist(todolist_title + "2", self.username_alice)

        response = self.client.get(url_for("api.get_todolists"))
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        todolists = json_response["todolists"]
        self.assertEqual(todolists[0]["title"], "new todolist 1")
        self.assertEqual(todolists[0]["creator"], self.username_alice)
        self.assertEqual(todolists[1]["title"], "new todolist 2")
        self.assertEqual(todolists[1]["creator"], self.username_alice)
        self.assertEqual(len(todolists), 2)

    def test_get_todolists_when_no_todolists_exist(self):
        response = self.client.get(url_for("api.get_todolists"))
        self.assert_200(response)

        todolists = json.loads(response.data.decode("utf-8"))["todolists"]
        self.assertEqual(todolists, [])

    def test_get_user_todolists(self):
        todolist_title = "new todolist "
        self.add_user(self.username_alice)
        self.add_todolist(todolist_title + "1", self.username_alice)
        self.add_todolist(todolist_title + "2", self.username_alice)

        response = self.client.get(
            url_for("api.get_user_todolists", username=self.username_alice)
        )
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        todolists = json_response["todolists"]

        self.assertEqual(todolists[0]["title"], "new todolist 1")
        self.assertEqual(todolists[0]["creator"], self.username_alice)
        self.assertEqual(todolists[1]["title"], "new todolist 2")
        self.assertEqual(todolists[1]["creator"], self.username_alice)
        self.assertEqual(len(todolists), 2)

    def test_get_user_todolists_when_user_does_not_exist(self):
        response = self.client.get(
            url_for("api.get_user_todolists", username=self.username_alice)
        )
        self.assert404Response(response)

    def test_get_user_todolists_when_user_has_no_todolists(self):
        self.add_user(self.username_alice)
        response = self.client.get(
            url_for("api.get_user_todolists", username=self.username_alice)
        )
        self.assert_200(response)

        todolists = json.loads(response.data.decode("utf-8"))["todolists"]
        self.assertEqual(todolists, [])

    def test_get_todolist_todos(self):
        todolist_title = "new todolist"
        new_todolist = self.add_todolist(todolist_title)

        self.add_todo("first", new_todolist.id)
        self.add_todo("second", new_todolist.id)

        response = self.client.get(
            url_for("api.get_todolist_todos", todolist_id=new_todolist.id)
        )
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        todos = json_response["todos"]
        self.assertEqual(todos[0]["description"], "first")
        self.assertEqual(todos[0]["creator"], None)
        self.assertEqual(todos[1]["description"], "second")
        self.assertEqual(todos[1]["creator"], None)
        self.assertEqual(len(todos), 2)

    def test_get_todolist_todos_when_todolist_does_not_exist(self):
        response = self.client.get(url_for("api.get_todolist_todos", todolist_id=1))
        self.assert404Response(response)

    def test_get_todolist_todos_when_todolist_has_no_todos(self):
        todolist_title = "new todolist"
        new_todolist = self.add_todolist(todolist_title)
        response = self.client.get(
            url_for("api.get_todolist_todos", todolist_id=new_todolist.id)
        )
        self.assert_200(response)

        todos = json.loads(response.data.decode("utf-8"))["todos"]
        self.assertEqual(todos, [])

    def test_get_user_todolist_todos(self):
        todolist_title = "new todolist"
        self.add_user(self.username_alice)
        new_todolist = self.add_todolist(todolist_title, self.username_alice)

        self.add_todo("first", new_todolist.id, self.username_alice)
        self.add_todo("second", new_todolist.id, self.username_alice)

        response = self.client.get(
            url_for(
                "api.get_user_todolist_todos",
                username=self.username_alice,
                todolist_id=new_todolist.id,
            )
        )
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        todos = json_response["todos"]
        self.assertEqual(todos[0]["description"], "first")
        self.assertEqual(todos[0]["creator"], self.username_alice)
        self.assertEqual(todos[1]["description"], "second")
        self.assertEqual(todos[1]["creator"], self.username_alice)
        self.assertEqual(len(todos), 2)

    def test_get_user_todolist_todos_when_user_does_not_exist(self):
        response = self.client.get(
            url_for(
                "api.get_user_todolist_todos",
                username=self.username_alice,
                todolist_id=1,
            )
        )
        self.assert404Response(response)

    def test_get_user_todolist_todos_when_todolist_does_not_exist(self):
        self.add_user(self.username_alice)

        response = self.client.get(
            url_for(
                "api.get_user_todolist_todos",
                username=self.username_alice,
                todolist_id=1,
            )
        )
        self.assert404Response(response)

    def test_get_user_todolist_todos_when_todolist_has_no_todos(self):
        todolist_title = "new todolist"
        self.add_user(self.username_alice)
        new_todolist = self.add_todolist(todolist_title, self.username_alice)

        response = self.client.get(
            url_for(
                "api.get_user_todolist_todos",
                username=self.username_alice,
                todolist_id=new_todolist.id,
            )
        )
        self.assert_200(response)

        todos = json.loads(response.data.decode("utf-8"))["todos"]
        self.assertEqual(todos, [])

    def test_get_different_user_todolist_todos(self):
        first_username = self.username_alice
        second_username = "bob"
        todolist_title = "new todolist"
        first_user = self.add_user(first_username)
        self.add_user(second_username)
        new_todolist = self.add_todolist(todolist_title, second_username)

        self.add_todo("first", new_todolist.id, second_username)
        self.add_todo("second", new_todolist.id, second_username)

        response = self.client.get(
            url_for(
                "api.get_user_todolist_todos",
                username=first_user,
                todolist_id=new_todolist.id,
            )
        )
        self.assert404Response(response)

    def test_get_user_todolist(self):
        todolist_title = "new todolist"
        self.add_user(self.username_alice)
        new_todolist = self.add_todolist(todolist_title, self.username_alice)

        response = self.client.get(
            url_for(
                "api.get_user_todolist",
                username=self.username_alice,
                todolist_id=new_todolist.id,
            )
        )
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))

        self.assertEqual(json_response["title"], todolist_title)
        self.assertEqual(json_response["creator"], self.username_alice)

    def test_get_user_todolist_when_user_does_not_exist(self):
        response = self.client.get(
            url_for(
                "api.get_user_todolist", username=self.username_alice, todolist_id=1
            )
        )
        self.assert404Response(response)

    def test_get_user_todolist_when_todolist_does_not_exist(self):
        self.add_user(self.username_alice)
        response = self.client.get(
            url_for(
                "api.get_user_todolist", username=self.username_alice, todolist_id=1
            )
        )
        self.assert404Response(response)

    # test api put call
    def test_update_todo_status_to_finished(self):
        todolist = self.add_todolist("new todolist")
        todo = self.add_todo("first", todolist.id)
        self.assertFalse(todo.is_finished)

        self.client.put(
            url_for("api.update_todo_status", todo_id=todo.id),
            headers=self.get_headers(),
            data=json.dumps({"is_finished": True}),
        )

        todo = Todo.query.get(todo.id)
        self.assertTrue(todo.is_finished)

    def test_update_todo_status_to_open(self):
        todolist = self.add_todolist("new todolist")
        todo = self.add_todo("first", todolist.id)
        todo.finished()
        self.assertTrue(todo.is_finished)

        self.client.put(
            url_for("api.update_todo_status", todo_id=todo.id),
            headers=self.get_headers(),
            data=json.dumps({"is_finished": False}),
        )
        todo = Todo.query.get(todo.id)
        self.assertFalse(todo.is_finished)
        self.assertTrue(todo.finished_at is None)

    def test_change_todolist_title(self):
        todolist = self.add_todolist("new todolist")

        response = self.client.put(
            url_for("api.change_todolist_title", todolist_id=todolist.id),
            headers=self.get_headers(),
            data=json.dumps({"title": "changed title"}),
        )
        self.assert_200(response)

        json_response = json.loads(response.data.decode("utf-8"))
        self.assertEqual(json_response["title"], "changed title")

    def test_change_todolist_title_too_long_title(self):
        todolist = self.add_todolist("new todolist")

        response = self.client.put(
            url_for("api.change_todolist_title", todolist_id=todolist.id),
            headers=self.get_headers(),
            data=json.dumps({"title": 129 * "t"}),
        )
        self.assert_400(response)

    def test_change_todolist_title_empty_title(self):
        todolist = self.add_todolist("new todolist")

        response = self.client.put(
            url_for("api.change_todolist_title", todolist_id=todolist.id),
            headers=self.get_headers(),
            data=json.dumps({"title": ""}),
        )
        self.assert_400(response)

    def test_change_todolist_title_without_title(self):
        todolist = self.add_todolist("new todolist")

        response = self.client.put(
            url_for("api.change_todolist_title", todolist_id=todolist.id),
            headers=self.get_headers(),
        )
        self.assert_400(response)

    # test api delete calls
    @unittest.skip("because acquiring admin rights is currently an issue")
    def test_delete_user(self):
        admin = self.create_admin()
        login_user(admin)

        user = self.add_user(self.username_alice)
        user_id = user.id

        response = self.client.delete(
            url_for("api.delete_user", user_id=user_id),
            headers=self.get_headers(),
            data=json.dumps({"user_id": user_id}),
        )
        self.assert_200(response)

        response = self.client.get(url_for("api.get_user", user_id=user_id))
        self.assert_404(response)

    @unittest.skip("because acquiring admin rights is currently an issue")
    def test_delete_todolist(self):
        admin = self.create_admin()
        login_user(admin)

        todolist = self.add_todolist("new todolist")
        todolist_id = todolist.id

        response = self.client.delete(
            url_for("api.delete_todolist", todolist_id=todolist_id),
            headers=self.get_headers(),
            data=json.dumps({"todolist_id": todolist_id}),
        )
        self.assert_200(response)

        response = self.client.get(url_for("api.get_todolist", todolist_id=todolist_id))
        self.assert_404(response)

    @unittest.skip("because acquiring admin rights is currently an issue")
    def test_delete_todo(self):
        admin = self.create_admin()
        login_user(admin)

        todolist = self.add_todolist("new todolist")
        todo = self.add_todo("new todo", todolist.id)
        todo_id = todo.id

        response = self.client.delete(
            url_for("api.delete_todo", todo_id=todo_id),
            headers=self.get_headers(),
            data=json.dumps({"todo_id": todo_id}),
        )
        self.assert_200(response)

        response = self.client.get(url_for("api.get_todo", todo_id=todo_id))
        self.assert_404(response)
