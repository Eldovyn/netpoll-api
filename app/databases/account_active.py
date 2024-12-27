from .database import Database
from ..models import AccountActiveModel, UserModel
from ..utils import DataNotFoundError
from ..database import db


class AccountActiveDatabase(Database):
    @staticmethod
    async def insert(
        account_active_id, user_id, email_token, web_token, expired_at, created_at
    ):
        if user := UserModel.query.filter(UserModel.user_id == user_id).first():
            if token := AccountActiveModel.query.filter(
                AccountActiveModel.user_id == user_id
            ).first():
                token.token_email = email_token
                token.token_web = web_token
                token.expired_at = expired_at
                token.updated_at = created_at
                db.session.commit()
                return token
            account_active = AccountActiveModel(
                account_active_id=account_active_id,
                token_email=email_token,
                token_web=web_token,
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
                return AccountActiveModel.query.filter(
                    AccountActiveModel.user_id == user.user_id
                ).first()
        if category == "account_active_email":
            if user := UserModel.query.filter(UserModel.user_id == user_id).first():
                return AccountActiveModel.query.filter(
                    AccountActiveModel.token_email == email_token,
                    AccountActiveModel.user_id == user.user_id,
                ).first()

    @staticmethod
    async def delete(category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "user_id":
            if user_data := UserModel.objects(id=user_id).first():
                return AccountActiveModel.objects(user=user_data).delete()

    @staticmethod
    async def update(category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "user_id":
            if user := UserModel.query.filter(UserModel.user_id == user_id).first():
                user.is_active = True
                db.session.commit()
                if token := AccountActiveModel.query.filter(
                    AccountActiveModel.user_id == user_id
                ).first():
                    db.session.delete(token)
                    db.session.commit()
                return user
