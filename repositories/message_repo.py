from repositories.base_repo import BaseCrudRepo
from models.db_models import db, Message, unread_messages, Chat


class MessageRepo(BaseCrudRepo):
    def get_all(self):
        all_messages = Message.query.all()
        return all_messages

    def get_by_id(self, message_id: int):
        if not isinstance(message_id, int):
            raise ValueError(f"Value {message_id} must be 'int' type")

        message = Message.query.filter_by(id=message_id).first()

        return message

    def get_last_message_by_chat_id(self, chat_id: int):
        if not isinstance(chat_id, int):
            raise ValueError(f"Value {chat_id} must be 'int' type")

        message = Message.query.filter_by(chat_id=chat_id).order_by(Message.id.desc()).first()

        return message

    def get_by_chat_id(self, chat_id: int, limit: int, offset: int):
        if not isinstance(chat_id, int):
            raise ValueError(f"Value {chat_id} must be 'int' type")
        if not isinstance(limit, int):
            raise ValueError(f"Value {limit} must be 'int' type")
        if not isinstance(offset, int):
            raise ValueError(f"Value {offset} must be 'int' type")

        # if offset:
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.send_at.desc()) \
            .limit(limit).offset(offset).all()
        # else:
        #     messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.send_at.desc())\
        #         .limit(limit).all()

        return messages

    def get_by_chat_id1(self, chat_id: int):
        if not isinstance(chat_id, int):
            raise ValueError(f"Value {chat_id} must be 'int' type")

        # if offset:
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.send_at.desc()).all()
        # else:
        #     messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.send_at.desc())\
        #         .limit(limit).all()

        return messages

    def create(self, message: Message):
        if not isinstance(message, Message):
            raise ValueError(f"Value {message} must be 'Message' type")

        try:
            db.session.add(message)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return message.id

    def update(self, message_id: int, new_message: Message):
        if not isinstance(message_id, int):
            raise ValueError(f"Value {message_id} must be 'int' type")
        if not isinstance(new_message, Message):
            raise ValueError(f"Value {new_message} must be 'Message' type")

        message_to_update = Message.query.filter_by(id=message_id).first()
        if message_to_update is None:
            raise ValueError(f"Message with id={message_id} doesn't exist")

        # update params
        if new_message.text:
            message_to_update.text = new_message.text
        if new_message.sent_files:
            message_to_update.sent_files = new_message.sent_files

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return message_id
    
    def read_message(self, message_id: int):
        if not isinstance(message_id, int):
            raise ValueError(f"Value {message_id} must be 'int' type")

        message_to_make_read = Message.query.filter_by(id=message_id).first()
        if message_to_make_read is None:
            raise ValueError(f"Message with id={message_id} doesn't exist")

        message_to_make_read.is_read = True

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return message_id

    def delete(self, message_id):
        if not isinstance(message_id, int):
            raise ValueError(f"Value {message_id} must be 'int' type")

        message_to_delete = Message.query.filter_by(id=message_id).first()
        if message_to_delete is None:
            raise ValueError(f"Message with id={message_id} doesn't exist")

        try:
            db.session.delete(message_to_delete)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_unread_messages(self, user_id, chat_id):
        if not isinstance(user_id, int):
            raise ValueError(f"Value {user_id} must be 'int' type")
        if not isinstance(chat_id, int):
            raise ValueError(f"Value {chat_id} must be 'int' type")

        chat = Chat.query.filter_by(id=chat_id).first()
        chat_messages_ids = [m.id for m in chat.messages]

        try:
            db.session.execute(
                unread_messages.delete().where(
                    unread_messages.c.user_id == user_id and
                    unread_messages.c.message_id in chat_messages_ids
                )
            )

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


message_repo = MessageRepo()
