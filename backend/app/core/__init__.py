"""
===============================================================================
WildLink AI — Core Package (Configuration & Security)
===============================================================================
Provides central system configuration settings and cryptographic helpers:
- settings           — Environment-driven pydantic configuration settings
- hash_password      — bcrypt password hashing
- verify_password    — bcrypt verification
- create_access_token— JWT token encoding
- decode_access_token— JWT token verification
"""

__title__ = "WildLink Core Package"
__description__ = "Application settings, environment variables, and security helpers"

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

__all__ = [
    "settings",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
]
