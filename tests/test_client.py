from app.models import User


USERNAME_ALICE = "alice"
PASSWORD = "correcthorsebatterystaple"


def assert_redirect(response, location):
    assert response.status_code == 302
    assert response.headers["Location"].endswith(location)


def register_user(client, url_for, name):
    return client.post(
        url_for("auth.register"),
        data={
            "username": name,
            "email": name + "@example.com",
            "password": PASSWORD,
            "password_confirmation": PASSWORD,
        },
    )


def login_user(client, url_for, name):
    return client.post(
        url_for("auth.login"),
        data={
            "email_or_username": name + "@example.com",
            "password": PASSWORD,
        },
    )


def register_and_login(client, url_for, name):
    response = register_user(client, url_for, name)
    assert_redirect(response, "/auth/login")
    response = login_user(client, url_for, name)
    assert_redirect(response, "/")


def test_home_page(client, url_for, templates):
    response = client.get(url_for("main.index"))
    assert response.status_code == 200
    assert "index.html" in templates


def test_register_page(client, url_for, templates):
    response = client.get(url_for("auth.register"))
    assert response.status_code == 200
    assert "register.html" in templates


def test_login_page(client, url_for, templates):
    response = client.get(url_for("auth.login"))
    assert response.status_code == 200
    assert "login.html" in templates


def test_overview_page(client, url_for, templates):
    register_and_login(client, url_for, USERNAME_ALICE)
    response = client.get(url_for("main.todolist_overview"))
    assert response.status_code == 200
    assert "overview.html" in templates


def test_last_seen_update_after_login(client, url_for):
    register_user(client, url_for, USERNAME_ALICE)
    user = User.query.filter_by(username=USERNAME_ALICE).first()
    before = user.last_seen
    login_user(client, url_for, USERNAME_ALICE)
    after = user.last_seen
    assert before != after


def test_register_and_login_and_logout(client, url_for, templates):
    response = register_user(client, url_for, USERNAME_ALICE)
    assert_redirect(response, "/auth/login")

    response = login_user(client, url_for, USERNAME_ALICE)
    assert_redirect(response, "/")

    response = client.get(url_for("auth.logout"), follow_redirects=True)
    assert response.status_code == 200
    assert "index.html" in templates


def test_empty_todo_stays_on_todolist_view(client, url_for, templates):
    register_and_login(client, url_for, USERNAME_ALICE)
    response = client.post(
        url_for("main.new_todolist"),
        data={"todo": "initial todo"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "todolist.html" in templates

    response = client.post(
        url_for("main.todolist", id=1),
        data={"todo": ""},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "todolist.html" in templates
    assert b"Todos should neither be empty nor be longer than 128 characters." in response.data
