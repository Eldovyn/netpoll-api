from .database import Database
from ..models import UserModel, UserAvatarModel
from ..database import db


class UserDatabase(Database):
    @staticmethod
    async def insert(user_id, email, username, password, avatar_image, avatar_id):
        with open(avatar_image, "rb") as f:
            avatar = f.read()
        user = UserModel(
            email=email,
            username=username,
            password=password,
            user_id=user_id,
        )
        avatar = UserAvatarModel(avatar_id, user_id, avatar)
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
        if category == "password":
            if user := UserModel.query.filter(UserModel.user_id == user_id).first():
                user.password = new_password
                db.session.commit()
                return user
