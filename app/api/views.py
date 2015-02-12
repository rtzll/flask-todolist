# -*- coding: utf-8 -*-

from flask import jsonify, request, abort

from . import api
from ..models import User, Todo, TodoList


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


@api.route('/users/', methods=['POST'])
def add_user():
    try:
        user = User(username=request.json.get('username'),
                    email=request.json.get('email'),
                    password=request.json.get('password')).save()
    except:
        abort(400)
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


@api.route('/user/<username>/todolist/', methods=['POST'])
def add_user_todolist(username):
    try:
        user = User.query.filter_by(username=username).one()
        todolist = TodoList(title=request.json.get('title'),
                            creator=user.username).save()
    except:
        abort(400)
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
        todolist = TodoList(title=request.json.get('title')).save()
    except:
        abort(400)
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
    try:
        user = User.query.filter_by(username=username).one()
        todo = Todo(description=request.json.get('description'),
                    todolist_id=todolist_id, creator=username).save()
    except:
        abort(400)
    return jsonify({'todo': todo.to_json()}), 201


@api.route('/todolist/<int:todolist_id>/', methods=['POST'])
def add_todolist_todo(todolist_id):
    try:
        todo = Todo(description=request.json.get('description'),
                    todolist_id=todolist_id).save()
    except:
        abort(400)
    return jsonify({'todo': todo.to_json()}), 201
