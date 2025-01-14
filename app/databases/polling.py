from .database import Database
from ..models import PollingModel, AnswerModel, UserModel
from .. import db
from ..utils import generate_id
from sqlalchemy.orm import load_only
import difflib


class PollingDatabase(Database):
    @staticmethod
    async def insert(
        polling_id, user_id, title, answer, private, multi_choice, disable_comment
    ):
        if user := UserModel.query.filter(UserModel.user_id == user_id).first():
            polling = PollingModel(
                polling_id=polling_id,
                user_id=user_id,
                title=title,
            )
            polling.private = private
            polling.multi_choice = multi_choice
            polling.disable_comment = disable_comment
            bulk_answer = [
                AnswerModel(generate_id(), polling_id, user_id, item) for item in answer
            ]
            db.session.add(polling)
            db.session.add_all(bulk_answer)
            db.session.commit()
            return polling, bulk_answer

    @staticmethod
    async def get(category, **kwargs):
        user_id = kwargs.get("user_id")
        polling_id = kwargs.get("polling_id")
        title = kwargs.get("title")
        if category == "polling":
            return PollingModel.query.filter(
                PollingModel.polling_id == polling_id
            ).first()
        if category == "polling_user_title":
            pollings = (
                PollingModel.query.options(
                    load_only(
                        PollingModel.polling_id,
                        PollingModel.user_id,
                        PollingModel.title,
                        PollingModel.private,
                        PollingModel.multi_choice,
                        PollingModel.disable_comment,
                        PollingModel.created_at,
                        PollingModel.updated_at,
                    )
                )
                .filter(PollingModel.user_id == user_id)
                .all()
            )
            titles = [p.title for p in pollings]
            matches = difflib.get_close_matches(title, titles, n=5, cutoff=0.5)
            similar_pollings = (
                PollingModel.query.options(
                    load_only(
                        PollingModel.polling_id,
                        PollingModel.user_id,
                        PollingModel.title,
                        PollingModel.private,
                        PollingModel.multi_choice,
                        PollingModel.disable_comment,
                        PollingModel.created_at,
                        PollingModel.updated_at,
                    )
                )
                .filter(
                    PollingModel.user_id == user_id, PollingModel.title.in_(matches)
                )
                .all()
            )
            return similar_pollings
        if category == "polling_user":
            return (
                PollingModel.query.options(
                    load_only(
                        PollingModel.polling_id,
                        PollingModel.user_id,
                        PollingModel.title,
                        PollingModel.private,
                        PollingModel.multi_choice,
                        PollingModel.disable_comment,
                        PollingModel.created_at,
                        PollingModel.updated_at,
                    )
                )
                .filter(PollingModel.user_id == user_id)
                .all()
            )

    @staticmethod
    async def delete(category, **kwargs):
        pass

    @staticmethod
    async def update(category, **kwargs):
        pass
