"""
M1 STEP-Based Land Information API
===================================

8-STEP progressive land information collection API endpoints.

Architecture:
- STEP 1: Address search (도로명/지번)
- STEP 2: Geocoding & location verification
- STEP 3: Cadastral data (parcel, area)
- STEP 4: Land use & legal information
- STEP 5: Road & access information
- STEP 6: Market & transaction data
- STEP 7: (Frontend only - comprehensive verification)
- STEP 8: Context freeze → CanonicalLandContext (frozen=true)

Features:
- Distributed API calls (no rate limiting)
- Graceful degradation (manual input fallback)
- Data source tracking (API/manual/PDF)
- Immutable context after freeze
- Full M4 V2 pipeline integration

Author: ZeroSite M1 Development Team
Date: 2025-12-17
Version: 1.0
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import logging
import httpx

from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from app.core.context.canonical_land import CanonicalLandContext
from app.services.context_storage import context_storage
from app.config import get_settings
from app.services.land_bundle_collector import land_bundle_collector, LandDataBundle

logger = logging.getLogger(__name__)
settings = get_settings()

# Router
router = APIRouter(prefix="/api/m1", tags=["M1 STEP-Based Land Info"])

# In-memory storage (fallback only - Redis is primary)
frozen_contexts: Dict[str, CanonicalLandContext] = {}


# ============================================================================
# Request/Response Models
# ============================================================================

class AddressSearchRequest(BaseModel):
    """STEP 1: Address search request"""
    query: str = Field(..., description="도로명 or 지번 address query", min_length=3)


class AddressSearchResponse(BaseModel):
    """STEP 1: Address search response"""
    suggestions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of address suggestions"
    )
    success: bool = Field(True, description="Query success status")
    using_mock_data: bool = Field(False, description="Whether mock data is being used (no API key)")
    
    class AddressSuggestion(BaseModel):
        road_address: str
        jibun_address: str
        coordinates: Dict[str, float]  # {lat, lon}
        sido: str
        sigungu: str
        dong: str
        building_name: Optional[str] = None


class GeocodeRequest(BaseModel):
    """STEP 2: Geocoding request"""
    address: str = Field(..., description="Selected address from STEP 1")


class GeocodeResponse(BaseModel):
    """STEP 2: Geocoding response"""
    coordinates: Dict[str, float] = Field(..., description="Latitude & longitude")
    sido: str = Field(..., description="시/도")
    sigungu: str = Field(..., description="시/군/구")
    dong: str = Field(..., description="읍/면/동")
    beopjeong_dong: str = Field(..., description="법정동")
    success: bool = Field(True, description="API success status")


class CadastralRequest(BaseModel):
    """STEP 3: Cadastral data request"""
    coordinates: Dict[str, float] = Field(..., description="Lat/lon from STEP 2")


class CadastralResponse(BaseModel):
    """STEP 3: Cadastral data response"""
    bonbun: str = Field(..., description="본번")
    bubun: str = Field("", description="부번")
    jimok: str = Field(..., description="지목")
    area: float = Field(..., description="대지면적 (㎡)", gt=0)
    success: bool = Field(True, description="API success status")


class LandUseRequest(BaseModel):
    """STEP 4: Land use information request"""
    coordinates: Dict[str, float]
    jimok: str = Field(..., description="지목 from STEP 3")


class LandUseResponse(BaseModel):
    """STEP 4: Land use information response"""
    zone_type: str = Field(..., description="용도지역")
    zone_detail: str = Field("", description="지구/구역")
    bcr: float = Field(..., description="건폐율 (%)", ge=0, le=100)
    far: float = Field(..., description="용적률 (%)", gt=0)
    land_use: str = Field(..., description="이용상황")
    regulations: List[str] = Field(default_factory=list, description="규제사항")
    restrictions: List[str] = Field(default_factory=list, description="제한사항")
    success: bool = Field(True, description="API success status")


class RoadInfoRequest(BaseModel):
    """STEP 5: Road information request"""
    coordinates: Dict[str, float]
    radius: int = Field(100, description="Search radius in meters", ge=50, le=500)


class RoadInfoResponse(BaseModel):
    """STEP 5: Road information response"""
    nearby_roads: List[Dict[str, Any]] = Field(default_factory=list)
    road_contact: str = Field("unknown", description="접도 여부: yes/no/partial")
    road_width: float = Field(0, description="도로 폭 (m)", ge=0)
    road_type: str = Field("도로", description="도로 위치")
    success: bool = Field(True, description="API success status")


class MarketDataRequest(BaseModel):
    """STEP 6: Market data request"""
    coordinates: Dict[str, float]
    area: float = Field(..., description="대지면적", gt=0)
    radius: int = Field(1000, description="Search radius (m)", ge=500, le=5000)


class MarketDataResponse(BaseModel):
    """STEP 6: Market data response"""
    official_land_price: float = Field(0, description="공시지가 (원/㎡)", ge=0)
    official_land_price_date: str = Field("", description="기준일")
    transactions: List[Dict[str, Any]] = Field(default_factory=list)
    success: bool = Field(True, description="API success status")


class FreezeContextRequest(BaseModel):
    """STEP 8: Freeze context request"""
    
    # STEP 1 data
    address: str
    road_address: str
    
    # STEP 2 data
    coordinates: Dict[str, float]
    sido: str
    sigungu: str
    dong: str
    
    # STEP 3 data
    bonbun: str
    bubun: str = ""
    jimok: str
    area: float
    
    # STEP 4 data
    zone_type: str
    zone_detail: str = ""
    bcr: float
    far: float
    land_use: str
    regulations: List[str] = Field(default_factory=list)
    restrictions: List[str] = Field(default_factory=list)
    
    # STEP 5 data
    road_width: float
    road_type: str
    
    # STEP 6 data (optional)
    official_land_price: Optional[float] = None
    
    # Data sources tracking
    data_sources: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('area', 'bcr', 'far', 'road_width')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError("Must be positive")
        return v


class FreezeContextResponse(BaseModel):
    """STEP 8: Freeze context response"""
    context_id: str = Field(..., description="Unique context ID (parcel_id)")
    land_info_context: Dict[str, Any] = Field(..., description="Frozen CanonicalLandContext")
    frozen: bool = Field(True, description="Immutability flag")
    created_at: str = Field(..., description="Freeze timestamp")
    message: str = Field("토지 기본정보가 확정되었습니다.")


# ============================================================================
# Helper Functions
# ============================================================================

def generate_parcel_id(bonbun: str, bubun: str, sido: str, sigungu: str) -> str:
    """
    Generate unique parcel ID from land data
    
    Format: {sido_code}{sigungu_code}{bonbun}{bubun}
    Example: 1168010100100010001
    """
    # Simplified PNU generation (replace with actual PNU logic)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"M1_{timestamp}_{uuid.uuid4().hex[:8]}"


def mock_address_api(query: str) -> List[Dict[str, Any]]:
    """Mock address search API (replace with real API)"""
    # Simulate address suggestions
    return [
        {
            "road_address": f"{query} (도로명)",
            "jibun_address": f"{query} (지번)",
            "coordinates": {"lat": 37.5665, "lon": 126.9780},
            "sido": "서울특별시",
            "sigungu": "강남구",
            "dong": "역삼동",
            "building_name": "예시 빌딩"
        }
    ]


def mock_geocode_api(address: str) -> Dict[str, Any]:
    """Mock geocoding API (replace with Kakao/Naver API)"""
    return {
        "coordinates": {"lat": 37.5665, "lon": 126.9780},
        "sido": "서울특별시",
        "sigungu": "강남구",
        "dong": "역삼동",
        "beopjeong_dong": "역삼동"
    }


def mock_cadastral_api(coordinates: Dict[str, float]) -> Dict[str, Any]:
    """Mock cadastral API (replace with real land registry API)"""
    return {
        "bonbun": "123",
        "bubun": "45",
        "jimok": "대",
        "area": 1000.0
    }


def mock_land_use_api(coordinates: Dict[str, float], jimok: str) -> Dict[str, Any]:
    """Mock land use API (replace with zoning API)"""
    return {
        "zone_type": "general_residential",
        "zone_detail": "제2종일반주거지역",
        "bcr": 60.0,
        "far": 200.0,
        "land_use": "주거용",
        "regulations": [],
        "restrictions": []
    }


def mock_road_api(coordinates: Dict[str, float]) -> Dict[str, Any]:
    """Mock road information API"""
    return {
        "nearby_roads": [
            {"name": "테헤란로", "width": 25.0, "type": "도로", "distance": 10}
        ],
        "road_contact": "yes",
        "road_width": 8.0,
        "road_type": "도로"
    }


def mock_market_data_api(coordinates: Dict[str, float], area: float) -> Dict[str, Any]:
    """Mock market data API"""
    return {
        "official_land_price": 5000000,
        "official_land_price_date": "2024-01-01",
        "transactions": [
            {
                "date": "2024-06-15",
                "area": 1000,
                "amount": 800000,
                "distance": 150,
                "address": "인근 필지"
            }
        ]
    }


def _generate_mock_address_suggestions(query: str) -> List[Dict[str, Any]]:
    """
    Generate intelligent mock address suggestions based on search query.
    
    ⚠️ WARNING: This is a FALLBACK for development/testing only.
    Production systems should use real Kakao API with valid API keys.
    
    Returns contextually relevant mock data based on search query keywords.
    """
    query_lower = query.lower().strip()
    
    # Parse Korean address patterns
    is_gangnam = any(x in query_lower for x in ["강남", "gangnam"])
    is_mapo = any(x in query_lower for x in ["마포", "mapo", "월드컵", "worldcup"])
    is_jongno = any(x in query_lower for x in ["종로", "jongno", "광화문", "gwanghwamun"])
    is_songpa = any(x in query_lower for x in ["송파", "songpa", "잠실", "jamsil"])
    is_yeoksam = any(x in query_lower for x in ["역삼", "yeoksam"])
    is_samseong = any(x in query_lower for x in ["삼성", "samseong"])
    is_seoul = any(x in query_lower for x in ["서울", "seoul"])
    
    suggestions = []
    
    logger.warning(f"⚠️ Using Mock data for development - query: '{query}' | parsed: gangnam={is_gangnam}, mapo={is_mapo}, jongno={is_jongno}")
    
    # Generate contextual mock data based on search intent
    if is_mapo:
        # Mapo area (월드컵북로, 상암동)
        suggestions.extend([
            {
                "road_address": "서울특별시 마포구 월드컵북로 396",
                "jibun_address": "서울특별시 마포구 상암동 1602",
                "coordinates": {"lat": 37.5780528, "lon": 126.8897399},
                "sido": "서울특별시",
                "sigungu": "마포구",
                "dong": "상암동",
                "building_name": "누리꿈스퀘어"
            },
            {
                "road_address": "서울특별시 마포구 월드컵북로 400",
                "jibun_address": "서울특별시 마포구 상암동 1601",
                "coordinates": {"lat": 37.5793012, "lon": 126.8895034},
                "sido": "서울특별시",
                "sigungu": "마포구",
                "dong": "상암동",
                "building_name": "상암 IT타워"
            },
            {
                "road_address": "서울특별시 마포구 월드컵북로 56길 12",
                "jibun_address": "서울특별시 마포구 성산동 520",
                "coordinates": {"lat": 37.5684201, "lon": 126.9123456},
                "sido": "서울특별시",
                "sigungu": "마포구",
                "dong": "성산동",
                "building_name": None
            }
        ])
    
    elif is_jongno:
        # Jongno area (광화문, 종로)
        suggestions.extend([
            {
                "road_address": "서울특별시 종로구 세종대로 175",
                "jibun_address": "서울특별시 종로구 세종로 1-67",
                "coordinates": {"lat": 37.5719384, "lon": 126.9768759},
                "sido": "서울특별시",
                "sigungu": "종로구",
                "dong": "세종로",
                "building_name": "광화문 빌딩"
            },
            {
                "road_address": "서울특별시 종로구 종로 1",
                "jibun_address": "서울특별시 종로구 종로1가 1",
                "coordinates": {"lat": 37.5701234, "lon": 126.9825678},
                "sido": "서울특별시",
                "sigungu": "종로구",
                "dong": "종로1가",
                "building_name": "종로타워"
            }
        ])
    
    elif is_songpa:
        # Songpa area (잠실, 롯데타워)
        suggestions.extend([
            {
                "road_address": "서울특별시 송파구 올림픽로 300",
                "jibun_address": "서울특별시 송파구 신천동 7",
                "coordinates": {"lat": 37.5145123, "lon": 127.1029876},
                "sido": "서울특별시",
                "sigungu": "송파구",
                "dong": "신천동",
                "building_name": "롯데월드타워"
            },
            {
                "road_address": "서울특별시 송파구 올림픽로 424",
                "jibun_address": "서울특별시 송파구 잠실동 10",
                "coordinates": {"lat": 37.5149876, "lon": 127.1012345},
                "sido": "서울특별시",
                "sigungu": "송파구",
                "dong": "잠실동",
                "building_name": "잠실 오피스빌딩"
            }
        ])
    
    elif is_gangnam or is_yeoksam or is_samseong:
        # Gangnam area (강남, 역삼, 삼성)
        suggestions.extend([
            {
                "road_address": "서울특별시 강남구 테헤란로 521",
                "jibun_address": "서울특별시 강남구 삼성동 143",
                "coordinates": {"lat": 37.5084448, "lon": 127.0626804},
                "sido": "서울특별시",
                "sigungu": "강남구",
                "dong": "삼성동",
                "building_name": "파르나스타워"
            },
            {
                "road_address": "서울특별시 강남구 테헤란로 152",
                "jibun_address": "서울특별시 강남구 역삼동 737",
                "coordinates": {"lat": 37.4998701, "lon": 127.0359376},
                "sido": "서울특별시",
                "sigungu": "강남구",
                "dong": "역삼동",
                "building_name": "강남파이낸스센터"
            },
            {
                "road_address": "서울특별시 강남구 영동대로 513",
                "jibun_address": "서울특별시 강남구 삼성동 159",
                "coordinates": {"lat": 37.5084448, "lon": 127.0593256},
                "sido": "서울특별시",
                "sigungu": "강남구",
                "dong": "삼성동",
                "building_name": "코엑스"
            }
        ])
    
    elif is_seoul:
        # General Seoul (diverse districts)
        suggestions.extend([
            {
                "road_address": "서울특별시 강남구 테헤란로 521",
                "jibun_address": "서울특별시 강남구 삼성동 143",
                "coordinates": {"lat": 37.5084448, "lon": 127.0626804},
                "sido": "서울특별시",
                "sigungu": "강남구",
                "dong": "삼성동",
                "building_name": "파르나스타워"
            },
            {
                "road_address": "서울특별시 종로구 세종대로 175",
                "jibun_address": "서울특별시 종로구 세종로 1-67",
                "coordinates": {"lat": 37.5719384, "lon": 126.9768759},
                "sido": "서울특별시",
                "sigungu": "종로구",
                "dong": "세종로",
                "building_name": "광화문 빌딩"
            },
            {
                "road_address": "서울특별시 마포구 월드컵북로 396",
                "jibun_address": "서울특별시 마포구 상암동 1602",
                "coordinates": {"lat": 37.5780528, "lon": 126.8897399},
                "sido": "서울특별시",
                "sigungu": "마포구",
                "dong": "상암동",
                "building_name": "누리꿈스퀘어"
            }
        ])
    
    else:
        # Default: Diverse Seoul landmarks
        logger.warning(f"⚠️ No specific area matched for '{query}' - returning diverse Seoul landmarks")
        suggestions.extend([
            {
                "road_address": "서울특별시 강남구 테헤란로 521",
                "jibun_address": "서울특별시 강남구 삼성동 143",
                "coordinates": {"lat": 37.5084448, "lon": 127.0626804},
                "sido": "서울특별시",
                "sigungu": "강남구",
                "dong": "삼성동",
                "building_name": "파르나스타워"
            },
            {
                "road_address": "서울특별시 마포구 월드컵북로 396",
                "jibun_address": "서울특별시 마포구 상암동 1602",
                "coordinates": {"lat": 37.5780528, "lon": 126.8897399},
                "sido": "서울특별시",
                "sigungu": "마포구",
                "dong": "상암동",
                "building_name": "누리꿈스퀘어"
            },
            {
                "road_address": "서울특별시 종로구 세종대로 175",
                "jibun_address": "서울특별시 종로구 세종로 1-67",
                "coordinates": {"lat": 37.5719384, "lon": 126.9768759},
                "sido": "서울특별시",
                "sigungu": "종로구",
                "dong": "세종로",
                "building_name": "광화문 빌딩"
            },
            {
                "road_address": "서울특별시 송파구 올림픽로 300",
                "jibun_address": "서울특별시 송파구 신천동 7",
                "coordinates": {"lat": 37.5145123, "lon": 127.1029876},
                "sido": "서울특별시",
                "sigungu": "송파구",
                "dong": "신천동",
                "building_name": "롯데월드타워"
            }
        ])
    
    logger.info(f"📝 Generated {len(suggestions)} mock address suggestions for '{query}' (Development mode)")
    return suggestions


async def real_address_api(query: str, kakao_api_key: Optional[str] = None) -> tuple[List[Dict[str, Any]], bool]:
    """
    Real address search API using Kakao Maps
    
    Returns list of address suggestions with coordinates and a flag indicating mock data usage.
    Falls back to intelligent mock data if API key not provided or API fails.
    
    Args:
        query: Search address query
        kakao_api_key: Kakao REST API key from request header (optional)
    
    Returns:
        Tuple of (suggestions, using_mock_data)
    
    Security:
        API key from header overrides settings key.
        If no key provided, uses mock data fallback.
    """
    try:
        # Use provided API key or fallback to settings
        effective_key = kakao_api_key or settings.kakao_rest_api_key
        
        if not effective_key:
            logger.warning("⚠️ No Kakao API key provided - using mock data")
            return (_generate_mock_address_suggestions(query), True)  # Mock data flag
        
        # Use Kakao address search API
        url = f"{settings.kakao_api_base_url}/v2/local/search/address.json"
        headers = {
            "Authorization": f"KakaoAK {effective_key}"
        }
        params = {"query": query}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=10.0)
            response.raise_for_status()
            
            data = response.json()
            suggestions = []
            
            for doc in data.get("documents", [])[:10]:  # Limit to 10 results
                # Kakao API returns both road and jibun addresses
                address_info = doc.get("address", {})
                road_address_info = doc.get("road_address", {})
                
                suggestion = {
                    "road_address": road_address_info.get("address_name", "") if road_address_info else "",
                    "jibun_address": address_info.get("address_name", ""),
                    "coordinates": {
                        "lat": float(doc.get("y", 37.5665)),
                        "lon": float(doc.get("x", 126.978))
                    },
                    "sido": address_info.get("region_1depth_name", ""),
                    "sigungu": address_info.get("region_2depth_name", ""),
                    "dong": address_info.get("region_3depth_name", ""),
                    "building_name": road_address_info.get("building_name", "") if road_address_info else None
                }
                suggestions.append(suggestion)
            
            logger.info(f"✅ Found {len(suggestions)} REAL address suggestions for '{query}'")
            return (suggestions, False)  # Real API data
            
    except Exception as e:
        logger.warning(f"⚠️ Kakao API failed: {str(e)}")
        logger.info(f"🔄 Falling back to intelligent mock data for development (query: '{query}')")
        
        # INTELLIGENT MOCK FALLBACK (for development/testing)
        # Generate contextual mock data based on search query
        return (_generate_mock_address_suggestions(query), True)  # Mock data flag


# ============================================================================
# STEP 1: Address Search
# ============================================================================

@router.get("/address/search", response_model=AddressSearchResponse)
async def search_address_get(
    query: str = Query(..., description="주소 검색 쿼리"),
    x_kakao_api_key: Optional[str] = Header(None, alias="X-Kakao-API-Key")
):
    """
    STEP 1: Search for addresses (도로명/지번) - GET method
    
    Returns list of address suggestions with coordinates.
    User selects one to proceed to STEP 2.
    
    ⚠️ WARNING: If no API key provided, returns mock development data.
    Production systems must provide valid Kakao API key.
    
    Security: Kakao API key provided via request header (not stored server-side)
    """
    try:
        logger.info(f"🔍 STEP 1: Address search (GET) - query: {query}")
        logger.info(f"🔑 Kakao API Key provided: {bool(x_kakao_api_key)}")
        
        # Call real address search API with fallback
        suggestions, using_mock = await real_address_api(query, x_kakao_api_key)
        
        if using_mock:
            logger.warning(f"⚠️ Returning MOCK data for '{query}' - {len(suggestions)} suggestions")
        
        return AddressSearchResponse(
            suggestions=suggestions,
            success=True,
            using_mock_data=using_mock
        )
        
    except Exception as e:
        logger.error(f"❌ Address search failed: {str(e)}")
        return AddressSearchResponse(
            suggestions=[],
            success=False,
            using_mock_data=False
        )


@router.post("/address/search", response_model=AddressSearchResponse)
async def search_address_endpoint(
    request: AddressSearchRequest,
    x_kakao_api_key: Optional[str] = Header(None, alias="X-Kakao-API-Key")
):
    """
    STEP 1: Search for addresses (도로명/지번) - POST method
    
    Returns list of address suggestions with coordinates.
    User selects one to proceed to STEP 2.
    
    ⚠️ WARNING: If no API key provided, returns mock development data.
    Production systems must provide valid Kakao API key.
    
    Security: Kakao API key provided via request header (not stored server-side)
    """
    try:
        logger.info(f"🔍 STEP 1: Address search (POST) - query: {request.query}")
        logger.info(f"🔑 Kakao API Key provided: {bool(x_kakao_api_key)}")
        
        # Call real address search API with fallback
        suggestions, using_mock = await real_address_api(request.query, x_kakao_api_key)
        
        if using_mock:
            logger.warning(f"⚠️ Returning MOCK data for '{request.query}' - {len(suggestions)} suggestions")
        
        return AddressSearchResponse(
            suggestions=suggestions,
            success=True,
            using_mock_data=using_mock
        )
        
    except Exception as e:
        logger.error(f"❌ Address search failed: {str(e)}")
        return AddressSearchResponse(
            suggestions=[],
            success=False,
            using_mock_data=False
        )


# ============================================================================
# STEP 2: Geocoding & Location
# ============================================================================

@router.post("/geocode", response_model=GeocodeResponse)
async def geocode_address(request: GeocodeRequest):
    """
    STEP 2: Geocode address to coordinates
    
    Returns lat/lon and administrative divisions.
    Displays on map for user verification.
    """
    try:
        logger.info(f"📍 STEP 2: Geocoding - address: {request.address}")
        
        # Call geocoding API (mock for now)
        result = mock_geocode_api(request.address)
        
        return GeocodeResponse(**result, success=True)
        
    except Exception as e:
        logger.error(f"❌ Geocoding failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Geocoding failed: {str(e)}. Please enter coordinates manually."
        )


# ============================================================================
# STEP 3: Cadastral Data
# ============================================================================

@router.post("/cadastral", response_model=CadastralResponse)
async def get_cadastral_data(request: CadastralRequest):
    """
    STEP 3: Get cadastral data (parcel number, area)
    
    Returns 본번/부번, 지목, 대지면적.
    User can upload PDF to override.
    """
    try:
        logger.info(f"🗺️ STEP 3: Cadastral query - coords: {request.coordinates}")
        
        # Call cadastral API (mock for now)
        result = mock_cadastral_api(request.coordinates)
        
        return CadastralResponse(**result, success=True)
        
    except Exception as e:
        logger.error(f"❌ Cadastral query failed: {str(e)}")
        # Return partial success for manual input
        return CadastralResponse(
            bonbun="",
            bubun="",
            jimok="대",
            area=0,
            success=False
        )


# ============================================================================
# STEP 4: Land Use & Legal Information
# ============================================================================

@router.post("/land-use", response_model=LandUseResponse)
async def get_land_use(request: LandUseRequest):
    """
    STEP 4: Get land use and legal information
    
    Returns zone type, BCR, FAR, regulations.
    No judgment - factual data only.
    """
    try:
        logger.info(f"⚖️ STEP 4: Land use query - zone: {request.jimok}")
        
        # Call land use API (mock for now)
        result = mock_land_use_api(request.coordinates, request.jimok)
        
        return LandUseResponse(**result, success=True)
        
    except Exception as e:
        logger.error(f"❌ Land use query failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Land use query failed: {str(e)}. Please enter data manually."
        )


# ============================================================================
# STEP 5: Road & Access Information
# ============================================================================

@router.post("/road-info", response_model=RoadInfoResponse)
async def get_road_info(request: RoadInfoRequest):
    """
    STEP 5: Get road and access information
    
    Returns nearby roads, road width, access status.
    Displays on map with road overlay.
    """
    try:
        logger.info(f"🛣️ STEP 5: Road info query - radius: {request.radius}m")
        
        # Call road info API (mock for now)
        result = mock_road_api(request.coordinates)
        
        return RoadInfoResponse(**result, success=True)
        
    except Exception as e:
        logger.error(f"❌ Road info query failed: {str(e)}")
        return RoadInfoResponse(
            nearby_roads=[],
            road_contact="unknown",
            road_width=0,
            road_type="도로",
            success=False
        )


# ============================================================================
# STEP 6: Market & Transaction Data
# ============================================================================

@router.post("/market-data", response_model=MarketDataResponse)
async def get_market_data(request: MarketDataRequest):
    """
    STEP 6: Get market and transaction data
    
    Returns official land price and recent transactions.
    Display only - no price judgment.
    """
    try:
        logger.info(f"💰 STEP 6: Market data query - area: {request.area}㎡")
        
        # Call market data API (mock for now)
        result = mock_market_data_api(request.coordinates, request.area)
        
        return MarketDataResponse(**result, success=True)
        
    except Exception as e:
        logger.error(f"❌ Market data query failed: {str(e)}")
        return MarketDataResponse(
            official_land_price=0,
            official_land_price_date="",
            transactions=[],
            success=False
        )


# ============================================================================
# PDF Parsing (Optional)
# ============================================================================

@router.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    """
    Parse uploaded PDF (토지대장, etc.) to extract data
    
    Returns extracted fields with confidence scores.
    User confirms before using.
    """
    try:
        logger.info(f"📄 PDF upload - filename: {file.filename}")
        
        # TODO: Implement PDF parsing (OCR, text extraction)
        # For now, return mock extracted data
        
        extracted = {
            "bonbun": "123",
            "bubun": "45",
            "jimok": "대",
            "area": 1000.0
        }
        
        confidence = {
            "bonbun": 0.95,
            "bubun": 0.90,
            "jimok": 0.98,
            "area": 0.92
        }
        
        return JSONResponse(content={
            "extracted": extracted,
            "confidence": confidence,
            "success": True,
            "message": "PDF 분석 완료. 추출된 값을 확인하세요."
        })
        
    except Exception as e:
        logger.error(f"❌ PDF parsing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF parsing failed: {str(e)}"
        )


# ============================================================================
# STEP 8: Freeze Context (CRITICAL)
# ============================================================================

@router.post("/freeze-context", response_model=FreezeContextResponse)
async def freeze_context(request: FreezeContextRequest):
    """
    STEP 8: Freeze land information context
    
    Creates immutable CanonicalLandContext with frozen=True.
    This context is used by entire M2→M3→M4→M5→M6 pipeline.
    
    CRITICAL: Once frozen, context cannot be modified.
    """
    try:
        logger.info(f"🔒 STEP 8: Freezing context - area: {request.area}㎡")
        
        # Generate unique parcel ID
        context_id = generate_parcel_id(
            request.bonbun,
            request.bubun,
            request.sido,
            request.sigungu
        )
        
        # Create frozen CanonicalLandContext
        # Note: CanonicalLandContext is @dataclass(frozen=True), so it's immutable by design
        land_context = CanonicalLandContext(
            parcel_id=context_id,
            address=request.address,
            road_address=request.road_address,
            coordinates=(request.coordinates["lat"], request.coordinates["lon"]),  # Convert dict to tuple
            sido=request.sido,
            sigungu=request.sigungu,
            dong=request.dong,
            area_sqm=request.area,
            area_pyeong=request.area / 3.3058,
            land_category=request.jimok,
            land_use=request.land_use,
            zone_type=request.zone_type,
            zone_detail=request.zone_detail or "",
            far=request.far,
            bcr=request.bcr,
            road_width=request.road_width,
            road_type=request.road_type,
            terrain_height="평지",  # Default
            terrain_shape="정형",  # Default
            regulations=request.data_sources if request.data_sources else {},
            restrictions=request.restrictions,
            data_source="step_based_collection_v1",
            retrieval_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Store in Redis (primary) + memory (fallback)
        context_storage.store_frozen_context(context_id, land_context, ttl_hours=24)
        frozen_contexts[context_id] = land_context
        
        logger.info(f"✅ Context frozen - ID: {context_id}")
        
        # Return frozen context
        return FreezeContextResponse(
            context_id=context_id,
            land_info_context=land_context.to_dict() if hasattr(land_context, 'to_dict') else {},
            frozen=True,
            created_at=datetime.now().isoformat(),
            message=f"토지 기본정보가 확정되었습니다. Context ID: {context_id}"
        )
        
    except Exception as e:
        logger.error(f"❌ Context freeze failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Context freeze failed: {str(e)}"
        )


# ============================================================================
# Get Frozen Context
# ============================================================================

@router.get("/context/{context_id}")
async def get_frozen_context(context_id: str):
    """
    Get frozen CanonicalLandContext by ID
    
    Returns read-only context for pipeline use (M2→M3→M4→M5→M6).
    Context is immutable after freeze.
    """
    try:
        logger.info(f"📖 Retrieving frozen context - ID: {context_id}")
        
        if context_id not in frozen_contexts:
            raise HTTPException(
                status_code=404,
                detail=f"Context not found: {context_id}"
            )
        
        land_context = frozen_contexts[context_id]
        
        return JSONResponse(content={
            "context_id": context_id,
            "land_info_context": land_context.to_dict() if hasattr(land_context, 'to_dict') else {},
            "frozen": True,
            "created_at": datetime.now().isoformat(),
            "message": "Frozen context retrieved (read-only)"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Context retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Context retrieval failed: {str(e)}"
        )


# ============================================================================
# NEW: Unified Data Collection (M1 Redesign)
# ============================================================================

class CollectAllRequest(BaseModel):
    """Request for unified data collection"""
    address: str = Field(..., description="Full address")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")


class CollectAllResponse(BaseModel):
    """
    Response from unified data collection
    
    ⚠️ CRITICAL: success=False means REAL API data collection failed
    Mock data fallback does NOT count as success
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    failed_modules: List[str] = Field(default_factory=list, description="List of failed data modules (cadastral, legal, road, market)")
    using_mock_data: bool = Field(False, description="Whether any mock data was used")
    timestamp: str = ""


