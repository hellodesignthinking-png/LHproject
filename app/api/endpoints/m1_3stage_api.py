"""
M1 3-Stage API Endpoints
=========================

ZeroSite Decision OS M1 핵심 API

5개 핵심 엔드포인트:
1. POST /auto-fetch - Stage 1: 자동 수집
2. POST /mock-generate - Stage 2 초기화: Mock 생성
3. PATCH /edit - Stage 2: 수기 수정
4. GET /validate - Stage 2→3: Freeze 가능 여부
5. POST /freeze - Stage 3: FACT FREEZE (되돌릴 수 없음)

Author: ZeroSite Decision OS
Date: 2026-01-12
"""

import uuid
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging

from app.core.m1_state_machine import (
    M1Status, M1StateContext, M1AutoData, M1MockData, M1EditableData,
    M1ResultData, DataSource,
    get_m1_state, save_m1_state, create_m1_state
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/projects/{project_id}/modules/M1",
    tags=["M1 3-Stage System"]
)


# ============================================================================
# Stage 1: 자동 수집
# ============================================================================

@router.post("/auto-fetch")
async def auto_fetch_land_data(project_id: str) -> JSONResponse:
    """
    Stage 1: 지번 입력 & 자동 수집
    
    **역할:**
    - 카카오 API로 주소 → 좌표 변환
    - 행정구역, POI 1차 수집
    - 실패 항목은 null로 남김
    
    **상태 전이:** EMPTY → AUTO_FETCHED
    """
    
    logger.info("="*80)
    logger.info(f"🔵 M1 STAGE 1: AUTO FETCH")
    logger.info(f"   Project ID: {project_id}")
    logger.info("="*80)
    
    # 1. 상태 조회 또는 생성
    context = get_m1_state(project_id)
    if not context:
        context = create_m1_state(project_id)
        logger.info(f"✅ M1 State created: {project_id}")
    
    # 2. 상태 검증
    if context.status != M1Status.EMPTY:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": f"auto-fetch는 EMPTY 상태에서만 가능합니다 (현재: {context.status})",
                "current_status": context.status.value
            }
        )
    
    # 3. 자동 수집 (카카오 API)
    try:
        # TODO: 실제 카카오 API 호출
        # from app.services.kakao_api import fetch_address_data
        # auto_data = fetch_address_data(address)
        
        # 현재는 Mock 데이터 (실제 구현 시 교체)
        auto_data = M1AutoData(
            address="서울특별시 강남구 테헤란로 518",
            lat=37.5079,
            lng=127.0623,
            admin_area={
                "si": "서울특별시",
                "gu": "강남구",
                "dong": "대치동"
            },
            poi_summary={
                "subway": 2,
                "school": 1,
                "public_facility": 3
            }
        )
        
        context.auto_data = auto_data
        context.transition_to(M1Status.AUTO_FETCHED, "자동 수집 완료")
        save_m1_state(context)
        
        logger.info("✅ Auto fetch completed")
        logger.info(f"   Address: {auto_data.address}")
        logger.info(f"   Coordinates: ({auto_data.lat}, {auto_data.lng})")
        logger.info("="*80)
        
        return JSONResponse(content={
            "status": context.status.value,
            "auto_data": auto_data.dict()
        })
        
    except Exception as e:
        logger.error(f"❌ Auto fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "AUTO_FETCH_FAILED",
                "message": f"자동 수집 실패: {str(e)}"
            }
        )


# ============================================================================
# Stage 2 초기화: Mock 생성
# ============================================================================

