from flask import redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_by_email = User.query.filter_by(email=form.email_or_username.data).first()
        user_by_name = User.query.filter_by(
            username=form.email_or_username.data
        ).first()
        if user_by_email is not None and user_by_email.verify_password(
            form.password.data
        ):
            login_user(user_by_email.seen())
            return redirect(request.args.get("next") or url_for("main.index"))
        if user_by_name is not None and user_by_name.verify_password(
            form.password.data
        ):
            login_user(user_by_name.seen())
            return redirect(request.args.get("next") or url_for("main.index"))
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
