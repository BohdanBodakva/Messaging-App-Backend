from datetime import datetime

from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import SocketIO, rooms, emit, join_room, leave_room

from controllers.http_handlers.handlers import validate_access_token
from repositories.message_repo import message_repo
from models.db_models import Message
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
def connect(data):
    try:
        user_id = data.get('user_id')
        user = user_repo.get_by_id(int(user_id))

        load_messages_value = data.get('load_messages')
        load_messages = bool(load_messages_value) if load_messages_value else False

        a = user.serialize(
                        include_chats=True,
                        include_messages=load_messages
                    )

        if user:
            emit(
                "load_user",
                {
                    "msg": "Success",
                    "user": a
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






@socketio.on("disconnect")
def disconnect(data):
    print("Disconnected")


@socketio.on("b")
def connect(data):
    emit("b", {"data": "data"},
         # to=request.sid,
         broadcast=True)
    # print(1111111111111)


@socketio.on("get_user_data", namespace=namespace)
def go_online(data):
    try:
        user_id = int(data.user.id)

        user = user_repo.get_by_id(user_id)

        if user:
            emit(
                "get_user_data",
                {
                    "user": user.serialize(include_chats=True)
                },
                namespace=namespace,
                to=request.sid
            )
    except Exception as e:
        emit_error(
            "get_current_user_data_error",
            repr(e),
            name_space=namespace,
            to=request.sid
        )


@socketio.on("change_status", namespace=namespace)
def go_online(data):
    try:
        user_id = int(data.user.id)
        is_online = bool(data.is_online)

        if is_online:
            user_repo.update_last_seen_by_id(user_id)
        else:
            user_repo.update_last_seen_by_id(user_id, datetime.now())

        emit(
            "user_status_updated",
            {
                "user_id": user_id,
                "status": is_online
            },
            namespace=namespace,
            broadcast=True
        )
    except Exception as e:
        emit_error(
            "change_status_error",
            repr(e),
            name_space=namespace,
            to=request.sid
        )


@socketio.on("change_user_info", namespace=namespace)
def go_online(data):
    try:
        user_id = int(data.user.id)
        new_user = data.new_user

        updated_user = user_repo.update(user_id, new_user)

        emit(
            "change_user_info",
            updated_user.serialize(),
            namespace=namespace,
            broadcast=True
        )
    except Exception as e:
        emit_error(
            "change_user_info_error",
            repr(e),
            name_space=namespace,
            to=request.sid
        )


# Namespace "/rooms"
namespace = "/rooms"


@socketio.on("join_room", namespace="/rooms")
def join_room(data):
    user_id = data.get("user_id")
    room = data.get("room")
    join_room(room)
    emit(
        "join",
        {
            "user_id": user_id
        },
        to=room
    )


@socketio.on("leave")
def on_leave(data):
    user_id = data.get("user_id")
    room = data.get("room")
    leave_room(room)
    emit(
        "leave",
        {
            "user_id": user_id
        },
        to=room
    )


@socketio.on("message")
def handle_message(data):
    user_id = data.get("user_id")
    message = data.get("message")
    room = data.get("room")

    print("message:", message)

    if room in rooms():
        emit(
            "message",
            {
                "user_id": user_id,
                "message": message,
                "room": room
            },
            to=room
        )

    message_repo.create(
        Message(
            text=message,
            user_id=user_id,
            chat_id=room
        )
    )
