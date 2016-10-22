# -*- coding: utf-8 -*-

from flask import jsonify, request, abort, url_for

from app.api import api
from app.models import User, Todo, TodoList
from app.decorators import admin_required


@api.route('/')
def get_routes():
    return jsonify({
        'users': url_for('api.get_users', _external=True),
        'todolists': url_for('api.get_todolists', _external=True),
    })


@api.route('/users/')
def get_users():
    return jsonify({'users': [user.to_dict() for user in User.query.all()]})


@api.route('/user/<string:username>/')
def get_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return jsonify(user.to_dict())


@api.route('/user/', methods=['POST'])
def add_user():
    try:
        user = User(
            username=request.json.get('username'),
            email=request.json.get('email'),
            password=request.json.get('password'),
        ).save()
    except:
        abort(400)
    return jsonify(user.to_dict()), 201


@api.route('/user/<string:username>/todolists/')
def get_user_todolists(username):
    user = User.query.filter_by(username=username).first_or_404()
    todolists = user.todolists
    return jsonify({
        'todolists': [todolist.to_dict() for todolist in todolists]
    })


@api.route('/user/<string:username>/todolist/<int:todolist_id>/')
def get_user_todolist(username, todolist_id):
    user = User.query.filter_by(username=username).first()
    todolist = TodoList.query.get_or_404(todolist_id)
    if not user or username != todolist.creator:
        abort(404)
    return jsonify(todolist.to_dict())


@api.route('/user/<string:username>/todolist/', methods=['POST'])
def add_user_todolist(username):
    user = User.query.filter_by(username=username).first_or_404()
    try:
        todolist = TodoList(
            title=request.json.get('title'),
            creator=user.username
        ).save()
    except:
        abort(400)
    return jsonify(todolist.to_dict()), 201


@api.route('/todolists/')
def get_todolists():
    todolists = TodoList.query.all()
    return jsonify({
        'todolists': [todolist.to_dict() for todolist in todolists]
    })


@api.route('/todolist/<int:todolist_id>/')
def get_todolist(todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    return jsonify(todolist.to_dict())


@api.route('/todolist/', methods=['POST'])
def add_todolist():
    try:
        todolist = TodoList(title=request.json.get('title')).save()
    except:
        abort(400)
    return jsonify(todolist.to_dict()), 201


@api.route('/todolist/<int:todolist_id>/todos/')
def get_todolist_todos(todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    return jsonify({
        'todos': [todo.to_dict() for todo in todolist.todos]
    })


@api.route('/user/<string:username>/todolist/<int:todolist_id>/todos/')
def get_user_todolist_todos(username, todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    if todolist.creator != username:
        abort(404)
    return jsonify({
        'todos': [todo.to_dict() for todo in todolist.todos]
    })


@api.route('/user/<string:username>/todolist/<int:todolist_id>/',
           methods=['POST'])
def add_user_todolist_todo(username, todolist_id):
    user = User.query.filter_by(username=username).first_or_404()
    todolist = TodoList.query.get_or_404(todolist_id)
    try:
        todo = Todo(
            description=request.json.get('description'),
            todolist_id=todolist.id,
            creator=user.username
        ).save()
    except:
        abort(400)
    return jsonify(todo.to_dict()), 201


@api.route('/todolist/<int:todolist_id>/', methods=['POST'])
def add_todolist_todo(todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    try:
        todo = Todo(
            description=request.json.get('description'),
            todolist_id=todolist.id
        ).save()
    except:
        abort(400)
    return jsonify(todo.to_dict()), 201


@api.route('/todo/<int:todo_id>/')
def get_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    return jsonify(todo.to_dict())


@api.route('/todo/<int:todo_id>/', methods=['PUT'])
def update_todo_status(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    try:
        if request.json.get('is_finished'):
            todo.finished()
        else:
            todo.reopen()
    except:
        abort(400)
    return jsonify(todo.to_dict())


@api.route('/todolist/<int:todolist_id>/', methods=['PUT'])
def change_todolist_title(todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    try:
        todolist.title = request.json.get('title')
        todolist.save()
    except:
        abort(400)
    return jsonify(todolist.to_dict())


@api.route('/user/<string:username>/', methods=['DELETE'])
@admin_required
def delete_user(username):
    user = User.query.get_or_404(username=username)
    try:
        if username == request.json.get('username'):
            user.delete()
            return jsonify()
        else:
            abort(400)
    except:
        abort(400)


@api.route('/todolist/<int:todolist_id>/', methods=['DELETE'])
@admin_required
def delete_todolist(todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    try:
        if todolist_id == request.json.get('todolist_id'):
            todolist.delete()
            return jsonify()
        else:
            abort(400)
    except:
        abort(400)


@api.route('/todo/<int:todo_id>/', methods=['DELETE'])
@admin_required
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    try:
        if todo_id == request.json.get('todo_id'):
            todo.delete()
            return jsonify()
        else:
            abort(400)
    except:
        abort(400)
