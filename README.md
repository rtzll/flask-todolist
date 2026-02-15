# Flask-Todolist

Flask-Todolist is a simple To Do List web application with the most basic
features of most web apps, i.e. accounts/login, API and (somewhat) interactive
UI.

---

CSS | [Skeleton](http://getskeleton.com/) JS | [jQuery](https://jquery.com/)

I've also build a quite similar app in Django:
https://github.com/rtzll/django-todolist

## Explore

Try it out!

### Docker

Using `docker-compose` you can simple run:

    docker-compose build
    docker-compose up

And the application will run on http://localhost:8000/

(It's serving the app using [gunicorn](http://gunicorn.org/) which you would use
for deployment, instead of just running `flask run`.)

### Manually

If you prefer to run it directly on your local machine, you can use
[uv](https://docs.astral.sh/uv/) for dependency management.

    uv sync
    APP_CONFIG=development FLASK_APP=todolist.py uv run flask run

To add some 'play' data you can run

    uv run flask fill-db

To run the test suite:

    uv run pytest -v

To run the test suite using Docker:

    docker-compose --profile test run --rm tests

Now you can browse the API: http://localhost:5000/api/users

Pick a user, login as the user. Default password after `fill-db` is
_correcthorsebatterystaple_. Click around, there is not too much, but I like the
overview under: http://localhost:5000/todolists (You must be logged in to see
it.)

## Extensions

In the process of this project I used a couple of extensions.

| Usage       | Flask-Extension                                                 |
| ----------- | --------------------------------------------------------------- |
| Model & ORM | [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/latest/)   |
| Migration   | [Flaks-Migrate](http://flask-migrate.readthedocs.io/en/latest/) |
| Forms       | [Flask-WTF](https://flask-wtf.readthedocs.org/en/latest/)       |
| Login       | [Flask-Login](https://flask-login.readthedocs.org/en/latest/)   |
| Testing     | [Flask-Testing](https://pythonhosted.org/Flask-Testing/)        |

I tried out some more, but for the scope of this endeavor the above mentioned
extensions sufficed.
