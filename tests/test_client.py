from flask import url_for
from flask_testing import TestCase

from app import create_app, db
from app.models import User


class TodolistClientTestCase(TestCase):
    def create_app(self):
        """
        Create a flask application.

        Args:
            self: (todo): write your description
        """
        return create_app("testing")

    def setUp(self):
        """
        Sets all the database

        Args:
            self: (todo): write your description
        """
        db.create_all()
        self.username_alice = "alice"

    def tearDown(self):
        """
        Removes all tokens.

        Args:
            self: (todo): write your description
        """
        db.session.remove()
        db.drop_all()

    def register_user(self, name):
        """
        Register a new user.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        response = self.client.post(
            url_for("auth.register"),
            data={
                "username": name,
                "email": name + "@example.com",
                "password": "correcthorsebatterystaple",
                "password_confirmation": "correcthorsebatterystaple",
            },
        )
        return response

    def login_user(self, name):
        """
        Login to a user.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        response = self.client.post(
            url_for("auth.login"),
            data={
                "email_or_username": name + "@example.com",
                "password": "correcthorsebatterystaple",
            },
        )
        return response

    def register_and_login(self, name):
        """
        Register a user and password and return the user.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        response = self.register_user(name)
        self.assert_redirects(response, "/auth/login")
        response = self.login_user(name)
        self.assert_redirects(response, "/")

    def test_home_page(self):
        """
        Download the home page.

        Args:
            self: (todo): write your description
        """
        response = self.client.get(url_for("main.index"))
        self.assert_200(response)
        self.assert_template_used("index.html")

    def test_register_page(self):
        """
        Register a new page.

        Args:
            self: (todo): write your description
        """
        response = self.client.get(url_for("auth.register"))
        self.assert_200(response)
        self.assert_template_used("register.html")

    def test_login_page(self):
        """
        Get the login page.

        Args:
            self: (todo): write your description
        """
        response = self.client.get(url_for("auth.login"))
        self.assert_200(response)
        self.assert_template_used("login.html")

    def test_overview_page(self):
        """
        Test for login page.

        Args:
            self: (todo): write your description
        """
        self.register_and_login(self.username_alice)
        response = self.client.get(url_for("main.todolist_overview"))
        # expect not redirect as user is logged in
        self.assert_200(response)
        self.assert_template_used("overview.html")

    def test_last_seen_update_after_login(self):
        """
        Test if the last update of the last update.

        Args:
            self: (todo): write your description
        """
        self.register_user(self.username_alice)
        user = User.query.filter_by(username=self.username_alice).first()
        before = user.last_seen
        self.login_user(self.username_alice)
        after = user.last_seen
        self.assertNotEqual(before, after)

    def test_register_and_login_and_logout(self):
        """
        Logout and redirect to the user.

        Args:
            self: (todo): write your description
        """
        # register a new account
        response = self.register_user(self.username_alice)
        # expect redirect to login
        self.assert_redirects(response, "/auth/login")

        # login with the new account
        response = self.login_user(self.username_alice)
        # expect redirect to index
        self.assert_redirects(response, "/")

        # logout
        response = self.client.get(url_for("auth.logout"), follow_redirects=True)
        # follow redirect to index
        self.assert_200(response)
        self.assert_template_used("index.html")
