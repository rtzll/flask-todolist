flask-todolist
=======================
This is a side project in which I'm exploring Flask and some of it's great
extensions by building a smallish web app with some of the most basic features.

### Explore
To try out the app yourself install the requirements.
```
pip install requirements.txt
```
And than start the server(default: http://localhost:5000)
```
python manage.py runserver
```

#### Structure
Usage               | Flask-Extension  
------------------- | -----------------------
Model & Database    | (Flask-)SQLAlchemy
Forms               | Flask-WTF
Login               | Flask-Login
Database Migrations | Flask-Migrate & Alembic

*Note*: I'm somewhat unhappy with the database migrations.
For some reason migrations don't work properly. After changing the model and
running `python manage.py db migrate` it runs into an error which have yet to
understand.
