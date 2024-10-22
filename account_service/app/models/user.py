from sqlalchemy import Column, Integer, String, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String, index=True)
    lastName = Column(String, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    roles = Column(ARRAY(String), nullable=False, default=["User"])  

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, roles={self.roles})>"

    def has_role(self, role: str) -> bool:
        return role in self.roles