@router.post("/mock-generate")
async def generate_mock_data(project_id: str) -> JSONResponse:
    """
    Stage 2 초기화: Mock 데이터 생성
    
    **역할:**
    - 자동 수집 실패/미제공 항목을 Mock으로 채움
    - 이후 사용자 수정 가능
    
    **Mock 대상:**
    - 대지면적, 용도지역, 건폐율/용적률
    - 공시지가, 거래사례, 규제 요약
    
    **상태 전이:** AUTO_FETCHED → EDITABLE
    """
    
    logger.info("="*80)
    logger.info(f"🟡 M1 STAGE 2: MOCK GENERATE")
    logger.info(f"   Project ID: {project_id}")
    logger.info("="*80)
    
    # 1. 상태 조회
    context = get_m1_state(project_id)
    if not context:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 2. 상태 검증
    if context.status != M1Status.AUTO_FETCHED:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": f"mock-generate는 AUTO_FETCHED 상태에서만 가능합니다 (현재: {context.status})",
                "current_status": context.status.value
            }
        )
    
    # 3. Mock 데이터 생성 (LH 실무 기준 포함)
    try:
        mock_data = M1MockData(
            area_sqm=1200,
            zone_type="상업지역",
            bcr=60,
            far=800,
            official_land_price=18000000,
            road_condition="8m 접도",
            transaction_cases=[
                {
                    "date": "2024-06-15",
                    "price_per_sqm": 17500000,
                    "area_sqm": 1100,
                    "zone": "상업지역",
                    "distance_m": 250
                },
                {
                    "date": "2024-03-20",
                    "price_per_sqm": 18200000,
                    "area_sqm": 1300,
                    "zone": "상업지역",
                    "distance_m": 380
                }
            ],
            regulation_summary={
                "height_limit": "없음",
                "cultural_heritage": False,
                "school_zone": True
            }
        )
        
        # editable_data 초기화 (auto_data + mock_data + LH 필수 필드)
        editable_data = M1EditableData(
            # 기본 정보
            address=context.auto_data.address if context.auto_data else None,
            lat=context.auto_data.lat if context.auto_data else None,
            lng=context.auto_data.lng if context.auto_data else None,
            
            # 토지 정보 (신규 필드명)
            land_area=mock_data.area_sqm,
            zoning=mock_data.zone_type,
            bcr=mock_data.bcr,
            far=mock_data.far,
            official_land_price=mock_data.official_land_price,
            
            # 🔴 도로 조건 (LH 필수 - Mock 데이터)
            road_access_type="단일접면",
            road_width_m=8.0,
            road_count=1,
            fire_truck_access=True,
            road_legal_status="도로",
            
            # 🔴 대지 형상 (LH 필수 - Mock 데이터)
            site_shape_type="정형",
            frontage_m=20.0,
            depth_m=24.0,
            effective_build_ratio=90.0,
            
            # 방향/일조 (Mock 데이터)
            main_direction="남",
            sunlight_risk="낮음",
            adjacent_height_risk="낮음",
            
            # 시세 정보 (Mock 데이터)
            nearby_transaction_price_py=20000000.0,
            public_land_price_py=15000000.0,
            price_gap_ratio=1.33,
            
            # 기존 건물 (Mock 데이터)
            existing_building_exists=False,
            
            # 기타
            transaction_price=17500000.0,
            regulation_summary="일반규제지역",
            lh_compatibility="적합"
        )
        
        context.mock_data = mock_data
        context.editable_data = editable_data
        
        # 🔴 Freeze 가능 여부 확인 (Mock 데이터는 모든 필드 완성)
        validation = context.validate_for_freeze()
        
        if validation.can_freeze:
            context.transition_to(M1Status.READY_TO_FREEZE, "Mock 데이터 생성 완료 (필수값 충족)")
        else:
            context.transition_to(M1Status.EDITABLE, "Mock 데이터 생성 완료")
        
        save_m1_state(context)
        
        logger.info("✅ Mock data generated")
        logger.info(f"   Area: {mock_data.area_sqm} ㎡")
        logger.info(f"   Zone: {mock_data.zone_type}")
        logger.info(f"   Price: ₩{mock_data.official_land_price:,}/㎡")
        logger.info(f"   Status: {context.status.value}")
        logger.info(f"   Can freeze: {validation.can_freeze}")
        logger.info("="*80)
        
        return JSONResponse(content={
            "status": context.status.value,
            "mock_data": mock_data.dict(),
            "editable_data": editable_data.dict(),
            "validation": validation.dict()
        })
        
    except Exception as e:
        logger.error(f"❌ Mock generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "MOCK_GENERATION_FAILED",
                "message": f"Mock 데이터 생성 실패: {str(e)}"
            }
        )


# ============================================================================
# Stage 2: 수기 수정
# ============================================================================

