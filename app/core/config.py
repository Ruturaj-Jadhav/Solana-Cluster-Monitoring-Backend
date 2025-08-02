# app/core/config.py
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project Information
    PROJECT_NAME: str = "Solana Cluster Monitoring Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI backend for Solana parent-child wallet detection"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Helius API
    HELIUS_API_KEY: str = "29dce386-f700-47b7-a61d-6562b1145a45"
    HELIUS_BASE_URL: str = "https://api.helius.xyz/v0"
    
    # Detection Settings
    MIN_CHILD_WALLETS: int = 5  # Minimum child wallets to trigger parent detection
    DETECTION_WINDOW_MINUTES: int = 5  # Time window for parent-child detection
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()