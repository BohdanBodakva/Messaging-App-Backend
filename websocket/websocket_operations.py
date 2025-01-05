from datetime import datetime

from flask import request
from flask_socketio import SocketIO, rooms, emit, join_room, leave_room

from controllers.http_handlers.handlers import validate_access_token
from models.db_models import Message, SentFile, User, Chat
from repositories.chat_repo import chat_repo
from repositories.message_repo import message_repo
from repositories.user_repo import user_repo

socketio = SocketIO()


def emit_error(event, error_message, name_space=None, room=None, to=None):
    error_json = {"error": error_message}

    if name_space and room:
        emit(event, error_json, namespace=name_space, room=room)
    elif name_space:
        emit(event, error_json, namespace=name_space)
    elif room:
        emit(event, error_json, room=room)
    elif to:
        emit(event, error_json, to=to)
    else:
        emit(event, error_json)


# Namespace "/public"
namespace = "/public"


@socketio.on("validate_token")
def connect(data):
    access_token = data.get('access_token')

    try:
        if not access_token:
            raise Exception("access_token is missing")

        decoded_token = validate_access_token(access_token)
        user_id = int(decoded_token.get("sub"))
        if decoded_token and user_id:
            emit(
                "validate_token",
                {
                    "msg": "Connected successfully",
                    "user_id": user_id
                },
                to=request.sid
            )
        else:
            emit(
                "validate_token_error",
                {
                    "msg": f"Incorrect data",
                    "error": ""
                },
                to=request.sid
            )
    except Exception as e:
        emit(
            "validate_token_error",
            {
                "msg": f"Error while validating",
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("validate_refreshed_token")
def connect(data):
    access_token = data.get('access_token')

    try:
        if not access_token:
            raise Exception("access_token is missing")

        decoded_token = validate_access_token(access_token)
        user_id = int(decoded_token.get("sub"))
        if decoded_token and user_id:
            emit(
                "validate_refreshed_token",
                {
                    "msg": "Validated successfully",
                    "user_id": user_id
                },
                to=request.sid
            )
        else:
            emit(
                "validate_refreshed_token_error",
                {
                    "msg": f"Incorrect data"
                },
                to=request.sid
            )
    except Exception as e:
        emit(
            "validate_refreshed_token_error",
            {
                "msg": repr(e)
            },
            to=request.sid
        )


@socketio.on("load_user")
def load_user(data):
    try:
        user_id = int(data.get('user_id'))
        user_repo.update_last_seen_by_id(user_id=user_id, new_last_seen=None)

        user = user_repo.get_by_id(user_id)

        user_to_load = user.serialize(include_chats=True)
        user_to_inform_update = user.serialize()

        # for idx, c in enumerate(user_to_load.chats):
        #     user.chats[idx]["messages"] = message_repo.get_last_message_by_chat_id(c.id)

        if user:
            emit(
                "load_user",
                {
                    "msg": "Success",
                    "user": user_to_load
                },
                to=request.sid
            )
        else:
            emit(
                "load_user_error",
                {
                    "msg": f"User with id={user_id} doesn't exist"
                },
                to=request.sid
            )
    except Exception as e:
        emit(
            "load_user_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("load_chat_history")
def load_chat_history(data):
    try:
        chat_id = int(data.get('chat_id'))
        items_count = int(data.get('items_count'))
        offset = int(data.get('offset'))

        messages = message_repo.get_by_chat_id(chat_id=chat_id, limit=items_count, offset=offset)

        messages.sort(key=lambda msg: msg.send_at)
        messages = [msg.serialize() for msg in messages]

        is_end = len(messages) < items_count

        emit(
            "load_chat_history",
            {
                "chat_id": chat_id,
                "chat_history": messages,
                "is_end": is_end
            },
            to=request.sid
        )
    except Exception as e:
        emit(
            "load_chat_history_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )





# === ROOMS ===

@socketio.on("join_room")
def on_join_room(data):
    room = int(data.get("room"))

    join_room(room)
    emit(
        "join_room",
        {
            "msg": "Success",
            "room": room
        },
        to=room
    )


@socketio.on("leave_room")
def on_leave(data):
    room = data.get("room")

    leave_room(room)
    emit(
        "leave_room",
        {
            "msg": "Success"
        },
        to=room
    )


@socketio.on("send_message")
def send_message(data):
    user_id = data.get("user_id")
    text = data.get("text")
    sent_files = data.get("sent_files")
    send_at = data.get("sent_at")

    room = int(data.get("room"))

    sent_files_list = []
    if sent_files:
        for file in sent_files:
            file_link = file.get("file_link")
            if file_link:
                sent_files_list.append(SentFile(
                    file_link=file_link
                ))

    message = Message(
        text=text,
        send_at=send_at if send_at else datetime.now(),
        sent_files=sent_files_list,
        users_that_unread=user_repo.get_by_chat_id(room),
        user_id=user_id,
        chat_id=room
    )

    message.id = message_repo.create(message)

    if room in rooms():
        emit(
            "send_message",
            {
                "message": message.serialize(include_files=True),
                "room": room
            },
            to=room
        )


@socketio.on("delete_message")
def delete_message(data):
    message_id = int(data.get("message_id"))
    room = int(data.get("room"))

    message_repo.delete(message_id)

    emit(
        "delete_message",
        {
            "message_id": message_id,
            "chat_id": room,
            "status": "Deleted"
        },
        to=room
    )




@socketio.on("create_chat")
def create_chat(data):
    current_user_id = int(data.get("current_user_id"))
    user_ids = list(data.get("user_ids"))
    is_group = bool(data.get("is_group"))
    created_at = data.get("created_at")
    name = data.get("name")
    chat_photo_link = data.get("chat_photo_link")

    users = [user_repo.get_by_id(u_id) for u_id in user_ids]

    chats_by_is_group = chat_repo.get_chats_by_is_group(is_group=is_group)

    def do_filter(c):
        user_ids_list = [u.id for u in c.users]
        return (current_user_id in user_ids_list) and (user_ids[0] in user_ids_list)

    if is_group:
        filtered_chats = None
    else:
        filtered_chats = list(filter(lambda c: do_filter(c), chats_by_is_group))

    chat = None
    if not filtered_chats:
        current_user = user_repo.get_by_id(current_user_id)

        if current_user and users:
            new_chat = Chat(
                name=name if (is_group and name) else None,
                admin_id=current_user_id if is_group else None,
                chat_photo_link=chat_photo_link if (is_group and chat_photo_link) else None,
                created_at=created_at,
                is_group=is_group,
                users=[current_user, *users]
            )

            new_chat_id = chat_repo.create(new_chat)

            chat = new_chat
            chat.id = new_chat_id
    else:
        chat = filtered_chats[0]

    emit(
        "create_chat",
        {
            "current_user_id": current_user_id,
            "chat": chat.serialize(),
            "users": [u.serialize() for u in users]
        },
        broadcast=True
    )


# ================================================================================================================

# @socketio.on("b")
# def connect(data):
#     emit("b", {"data": "data"},
#          # to=request.sid,
#          broadcast=True)
#     # print(1111111111111)
#
#
# @socketio.on("get_user_data", namespace=namespace)
# def go_online(data):
#     try:
#         user_id = int(data.user.id)
#
#         user = user_repo.get_by_id(user_id)
#
#         if user:
#             emit(
#                 "get_user_data",
#                 {
#                     "user": user.serialize(include_chats=True)
#                 },
#                 namespace=namespace,
#                 to=request.sid
#             )
#     except Exception as e:
#         emit_error(
#             "get_current_user_data_error",
#             repr(e),
#             name_space=namespace,
#             to=request.sid
#         )
#
#
# @socketio.on("change_status", namespace=namespace)
# def go_online(data):
#     try:
#         user_id = int(data.user.id)
#         is_online = bool(data.is_online)
#
#         if is_online:
#             user_repo.update_last_seen_by_id(user_id)
#         else:
#             user_repo.update_last_seen_by_id(user_id, datetime.now())
#
#         emit(
#             "user_status_updated",
#             {
#                 "user_id": user_id,
#                 "status": is_online
#             },
#             namespace=namespace,
#             broadcast=True
#         )
#     except Exception as e:
#         emit_error(
#             "change_status_error",
#             repr(e),
#             name_space=namespace,
#             to=request.sid
#         )
#
#
# @socketio.on("change_user_info", namespace=namespace)
# def go_online(data):
#     try:
#         user_id = int(data.user.id)
#         new_user = data.new_user
#
#         updated_user = user_repo.update(user_id, new_user)
#
#         emit(
#             "change_user_info",
#             updated_user.serialize(),
#             namespace=namespace,
#             broadcast=True
#         )
#     except Exception as e:
#         emit_error(
#             "change_user_info_error",
#             repr(e),
#             name_space=namespace,
#             to=request.sid
#         )
#
#
# # Namespace "/rooms"
# namespace = "/rooms"
#
#
#
#
#
# @socketio.on("message")
# def handle_message(data):
#     user_id = data.get("user_id")
#     message = data.get("message")
#     room = data.get("room")
#
#     print("message:", message)
#
#     if room in rooms():
#         emit(
#             "message",
#             {
#                 "user_id": user_id,
#                 "message": message,
#                 "room": room
#             },
#             to=room
#         )
#
#     message_repo.create(
#         Message(
#             text=message,
#             user_id=user_id,
#             chat_id=room
#         )
#     )
