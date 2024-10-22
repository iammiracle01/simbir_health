from pydantic import BaseModel

class DoctorResponse(BaseModel):
    firstName: str
    lastName: str

    class Config:
        from_attributes = True
