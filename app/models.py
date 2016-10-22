# -*- coding: utf-8 -*-

import re
from datetime import datetime

from sqlalchemy.orm import synonym
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
from flask_login import UserMixin

from app import db, login_manager

EMAIL_REGEX = re.compile(r'^\S+@\S+\.\S+$')
USERNAME_REGEX = re.compile(r'^\S+$')


def check_length(attribute, length):
    """Checks the attribute's length."""
    try:
        return bool(attribute) and len(attribute) <= length
    except:
        return False


class BaseModel:
    """Base for all models, providing save, delete and from_dict methods."""

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

    @classmethod
    def from_dict(cls, model_dict):
        return cls(**model_dict).save()


class User(UserMixin, db.Model, BaseModel):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    _username = db.Column('username', db.String(64), unique=True)
    _email = db.Column('email', db.String(64), unique=True)
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

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        is_valid_length = check_length(username, 64)
        if not is_valid_length or not bool(USERNAME_REGEX.match(username)):
            raise ValueError('{} is not a valid username'.format(username))
        self._username = username

    username = synonym('_username', descriptor=username)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        if not check_length(email, 64) or not bool(EMAIL_REGEX.match(email)):
            raise ValueError('{} is not a valid email address'.format(email))
        self._email = email

    email = synonym('_email', descriptor=email)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        if not bool(password):
            raise ValueError('no password given')

        hashed_password = generate_password_hash(password)
        if not check_length(hashed_password, 128):
            raise ValueError('not a valid password, hash is too long')
        self.password_hash = hashed_password

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def seen(self):
        self.last_seen = datetime.utcnow()
        return self.save()

    def to_dict(self):
        return {
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

    def promote_to_admin(self):
        self.is_admin = True
        return self.save()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class TodoList(db.Model, BaseModel):
    __tablename__ = 'todolist'
    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column('title', db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator = db.Column(db.String(64), db.ForeignKey('user.username'))
    todos = db.relationship('Todo', backref='todolist', lazy='dynamic')

    def __init__(self, title=None, creator=None, created_at=None):
        self.title = title or 'untitled'
        self.creator = creator
        self.created_at = created_at or datetime.utcnow()

    def __repr__(self):
        return '<Todolist: {0}>'.format(self.title)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        if not check_length(title, 128):
            raise ValueError('{} is not a valid title'.format(title))
        self._title = title

    title = synonym('_title', descriptor=title)

    @property
    def todos_url(self):
        url = None
        kwargs = dict(todolist_id=self.id, _external=True)
        if self.creator:
            kwargs['username'] = self.creator
            url = 'api.get_user_todolist_todos'
        return url_for(url or 'api.get_todolist_todos', **kwargs)

    def to_dict(self):
        return {
            'title': self.title,
            'creator': self.creator,
            'created_at': self.created_at,
            'total_todo_count': self.todo_count,
            'open_todo_count': self.open_count,
            'finished_todo_count': self.finished_count,
            'todos': self.todos_url,
        }

    @property
    def todo_count(self):
        return self.todos.order_by(None).count()

    @property
    def finished_count(self):
        return self.todos.filter_by(is_finished=True).count()

    @property
    def open_count(self):
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
                 created_at=None):
        self.description = description
        self.todolist_id = todolist_id
        self.creator = creator
        self.created_at = created_at or datetime.utcnow()

    def __repr__(self):
        return '<{0} Todo: {1} by {2}>'.format(
            self.status, self.description, self.creator or 'None')

    @property
    def status(self):
        return 'finished' if self.is_finished else 'open'

    def finished(self):
        self.is_finished = True
        self.finished_at = datetime.utcnow()
        self.save()

    def reopen(self):
        self.is_finished = False
        self.finished_at = None
        self.save()

    def to_dict(self):
        return {
            'description': self.description,
            'creator': self.creator,
            'created_at': self.created_at,
            'status': self.status,
        }
