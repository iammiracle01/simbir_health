from sqlalchemy import ARRAY, Boolean, Column, Integer, String
from app.db.database import Base  

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    contactPhone = Column(String)
    rooms = Column(ARRAY(String), nullable=False, default=[])  
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Hospital(id={self.id}, name={self.name}, rooms={self.rooms})>"

    def has_room(self, room: str) -> bool:
        return room in self.rooms