"""
토지 데이터 조회 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import traceback

from app.services.land_data_service import LandDataService

router = APIRouter(prefix="/api/v3/land", tags=["토지 데이터"])

# 서비스 인스턴스
land_service = LandDataService()


class AddressRequest(BaseModel):
    """주소 입력 요청"""
    address: str
    
    class Config:
        schema_extra = {
            "example": {
                "address": "서울특별시 강남구 역삼동 123-45"
            }
        }


class LandDataResponse(BaseModel):
    """토지 정보 응답"""
    success: bool
    
    # 기본 정보
    address: str
    pnu: Optional[str] = None
    area: Optional[float] = None
    land_category: Optional[str] = None
    land_use_zone: Optional[str] = None
    land_use_situation: Optional[str] = None
    ownership_type: Optional[str] = None
    road_side: Optional[str] = None
    terrain_height: Optional[str] = None
    terrain_shape: Optional[str] = None
    change_date: Optional[str] = None
    
    # 가격 정보
    official_price: Optional[int] = None
    official_price_year: Optional[str] = None
    total_price: Optional[int] = None
    
    # 규제 정보
    floor_area_ratio: Optional[int] = None
    building_coverage_ratio: Optional[int] = None
    max_height: Optional[int] = None
    regulations: Optional[List[str]] = None
    
    # 거래사례
    transactions: Optional[List[Dict[str, Any]]] = None
    
    # 건물 정보
    building_info: Optional[Dict[str, Any]] = None
    
    # 오류
    error: Optional[str] = None


@router.post("/fetch")
async def fetch_land_data(request: AddressRequest):
    """
    토지 주소로 모든 정보 자동 조회 (v3.4 - Frontend Integration)
    
    **입력**: 토지 지번 주소
    
    **예시**: 
    - "서울특별시 강남구 역삼동 123-45"
    - "경기도 성남시 분당구 정자동 100"
    
    **출력**: 
    - land_data: 완전한 토지 정보 객체 (basic_info, price_info, regulation_info, transactions, building_info)
    - appraisal_context: 보고서 생성용 감정평가 컨텍스트
    - success: 성공 여부
    """
    try:
        # 토지 데이터 조회
        data = land_service.fetch_all_by_address(request.address)
        
        if not data["success"]:
            return {
                "success": False,
                "address": request.address,
                "land_data": None,
                "appraisal_context": None,
                "error": data.get("error", "데이터 조회에 실패했습니다.")
            }
        
        # 원본 land_data 구조로 변환
        basic_info = data.get("basic_info")
        price_info = data.get("price_info")
        regulation_info = data.get("regulation_info")
        
        land_area_sqm = getattr(basic_info, 'area', 0) if basic_info else 0
        land_area_pyeong = round(land_area_sqm / 3.3058, 1) if land_area_sqm > 0 else 0
        
        land_data = {
            "basic_info": {
                "address": request.address,
                "pnu_code": getattr(basic_info, 'pnu', None) if basic_info else None,
                "land_area_sqm": land_area_sqm,
                "land_area_pyeong": land_area_pyeong,
                "land_category": getattr(basic_info, 'land_category', None) if basic_info else None,
                "land_use": getattr(basic_info, 'land_use_situation', None) if basic_info else None,
                "ownership_type": getattr(basic_info, 'ownership_type', None) if basic_info else None,
                "road_side": getattr(basic_info, 'road_side', None) if basic_info else None,
                "terrain_shape": getattr(basic_info, 'terrain_shape', None) if basic_info else None,
                "terrain_height": getattr(basic_info, 'terrain_height', None) if basic_info else None
            },
            "price_info": {
                "official_price_per_sqm": getattr(price_info, 'official_price', 0) if price_info else 0,
                "total_official_price": getattr(price_info, 'total_price', 0) if price_info else 0,
                "price_year": getattr(price_info, 'base_year', "2024") if price_info else "2024",
                "reference_parcel": "인근 표준지"
            },
            "regulation_info": {
                "land_use_zone": getattr(regulation_info, 'use_zone', None) if regulation_info else None,
                "floor_area_ratio": getattr(regulation_info, 'floor_area_ratio', 0) if regulation_info else 0,
                "building_coverage_ratio": getattr(regulation_info, 'building_coverage_ratio', 0) if regulation_info else 0,
                "max_building_height": getattr(regulation_info, 'max_height', 0) if regulation_info else 0,
                "parking_required": False
            },
            "transactions": data.get("transactions", []),
            "building_info": data.get("building_info", [])
        }
        
        # AppraisalContext 형식으로 변환
        appraisal_context = land_service.to_appraisal_context(data)
        
        return {
            "success": True,
            "address": request.address,
            "land_data": land_data,
            "appraisal_context": appraisal_context,
            "error": None
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "address": request.address,
            "land_data": None,
            "appraisal_context": None,
            "error": f"서버 오류: {str(e)}"
        }


@router.get("/health")
async def check_api_health():
    """
    API 키 설정 상태 확인
    """
    import os
    from dotenv import load_dotenv
    
    # Ensure .env is loaded
    load_dotenv()
    
    kakao_key = os.getenv("KAKAO_REST_API_KEY")
    data_key = os.getenv("DATA_GO_KR_API_KEY") or os.getenv("MOIS_API_KEY")
    vworld_key = os.getenv("VWORLD_API_KEY") or os.getenv("LAND_REGULATION_API_KEY")
    
    return {
        "kakao_api": "✅ 설정됨" if kakao_key else "❌ 미설정",
        "data_go_kr_api": "✅ 설정됨" if data_key else "❌ 미설정",
        "vworld_api": "✅ 설정됨" if vworld_key else "❌ 미설정",
        "status": "ready" if all([kakao_key, data_key, vworld_key]) else "api_keys_missing"
    }


@router.post("/test")
async def test_with_sample():
    """
    샘플 주소로 API 테스트
    """
    sample_address = "서울특별시 강남구 역삼동 858"
    
    data = land_service.fetch_all_by_address(sample_address)
    
    return {
        "test_address": sample_address,
        "success": data.get("success"),
        "basic_info": data.get("basic_info").__dict__ if data.get("basic_info") else None,
        "price_info": data.get("price_info").__dict__ if data.get("price_info") else None,
        "regulation_info": data.get("regulation_info").__dict__ if data.get("regulation_info") else None,
        "transactions_count": len(data.get("transactions", [])),
        "error": data.get("error")
    }
