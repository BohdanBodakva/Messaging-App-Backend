from functools import wraps

from flask import make_response, Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from controllers.http_handlers.handlers import skip_options_request
from repositories.message_repo import message_repo
from repositories.user_repo import user_repo

users_bp = Blueprint('users_bp', __name__)


@users_bp.route('/current-user', methods=['GET', 'OPTIONS'])
@skip_options_request
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()

    current_user = user_repo.get_by_id(int(current_user_id))

    if current_user:
        return {
            'user': current_user.serialize(include_chats=True, include_messages=True)
        }, 200

    return {
        'msg': f"User with id={current_user_id} doesn't exist"
    }, 404


@users_bp.route('/username/contains/<string:text>', methods=['GET', 'OPTIONS'])
@skip_options_request
@jwt_required()
def get_users_where_username_contains_text(text):
    current_user_id = get_jwt_identity()
    current_user = user_repo.get_by_id(int(current_user_id))

    if current_user:
        users = user_repo.get_all()

        matched_users = [user for user in users if user.username != current_user.username]
        serialized_matched_users = [user.serialize() for user in matched_users if text in user.username]

        return {
            'users': serialized_matched_users
        }, 200

    return {
        'msg': f"User with id={current_user_id} doesn't exist"
    }, 404




@users_bp.route('/load/<int:chat_id>', methods=['GET', 'OPTIONS'])
@skip_options_request
def g1w11sadasdsa(chat_id):

    chat_id = int(chat_id)

    history = [m.serialize() for m in message_repo.get_by_chat_id1(chat_id)]
    history = len(history)

    return {
        'history': history
    }, 200

@users_bp.route('/load/<int:chat_id>/<int:limit>/<int:offset>', methods=['GET', 'OPTIONS'])
@skip_options_request
def g111(chat_id, limit, offset):

    chat_id = int(chat_id)
    limit = int(limit)
    offset = int(offset)

    history = [m.serialize() for m in message_repo.get_by_chat_id(chat_id, limit, offset)]
    history = len(history)

    return {
        'history': history
    }, 200


@users_bp.route('/load/<int:chat_id>', methods=['GET', 'OPTIONS'])
@skip_options_request
def g11sdfdsf1(chat_id):

    chat_id = int(chat_id)

    history = [m.serialize() for m in message_repo.get_by_chat_id1(chat_id)]
    history = len(history)

    return {
        'history': history
    }, 200


