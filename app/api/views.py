# -*- coding: utf-8 -*-

from flask import jsonify, request, current_app, url_for, make_response, abort

from . import api
from ..models import User, TodoList


@api.route('/user/')
def get_users():
    users = User.query.all()
    return jsonify({
        'users' : [{'user': user.to_json()} for user in users]
    })


@api.route('/user/', methods=['POST'])
def add_user():
    try:
        user = User(request.json.get('username'), request.json.get('email'),
                    request.json.get('password')).save()
    except:
        abort(400)
    return jsonify({'user' : user.to_json()}, 201)


@api.route('/user/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'user' : user.to_json()})


@api.route('/user/<int:id>/todolists')
def get_user_todolists(id):
    user = User.query.get_or_404(id)
    todolists = user.todolists
    return jsonify({
        'todolists': [todolist.to_json() for todolist in todolists]
    })


@api.route('/user/<int:user_id>/todolist/<int:todolist_id>')
def get_todolist_todos(todolist_id, user_id):
    todolist = TodoList.query.get_or_404(todolist_id)
    return jsonify({
        'todos': [todo.to_json() for todo in todolist.todos]
    })


@api.app_errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@api.app_errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': 'Unauthorized'}), 401)

@api.app_errorhandler(403)
def forbidden(error):
    return make_response(jsonify({'error': 'Forbidden'}), 403)

@api.app_errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
