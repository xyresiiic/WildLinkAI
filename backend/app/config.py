"""
WildLink AI — Core Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "WildLink AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./wildlink.db"
    DATABASE_URL_SYNC: str = "sqlite:///./wildlink.db"

    # Security
    JWT_SECRET: str = "dev-secret-key-not-for-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Data paths
    DATA_DIR: str = "./data"
    MODEL_DIR: str = "./ml/models"
    RASTER_DIR: str = "./data/rasters"

    # Map defaults (Central Indian Highlands)
    DEFAULT_MAP_CENTER_LAT: float = 23.5
    DEFAULT_MAP_CENTER_LNG: float = 80.5
    DEFAULT_MAP_ZOOM: int = 7

    # Analysis defaults
    HABITAT_SUITABILITY_THRESHOLD: float = 0.5
    DEFAULT_GRID_RESOLUTION: float = 0.045  # degrees (~5.0km) for optimal analysis & interactive speed

    # Priority weights (configurable)
    WEIGHT_HABITAT: float = 0.25
    WEIGHT_CONNECTIVITY: float = 0.30
    WEIGHT_SPECIES: float = 0.25
    WEIGHT_RESTORATION: float = 0.15
    WEIGHT_CONSTRAINT: float = 0.05

    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5173

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
