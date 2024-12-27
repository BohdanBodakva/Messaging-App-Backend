# import eventlet
# eventlet.monkey_patch()
from controllers.chat_controller import chats_bp
from websocket.websocket_operations import socketio

from flask import Flask, Blueprint, jsonify, make_response

# import redis

from repositories.chat_repo import chat_repo

from common.env_vars import env_vars
from models.db_models import db
from auth.auth_controller import auth_bp
from controllers.user_controller import users_bp
from models.db_models import User, Chat, Message
from auth.jwt_wrapper import token_required

from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash

app = Flask(__name__)


CORS(
    app,
    # origins=env_vars['SOCKETIO_CORS_ALLOWED_ORIGINS']
)

# @app.after_request
# def add_cors_headers(response):
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
#     response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, x-access-token'
#     return response


app.config['SECRET_KEY'] = env_vars['FLASK_SECRET_KEY']
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{env_vars['DB_USER']}:{env_vars['DB_PASSWORD']}@{env_vars['DB_HOSTNAME']}/{env_vars['DB_NAME']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

socketio.init_app(
    app,
    cors_allowed_origins=env_vars['SOCKETIO_CORS_ALLOWED_ORIGINS'],
    # message_queue=f"redis://{env_vars['REDIS_ADDRESS']}:{env_vars['REDIS_PORT']}"
)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(chats_bp, url_prefix='/chats')


@app.route("/protected", methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({'current_user': current_user.serialize()})


@app.route("/chat/<int:chat_id>", methods=['GET'])
@token_required
def get_chat(current_user, chat_id):
    chat = chat_repo.get_by_id(chat_id)

    return jsonify({'chat': chat.serialize()})


@app.route("/sss", methods=['GET'])
def get_chats():
    return "Hello !!!"


@app.route("/hi")
def hello_world1(current_user):
    return "Hello !!!!!!!1"


@app.route("/")
def hello_world():
    with app.app_context():
        db.create_all()

    user1 = User(
        username='a',
        name='User 1',
        password=generate_password_hash('a')
    )
    user2 = User(
        username='b',
        name='User 2',
        password=generate_password_hash('b')
    )
    user3 = User(
        username='c',
        name='User 3',
        password=generate_password_hash('c')
    )
    user4 = User(
        username='d',
        name='User 4',
        password=generate_password_hash('d')
    )

    chat1 = Chat(
        name='chat 1',
        users=[user1, user2]
    )
    chat2 = Chat(
        name='chat 2',
        users=[user1, user3]
    )
    chat3 = Chat(
        name='chat 3',
        users=[user1, user4]
    )
    chat4 = Chat(
        name='chat 4',
        users=[user2, user3]
    )
    chat5 = Chat(
        name='chat 5',
        users=[user2, user4]
    )
    chat6 = Chat(
        name='chat 6',
        users=[user3, user4]
    )

    message1 = Message(
        text="some msg 1",
        chat_id=1,
        user_id=1
    )

    db.session.add_all([user1, user2, user3, user4])
    db.session.commit()
    db.session.add_all([chat1, chat2, chat3, chat4, chat5, chat6])
    db.session.commit()
    db.session.add_all([message1])
    db.session.commit()
    all_users = User.query.all()
    return jsonify([user.serialize() for user in all_users])
    # return 'hello world'


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    socketio.run(app,
                 allow_unsafe_werkzeug=True,
                 debug=True,
                 port=int(env_vars['SOCKETIO_RUN_PORT']),
                 host=env_vars['SOCKETIO_RUN_HOST_ADDRESS']
                 )
