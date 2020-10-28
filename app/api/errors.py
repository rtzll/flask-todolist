from flask import make_response

from app.api import api


@api.errorhandler(400)
def bad_request(error):
    return make_response({"error": "Bad Request"}), 400


@api.errorhandler(401)
def unauthorized(error):
    return make_response({"error": "Unauthorized"}), 401


@api.errorhandler(403)
def forbidden(error):
    return make_response({"error": "Forbidden"}), 403


@api.errorhandler(404)
def not_found(error):
    return make_response({"error": "Not found"}), 404


def internal_server_error(error):
    return make_response({"error": "Internal Server Error"}), 500
