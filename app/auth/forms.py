from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import Email, EqualTo, Length, Regexp, InputRequired

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
                "Usernames must have only letters, " "numbers, dots or underscores",
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
    password_confirmation = PasswordField("Confirm password", validators=[InputRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")
