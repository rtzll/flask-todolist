# pyright: reportOptionalMemberAccess=false

import json

from app import db
from app.models import Todo, TodoList, User


USERNAME_ALICE = "alice"
PASSWORD = "correcthorsebatterystaple"


def setup_new_user(username: str) -> dict[str, str | bool]:
    return {
        "username": username,
        "email": username + "@example.com",
        "password": PASSWORD,
    }


def get_headers():
    return {"Accept": "application/json", "Content-Type": "application/json"}


def add_user(username):
    user_data = setup_new_user(username)
    User.from_dict(user_data)
    return User.query.filter_by(username=username).first()


def add_todolist(title, username=None):
    todolist = TodoList(title=title, creator=username).save()
    return TodoList.query.filter_by(id=todolist.id).first()


def add_todo(description, todolist_id, username=None):
    todolist = TodoList.query.filter_by(id=todolist_id).first()
    todo = Todo(
        description=description, todolist_id=todolist.id, creator=username
    ).save()
    return Todo.query.filter_by(id=todo.id).first()


def add_user_through_json_post(client, url_for, username):
    user_data = setup_new_user(username)
    return client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )


def create_admin():
    new_user = setup_new_user("admin")
    new_user["is_admin"] = True
    return User.from_dict(new_user)


def create_admin_user():
    return User(
        username="admin",
        email="admin@example.com",
        password=PASSWORD,
        is_admin=True,
    ).save()


def login_user(client, url_for, username):
    return client.post(
        url_for("auth.login"),
        data={"email_or_username": username, "password": PASSWORD},
    )


def assert_404_response(response):
    assert response.status_code == 404
    json_response = json.loads(response.data.decode("utf-8"))
    assert json_response["error"] == "Not found"


def assert_400_response(response):
    assert response.status_code == 400
    json_response = json.loads(response.data.decode("utf-8"))
    assert json_response["error"] == "Bad Request"


def test_main_route(client, url_for):
    response = client.get(url_for("api.get_routes"))
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    assert "users" in json_response
    assert "todolists" in json_response


def test_not_found(client):
    response = client.get("/api/not/found")
    assert_404_response(response)


def test_add_user(client, url_for):
    post_response = add_user_through_json_post(client, url_for, USERNAME_ALICE)
    assert post_response.headers["Content-Type"] == "application/json"
    assert post_response.status_code == 201

    response = client.get(url_for("api.get_users"))
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    users = json_response["users"]
    assert users[0]["username"] == USERNAME_ALICE


def test_add_user_with_duplicate_username_returns_400(client, url_for):
    add_user_through_json_post(client, url_for, USERNAME_ALICE)
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(
            {
                "username": USERNAME_ALICE,
                "email": "another@example.com",
                "password": PASSWORD,
            }
        ),
    )
    assert_400_response(response)


def test_add_user_with_duplicate_email_returns_400(client, url_for):
    add_user_through_json_post(client, url_for, USERNAME_ALICE)
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(
            {
                "username": "another_user",
                "email": USERNAME_ALICE + "@example.com",
                "password": PASSWORD,
            }
        ),
    )
    assert_400_response(response)


def test_add_user_only_using_the_username(client, url_for):
    user_data = {"username": USERNAME_ALICE}
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )
    assert_400_response(response)


def test_add_user_only_using_the_username_and_email(client, url_for):
    user_data = {
        "username": USERNAME_ALICE,
        "email": USERNAME_ALICE + "@example.com",
    }
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )
    assert_400_response(response)


def test_add_user_with_to_long_username(client, url_for):
    user_data = {
        "username": 65 * "a",
        "email": USERNAME_ALICE + "@example.com",
        "password": PASSWORD,
    }
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )
    assert_400_response(response)


def test_add_user_with_invalid_username(client, url_for):
    user_data = {
        "username": "not a valid username",
        "email": USERNAME_ALICE + "@example.com",
        "password": PASSWORD,
    }
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )
    assert_400_response(response)


def test_add_user_without_username(client, url_for):
    user_data = {
        "username": "",
        "email": USERNAME_ALICE + "@example.com",
        "password": PASSWORD,
    }
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )
    assert_400_response(response)


def test_add_user_with_invalid_email(client, url_for):
    user_data = {
        "username": USERNAME_ALICE,
        "email": USERNAME_ALICE + "example.com",
        "password": PASSWORD,
    }
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )
    assert_400_response(response)


