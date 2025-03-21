import time
from datetime import datetime

import requests
from flask import request
from flask_socketio import SocketIO, rooms, emit, join_room, leave_room

from controllers.http_handlers.handlers import validate_access_token
from models.db_models import Message, SentFile, User, Chat
from repositories.chat_repo import chat_repo
from repositories.message_repo import message_repo
from repositories.user_repo import user_repo
import base64
import boto3
import io

# import redis



s3_client = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


socketio = SocketIO()


@socketio.on('typing')
def handle_typing(data):
    user_id = data.get("user_id")
    chat_id = data.get("chat_id")

    user = user_repo.get_by_id(user_id)

    socketio.emit(
        "user_typing",
        {
            "user_id": user_id,
            "name": user.name,
            "surname": user.surname
        },
        room=chat_id
    )


@socketio.on("validate_token")
def validate_token(data):
    access_token = data.get('access_token')

    try:
        if not access_token:
            emit(
                "validate_token_error",
                {
                    "error": "access_token is missing in request"
                },
                to=request.sid
            )

        decoded_token = validate_access_token(access_token)
        user_id = int(decoded_token.get("sub"))
        if decoded_token and user_id:
            emit(
                "validate_token",
                {
                    "msg": "access_token validation is successful",
                    "user_id": user_id
                },
                to=request.sid
            )
        else:
            emit(
                "validate_token_error",
                {
                    "error": "access_token is expired or incorrect"
                },
                to=request.sid
            )
    except Exception as e:
        emit(
            "validate_token_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


# === USER ===

@socketio.on("load_user")
def load_user(data):
    try:
        user_id = int(data.get('user_id'))
        user = user_repo.get_by_id(user_id)

        if user:
            def sort_chats(c):
                if c.messages:
                    return message_repo.get_last_message_by_chat_id(c.id).send_at
                else:
                    return c.created_at

            user.chats.sort(reverse=True, key=sort_chats)

            user_to_load = user.serialize(include_chats=True)
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
                    "error": f"User with id={user_id} doesn't exist"
                },
                to=request.sid
            )
    except Exception as e:
        print(repr(e))
        emit(
            "load_user_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("load_user_chats")
def load_user_chats(data):
    try:
        user_id = int(data.get('user_id'))
        user = user_repo.get_by_id(user_id)

        if user:
            def sort_chats(c):
                if c.messages:
                    return message_repo.get_last_message_by_chat_id(c.id).send_at
                else:
                    return datetime(1990, 1, 1)

            user.chats.sort(reverse=True, key=sort_chats)

            user_chats = [chat.serialize() for chat in user.chats]

            emit(
                "load_user_chats",
                {
                    "msg": "Success",
                    "user_chats": user_chats
                },
                to=request.sid
            )
        else:
            emit(
                "load_user_chats_error",
                {
                    "error": f"User with id={user_id} doesn't exist"
                },
                to=request.sid
            )
    except Exception as e:
        print(repr(e))
        emit(
            "load_user_chats_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("change_user_info")
def change_user_info(data):
    try:
        user_id = int(data.get('user_id'))
        user = user_repo.get_by_id(user_id)

        new_name = data.get("new_name")
        new_surname = data.get("new_surname")
        new_username = data.get("new_username")

        if user.username != new_username:
            is_username_unique = len(user_repo.get_all_by_username(new_username)) == 0
            if not is_username_unique:
                emit(
                    "change_user_info_username_exists",
                    {
                        "msg": f"Username={new_username} already exists"
                    },
                    to=request.sid
                )
                return

        if user:
            new_user = User()

            if new_name:
                new_user.name = str(new_name)
            if new_surname:
                new_user.surname = str(new_surname)
            if new_username:
                new_user.username = str(new_username)

            updated_user = user_repo.update(user_id=user_id, new_user=new_user)
            updated_user = updated_user.serialize(
                include_chats=False,
                include_last_message=False,
                include_messages=False,
                include_unread_messages=False
            )

            emit(
                "change_user_info",
                {
                    "msg": "Success",
                    "user": updated_user
                },
                to=request.sid
            )
            emit(
                "change_user_info_for_chat_list",
                {
                    "msg": "Success",
                    "changed_user_id": user.id
                },
                broadcast=True
            )
        else:
            emit(
                "change_user_info_error",
                {
                    "error": f"User with id={user_id} doesn't exist"
                },
                to=request.sid
            )
    except Exception as e:
        emit(
            "change_user_info_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("change_group_info")
def change_group_info(data):
    try:
        group_id = data.get('group_id')
        new_user_ids = list(data.get('new_user_ids'))
        new_name = str(data.get('new_name'))
        new_group_photo_link = str(data.get('new_chat_photo_link'))

        group = chat_repo.get_by_id(group_id)

        print([u.id for u in group.users])

        if group:
            new_users = [user_repo.get_by_id(u_id) for u_id in new_user_ids]

            updated_group = chat_repo.update_group(
                group_id=group_id,
                new_group_name=new_name,
                new_group_photo_link=new_group_photo_link,
                new_group_user_list=new_users
            )

            print([u.id for u in updated_group.users])

            updated_group = updated_group.serialize(
                include_last_message=False,
                include_messages=False
            )

            emit(
                "change_group_info",
                {
                    "updated_group": updated_group
                },
                room=group_id
            )
            emit(
                "change_group_info_from_chat_area",
                {
                    "updated_group": updated_group
                },
                room=group_id
            )
            emit(
                "change_group_info_from_chat_list",
                {
                    "updated_group": updated_group
                },
                room=group_id
            )
    except Exception as e:
        print(repr(e))
        emit(
            "change_group_info_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("go_online")
def go_online(data):
    try:
        user_id = int(data.get('user_id'))

        user_repo.go_online(user_id)

        print("online")

        emit(
            "set_status",
            {
                "msg": "Success",
                "is_online": True,
                "user_id": user_id
            },
            broadcast=True
        )
    except Exception as e:
        emit(
            "go_online_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("search_users_by_username")
@socketio.on("search_users_for_group")
def search_users_by_username(data):
    event_name = str(request.event['message'])

    try:
        value = str(data.get('username_value'))
        users = user_repo.get_all()

        serialized_matched_users = [
            user.serialize(include_last_message=False) for user in users if value in user.username
        ]

        emit(
            event_name,
            {
                "users": serialized_matched_users
            },
            to=request.sid
        )
    except Exception as e:
        emit(
            f"{event_name}_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("go_offline")
def go_offline(data):
    try:
        user_id = int(data.get('user_id'))

        user_repo.go_offline(user_id)

        emit(
            "set_status",
            {
                "msg": "Success",
                "is_online": False,
                "user_id": user_id
            },
            broadcast=True
        )
    except Exception as e:
        emit(
            "go_offline_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


# === CHAT ===

@socketio.on("load_chat_history")
def load_chat_history(data):
    try:
        chat_id = int(data.get('chat_id'))
        items_count = int(data.get('items_count'))
        offset = int(data.get('offset'))

        messages = message_repo.get_by_chat_id(chat_id=chat_id, limit=items_count, offset=offset)

        messages.sort(key=lambda msg: msg.send_at)
        messages = [msg.serialize() for msg in messages]

        print(messages)

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
    try:
        chat_id = int(data.get('chat_id'))
        user_id = int(data.get('user_id'))

        message_repo.delete_unread_messages(user_id, chat_id)
    except Exception as e:
        emit(
            "read_chat_history_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("clear_chat_history")
def load_chat_history(data):
    try:
        chat_id = int(data.get('chat_id'))

        message_repo.clear_chat_history(chat_id)

        emit(
            "clear_chat_history",
            {
                "msg": "Success"
            },
            to=request.sid
        )
    except Exception as e:
        emit(
            "clear_chat_history_error",
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
    try:
        room = data.get("room")

        leave_room(room)
        emit(
            "leave_room",
            {
                "msg": "Success"
            },
            to=room
        )
    except Exception as e:
        print(repr(e))


# === MESSAGE ===

@socketio.on("send_message")
def send_message(data):
    try:
        user_id = int(data.get("user_id"))
        text = data.get("text")
        sent_files = data.get("sent_files")
        send_at = datetime.fromisoformat(data.get("sent_at").replace("Z", "+00:00"))

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
        message = message.serialize(include_files=True)

        user_that_send = user_repo.get_by_id(user_id)
        user_that_send = user_that_send.serialize(
            include_chats=False,
            include_last_message=False,
            include_messages=False,
            include_unread_messages=False
        )

        chat = chat_repo.get_by_id(room)
        chat = chat.serialize(
            include_last_message=False,
            include_messages=False
        )

        if room in rooms():
            emit(
                "send_message",
                {
                    "message": message,
                    "room": room
                },
                to=room
            )
            emit(
                "send_message_chat_list",
                {
                    "message": message,
                    "chat": chat,
                    "user_that_send": user_that_send,
                    "room": room
                },
                to=room
            )
    except Exception as e:
        emit(
            "send_message_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("delete_message")
def delete_message(data):
    try:
        message_id = int(data.get("message_id"))
        room = int(data.get("room"))

        message_repo.delete(message_id)

        last_chat_message = message_repo.get_last_message_by_chat_id(chat_id=room)
        if last_chat_message:
            last_chat_message = last_chat_message.serialize(include_files=False)

        emit(
            "delete_message",
            {
                "message_id": message_id,
                "chat_id": room,
                "status": "Deleted"
            },
            to=room
        )
        emit(
            "delete_message_chat_list",
            {
                "message_id": message_id,
                "chat_id": room,
                "last_chat_message": last_chat_message,
                "status": "Deleted"
            },
            to=room
        )
    except Exception as e:
        emit(
            "delete_message_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("create_chat")
@socketio.on("create_group")
def create_chat(data):
    try:
        event_name = str(request.event['message'])

        current_user_id = int(data.get("current_user_id"))
        user_ids = list(data.get("user_ids"))
        is_group = bool(data.get("is_group"))
        created_at = datetime.fromisoformat(data.get("created_at").replace("Z", "+00:00"))
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

        if event_name == "create_chat":
            emit(
                event_name,
                {
                    "current_user_id": current_user_id,
                    "chat": chat.serialize(),
                    "users": [u.serialize() for u in users]
                },
                broadcast=True
            )
        else:

            emit(
                event_name,
                {
                    "current_user_id": current_user_id,
                    "chat": chat.serialize(),
                    "users": [u.serialize() for u in users]
                },
                broadcast=True
            )
            emit(
                "create_group_chat_list",
                {
                    "current_user_id": current_user_id,
                    "chat": chat.serialize(),
                    "users": [u.serialize() for u in users]
                },
                broadcast=True
            )
    except Exception as e:
        print(repr(e))
        emit(
            f"{event_name}_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("delete_chat")
def delete_chat(data):
    try:
        chat_id = int(data.get("chat_id"))

        chat_repo.delete(chat_id)

        emit(
            "delete_chat",
            {
                "chat_id": chat_id
            },
            room=chat_id
        )
        emit(
            "delete_chat_from_chat_info",
            {
                "chat_id": chat_id
            },
            room=chat_id
        )
        emit(
            "delete_chat_from_chats",
            {
                "chat_id": chat_id
            },
            room=chat_id
        )
    except Exception as e:
        emit(
            "delete_chat_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("leave_group")
def leave_group(data):
    try:
        chat_id = int(data.get("chat_id"))
        user_id = int(data.get("user_id"))

        chat_repo.remove_user_from_chat(user_id=user_id, chat_id=chat_id)

        emit(
            "leave_group",
            {
                "user_id": user_id,
                "chat_id": chat_id
            },
            room=chat_id
        )
        emit(
            "leave_group_from_chat_area",
            {
                "user_id": user_id,
                "chat_id": chat_id
            },
            to=request.sid
        )
        emit(
            "leave_group_from_chats",
            {
                "user_id": user_id,
                "chat_id": chat_id
            },
            to=request.sid
        )
    except Exception as e:
        emit(
            "leave_group_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on("remove_user_from_chat")
def remove_user_from_chat(data):
    try:
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
    except Exception as e:
        emit(
            "remove_user_from_chat_error",
            {
                "error": repr(e)
            },
            to=request.sid
        )


@socketio.on('upload_user_image')
@socketio.on('upload_group_image')
def handle_image(data):
    event_name = str(request.event['message'])

    try:
        user_id = data["user_id"]
        image_data = data["image"]
        filename = data["filename"]

        user = user_repo.get_by_id(user_id)
        if user:
            image_bytes = base64.b64decode(image_data)

            image_file = io.BytesIO(image_bytes)

            s3_client.upload_fileobj(
                image_file,
                S3_BUCKET,
                filename
            )

            file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"

            user_repo.update_profile_photo_link_by_id(user_id, file_url)

            emit(
                event_name,
                {
                    "image_url": file_url
                },
                broadcast=True
            )
        else:
            emit(
                f'{event_name}_error',
                {
                    "error": f"User with id={user_id} doesn't exist"
                },
                to=request.sid
            )
    except Exception as e:
        emit(
            'upload_user_image_error',
            {
                "error": repr(e)
            },
            to=request.sid
        )


TOGETHER_AI_BEARER_TOKEN = "6db4431fee0f8d275a3473835f5650e913d88a68b08ea57ce86d97a04ced89d7"


@socketio.on("ai_chat")
def ai_chat(data):
    print("GO")
    try:
        user_input = data["prompt"]
        user_id = int(data["user_id"])
        chat_id = int(data["chat_id"])
        sent_at = data["sent_at"]

        if not user_input:
            emit(
                "ai_chat_error",
                {
                    "error": "Incorrect or empty user input"
                },
                to=request.sid
            )

        ai_user = user_repo.get_by_id(1)
        user = user_repo.get_by_id(user_id)
        chat = chat_repo.get_by_id(chat_id)

        # Save user message
        message = Message(
            text=user_input,
            send_at=sent_at if sent_at else datetime.now(),
            sent_files=[],
            users_that_unread=[],
            user_id=user_id,
            chat_id=chat_id
        )

        message.id = message_repo.create(message)
        message = message.serialize()

        print(f"NEW MESSAGE: {message}")

        emit(
            "send_message",
            {
                "message": message,
                "room": chat_id
            },
            room=chat_id
        )

        # Save AI message
        prompt = [
            {"role": "user", "content": user_input}
        ]

        # last_messages = message_repo.get_by_chat_id(
        #     chat_id=chat_id,
        #     limit=10,
        #     offset=0
        # )
        # for msg in last_messages:
        #     role = "assistant" if msg.user_id == 1 else "user"
        #     prompt.append(
        #         {"role": role, "content": msg.text}
        #     )

        print(f"PROMPT: {prompt}")

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={"Authorization": f"Bearer {TOGETHER_AI_BEARER_TOKEN}"},
            json={
                "model": "meta-llama/Llama-2-7b-chat-hf",
                "messages": prompt,
                "max_tokens": 250
            }
        )

        print(response.json())

        ai_response_text = response.json()["choices"][0]["message"]["content"]

        ai_message = Message(
            text=ai_response_text,
            send_at=datetime.now(),
            sent_files=[],
            users_that_unread=[],
            user_id=1,
            chat_id=chat_id
        )

        ai_message.id = message_repo.create(ai_message)
        ai_message = ai_message.serialize()

        time.sleep(0.5)
        emit(
            "send_message",
            {
                "message": ai_message,
                "room": chat_id
            },
            room=chat_id
        )
    except Exception as e:
        print(repr(e))
        emit(
            'ai_chat_error',
            {
                "error": repr(e)
            },
            to=request.sid
        )
