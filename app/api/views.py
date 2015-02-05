# -*- coding: utf-8 -*-

from flask import jsonify, request, abort

from . import api
from ..models import User, Todo, TodoList


@api.route('/user/')
def get_users():
    users = User.query.all()
    return jsonify({
        'users': [{'user': user.to_json()} for user in users]
    })


@api.route('/user/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'user': user.to_json()})


@api.route('/user/', methods=['POST'])
def add_user():
    try:
        user = User(username=request.json.get('username'),
                    email=request.json.get('email'),
                    password=request.json.get('password')).save()
    except:
        abort(400)
    return jsonify({'user': user.to_json()}), 201


@api.route('/user/<int:id>/todolists')
def get_user_todolists(id):
    user = User.query.get_or_404(id)
    todolists = user.todolists
    return jsonify({
        'todolists': [todolist.to_json() for todolist in todolists]
    })


@api.route('/user/<int:id>/todolists', methods=['POST'])
def add_user_todolists(id):
    try:
        todolist = TodoList(title=request.json.get('title'),
                            creator_id=id).save()
    except:
        abort(400)
    return jsonify({'todolist': todolist.to_json()}), 201


@api.route('/user/<int:user_id>/todolist/<int:todolist_id>')
def get_todolist_todos(todolist_id, user_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    return jsonify({
        'todos': [todo.to_json() for todo in todolist.todos]
    })


@api.route('/user/<int:user_id>/todolist/<int:todolist_id>', methods=['POST'])
def add_todo(user_id, todolist_id):
    try:
        todo = Todo(description=request.json.get('description'),
                    todolist_id=todolist_id, creator_id=user_id).save()
    except:
        abort(400)
    return jsonify({'todo': todo.to_json()}), 201
