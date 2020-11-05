import re
from datetime import datetime

from flask import url_for
from flask_login import UserMixin
from sqlalchemy.orm import synonym
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager

EMAIL_REGEX = re.compile(r"^\S+@\S+\.\S+$")
USERNAME_REGEX = re.compile(r"^\S+$")


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
        """
        Create a model object from a dictionary.

        Args:
            cls: (todo): write your description
            model_dict: (dict): write your description
        """
        return cls(**model_dict).save()


class User(UserMixin, db.Model, BaseModel):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    _username = db.Column("username", db.String(64), unique=True)
    _email = db.Column("email", db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    todolists = db.relationship("TodoList", backref="user", lazy="dynamic")

    def __init__(self, **kwargs):
        """
        Initialize the class.

        Args:
            self: (todo): write your description
        """
        super().__init__(**kwargs)

    def __repr__(self):
        """
        Return a human - readable representation of this object.

        Args:
            self: (todo): write your description
        """
        if self.is_admin:
            return f"<Admin {self.username}>"
        return f"<User {self.username}>"

    @property
    def username(self):
        """
        The username of the user.

        Args:
            self: (todo): write your description
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Validate username.

        Args:
            self: (todo): write your description
            username: (str): write your description
        """
        is_valid_length = check_length(username, 64)
        if not is_valid_length or not bool(USERNAME_REGEX.match(username)):
            raise ValueError(f"{username} is not a valid username")
        self._username = username

    username = synonym("_username", descriptor=username)

    @property
    def email(self):
        """
        Get the email address.

        Args:
            self: (todo): write your description
        """
        return self._email

    @email.setter
    def email(self, email):
        """
        Sets the email address.

        Args:
            self: (todo): write your description
            email: (str): write your description
        """
        if not check_length(email, 64) or not bool(EMAIL_REGEX.match(email)):
            raise ValueError(f"{email} is not a valid email address")
        self._email = email

    email = synonym("_email", descriptor=email)

    @property
    def password(self):
        """
        Set the password.

        Args:
            self: (todo): write your description
        """
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        """
        Generate a password.

        Args:
            self: (todo): write your description
            password: (str): write your description
        """
        if not bool(password):
            raise ValueError("no password given")

        hashed_password = generate_password_hash(password)
        if not check_length(hashed_password, 128):
            raise ValueError("not a valid password, hash is too long")
        self.password_hash = hashed_password

    def verify_password(self, password):
        """
        Verifies whether a given password matches.

        Args:
            self: (todo): write your description
            password: (str): write your description
        """
        return check_password_hash(self.password_hash, password)

    def seen(self):
        """
        Return the last modified time.

        Args:
            self: (todo): write your description
        """
        self.last_seen = datetime.utcnow()
        return self.save()

    def to_dict(self):
        """
        Returns a dict to a dict.

        Args:
            self: (todo): write your description
        """
        return {
            "username": self.username,
            "user_url": url_for("api.get_user", username=self.username, _external=True),
            "member_since": self.member_since,
            "last_seen": self.last_seen,
            "todolists": url_for(
                "api.get_user_todolists", username=self.username, _external=True
            ),
            "todolist_count": self.todolists.count(),
        }

    def promote_to_admin(self):
        """
        Promote the user to save the admin.

        Args:
            self: (todo): write your description
        """
        self.is_admin = True
        return self.save()


@login_manager.user_loader
def load_user(user_id):
    """
    Load a user by id

    Args:
        user_id: (str): write your description
    """
    return User.query.get(int(user_id))


class TodoList(db.Model, BaseModel):
    __tablename__ = "todolist"
    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column("title", db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator = db.Column(db.String(64), db.ForeignKey("user.username"))
    todos = db.relationship("Todo", backref="todolist", lazy="dynamic")

    def __init__(self, title=None, creator=None, created_at=None):
        """
        Initialize the database.

        Args:
            self: (todo): write your description
            title: (str): write your description
            creator: (todo): write your description
            created_at: (todo): write your description
        """
        self.title = title or "untitled"
        self.creator = creator
        self.created_at = created_at or datetime.utcnow()

    def __repr__(self):
        """
        Return a repr representation of a repr__.

        Args:
            self: (todo): write your description
        """
        return f"<Todolist: {self.title}>"

    @property
    def title(self):
        """
        Returns the title of the document.

        Args:
            self: (todo): write your description
        """
        return self._title

    @title.setter
    def title(self, title):
        """
        Sets the title.

        Args:
            self: (todo): write your description
            title: (str): write your description
        """
        if not check_length(title, 128):
            raise ValueError(f"{title} is not a valid title")
        self._title = title

    title = synonym("_title", descriptor=title)

    @property
    def todos_url(self):
        """
        Returns the url of this instance.

        Args:
            self: (todo): write your description
        """
        url = None
        kwargs = dict(todolist_id=self.id, _external=True)
        if self.creator:
            kwargs["username"] = self.creator
            url = "api.get_user_todolist_todos"
        return url_for(url or "api.get_todolist_todos", **kwargs)

    def to_dict(self):
        """
        Serialize object to a dict.

        Args:
            self: (todo): write your description
        """
        return {
            "title": self.title,
            "creator": self.creator,
            "created_at": self.created_at,
            "total_todo_count": self.todo_count,
            "open_todo_count": self.open_count,
            "finished_todo_count": self.finished_count,
            "todos": self.todos_url,
        }

    @property
    def todo_count(self):
        """
        Return the number of todoist.

        Args:
            self: (todo): write your description
        """
        return self.todos.order_by(None).count()

    @property
    def finished_count(self):
        """
        Return the number of tasks that have finished.

        Args:
            self: (todo): write your description
        """
        return self.todos.filter_by(is_finished=True).count()

    @property
    def open_count(self):
        """
        Return the number of open count.

        Args:
            self: (todo): write your description
        """
        return self.todos.filter_by(is_finished=False).count()


class Todo(db.Model, BaseModel):
    __tablename__ = "todo"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, index=True, default=None)
    is_finished = db.Column(db.Boolean, default=False)
    creator = db.Column(db.String(64), db.ForeignKey("user.username"))
    todolist_id = db.Column(db.Integer, db.ForeignKey("todolist.id"))

    def __init__(self, description, todolist_id, creator=None, created_at=None):
        """
        Initialize the object.

        Args:
            self: (todo): write your description
            description: (str): write your description
            todolist_id: (str): write your description
            creator: (todo): write your description
            created_at: (todo): write your description
        """
        self.description = description
        self.todolist_id = todolist_id
        self.creator = creator
        self.created_at = created_at or datetime.utcnow()

    def __repr__(self):
        """
        Return a human - readable representation of this object.

        Args:
            self: (todo): write your description
        """
        return "<{} Todo: {} by {}>".format(
            self.status, self.description, self.creator or "None"
        )

    @property
    def status(self):
        """
        Return the status string.

        Args:
            self: (todo): write your description
        """
        return "finished" if self.is_finished else "open"

    def finished(self):
        """
        Called when the task.

        Args:
            self: (todo): write your description
        """
        self.is_finished = True
        self.finished_at = datetime.utcnow()
        self.save()

    def reopen(self):
        """
        Reopen the lock.

        Args:
            self: (todo): write your description
        """
        self.is_finished = False
        self.finished_at = None
        self.save()

    def to_dict(self):
        """
        Return a dict to a dictionary.

        Args:
            self: (todo): write your description
        """
        return {
            "description": self.description,
            "creator": self.creator,
            "created_at": self.created_at,
            "status": self.status,
        }
