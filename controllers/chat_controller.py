from flask import request, jsonify, make_response, Blueprint
from flask_jwt_extended import jwt_required

from repositories.chat_repo import chat_repo

chats_bp = Blueprint('chats_bp', __name__)


@chats_bp.route('/<int:chat_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_chat_by_id(chat_id):
    chat = chat_repo.get_by_id(chat_id)

    if chat:
        return make_response(
            {'chat': chat.serialize(include_messages=True)},
            200
        )

    return make_response(
        {'msg': f"Chat with id={chat_id} doesn't exist"},
        400
    )
