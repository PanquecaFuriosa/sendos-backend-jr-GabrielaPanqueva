"""
Career Paths API application configuration.
Loads environment variables and provides centralized configuration.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Project
    PROJECT_NAME: str = "Career Paths API - Sendos"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://sendos:sendos123@localhost:5432/career_paths_db"
    
    # AI Service
    AI_SERVICE_BASE_URL: str = "http://localhost:8001"
    AI_SERVICE_TIMEOUT: int = 30
    
    # Security (optional for this test)
    SECRET_KEY: str = "tu-clave-secreta-super-segura-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get application configuration.
    Uses cache to avoid reloading on every call.
    """
    return Settings()
