from .database import Database
from ..models import UserModel
from ..database import db


class UserDatabase(Database):
    @staticmethod
    async def insert(user_id, email, username, password, avatar):
        with open(avatar, "rb") as f:
            avatar = f.read()
        user = UserModel(
            email=email,
            username=username,
            password=password,
            avatar=avatar,
            user_id=user_id,
        )
        db.session.add(user)
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
        pass
