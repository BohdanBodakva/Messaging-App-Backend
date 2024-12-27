from auth.jwt_wrapper import token_required
from flask import request, jsonify, make_response, Blueprint
from repositories.chat_repo import chat_repo

chats_bp = Blueprint('chats_bp', __name__)


@chats_bp.route('/<int:chat_id>', methods=['GET', 'OPTIONS'])
@token_required
def get_chat_by_id(current_user, chat_id):
    chat = chat_repo.get_by_id(chat_id)

    if current_user and chat:
        return make_response(
            {'chat': chat.serialize(include_messages=True)},
            200
        )

    return make_response(
        {'msg': f"Chat with id={chat_id} doesn't exist"},
        400
    )
