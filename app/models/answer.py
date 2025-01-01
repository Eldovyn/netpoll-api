from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import db
import datetime


class AnswerModel(db.Model):
    __tablename__ = "answer"
    answer_id = Column(String, primary_key=True)
    polling_id = Column(String, ForeignKey("polling.polling_id", ondelete="CASCADE"))
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"))
    answer = Column(String, nullable=False)
    created_at = Column(
        Integer,
        nullable=False,
    )
    updated_at = Column(
        Integer,
        nullable=False,
    )
    user = relationship("UserModel", back_populates="answer")
    polling = relationship("PollingModel", back_populates="answers")

    def __init__(
        self,
        answer_id,
        polling_id,
        user_id,
        answer,
    ):
        self.answer_id = answer_id
        self.user_id = user_id
        self.polling_id = polling_id
        self.answer = answer
        self.created_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        self.updated_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    def __repr__(self):
        return f"<Answer {self.user_id!r}>"
