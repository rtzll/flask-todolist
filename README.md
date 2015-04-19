# Flask-Todolist

[![License][license-image]][license-url] [![Build Status][travis-image]][travis-url]

Flask-Todolist is a todolist web application with the most basic features of most web apps, i.e. accounts/login, API and (somewhat) interactive UI.

---
CSS | [Skeleton](http://getskeleton.com/)
JS  | [jQuery](https://jquery.com/)

I've also build a quite similar app in Django: https://github.com/0xfoo/django-todolist


## Explore
Try it out by installing the requirements. (Works with Python 2 and 3.)

    pip install -r requirements.txt

For your exploration you might find it useful to have some data. (This takes a moment or two.)

    python manage.py fill_db

And then start the server (default: http://localhost:5000)

    python manage.py runserver


Now you can browse the API:
http://localhost:5000/api/users

Pick a user, login as the user. Default password after fill_db is *correcthorsebatterystaple*.
Click around, there is not to much, but I like the overview under: http://localhost:5000/todolists
(You must be logged in to see it.)


## Extensions

In the process of this project I used a couple of extensions.

Usage               | Flask-Extension
------------------- | -----------------------
Model & Database    | [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.0/)
Forms               | [Flask-WTF](https://flask-wtf.readthedocs.org/en/latest/)
Login               | [Flask-Login](https://flask-login.readthedocs.org/en/latest/)
Extras              | [Flask-Script](https://flask-script.readthedocs.org/en/latest/)
Testing             | [Flask-Testing](https://pythonhosted.org/Flask-Testing/)

I tried out some more, but for the scope of this endeavor the above mentioned extensions sufficed.


## Issues

So here a few issues, that are still bothering me and hopefully I will come to later.

 - [ ] In testing I found that login_required was returning the site even when not logged in
 - [ ] find a way to test admin_required views
 - [ ] making the todolist titles editable (maybe with some jQuery magic, or use title forms)
 - [ ] using login_required/admin_required for access control on API


[license-url]: https://github.com/0xfoo/flask-todolist/blob/master/LICENSE
[license-image]: https://img.shields.io/badge/license-MIT-blue.svg?style=flat

[travis-url]: https://travis-ci.org/0xfoo/flask-todolist
[travis-image]: https://travis-ci.org/0xfoo/flask-todolist.svg?branch=master
