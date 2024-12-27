from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import db


class AccountActiveModel(db.Model):
    __tablename__ = "account_active"
    account_active_id = Column(String, primary_key=True)
    user_id = Column(
        String, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True
    )
    token_email = Column(String, nullable=False)
    token_web = Column(String, nullable=False)
    created_at = Column(
        Integer,
        nullable=False,
    )
    updated_at = Column(
        Integer,
        nullable=False,
    )
    expired_at = Column(
        Integer,
        nullable=False,
    )
    user = relationship("UserModel", back_populates="account_active")

    def __init__(
        self,
        account_active_id,
        user_id,
        token_email,
        token_web,
        created_at,
        updated_at,
        expired_at,
    ):
        self.account_active_id = account_active_id
        self.user_id = user_id
        self.token_email = token_email
        self.token_web = token_web
        self.created_at = created_at
        self.updated_at = updated_at
        self.expired_at = expired_at

    def __repr__(self):
        return f"<AccountActive {self.user_id}>"
