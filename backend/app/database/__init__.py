"""
===============================================================================
WildLink AI — Database Package (Connections & Session Pools)
===============================================================================
Manages async and sync database connections, SQLite WAL pragma configurations,
and transaction session context managers:
- async_engine      — Async SQLAlchemy engine for FastAPI endpoints
- sync_engine       — Synchronous SQLAlchemy engine for GIS raster operations
- AsyncSessionLocal — Session factory for async database transactions
- get_db            — FastAPI dependency yielding managed database sessions
- init_db / close_db— Startup/shutdown schema migration and connection lifecycle
"""

__title__ = "WildLink Database Package"
__description__ = "Database connection pool and async session management"

from app.database.connection import (
    Base,
    async_engine,
    sync_engine,
    AsyncSessionLocal,
    get_db,
    init_db,
    close_db,
)

__all__ = [
    "Base",
    "async_engine",
    "sync_engine",
    "AsyncSessionLocal",
    "get_db",
    "init_db",
    "close_db",
]
