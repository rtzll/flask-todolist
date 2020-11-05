from functools import wraps

from flask import abort


def admin_required(f):
    """
    Decorator for views that checks if user is logged in.

    Args:
        f: (todo): write your description
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        Decorator for views that the user is logged in.

        Args:
        """
        from flask_login import current_user

        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
