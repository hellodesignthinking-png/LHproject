"""
Kakao Local API
===============

Geocoding and Location Services

Documentation: https://developers.kakao.com/docs/latest/ko/local/dev-guide

Author: ZeroSite Backend Team
Date: 2025-12-17
"""

import httpx
import logging
from typing import Dict, Any, Optional

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# API Configuration
KAKAO_GEOCODE_URL = "https://dapi.kakao.com/v2/local/search/address.json"
KAKAO_COORD2ADDRESS_URL = "https://dapi.kakao.com/v2/local/geo/coord2address.json"


async def geocode_address(address: str) -> Optional[Dict[str, Any]]:
    """
    Geocode address to coordinates using Kakao API
    
    Args:
        address: Full address string
        
    Returns:
        Geocoding result with coordinates
    """
    try:
        # Get API key
        api_key = settings.kakao_rest_api_key
        
        if not api_key:
            logger.warning("⚠️ Kakao API key not configured. Using mock data.")
            return _mock_geocode(address)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"KakaoAK {api_key}"}
            params = {"query": address}
            
            response = await client.get(
                KAKAO_GEOCODE_URL,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            documents = data.get("documents", [])
            
            if not documents:
                logger.warning(f"⚠️ No results for address: {address}")
                return _mock_geocode(address)
            
            # Get first result
            doc = documents[0]
            address_info = doc.get("address", {})
            road_address = doc.get("road_address", {})
            
            result = {
                "coordinates": {
                    "lat": float(doc.get("y", 0)),
                    "lon": float(doc.get("x", 0))
                },
                "sido": address_info.get("region_1depth_name", ""),
                "sigungu": address_info.get("region_2depth_name", ""),
                "dong": address_info.get("region_3depth_name", ""),
                "beopjeong_dong": address_info.get("region_3depth_name", ""),
                "road_name": road_address.get("road_name", "") if road_address else "",
                "building_name": road_address.get("building_name", "") if road_address else ""
            }
            
            logger.info(f"✅ Kakao Geocoding: {address} → {result['coordinates']}")
            return result
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Kakao API HTTP error: {e.response.status_code}")
        return _mock_geocode(address)
    except Exception as e:
        logger.error(f"❌ Kakao Geocoding error: {str(e)}")
        return _mock_geocode(address)


async def reverse_geocode(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Reverse geocode coordinates to address
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Address information
    """
    try:
        api_key = settings.kakao_rest_api_key
        
        if not api_key:
            logger.warning("⚠️ Kakao API key not configured. Using mock data.")
            return _mock_reverse_geocode(lat, lon)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"KakaoAK {api_key}"}
            params = {"x": lon, "y": lat}
            
            response = await client.get(
                KAKAO_COORD2ADDRESS_URL,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            documents = data.get("documents", [])
            
            if not documents:
                return _mock_reverse_geocode(lat, lon)
            
            doc = documents[0]
            address = doc.get("address", {})
            road_address = doc.get("road_address", {})
            
            result = {
                "jibun_address": address.get("address_name", ""),
                "road_address": road_address.get("address_name", "") if road_address else "",
                "sido": address.get("region_1depth_name", ""),
                "sigungu": address.get("region_2depth_name", ""),
                "dong": address.get("region_3depth_name", "")
            }
            
            logger.info(f"✅ Kakao Reverse Geocoding: ({lat}, {lon}) → {result['jibun_address']}")
            return result
            
    except Exception as e:
        logger.error(f"❌ Kakao Reverse Geocoding error: {str(e)}")
        return _mock_reverse_geocode(lat, lon)


def _mock_geocode(address: str) -> Dict[str, Any]:
    """Mock geocoding result"""
    logger.info(f"🔄 Using mock geocoding for: {address}")
    return {
        "coordinates": {"lat": 37.5665, "lon": 126.9780},
        "sido": "서울특별시",
        "sigungu": "강남구",
        "dong": "역삼동",
        "beopjeong_dong": "역삼동",
        "road_name": "테헤란로",
        "building_name": ""
    }


def _mock_reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
    """Mock reverse geocoding result"""
    logger.info(f"🔄 Using mock reverse geocoding for: ({lat}, {lon})")
    return {
        "jibun_address": "서울특별시 강남구 역삼동 123-45",
        "road_address": "서울특별시 강남구 테헤란로 123",
        "sido": "서울특별시",
        "sigungu": "강남구",
        "dong": "역삼동"
    }
