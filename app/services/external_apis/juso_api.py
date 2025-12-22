"""
주소정보 API (행정안전부)
=======================

Government Address Search API Integration
API: 도로명주소 안내시스템

Documentation: https://www.juso.go.kr/addrlink/devAddrLinkRequestGuide.do

Author: ZeroSite Backend Team
Date: 2025-12-17
"""

import httpx
import logging
from typing import List, Dict, Any, Optional

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# API Configuration
JUSO_API_URL = "https://www.juso.go.kr/addrlink/addrLinkApi.do"


async def search_address(query: str, page: int = 1, count_per_page: int = 10) -> List[Dict[str, Any]]:
    """
    Search addresses using government JUSO API
    
    Args:
        query: Search keyword (도로명 or 지번)
        page: Page number (default: 1)
        count_per_page: Results per page (default: 10)
        
    Returns:
        List of address suggestions
    """
    try:
        # Check if API key is configured
        juso_key = getattr(settings, 'juso_api_key', None)
        if not juso_key:
            logger.warning("⚠️ JUSO API key not configured. Using mock data.")
            return _mock_address_search(query)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "confmKey": juso_key,
                "currentPage": page,
                "countPerPage": count_per_page,
                "keyword": query,
                "resultType": "json"
            }
            
            response = await client.get(JUSO_API_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", {})
            
            if results.get("common", {}).get("errorCode") != "0":
                error_msg = results.get("common", {}).get("errorMessage", "Unknown error")
                logger.error(f"❌ JUSO API error: {error_msg}")
                return _mock_address_search(query)
            
            juso_list = results.get("juso", [])
            
            # Transform to our format
            addresses = []
            for item in juso_list:
                addresses.append({
                    "road_address": item.get("roadAddr", ""),
                    "jibun_address": item.get("jibunAddr", ""),
                    "coordinates": {
                        "lat": 0,  # JUSO API doesn't provide coordinates
                        "lon": 0   # Need geocoding in next step
                    },
                    "sido": item.get("siNm", ""),
                    "sigungu": item.get("sggNm", ""),
                    "dong": item.get("emdNm", ""),
                    "building_name": item.get("bdNm", ""),
                    "zipcode": item.get("zipNo", ""),
                    "building_code": item.get("bdKdcd", "")
                })
            
            logger.info(f"✅ JUSO API: Found {len(addresses)} addresses for '{query}'")
            return addresses
            
    except httpx.TimeoutException:
        logger.error(f"❌ JUSO API timeout for query: {query}")
        return _mock_address_search(query)
    except Exception as e:
        logger.error(f"❌ JUSO API error: {str(e)}")
        return _mock_address_search(query)


def _mock_address_search(query: str) -> List[Dict[str, Any]]:
    """
    Mock address search for fallback
    
    Args:
        query: Search keyword
        
    Returns:
        Mock address suggestions
    """
    logger.info(f"🔄 Using mock address search for: {query}")
    
    # Return mock data with query
    return [
        {
            "road_address": f"{query} (도로명 - Mock)",
            "jibun_address": f"{query} (지번 - Mock)",
            "coordinates": {"lat": 37.5665, "lon": 126.9780},
            "sido": "서울특별시",
            "sigungu": "강남구",
            "dong": "역삼동",
            "building_name": "Mock 빌딩",
            "zipcode": "06000"
        }
    ]


async def validate_address(address: str) -> Optional[Dict[str, Any]]:
    """
    Validate and get detailed address information
    
    Args:
        address: Full address string
        
    Returns:
        Validated address information or None
    """
    try:
        results = await search_address(address, count_per_page=1)
        if results:
            return results[0]
        return None
    except Exception as e:
        logger.error(f"❌ Address validation error: {str(e)}")
        return None
