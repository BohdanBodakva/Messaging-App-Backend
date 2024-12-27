from repositories.base_repo import BaseCrudRepo
from models.db_models import db, User
from datetime import datetime


class UserRepo(BaseCrudRepo):
    def get_all(self):
        all_users = User.query.all()
        return all_users

    def get_by_id(self, user_id: int):
        if not isinstance(user_id, int):
            raise ValueError(f"Value {user_id} must be 'int' type")

        user = User.query.filter_by(id=user_id).first()

        return user

    def get_by_username(self, user_username: str):
        if not isinstance(user_username, str):
            raise ValueError(f"Value {user_username} must be 'str' type")

        user = User.query.filter_by(username=user_username).first()

        return user

    def create(self, user: User):
        if not isinstance(user, User):
            raise ValueError(f"Value {user} must be 'User' type")

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return user.id

    def update(self, user_id: int, new_user: User):
        if not isinstance(user_id, int):
            raise ValueError(f"Value {user_id} must be 'int' type")
        if not isinstance(new_user, User):
            raise ValueError(f"Value {new_user} must be 'User' type")

        user_to_update = User.query.filter_by(id=item_id).first()
        if user_to_update is None:
            raise ValueError(f"User with id={item_id} doesn't exist")

        # update params
        if new_user.username:
            user_to_update.username = new_user.username
        if new_user.profile_photo_link:
            user_to_update.profile_photo_link = new_user.profile_photo_link
        if new_user.name:
            user_to_update.name = new_user.name
        if new_user.surname:
            user_to_update.surname = new_user.surname

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return user_id

    def update_last_seen_by_id(self, user_id: int, new_last_seen: datetime):
        if not isinstance(user_id, int):
            raise ValueError(f"Value {user_id} must be 'int' type")
        if not isinstance(new_last_seen, datetime.datetime):
            raise ValueError(f"'last_seen' must be 'datetime.datetime' type")

        user_to_update = User.query.filter_by(id=user_id).first()
        if user_to_update is None:
            raise ValueError(f"User with id={user_id} doesn't exist")

        # update last_seen
        user_to_update.last_seen = new_last_seen

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return user_id

    def update_password_by_id(self, user_id: int, new_password: str):
        if not isinstance(user_id, int):
            raise ValueError(f"Value {user_id} must be 'int' type")
        if not isinstance(new_password, str):
            raise ValueError(f"Password must be 'str' type")
        if not new_password:
            raise ValueError("Password is empty string")

        item_to_update = User.query.filter_by(id=user_id).first()
        if not item_to_update:
            raise ValueError(f"User with id={user_id} doesn't exist")
        
        # update password
        item_to_update.password = new_password
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return user_id

    def delete(self, user_id):
        if not isinstance(user_id, int):
            raise ValueError(f"Value {user_id} must be 'int' type")

        user_to_delete = User.query.filter_by(id=user_id).first()
        if user_to_delete is None:
            raise ValueError(f"User with id={user_id} doesn't exist")

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

user_repo = UserRepo()
