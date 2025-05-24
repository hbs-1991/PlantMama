"""Application settings and configuration."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Application
    APP_NAME: str = "PlantMama AI Agent"
    VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="production")
    LOG_LEVEL: str = Field(default="INFO")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(...)
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(...)
    TELEGRAM_WEBHOOK_URL: Optional[str] = Field(default=None)
    
    # Database
    DATABASE_URL: str = Field(default="postgresql://user:password@localhost:5432/plantcare")
    DATABASE_POOL_SIZE: int = Field(default=5)
    DATABASE_MAX_OVERFLOW: int = Field(default=10)
    
    # Redis (for caching and rate limiting)
    REDIS_URL: Optional[str] = Field(default=None)
    
    # File storage
    UPLOAD_DIR: Path = Field(default=Path("uploads"))
    MAX_IMAGE_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    
    # Rate limiting
    RATE_LIMIT_PER_USER: int = Field(default=30)  # requests per minute
    RATE_LIMIT_WINDOW: int = Field(default=60)  # seconds
    
    @field_validator("UPLOAD_DIR")
    @classmethod
    def create_upload_dir(cls, v: Path) -> Path:
        """Ensure upload directory exists."""
        v.mkdir(exist_ok=True, parents=True)
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()


# Create settings instance
settings = Settings()
