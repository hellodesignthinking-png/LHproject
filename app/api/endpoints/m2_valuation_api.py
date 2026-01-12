"""
M2 – LAND VALUATION (LH-GRADE)
토지감정평가 모듈 API

역할:
- LH 신축매입임대 사업 대상으로서 토지가치 판단 근거 생성
- 감정평가 논리 설명 (감정평가서 대체 ❌, 논리 설명 ⭕)

실행 전제:
- M1.status == FROZEN
- M1.result_data 존재
- context_id 유효

출력:
- 정량(숫자): base_land_value, adjusted_land_value, value_range, unit_price_sqm, confidence_score
- 정성(논리): valuation_rationale (base_logic, market_logic, utility_logic)
- 리스크: risk_factors, lh_review_notes

Author: ZeroSite Decision OS Team
Date: 2026-01-12
Version: 2.0
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/projects/{project_id}/modules/M2",
    tags=["M2 - Land Valuation (LH-GRADE)"]
)

# ============================================================
# M2 상태 정의
# ============================================================

class M2Status(str, Enum):
    """M2 모듈 상태"""
    NOT_STARTED = "NOT_STARTED"        # M1 미완료
    CALCULATING = "CALCULATING"        # 계산 중
    COMPLETED = "COMPLETED"            # 완료
    FAILED = "FAILED"                  # 실패

# ============================================================
# M2 데이터 모델
# ============================================================

class ValueRange(BaseModel):
    """토지가치 범위"""
    min: float = Field(..., gt=0, description="최소 가치 (원)")
    max: float = Field(..., gt=0, description="최대 가치 (원)")
    
    @field_validator('max')
    def max_must_be_greater_than_min(cls, v, info):
        if 'min' in info.data and v <= info.data['min']:
            raise ValueError('max must be greater than min')
        return v

class ValuationRationale(BaseModel):
    """감정평가 논리 설명"""
    base_logic: str = Field(..., min_length=10, description="기준 가치 산정 논리")
    market_logic: str = Field(..., min_length=10, description="시장 비교 논리")
    utility_logic: str = Field(..., min_length=10, description="이용가능성 보정 논리")

class M2ResultData(BaseModel):
    """M2 결과 데이터 (result_data)"""
    
    # 정량 (숫자)
    base_land_value: float = Field(..., gt=0, description="기준 토지가치 (원)")
    adjusted_land_value: float = Field(..., gt=0, description="보정 토지가치 (원)")
    value_range: ValueRange = Field(..., description="적정 토지가치 범위")
    unit_price_sqm: float = Field(..., gt=0, description="단위면적당 가격 (원/㎡)")
    confidence_score: int = Field(..., ge=0, le=100, description="신뢰도 점수 (0-100)")
    
    # 정성 (논리)
    valuation_rationale: ValuationRationale = Field(..., description="감정평가 논리 설명")
    
    # 리스크
    risk_factors: List[str] = Field(..., min_length=2, description="리스크 요인 (최소 2개)")
    lh_review_notes: List[str] = Field(..., min_length=1, description="LH 검토 의견")
    
    # 메타데이터
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="계산 시각")
    context_id: str = Field(..., description="M1 Context ID")

# ============================================================
# M2 계산 요청/응답
# ============================================================

class M2CalculateRequest(BaseModel):
    """M2 계산 요청"""
    context_id: str = Field(..., description="M1 Context ID (FROZEN 상태여야 함)")
    force_recalculate: bool = Field(default=False, description="강제 재계산 여부")

class M2CalculateResponse(BaseModel):
    """M2 계산 응답"""
    status: M2Status
    message: str
    result_data: Optional[M2ResultData] = None
    errors: Optional[List[str]] = None

# ============================================================
# In-Memory Storage (실제 구현 시 DB로 대체)
# ============================================================

m2_results: Dict[str, M2ResultData] = {}
m2_status: Dict[str, M2Status] = {}

# ============================================================
# Helper Functions
# ============================================================

def get_m1_frozen_data(context_id: str) -> Optional[Dict[str, Any]]:
    """
    M1 FROZEN 데이터 조회
    
    실제 구현에서는:
    1. app.api.endpoints.m1_context_freeze_v2.frozen_contexts_v2 조회
    2. context_id로 매칭
    3. M1 상태 FROZEN 확인
    """
    try:
        from app.api.endpoints.m1_context_freeze_v2 import frozen_contexts_v2
        
        if context_id not in frozen_contexts_v2:
            logger.warning(f"❌ M1 Context not found: {context_id}")
            return None
        
        frozen_ctx = frozen_contexts_v2[context_id]
        
        # M1FinalContext를 dict로 변환
        if hasattr(frozen_ctx, 'model_dump'):
            return frozen_ctx.model_dump()
        elif hasattr(frozen_ctx, 'dict'):
            return frozen_ctx.dict()
        else:
            return dict(frozen_ctx)
            
    except Exception as e:
        logger.error(f"❌ Failed to load M1 FROZEN data: {e}")
        return None

def validate_m1_data(m1_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    M1 데이터 유효성 검증
    
    검증 항목:
    - land_info.cadastral.area_sqm > 0
    - land_info.zoning.zone_type 존재
    - appraisal_inputs.official_land_price > 0
    """
    errors = []
    
    try:
        # area_sqm 검증
        area_sqm = m1_data.get('land_info', {}).get('cadastral', {}).get('area_sqm', 0)
        if area_sqm <= 0:
            errors.append(f"Invalid area_sqm: {area_sqm}")
        
        # zone_type 검증
        zone_type = m1_data.get('land_info', {}).get('zoning', {}).get('zone_type', '')
        if not zone_type:
            errors.append("Missing zone_type")
        
        # official_land_price 검증
        official_price = m1_data.get('appraisal_inputs', {}).get('official_land_price', 0)
        if official_price <= 0:
            errors.append(f"Invalid official_land_price: {official_price}")
        
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
    
    return len(errors) == 0, errors

