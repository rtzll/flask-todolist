from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import restless

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
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
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User',
        backref=db.backref('todo', lazy='dynamic'))

    def __init__(self, description, creator):
        self.description = description
        self.creator = creator

    def __repr__(self):
        return '<ToDo: %r>' % self.description


# Create the database tables.
db.create_all()

# Create the Flask-Restless API manager.
manager = restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(User, methods=['GET', 'POST', 'DELETE'])
manager.create_api(Todo, methods=['GET', 'POST', 'DELETE'])

# start the flask loop
app.run()