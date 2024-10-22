from pydantic import BaseModel, field_validator
from datetime import datetime
from dateutil import parser

class HistoryCreate(BaseModel):
    date: datetime
    patient_id: int
    hospital_id: int
    doctor_id: int
    room: str
    data: str
    
    @field_validator('date')
    def validate_iso8601(cls, value):
        if isinstance(value, str):
            try:
                return parser.isoparse(value)
            except ValueError:
                raise ValueError(f"{value} должно быть в формате ISO 8601.")
        return value

    class Config:
        from_attributes = True

class HistoryUpdate(HistoryCreate):
    pass

class HistoryResponse(BaseModel):
    id: int
    date: datetime
    patient_id: int
    hospital_id: int
    doctor_id: int
    room: str
    data: str

    class Config:
        from_attributes = True
        
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') 
        }
