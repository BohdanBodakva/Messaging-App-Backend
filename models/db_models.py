from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import validates

db = SQLAlchemy()

user_chat = db.Table('user_chat',
                     db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                     db.Column('chat_id', db.Integer, db.ForeignKey('chats.id'), primary_key=True)
                     )


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    profile_photo_link = db.Column(db.Text, nullable=False, default="")
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100))
    last_seen = db.Column(db.DateTime, nullable=False, default=datetime.now())
    password = db.Column(db.Text, nullable=False)
    chats = db.relationship('Chat', secondary=user_chat, back_populates=__tablename__, lazy='joined')

    @validates("username", "password", "name")
    def validate_id(self, key, value):
        if not isinstance(value, str):
            raise ValueError(f"User: {key} must be 'str' type")
        if not value:
            raise ValueError(f"User: {key} cannot be empty string")
        return value

    def __repr__(self):
        return f"<User {self.id}: '{self.username}'>"

    def serialize(self, include_chats=False):
        user = {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "surname": self.surname,
            "last_seen": self.last_seen,
            "profile_photo_link": self.profile_photo_link
        }
        if include_chats:
            user["chats"] = [chat.serialize(include_messages=False) for chat in self.chats]

        return user


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    sent_files = db.relationship('SentFile', backref=__tablename__, lazy='joined')
    send_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)

    @validates("text")
    def validate_id(self, key, value):
        if not isinstance(value, str):
            raise ValueError(f"Message: {key} must be 'str' type")
        if not value:
            raise ValueError(f"Message: {key} cannot be empty string")
        return value

    def __repr__(self):
        return f"<Message {self.id}>"

    def serialize(self):
        return {
            "id": self.id,
            "text": self.text,
            "sent_files": [sent_file.serialize() for sent_file in self.sent_files],
            "send_at": self.send_at,
            "is_read": self.is_read,
            "user_id": self.user_id,
            "chat": self.chat_id
        }


class SentFile(db.Model):
    __tablename__ = 'sent_files'

    id = db.Column(db.Integer, primary_key=True)
    file_link = db.Column(db.Text, nullable=False, default="")
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)

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
            "file_link": self.file_link
        }


class Chat(db.Model):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="unnamed chat")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    users = db.relationship('User', secondary=user_chat, back_populates=__tablename__, lazy='joined')
    chat_photo_link = db.Column(db.Text, nullable=True)
    is_group = db.Column(db.Boolean, nullable=False, default=False)
    messages = db.relationship('Message', backref=__tablename__, lazy='joined')

    def __repr__(self):
        return f"<Chat {self.id}>"

    def serialize(self, include_messages=False):
        chat = {
            "id": self.id,
            "name": self.name,
            "chat_photo_link": self.chat_photo_link,
            "is_group": self.is_group,
            "created_at": self.created_at,
            "users": [user.serialize(include_chats=False) for user in self.users],
        }
        if include_messages:
            chat["messages"] = [message.serialize() for message in self.messages]

        return chat
