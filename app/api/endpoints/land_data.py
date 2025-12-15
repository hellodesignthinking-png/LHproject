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


@router.post("/fetch", response_model=LandDataResponse)
async def fetch_land_data(request: AddressRequest):
    """
    토지 주소로 모든 정보 자동 조회
    
    **입력**: 토지 지번 주소
    
    **예시**: 
    - "서울특별시 강남구 역삼동 123-45"
    - "경기도 성남시 분당구 정자동 100"
    
    **출력**: 
    - 토지 기본정보 (면적, 지목, 용도지역, 도로접면 등)
    - 개별공시지가
    - 토지이용규제 (용적률, 건폐율)
    - 최근 거래사례
    - 건축물대장 (건물이 있는 경우)
    """
    try:
        # 토지 데이터 조회
        data = land_service.fetch_all_by_address(request.address)
        
        if not data["success"]:
            return LandDataResponse(
                success=False,
                address=request.address,
                error=data.get("error", "데이터 조회에 실패했습니다.")
            )
        
        # AppraisalContext 형식으로 변환
        ctx = land_service.to_appraisal_context(data)
        
        return LandDataResponse(
            success=True,
            address=request.address,
            pnu=ctx.get("parcel_id"),
            area=ctx.get("land_area"),
            land_category=ctx.get("land_category"),
            land_use_zone=ctx.get("zoning_code"),
            land_use_situation=ctx.get("land_use_situation"),
            ownership_type=ctx.get("ownership_type"),
            road_side=ctx.get("road_side"),
            terrain_height=ctx.get("terrain_height"),
            terrain_shape=ctx.get("terrain_shape"),
            change_date=ctx.get("change_date"),
            official_price=ctx.get("public_price"),
            official_price_year=ctx.get("public_price_year"),
            total_price=ctx.get("total_public_price"),
            floor_area_ratio=ctx.get("regulations", {}).get("floor_area_ratio"),
            building_coverage_ratio=ctx.get("regulations", {}).get("building_coverage_ratio"),
            max_height=ctx.get("regulations", {}).get("max_height"),
            regulations=ctx.get("regulations", {}).get("regulation_list"),
            transactions=ctx.get("recent_transactions"),
            building_info=ctx.get("building_info")
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def check_api_health():
    """
    API 키 설정 상태 확인
    """
    import os
    
    kakao_key = os.getenv("KAKAO_REST_API_KEY")
    data_key = os.getenv("DATA_GO_KR_API_KEY")
    vworld_key = os.getenv("VWORLD_API_KEY")
    
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
