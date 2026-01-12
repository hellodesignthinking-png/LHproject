"""
Kakao Map API Integration
=========================

Provides location-based services using Kakao Map REST API:
- Address to coordinates conversion
- Nearby subway stations
- Nearby bus stops
- Nearby schools
- Nearby commercial facilities
"""

from .kakao_map_service import KakaoMapService

__all__ = ['KakaoMapService']
