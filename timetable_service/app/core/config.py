import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    ACCOUNT_SERVICE_URL: str = os.getenv('ACCOUNT_SERVICE_URL')
    HOSPITAL_SERVICE_URL: str = os.getenv('HOSPITAL_SERVICE_URL')
    

settings = Settings()