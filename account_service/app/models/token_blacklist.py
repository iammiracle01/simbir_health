from sqlalchemy import Column, String, DateTime
from app.db.database import Base

class Blacklist(Base):
    __tablename__ = "Blacklisted_Tokens"

    token = Column(String, primary_key=True, index=True)
    expiration = Column(DateTime)

