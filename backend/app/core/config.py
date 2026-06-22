"""
Application configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from pathlib import Path
from typing import Any
from typing import List


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb+srv://buradvaibhav5_db_user:gDIWmIDGMUSSnIrS@cluster0.j3xoopn.mongodb.net/?appName=Cluster0"
    MONGODB_DB_NAME: str = "nutriguide_db"

    # Groq AI
    GROQ_API_KEY: str = ""

    # JWT
    JWT_SECRET_KEY: str = "default_change_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,"
        "https://amway-india.vercel.app"
    )

    # App
    APP_NAME: str = "NutriGuide AI"
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production", "false", "0", "no", "off"}:
                return False
            if normalized in {"debug", "dev", "development", "true", "1", "yes", "on"}:
                return True
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
