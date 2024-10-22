from pydantic import BaseModel
from typing import List

class SignUpRequest(BaseModel):
    lastName: str
    firstName: str
    username: str
    password: str
    
class AccountResponse(BaseModel):
    id: int
    lastName: str
    firstName: str
    username: str
    roles: List[str]

    class Config:
        from_attributes = True
        
    
class SignInRequest(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refreshToken: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

