from flask import Flask, jsonify
from flask_socketio import SocketIO
from common.env_vars import env_vars
from models.db_models import db, User, Chat, Message



app = Flask(__name__)
app.config['SECRET_KEY'] = env_vars['FLASK_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{env_vars['DB_USER']}:{env_vars['DB_PASSWORD']}@{env_vars['DB_HOSTNAME']}/{env_vars['DB_NAME']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

socketio = SocketIO(app, cors_allowed_origins=env_vars['SOCKETIO_CORS_ALLOWED_ORIGINS'])



@app.route("/")
def hello_world():
    with app.app_context():
        db.drop_all()
        db.create_all()

    user1 = User(
        username='user1',
        name='User 1',
        password='xxx'
    )

    user2 = User(
        username='user2',
        name='User 2',
        password='xxx'
    )

    chat = Chat(
        name='chat 1',
        users=[user1, user2]
    )

    message1 = Message(
        text="some msg 1",
        chat_id=1
    )

    db.session.add_all([user1, user2])
    db.session.add_all([chat])
    db.session.add_all([message1])
    db.session.commit()

    all_users = Chat.query.all()

    return jsonify([user.serialize() for user in all_users])


if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    socketio.run(app, 
                 debug=True, 
                 port=env_vars['SOCKETIO_RUN_PORT'], 
                 host=env_vars['SOCKETIO_RUN_HOST_ADDRESS']
                 )
