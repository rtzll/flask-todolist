# -*- coding: utf-8 -*-

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    todolists = db.relationship('TodoList', backref='creator', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return '<User %r>' % self.username

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
        db.session.add(self)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class TodoList(db.Model):
    __tablename__ = 'todolist'
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(128))
    todos = db.relationship('Todo', backref='todolist', lazy='dynamic')

    def __init__(self, title, creator_id=None):
        self.title = title
        self.creator_id = creator_id

    def __repr__(self):
        return '<todolist: {0}>'.format(self.title)


class Todo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, index=True, default=None)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    todolist_id = db.Column(db.Integer, db.ForeignKey('todolist.id'))

    def __init__(self, description, creator_id=None):
        self.description = description
        self.creator_id = creator_id

    def __repr__(self):
        description = self.description
        if self.creator_id is None:
            return '<todo: {0}>'.format(description)
        creator = User.query.filter_by(id=self.creator_id).first().username
        status = 'open' if self.finished_at is None else 'finished'
        return '<{0} todo: {1} from {2}>'.format(status, description, creator)

    def finished(self):
        self.finished_at = datetime.utcnow()
