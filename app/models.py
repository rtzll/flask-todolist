# -*- coding: utf-8 -*-

import re
import json
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
from flask_login import UserMixin

from . import db, login_manager


class BaseModel:
    """Base for all models, providing save and delte methods."""

    def __commit(self):
        """Commits the current db.session, does rollback on failure."""
        from sqlalchemy.exc import IntegrityError
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    def delete(self):
        """Deletes this model from the db (through db.session)"""
        db.session.delete(self)
        self.__commit()

    def save(self):
        """Adds this model to the db (through db.session)"""
        db.session.add(self)
        self.__commit()
        return self


class User(UserMixin, db.Model, BaseModel):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    todolists = db.relationship('TodoList', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        if self.is_admin:
            return '<Admin {0}>'.format(self.username)
        return '<User {0}>'.format(self.username)

    @staticmethod
    def is_valid_username(username):
        return len(username) <= 64 and re.match('^\S+$', username)

    @staticmethod
    def is_valid_email(email):
        return len(email) <= 64 and re.match('^\S+@\S+\.\S+$', email)

    @staticmethod
    def is_valid_password(passwd):
        return len(generate_password_hash(passwd)) <= 128 and passwd

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def seen(self):
        self.last_seen = datetime.utcnow()
        return self.save()

    def to_json(self):
        json_user = {
            'username': self.username,
            'user_url': url_for(
                'api.get_user', username=self.username, _external=True
            ),
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'todolists': url_for(
                'api.get_user_todolists',
                username=self.username, _external=True
            ),
            'todolist_count': self.todolists.count()
        }
        return json_user

    @staticmethod
    def from_json(json_user):
        User(json.loads(json_user)).save()

    def promote_to_admin(self):
        self.is_admin = True
        return self.save()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class TodoList(db.Model, BaseModel):
    __tablename__ = 'todolist'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator = db.Column(db.String(64), db.ForeignKey('user.username'))
    todos = db.relationship('Todo', backref='todolist', lazy='dynamic')

    def __init__(self, title='untitled', creator=None,
                 created_at=datetime.utcnow()):
        self.title = title
        self.creator = creator
        self.created_at = created_at

    def __repr__(self):
        return '<Todolist: {0}>'.format(self.title)

    @staticmethod
    def is_valid_title(list_title):
        return len(list_title) <= 128 and list_title

    def change_title(self, new_title):
        self.title = new_title
        self.save()

    def to_json(self):
        if self.creator:
            todos_url = url_for(
                'api.get_user_todolist_todos',
                todolist_id=self.id, username=self.creator, _external=True
            )
        else:
            todos_url = url_for(
                'api.get_todolist_todos', todolist_id=self.id, _external=True
            )

        json_todolist = {
            'title': self.title,
            'creator': self.creator,
            'created_at': self.created_at,
            'total_todo_count': self.count_todos(),
            'open_todo_count': self.count_open(),
            'finished_todo_count': self.count_finished(),
            'todos': todos_url
        }
        return json_todolist

    @staticmethod
    def from_json(json_todolist):
        TodoList(json.loads(json_todolist)).save()

    def count_todos(self):
        return self.todos.order_by(None).count()

    def count_finished(self):
        return self.todos.filter_by(is_finished=True).count()

    def count_open(self):
        return self.todos.filter_by(is_finished=False).count()


class Todo(db.Model, BaseModel):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, index=True, default=None)
    is_finished = db.Column(db.Boolean, default=False)
    creator = db.Column(db.String(64), db.ForeignKey('user.username'))
    todolist_id = db.Column(db.Integer, db.ForeignKey('todolist.id'))

    def __init__(self, description, todolist_id, creator=None,
                 created_at=datetime.utcnow()):
        self.description = description
        self.todolist_id = todolist_id
        self.creator = creator
        self.created_at = created_at

    def __repr__(self):
        if self.creator is None:
            return '<Todo: {0}>'.format(self.description)
        status = 'finished' if self.is_finished else 'open'
        return '<{0} todo: {1} by {2}>'.format(
            status, self.description, self.creator)

    def finished(self):
        self.is_finished = True
        self.finished_at = datetime.utcnow()
        self.save()

    def reopen(self):
        self.is_finished = False
        self.finished_at = None
        self.save()

    def to_json(self):
        json_todo = {
            'description': self.description,
            'creator': self.creator,
            'created_at': self.created_at,
            'status': 'finished' if self.is_finished else 'open'
        }
        return json_todo

    @staticmethod
    def from_json(json_todo):
        Todo(json.loads(json_todo)).save()
