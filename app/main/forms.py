from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Required


class TodoForm(FlaskForm):
    todo = StringField("Enter your todo", validators=[Required(), Length(1, 128)])
    submit = SubmitField("Submit")


class TodoListForm(FlaskForm):
    title = StringField(
        "Enter your todolist title", validators=[Required(), Length(1, 128)]
    )
    submit = SubmitField("Submit")
