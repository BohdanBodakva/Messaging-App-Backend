from auth.jwt_wrapper import token_required
from flask import request, jsonify, make_response, Blueprint
from flask_cors import cross_origin

users_bp = Blueprint('users_bp', __name__)


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


@users_bp.route('/<int:current_user_id>', methods=['GET', 'OPTIONS'])
@token_required
def get_user_by_username(current_user, current_user_id):
    if current_user and current_user.id == int(current_user_id):
        return make_response(
            {'user': current_user.serialize(include_chats=True)},
            200
        )

    return make_response(
        {'msg': f"User with id={current_user_id} doesn't exist"},
        400
    )
