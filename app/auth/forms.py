# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    email_or_username = StringField(
        'Email or Username', validators=[Required(), Length(1, 64)]
    )
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField(
        'Email', validators=[Required(), Length(1, 64), Email()]
    )
    username = StringField(
        'Username',
        validators=[
            Required(), Length(1, 64),
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                   'Usernames must have only letters, '
                   'numbers, dots or underscores')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            Required(),
            EqualTo('password_confirmation', message='Passwords must match.')
        ]
    )
    password_confirmation = PasswordField(
        'Confirm password', validators=[Required()]
    )
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