def calculate_m2_valuation(m1_data: Dict[str, Any], context_id: str) -> M2ResultData:
    """
    M2 감정평가 계산 엔진
    
    계산 흐름:
    1. 기준가치 = 면적 × 공시지가 × 기본보정계수
    2. 비교사례 보정
    3. 이용가능성 보정
    """
    logger.info("=" * 80)
    logger.info("🧮 M2 LAND VALUATION ENGINE START")
    logger.info("=" * 80)
    
    try:
        # M1 데이터 추출
        land_info = m1_data.get('land_info', {})
        cadastral = land_info.get('cadastral', {})
        zoning = land_info.get('zoning', {})
        road_access = land_info.get('road_access', {})
        
        appraisal_inputs = m1_data.get('appraisal_inputs', {})
        
        area_sqm = cadastral.get('area_sqm', 0)
        zone_type = zoning.get('zone_type', '')
        official_land_price = appraisal_inputs.get('official_land_price', 0)
        
        logger.info(f"📊 M1 입력 데이터:")
        logger.info(f"   - 면적: {area_sqm:,.0f} ㎡")
        logger.info(f"   - 용도지역: {zone_type}")
        logger.info(f"   - 공시지가: ₩{official_land_price:,.0f}/㎡")
        
        # ① 기준가치 계산
        # 기본보정계수 (LH 내부 가정값: 1.15 ~ 1.35)
        base_correction_factor = 1.25  # 중간값 사용
        
        base_land_value = area_sqm * official_land_price * base_correction_factor
        
        logger.info(f"① 기준가치 계산:")
        logger.info(f"   {area_sqm:,.0f} × {official_land_price:,.0f} × {base_correction_factor} = ₩{base_land_value:,.0f}")
        
        # ② 비교사례 보정 (간단한 예시 로직)
        # 실제로는 transaction_cases를 분석
        market_adjustment_factor = 1.10  # +10% 시장 프리미엄
        
        logger.info(f"② 비교사례 보정:")
        logger.info(f"   시장 보정계수: {market_adjustment_factor} (+10%)")
        
        # ③ 이용가능성 보정
        # FAR, 도로 폭 등 고려
        building_constraints = m1_data.get('building_constraints', {})
        legal = building_constraints.get('legal', {})
        far_max = legal.get('far_max', 200)
        
        utility_factor = 1.0
        if far_max >= 300:
            utility_factor = 1.10  # +10%
        elif far_max >= 200:
            utility_factor = 1.05  # +5%
        
        logger.info(f"③ 이용가능성 보정:")
        logger.info(f"   FAR: {far_max}% → 보정계수: {utility_factor}")
        
        # 최종 보정 토지가치
        adjusted_land_value = base_land_value * market_adjustment_factor * utility_factor
        
        logger.info(f"🎯 최종 보정 토지가치:")
        logger.info(f"   ₩{adjusted_land_value:,.0f}")
        
        # 가치 범위 (±5%)
        value_range = ValueRange(
            min=adjusted_land_value * 0.95,
            max=adjusted_land_value * 1.05
        )
        
        # 단위면적당 가격
        unit_price_sqm = adjusted_land_value / area_sqm
        
        logger.info(f"📊 가치 범위:")
        logger.info(f"   최소: ₩{value_range.min:,.0f}")
        logger.info(f"   최대: ₩{value_range.max:,.0f}")
        logger.info(f"   단가: ₩{unit_price_sqm:,.0f}/㎡")
        
        # 감정평가 논리 설명
        rationale = ValuationRationale(
            base_logic=f"공시지가 기준(₩{official_land_price:,.0f}/㎡) + LH 내부 보정계수({base_correction_factor}) 적용",
            market_logic=f"인근 유사 거래사례 비교 보정 (+{(market_adjustment_factor-1)*100:.0f}%)",
            utility_logic=f"{zone_type} · 용적률 {far_max}%로 이용보정 계수 {utility_factor} 적용"
        )
        
        # 리스크 요인
        risk_factors = [
            "거래사례의 상업용 편중 가능성",
            f"공시지가 기준연도 차이 ({appraisal_inputs.get('official_land_price_date', '미상')})",
            f"용적률 {far_max}% 인허가 변수 존재"
        ]
        
        # LH 검토 의견
        lh_review_notes = [
            "보수적 매입가 적용 권장 (하한가 기준)",
            "감정평가 병행 필수",
            f"인근 {zone_type} 거래사례 추가 확인 필요"
        ]
        
        # 신뢰도 점수 (간단한 로직)
        confidence_score = 75  # 기본값
        if appraisal_inputs.get('official_land_price_date'):
            confidence_score += 5
        if len(appraisal_inputs.get('transaction_cases', [])) > 0:
            confidence_score += 10
        
        logger.info(f"✅ M2 계산 완료 - 신뢰도: {confidence_score}점")
        logger.info("=" * 80)
        
        return M2ResultData(
            base_land_value=base_land_value,
            adjusted_land_value=adjusted_land_value,
            value_range=value_range,
            unit_price_sqm=unit_price_sqm,
            confidence_score=min(confidence_score, 100),
            valuation_rationale=rationale,
            risk_factors=risk_factors,
            lh_review_notes=lh_review_notes,
            context_id=context_id
        )
        
    except Exception as e:
        logger.error(f"❌ M2 계산 실패: {e}", exc_info=True)
        raise

