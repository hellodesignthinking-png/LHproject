"""
Kakao API Proxy for ZeroSite M1
================================
Bypasses browser CORS restrictions for Kakao REST API calls (address → coordinates).

**WHY THIS EXISTS:**
- Browser directly calling Kakao API fails with CORS errors
- Kakao API requires proper Origin/Referer headers
- API keys must not be exposed to frontend JavaScript

**SOLUTION:**
Backend proxy adds proper headers and manages API key securely.

**USAGE:**
GET /api/proxy/kakao?address=서울특별시 강남구 역삼동 737

**RESPONSE:**
{
  "success": true,
  "data": {
    "longitude": 127.0280,
    "latitude": 37.4980,
    "address": "서울특별시 강남구 역삼동 737",
    "pnu": "1168010100073700000"
  }
}

**ERROR HANDLING:**
{
  "success": false,
  "error": "Address not found"
}
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional
import httpx
import logging
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
env_path = Path(__file__).parents[3] / ".env"
load_dotenv(env_path)

router = APIRouter(prefix="/api/proxy", tags=["Proxy"])
logger = logging.getLogger(__name__)

# Kakao API Configuration
KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY", "1b172a21a17b8b51dd47884b45228483")
KAKAO_ADDRESS_URL = "https://dapi.kakao.com/v2/local/search/address.json"

@router.get("/kakao")
async def proxy_kakao_address_search(
    address: str = Query(..., description="Address to search (한글 주소)")
) -> Dict[str, Any]:
    """
    Proxy Kakao address search API (주소 검색 → 좌표 변환)
    
    **Flow:**
    1. Frontend calls: /api/proxy/kakao?address=서울 강남구 역삼동 737
    2. Backend adds Authorization header + spoofs Referer
    3. Calls Kakao REST API
    4. Returns coordinates + PNU with CORS headers
    
    **Parameters:**
    - address: Full Korean address (시/도 + 시/군/구 + 읍/면/동 + 번지)
    
    **Returns:**
    {
        "success": true,
        "data": {
            "longitude": 127.028,
            "latitude": 37.498,
            "address": "서울특별시 강남구 역삼동 737",
            "pnu": "1168010100073700000",
            "sido": "서울특별시",
            "sigungu": "강남구",
            "dong": "역삼동",
            "jibun": "737"
        }
    }
    """
    try:
        logger.info(f"🗺️  [Kakao Proxy] Address search: {address}")
        
        # Prepare Kakao API headers
        headers = {
            "Authorization": f"KakaoAK {KAKAO_API_KEY}",
            "Referer": "http://localhost",  # Spoof Referer
            "User-Agent": "ZeroSite/1.0 (Backend Proxy)",
            "Accept": "application/json"
        }
        
        # Call Kakao API
        params = {"query": address}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                KAKAO_ADDRESS_URL,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
        
        # Parse Kakao response
        if not data.get("documents"):
            logger.warning(f"⚠️  [Kakao Proxy] No results for: {address}")
            return {
                "success": False,
                "error": "Address not found",
                "address": address
            }
        
        # Extract first result
        doc = data["documents"][0]
        address_info = doc.get("address", {})
        road_address_info = doc.get("road_address", {})
        
        # Calculate 19-digit PNU
        b_code = address_info.get("b_code", "")  # 법정동코드 (10자리)
        mountain_yn = "2" if address_info.get("mountain_yn") == "Y" else "1"  # 산 여부
        main_no = str(address_info.get("main_address_no", "0")).zfill(4)  # 본번 (4자리)
        sub_no = str(address_info.get("sub_address_no", "0")).zfill(4)  # 부번 (4자리)
        
        pnu = f"{b_code}{mountain_yn}{main_no}{sub_no}"
        
        # Construct result
        result = {
            "success": True,
            "data": {
                "longitude": float(doc["x"]),
                "latitude": float(doc["y"]),
                "address": doc.get("address_name", address),
                "pnu": pnu,
                "sido": address_info.get("region_1depth_name", ""),
                "sigungu": address_info.get("region_2depth_name", ""),
                "dong": address_info.get("region_3depth_name", ""),
                "jibun": f"{address_info.get('main_address_no', '')}-{address_info.get('sub_address_no', '')}" 
                         if address_info.get('sub_address_no') else str(address_info.get('main_address_no', '')),
                "b_code": b_code,
                "road_address": road_address_info.get("address_name") if road_address_info else None
            }
        }
        
        logger.info(f"✅ [Kakao Proxy] Success: {result['data']['address']} → PNU: {pnu}")
        return result
        
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ [Kakao Proxy] HTTP Error {e.response.status_code}: {e.response.text}")
        return {
            "success": False,
            "error": f"Kakao API returned {e.response.status_code}",
            "details": str(e.response.text)
        }
    
    except httpx.TimeoutException:
        logger.error(f"⏰ [Kakao Proxy] Timeout for address: {address}")
        return {
            "success": False,
            "error": "Kakao API request timeout (30s)"
        }
    
    except Exception as e:
        logger.error(f"💥 [Kakao Proxy] Unexpected error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": "Internal proxy error",
            "details": str(e)
        }


@router.get("/kakao/test")
async def test_kakao_proxy(
    address: str = Query(default="서울특별시 강남구 역삼동 737", description="Test address")
) -> Dict[str, Any]:
    """
    Test endpoint for Kakao proxy
    
    **Usage:**
    GET /api/proxy/kakao/test
    GET /api/proxy/kakao/test?address=서울 관악구 신림동 1524-8
    """
    logger.info(f"🧪 [Kakao Proxy Test] Testing with address: {address}")
    result = await proxy_kakao_address_search(address=address)
    result["_test_mode"] = True
    return result
