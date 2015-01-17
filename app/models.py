# -*- coding: utf-8 -*-

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from . import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    todos = db.relationship('Todo', backref='creator', lazy='dynamic')

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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(140))
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, description, creator_id):
        self.description = description
        self.creator_id = creator_id

    def __repr__(self):
        creator = User.query.filter_by(id=self.creator_id)
        return '<Todo: %r from %r>' % (self.description, creator.username)
