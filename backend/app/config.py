"""
WildLink AI — Core Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os


def _get_db_path() -> str:
    """Resolve database path, ensuring writable /tmp directory on Vercel / serverless."""
    is_serverless = os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or not os.access(".", os.W_OK)
    if is_serverless:
        tmp_db = "/tmp/wildlink.db"
        # If repo has a pre-seeded wildlink.db, copy it to /tmp on first boot
        repo_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "wildlink.db"))
        alt_repo_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "wildlink.db"))
        src_db = repo_db if os.path.exists(repo_db) else (alt_repo_db if os.path.exists(alt_repo_db) else None)
        if src_db and not os.path.exists(tmp_db):
            try:
                import shutil
                shutil.copy2(src_db, tmp_db)
            except Exception:
                pass
        return tmp_db
    return "./wildlink.db"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "WildLink AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{_get_db_path()}"
    DATABASE_URL_SYNC: str = f"sqlite:///{_get_db_path()}"

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
