from sqlalchemy import Column, Integer, DateTime, String
from app.db.database import Base
from sqlalchemy.orm import relationship


class Timetable(Base):
    __tablename__ = "timetables"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer, nullable=False)
    from_time = Column(DateTime, nullable=False)
    to_time = Column(DateTime, nullable=False)
    room = Column(String, nullable=False)
    appointments = relationship("Appointment", back_populates="timetable")
    
    def __repr__(self):
        return f"<Timetable(id={self.id}, hospital_id={self.hospital_id}, room={self.room})>"


