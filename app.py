from controllers.chat_controller import chats_bp
from websocket.websocket_operations import socketio
from flask import Flask
# import redis
from common.env_vars import env_vars
from models.db_models import db
from auth.auth_controller import auth_bp, jwt
from controllers.user_controller import users_bp
from flask_cors import CORS
import datetime
from werkzeug.security import generate_password_hash
from models.db_models import User, SentFile, Message, Chat

# Create app object
app = Flask(__name__)

# App database config
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{env_vars['DB_USER']}:{env_vars['DB_PASSWORD']}" \
                                        f"@{env_vars['DB_HOSTNAME']}/{env_vars['DB_NAME']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# App JWT config
app.config['SECRET_KEY'] = env_vars['FLASK_SECRET_KEY']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(seconds=int(env_vars['ACCESS_TOKEN_EXPIRES_SEC']))
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(seconds=int(env_vars['REFRESH_TOKEN_EXPIRES_SEC']))

# Database init
db.init_app(app)

# JWT init
jwt.init_app(app)

# CORS config
CORS(
    app,
    origins=env_vars['SOCKETIO_CORS_ALLOWED_ORIGINS']
)

# Socketio init
socketio.init_app(
    app,
    cors_allowed_origins=env_vars['SOCKETIO_CORS_ALLOWED_ORIGINS'],
    # message_queue=f"redis://{env_vars['REDIS_ADDRESS']}:{env_vars['REDIS_PORT']}"
)


@app.route("/a", methods=["GET"])
def get_from_db2():
    user = User.query.filter_by(id=1).first()
    chat = Chat.query.filter_by(id=1).first()

    user.chats.remove(chat)

    db.session.commit()

    return "Yes"



@app.route("/g", methods=["GET"])
def get_from_db():
    result = User.query.all()

    result = [x.serialize(include_chats=True) for x in result]

    return result


@app.route("/fill", methods=["GET"])
def fill_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

    user1 = User(
        name="User",
        surname="1",
        username="user_1",
        password=generate_password_hash("1"),
    )
    user2 = User(
        name="User",
        surname="2",
        username="user_2",
        password=generate_password_hash("2"),
    )
    user3 = User(
        name="User",
        surname="3",
        username="user_3",
        password=generate_password_hash("3")
    )

    db.session.add_all([user1, user2, user3])
    db.session.commit()




    chat1 = Chat(
        users=[user1, user2]
    )
    chat2 = Chat(
        users=[user1, user3]
    )
    chat3 = Chat(
        users=[user2, user3]
    )

    group1 = Chat(
        users=[user1, user2, user3],
        is_group=True,
        admin_id=1
    )

    m1 = Message(
        text="Hello",
        user_id=1,
        chat_id=1,
        users_that_unread=[user2]
    )
    file1 = SentFile(
        file_link="some-file-link-1",
        message_id=1
    )
    file2 = SentFile(
        file_link="some-file-link-2",
        message_id=1
    )


    m2 = Message(
        text="Hi",
        user_id=2,
        chat_id=1
    )

    m3 = Message(
        text="hi 1",
        user_id=1,
        chat_id=4
    )
    m4 = Message(
        text="Hi 2",
        user_id=2,
        chat_id=4
    )
    m5 = Message(
        text="Hi 3",
        user_id=3,
        chat_id=4
    )

    m6 = Message(
        text="Hi 3",
        user_id=2,
        chat_id=1,
        send_at=datetime.datetime.strptime('2/1/2025 10:10:10', '%d/%m/%Y %H:%M:%S')
    )

    m7 = Message(
        text="Hi 3",
        user_id=2,
        chat_id=1,
        send_at=datetime.datetime.strptime('1/1/2025 10:10:10', '%d/%m/%Y %H:%M:%S')
    )
    m8 = Message(
        text="Hi 3",
        user_id=2,
        chat_id=1,
        send_at=datetime.datetime.strptime('31/12/2024 10:10:10', '%d/%m/%Y %H:%M:%S')
    )
    m9 = Message(
        text="Hi 3sadasdsaddsadasd",
        user_id=2,
        chat_id=1,
        send_at=datetime.datetime.strptime('1/1/2025 10:11:12', '%d/%m/%Y %H:%M:%S')
    )






    db.session.add_all([chat1, chat2, chat3])
    db.session.add_all([group1])
    db.session.add_all([m1, m2, m3, m4, m5, m6, m7, m8, m9])
    db.session.add_all([file1, file2])
    db.session.commit()

    return "Success"


# Registering blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(chats_bp, url_prefix='/chats')

# Run app
if __name__ == '__main__':
    socketio.run(app,
                 allow_unsafe_werkzeug=True,
                 debug=True,
                 port=int(env_vars['SOCKETIO_RUN_PORT']),
                 host=env_vars['SOCKETIO_APP_RUN_HOST_ADDRESS']
                 )
