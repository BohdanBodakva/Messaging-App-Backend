from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from third_party.env_vars import env_vars

app = Flask(__name__)
app.config['SECRET_KEY'] = env_vars['FLASK_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{env_vars['DB_USER']}:{env_vars['DB_PASSWORD']}@hostname/{env_vars['DB_NAME']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
socketio = SocketIO(app, cors_allowed_origins=env_vars['SOCKETIO_CORS_ALLOWED_ORIGINS'])

@app.route("/")
def hello_world():
    return 'hello world'

if __name__ == '__main__':
    socketio.run(app, 
                 debug=True, 
                 port=env_vars['SOCKETIO_RUN_PORT'], 
                 host=env_vars['SOCKETIO_RUN_HOST_ADDRESS']
                 )


