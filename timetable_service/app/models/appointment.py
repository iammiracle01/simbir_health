from sqlalchemy import Column, ForeignKey, Integer, DateTime, String
from app.db.database import Base
from sqlalchemy.orm import relationship
class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    timetable_id = Column(Integer, ForeignKey('timetables.id')) 
    username = Column(String, nullable=False)  
    time = Column(DateTime, nullable=False)
    
    timetable = relationship("Timetable", back_populates="appointments")


    def __repr__(self):
        return f"<Appointment(id={self.id}, timetable_id={self.timetable_id}, username={self.username}, time={self.time})>"

