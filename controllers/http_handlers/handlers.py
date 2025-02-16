from functools import wraps
from flask import request, make_response
from flask_jwt_extended import decode_token


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def skip_options_request(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return _build_cors_preflight_response()

        return fn(*args, **kwargs)

    return wrapper


def validate_access_token(access_token):
    return decode_token(
        access_token,
        csrf_value=None,
        allow_expired=False
    )
