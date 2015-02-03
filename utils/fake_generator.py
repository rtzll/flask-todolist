# -*- coding: utf-8 -*-

import random
import forgery_py

from sqlalchemy.exc import InvalidRequestError, IntegrityError
from app import db
from app.models import User, Todo, TodoList


class FakeGenerator(object):

    def __init__(self):
        # in case the tables haven't been created already
        db.drop_all()
        db.create_all()
        self.users = []
        self.todolists = []
        self.todos = []

    def genereate_fake_users(self, count=42):
        for i in xrange(count):

            try:
                user = User(email=forgery_py.internet.email_address(),
                            username=forgery_py.internet.user_name(True),
                            password="correcthorsebatterystaple",
                            member_since=forgery_py.date.date(True)).save()

            except (InvalidRequestError, IntegrityError), err:
                # unlucky, we tried an existing email or username
                pass  # me the dice I'm feeling lucky again!

            else:
                self.users.append(user)

    def genereate_fake_todolists(self, count=42):
        # for the creator relation we need users
        assert self.users != []
        for i in xrange(count):
            todolist = TodoList(title=forgery_py.forgery.lorem_ipsum.title(),
                                creator_id=random.choice(self.users).id,
                                created_at=forgery_py.date.date(True)).save()
            self.todolists.append(todolist)

    def genereate_fake_todo(self, count=42):
        # for the todolist relation we need todolists
        assert self.todolists != []
        for i in xrange(count):
            todo = Todo(description=forgery_py.forgery.lorem_ipsum.words(),
                        todolist_id=random.choice(self.todolists).id,
                        created_at=forgery_py.date.date(True)).save()
            self.todos.append(todo)


    def generate_fake_data(self, count=42):
        self.genereate_fake_users(count)
        self.genereate_fake_todolists(count*2)
        self.genereate_fake_todolists(count*3)
