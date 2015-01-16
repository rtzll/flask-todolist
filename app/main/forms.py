# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class TodoForm(Form):
    todo = StringField('Enter your todo', validators=[Required()])
    submit = SubmitField('Submit')
