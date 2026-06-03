from functools import wraps
import flask
import os

def with_username():

    # determine correct header #
    header = os.environ.get("X_AUTH_USER_HEADER") or "X-Auth-Request-Preferred-Username"

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            username = flask.request.headers.get(header)
            kwargs["username"] = username
            return f(*args, **kwargs)
        return wrapper
    return decorator