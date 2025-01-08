from .database import Database
from ..models import UserModel, UserAvatarModel
from ..database import db


class UserDatabase(Database):
    @staticmethod
    async def insert(user_id, email, username, password, avatar_id, avatar):
        user = UserModel(
            email=email,
            username=username,
            password=password,
            user_id=user_id,
        )
        avatar = UserAvatarModel(user_id=user_id, avatar=avatar, avatar_id=avatar_id)
        db.session.add(user)
        db.session.add(avatar)
        db.session.commit()
        return user

    @staticmethod
    async def get(category, **kwargs):
        email = kwargs.get("email")
        user_id = kwargs.get("user_id")
        if category == "email":
            return UserModel.query.filter(UserModel.email == email).first()
        if category == "user_id":
            return UserModel.query.filter(UserModel.user_id == user_id).first()

    @staticmethod
    async def delete():
        pass

    @staticmethod
    async def update(category, **kwargs):
        user_id = kwargs.get("user_id")
        new_password = kwargs.get("new_password")
        created_at = kwargs.get("created_at")
        if category == "password":
            if user := UserModel.query.filter(UserModel.user_id == user_id).first():
                user.password = new_password
                user.updated_at = created_at
                db.session.commit()
                return user
