from repositories.base_repo import BaseCrudRepo
from models.db_models import db, Message
from datetime import datetime


class MessageRepo(BaseCrudRepo):
    def get_all(self):
        all_messages = Message.query.all()
        return all_messages

    def get_by_id(self, message_id: int):
        if not isinstance(message_id, int):
            raise ValueError(f"Value {message_id} must be 'int' type")

        message = Message.query.filter_by(id=message_id).first()

        return message

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


message_repo = MessageRepo()
