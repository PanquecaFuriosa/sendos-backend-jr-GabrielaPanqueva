"""
Configuración de la aplicación Career Paths API.
Carga las variables de entorno y proporciona configuraciones centralizadas.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    
    # Proyecto
    PROJECT_NAME: str = "Career Paths API - Sendos"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Base de datos
    DATABASE_URL: str = "postgresql://sendos:sendos123@localhost:5432/career_paths_db"
    
    # Servicio de IA
    AI_SERVICE_BASE_URL: str = "http://localhost:8001"
    AI_SERVICE_TIMEOUT: int = 30
    
    # Seguridad (opcional para esta prueba)
    SECRET_KEY: str = "tu-clave-secreta-super-segura-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuración de la aplicación.
    Usa cache para evitar recargar en cada llamada.
    """
    return Settings()
