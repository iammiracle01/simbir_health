from pydantic import BaseModel, field_validator
from datetime import datetime
from dateutil import parser

class AppointmentBase(BaseModel):
    time: datetime
    
    @field_validator('time')
    def validate_iso8601(cls, value):
        if isinstance(value, str):
            try:
                return parser.isoparse(value)
            except ValueError:
                raise ValueError(f"{value} должно быть в формате ISO 8601.")
        return value



class AppointmentCreate(AppointmentBase):
    pass     

class AppointmentResponse(AppointmentBase):
    username: str

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') 
        }
