"""
External APIs Package
====================

Integration with government and third-party APIs

Author: ZeroSite Backend Team
Date: 2025-12-17
"""

from .juso_api import search_address as juso_search_address
from .kakao_api import geocode_address as kakao_geocode_address

__all__ = [
    'juso_search_address',
    'kakao_geocode_address',
]
