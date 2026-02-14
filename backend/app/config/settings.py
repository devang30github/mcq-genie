"""
Configuration settings for MCQ Genie application.
Uses Pydantic for type-safe configuration management.
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "openai/gpt-3.5-turbo"
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "mcq_genie"
    
    # Application Settings
    app_name: str = "MCQ Genie"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Test Configuration
    default_mcq_count: int = 10
    max_mcq_count: int = 50
    test_time_limit_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def origins_list(self) -> List[str]:
        """Convert comma-separated origins string to list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures we only load settings once.
    """
    return Settings()