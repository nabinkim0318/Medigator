"""
Application settings
Manage environment variables and default settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings
    db_url: str = "sqlite:///./copilot.db"
    
    # API settings
    api_title: str = "BBB Medical Report API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # CORS settings
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080"
    ]
    
    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    # PDF settings
    pdf_output_dir: str = "./reports"
    
    # Data file path
    data_dir: str = "./data"
    rules_dir: str = "./data/rules"
    fhir_dir: str = "./data/fhir"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
