# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(140))
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User',
        backref=db.backref('todo', lazy='dynamic'))

    def __init__(self, description, creator):
        self.description = description
        self.creator = creator

    def __repr__(self):
        return '<ToDo: %r>' % self.description


@app.route('/todo/<int:todo_id>')
def show_todo(todo_id):
    todo = Todo.query.get(todo_id)
    return render_template('show_todo.html', todo=todo)


@app.route('/user/<int:user_id>')
def show_user(user_id):
    user = User.query.get(user_id)
    return render_template('show_user.html', user=user)
