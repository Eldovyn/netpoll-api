from .database import Database
from ..models import TokenBlocklistModel
from ..database import db


class TokenBlacklistDatabase(Database):
    @staticmethod
    async def insert(token_id, jti, created_at):
        token = TokenBlocklistModel(
            token_id=token_id,
            jti=jti,
            created_at=created_at,
        )
        db.session.add(token)
        db.session.commit()
        return token

    @staticmethod
    async def get(category, **kwargs):
        pass

    @staticmethod
    async def delete(category, **kwargs):
        pass

    @staticmethod
    async def update(category, **kwargs):
        pass
