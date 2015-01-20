# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash

from . import main
from .forms import TodoForm
from ..models import User, Todo, TodoList


@main.route('/')
def index():
    form = TodoForm()
    if form.validate_on_submit():
        return redirect(url_for('main.new_todolist'))
    flash('There seems to be something wrong with your todo.')
    return render_template('index.html', form=form)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    todos = user.todos.order_by(Todo.timestamp.desc())
    return render_template('user.html', user=user, todos=todos)


@main.route('/todolist/<int:id>', methods=['GET', 'POST'])
def todolist(id):
    todolist = TodoList.query.filter_by(id=id).first_or_404()
    form = TodoForm()
    if form.validate_on_submit():
        todo = Todo("generic description")
        todo.todolist_id = todolist.id
        todo.save()
        return redirect(url_for('main.todolist', id=id))
        flash('Todo added.')
    flash('There seems to be something wrong with your todo.')
    return render_template('todolist.html', todolist=todolist, form=form)


@main.route('/todolist/new', methods=['POST'])
def new_todolist():
    form = TodoForm(todo=request.form.get('todo'))
    # request.method == 'POST'
    if form.validate():
        todolist = TodoList("")
        todolist.save()
        todo = Todo("Read the docs")
        todo.todolist_id = todolist.id
        todo.save()
        return redirect(url_for('main.todolist', id=todolist.id))
    flash('There seems to be something wrong with your todo.')
    return redirect(url_for('main.index'))