@router.patch("/edit")
async def edit_land_data(
    project_id: str,
    edit_data: M1EditableData
) -> JSONResponse:
    """
    Stage 2: Fact Editor 수정
    
    **역할:**
    - Fact Editor에서 수정한 값 저장
    - 아직 분석에는 사용 ❌
    
    **상태:** EDITABLE 유지 (필수값 충족 시 READY_TO_FREEZE)
    """
    
    logger.info("="*80)
    logger.info(f"✏️ M1 STAGE 2: EDIT")
    logger.info(f"   Project ID: {project_id}")
    logger.info("="*80)
    
    # 1. 상태 조회
    context = get_m1_state(project_id)
    if not context:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 2. 편집 가능 여부 검증
    if not context.can_edit():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "CANNOT_EDIT",
                "message": f"현재 상태에서는 편집할 수 없습니다 (현재: {context.status})",
                "current_status": context.status.value
            }
        )
    
    # 3. 수정 데이터 병합
    try:
        # 기존 데이터와 병합
        if context.editable_data:
            # 제공된 필드만 업데이트
            for field, value in edit_data.dict(exclude_unset=True).items():
                setattr(context.editable_data, field, value)
        else:
            context.editable_data = edit_data
        
        # 4. Freeze 가능 여부 확인
        validation = context.validate_for_freeze()
        
        if validation.can_freeze:
            context.transition_to(M1Status.READY_TO_FREEZE, "필수값 충족")
        elif context.status == M1Status.READY_TO_FREEZE:
            # 필수값이 다시 불충족되면 EDITABLE로 복귀
            context.transition_to(M1Status.EDITABLE, "필수값 미충족")
        
        context.updated_at = datetime.now()
        save_m1_state(context)
        
        logger.info("✅ Edit completed")
        logger.info(f"   Status: {context.status.value}")
        logger.info(f"   Can freeze: {validation.can_freeze}")
        logger.info("="*80)
        
        return JSONResponse(content={
            "status": context.status.value,
            "editable_data": context.editable_data.dict(),
            "validation": validation.dict()
        })
        
    except Exception as e:
        logger.error(f"❌ Edit failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "EDIT_FAILED",
                "message": f"수정 실패: {str(e)}"
            }
        )


# ============================================================================
# Stage 2→3: Freeze 가능 여부 검증
# ============================================================================

@router.get("/validate")
async def validate_for_freeze(project_id: str) -> JSONResponse:
    """
    Freeze 가능 여부 검증
    
    **검증 조건 (필수):**
    - area_sqm > 0
    - zone_type 존재
    - bcr / far 존재
    - official_land_price > 0
    """
    
    logger.info(f"🔍 M1 VALIDATE: {project_id}")
    
    context = get_m1_state(project_id)
    if not context:
        raise HTTPException(status_code=404, detail="Project not found")
    
    validation = context.validate_for_freeze()
    
    return JSONResponse(content=validation.dict())


# ============================================================================
# Stage 3: FACT FREEZE (가장 중요)
# ============================================================================

class FreezeRequest(BaseModel):
    """Freeze 요청"""
    approved_by: str = Field(default="human", description="승인자")
    agree_irreversible: bool = Field(..., description="되돌릴 수 없음 동의")


