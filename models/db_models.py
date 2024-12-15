from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


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

    def __repr__(self):
        return f"<User {self.id}: '{self.username}'>"
    
    def serialize(self, include_chats=True):
        user = {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "surname": self.surname,
            "last_seen": self.last_seen,
            "profile_photo_link": self.profile_photo_link
            }
        if include_chats:
            user["chats"] = [chat.serialize() for chat in self.chats]

        return user
    

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    file_link = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)

    def __repr__(self):
        return f"<Message {self.id}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "text": self.text,
            "file_link": self.file_link,
            "created_at": self.created_at,
            "is_read": self.is_read,
            "chat": self.chat_id
            }


class Chat(db.Model):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    name = db.Column(db.String(100), default="unnamed chat")
    chat_photo_link = db.Column(db.Text, nullable=False, default="")
    users = db.relationship('User', secondary=user_chat, back_populates=__tablename__, lazy='joined')
    messages = db.relationship('Message', backref=__tablename__, lazy='joined')

    def __repr__(self):
        return f"<Chat {self.id}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "chat_photo_link": self.chat_photo_link,
            "created_at": self.created_at,
            "users": [user.serialize(include_chats=False) for user in self.users],
            "messages": [message.serialize() for message in self.messages]
            }