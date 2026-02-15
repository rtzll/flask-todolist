from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, Self

from flask import url_for
from flask_login import UserMixin
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DynamicMapped, Mapped, mapped_column, relationship, synonym
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager

EMAIL_REGEX = re.compile(r"^\S+@\S+\.\S+$")
USERNAME_REGEX = re.compile(r"^\S+$")


def check_length(attribute: object, length: int) -> bool:
    """Checks the attribute's length."""
    try:
        return bool(attribute) and len(attribute) <= length
    except TypeError:
        return False


class BaseModel:
    """Base for all models, providing save, delete and from_dict methods."""

    def __commit(self) -> None:
        """Commits the current db.session, does rollback on failure."""
        from sqlalchemy.exc import IntegrityError

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise

    def delete(self) -> None:
        """Deletes this model from the db (through db.session)"""
        db.session.delete(self)
        self.__commit()

    def save(self) -> Self:
        """Adds this model to the db (through db.session)"""
        db.session.add(self)
        self.__commit()
        return self

    @classmethod
    def from_dict(cls, model_dict: Mapping[str, Any]) -> Self:
        return cls(**dict(model_dict)).save()


class User(UserMixin, db.Model, BaseModel):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _username: Mapped[str | None] = mapped_column("username", String(64), unique=True)
    _email: Mapped[str | None] = mapped_column("email", String(64), unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(128))
    member_since: Mapped[datetime | None] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    todolists: DynamicMapped[TodoList] = relationship(
        "TodoList", backref="user", lazy="dynamic"
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        if self.is_admin:
            return f"<Admin {self.username}>"
        return f"<User {self.username}>"

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, username: str) -> None:
        is_valid_length = check_length(username, 64)
        if not is_valid_length or not bool(USERNAME_REGEX.match(username)):
            raise ValueError(f"{username} is not a valid username")
        self._username = username

    username = synonym("_username", descriptor=username)

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email: str) -> None:
        if not check_length(email, 64) or not bool(EMAIL_REGEX.match(email)):
            raise ValueError(f"{email} is not a valid email address")
        self._email = email

    email = synonym("_email", descriptor=email)

    @property
    def password(self) -> str:
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password: str) -> None:
        if not bool(password):
            raise ValueError("no password given")

        hashed_password = generate_password_hash(password)
        if len(hashed_password) > 256:
            raise ValueError("not a valid password, hash is too long")
        self.password_hash = hashed_password

    def verify_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def seen(self) -> Self:
        self.last_seen = datetime.now(UTC)
        return self.save()

    def to_dict(self) -> dict[str, Any]:
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

    def promote_to_admin(self) -> Self:
        self.is_admin = True
        return self.save()


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))


class TodoList(db.Model, BaseModel):
    __tablename__ = "todolist"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _title: Mapped[str | None] = mapped_column("title", String(128))
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    creator: Mapped[str | None] = mapped_column(String(64), ForeignKey("user.username"))
    todos: DynamicMapped[Todo] = relationship(
        "Todo", backref="todolist", lazy="dynamic"
    )

    def __init__(
        self,
        title: str | None = None,
        creator: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.title = title or "untitled"
        self.creator = creator
        self.created_at = created_at or datetime.now(UTC)

    def __repr__(self) -> str:
        return f"<Todolist: {self.title}>"

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: str) -> None:
        if not check_length(title, 128):
            raise ValueError(f"{title} is not a valid title")
        self._title = title

    title = synonym("_title", descriptor=title)

    @property
    def todos_url(self) -> str:
        url = None
        kwargs = dict(todolist_id=self.id, _external=True)
        if self.creator:
            kwargs["username"] = self.creator
            url = "api.get_user_todolist_todos"
        return url_for(url or "api.get_todolist_todos", **kwargs)

    def to_dict(self) -> dict[str, Any]:
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
    def todo_count(self) -> int:
        return int(self.todos.order_by(None).count())

    @property
    def finished_count(self) -> int:
        return int(self.todos.filter_by(is_finished=True).count())

    @property
    def open_count(self) -> int:
        return int(self.todos.filter_by(is_finished=False).count())


class Todo(db.Model, BaseModel):
    __tablename__ = "todo"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, index=True, default=lambda: datetime.now(UTC)
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime, index=True, default=None
    )
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False)
    creator: Mapped[str | None] = mapped_column(String(64), ForeignKey("user.username"))
    todolist_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("todolist.id"))

    def __init__(
        self,
        description: str,
        todolist_id: int,
        creator: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.description = description
        self.todolist_id = todolist_id
        self.creator = creator
        self.created_at = created_at or datetime.now(UTC)

    def __repr__(self) -> str:
        return "<{} Todo: {} by {}>".format(
            self.status, self.description, self.creator or "None"
        )

    @property
    def status(self) -> str:
        return "finished" if self.is_finished else "open"

    def finished(self) -> None:
        self.is_finished = True
        self.finished_at = datetime.now(UTC)
        self.save()

    def reopen(self) -> None:
        self.is_finished = False
        self.finished_at = None
        self.save()

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "creator": self.creator,
            "created_at": self.created_at,
            "status": self.status,
        }
