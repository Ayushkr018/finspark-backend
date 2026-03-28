from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    APP_ENV: str = "production"
    SECRET_KEY: str = "finspark-secret-change-in-prod"

    class Config:
        env_file = ".env"

settings = Settings()
