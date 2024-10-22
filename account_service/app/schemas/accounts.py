from pydantic import BaseModel
from typing import List


class AccountResponse(BaseModel):
    id: int
    lastName: str
    firstName: str
    username: str
    roles: List[str]

    class Config:
        from_attributes = True

class AdminAccountResponse(AccountResponse):
    
    class Config:
        from_attributes = True

class UpdateAccountRequest(BaseModel):
    lastName: str
    firstName: str
    password: str

class CreateAccountRequest(BaseModel):
    firstName: str
    lastName: str
    username: str
    password: str
    roles: List[str]

class DeleteResponse(BaseModel):
    detail: str
    
    