def test_add_user_withoout_email(client, url_for):
    user_data = {
        "username": USERNAME_ALICE,
        "email": "",
        "password": PASSWORD,
    }
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )
    assert_400_response(response)


def test_add_user_with_too_long_email(client, url_for):
    user_data = {
        "username": USERNAME_ALICE,
        "email": 53 * "a" + "@example.com",
        "password": PASSWORD,
    }
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )
    assert_400_response(response)


def test_add_user_without_password(client, url_for):
    user_data = {
        "username": USERNAME_ALICE,
        "email": USERNAME_ALICE + "@example.com",
        "password": "",
    }
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )
    assert_400_response(response)


def test_add_user_with_extra_fields(client, url_for):
    user_data = {
        "username": USERNAME_ALICE,
        "email": USERNAME_ALICE + "@example.com",
        "password": PASSWORD,
        "extra-field": "will be ignored",
    }
    post_response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )
    assert post_response.headers["Content-Type"] == "application/json"
    assert post_response.status_code == 201

    response = client.get(url_for("api.get_users"))
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    assert json_response["users"][0]["username"] == USERNAME_ALICE


def test_add_user_only_using_the_username_and_password(client, url_for):
    user_data = {
        "username": USERNAME_ALICE,
        "password": PASSWORD,
    }
    response = client.post(
        url_for("api.add_user"),
        headers=get_headers(),
        data=json.dumps(user_data),
    )
    assert_400_response(response)


def test_add_todolist(client, url_for):
    post_response = client.post(
        url_for("api.add_todolist"),
        headers=get_headers(),
        data=json.dumps({"title": "todolist"}),
    )
    assert post_response.status_code == 201

    response = client.get(url_for("api.get_todolist", todolist_id=1))
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    assert json_response["title"] == "todolist"


def test_add_todolist_without_title(client, url_for):
    response = client.post(url_for("api.add_todolist"), headers=get_headers())
    assert_400_response(response)


def test_add_todolist_with_too_long_title(client, url_for):
    response = client.post(
        url_for("api.add_todolist"),
        headers=get_headers(),
        data=json.dumps({"title": 129 * "t"}),
    )
    assert_400_response(response)


def test_add_user_todolist(client, url_for):
    add_user(USERNAME_ALICE)
    post_response = client.post(
        url_for("api.add_user_todolist", username=USERNAME_ALICE),
        headers=get_headers(),
        data=json.dumps({"title": "todolist"}),
    )
    assert post_response.status_code == 201

    response = client.get(url_for("api.get_user_todolists", username=USERNAME_ALICE))
    assert response.status_code == 200
    json_response = json.loads(response.data.decode("utf-8"))

    todolists = json_response["todolists"]
    assert todolists[0]["title"] == "todolist"
    assert todolists[0]["creator"] == USERNAME_ALICE
    assert len(todolists) == 1


def test_add_user_todolist_when_user_does_not_exist(client, url_for):
    post_response = client.post(
        url_for("api.add_user_todolist", username=USERNAME_ALICE),
        headers=get_headers(),
        data=json.dumps({"title": "todolist"}),
    )
    assert_404_response(post_response)


def test_add_user_todolist_todo(client, url_for):
    todolist_title = "new todolist"
    add_user(USERNAME_ALICE)
    new_todolist = add_todolist(todolist_title, USERNAME_ALICE)

    post_response = client.post(
        url_for(
            "api.add_user_todolist_todo",
            username=USERNAME_ALICE,
            todolist_id=new_todolist.id,
        ),
        headers=get_headers(),
        data=json.dumps(
            {
                "description": "new todo",
                "creator": USERNAME_ALICE,
                "todolist_id": new_todolist.id,
            }
        ),
    )
    assert post_response.status_code == 201

    response = client.get(
        url_for(
            "api.get_user_todolist_todos",
            username=USERNAME_ALICE,
            todolist_id=new_todolist.id,
        )
    )
    assert response.status_code == 200
    json_response = json.loads(response.data.decode("utf-8"))

    todos = json_response["todos"]
    assert todos[0]["description"] == "new todo"
    assert todos[0]["creator"] == USERNAME_ALICE
    assert len(todos) == 1


def test_add_user_todolist_todo_rejects_other_users_todolist(client, url_for):
    add_user(USERNAME_ALICE)
    add_user("bob")
    bobs_todolist = add_todolist("bob list", "bob")

    post_response = client.post(
        url_for(
            "api.add_user_todolist_todo",
            username=USERNAME_ALICE,
            todolist_id=bobs_todolist.id,
        ),
        headers=get_headers(),
        data=json.dumps({"description": "should fail"}),
    )
    assert_404_response(post_response)

    response = client.get(
        url_for(
            "api.get_user_todolist_todos",
            username="bob",
            todolist_id=bobs_todolist.id,
        )
    )
    assert response.status_code == 200
    assert json.loads(response.data.decode("utf-8"))["todos"] == []


