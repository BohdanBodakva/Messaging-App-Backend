import time

from flask import request, Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, JWTManager
from repositories.user_repo import user_repo
from werkzeug.security import generate_password_hash, check_password_hash
from models.db_models import User

auth_bp = Blueprint('auth_bp', __name__)

jwt = JWTManager()


@auth_bp.route('/login', methods=['POST'])
def login():
    request_body = request.get_json()

    print(request_body)

    if request_body:
        username = request_body.get('username')
        password = request_body.get('password')

        if all((username, password)):
            user = user_repo.get_by_username(username)

            if user:
                if check_password_hash(user.password, password):
                    access_token = create_access_token(identity=str(user.id))
                    refresh_token = create_refresh_token(identity=str(user.id))
                    return {
                        "message": "Login successful",
                        "user_id": user.id,
                        "access_token": access_token,
                        "refresh_token": refresh_token
                    }, 202
                else:
                    return {
                        "msg": f"Incorrect password",
                        "username": username
                    }, 404
            else:
                return {
                    "msg": f"User doesn't exist",
                    "username": username
                }, 404
        else:
            return {
                "msg", "Invalid request body"
            }, 400
    else:
        return {
            "msg", "Request body is absent"
        }, 400


@auth_bp.route('/signup', methods=['POST'])
def signup():
    request_body = request.get_json()

    if request_body:
        name = request_body.get('name')
        surname = request_body.get('surname')
        username = request_body.get('username')
        password = request_body.get('password')

        if all((name, surname, username, password)):
            user = user_repo.get_by_username(username)

            if not user:
                user = User(
                    name=name,
                    surname=surname,
                    username=username,
                    profile_photo_link=None,
                    password=generate_password_hash(password)
                )

                try:
                    user_repo.create(user)
                except Exception as e:
                    return {
                        "msg": repr(e)
                    }, 500

                return {
                    "msg": "Signup successful"
                }, 201
            else:
                return {
                    "msg": f"User already exists",
                    "username": username
                }, 409
        else:
            return {
                "msg", "Invalid request body"
            }, 400
    else:
        return {
            "msg", "Request body is absent"
        }, 400


@auth_bp.route("/refresh", methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)

    return {
        "access_token": access_token
    }, 200


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return {
        "msg": "Expired token"
    }, 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {
        "msg": "Invalid token"
    }, 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return {
        "msg": "Request does not contain token"
    }, 401
