from flask import Flask, Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from common.env_vars import env_vars
from models.db_models import db
from controllers.auth_controller import auth_bp
from models.db_models import User, Chat, Message
from auth.jwt_wrapper import token_required


app = Flask(__name__)

app.config['SECRET_KEY'] = env_vars['FLASK_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{env_vars['DB_USER']}:{env_vars['DB_PASSWORD']}@{env_vars['DB_HOSTNAME']}/{env_vars['DB_NAME']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')



@app.route("/protected")
@token_required
def protected_route(current_user):
    return f'hello from protected route\ncurrent user: {current_user}'


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
    all_users = User.query.all()
    return jsonify([user.serialize() for user in all_users])
    # return 'hello world'


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    from websocket.websocket_operations import socketio
    socketio.run(app, 
                 debug=True, 
                 port=int(env_vars['SOCKETIO_RUN_PORT']), 
                 host=env_vars['SOCKETIO_RUN_HOST_ADDRESS']
                 )
