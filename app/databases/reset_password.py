from .database import Database
from ..models import ResetPasswordModel, UserModel
from mongoengine import errors
import datetime
from ..utils import DataNotFoundError, TokenResetPassword


class ResetPasswordDatabase(Database):
    @staticmethod
    async def insert(user_id, token, expired_at):
        if user_data := UserModel.objects(id=user_id).first():
            if token_data := ResetPasswordModel.objects(user=user_data).first():
                created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
                expired_at = created_at + 300
                token = await TokenResetPassword.insert(
                    f"{user_data.id}", int(created_at)
                )
                token_data.expired_at = expired_at
                token_data.token = f"{token}"
                token_data.save()
                return token_data
            reset_password = ResetPasswordModel(
                user=user_data, token=token, expired_at=expired_at
            )
            reset_password.save()
            return reset_password
        raise DataNotFoundError("user not found")

    @staticmethod
    async def get(category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "user_id":
            if user_data := UserModel.objects(id=user_id).first():
                return ResetPasswordModel.objects(user=user_data).first()

    @staticmethod
    async def delete(category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "user_id":
            if user_data := UserModel.objects(id=user_id).first():
                return ResetPasswordModel.objects(user=user_data).delete()

    @staticmethod
    async def update():
        pass
