"""
ZeroSite v9.1 API Endpoints
============================

Phase 3: API Integration - New Endpoints for v9.1 Auto Input System

New Endpoints:
1. POST /api/v9/resolve-address - Address to coordinates conversion
2. POST /api/v9/estimate-units - Unit count estimation
3. GET /api/v9/zoning-standards/{zone_type} - Zoning standards lookup
4. POST /api/v9/analyze-land (Enhanced) - Minimal input (4 fields) land analysis

Author: ZeroSite Development Team
Date: 2025-12-04
Version: 9.1.0
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

# v9.1 Services
from app.services_v9.address_resolver_v9_0 import AddressResolverV9, AddressInfo
from app.services_v9.zoning_auto_mapper_v9_0 import ZoningAutoMapperV9, ZoningStandards
from app.services_v9.unit_estimator_v9_0 import UnitEstimatorV9, UnitEstimationResult
from app.services_v9.normalization_layer_v9_1_enhanced import NormalizationLayerV91

# v9.0 Components (backward compatibility)
from app.orchestrator_v9.engine_orchestrator_v9_0 import EngineOrchestratorV90
from app.models_v9.standard_schema_v9_0 import StandardAnalysisOutput

# Configuration
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Router
router = APIRouter(prefix="/api/v9", tags=["ZeroSite v9.1"])

# Initialize v9.1 Services (lazy loading)
_address_resolver: Optional[AddressResolverV9] = None
_zoning_mapper: Optional[ZoningAutoMapperV9] = None
_unit_estimator: Optional[UnitEstimatorV9] = None
_normalization_layer: Optional[NormalizationLayerV91] = None


def get_address_resolver() -> AddressResolverV9:
    """Get or initialize AddressResolverV9 singleton"""
    global _address_resolver
    if _address_resolver is None:
        kakao_api_key = getattr(settings, 'KAKAO_REST_API_KEY', None)
        if not kakao_api_key:
            logger.warning("KAKAO_REST_API_KEY not configured. Address resolution may fail.")
        _address_resolver = AddressResolverV9(api_key=kakao_api_key)
    return _address_resolver


def get_zoning_mapper() -> ZoningAutoMapperV9:
    """Get or initialize ZoningAutoMapperV9 singleton"""
    global _zoning_mapper
    if _zoning_mapper is None:
        _zoning_mapper = ZoningAutoMapperV9()
    return _zoning_mapper


def get_unit_estimator() -> UnitEstimatorV9:
    """Get or initialize UnitEstimatorV9 singleton"""
    global _unit_estimator
    if _unit_estimator is None:
        _unit_estimator = UnitEstimatorV9()
    return _unit_estimator


def get_normalization_layer() -> NormalizationLayerV91:
    """Get or initialize NormalizationLayerV91 singleton"""
    global _normalization_layer
    if _normalization_layer is None:
        _normalization_layer = NormalizationLayerV91()
    return _normalization_layer


# ============================================================================
# 1. POST /api/v9/resolve-address - Address Resolution Endpoint
# ============================================================================

class ResolveAddressRequest(BaseModel):
    """Request model for address resolution"""
    address: str = Field(
        ...,
        description="한국 주소 (도로명 주소 또는 지번 주소)",
        example="서울특별시 마포구 월드컵북로 120"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "address": "서울특별시 마포구 월드컵북로 120"
            }
        }


class ResolveAddressResponse(BaseModel):
    """Response model for address resolution"""
    success: bool = Field(..., description="요청 성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: Optional[Dict[str, Any]] = Field(None, description="주소 해석 결과")
    timestamp: str = Field(..., description="응답 생성 시각 (ISO 8601)")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "주소 해석 성공",
                "data": {
                    "road_address": "서울특별시 마포구 월드컵북로 120",
                    "parcel_address": "서울특별시 마포구 상암동 1602",
                    "latitude": 37.579617,
                    "longitude": 126.889084,
                    "legal_code": "1144000000",
                    "administrative_district": "서울특별시 마포구"
                },
                "timestamp": "2025-12-04T10:30:00Z"
            }
        }


@router.post(
    "/resolve-address",
    response_model=ResolveAddressResponse,
    summary="주소 → 좌표 변환",
    description="한국 주소를 입력하면 위경도 좌표, 법정동 코드, 정규화된 주소를 반환합니다.",
    status_code=status.HTTP_200_OK
)
async def resolve_address(request: ResolveAddressRequest) -> ResolveAddressResponse:
    """
    주소 해석 API
    
    **기능:**
    - 도로명 주소 또는 지번 주소 입력
    - 정규화된 도로명/지번 주소 반환
    - 위경도 좌표 (latitude, longitude) 반환
    - 법정동 코드 (legal_code) 반환
    - 행정구역명 반환
    
    **사용 예시:**
    ```json
    {
        "address": "서울특별시 마포구 월드컵북로 120"
    }
    ```
    
    **응답 예시:**
    ```json
    {
        "success": true,
        "data": {
            "road_address": "서울특별시 마포구 월드컵북로 120",
            "parcel_address": "서울특별시 마포구 상암동 1602",
            "latitude": 37.579617,
            "longitude": 126.889084,
            "legal_code": "1144000000"
        }
    }
    ```
    """
    try:
        logger.info(f"[v9.1 API] Address resolution requested: {request.address}")
        
        # Get address resolver
        resolver = get_address_resolver()
        
        # Resolve address
        address_info: Optional[AddressInfo] = await resolver.resolve_address(request.address)
        
        if not address_info:
            logger.warning(f"[v9.1 API] Address resolution failed: {request.address}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"주소를 찾을 수 없습니다: {request.address}"
            )
        
        # Build response data
        response_data = {
            "road_address": address_info.road_address,
            "parcel_address": address_info.parcel_address,
            "latitude": address_info.latitude,
            "longitude": address_info.longitude,
            "legal_code": address_info.legal_code,
            "administrative_district": address_info.administrative_district
        }
        
        logger.info(f"[v9.1 API] Address resolved successfully: {address_info.road_address}")
        
        return ResolveAddressResponse(
            success=True,
            message="주소 해석 성공",
            data=response_data,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[v9.1 API] Address resolution error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"주소 해석 중 오류가 발생했습니다: {str(e)}"
        )


# ============================================================================
# 2. POST /api/v9/estimate-units - Unit Count Estimation Endpoint
# ============================================================================

class EstimateUnitsRequest(BaseModel):
    """Request model for unit count estimation"""
    land_area: float = Field(
        ...,
        gt=0,
        description="대지 면적 (m²)",
        example=1000.0
    )
    zone_type: str = Field(
        ...,
        description="용도지역 (예: 제3종일반주거지역)",
        example="제3종일반주거지역"
    )
    building_coverage_ratio: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="건폐율 (%). 미입력 시 용도지역 기준 자동 설정",
        example=50.0
    )
    floor_area_ratio: Optional[float] = Field(
        None,
        ge=0,
        le=2000,
        description="용적률 (%). 미입력 시 용도지역 기준 자동 설정",
        example=300.0
    )
    
    class Config:
        schema_extra = {
            "example": {
                "land_area": 1000.0,
                "zone_type": "제3종일반주거지역",
                "building_coverage_ratio": 50.0,
                "floor_area_ratio": 300.0
            }
        }


class EstimateUnitsResponse(BaseModel):
    """Response model for unit count estimation"""
    success: bool = Field(..., description="요청 성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: Optional[Dict[str, Any]] = Field(None, description="세대수 추정 결과")
    timestamp: str = Field(..., description="응답 생성 시각 (ISO 8601)")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "세대수 추정 완료",
                "data": {
                    "estimated_units": 42,
                    "total_gfa": 3000.0,
                    "residential_gfa": 2550.0,
                    "estimated_floors": 6,
                    "parking_spaces": 42,
                    "building_coverage_ratio": 50.0,
                    "floor_area_ratio": 300.0
                },
                "timestamp": "2025-12-04T10:30:00Z"
            }
        }


@router.post(
    "/estimate-units",
    response_model=EstimateUnitsResponse,
    summary="세대수 자동 추정",
    description="대지 면적과 용도지역을 입력하면 세대수, 층수, 주차면수를 자동 계산합니다.",
    status_code=status.HTTP_200_OK
)
async def estimate_units(request: EstimateUnitsRequest) -> EstimateUnitsResponse:
    """
    세대수 자동 추정 API
    
    **기능:**
    - 대지면적 + 용도지역 입력
    - 건폐율/용적률 자동 설정 (미입력 시)
    - 총 세대수 자동 계산
    - 층수, 주차면수 자동 계산
    - 총 연면적, 주거 연면적 계산
    
    **사용 예시:**
    ```json
    {
        "land_area": 1000.0,
        "zone_type": "제3종일반주거지역"
    }
    ```
    
    **응답 예시:**
    ```json
    {
        "success": true,
        "data": {
            "estimated_units": 42,
            "total_gfa": 3000.0,
            "residential_gfa": 2550.0,
            "estimated_floors": 6,
            "parking_spaces": 42
        }
    }
    ```
    """
    try:
        logger.info(f"[v9.1 API] Unit estimation requested: land_area={request.land_area}, zone={request.zone_type}")
        
        # Get services
        zoning_mapper = get_zoning_mapper()
        unit_estimator = get_unit_estimator()
        
        # Get or auto-fill building standards
        bcr = request.building_coverage_ratio
        far = request.floor_area_ratio
        
        if bcr is None or far is None:
            zoning_standards = zoning_mapper.get_zoning_standards(request.zone_type)
            if not zoning_standards:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"알 수 없는 용도지역: {request.zone_type}"
                )
            
            if bcr is None:
                bcr = zoning_standards.building_coverage_ratio
                logger.info(f"[v9.1 API] Auto-filled BCR: {bcr}%")
            
            if far is None:
                far = zoning_standards.floor_area_ratio
                logger.info(f"[v9.1 API] Auto-filled FAR: {far}%")
        
        # Estimate units
        estimation: UnitEstimationResult = unit_estimator.estimate_units(
            land_area=request.land_area,
            floor_area_ratio=far,
            building_coverage_ratio=bcr,
            zone_type=request.zone_type
        )
        
        # Build response data
        response_data = {
            "estimated_units": estimation.estimated_units,
            "total_gfa": round(estimation.total_gfa, 2),
            "residential_gfa": round(estimation.residential_gfa, 2),
            "estimated_floors": estimation.estimated_floors,
            "parking_spaces": estimation.parking_spaces,
            "building_coverage_ratio": bcr,
            "floor_area_ratio": far
        }
        
        logger.info(f"[v9.1 API] Unit estimation completed: {estimation.estimated_units} units")
        
        return EstimateUnitsResponse(
            success=True,
            message="세대수 추정 완료",
            data=response_data,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[v9.1 API] Unit estimation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"세대수 추정 중 오류가 발생했습니다: {str(e)}"
        )


# ============================================================================
# 3. GET /api/v9/zoning-standards/{zone_type} - Zoning Standards Lookup
# ============================================================================

class ZoningStandardsResponse(BaseModel):
    """Response model for zoning standards lookup"""
    success: bool = Field(..., description="요청 성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: Optional[Dict[str, Any]] = Field(None, description="용도지역 기준 정보")
    timestamp: str = Field(..., description="응답 생성 시각 (ISO 8601)")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "용도지역 기준 조회 완료",
                "data": {
                    "zone_type": "제3종일반주거지역",
                    "zone_type_full": "제3종일반주거지역 (Type 3 General Residential Area)",
                    "building_coverage_ratio": 50.0,
                    "floor_area_ratio": 300.0,
                    "height_limit": None,
                    "parking_ratio": 1.0,
                    "description": "중·고층 공동주택 중심, 높은 용적률"
                },
                "timestamp": "2025-12-04T10:30:00Z"
            }
        }


@router.get(
    "/zoning-standards/{zone_type}",
    response_model=ZoningStandardsResponse,
    summary="용도지역 기준 조회",
    description="용도지역을 입력하면 해당 지역의 건폐율, 용적률, 주차 기준 등을 반환합니다.",
    status_code=status.HTTP_200_OK
)
async def get_zoning_standards(zone_type: str) -> ZoningStandardsResponse:
    """
    용도지역 기준 조회 API
    
    **기능:**
    - 용도지역명 입력
    - 건폐율 (Building Coverage Ratio) 반환
    - 용적률 (Floor Area Ratio) 반환
    - 높이 제한 반환
    - 주차 기준 (세대당 대수) 반환
    
    **지원 용도지역:**
    - 제1종일반주거지역
    - 제2종일반주거지역
    - 제3종일반주거지역
    - 준주거지역
    - 중심상업지역
    - 일반상업지역
    - 근린상업지역
    - 준공업지역
    - 그 외 15개 용도지역
    
    **사용 예시:**
    ```
    GET /api/v9/zoning-standards/제3종일반주거지역
    ```
    
    **응답 예시:**
    ```json
    {
        "success": true,
        "data": {
            "zone_type": "제3종일반주거지역",
            "building_coverage_ratio": 50.0,
            "floor_area_ratio": 300.0,
            "parking_ratio": 1.0
        }
    }
    ```
    """
    try:
        logger.info(f"[v9.1 API] Zoning standards lookup requested: {zone_type}")
        
        # Get zoning mapper
        zoning_mapper = get_zoning_mapper()
        
        # Get zoning standards
        standards: Optional[ZoningStandards] = zoning_mapper.get_zoning_standards(zone_type)
        
        if not standards:
            # Return all available zone types for debugging
            available_zones = zoning_mapper.get_all_zone_types()
            logger.warning(f"[v9.1 API] Unknown zone type: {zone_type}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": f"알 수 없는 용도지역: {zone_type}",
                    "available_zone_types": available_zones
                }
            )
        
        # Build response data
        response_data = {
            "zone_type": standards.zone_type,
            "zone_type_full": standards.zone_type_full,
            "building_coverage_ratio": standards.building_coverage_ratio,
            "floor_area_ratio": standards.floor_area_ratio,
            "height_limit": standards.height_limit,
            "parking_ratio": standards.parking_ratio,
            "description": standards.description
        }
        
        logger.info(f"[v9.1 API] Zoning standards retrieved: BCR={standards.building_coverage_ratio}%, FAR={standards.floor_area_ratio}%")
        
        return ZoningStandardsResponse(
            success=True,
            message="용도지역 기준 조회 완료",
            data=response_data,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[v9.1 API] Zoning standards lookup error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"용도지역 기준 조회 중 오류가 발생했습니다: {str(e)}"
        )


# ============================================================================
# 4. POST /api/v9/analyze-land (Enhanced) - Minimal Input Analysis
# ============================================================================

class AnalyzeLandRequestV91(BaseModel):
    """
    v9.1 Enhanced Land Analysis Request
    
    **핵심 변경사항:**
    - 필수 입력 4개: address, land_area, land_appraisal_price, zone_type
    - 선택 입력 6개: 모두 자동 계산됨 (unit_count, latitude, longitude, etc.)
    """
    
    # ===== 필수 입력 (4개) =====
    address: str = Field(
        ...,
        description="대지 주소 (도로명 또는 지번)",
        example="서울특별시 마포구 월드컵북로 120"
    )
    land_area: float = Field(
        ...,
        gt=0,
        description="대지 면적 (m²)",
        example=1000.0
    )
    land_appraisal_price: float = Field(
        ...,
        gt=0,
        description="토지 감정평가액 (원/m²)",
        example=9000000
    )
    zone_type: str = Field(
        ...,
        description="용도지역",
        example="제3종일반주거지역"
    )
    
    # ===== 선택 입력 (자동 계산) =====
    unit_count: Optional[int] = Field(
        None,
        ge=1,
        description="[자동 계산] 총 세대수. 미입력 시 자동 추정"
    )
    latitude: Optional[float] = Field(
        None,
        description="[자동 계산] 위도. 미입력 시 주소로부터 자동 변환"
    )
    longitude: Optional[float] = Field(
        None,
        description="[자동 계산] 경도. 미입력 시 주소로부터 자동 변환"
    )
    building_coverage_ratio: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="[자동 계산] 건폐율 (%). 미입력 시 용도지역 기준 자동 설정"
    )
    floor_area_ratio: Optional[float] = Field(
        None,
        ge=0,
        le=2000,
        description="[자동 계산] 용적률 (%). 미입력 시 용도지역 기준 자동 설정"
    )
    height_limit: Optional[float] = Field(
        None,
        description="[자동 계산] 높이 제한 (m). 미입력 시 용도지역 기준 자동 설정"
    )
    
    # ===== 기타 선택 입력 =====
    unit_type_distribution: Optional[Dict[str, int]] = Field(
        None,
        description="세대 타입별 분포 (예: {'59㎡': 20, '84㎡': 15})"
    )
    construction_cost_per_sqm: Optional[float] = Field(
        None,
        gt=0,
        description="건축 공사비 (원/m²)"
    )
    
    @validator('zone_type')
    def validate_zone_type(cls, v):
        """용도지역 유효성 검증"""
        if not v or not v.strip():
            raise ValueError("용도지역은 필수 입력입니다.")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "address": "서울특별시 마포구 월드컵북로 120",
                "land_area": 1000.0,
                "land_appraisal_price": 9000000,
                "zone_type": "제3종일반주거지역"
            }
        }


class AnalyzeLandResponseV91(BaseModel):
    """Response model for v9.1 land analysis"""
    success: bool = Field(..., description="요청 성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: Optional[StandardAnalysisOutput] = Field(None, description="분석 결과 (표준 스키마)")
    auto_calculated_fields: Optional[Dict[str, Any]] = Field(
        None,
        description="v9.1에서 자동 계산된 필드 목록"
    )
    timestamp: str = Field(..., description="응답 생성 시각 (ISO 8601)")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "v9.1 토지 분석 완료 (4개 입력 → 10개 자동 계산)",
                "auto_calculated_fields": {
                    "latitude": 37.579617,
                    "longitude": 126.889084,
                    "building_coverage_ratio": 50.0,
                    "floor_area_ratio": 300.0,
                    "unit_count": 42,
                    "estimated_floors": 6,
                    "parking_spaces": 42
                },
                "data": {"site_info": {}, "financial_result": {}},
                "timestamp": "2025-12-04T10:30:00Z"
            }
        }


@router.post(
    "/analyze-land",
    response_model=AnalyzeLandResponseV91,
    summary="토지 분석 (v9.1 최소 입력)",
    description="v9.1: 4개 필드만 입력하면 나머지 10개 필드를 자동 계산하여 전체 분석 수행",
    status_code=status.HTTP_200_OK
)
async def analyze_land_v91(request: AnalyzeLandRequestV91) -> AnalyzeLandResponseV91:
    """
    v9.1 토지 분석 API (Minimal Input)
    
    **v9.1 핵심 개선사항:**
    - ✅ 필수 입력 4개로 축소 (v9.0: 10개 → v9.1: 4개)
    - ✅ 주소 → 좌표 자동 변환
    - ✅ 용도지역 → 건폐율/용적률 자동 설정
    - ✅ 세대수/층수/주차면수 자동 계산
    
    **필수 입력 (4개):**
    1. address: 주소
    2. land_area: 대지 면적
    3. land_appraisal_price: 토지 감정평가액
    4. zone_type: 용도지역
    
    **자동 계산 (10개):**
    1. latitude, longitude (주소 → 좌표)
    2. building_coverage_ratio, floor_area_ratio (용도지역 → 법정 기준)
    3. height_limit (용도지역 기준)
    4. unit_count (세대수 자동 추정)
    5. estimated_floors (층수)
    6. parking_spaces (주차면수)
    7. total_gfa, residential_gfa
    
    **사용 예시:**
    ```json
    {
        "address": "서울특별시 마포구 월드컵북로 120",
        "land_area": 1000.0,
        "land_appraisal_price": 9000000,
        "zone_type": "제3종일반주거지역"
    }
    ```
    """
    try:
        logger.info(f"[v9.1 API] Land analysis requested (minimal input): {request.address}")
        
        # Track auto-calculated fields
        auto_calculated = {}
        
        # Get v9.1 Normalization Layer
        norm_layer = get_normalization_layer()
        
        # Convert request to dict for processing
        raw_input = request.dict()
        
        # Step 1: Auto-fill missing fields using v9.1 services
        logger.info("[v9.1 API] Step 1: Auto-filling missing fields...")
        
        # 1.1 Address → Coordinates
        if request.latitude is None or request.longitude is None:
            address_info = await norm_layer.address_resolver.resolve_address(request.address)
            if address_info:
                raw_input['latitude'] = address_info.latitude
                raw_input['longitude'] = address_info.longitude
                auto_calculated['latitude'] = address_info.latitude
                auto_calculated['longitude'] = address_info.longitude
                auto_calculated['legal_code'] = address_info.legal_code
                logger.info(f"[v9.1 API] Auto-calculated coordinates: ({address_info.latitude}, {address_info.longitude})")
        
        # 1.2 Zone Type → Building Standards
        if request.building_coverage_ratio is None or request.floor_area_ratio is None:
            zoning_standards = norm_layer.zoning_mapper.get_zoning_standards(request.zone_type)
            if zoning_standards:
                if request.building_coverage_ratio is None:
                    raw_input['building_coverage_ratio'] = zoning_standards.building_coverage_ratio
                    auto_calculated['building_coverage_ratio'] = zoning_standards.building_coverage_ratio
                
                if request.floor_area_ratio is None:
                    raw_input['floor_area_ratio'] = zoning_standards.floor_area_ratio
                    auto_calculated['floor_area_ratio'] = zoning_standards.floor_area_ratio
                
                if request.height_limit is None and zoning_standards.height_limit:
                    raw_input['height_limit'] = zoning_standards.height_limit
                    auto_calculated['height_limit'] = zoning_standards.height_limit
                
                logger.info(f"[v9.1 API] Auto-calculated standards: BCR={zoning_standards.building_coverage_ratio}%, FAR={zoning_standards.floor_area_ratio}%")
        
        # 1.3 Unit Count Estimation (CRITICAL FIX: Always calculate and pass to analysis)
        # Get BCR/FAR (either from user input or auto-filled from zoning)
        bcr = raw_input.get('building_coverage_ratio', 50.0)
        far = raw_input.get('floor_area_ratio', 300.0)
        
        # Always estimate units, floors, parking (even if user provided unit_count)
        estimation = norm_layer.unit_estimator.estimate_units(
            land_area=request.land_area,
            floor_area_ratio=far,
            building_coverage_ratio=bcr,
            zone_type=request.zone_type
        )
        
        # CRITICAL FIX 1: Pass ALL estimated values to raw_input for Financial Engine
        if request.unit_count is None:
            raw_input['unit_count'] = estimation.estimated_units
            auto_calculated['unit_count'] = estimation.estimated_units
        
        # CRITICAL FIX 3: Pass GFA and other critical fields to Financial Engine
        # These fields are REQUIRED by Financial Engine but were missing
        raw_input['total_gfa'] = estimation.total_gfa
        raw_input['residential_gfa'] = estimation.residential_gfa
        raw_input['estimated_floors'] = estimation.estimated_floors
        raw_input['parking_spaces'] = estimation.parking_spaces
        
        # Track all auto-calculated fields
        auto_calculated['estimated_floors'] = estimation.estimated_floors
        auto_calculated['parking_spaces'] = estimation.parking_spaces
        auto_calculated['total_gfa'] = round(estimation.total_gfa, 2)
        auto_calculated['residential_gfa'] = round(estimation.residential_gfa, 2)
        
        logger.info(f"[v9.1 API] Auto-calculated units: {estimation.estimated_units} units, {estimation.estimated_floors} floors")
        logger.info(f"[v9.1 API] GFA calculations: total={estimation.total_gfa:.2f}m², residential={estimation.residential_gfa:.2f}m²")
        
        # CRITICAL FIX 2 & 3: Ensure all required fields for Financial Engine are present
        # Add construction cost estimate if not provided
        if 'construction_cost_per_sqm' not in raw_input or raw_input.get('construction_cost_per_sqm') is None:
            # Use default construction cost based on zone type
            if '상업' in request.zone_type:
                default_construction_cost = 3500000  # 상업: 350만원/m²
            elif '준주거' in request.zone_type:
                default_construction_cost = 3000000  # 준주거: 300만원/m²
            else:
                default_construction_cost = 2800000  # 주거: 280만원/m²
            
            raw_input['construction_cost_per_sqm'] = default_construction_cost
            auto_calculated['construction_cost_per_sqm'] = default_construction_cost
            logger.info(f"[v9.1 API] Auto-set construction cost: {default_construction_cost:,}원/m²")
        
        # Calculate total land cost for Financial Engine
        total_land_cost = request.land_area * request.land_appraisal_price
        raw_input['total_land_cost'] = total_land_cost
        auto_calculated['total_land_cost'] = total_land_cost
        
        # Step 2: Run full analysis using v9.0 orchestrator
        logger.info("[v9.1 API] Step 2: Running full analysis pipeline with auto-calculated fields...")
        logger.info(f"[v9.1 API] Passing to orchestrator: unit_count={raw_input.get('unit_count')}, "
                   f"total_gfa={raw_input.get('total_gfa'):.2f}, "
                   f"construction_cost={raw_input.get('construction_cost_per_sqm', 0):,}")
        
        orchestrator = EngineOrchestratorV90()
        
        analysis_result: StandardAnalysisOutput = await orchestrator.run_full_analysis(raw_input)
        
        # Step 3: Build response
        logger.info("[v9.1 API] Step 3: Building response...")
        
        return AnalyzeLandResponseV91(
            success=True,
            message=f"v9.1 토지 분석 완료 (4개 입력 → {len(auto_calculated)}개 자동 계산)",
            data=analysis_result,
            auto_calculated_fields=auto_calculated,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[v9.1 API] Land analysis error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"토지 분석 중 오류가 발생했습니다: {str(e)}"
        )


# ============================================================================
# Health Check Endpoint
# ============================================================================

@router.get(
    "/health",
    summary="API 상태 확인",
    description="v9.1 API 서버의 상태와 연동 서비스를 확인합니다.",
    status_code=status.HTTP_200_OK
)
async def health_check():
    """
    v9.1 API Health Check
    
    **확인 항목:**
    - API 서버 상태
    - AddressResolver 초기화 여부
    - ZoningMapper 초기화 여부
    - UnitEstimator 초기화 여부
    - Normalization Layer 초기화 여부
    """
    try:
        # Check services
        services_status = {
            "address_resolver": _address_resolver is not None,
            "zoning_mapper": _zoning_mapper is not None,
            "unit_estimator": _unit_estimator is not None,
            "normalization_layer": _normalization_layer is not None
        }
        
        return {
            "status": "healthy",
            "version": "9.1.0",
            "services": services_status,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"[v9.1 API] Health check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )
