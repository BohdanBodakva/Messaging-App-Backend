import jwt
from functools import wraps
from flask import request, jsonify
from common.env_vars import env_vars
from common.constants import INVALID_JWT_MESSAGE
from repositories.user_repo import user_repo


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': INVALID_JWT_MESSAGE}), 401

        try:
            data = jwt.decode(token, env_vars['FLASK_SECRET_KEY'], algorithms=['HS256'])
            current_user = user_repo.get_by_id(int(data['public_id']))
        except:
            return jsonify({'message': INVALID_JWT_MESSAGE}), 401

        return f(current_user, *args, **kwargs)

    return decorated