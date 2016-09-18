# -*- coding: utf-8 -*-

from flask import jsonify, request, abort, url_for

from datetime import datetime

from . import api
from ..models import User, Todo, TodoList
from ..decorators import admin_required


@api.route('/')
def get_routes():
    routes = dict()
    routes['users'] = url_for('api.get_users', _external=True)
    routes['todolists'] = url_for('api.get_todolists', _external=True)
    return jsonify(routes)


@api.route('/users/')
def get_users():
    users = User.query.all()
    return jsonify({
        'users': [{'user': user.to_json()} for user in users]
    })


@api.route('/user/<username>/')
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    return jsonify({'user': user.to_json()})


@api.route('/user/', methods=['POST'])
def add_user():
    try:
        username = request.json.get('username')
        email = request.json.get('email')
        password = request.json.get('password')
        if User.is_valid_username(username) and User.is_valid_email(email) \
                and User.is_valid_password(password):
            user = User(
                username=username, email=email, password=password
            ).save()
        else:
            abort(500)
    except:
        abort(500)
    return jsonify({'user': user.to_json()}), 201


@api.route('/user/<username>/todolists/')
def get_user_todolists(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    todolists = user.todolists
    return jsonify({
        'todolists': [todolist.to_json() for todolist in todolists]
    })


@api.route('/user/<username>/todolist/<int:todolist_id>/')
def get_user_todolist(username, todolist_id):
    user = User.query.filter_by(username=username).first()
    todolist = TodoList.query.get_or_404(todolist_id)
    if not user or username != todolist.creator:
        abort(404)
    return jsonify({'todolist': todolist.to_json()})


@api.route('/user/<username>/todolist/', methods=['POST'])
def add_user_todolist(username):
    user = User.query.filter_by(username=username).first_or_404()
    try:
        todolist = TodoList(
            title=request.json.get('title'),
            creator=user.username
        ).save()
    except:
        abort(500)
    return jsonify({'todolist': todolist.to_json()}), 201


@api.route('/todolists/')
def get_todolists():
    todolists = TodoList.query.all()
    return jsonify({
        'todolists': [todolist.to_json() for todolist in todolists]
    })


@api.route('/todolist/<int:todolist_id>/')
def get_todolist(todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    return jsonify({'todolist': todolist.to_json()})


@api.route('/todolist/', methods=['POST'])
def add_todolist():
    try:
        title = request.json.get('title')
        if title and TodoList.is_valid_title(title):
            todolist = TodoList(title=title).save()
        else:
            abort(500)
    except:
        abort(500)
    return jsonify({'todolist': todolist.to_json()}), 201


@api.route('/todolist/<int:todolist_id>/todos/')
def get_todolist_todos(todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    return jsonify({
        'todos': [todo.to_json() for todo in todolist.todos]
    })


@api.route('/user/<username>/todolist/<int:todolist_id>/todos/')
def get_user_todolist_todos(username, todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    if todolist.creator != username:
        abort(404)
    return jsonify({
        'todos': [todo.to_json() for todo in todolist.todos]
    })


@api.route('/user/<username>/todolist/<int:todolist_id>/', methods=['POST'])
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
        abort(500)
    return jsonify({'todo': todo.to_json()}), 201


@api.route('/todolist/<int:todolist_id>/', methods=['POST'])
def add_todolist_todo(todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    try:
        todo = Todo(
            description=request.json.get('description'),
            todolist_id=todolist.id
        ).save()
    except:
        abort(500)
    return jsonify({'todo': todo.to_json()}), 201


@api.route('/todo/<int:todo_id>/')
def get_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    return jsonify({'todo': todo.to_json()})


@api.route('/todo/<int:todo_id>/', methods=['PUT'])
def update_todo_status(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    try:
        todo_json = request.json.get('todo')
        todo.is_finished = todo_json.get('is_finished')
        if todo.is_finished:
            todo.finished_at = datetime.strptime(
                todo_json.get('finished_at'), '%Y-%m-%dT%H:%M:%S.%fZ'
            )
        else:
            todo.finished_at = None
        todo.save()
    except:
        abort(500)
    return jsonify({'todo': todo.to_json()})


@api.route('/todolist/<int:todolist_id>/', methods=['PUT'])
def change_todolist_title(todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    try:
        todolist_json = request.json.get('todolist')
        title = todolist_json.get('title')
        if TodoList.is_valid_title(title):
            todolist.change_title(title)
        else:
            abort(500)
    except:
        abort(500)
    return jsonify({'todolist': todolist.to_json()})


@api.route('/user/<int:user_id>/', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        if user_id == request.json.get('user_id'):
            user.delete()
            return jsonify()
        else:
            abort(500)
    except:
        abort(500)


@api.route('/todolist/<int:todolist_id>/', methods=['DELETE'])
@admin_required
def delete_todolist(todolist_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    try:
        if todolist_id == request.json.get('todolist_id'):
            todolist.delete()
            return jsonify()
        else:
            abort(500)
    except:
        abort(500)


@api.route('/todo/<int:todo_id>/', methods=['DELETE'])
@admin_required
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    try:
        if todo_id == request.json.get('todo_id'):
            todo.delete()
            return jsonify()
        else:
            abort(500)
    except:
        abort(500)
