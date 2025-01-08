from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import validates

db = SQLAlchemy()

user_chat = db.Table('user_chat',
                     db.Column(
                         'user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True
                     ),
                     db.Column(
                         'chat_id', db.Integer, db.ForeignKey('chats.id', ondelete='CASCADE'), primary_key=True
                     ))

unread_messages = db.Table('unread_messages',
                           db.Column(
                               'user_id', db.Integer,
                               db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True
                           ),
                           db.Column(
                               'message_id', db.Integer,
                               db.ForeignKey('messages.id', ondelete='CASCADE'), primary_key=True
                           ))


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    profile_photo_link = db.Column(db.Text, nullable=False, default="")
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100))
    password = db.Column(db.Text, nullable=False)
    last_seen = db.Column(db.DateTime)
    chats = db.relationship('Chat', secondary=user_chat, back_populates=__tablename__, lazy='joined')
    unread_messages = db.relationship(
        'Message', secondary=unread_messages, back_populates="users_that_unread", lazy='joined'
    )

    @validates("username", "password", "name")
    def validate_id(self, key, value):
        if not isinstance(value, str):
            raise ValueError(f"User: {key} must be 'str' type")
        if not value:
            raise ValueError(f"User: {key} cannot be empty string")
        return value

    def __repr__(self):
        return f"<User {self.id}: '{self.username}'>"

    def serialize_id(self):
        return {"id": self.id}

    def serialize(self, include_chats=False, include_last_message=True, include_messages=False):
        user = {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "surname": self.surname,
            "profile_photo_link": self.profile_photo_link,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "unread_messages": [message.serialize() for message in self.unread_messages]
        }
        if include_chats:
            user["chats"] = [
                chat.serialize(
                    include_last_message=include_last_message, include_messages=include_messages
                ) for chat in self.chats
            ]

        return user


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    sent_files = db.relationship('SentFile', backref=__tablename__, lazy='joined')
    send_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    users_that_unread = db.relationship('User', secondary=unread_messages, back_populates="unread_messages", lazy='joined')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id', ondelete='SET NULL'))

    @validates("text")
    def validate_id(self, key, value):
        if not isinstance(value, str):
            raise ValueError(f"Message: {key} must be 'str' type")
        if not value:
            raise ValueError(f"Message: {key} cannot be empty string")
        return value

    def __repr__(self):
        return f"<Message {self.id}>"

    def serialize(self, include_files=True):
        message = {
            "id": self.id,
            "text": self.text,
            "send_at": self.send_at.isoformat(),
            "users_that_unread": [user.serialize_id() for user in self.users_that_unread],
            "user_id": self.user_id,
            "chat_id": self.chat_id
        }
        if include_files:
            message["sent_files"] = [sent_file.serialize() for sent_file in self.sent_files]

        return message


class SentFile(db.Model):
    __tablename__ = 'sent_files'

    id = db.Column(db.Integer, primary_key=True)
    file_link = db.Column(db.Text, nullable=False, default="")
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id', ondelete='CASCADE'))

    @validates("file_link")
    def validate_id(self, key, value):
        if not isinstance(value, str):
            raise ValueError(f"SentFile: {key} must be 'str' type")
        if not value:
            raise ValueError(f"SentFile: {key} cannot be empty string")
        return value

    def __repr__(self):
        return f"<SentFile {self.id}>"

    def serialize(self):
        return {
            "id": self.id,
            "file_link": self.file_link,
            "message_id": self.message_id
        }


class Chat(db.Model):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    users = db.relationship('User', secondary=user_chat, back_populates=__tablename__, lazy='joined')
    chat_photo_link = db.Column(db.Text, nullable=True)
    is_group = db.Column(db.Boolean, nullable=False, default=False)
    messages = db.relationship('Message', backref=__tablename__, lazy='joined')

    def __repr__(self):
        return f"<Chat {self.id}>"

    def serialize(self, include_last_message=True, include_messages=False):
        chat = {
            "id": self.id,
            "name": self.name,
            "chat_photo_link": self.chat_photo_link,
            "is_group": self.is_group,
            "created_at": self.created_at.isoformat(),
            "admin": self.admin_id,
            "users": [user.serialize(include_chats=False) for user in self.users]
        }
        if include_last_message:
            last_message = Message.query.filter_by(chat_id=self.id).order_by(Message.id.desc()).first()

            chat["messages"] = [last_message.serialize()] if last_message else []

        elif include_messages:
            chat["messages"] = [message.serialize() for message in self.messages]

        return chat
