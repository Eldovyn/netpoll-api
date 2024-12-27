from sqlalchemy import Column, String, Integer, LargeBinary, Boolean
from ..database import db
from sqlalchemy.orm import relationship
import datetime


class UserModel(db.Model):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    username = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(LargeBinary, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        Integer,
        nullable=False,
    )
    updated_at = Column(
        Integer,
        nullable=False,
    )
    account_active = relationship(
        "AccountActiveModel", uselist=False, back_populates="user"
    )
    reset_password = relationship(
        "ResetPasswordModel", uselist=False, back_populates="user"
    )

    def __init__(self, user_id, username, email, password, avatar):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.avatar = avatar
        self.created_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        self.updated_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    def __repr__(self):
        return f"<User {self.username!r}>"