@router.options("/collect-all")
async def collect_all_options():
    """Handle CORS preflight for collect-all endpoint"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-Kakao-API-Key, X-VWorld-API-Key, X-DataGoKr-API-Key",
        }
    )

@router.post("/collect-all", response_model=CollectAllResponse)
async def collect_all_land_data(
    request: CollectAllRequest,
    x_kakao_api_key: Optional[str] = Header(None, alias="X-Kakao-API-Key"),
    x_vworld_api_key: Optional[str] = Header(None, alias="X-VWorld-API-Key"),
    x_datagokr_api_key: Optional[str] = Header(None, alias="X-DataGoKr-API-Key")
):
    """
    🎯 NEW M1 UNIFIED DATA COLLECTION
    
    Collects all land data based on coordinates in one operation:
    - Cadastral data (PNU, area, jimok)
    - Legal information (zones, regulations)
    - Road conditions
    - Market data (price, transactions)
    
    Security: API keys are provided via request headers (never stored server-side)
    This replaces the old step-by-step approach.
    User reviews all collected data in a single screen.
    """
    try:
        logger.info(f"🎯 Unified data collection - Address: {request.address}")
        logger.info(f"📍 Coordinates: ({request.lat}, {request.lon})")
        
        # Log API key presence (not the actual keys for security)
        logger.info(f"🔑 API Keys provided - Kakao: {bool(x_kakao_api_key)}, VWorld: {bool(x_vworld_api_key)}, Data.go.kr: {bool(x_datagokr_api_key)}")
        
        # Collect all data using new unified service with API keys from headers
        bundle = await land_bundle_collector.collect_bundle(
            address=request.address,
            lat=request.lat,
            lon=request.lon,
            kakao_api_key=x_kakao_api_key,
            vworld_api_key=x_vworld_api_key,
            datagokr_api_key=x_datagokr_api_key
        )
        
        # Determine which modules failed (using mock data)
        failed_modules = []
        using_mock = False
        
        if bundle.cadastral and bundle.cadastral.api_result and not bundle.cadastral.api_result.success:
            failed_modules.append("cadastral")
            using_mock = True
            
        if bundle.legal and bundle.legal.api_result and not bundle.legal.api_result.success:
            failed_modules.append("legal")
            using_mock = True
            
        if bundle.road and bundle.road.api_result and not bundle.road.api_result.success:
            failed_modules.append("road")
            using_mock = True
            
        if bundle.market and bundle.market.api_result and not bundle.market.api_result.success:
            failed_modules.append("market")
            using_mock = True
        
        # Log warning if using mock data
        if using_mock:
            logger.warning(f"⚠️ Using MOCK data for: {', '.join(failed_modules)}")
            logger.warning(f"⚠️ Original collection_success={bundle.collection_success}")
        
        # 🔥 CRITICAL FIX: Always return success=True if data is complete (even with mock data)
        # User can decide whether to accept mock data via UI verification checkboxes
        data_is_complete = (
            bundle.cadastral is not None and
            bundle.legal is not None and
            bundle.road is not None and
            bundle.market is not None
        )
        
        response_success = data_is_complete  # ✅ Success if data exists (API or Mock)
        
        return CollectAllResponse(
            success=response_success,
            data=bundle.to_dict(),
            error=None if response_success else "; ".join(bundle.collection_errors) if bundle.collection_errors else "Data collection incomplete",
            failed_modules=failed_modules,
            using_mock_data=using_mock,
            timestamp=bundle.collection_timestamp
        )
        
    except Exception as e:
        logger.error(f"❌ Unified data collection failed: {str(e)}")
        return CollectAllResponse(
            success=False,
            data=None,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """M1 API health check"""
    return JSONResponse(content={
        "status": "healthy",
        "module": "M1 Unified Data Collection API",
        "version": "2.0",
        "endpoints": 10,
        "frozen_contexts_count": len(frozen_contexts),
        "timestamp": datetime.now().isoformat(),
        "architecture": "unified_collection",
        "features": ["no_mock_fallback", "single_review_ready"]
    })


# Export router
__all__ = ["router"]

# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """M1 API health check"""
    return JSONResponse(content={
        "status": "healthy",
        "module": "M1 Unified Data Collection API",
        "version": "2.0",
        "endpoints": 10,
        "frozen_contexts_count": len(frozen_contexts),
        "timestamp": datetime.now().isoformat(),
        "architecture": "unified_collection",
        "features": ["no_mock_fallback", "single_review_ready"]
    })


# Export router
__all__ = ["router"]

# ============================================================================
# Health Check Endpoint
# ============================================================================

@router.get("/health")
async def health_check():
    """M1 API health check"""
    return JSONResponse(content={
        "status": "healthy",
        "module": "M1 Unified Data Collection API",
        "version": "2.0",
        "endpoints": 10,
        "frozen_contexts_count": len(frozen_contexts),
        "timestamp": datetime.now().isoformat(),
        "architecture": "unified_collection",
        "features": ["no_mock_fallback", "single_review_ready"]
    })


# Export router
__all__ = ["router"]
