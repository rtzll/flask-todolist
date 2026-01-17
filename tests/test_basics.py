from flask import current_app

from app import db
from app.models import Todo, TodoList, User


USERNAME_ADAM = "adam"
SHOPPING_LIST_TITLE = "shopping list"
READ_TODO_DESCRIPTION = "Read a book about TDD"


def add_user(username):
    user_data = {
        "email": username + "@example.com",
        "username": username,
        "password": "correcthorsebatterystaple",
    }
    user = User.from_dict(user_data)
    return User.query.filter_by(username=user.username).first()


def add_todo(description, user, todolist_id=None):
    todo_data = {
        "description": description,
        "todolist_id": todolist_id or TodoList().save().id,
        "creator": user.username,
    }
    read_todo = Todo.from_dict(todo_data)
    return Todo.query.filter_by(id=read_todo.id).first()


def test_app_exists(app):
    assert current_app is not None


def test_app_is_testing(app):
    assert current_app.config["TESTING"]


def test_password_setter(app):
    u = User(password="correcthorsebatterystaple")
    assert u.password_hash is not None


def test_no_password_getter(app):
    u = User(password="correcthorsebatterystaple")
    try:
        _ = u.password
    except AttributeError:
        return
    assert False, "password should not be readable"


def test_password_verification(app):
    u = User(password="correcthorsebatterystaple")
    assert u.verify_password("correcthorsebatterystaple")
    assert not u.verify_password("incorrecthorsebatterystaple")


def test_password_salts_are_random(app):
    u = User(password="correcthorsebatterystaple")
    u2 = User(password="correcthorsebatterystaple")
    assert u.password_hash != u2.password_hash


def test_adding_new_user(app):
    new_user = add_user(USERNAME_ADAM)
    assert new_user.username == USERNAME_ADAM
    assert new_user.email == USERNAME_ADAM + "@example.com"


def test_adding_new_todo_without_user(app):
    todo = Todo(
        description=READ_TODO_DESCRIPTION, todolist_id=TodoList().save().id
    ).save()
    todo_from_db = Todo.query.filter_by(id=todo.id).first()

    assert todo_from_db.description == READ_TODO_DESCRIPTION
    assert todo_from_db.creator is None


def test_adding_new_todo_with_user(app):
    some_user = add_user(USERNAME_ADAM)
    new_todo = add_todo(READ_TODO_DESCRIPTION, some_user)
    assert new_todo.description == READ_TODO_DESCRIPTION
    assert new_todo.creator == some_user.username


def test_closing_todo(app):
    some_user = add_user(USERNAME_ADAM)
    new_todo = add_todo(READ_TODO_DESCRIPTION, some_user)
    assert not new_todo.is_finished
    new_todo.finished()
    assert new_todo.is_finished
    assert new_todo.description == READ_TODO_DESCRIPTION
    assert new_todo.creator == some_user.username


def test_reopen_closed_todo(app):
    some_user = add_user(USERNAME_ADAM)
    new_todo = add_todo(READ_TODO_DESCRIPTION, some_user)
    assert not new_todo.is_finished
    new_todo.finished()
    assert new_todo.is_finished
    new_todo.reopen()
    assert not new_todo.is_finished
    assert new_todo.description == READ_TODO_DESCRIPTION
    assert new_todo.creator == some_user.username


def test_adding_two_todos_with_the_same_description(app):
    some_user = add_user(USERNAME_ADAM)
    first_todo = add_todo(READ_TODO_DESCRIPTION, some_user)
    second_todo = add_todo(READ_TODO_DESCRIPTION, some_user)

    assert first_todo.description == second_todo.description
    assert first_todo.creator == second_todo.creator
    assert first_todo.id != second_todo.id


def test_adding_new_todolist_without_user(app):
    todolist = TodoList(SHOPPING_LIST_TITLE).save()
    todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

    assert todolist_from_db.title == SHOPPING_LIST_TITLE
    assert todolist_from_db.creator is None


def test_adding_new_todolist_with_user(app):
    user = add_user(USERNAME_ADAM)
    todolist = TodoList(title=SHOPPING_LIST_TITLE, creator=user.username).save()
    todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

    assert todolist_from_db.title == SHOPPING_LIST_TITLE
    assert todolist_from_db.creator == user.username


def test_adding_two_todolists_with_the_same_title(app):
    user = add_user(USERNAME_ADAM)
    first = TodoList(title=SHOPPING_LIST_TITLE, creator=user.username).save()
    first_todolist = TodoList.query.filter_by(id=first.id).first()
    second = TodoList(title=SHOPPING_LIST_TITLE, creator=user.username).save()
    second_todolist = TodoList.query.filter_by(id=second.id).first()

    assert first_todolist.title == second_todolist.title
    assert first_todolist.creator == second_todolist.creator
    assert first_todolist.id != second_todolist.id


def test_adding_todo_to_todolist(app):
    user = add_user(USERNAME_ADAM)
    todolist = TodoList(title=SHOPPING_LIST_TITLE, creator=user.username).save()
    todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

    todo_description = "A book about TDD"
    todo = add_todo(todo_description, user, todolist_from_db.id)

    assert todolist_from_db.todo_count == 1
    assert todolist.title == SHOPPING_LIST_TITLE
    assert todolist.creator == user.username
    assert todo.todolist_id == todolist_from_db.id
    assert todolist.todos.first() == todo


def test_counting_todos_of_todolist(app):
    user = add_user(USERNAME_ADAM)
    todolist = TodoList(title=SHOPPING_LIST_TITLE, creator=user.username).save()
    todolist_from_db = TodoList.query.filter_by(id=todolist.id).first()

    todo_description = "A book about TDD"
    todo = add_todo(todo_description, user, todolist_from_db.id)

    assert todolist.title == SHOPPING_LIST_TITLE
    assert todolist.creator == user.username
    assert todo.todolist_id == todolist_from_db.id
    assert todolist.todos.first() == todo

    assert todolist_from_db.finished_count == 0
    assert todolist_from_db.open_count == 1

    todo.finished()

    assert todolist_from_db.finished_count == 1
    assert todolist_from_db.open_count == 0


def test_delete_user(app):
    user = add_user(USERNAME_ADAM)
    user_id = user.id
    user.delete()
    assert db.session.get(User, user_id) is None


def test_delete_todolist(app):
    todolist = TodoList(SHOPPING_LIST_TITLE).save()
    todolist_id = todolist.id
    todolist.delete()
    assert db.session.get(TodoList, todolist_id) is None


def test_delete_todo(app):
    todolist = TodoList(SHOPPING_LIST_TITLE).save()
    todo = Todo("A book about TDD", todolist.id).save()
    assert todolist.todo_count == 1
    todo_id = todo.id
    todo.delete()
    assert db.session.get(Todo, todo_id) is None
    assert todolist.todo_count == 0
