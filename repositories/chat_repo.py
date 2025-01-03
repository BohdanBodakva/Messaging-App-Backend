from sqlalchemy import func

from repositories.base_repo import BaseCrudRepo
from models.db_models import db, Chat, user_chat
from datetime import datetime


class ChatRepo(BaseCrudRepo):
    def get_all(self):
        all_chats = Chat.query.all()
        return all_chats

    def get_chats_by_is_group(self, is_group: bool):
        only_chats = Chat.query.filter_by(is_group=is_group).all()
        return only_chats

    def get_by_id(self, chat_id: int):
        if not isinstance(chat_id, int):
            raise ValueError(f"Value {chat_id} must be 'int' type")

        chat = Chat.query.filter_by(id=chat_id).first()

        return chat

    # def get_by_user_ids(self, user_ids: list):
    #     # if not isinstance(user1_id, int):
    #     #     raise ValueError(f"Value {user1_id} must be 'int' type")
    #     # if not isinstance(user2_id, int):
    #     #     raise ValueError(f"Value {user2_id} must be 'int' type")
    #
    #     # chat = Chat.query.filter_by(
    #     #     (len(Chat.users) == 2)
    #     #     and
    #     #     (Chat.users[0].id == user1_id or Chat.users[1].id == user2_id)
    #     #     and
    #     #     (Chat.users[0].id == user2_id or Chat.users[1].id == user1_id)
    #     # ).first()
    #
    #     subquery = (
    #         db.session.query(user_chat.c.chat_id)
    #         .filter(user_chat.c.user_id.in_(user_ids))  # Filter user IDs
    #         .group_by(user_chat.c.chat_id)
    #         .having(func.count(user_chat.c.user_id) == len(user_ids))  # Match exact count
    #         .subquery()
    #     )
    #
    #     # Query chats that match the subquery
    #     chat = db.session.query(Chat).filter(Chat.id.in_(subquery)).first()
    #
    #     return chat

    def create(self, chat: Chat):
        if not isinstance(chat, Chat):
            raise ValueError(f"Value {chat} must be 'Chat' type")

        try:
            db.session.add(chat)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return chat.id

    def update(self, chat_id: int, new_chat: Chat):
        if not isinstance(chat_id, int):
            raise ValueError(f"Value {chat_id} must be 'int' type")
        if not isinstance(new_chat, Chat):
            raise ValueError(f"Value {new_chat} must be 'Chat' type")

        chat_to_update = Chat.query.filter_by(id=chat_id).first()
        if chat_to_update is None:
            raise ValueError(f"User with id={chat_id} doesn't exist")

        # update params
        if new_chat.name:
            chat_to_update.name = new_chat.name
        if new_chat.chat_photo_link:
            chat_to_update.chat_photo_link = new_chat.chat_photo_link

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return chat_id
    
    # def add_message_to_chat(self, new_message: Message, chat_id: int):
    #     if not isinstance(chat_id, int):
    #         raise ValueError(f"Value {chat_id} must be 'int' type")
    #     if not isinstance(new_message, Chat):
    #         raise ValueError(f"Value {new_message} must be 'Message' type")

    #     chat_to_update = Chat.query.filter_by(id=chat_id).first()
    #     if chat_to_update is None:
    #         raise ValueError(f"User with id={chat_id} doesn't exist")

    #     chat_to_update.messages.append(new_message)

    #     try:
    #         db.session.commit()
    #     except Exception as e:
    #         db.session.rollback()
    #         raise e

    #     return chat_id

    def delete(self, chat_id):
        if not isinstance(chat_id, int):
            raise ValueError(f"Value {chat_id} must be 'int' type")

        user_to_delete = Chat.query.filter_by(id=chat_id).first()
        if user_to_delete is None:
            raise ValueError(f"Chat with id={chat_id} doesn't exist")

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


chat_repo = ChatRepo()
