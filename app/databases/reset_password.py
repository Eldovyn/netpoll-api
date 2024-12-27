from .database import Database
from ..models import ResetPasswordModel, UserModel
from ..database import db


class ResetPasswordDatabase(Database):
    @staticmethod
    async def insert(account_active_id, user_id, token, expired_at, created_at):
        if user := UserModel.query.filter(UserModel.user_id == user_id).first():
            if token := ResetPasswordModel.query.filter(
                ResetPasswordModel.user_id == user_id
            ).first():
                token.token = (token,)
                token.expired_at = expired_at
                token.updated_at = created_at
                db.session.commit()
                return token
            account_active = ResetPasswordModel(
                account_active_id=account_active_id,
                token=token,
                expired_at=expired_at,
                created_at=created_at,
                updated_at=created_at,
                user_id=user_id,
            )
            db.session.add(account_active)
            db.session.commit()
            return account_active

    @staticmethod
    async def get(category, **kwargs):
        user_id = kwargs.get("user_id")
        web_token = kwargs.get("web_token")
        email_token = kwargs.get("email_token")
        if category == "account_active":
            if user := UserModel.query.filter(UserModel.user_id == user_id).first():
                return ResetPasswordModel.query.filter(
                    ResetPasswordModel.user_id == user.user_id
                ).first()
        if category == "account_active_email":
            if user := UserModel.query.filter(UserModel.user_id == user_id).first():
                return ResetPasswordModel.query.filter(
                    ResetPasswordModel.token == email_token,
                    ResetPasswordModel.user_id == user.user_id,
                ).first()

    @staticmethod
    async def delete(category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "user_id":
            if user_data := UserModel.objects(id=user_id).first():
                return ResetPasswordModel.objects(user=user_data).delete()

    @staticmethod
    async def update(category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "user_id":
            if user := UserModel.query.filter(UserModel.user_id == user_id).first():
                user.is_active = True
                db.session.commit()
                if token := ResetPasswordModel.query.filter(
                    ResetPasswordModel.user_id == user_id
                ).first():
                    db.session.delete(token)
                    db.session.commit()
                return user
