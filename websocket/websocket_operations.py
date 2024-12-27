from flask_socketio import SocketIO, rooms, emit, join_room, leave_room
from common.env_vars import env_vars
from repositories.message_repo import message_repo
from models.db_models import Message


socketio = SocketIO()


@socketio.on("join")
def on_join(data):
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

    


