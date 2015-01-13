# -*- coding: utf-8 -*-

from flask import Flask, render_template, flash, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from flask.ext.login import UserMixin, LoginManager
from flask.ext.login import login_user, logout_user, login_required, \
    current_user

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo

import logging
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    return app


app = create_app()
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app)


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


class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Log In')


class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                           Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password_confirmation',
        message='Passwords must match.')
    ])
    password_confirmation = PasswordField('Confirm password',
                                          validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class TodoForm(Form):
    todo = StringField('Enter your todo', validators=[Required()])
    submit = SubmitField('Submit')


@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)


@login_required
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You successfully registered. Welcome!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    todos = user.todos.order_by(Todo.timestamp.desc())
    return render_template('user.html', user=user, todos=todos)
