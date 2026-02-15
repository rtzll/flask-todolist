import random
from datetime import UTC, datetime

import forgery_py
from sqlalchemy import select

from app import db
from app.models import Todo, TodoList, User


class FakeGenerator:
    def __init__(self):
        # in case the tables haven't been created already
        db.drop_all()
        db.create_all()

    def generate_fake_date(self):
        return datetime.combine(forgery_py.date.date(True), datetime.now(UTC).time())

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
        users = db.session.execute(select(User)).scalars().all()
        assert users != []
        for _ in range(count):
            TodoList(
                title=forgery_py.forgery.lorem_ipsum.title(),
                creator=random.choice(users).username,
                created_at=self.generate_fake_date(),
            ).save()

    def generate_fake_todo(self, count):
        # for the todolist relation we need todolists
        todolists = db.session.execute(select(TodoList)).scalars().all()
        assert todolists != []
        for _ in range(count):
            todolist = random.choice(todolists)
            description = forgery_py.forgery.lorem_ipsum.words()
            if isinstance(description, list):
                description = " ".join(description)
            todo = Todo(
                description=description,
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
