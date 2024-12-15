from repositories.base_repo import BaseCrudRepo
from models.db_models import db, User
from datetime import datetime

class UserRepo(BaseCrudRepo):
    def get_all(self):
        all_users = User.query.all()
        return all_users
    
    def get_by_id(self, item_id):
        if not isinstance(item_id, int):
            raise ValueError(f"Value {item_id} must be 'int' type")
        
        user = User.query.filter_by(id=item_id).first()
        if user:
            user = user.serialize()

        return user
    
    def get_by_username(self, item_username):
        if not isinstance(item_username, str):
            raise ValueError(f"Value {item_username} must be 'str' type")
        
        user = User.query.filter_by(username=item_username).first()
        if user:
            user = user.serialize()

        return user
    
    def create(self, item):
        if not isinstance(item, User):
            raise ValueError(f"Value {item} must be 'User' type")
        
        try:
            db.session.add(item)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        # finally:
        #     db.session.close()

        added_user = User.query.filter_by(username=item.username).first()
        if user:
            user = user.serialize()

        return added_user
    
    def update(self, item_id, new_item):
        if not isinstance(item_id, int):
            raise ValueError(f"Value {item_id} must be 'int' type")
        elif not isinstance(new_item, User):
            raise ValueError(f"Value {new_item} must be 'User' type")

        item_to_update = User.query.filter_by(id=item_id).first()
        if not item_to_update:
            raise ValueError(f"User with id={item_id} doesn't exist")
        
        # update params
        if new_item.username:
            item_to_update.username = new_item.username
        if new_item.profile_photo_link:
            item_to_update.profile_photo_link = new_item.profile_photo_link
        if new_item.name:
            item_to_update.name = new_item.name
        if new_item.surname:
            item_to_update.surname = new_item.surname
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        # finally:
        #     db.session.close()

        updated_user = User.query.filter_by(id=item_id).first()
        if user:
            user = user.serialize()

        return updated_user
    
    def update_by_username(self, item_username, new_item):
        if not isinstance(item_username, str):
            raise ValueError(f"Value {item_username} must be 'str' type")
        elif not isinstance(new_item, User):
            raise ValueError(f"Value {new_item} must be 'User' type")

        item_to_update = User.query.filter_by(username=item_username).first()
        if not item_to_update:
            raise ValueError(f"User with username={item_username} doesn't exist")
        
        # update params
        if new_item.username:
            item_to_update.username = new_item.username
        if new_item.profile_photo_link:
            item_to_update.profile_photo_link = new_item.profile_photo_link
        if new_item.name:
            item_to_update.name = new_item.name
        if new_item.surname:
            item_to_update.surname = new_item.surname
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        # finally:
        #     db.session.close()

        updated_user = User.query.filter_by(username=new_item.username).first()
        if user:
            user = user.serialize()

        return updated_user
    
    def update_last_seen_by_id(self, item_id, new_last_seen):
        if not isinstance(item_id, int):
            raise ValueError(f"Value {item_id} must be 'int' type")
        elif not isinstance(new_last_seen, datetime.datetime):
            raise ValueError(f"'last_seen' must be 'datetime.datetime' type")

        item_to_update = User.query.filter_by(id=item_id).first()
        if not item_to_update:
            raise ValueError(f"User with id={item_id} doesn't exist")
        
        # update password
        item_to_update.last_seen = new_last_seen
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        # finally:
        #     db.session.close()

        updated_user = User.query.filter_by(id=item_id).first()
        if user:
            user = user.serialize()

        return updated_user
    
    def update_last_seen_by_username(self, item_username, new_last_seen):
        if not isinstance(item_username, str):
            raise ValueError(f"Value {item_username} must be 'str' type")
        elif not isinstance(new_last_seen, datetime.datetime):
            raise ValueError(f"'last_seen' must be 'datetime.datetime' type")

        item_to_update = User.query.filter_by(username=item_username).first()
        if not item_to_update:
            raise ValueError(f"User with username={item_username} doesn't exist")
        
        # update password
        item_to_update.last_seen = new_last_seen
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        # finally:
        #     db.session.close()

        updated_user = User.query.filter_by(username=item_username).first()
        if user:
            user = user.serialize()

        return updated_user
    
    def update_password_by_id(self, item_id, new_password):
        if not isinstance(item_id, int):
            raise ValueError(f"Value {item_id} must be 'int' type")
        elif not isinstance(new_password, str):
            raise ValueError(f"Password must be 'str' type")
        elif not new_password:
            raise ValueError("Password is empty string")

        item_to_update = User.query.filter_by(id=item_id).first()
        if not item_to_update:
            raise ValueError(f"User with id={item_id} doesn't exist")
        
        # update password
        item_to_update.password = new_password
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        # finally:
        #     db.session.close()

        updated_user = User.query.filter_by(id=item_id).first()
        if user:
            user = user.serialize()

        return updated_user
    
    def update_password_by_username(self, item_username, new_password):
        if not isinstance(item_username, str):
            raise ValueError(f"Value {item_username} must be 'str' type")
        elif not isinstance(new_password, str):
            raise ValueError(f"Password must be 'str' type")
        elif not new_password:
            raise ValueError("Password is empty string")

        item_to_update = User.query.filter_by(username=item_username).first()
        if not item_to_update:
            raise ValueError(f"User with username={item_username} doesn't exist")
        
        # update password
        item_to_update.password = new_password
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        # finally:
        #     db.session.close()

        updated_user = User.query.filter_by(username=item_username).first()
        if user:
            user = user.serialize()

        return updated_user
    
    def delete(self, item_id):
        if not isinstance(item_id, int):
            raise ValueError(f"Value {item_id} must be 'int' type")
        
        item_to_delete = User.query.filter_by(id=item_id).first()
        if not item_to_delete:
            raise ValueError(f"User with id={item_id} doesn't exist")
        
        try:
            db.session.delete(item_to_delete)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        # finally:
        #     db.session.close()

    def delete_by_username(self, item_username):
        if not isinstance(item_username, str):
            raise ValueError(f"Value {item_username} must be 'str' type")
        
        item_to_delete = User.query.filter_by(username=item_username).first()
        if not item_to_delete:
            raise ValueError(f"User with username={item_username} doesn't exist")
        
        try:
            db.session.delete(item_to_delete)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        # finally:
        #     db.session.close()


user_repo = UserRepo()