def test_add_user_todolist_todo_when_todolist_does_not_exist(client, url_for):
    add_user(USERNAME_ALICE)
    post_response = client.post(
        url_for(
            "api.add_user_todolist_todo",
            username=USERNAME_ALICE,
            todolist_id=1,
        ),
        headers=get_headers(),
        data=json.dumps(
            {
                "description": "new todo",
                "creator": USERNAME_ALICE,
                "todolist_id": 1,
            }
        ),
    )
    assert_404_response(post_response)


def test_add_user_todolist_todo_without_todo_data(client, url_for):
    todolist_title = "new todolist"
    add_user(USERNAME_ALICE)
    new_todolist = add_todolist(todolist_title, USERNAME_ALICE)

    post_response = client.post(
        url_for(
            "api.add_user_todolist_todo",
            username=USERNAME_ALICE,
            todolist_id=new_todolist.id,
        ),
        headers=get_headers(),
    )
    assert_400_response(post_response)


def test_add_todolist_todo(client, url_for):
    new_todolist = TodoList().save()

    post_response = client.post(
        url_for("api.add_todolist_todo", todolist_id=new_todolist.id),
        headers=get_headers(),
        data=json.dumps(
            {
                "description": "new todo",
                "creator": "null",
                "todolist_id": new_todolist.id,
            }
        ),
    )
    assert post_response.status_code == 201
    response = client.get(
        url_for("api.get_todolist_todos", todolist_id=new_todolist.id)
    )
    assert response.status_code == 200
    json_response = json.loads(response.data.decode("utf-8"))

    todos = json_response["todos"]
    assert todos[0]["description"] == "new todo"
    assert todos[0]["creator"] is None
    assert len(todos) == 1


def test_add_todolist_todo_when_todolist_does_not_exist(client, url_for):
    post_response = client.post(
        url_for("api.add_todolist_todo", todolist_id=1),
        headers=get_headers(),
        data=json.dumps(
            {"description": "new todo", "creator": "null", "todolist_id": 1}
        ),
    )
    assert_404_response(post_response)


def test_add_todolist_todo_without_todo_data(client, url_for):
    new_todolist = TodoList().save()
    post_response = client.post(
        url_for("api.add_todolist_todo", todolist_id=new_todolist.id),
        headers=get_headers(),
    )
    assert_400_response(post_response)


def test_get_users(client, url_for):
    add_user(USERNAME_ALICE)
    response = client.get(url_for("api.get_users"))
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    assert json_response["users"][0]["username"] == USERNAME_ALICE


def test_get_users_when_no_users_exist(client, url_for):
    response = client.get(url_for("api.get_users"))
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    assert json_response["users"] == []


def test_get_user(client, url_for):
    add_user(USERNAME_ALICE)
    response = client.get(url_for("api.get_user", username=USERNAME_ALICE))
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    assert json_response["username"] == USERNAME_ALICE


def test_get_user_when_user_does_not_exist(client, url_for):
    response = client.get(url_for("api.get_user", username=USERNAME_ALICE))
    assert_404_response(response)


def test_get_todolists(client, url_for):
    todolist_title = "new todolist "
    add_user(USERNAME_ALICE)
    add_todolist(todolist_title + "1", USERNAME_ALICE)
    add_todolist(todolist_title + "2", USERNAME_ALICE)

    response = client.get(url_for("api.get_todolists"))
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    todolists = json_response["todolists"]
    assert todolists[0]["title"] == "new todolist 1"
    assert todolists[0]["creator"] == USERNAME_ALICE
    assert todolists[1]["title"] == "new todolist 2"
    assert todolists[1]["creator"] == USERNAME_ALICE
    assert len(todolists) == 2


def test_get_todolists_when_no_todolists_exist(client, url_for):
    response = client.get(url_for("api.get_todolists"))
    assert response.status_code == 200

    todolists = json.loads(response.data.decode("utf-8"))["todolists"]
    assert todolists == []


