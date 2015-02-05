flask-todolist
=======================
This is a side project in which I'm exploring Flask and some of it's great
extensions by building a smallish web app with some of the most basic features.

### Explore
To try out the app yourself install the requirements.
```
pip install -r requirements.txt
```
For your exploration you might find it useful to have some data.
```
python manage.py fill_db
```
And then start the server(default: http://localhost:5000)
```
python manage.py runserver
```

### Structure
Usage               | Flask-Extension  
------------------- | -----------------------
Model & Database    | (Flask-)SQLAlchemy
Forms               | Flask-WTF
Login               | Flask-Login
Extras              | Flask-Script

*Note*: I was using Flask-Migrate, but for the scope of this project it seemed unfitting.
