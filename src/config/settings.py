"""Settings and environment configuration for the Notion Bot API."""

from datetime import datetime
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB Configuration
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017/notion-bot",
        description="MongoDB connection URI"
    )
    
    # Notion API Configuration
    notion_api_key: str = Field(
        description="Notion API integration token",
        min_length=1
    )
    notion_api_version: str = Field(
        default="2022-10-28",
        description="Notion API version"
    )
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    debug: bool = Field(default=False, description="Enable debug mode")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Rate Limiting
    notion_rate_limit_max_retries: int = Field(
        default=4,
        description="Maximum number of retries for rate limited requests"
    )
    notion_rate_limit_initial_delay: float = Field(
        default=1.0,
        description="Initial delay in seconds for rate limit retries"
    )
    notion_rate_limit_timeout: int = Field(
        default=10,
        description="Timeout in seconds for Notion API requests"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of expected values."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @validator("api_port")
    def validate_port(cls, v: int) -> int:
        """Validate port is in valid range."""
        if not 1 <= v <= 65535:
            raise ValueError("api_port must be between 1 and 65535")
        return v


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the application settings instance (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
