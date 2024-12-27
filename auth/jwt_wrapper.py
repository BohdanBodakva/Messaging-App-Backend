import jwt
from functools import wraps
from flask import request, jsonify, make_response
from common.env_vars import env_vars
from common.constants import INVALID_JWT_MESSAGE
from repositories.user_repo import user_repo


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ("OPTIONS",):
            return _build_cors_preflight_response()

        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message1': INVALID_JWT_MESSAGE}), 401

        try:
            data = jwt.decode(token, env_vars['FLASK_SECRET_KEY'], algorithms=['HS256'])
            current_user = user_repo.get_by_id(int(data['public_id']))
        except:
            return jsonify({'message2': INVALID_JWT_MESSAGE}), 401

        return f(current_user=current_user, *args, **kwargs)

    return decorated
