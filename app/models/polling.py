from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import db
import datetime


class PollingModel(db.Model):
    __tablename__ = "polling"
    polling_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    private = Column(Boolean, nullable=False, default=False)
    multi_choice = Column(Boolean, nullable=False, default=False)
    disable_comment = Column(Boolean, nullable=False, default=False)
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=False)
    user = relationship("UserModel", back_populates="polling")

    answers = relationship("AnswerModel", back_populates="polling", lazy="joined")

    def __init__(self, polling_id, user_id, title):
        self.polling_id = polling_id
        self.user_id = user_id
        self.title = title
        self.created_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        self.updated_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    def __repr__(self):
        return f"<Polling {self.user_id!r}>"
