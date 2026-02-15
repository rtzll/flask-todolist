from flask import abort, request, url_for
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app import db
from app.api import api
from app.decorators import admin_required
from app.models import Todo, TodoList, User


@api.route("/")
def get_routes():
    return {
        "users": url_for("api.get_users", _external=True),
        "todolists": url_for("api.get_todolists", _external=True),
    }


@api.route("/users/")
def get_users():
    users = db.session.execute(select(User)).scalars().all()
    return {"users": [user.to_dict() for user in users]}


@api.route("/user/<string:username>/")
def get_user(username):
    user = db.first_or_404(select(User).filter_by(username=username))
    return user.to_dict()


@api.route("/user/", methods=["POST"])
def add_user():
    payload = request.get_json(silent=True)
    if payload is None:
        abort(400)
    try:
        user = User(
            username=payload.get("username"),
            email=payload.get("email"),
            password=payload.get("password"),
        ).save()
    except (AttributeError, IntegrityError, ValueError):
        abort(400)
    return user.to_dict(), 201


@api.route("/user/<string:username>/todolists/")
def get_user_todolists(username):
    user = db.first_or_404(select(User).filter_by(username=username))
    todolists = user.todolists
    return {"todolists": [todolist.to_dict() for todolist in todolists]}


@api.route("/user/<string:username>/todolist/<int:todolist_id>/")
def get_user_todolist(username, todolist_id):
    user = db.session.execute(
        select(User).filter_by(username=username)
    ).scalar_one_or_none()
    todolist = db.get_or_404(TodoList, todolist_id)
    if not user or username != todolist.creator:
        abort(404)
    return todolist.to_dict()


@api.route("/user/<string:username>/todolist/", methods=["POST"])
def add_user_todolist(username):
    user = db.first_or_404(select(User).filter_by(username=username))
    payload = request.get_json(silent=True)
    if payload is None:
        abort(400)
    try:
        todolist = TodoList(title=payload.get("title"), creator=user.username).save()
    except (AttributeError, IntegrityError, ValueError):
        abort(400)
    return todolist.to_dict(), 201


@api.route("/todolists/")
def get_todolists():
    todolists = db.session.execute(select(TodoList)).scalars().all()
    return {"todolists": [todolist.to_dict() for todolist in todolists]}


@api.route("/todolist/<int:todolist_id>/")
def get_todolist(todolist_id):
    todolist = db.get_or_404(TodoList, todolist_id)
    return todolist.to_dict()


@api.route("/todolist/", methods=["POST"])
def add_todolist():
    payload = request.get_json(silent=True)
    if payload is None:
        abort(400)
    try:
        todolist = TodoList(title=payload.get("title")).save()
    except (AttributeError, IntegrityError, ValueError):
        abort(400)
    return todolist.to_dict(), 201


@api.route("/todolist/<int:todolist_id>/todos/")
def get_todolist_todos(todolist_id):
    todolist = db.get_or_404(TodoList, todolist_id)
    return {"todos": [todo.to_dict() for todo in todolist.todos]}


@api.route("/user/<string:username>/todolist/<int:todolist_id>/todos/")
def get_user_todolist_todos(username, todolist_id):
    todolist = db.get_or_404(TodoList, todolist_id)
    if todolist.creator != username:
        abort(404)
    return {"todos": [todo.to_dict() for todo in todolist.todos]}


@api.route("/user/<string:username>/todolist/<int:todolist_id>/", methods=["POST"])
def add_user_todolist_todo(username, todolist_id):
    user = db.first_or_404(select(User).filter_by(username=username))
    todolist = db.get_or_404(TodoList, todolist_id)
    if todolist.creator != user.username:
        abort(404)
    payload = request.get_json(silent=True)
    if payload is None:
        abort(400)
    try:
        todo = Todo(
            description=payload.get("description"),
            todolist_id=todolist.id,
            creator=user.username,
        ).save()
    except (AttributeError, IntegrityError, ValueError):
        abort(400)
    return todo.to_dict(), 201


@api.route("/todolist/<int:todolist_id>/", methods=["POST"])
def add_todolist_todo(todolist_id):
    todolist = db.get_or_404(TodoList, todolist_id)
    payload = request.get_json(silent=True)
    if payload is None:
        abort(400)
    try:
        todo = Todo(
            description=payload.get("description"), todolist_id=todolist.id
        ).save()
    except (AttributeError, IntegrityError, ValueError):
        abort(400)
    return todo.to_dict(), 201


@api.route("/todo/<int:todo_id>/")
def get_todo(todo_id):
    todo = db.get_or_404(Todo, todo_id)
    return todo.to_dict()


@api.route("/todo/<int:todo_id>/", methods=["PUT"])
def update_todo_status(todo_id):
    todo = db.get_or_404(Todo, todo_id)
    payload = request.get_json(silent=True)
    if payload is None:
        abort(400)
    try:
        if payload.get("is_finished"):
            todo.finished()
        else:
            todo.reopen()
    except (AttributeError, ValueError):
        abort(400)
    return todo.to_dict()


@api.route("/todolist/<int:todolist_id>/", methods=["PUT"])
def change_todolist_title(todolist_id):
    todolist = db.get_or_404(TodoList, todolist_id)
    payload = request.get_json(silent=True)
    if payload is None:
        abort(400)
    try:
        todolist.title = payload.get("title")
        todolist.save()
    except (AttributeError, IntegrityError, ValueError):
        abort(400)
    return todolist.to_dict()


@api.route("/user/<string:username>/", methods=["DELETE"])
@admin_required
def delete_user(username):
    user = db.first_or_404(select(User).filter_by(username=username))
    payload = request.get_json(silent=True) or {}
    if username != payload.get("username"):
        abort(400)
    user.delete()
    return {}


@api.route("/todolist/<int:todolist_id>/", methods=["DELETE"])
@admin_required
def delete_todolist(todolist_id):
    todolist = db.get_or_404(TodoList, todolist_id)
    payload = request.get_json(silent=True) or {}
    if todolist_id != payload.get("todolist_id"):
        abort(400)
    todolist.delete()
    return {}


@api.route("/todo/<int:todo_id>/", methods=["DELETE"])
@admin_required
def delete_todo(todo_id):
    todo = db.get_or_404(Todo, todo_id)
    payload = request.get_json(silent=True) or {}
    if todo_id != payload.get("todo_id"):
        abort(400)
    todo.delete()
    return {}