def test_get_user_todolists(client, url_for):
    todolist_title = "new todolist "
    add_user(USERNAME_ALICE)
    add_todolist(todolist_title + "1", USERNAME_ALICE)
    add_todolist(todolist_title + "2", USERNAME_ALICE)

    response = client.get(url_for("api.get_user_todolists", username=USERNAME_ALICE))
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    todolists = json_response["todolists"]

    assert todolists[0]["title"] == "new todolist 1"
    assert todolists[0]["creator"] == USERNAME_ALICE
    assert todolists[1]["title"] == "new todolist 2"
    assert todolists[1]["creator"] == USERNAME_ALICE
    assert len(todolists) == 2


def test_get_user_todolists_when_user_does_not_exist(client, url_for):
    response = client.get(url_for("api.get_user_todolists", username=USERNAME_ALICE))
    assert_404_response(response)


def test_get_user_todolists_when_user_has_no_todolists(client, url_for):
    add_user(USERNAME_ALICE)
    response = client.get(url_for("api.get_user_todolists", username=USERNAME_ALICE))
    assert response.status_code == 200

    todolists = json.loads(response.data.decode("utf-8"))["todolists"]
    assert todolists == []


def test_get_todolist_todos(client, url_for):
    todolist_title = "new todolist"
    new_todolist = add_todolist(todolist_title)

    add_todo("first", new_todolist.id)
    add_todo("second", new_todolist.id)

    response = client.get(
        url_for("api.get_todolist_todos", todolist_id=new_todolist.id)
    )
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    todos = json_response["todos"]
    assert todos[0]["description"] == "first"
    assert todos[0]["creator"] is None
    assert todos[1]["description"] == "second"
    assert todos[1]["creator"] is None
    assert len(todos) == 2


def test_get_todolist_todos_when_todolist_does_not_exist(client, url_for):
    response = client.get(url_for("api.get_todolist_todos", todolist_id=1))
    assert_404_response(response)


def test_get_todolist_todos_when_todolist_has_no_todos(client, url_for):
    todolist_title = "new todolist"
    new_todolist = add_todolist(todolist_title)
    response = client.get(
        url_for("api.get_todolist_todos", todolist_id=new_todolist.id)
    )
    assert response.status_code == 200

    todos = json.loads(response.data.decode("utf-8"))["todos"]
    assert todos == []


def test_get_user_todolist_todos(client, url_for):
    todolist_title = "new todolist"
    add_user(USERNAME_ALICE)
    new_todolist = add_todolist(todolist_title, USERNAME_ALICE)

    add_todo("first", new_todolist.id, USERNAME_ALICE)
    add_todo("second", new_todolist.id, USERNAME_ALICE)

    response = client.get(
        url_for(
            "api.get_user_todolist_todos",
            username=USERNAME_ALICE,
            todolist_id=new_todolist.id,
        )
    )
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    todos = json_response["todos"]
    assert todos[0]["description"] == "first"
    assert todos[0]["creator"] == USERNAME_ALICE
    assert todos[1]["description"] == "second"
    assert todos[1]["creator"] == USERNAME_ALICE
    assert len(todos) == 2


def test_get_user_todolist_todos_when_user_does_not_exist(client, url_for):
    response = client.get(
        url_for(
            "api.get_user_todolist_todos",
            username=USERNAME_ALICE,
            todolist_id=1,
        )
    )
    assert_404_response(response)


def test_get_user_todolist_todos_when_todolist_does_not_exist(client, url_for):
    add_user(USERNAME_ALICE)

    response = client.get(
        url_for(
            "api.get_user_todolist_todos",
            username=USERNAME_ALICE,
            todolist_id=1,
        )
    )
    assert_404_response(response)


def test_get_user_todolist_todos_when_todolist_has_no_todos(client, url_for):
    todolist_title = "new todolist"
    add_user(USERNAME_ALICE)
    new_todolist = add_todolist(todolist_title, USERNAME_ALICE)

    response = client.get(
        url_for(
            "api.get_user_todolist_todos",
            username=USERNAME_ALICE,
            todolist_id=new_todolist.id,
        )
    )
    assert response.status_code == 200

    todos = json.loads(response.data.decode("utf-8"))["todos"]
    assert todos == []


def test_get_different_user_todolist_todos(client, url_for):
    first_username = USERNAME_ALICE
    second_username = "bob"
    todolist_title = "new todolist"
    first_user = add_user(first_username)
    add_user(second_username)
    new_todolist = add_todolist(todolist_title, second_username)

    add_todo("first", new_todolist.id, second_username)
    add_todo("second", new_todolist.id, second_username)

    response = client.get(
        url_for(
            "api.get_user_todolist_todos",
            username=first_user.username,
            todolist_id=new_todolist.id,
        )
    )
    assert_404_response(response)


