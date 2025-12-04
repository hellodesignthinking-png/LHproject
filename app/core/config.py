"""
ZeroSite Core Configuration Module
Provides compatibility layer for app.core.config imports
"""

from app.config import Settings, get_settings

# Export settings for direct import
settings = get_settings()

__all__ = ["settings", "Settings", "get_settings"]
