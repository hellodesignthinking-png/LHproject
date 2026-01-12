"""
M4 – BUILDING SCALE (LH-SAFE)
건축규모·형태 검토 모듈 API

역할:
- 법적 최대치가 아닌 LH 심사·인허가·감리에서 걸리지 않는 보수적 건축안 도출
- LH 권장 규모 = 법정 최대 × 0.85 (보수 설계)
- 세대수·주차·공용면적 여유 있게 산정

실행 전제:
- M1.status == FROZEN
- M2.status == COMPLETED
- M3.status == COMPLETED (공급유형 확정)

출력:
- legal_max: 법정 최대 규모 (참고용)
- lh_recommended: LH 권장 규모 (실제 설계안)
- parking_plan: 주차 계획 (보수 기준)
- design_rationale: 설계 논리 (3개 이상)

Author: ZeroSite Decision OS Team
Date: 2026-01-12
Version: 2.0
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/projects/{project_id}/modules/M4",
    tags=["M4 - Building Scale (LH-SAFE)"]
)

# ============================================================
# M4 상태 정의
# ============================================================

class M4Status(str, Enum):
    """M4 모듈 상태"""
    NOT_STARTED = "NOT_STARTED"        # M3 미완료
    CALCULATING = "CALCULATING"        # 계산 중
    COMPLETED = "COMPLETED"            # 완료
    FAILED = "FAILED"                  # 실패

# ============================================================
# M4 데이터 모델
# ============================================================

class LegalMaxScale(BaseModel):
    """법정 최대 규모 (참고용)"""
    total_floor_area: float = Field(..., gt=0, description="법정 최대 연면적 (㎡)")
    building_area: float = Field(..., gt=0, description="법정 최대 건축면적 (㎡)")
    note: str = Field(default="법정 최대치 (참고용)", description="비고")

class LHRecommendedScale(BaseModel):
    """LH 권장 규모 (실제 설계안)"""
    total_floor_area: float = Field(..., gt=0, description="LH 권장 연면적 (㎡)")
    units: int = Field(..., gt=0, description="세대수")
    floors_estimated: int = Field(..., gt=0, description="예상 층수")
    unit_area_avg: float = Field(..., gt=0, description="평균 세대면적 (㎡)")
    common_ratio: float = Field(..., ge=0.3, le=0.4, description="공용비율 (0.3~0.4)")

class ParkingPlan(BaseModel):
    """주차 계획"""
    required: int = Field(..., ge=0, description="법정 필요 주차대수")
    applied: int = Field(..., ge=0, description="실제 적용 주차대수 (보수 기준)")
    parking_ratio: float = Field(..., ge=0, description="세대당 주차비율")
    note: str = Field(default="LH 보수 기준 적용", description="비고")

class M4ResultData(BaseModel):
    """M4 결과 데이터 (result_data)"""
    
    # 법정 최대 (참고용)
    legal_max: LegalMaxScale = Field(..., description="법정 최대 규모")
    
    # LH 권장 (실제 설계안)
    lh_recommended: LHRecommendedScale = Field(..., description="LH 권장 규모")
    
    # 주차 계획
    parking_plan: ParkingPlan = Field(..., description="주차 계획")
    
    # 설계 논리 (3개 이상)
    design_rationale: List[str] = Field(..., min_length=3, description="설계 논리")
    
    # 메타데이터
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="계산 시각")
    context_id: str = Field(..., description="M1 Context ID")
    
    # M3 연계 데이터
    housing_type: str = Field(..., description="M3 추천 공급유형")

# ============================================================
# M4 계산 요청/응답
# ============================================================

class M4CalculateRequest(BaseModel):
    """M4 계산 요청"""
    context_id: str = Field(..., description="M1 Context ID (FROZEN 상태)")
    force_recalculate: bool = Field(default=False, description="강제 재계산 여부")

class M4CalculateResponse(BaseModel):
    """M4 계산 응답"""
    status: M4Status
    message: str
    result_data: Optional[M4ResultData] = None
    errors: Optional[List[str]] = None

# ============================================================
# In-Memory Storage
# ============================================================

m4_results: Dict[str, M4ResultData] = {}
m4_status: Dict[str, M4Status] = {}

# ============================================================
# Helper Functions
# ============================================================

def get_m1_frozen_data(context_id: str) -> Optional[Dict[str, Any]]:
    """M1 FROZEN 데이터 조회"""
    try:
        from app.api.endpoints.m1_context_freeze_v2 import frozen_contexts_v2
        
        if context_id not in frozen_contexts_v2:
            logger.warning(f"❌ M1 Context not found: {context_id}")
            return None
        
        frozen_ctx = frozen_contexts_v2[context_id]
        
        if hasattr(frozen_ctx, 'model_dump'):
            return frozen_ctx.model_dump()
        elif hasattr(frozen_ctx, 'dict'):
            return frozen_ctx.dict()
        else:
            return dict(frozen_ctx)
            
    except Exception as e:
        logger.error(f"❌ Failed to load M1 data: {e}")
        return None

def get_m3_result_data(context_id: str) -> Optional[Dict[str, Any]]:
    """M3 결과 데이터 조회"""
    try:
        from app.api.endpoints.m3_housing_type_api import m3_results
        
        if context_id not in m3_results:
            logger.warning(f"❌ M3 Result not found: {context_id}")
            return None
        
        result = m3_results[context_id]
        
        if hasattr(result, 'model_dump'):
            return result.model_dump()
        elif hasattr(result, 'dict'):
            return result.dict()
        else:
            return dict(result)
            
    except Exception as e:
        logger.error(f"❌ Failed to load M3 result: {e}")
        return None

def validate_prerequisites(context_id: str) -> tuple[bool, List[str]]:
    """
    M4 실행 전제 조건 검증
    
    검증 항목:
    - M1 FROZEN 상태
    - M3 완료 상태
    """
    errors = []
    
    # M1 검증
    m1_data = get_m1_frozen_data(context_id)
    if not m1_data:
        errors.append("M1 FACT not frozen")
    
    # M3 검증
    m3_data = get_m3_result_data(context_id)
    if not m3_data:
        errors.append("M3 housing type analysis not completed")
    elif not m3_data.get('recommended_type'):
        errors.append("M3 recommended type is missing")
    
    return len(errors) == 0, errors

# ============================================================
# M4 핵심 계산 엔진: LH 보수 설계
# ============================================================

def calculate_building_scale(
    m1_data: Dict[str, Any],
    m3_data: Dict[str, Any],
    context_id: str
) -> M4ResultData:
    """
    M4 건축규모 계산 엔진
    
    계산 흐름:
    1. 법정 최대 규모 (참고용)
    2. LH 권장 규모 = 법정 × 0.85
    3. 세대수 산정 (유형별 세대당 면적)
    4. 주차 계획 (보수 기준)
    """
    logger.info("=" * 80)
    logger.info("🧮 M4 BUILDING SCALE ENGINE START (LH-SAFE)")
    logger.info("=" * 80)
    
    try:
        # M1 데이터 추출
        land_info = m1_data.get('land_info', {})
        cadastral = land_info.get('cadastral', {})
        building_constraints = m1_data.get('building_constraints', {})
        legal = building_constraints.get('legal', {})
        
        area_sqm = cadastral.get('area_sqm', 0)
        bcr = legal.get('bcr_max', 60) / 100  # % → 소수
        far = legal.get('far_max', 200) / 100  # % → 소수
        
        # M3 데이터 추출
        recommended_type = m3_data.get('recommended_type')
        
        logger.info(f"📊 입력 데이터:")
        logger.info(f"   - 대지면적: {area_sqm:,.0f} ㎡")
        logger.info(f"   - 건폐율: {bcr*100:.0f}%")
        logger.info(f"   - 용적률: {far*100:.0f}%")
        logger.info(f"   - 공급유형: {recommended_type}")
        
        # ============================================================
        # ① 법정 최대 규모 (참고용)
        # ============================================================
        
        legal_total_floor = area_sqm * far
        legal_building_area = area_sqm * bcr
        
        logger.info(f"① 법정 최대 규모 (참고용):")
        logger.info(f"   - 연면적: {legal_total_floor:,.0f} ㎡")
        logger.info(f"   - 건축면적: {legal_building_area:,.0f} ㎡")
        
        legal_max = LegalMaxScale(
            total_floor_area=legal_total_floor,
            building_area=legal_building_area,
            note="법정 최대치 (참고용 - LH 권장과 차이 있음)"
        )
        
        # ============================================================
        # ② LH 권장 규모 (실제 설계안)
        # ============================================================
        
        # LH 보수 계수 적용
        lh_safety_factor = 0.85  # 법정 최대 대비 15% 감소
        
        lh_total_floor = legal_total_floor * lh_safety_factor
        
        logger.info(f"② LH 권장 규모 (실제 설계안):")
        logger.info(f"   - 연면적: {lh_total_floor:,.0f} ㎡ (법정 × {lh_safety_factor})")
        
        # ============================================================
        # ③ 세대수 산정 (유형별 세대당 면적)
        # ============================================================
        
        # 공급유형별 세대당 전용면적 (㎡)
        unit_area_map = {
            "청년 매입임대": 22.5,    # 20~25㎡ 중간값
            "신혼부부 매입임대": 40.0,  # 35~45㎡ 중간값
            "고령자 복지주택": 35.0,   # 30~40㎡ 중간값
            "역세권 청년주택": 22.5,
            "일반 공공임대": 30.0
        }
        
        unit_area = unit_area_map.get(recommended_type, 30.0)
        
        # 공용비율
        common_ratio = 0.30  # 기본 30%
        
        # 세대당 면적 (전용 + 공용)
        unit_total_area = unit_area / (1 - common_ratio)
        
        # 세대수
        units = int(lh_total_floor / unit_total_area)
        
        logger.info(f"③ 세대수 산정:")
        logger.info(f"   - 세대당 전용면적: {unit_area:.1f} ㎡")
        logger.info(f"   - 공용비율: {common_ratio*100:.0f}%")
        logger.info(f"   - 세대당 총면적: {unit_total_area:.1f} ㎡")
        logger.info(f"   - 세대수: {units}세대")
        
        # 예상 층수 (간단 계산)
        typical_floor_area = legal_building_area * 0.8  # 건축면적의 80%
        floors_estimated = max(1, int(lh_total_floor / typical_floor_area))
        
        logger.info(f"   - 예상 층수: {floors_estimated}층")
        
        lh_recommended = LHRecommendedScale(
            total_floor_area=lh_total_floor,
            units=units,
            floors_estimated=floors_estimated,
            unit_area_avg=unit_area,
            common_ratio=common_ratio
        )
        
        # ============================================================
        # ④ 주차 계획 (보수 기준)
        # ============================================================
        
        # 공급유형별 주차 기준
        parking_ratio_map = {
            "청년 매입임대": 0.35,     # 0.3~0.4 중간값
            "신혼부부 매입임대": 0.85,  # 0.7~1.0 중간값
            "고령자 복지주택": 0.50,
            "역세권 청년주택": 0.35,
            "일반 공공임대": 0.70
        }
        
        parking_ratio = parking_ratio_map.get(recommended_type, 0.50)
        
        # 법정 필요 주차대수
        parking_required = math.ceil(units * parking_ratio)
        
        # LH 보수 기준: 법정 대비 +10% (올림)
        parking_applied = math.ceil(parking_required * 1.10)
        
        logger.info(f"④ 주차 계획:")
        logger.info(f"   - 세대당 주차비율: {parking_ratio}")
        logger.info(f"   - 법정 필요: {parking_required}대")
        logger.info(f"   - 실제 적용: {parking_applied}대 (법정 +10%)")
        
        parking_plan = ParkingPlan(
            required=parking_required,
            applied=parking_applied,
            parking_ratio=parking_ratio,
            note=f"LH 보수 기준 적용 (법정 대비 +10%)"
        )
        
        # ============================================================
        # 설계 논리 (3개 이상)
        # ============================================================
        
        design_rationale = [
            f"법정 최대 연면적({legal_total_floor:,.0f}㎡) 대비 15% 보수 설계 적용",
            f"{recommended_type} 표준 세대면적({unit_area:.1f}㎡) 기준 {units}세대 산정",
            f"주차 기준 법정({parking_required}대) 대비 상향 적용({parking_applied}대)",
            f"공용비율 {common_ratio*100:.0f}% 적용으로 설계 여유 확보",
            "LH 심사·인허가·감리 보수성 우선 반영"
        ]
        
        logger.info(f"✅ M4 계산 완료")
        logger.info("=" * 80)
        
        return M4ResultData(
            legal_max=legal_max,
            lh_recommended=lh_recommended,
            parking_plan=parking_plan,
            design_rationale=design_rationale,
            context_id=context_id,
            housing_type=recommended_type
        )
        
    except Exception as e:
        logger.error(f"❌ M4 계산 실패: {e}", exc_info=True)
        raise

# ============================================================
# API Endpoints
# ============================================================

@router.post("/calculate", response_model=M4CalculateResponse)
async def calculate_building_scale_endpoint(
    project_id: str,
    request: M4CalculateRequest
):
    """
    M4 건축규모 계산 실행
    
    실행 전제:
    - M1.status == FROZEN
    - M3.status == COMPLETED
    """
    logger.info(f"🚀 M4 CALCULATE START - Project: {project_id}, Context: {request.context_id}")
    
    try:
        # ① 전제 조건 검증
        is_valid, errors = validate_prerequisites(request.context_id)
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "PREREQUISITES_NOT_MET",
                    "message": "M4 cannot run: prerequisites not met",
                    "errors": errors,
                    "action": "Please complete M1 freeze and M3 analysis first"
                }
            )
        
        logger.info(f"✅ 전제 조건 검증 완료")
        
        # ② 기존 결과 확인
        if not request.force_recalculate and request.context_id in m4_results:
            logger.info(f"♻️ 기존 M4 결과 반환 (캐시)")
            return M4CalculateResponse(
                status=M4Status.COMPLETED,
                message="M4 calculation already completed (cached)",
                result_data=m4_results[request.context_id]
            )
        
        # ③ M1, M3 데이터 로드
        m1_data = get_m1_frozen_data(request.context_id)
        m3_data = get_m3_result_data(request.context_id)
        
        # ④ M4 계산 실행
        m4_status[request.context_id] = M4Status.CALCULATING
        
        result_data = calculate_building_scale(m1_data, m3_data, request.context_id)
        
        # ⑤ 결과 저장
        m4_results[request.context_id] = result_data
        m4_status[request.context_id] = M4Status.COMPLETED
        
        logger.info(f"✅ M4 계산 완료 및 저장")
        
        return M4CalculateResponse(
            status=M4Status.COMPLETED,
            message="M4 building scale calculation completed successfully",
            result_data=result_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M4 계산 실패: {e}", exc_info=True)
        m4_status[request.context_id] = M4Status.FAILED
        
        return M4CalculateResponse(
            status=M4Status.FAILED,
            message=f"M4 calculation failed: {str(e)}",
            errors=[str(e)]
        )

@router.get("/result", response_model=M4ResultData)
async def get_m4_result(
    project_id: str,
    context_id: str
):
    """M4 계산 결과 조회"""
    
    if context_id not in m4_results:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "M4_RESULT_NOT_FOUND",
                "message": "M4 calculation not yet performed",
                "context_id": context_id,
                "action": "Please calculate M4 first: POST /api/projects/{project_id}/modules/M4/calculate"
            }
        )
    
    return m4_results[context_id]

@router.get("/status")
async def get_m4_status(
    project_id: str,
    context_id: str
):
    """M4 상태 조회"""
    
    status = m4_status.get(context_id, M4Status.NOT_STARTED)
    
    return {
        "project_id": project_id,
        "context_id": context_id,
        "status": status,
        "has_result": context_id in m4_results
    }

@router.get("/validate")
async def validate_m4_prerequisites(
    project_id: str,
    context_id: str
):
    """
    M4 실행 가능 여부 검증
    
    검증 항목:
    - M1 FROZEN 상태
    - M3 완료 상태
    """
    
    is_valid, errors = validate_prerequisites(context_id)
    
    if not is_valid:
        return {
            "can_execute": False,
            "reason": "PREREQUISITES_NOT_MET",
            "errors": errors,
            "action": "Please complete M1 freeze and M3 analysis first"
        }
    
    # M3 데이터 요약
    m3_data = get_m3_result_data(context_id)
    
    return {
        "can_execute": True,
        "message": "M4 can be executed",
        "m3_data_summary": {
            "recommended_type": m3_data.get('recommended_type'),
            "lh_pass_score": m3_data.get('lh_pass_score')
        }
    }
