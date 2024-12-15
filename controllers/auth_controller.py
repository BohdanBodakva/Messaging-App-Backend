from auth.jwt_wrapper import token_required
from flask import request, jsonify, make_response, Blueprint
import jwt
from common.env_vars import env_vars
from repositories.user_repo import user_repo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models.db_models import User


auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    # return "it is login"
    request_body = request.get_json()

    username = request_body.get('username')
    password = request_body.get('password')

    if not request_body or not username or not password:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm="Login required"'}
        )

    user = user_repo.get_by_username(username)

    if not user:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm="User does not exist"'}
        )

    if check_password_hash(user.password, password):
        token = jwt.encode(
            {
                'public_id': user.id,
                'exp' : datetime.now() + timedelta(seconds=int(env_vars['JWT_EXPIRES_SEC']))
            }, 
            env_vars['FLASK_SECRET_KEY'],
            algorithms=['HS256']
        )
  
        return make_response(jsonify({'token' : token}), 201)

    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate' : 'Basic realm="Wrong Password"'}
    )


@auth_bp.route('/signup', methods=['POST'])
def signup():
    request_body = request.get_json()

    name = request_body.get('name')
    surname = request_body.get('surname')
    username = request_body.get('username')
    password = request_body.get('password')
    profile_photo_link = request_body.get('profile_photo_link')

    user = user_repo.get_by_username(username)
    if not user:
        user = User(
            name=name,
            surname=surname,
            username=username,
            profile_photo_link=profile_photo_link,
            password=generate_password_hash(password)
        )

        # try:
        user_repo.create(user)
        # except Exception as e:
        #     return make_response(
        #         e, 
        #         500
        #     )

        return make_response('Successfully registered.', 201)
    else:
        return make_response('User already exists. Please Log in.', 202)