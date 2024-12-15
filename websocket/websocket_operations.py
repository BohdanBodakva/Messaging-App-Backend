from flask_socketio import SocketIO
from app import app
from common.env_vars import env_vars


socketio = SocketIO(app, cors_allowed_origins=env_vars['SOCKETIO_CORS_ALLOWED_ORIGINS'])

@socketio.on("register_user")
def register_user():
    pass