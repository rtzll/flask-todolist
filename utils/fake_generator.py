# -*- coding: utf-8 -*-

import random
import datetime
import forgery_py

from sqlalchemy.exc import InvalidRequestError, IntegrityError
from app import db
from app.models import User, Todo, TodoList


class FakeGenerator(object):

    def __init__(self, count=42):
        # in case the tables haven't been created already
        db.drop_all()
        db.create_all()

    def genereate_fake_users(self, count=42):
        for i in xrange(count):
            try:
                dt = datetime.datetime.combine(forgery_py.date.date(True),
                                               datetime.time())
                user = User(email=forgery_py.internet.email_address(),
                            username=forgery_py.internet.user_name(True),
                            password="correcthorsebatterystaple",
                            member_since=dt).save()

            except (InvalidRequestError, IntegrityError), err:
                # unlucky, we tried an existing email or username
                pass  # me the dice I'm feeling lucky again!

    def genereate_fake_todolists(self, count=42):
        # for the creator relation we need users
        users = User.query.all()
        assert users != []
        for i in xrange(count):
            dt = datetime.datetime.combine(forgery_py.date.date(True),
                                           datetime.time())
            todolist = TodoList(title=forgery_py.forgery.lorem_ipsum.title(),
                                creator_id=random.choice(users).id,
                                created_at=dt).save()

    def genereate_fake_todo(self, count=42):
        # for the todolist relation we need todolists
        todolists = TodoList.query.all()
        assert todolists != []
        for i in xrange(count):
            dt = datetime.datetime.combine(forgery_py.date.date(True),
                                           datetime.time())
            todo = Todo(description=forgery_py.forgery.lorem_ipsum.words(),
                        todolist_id=random.choice(todolists).id,
                        created_at=dt).save()
            if random.choice([True, False]):
                todo.finished_todo()


    def generate_fake_data(self, count=42):
        # generation must follow this order, as each builds on the previous
        self.genereate_fake_users(count)
        self.genereate_fake_todolists(count*2)
        self.genereate_fake_todo(count*4)


    def start(self, count=42):
        self.generate_fake_data(count)
