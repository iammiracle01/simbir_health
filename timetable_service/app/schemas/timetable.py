from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List
from app.schemas.appointment import AppointmentResponse
from dateutil import parser

class TimetableBase(BaseModel):
    hospital_id: int
    doctor_id: int
    from_time: datetime
    to_time: datetime
    room: str
    
    @field_validator('from_time', 'to_time')
    def validate_iso8601(cls, value):
        if isinstance(value, str):
            try:
                return parser.isoparse(value)
            except ValueError:
                raise ValueError(f"{value} должно быть в формате ISO 8601.")
        return value



class TimetableCreate(TimetableBase):
    pass

class TimetableUpdate(TimetableBase):
    pass

class TimetableResponse(TimetableBase):
    id: int
    appointments: List[AppointmentResponse] = []

    class Config:
        from_attributes = True  
        
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') 
        }
