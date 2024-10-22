import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    SECRET_KEY: str = os.getenv('JWT_SECRET_KEY')
    ALGORITHM: str = 'HS256'

    

settings = Settings()