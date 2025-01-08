from sqlalchemy import Column, String, Integer, ForeignKey
from ..database import db
from sqlalchemy.orm import relationship
import datetime


class UserAvatarModel(db.Model):
    __tablename__ = "user_avatar"

    avatar_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"))
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=False)
    avatar = Column(String, nullable=False)
    user = relationship("UserModel", back_populates="user_avatar")

    def __init__(self, avatar_id, user_id, avatar):
        self.avatar_id = avatar_id
        self.user_id = user_id
        self.created_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        self.updated_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        self.avatar = avatar

    def __repr__(self):
        return f"<TokenBlocklist {self.jti!r}>"
