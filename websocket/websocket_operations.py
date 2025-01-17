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

        def sort_chats(c):
            if c.messages:
                return message_repo.get_last_message_by_chat_id(c.id).send_at
            else:
                return datetime(1990, 1, 1)

        user.chats.sort(reverse=True, key=sort_chats)

        user_to_load = user.serialize(include_chats=True)

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


@socketio.on("read_chat_history")
def load_chat_history(data):
    # try:
    chat_id = int(data.get('chat_id'))
    user_id = int(data.get('user_id'))

    message_repo.delete_unread_messages(user_id, chat_id)

    # emit(
    #     "load_chat_history",
    #     {
    #         "chat_id": chat_id,
    #         "chat_history": messages,
    #         "is_end": is_end
    #     },
    #     to=request.sid
    # )
    # except Exception as e:
    # emit(
    #     "load_chat_history_error",
    #     {
    #         "error": repr(e)
    #     },
    #     to=request.sid
    # )
    # print(repr(e))


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

    users_that_unread = user_repo.get_by_chat_id(room)
    users_that_unread = [u for u in users_that_unread if u.id != user_id]

    message = Message(
        text=text,
        send_at=send_at if send_at else datetime.now(),
        sent_files=sent_files_list,
        users_that_unread=users_that_unread,
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


@socketio.on("delete_chat")
def create_chat(data):
    chat_id = int(data.get("chat_id"))

    chat_repo.delete(chat_id)

    emit(
        "delete_chat",
        {
            "chat_id": chat_id
        },
        broadcast=True
    )


@socketio.on("remove_user_from_chat")
def create_chat(data):
    chat_id = int(data.get("chat_id"))
    user_id = int(data.get("user_id"))

    chat_repo.delete(chat_id)

    emit(
        "remove_user_from_chat",
        {
            "chat_id": chat_id
        },
        broadcast=True
    )




