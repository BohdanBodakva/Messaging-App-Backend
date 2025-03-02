from repositories.base_repo import BaseCrudRepo
from models.db_models import db, Chat, Message, user_chat
from sqlalchemy import and_


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

    def update(self, chat_id: int, chat: Chat):
        pass

    def update_group(self, group_id: int, new_group_name: str, new_group_photo_link: str, new_group_user_list: list):
        if not isinstance(group_id, int):
            raise ValueError(f"Value {group_id} must be 'int' type")

        group_to_update = Chat.query.filter_by(id=group_id).first()
        if group_to_update is None:
            raise ValueError(f"Group with id={group_id} doesn't exist")

        # update params
        if new_group_name:
            group_to_update.name = new_group_name
        if new_group_photo_link:
            group_to_update.chat_photo_link = new_group_photo_link
        if new_group_user_list:
            group_to_update.users = new_group_user_list

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return group_to_update

    def remove_user_from_chat(self, user_id, chat_id):
        if not isinstance(user_id, int):
            raise ValueError(f"Value {user_id} must be 'int' type")
        if not isinstance(chat_id, int):
            raise ValueError(f"Value {chat_id} must be 'int' type")

        try:
            db.session.execute(
                user_chat.delete().where(
                    and_(
                        user_chat.c.user_id == user_id,
                        user_chat.c.chat_id == chat_id
                    )
                )
            )

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self, chat_id):
        if not isinstance(chat_id, int):
            raise ValueError(f"Value {chat_id} must be 'int' type")

        chat_to_delete = Chat.query.filter_by(id=chat_id).first()
        if chat_to_delete is None:
            raise ValueError(f"Chat with id={chat_id} doesn't exist")

        try:
            db.session.delete(chat_to_delete)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


chat_repo = ChatRepo()
