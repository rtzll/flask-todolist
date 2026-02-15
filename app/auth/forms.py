from flask_wtf import FlaskForm
from sqlalchemy import select
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import Email, EqualTo, InputRequired, Length, Regexp

from app import db
from app.models import User


class LoginForm(FlaskForm):
    email_or_username = StringField(
        "Email or Username", validators=[InputRequired(), Length(1, 64)]
    )
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Length(1, 64), Email()])
    username = StringField(
        "Username",
        validators=[
            InputRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or underscores",
            ),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            EqualTo("password_confirmation", message="Passwords must match."),
        ],
    )
    password_confirmation = PasswordField(
        "Confirm password", validators=[InputRequired()]
    )
    submit = SubmitField("Register")

    def validate_email(self, field):
        if db.session.execute(
            select(User).filter_by(email=field.data)
        ).scalar_one_or_none():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if db.session.execute(
            select(User).filter_by(username=field.data)
        ).scalar_one_or_none():
            raise ValidationError("Username already in use.")