@router.post("/freeze")
async def freeze_land_data(
    project_id: str,
    request: FreezeRequest
) -> JSONResponse:
    """
    🔥 FACT FREEZE (가장 중요)
    
    **역할:**
    - M1 데이터를 result_data로 확정
    - 이후 수정 불가
    - Context 생성
    
    **🔥 이 result_data만이 M2~M7의 유일한 입력값**
    
    **상태 전이:** READY_TO_FREEZE → FROZEN (되돌릴 수 없음)
    """
    
    logger.info("="*80)
    logger.info(f"🔥 M1 STAGE 3: FREEZE")
    logger.info(f"   Project ID: {project_id}")
    logger.info("="*80)
    
    # 1. 동의 확인
    if not request.agree_irreversible:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "AGREEMENT_REQUIRED",
                "message": "되돌릴 수 없음에 동의해야 합니다"
            }
        )
    
    # 2. 상태 조회
    context = get_m1_state(project_id)
    if not context:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 3. 상태 검증
    if context.status != M1Status.READY_TO_FREEZE:
        validation = context.validate_for_freeze()
        raise HTTPException(
            status_code=400,
            detail={
                "error": "NOT_READY_TO_FREEZE",
                "message": f"Freeze 불가 (현재: {context.status})",
                "current_status": context.status.value,
                "validation": validation.dict()
            }
        )
    
    # 4. 이미 Frozen?
    if context.is_frozen():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ALREADY_FROZEN",
                "message": "이미 Freeze된 데이터입니다",
                "result_data": context.result_data.dict() if context.result_data else None
            }
        )
    
    # 5. result_data 생성
    try:
        data = context.editable_data
        context_id = f"ctx-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        
        result_data = M1ResultData(
            address=data.address,
            lat=data.lat,
            lng=data.lng,
            # 🔴 Updated field names
            land_area=data.land_area,
            zoning=data.zoning,
            bcr=data.bcr,
            far=data.far,
            official_land_price=data.official_land_price,
            
            # 🔴 Road conditions (5 fields)
            road_access_type=data.road_access_type,
            road_width_m=data.road_width_m,
            road_count=data.road_count,
            fire_truck_access=data.fire_truck_access,
            road_legal_status=data.road_legal_status,
            
            # 🔴 Site shape (4 fields)
            site_shape_type=data.site_shape_type,
            frontage_m=data.frontage_m,
            depth_m=data.depth_m,
            effective_build_ratio=data.effective_build_ratio,
            
            # 🔴 Orientation/sunlight (3 fields)
            main_direction=data.main_direction,
            sunlight_risk=data.sunlight_risk,
            adjacent_height_risk=data.adjacent_height_risk,
            
            # 🔴 Market context (3 fields)
            nearby_transaction_price_py=data.nearby_transaction_price_py,
            public_land_price_py=data.public_land_price_py,
            price_gap_ratio=data.price_gap_ratio,
            
            # 🔴 Existing building (5 fields)
            existing_building_exists=data.existing_building_exists,
            existing_building_structure=data.existing_building_structure,
            existing_building_floors=data.existing_building_floors,
            existing_building_area_m2=data.existing_building_area_m2,
            demolition_required=data.demolition_required,
            
            # 🔴 Additional fields
            transaction_price=data.transaction_price,
            regulation_summary=data.regulation_summary or "정보 없음",
            lh_compatibility=data.lh_compatibility or "검토 필요",
            sources={
                "address": DataSource.KAKAO_API.value,
                "lat": DataSource.KAKAO_API.value,
                "lng": DataSource.KAKAO_API.value,
                "land_area": DataSource.USER_EDIT.value,
                "zoning": DataSource.MOCK_EDIT.value,
                "bcr": DataSource.MOCK.value,
                "far": DataSource.MOCK.value,
                "official_land_price": DataSource.MOCK_EDIT.value
            },
            frozen_at=datetime.now(),
            frozen_by=request.approved_by,
            context_id=context_id
        )
        
        context.result_data = result_data
        context.transition_to(M1Status.FROZEN, f"사용자 승인 (by: {request.approved_by})")
        save_m1_state(context)
        
        logger.info("🔥 FREEZE COMPLETED")
        logger.info(f"   Context ID: {context_id}")
        logger.info(f"   Address: {result_data.address}")
        logger.info(f"   Area: {result_data.land_area} ㎡")
        logger.info(f"   Zone: {result_data.zoning}")
        logger.info(f"   Price: ₩{result_data.official_land_price:,}/㎡")
        logger.info(f"   Frozen by: {request.approved_by}")
        logger.info(f"   Frozen at: {result_data.frozen_at}")
        logger.info("🔒 THIS DATA IS NOW IMMUTABLE")
        logger.info("="*80)
        
        # Convert to dict with JSON-safe datetime
        result_dict = result_data.model_dump()
        result_dict['frozen_at'] = result_data.frozen_at.isoformat()
        
        return JSONResponse(content={
            "status": context.status.value,
            "context_id": context_id,
            "result_data": result_dict
        })
        
    except Exception as e:
        logger.error(f"❌ Freeze failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "FREEZE_FAILED",
                "message": f"Freeze 실패: {str(e)}"
            }
        )


# ============================================================================
# 상태 조회 (디버그용)
# ============================================================================

@router.get("/state")
async def get_state(project_id: str) -> JSONResponse:
    """M1 상태 조회 (UI에서 사용)"""
    context = get_m1_state(project_id)
    if not context:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Pydantic 모델을 dict로 변환
    def model_to_dict(obj):
        if obj is None:
            return None
        return obj.model_dump() if hasattr(obj, 'model_dump') else obj
    
    return JSONResponse(content={
        "project_id": context.project_id,
        "status": context.status.value,
        "can_edit": context.can_edit(),
        "is_frozen": context.is_frozen(),
        "created_at": context.created_at.isoformat(),
        "updated_at": context.updated_at.isoformat(),
        "state_history": context.state_history,
        # 🔥 실제 데이터 반환
        "auto_data": model_to_dict(context.auto_data),
        "mock_data": model_to_dict(context.mock_data),
        "editable_data": model_to_dict(context.editable_data),
        "result_data": model_to_dict(context.result_data),
        # Legacy flags (호환성)
        "has_auto_data": context.auto_data is not None,
        "has_mock_data": context.mock_data is not None,
        "has_editable_data": context.editable_data is not None,
        "has_result_data": context.result_data is not None
    })
