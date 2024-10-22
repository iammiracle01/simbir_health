from sqlalchemy import Column, Integer, String, DateTime
from app.db.database import Base

class History(Base):
    __tablename__ = "histories"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    patient_id = Column(Integer, nullable=False) 
    hospital_id = Column(Integer, nullable=False)  
    doctor_id = Column(Integer, nullable=False)  
    room = Column(String, nullable=False)
    data = Column(String, nullable=False)

    def __repr__(self):
        return f"<History(id={self.id}, patient_id={self.patient_id}, hospital_id={self.hospital_id}, doctor_id={self.doctor_id})>"
