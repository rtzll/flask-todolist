# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, flash

from . import main
from .forms import TodoForm
from ..models import User


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    todos = user.todos.order_by(Todo.timestamp.desc())
    return render_template('user.html', user=user, todos=todos)


@main.route('/todo', methods=['GET', 'POST'])
def todo():
    form = TodoForm()
    if form.validate_on_submit():
        return redirect(url_for('main.todo'))
        flash('Todo added.')
    return render_template('todo.html', form=form)
