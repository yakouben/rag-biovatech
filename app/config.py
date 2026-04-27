"""
Configuration module for ChronicCare FastAPI service.
Loads environment variables with type safety and validation.
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    # API Configuration
    app_name: str = "ChronicCare AI"
    app_version: str = "1.0.0"
    debug: bool = True

    # Supabase Configuration (optional for demo)
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_db_user: str = ""
    supabase_db_password: str = ""
    supabase_db_host: str = ""
    supabase_db_port: int = 5432
    supabase_db_name: str = ""

    # Gemini Configuration (optional for demo)
    gemini_api_key: str = ""
    gemini_model: Literal["gemini-1.5-pro", "gemini-1.5-flash"] = "gemini-1.5-flash"
    gemini_embedding_model: str = "models/text-embedding-004"

    # Service Configuration
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    # Feature Flags
    enable_drift_detection: bool = True
    enable_pdf_generation: bool = True

    # Model Configuration
    decision_tree_max_depth: int = 10
    decision_tree_min_samples_leaf: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
