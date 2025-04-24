from pydantic import BaseSettings, SecretStr, AnyHttpUrl
from typing import List, Union
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings using Pydantic for validation."""
    
    # App settings
    APP_ENV: str = "development"
    APP_NAME: str = "Date Mate API"
    APP_VERSION: str = "1.0.0"
    
    # Security
    GROQ_API_KEY: SecretStr
    JWT_SECRET_KEY: SecretStr = SecretStr("development_secret")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: Union[str, List[AnyHttpUrl]] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # 1 hour in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()