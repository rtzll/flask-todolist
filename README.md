# Flask-Todolist

[![License][license-image]][license-url]
[![Build Status][travis-image]][travis-url]

Flask-Todolist is a simple To Do List web application with the most basic
features of most web apps, i.e. accounts/login, API and (somewhat) interactive
UI.

---
CSS | [Skeleton](http://getskeleton.com/)
JS  | [jQuery](https://jquery.com/)

I've also build a quite similar app in Django:
https://github.com/rtzll/django-todolist


## Explore
Try it out!
### Docker
Using `docker-compose` you can simple run:

    docker-compose build
    docker-compose up

And the application will run on http://localhost:8000/

(It's serving the app using [gunicorn](http://gunicorn.org/) which you would
use for deployment, instead of just running `flask run`.)

### Manually
If you prefer to run it directly on your local machine, I suggest using
[venv](https://docs.python.org/3/library/venv.html).

    pip install -r requirements.txt
    FLASK_APP=todolist.py flask run

To add some 'play' data you can run

    pip install -r test-requirements.txt
    flask fill-db

Now you can browse the API:
http://localhost:5000/api/users

Pick a user, login as the user. Default password after `fill-db` is
*correcthorsebatterystaple*.
Click around, there is not too much, but I like the overview under:
http://localhost:5000/todolists
(You must be logged in to see it.)


## Extensions
In the process of this project I used a couple of extensions.

Usage               | Flask-Extension
------------------- | -----------------------
Model & ORM         | [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/latest/)
Migration           | [Flaks-Migrate](http://flask-migrate.readthedocs.io/en/latest/)
Forms               | [Flask-WTF](https://flask-wtf.readthedocs.org/en/latest/)
Login               | [Flask-Login](https://flask-login.readthedocs.org/en/latest/)
Testing             | [Flask-Testing](https://pythonhosted.org/Flask-Testing/)

I tried out some more, but for the scope of this endeavor the above mentioned extensions sufficed.

[license-url]: https://github.com/rtzll/flask-todolist/blob/master/LICENSE
[license-image]: https://img.shields.io/badge/license-MIT-blue.svg?style=flat

[travis-url]: https://travis-ci.org/rtzll/flask-todolist
[travis-image]: https://travis-ci.org/rtzll/flask-todolist.svg?branch=master
