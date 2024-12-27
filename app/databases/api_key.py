from .database import Database
from ..models import ApiKeyModel, UserModel
import datetime


class ApiKeyDatabase(Database):
    @staticmethod
    async def insert():
        pass

    @staticmethod
    async def get(category, **kwargs):
        user_id = kwargs.get("user_id")

    @staticmethod
    async def delete(category, **kwargs):
        pass

    @staticmethod
    async def update(category, **kwargs):
        pass
