from pydantic import BaseModel
from typing import List

class HospitalBase(BaseModel):
    name: str
    address: str
    contactPhone: str
    rooms: List[str]

class HospitalCreate(HospitalBase):
    pass

class HospitalUpdate(HospitalBase):
    pass

class HospitalResponse(BaseModel):
    id: int
    name: str
    address: str
    contactPhone: str
    rooms: List[str]
    
    class Config:
        from_attributes = True
