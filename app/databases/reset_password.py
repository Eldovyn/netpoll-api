from .database import Database
from ..models import ResetPasswordModel, UserModel
from ..database import db


class ResetPasswordDatabase(Database):
    @staticmethod
    async def insert(
        reset_password_id, user_id, token_email, token_web, expired_at, created_at
    ):
        if user := UserModel.query.filter(UserModel.user_id == user_id).first():
            if token := ResetPasswordModel.query.filter(
                ResetPasswordModel.user_id == user_id
            ).first():
                token.token_email = token_email
                token.token_web = token_web
                token.expired_at = expired_at
                token.updated_at = created_at
                db.session.commit()
                return token
            account_active = ResetPasswordModel(
                reset_password_id=reset_password_id,
                token_email=token_email,
                token_web=token_web,
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
        created_at = kwargs.get("created_at")
        if category == "reset_password":
            return ResetPasswordModel.query.filter(
                ResetPasswordModel.user_id == user_id
            ).first()
        if category == "reset_password_email":
            return ResetPasswordModel.query.filter(
                ResetPasswordModel.token_email == email_token,
                ResetPasswordModel.user_id == user_id,
            ).first()
        if category == "token_active":
            return ResetPasswordModel.query.filter(
                ResetPasswordModel.user_id == user_id,
            ).first()

    @staticmethod
    async def delete(category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "user_id":
            if token := ResetPasswordModel.query.filter(
                ResetPasswordModel.user_id == user_id
            ).first():
                db.session.delete(token)
                db.session.commit()

    @staticmethod
    async def update(category, **kwargs):
        user_id = kwargs.get("user_id")
        token_web = kwargs.get("token_web")
        token_email = kwargs.get("token_email")
        expired_at = kwargs.get("expired_at")
        updated_at = kwargs.get("updated_at")
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
        if category == "token_active":
            if user_token := ResetPasswordModel.query.filter(
                ResetPasswordModel.user_id == user_id
            ).first():
                user_token.token_web = token_web
                user_token.token_email = token_email
                user_token.expired_at = expired_at
                user_token.updated_at = updated_at
                db.session.commit()
                return user_token
