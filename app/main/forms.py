# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length


class TodoForm(Form):
    todo = StringField(
        'Enter your todo', validators=[Required(), Length(1, 128)]
    )
    submit = SubmitField('Submit')


class TodoListForm(Form):
    title = StringField(
        'Enter your todolist title', validators=[Required(), Length(1, 128)]
    )
    submit = SubmitField('Submit')
