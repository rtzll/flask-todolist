from flask import render_template, request

from .. import api
from . import utils


@utils.app_errorhandler(403)
def forbidden(error):
    """
    Render the error page.

    Args:
        error: (todo): write your description
    """
    if request.path.startswith("/api"):
        return api.errors.forbidden(error)
    return render_template("403.html"), 403


@utils.app_errorhandler(404)
def page_not_found(error):
    """
    Return a json - error page.

    Args:
        error: (todo): write your description
    """
    if request.path.startswith("/api"):
        return api.errors.not_found(error)
    return render_template("404.html"), 404


@utils.app_errorhandler(500)
def internal_server_error(error):
    """
    Render an error handler.

    Args:
        error: (todo): write your description
    """
    if request.path.startswith("/api"):
        return api.errors.internal_server_error(error)
    return render_template("500.html"), 500