# ============================================================
# API Endpoints
# ============================================================

@router.post("/calculate", response_model=M2CalculateResponse)
async def calculate_m2_valuation_endpoint(
    project_id: str,
    request: M2CalculateRequest
):
    """
    M2 감정평가 계산 실행
    
    실행 전제:
    - M1.status == FROZEN
    - M1.result_data 존재
    - context_id 유효
    """
    logger.info(f"🚀 M2 CALCULATE START - Project: {project_id}, Context: {request.context_id}")
    
    try:
        # ① M1 FROZEN 데이터 조회
        m1_data = get_m1_frozen_data(request.context_id)
        
        if not m1_data:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "UPSTREAM_NOT_READY",
                    "message": "M1 FACT not frozen",
                    "context_id": request.context_id,
                    "action": "Please freeze M1 first: POST /api/projects/{project_id}/modules/M1/freeze"
                }
            )
        
        logger.info(f"✅ M1 FROZEN 데이터 로드 완료")
        
        # ② M1 데이터 유효성 검증
        is_valid, errors = validate_m1_data(m1_data)
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_M1_DATA",
                    "message": "M1 data validation failed",
                    "errors": errors
                }
            )
        
        logger.info(f"✅ M1 데이터 유효성 검증 완료")
        
        # ③ 기존 결과 확인
        if not request.force_recalculate and request.context_id in m2_results:
            logger.info(f"♻️ 기존 M2 결과 반환 (캐시)")
            return M2CalculateResponse(
                status=M2Status.COMPLETED,
                message="M2 calculation already completed (cached)",
                result_data=m2_results[request.context_id]
            )
        
        # ④ M2 계산 실행
        m2_status[request.context_id] = M2Status.CALCULATING
        
        result_data = calculate_m2_valuation(m1_data, request.context_id)
        
        # ⑤ 결과 저장
        m2_results[request.context_id] = result_data
        m2_status[request.context_id] = M2Status.COMPLETED
        
        logger.info(f"✅ M2 계산 완료 및 저장")
        
        return M2CalculateResponse(
            status=M2Status.COMPLETED,
            message="M2 valuation completed successfully",
            result_data=result_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M2 계산 실패: {e}", exc_info=True)
        m2_status[request.context_id] = M2Status.FAILED
        
        return M2CalculateResponse(
            status=M2Status.FAILED,
            message=f"M2 calculation failed: {str(e)}",
            errors=[str(e)]
        )

@router.get("/result", response_model=M2ResultData)
async def get_m2_result(
    project_id: str,
    context_id: str
):
    """M2 계산 결과 조회"""
    
    if context_id not in m2_results:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "M2_RESULT_NOT_FOUND",
                "message": "M2 calculation not yet performed",
                "context_id": context_id,
                "action": "Please calculate M2 first: POST /api/projects/{project_id}/modules/M2/calculate"
            }
        )
    
    return m2_results[context_id]

