import random
from datetime import datetime

import forgery_py

from app import db
from app.models import Todo, TodoList, User


class FakeGenerator:
    def __init__(self):
        # in case the tables haven't been created already
        db.drop_all()
        db.create_all()

    def generate_fake_date(self):
        return datetime.combine(forgery_py.date.date(True), datetime.utcnow().time())

    def generate_fake_users(self, count):
        for _ in range(count):
            User(
                email=forgery_py.internet.email_address(),
                username=forgery_py.internet.user_name(True),
                password="correcthorsebatterystaple",
                member_since=self.generate_fake_date(),
            ).save()

    def generate_fake_todolists(self, count):
        # for the creator relation we need users
        users = User.query.all()
        assert users != []
        for _ in range(count):
            TodoList(
                title=forgery_py.forgery.lorem_ipsum.title(),
                creator=random.choice(users).username,
                created_at=self.generate_fake_date(),
            ).save()

    def generate_fake_todo(self, count):
        # for the todolist relation we need todolists
        todolists = TodoList.query.all()
        assert todolists != []
        for _ in range(count):
            todolist = random.choice(todolists)
            todo = Todo(
                description=forgery_py.forgery.lorem_ipsum.words(),
                todolist_id=todolist.id,
                creator=todolist.creator,
                created_at=self.generate_fake_date(),
            ).save()
            if random.choice([True, False]):
                todo.finished()

    def generate_fake_data(self, count):
        # generation must follow this order, as each builds on the previous
        self.generate_fake_users(count)
        self.generate_fake_todolists(count * 4)
        self.generate_fake_todo(count * 16)

    def start(self, count=10):
        self.generate_fake_data(count)
