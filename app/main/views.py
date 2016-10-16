# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

from app.main import main
from app.main.forms import TodoForm, TodoListForm
from app.models import Todo, TodoList


@main.route('/')
def index():
    form = TodoForm()
    if form.validate_on_submit():
        return redirect(url_for('main.new_todolist'))
    return render_template('index.html', form=form)


@main.route('/todolists/', methods=['GET', 'POST'])
@login_required
def todolist_overview():
    form = TodoListForm()
    if form.validate_on_submit():
        return redirect(url_for('main.add_todolist'))
    return render_template('overview.html', form=form)


def _get_user():
    return current_user.username if current_user.is_authenticated else None


@main.route('/todolist/<int:id>/', methods=['GET', 'POST'])
def todolist(id):
    todolist = TodoList.query.filter_by(id=id).first_or_404()
    form = TodoForm()
    if form.validate_on_submit():
        Todo(form.todo.data, todolist.id, _get_user()).save()
        return redirect(url_for('main.todolist', id=id))
    return render_template('todolist.html', todolist=todolist, form=form)


@main.route('/todolist/new/', methods=['POST'])
def new_todolist():
    form = TodoForm(todo=request.form.get('todo'))
    if form.validate():
        todolist = TodoList(creator=_get_user()).save()
        Todo(form.todo.data, todolist.id).save()
        return redirect(url_for('main.todolist', id=todolist.id))
    return redirect(url_for('main.index'))


@main.route('/todolist/add/', methods=['POST'])
def add_todolist():
    form = TodoListForm(todo=request.form.get('title'))
    if form.validate():
        todolist = TodoList(form.title.data, _get_user()).save()
        return redirect(url_for('main.todolist', id=todolist.id))
    return redirect(url_for('main.index'))
