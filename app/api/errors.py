from flask import make_response

from app.api import api


@api.errorhandler(400)
def bad_request(error):
    """
    Convert error response to bad.

    Args:
        error: (todo): write your description
    """
    return make_response({"error": "Bad Request"}), 400


@api.errorhandler(401)
def unauthorized(error):
    """
    Convert an error.

    Args:
        error: (todo): write your description
    """
    return make_response({"error": "Unauthorized"}), 401


@api.errorhandler(403)
def forbidden(error):
    """
    Return an error response.

    Args:
        error: (todo): write your description
    """
    return make_response({"error": "Forbidden"}), 403


@api.errorhandler(404)
def not_found(error):
    """
    Return an error response.

    Args:
        error: (todo): write your description
    """
    return make_response({"error": "Not found"}), 404


def internal_server_error(error):
    """
    Return the server error message.

    Args:
        error: (todo): write your description
    """
    return make_response({"error": "Internal Server Error"}), 500
