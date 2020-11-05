from flask import abort, request, url_for

from app.api import api
from app.decorators import admin_required
from app.models import Todo, TodoList, User


@api.route("/")
def get_routes():
    """
    List all routes

    Args:
    """
    return {
        "users": url_for("api.get_users", _external=True),
        "todolists": url_for("api.get_todolists", _external=True),
    }


@api.route("/users/")
def get_users():
    """
    Get all users.

    Args:
    """
    return {"users": [user.to_dict() for user in User.query.all()]}


@api.route("/user/<string:username>/")
def get_user(username):
    """
    Get user by username

    Args:
        username: (str): write your description
    """
    user = User.query.filter_by(username=username).first_or_404()
    return user.to_dict()


@api.route("/user/", methods=["POST"])
def add_user():
    """
    Add a user

    Args:
    """
    try:
        user = User(
            username=request.json.get("username"),
            email=request.json.get("email"),
            password=request.json.get("password"),
        ).save()
    except:
        abort(400)
    return user.to_dict(), 201


@api.route("/user/<string:username>/todolists/")
def get_user_todolists(username):
    """
    Get a user s username.

    Args:
        username: (str): write your description
    """
    user = User.query.filter_by(username=username).first_or_404()
    todolists = user.todolists
    return {"todolists": [todolist.to_dict() for todolist in todolists]}


@api.route("/user/<string:username>/todolist/<int:todolist_id>/")
def get_user_todolist(username, todolist_id):
    """
    Returns a list of all users.

    Args:
        username: (str): write your description
        todolist_id: (str): write your description
    """
    user = User.query.filter_by(username=username).first()
    todolist = TodoList.query.get_or_404(todolist_id)
    if not user or username != todolist.creator:
        abort(404)
    return todolist.to_dict()


@api.route("/user/<string:username>/todolist/", methods=["POST"])
def add_user_todolist(username):
    """
    Add a user to the database.

    Args:
        username: (str): write your description
    """
    user = User.query.filter_by(username=username).first_or_404()
    try:
        todolist = TodoList(
            title=request.json.get("title"), creator=user.username
        ).save()
    except:
        abort(400)
    return todolist.to_dict(), 201


@api.route("/todolists/")
def get_todolists():
    """
    Returns a list of todolists. todoist.

    Args:
    """
    todolists = TodoList.query.all()
    return {"todolists": [todolist.to_dict() for todolist in todolists]}


@api.route("/todolist/<int:todolist_id>/")
def get_todolist(todolist_id):
    """
    Return a list of todolist.

    Args:
        todolist_id: (str): write your description
    """
    todolist = TodoList.query.get_or_404(todolist_id)
    return todolist.to_dict()


@api.route("/todolist/", methods=["POST"])
def add_todolist():
    """
    Add a todolist.

    Args:
    """
    try:
        todolist = TodoList(title=request.json.get("title")).save()
    except:
        abort(400)
    return todolist.to_dict(), 201


@api.route("/todolist/<int:todolist_id>/todos/")
def get_todolist_todos(todolist_id):
    """
    Returns a list of todos.

    Args:
        todolist_id: (str): write your description
    """
    todolist = TodoList.query.get_or_404(todolist_id)
    return {"todos": [todo.to_dict() for todo in todolist.todos]}


@api.route("/user/<string:username>/todolist/<int:todolist_id>/todos/")
def get_user_todolist_todos(username, todolist_id):
    """
    Retrieve a list of lists.

    Args:
        username: (str): write your description
        todolist_id: (str): write your description
    """
    todolist = TodoList.query.get_or_404(todolist_id)
    if todolist.creator != username:
        abort(404)
    return {"todos": [todo.to_dict() for todo in todolist.todos]}


@api.route("/user/<string:username>/todolist/<int:todolist_id>/", methods=["POST"])
def add_user_todolist_todo(username, todolist_id):
    """
    Add a todolist.

    Args:
        username: (str): write your description
        todolist_id: (str): write your description
    """
    user = User.query.filter_by(username=username).first_or_404()
    todolist = TodoList.query.get_or_404(todolist_id)
    try:
        todo = Todo(
            description=request.json.get("description"),
            todolist_id=todolist.id,
            creator=user.username,
        ).save()
    except:
        abort(400)
    return todo.to_dict(), 201


@api.route("/todolist/<int:todolist_id>/", methods=["POST"])
def add_todolist_todo(todolist_id):
    """
    Add a todolist.

    Args:
        todolist_id: (str): write your description
    """
    todolist = TodoList.query.get_or_404(todolist_id)
    try:
        todo = Todo(
            description=request.json.get("description"), todolist_id=todolist.id
        ).save()
    except:
        abort(400)
    return todo.to_dict(), 201


@api.route("/todo/<int:todo_id>/")
def get_todo(todo_id):
    """
    Get a todoist.

    Args:
        todo_id: (str): write your description
    """
    todo = Todo.query.get_or_404(todo_id)
    return todo.to_dict()


@api.route("/todo/<int:todo_id>/", methods=["PUT"])
def update_todo_status(todo_id):
    """
    Updates the status of a status.

    Args:
        todo_id: (str): write your description
    """
    todo = Todo.query.get_or_404(todo_id)
    try:
        if request.json.get("is_finished"):
            todo.finished()
        else:
            todo.reopen()
    except:
        abort(400)
    return todo.to_dict()


@api.route("/todolist/<int:todolist_id>/", methods=["PUT"])
def change_todolist_title(todolist_id):
    """
    Updates the title

    Args:
        todolist_id: (str): write your description
    """
    todolist = TodoList.query.get_or_404(todolist_id)
    try:
        todolist.title = request.json.get("title")
        todolist.save()
    except:
        abort(400)
    return todolist.to_dict()


@api.route("/user/<string:username>/", methods=["DELETE"])
@admin_required
def delete_user(username):
    """
    Delete a user.

    Args:
        username: (str): write your description
    """
    user = User.query.get_or_404(username=username)
    try:
        if username == request.json.get("username"):
            user.delete()
            return {}
        else:
            abort(400)
    except:
        abort(400)


@api.route("/todolist/<int:todolist_id>/", methods=["DELETE"])
@admin_required
def delete_todolist(todolist_id):
    """
    Delete a list

    Args:
        todolist_id: (str): write your description
    """
    todolist = TodoList.query.get_or_404(todolist_id)
    try:
        if todolist_id == request.json.get("todolist_id"):
            todolist.delete()
            return jsonify()
        else:
            abort(400)
    except:
        abort(400)


@api.route("/todo/<int:todo_id>/", methods=["DELETE"])
@admin_required
def delete_todo(todo_id):
    """
    Delete a todo item.

    Args:
        todo_id: (str): write your description
    """
    todo = Todo.query.get_or_404(todo_id)
    try:
        if todo_id == request.json.get("todo_id"):
            todo.delete()
            return jsonify()
        else:
            abort(400)
    except:
        abort(400)