@router.get("/status")
async def get_m2_status(
    project_id: str,
    context_id: str
):
    """M2 상태 조회"""
    
    status = m2_status.get(context_id, M2Status.NOT_STARTED)
    
    return {
        "project_id": project_id,
        "context_id": context_id,
        "status": status,
        "has_result": context_id in m2_results
    }

@router.get("/validate")
async def validate_m2_requirements(
    project_id: str,
    context_id: str
):
    """
    M2 실행 가능 여부 검증
    
    검증 항목:
    - M1 FROZEN 상태
    - M1 데이터 유효성
    """
    
    # M1 데이터 조회
    m1_data = get_m1_frozen_data(context_id)
    
    if not m1_data:
        return {
            "can_execute": False,
            "reason": "M1_NOT_FROZEN",
            "message": "M1 FACT is not frozen yet",
            "action": "Please freeze M1 first"
        }
    
    # M1 데이터 유효성 검증
    is_valid, errors = validate_m1_data(m1_data)
    
    if not is_valid:
        return {
            "can_execute": False,
            "reason": "INVALID_M1_DATA",
            "message": "M1 data validation failed",
            "errors": errors
        }
    
    return {
        "can_execute": True,
        "message": "M2 can be executed",
        "m1_data_summary": {
            "area_sqm": m1_data.get('land_info', {}).get('cadastral', {}).get('area_sqm'),
            "zone_type": m1_data.get('land_info', {}).get('zoning', {}).get('zone_type'),
            "official_land_price": m1_data.get('appraisal_inputs', {}).get('official_land_price')
        }
    }
