from sqlalchemy import Column, String, Integer
from ..database import db


class TokenBlocklistModel(db.Model):
    __tablename__ = "token_blocklist"

    token_id = Column(String, primary_key=True)
    jti = Column(String(36), nullable=False, index=True)
    created_at = Column(Integer, nullable=False)

    def __init__(self, token_id, jti, created_at):
        self.token_id = token_id
        self.jti = jti
        self.created_at = created_at

    def __repr__(self):
        return f"<TokenBlocklist {self.jti!r}>"
