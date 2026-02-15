from urllib.parse import urljoin, urlsplit

from flask import redirect, render_template, request, url_for
from flask_login import login_user, logout_user
from sqlalchemy import select

from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


def _get_safe_redirect_target():
    next_url = request.args.get("next")
    if not next_url:
        return url_for("main.index")

    host_url = urlsplit(request.host_url)
    redirect_url = urlsplit(urljoin(request.host_url, next_url))
    if (
        redirect_url.scheme in {"http", "https"}
        and redirect_url.netloc == host_url.netloc
    ):
        return next_url
    return url_for("main.index")


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        if password is None:
            return render_template("login.html", form=form)
        user_by_email = db.session.execute(
            select(User).filter_by(email=form.email_or_username.data)
        ).scalar_one_or_none()
        user_by_name = db.session.execute(
            select(User).filter_by(username=form.email_or_username.data)
        ).scalar_one_or_none()
        if user_by_email is not None and user_by_email.verify_password(password):
            login_user(user_by_email.seen())
            return redirect(_get_safe_redirect_target())
        if user_by_name is not None and user_by_name.verify_password(password):
            login_user(user_by_name.seen())
            return redirect(_get_safe_redirect_target())
    return render_template("login.html", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
        ).save()
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)