def test_get_user_todolist(client, url_for):
    todolist_title = "new todolist"
    add_user(USERNAME_ALICE)
    new_todolist = add_todolist(todolist_title, USERNAME_ALICE)

    response = client.get(
        url_for(
            "api.get_user_todolist",
            username=USERNAME_ALICE,
            todolist_id=new_todolist.id,
        )
    )
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    assert json_response["title"] == todolist_title
    assert json_response["creator"] == USERNAME_ALICE


def test_get_user_todolist_when_user_does_not_exist(client, url_for):
    response = client.get(
        url_for("api.get_user_todolist", username=USERNAME_ALICE, todolist_id=1)
    )
    assert_404_response(response)


def test_get_user_todolist_when_todolist_does_not_exist(client, url_for):
    add_user(USERNAME_ALICE)
    response = client.get(
        url_for("api.get_user_todolist", username=USERNAME_ALICE, todolist_id=1)
    )
    assert_404_response(response)


def test_update_todo_status_to_finished(client, url_for):
    todolist = add_todolist("new todolist")
    todo = add_todo("first", todolist.id)
    assert not todo.is_finished

    client.put(
        url_for("api.update_todo_status", todo_id=todo.id),
        headers=get_headers(),
        data=json.dumps({"is_finished": True}),
    )

    todo = db.session.get(Todo, todo.id)
    assert todo.is_finished


def test_update_todo_status_to_open(client, url_for):
    todolist = add_todolist("new todolist")
    todo = add_todo("first", todolist.id)
    todo.finished()
    assert todo.is_finished

    client.put(
        url_for("api.update_todo_status", todo_id=todo.id),
        headers=get_headers(),
        data=json.dumps({"is_finished": False}),
    )
    todo = db.session.get(Todo, todo.id)
    assert not todo.is_finished
    assert todo.finished_at is None


def test_change_todolist_title(client, url_for):
    todolist = add_todolist("new todolist")

    response = client.put(
        url_for("api.change_todolist_title", todolist_id=todolist.id),
        headers=get_headers(),
        data=json.dumps({"title": "changed title"}),
    )
    assert response.status_code == 200

    json_response = json.loads(response.data.decode("utf-8"))
    assert json_response["title"] == "changed title"


def test_change_todolist_title_too_long_title(client, url_for):
    todolist = add_todolist("new todolist")

    response = client.put(
        url_for("api.change_todolist_title", todolist_id=todolist.id),
        headers=get_headers(),
        data=json.dumps({"title": 129 * "t"}),
    )
    assert response.status_code == 400


def test_change_todolist_title_empty_title(client, url_for):
    todolist = add_todolist("new todolist")

    response = client.put(
        url_for("api.change_todolist_title", todolist_id=todolist.id),
        headers=get_headers(),
        data=json.dumps({"title": ""}),
    )
    assert response.status_code == 400


def test_change_todolist_title_without_title(client, url_for):
    todolist = add_todolist("new todolist")

    response = client.put(
        url_for("api.change_todolist_title", todolist_id=todolist.id),
        headers=get_headers(),
    )
    assert response.status_code == 400


def test_delete_user(client, url_for):
    admin = create_admin_user()
    login_user(client, url_for, admin.username)

    user = add_user(USERNAME_ALICE)

    response = client.delete(
        url_for("api.delete_user", username=user.username),
        headers=get_headers(),
        data=json.dumps({"username": user.username}),
    )
    assert response.status_code == 200
    assert db.session.get(User, user.id) is None


def test_delete_todolist(client, url_for):
    admin = create_admin_user()
    login_user(client, url_for, admin.username)

    todolist = add_todolist("new todolist")
    response = client.delete(
        url_for("api.delete_todolist", todolist_id=todolist.id),
        headers=get_headers(),
        data=json.dumps({"todolist_id": todolist.id}),
    )
    assert response.status_code == 200
    assert db.session.get(TodoList, todolist.id) is None


def test_delete_todo(client, url_for):
    admin = create_admin_user()
    login_user(client, url_for, admin.username)

    todolist = add_todolist("new todolist")
    todo = add_todo("new todo", todolist.id)
    response = client.delete(
        url_for("api.delete_todo", todo_id=todo.id),
        headers=get_headers(),
        data=json.dumps({"todo_id": todo.id}),
    )
    assert response.status_code == 200
    assert db.session.get(Todo, todo.id) is None
