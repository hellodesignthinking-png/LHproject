"""
M1 POI Data Collection Endpoint
================================

Endpoint for collecting POI (Point of Interest) data using Kakao Map API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from app.services.kakao.kakao_map_service import KakaoMapService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/m1", tags=["M1 POI Collection"])


class POICollectionRequest(BaseModel):
    """Request to collect POI data"""
    address: str
    subway_radius: Optional[int] = 1000
    bus_radius: Optional[int] = 500
    school_radius: Optional[int] = 1000
    commercial_radius: Optional[int] = 1000


class POICollectionResponse(BaseModel):
    """Response with collected POI data"""
    success: bool
    message: str
    address: str
    coordinates: Optional[dict] = None
    data: Optional[dict] = None


@router.post("/collect-poi", response_model=POICollectionResponse)
async def collect_poi_data(request: POICollectionRequest):
    """
    Collect POI (Point of Interest) data using Kakao Map API
    
    Collects:
    - Nearby subway stations
    - Nearby bus stops
    - Nearby schools
    - Nearby commercial facilities
    
    Args:
        request: POI collection request with address and search radii
        
    Returns:
        POI data with coordinates and all nearby facilities
    """
    try:
        logger.info(f"📍 Collecting POI data for: {request.address}")
        
        service = KakaoMapService()
        
        # Get coordinates
        coords = await service.address_to_coordinates(request.address)
        if not coords:
            return POICollectionResponse(
                success=False,
                message=f"주소를 좌표로 변환할 수 없습니다: {request.address}",
                address=request.address
            )
        
        lat, lon = coords
        logger.info(f"✅ Coordinates: ({lat}, {lon})")
        
        # Collect all POI data
        poi_data = await service.collect_all_poi(
            address=request.address,
            subway_radius=request.subway_radius,
            bus_radius=request.bus_radius,
            school_radius=request.school_radius,
            commercial_radius=request.commercial_radius
        )
        
        return POICollectionResponse(
            success=True,
            message="POI 데이터 수집 완료",
            address=request.address,
            coordinates={
                'latitude': lat,
                'longitude': lon
            },
            data=poi_data
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to collect POI data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-kakao")
async def test_kakao_service():
    """Test endpoint to verify Kakao Map API is working"""
    try:
        service = KakaoMapService()
        test_address = "서울특별시 종로구 세종대로 209"  # 광화문
        
        coords = await service.address_to_coordinates(test_address)
        if coords:
            return {
                "success": True,
                "message": "Kakao Map API is working",
                "test_address": test_address,
                "coordinates": {
                    "latitude": coords[0],
                    "longitude": coords[1]
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to convert address to coordinates"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
