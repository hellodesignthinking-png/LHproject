"""
M3 – HOUSING TYPE SUITABILITY (LH-GRADE)
공급유형 적합성 모듈 API

역할:
- LH 심사 통과 확률이 가장 높은 공급유형 선정
- 정책·입지·가격·인허가·운영 측면 종합 평가
- "떨어질 확률이 가장 낮은 유형" 선택 (최적 유형 ❌)

실행 전제:
- M1.status == FROZEN
- M2.status == COMPLETED
- M2.result_data 존재

출력:
- recommended_type: 추천 공급유형 (1개)
- lh_pass_score: LH 통과 점수 (0-100)
- ranking: 전체 유형 순위
- rejection_reasons: 탈락 유형 사유

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

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/projects/{project_id}/modules/M3",
    tags=["M3 - Housing Type Suitability (LH-GRADE)"]
)

# ============================================================
# M3 상태 정의
# ============================================================

class M3Status(str, Enum):
    """M3 모듈 상태"""
    NOT_STARTED = "NOT_STARTED"        # M2 미완료
    ANALYZING = "ANALYZING"            # 분석 중
    COMPLETED = "COMPLETED"            # 완료
    FAILED = "FAILED"                  # 실패

# ============================================================
# M3 공급유형 정의 (LH 실무 기준)
# ============================================================

class HousingType(str, Enum):
    """LH 공급유형 Pool (고정)"""
    T1 = "청년 매입임대"
    T2 = "신혼부부 매입임대"
    T3 = "고령자 복지주택"
    T4 = "역세권 청년주택"
    T5 = "일반 공공임대"

# ============================================================
# M3 데이터 모델
# ============================================================

class HousingTypeScore(BaseModel):
    """공급유형별 점수"""
    type: str = Field(..., description="공급유형")
    total_score: int = Field(..., ge=0, le=100, description="총점 (0-100)")
    
    # 세부 점수
    policy_score: int = Field(..., ge=0, le=30, description="정책 적합성 (30점)")
    location_score: int = Field(..., ge=0, le=25, description="입지·수요 일치 (25점)")
    price_score: int = Field(..., ge=0, le=20, description="토지가격 부담 (20점)")
    permit_score: int = Field(..., ge=0, le=15, description="인허가 리스크 (15점)")
    operation_score: int = Field(..., ge=0, le=10, description="운영·민원 안정성 (10점)")
    
    # 논리 설명
    rationale: str = Field(..., min_length=20, description="선정/탈락 논리")

class M3ResultData(BaseModel):
    """M3 결과 데이터 (result_data)"""
    
    # 추천 결과
    recommended_type: str = Field(..., description="추천 공급유형 (1개)")
    lh_pass_score: int = Field(..., ge=0, le=100, description="LH 통과 점수")
    
    # 전체 순위
    ranking: List[HousingTypeScore] = Field(..., min_length=3, description="전체 유형 순위")
    
    # 탈락 사유
    rejection_reasons: Dict[str, str] = Field(..., description="탈락 유형별 사유")
    
    # LH 설득용 서술 (자동 생성)
    lh_persuasion_text: str = Field(..., min_length=50, description="LH 설득용 문장")
    
    # 메타데이터
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="분석 시각")
    context_id: str = Field(..., description="M1 Context ID")
    
    # M2 연계 데이터 (참조용)
    m2_land_value: float = Field(..., gt=0, description="M2 보정 토지가치 (원)")
    m2_unit_price: float = Field(..., gt=0, description="M2 단가 (원/㎡)")

# ============================================================
# M3 분석 요청/응답
# ============================================================

class M3AnalyzeRequest(BaseModel):
    """M3 분석 요청"""
    context_id: str = Field(..., description="M1 Context ID (FROZEN 상태)")
    force_recalculate: bool = Field(default=False, description="강제 재분석 여부")

class M3AnalyzeResponse(BaseModel):
    """M3 분석 응답"""
    status: M3Status
    message: str
    result_data: Optional[M3ResultData] = None
    errors: Optional[List[str]] = None

# ============================================================
# In-Memory Storage
# ============================================================

m3_results: Dict[str, M3ResultData] = {}
m3_status: Dict[str, M3Status] = {}

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

def get_m2_result_data(context_id: str) -> Optional[Dict[str, Any]]:
    """M2 결과 데이터 조회"""
    try:
        from app.api.endpoints.m2_valuation_api import m2_results
        
        if context_id not in m2_results:
            logger.warning(f"❌ M2 Result not found: {context_id}")
            return None
        
        result = m2_results[context_id]
        
        if hasattr(result, 'model_dump'):
            return result.model_dump()
        elif hasattr(result, 'dict'):
            return result.dict()
        else:
            return dict(result)
            
    except Exception as e:
        logger.error(f"❌ Failed to load M2 result: {e}")
        return None

def validate_prerequisites(context_id: str) -> tuple[bool, List[str]]:
    """
    M3 실행 전제 조건 검증
    
    검증 항목:
    - M1 FROZEN 상태
    - M2 완료 상태
    """
    errors = []
    
    # M1 검증
    m1_data = get_m1_frozen_data(context_id)
    if not m1_data:
        errors.append("M1 FACT not frozen")
    
    # M2 검증
    m2_data = get_m2_result_data(context_id)
    if not m2_data:
        errors.append("M2 valuation not completed")
    elif m2_data.get('adjusted_land_value', 0) <= 0:
        errors.append("M2 land value is invalid")
    
    return len(errors) == 0, errors

# ============================================================
# M3 핵심 분석 엔진: LH 통과 확률 계산
# ============================================================

def calculate_housing_type_scores(
    m1_data: Dict[str, Any],
    m2_data: Dict[str, Any],
    context_id: str
) -> M3ResultData:
    """
    M3 공급유형 적합성 분석 엔진
    
    LH 통과 점수 프레임 (100점):
    - 정책 적합성: 30점
    - 입지·수요 일치: 25점
    - 토지가격 부담: 20점
    - 인허가 리스크: 15점
    - 운영·민원 안정성: 10점
    """
    logger.info("=" * 80)
    logger.info("🧮 M3 HOUSING TYPE SUITABILITY ENGINE START")
    logger.info("=" * 80)
    
    try:
        # M1 데이터 추출
        land_info = m1_data.get('land_info', {})
        cadastral = land_info.get('cadastral', {})
        zoning = land_info.get('zoning', {})
        address_info = land_info.get('address', {})
        
        area_sqm = cadastral.get('area_sqm', 0)
        zone_type = zoning.get('zone_type', '')
        admin_dong = address_info.get('dong', '')
        
        # M2 데이터 추출
        adjusted_land_value = m2_data.get('adjusted_land_value', 0)
        unit_price_sqm = m2_data.get('unit_price_sqm', 0)
        risk_factors = m2_data.get('risk_factors', [])
        
        logger.info(f"📊 입력 데이터:")
        logger.info(f"   - 면적: {area_sqm:,.0f} ㎡")
        logger.info(f"   - 용도지역: {zone_type}")
        logger.info(f"   - 토지가치: ₩{adjusted_land_value:,.0f}")
        logger.info(f"   - 단가: ₩{unit_price_sqm:,.0f}/㎡")
        
        # ============================================================
        # 5가지 공급유형 점수 계산
        # ============================================================
        
        scores = []
        
        # T1: 청년 매입임대
        t1_policy = 27  # 도심 청년 정책 부합
        t1_location = 22  # 역세권·직주근접
        t1_price = 15 if unit_price_sqm < 30000000 else 12  # 가격 부담
        t1_permit = 13  # 인허가
        t1_operation = 8  # 운영 안정성
        t1_total = t1_policy + t1_location + t1_price + t1_permit + t1_operation
        
        scores.append(HousingTypeScore(
            type="청년 매입임대",
            total_score=t1_total,
            policy_score=t1_policy,
            location_score=t1_location,
            price_score=t1_price,
            permit_score=t1_permit,
            operation_score=t1_operation,
            rationale=f"{zone_type} 도심 접근성 우수, 청년 정책 부합도 높음"
        ))
        
        # T2: 신혼부부 매입임대
        t2_policy = 25  # 신혼부부 정책
        t2_location = 20  # 주거 환경
        t2_price = 14 if unit_price_sqm < 30000000 else 11
        t2_permit = 12
        t2_operation = 7
        t2_total = t2_policy + t2_location + t2_price + t2_permit + t2_operation
        
        scores.append(HousingTypeScore(
            type="신혼부부 매입임대",
            total_score=t2_total,
            policy_score=t2_policy,
            location_score=t2_location,
            price_score=t2_price,
            permit_score=t2_permit,
            operation_score=t2_operation,
            rationale="주거 환경 양호, 신혼부부 수요 존재"
        ))
        
        # T3: 고령자 복지주택
        t3_policy = 20  # 고령자 정책
        t3_location = 15  # 입지 특성 불일치
        t3_price = 12
        t3_permit = 10
        t3_operation = 6
        t3_total = t3_policy + t3_location + t3_price + t3_permit + t3_operation
        
        scores.append(HousingTypeScore(
            type="고령자 복지주택",
            total_score=t3_total,
            policy_score=t3_policy,
            location_score=t3_location,
            price_score=t3_price,
            permit_score=t3_permit,
            operation_score=t3_operation,
            rationale="입지 특성과 고령자 수요 불일치"
        ))
        
        # T4: 역세권 청년주택
        t4_policy = 22
        t4_location = 20
        t4_price = 10 if unit_price_sqm > 30000000 else 15  # 가격 과도 시 감점
        t4_permit = 11
        t4_operation = 7
        t4_total = t4_policy + t4_location + t4_price + t4_permit + t4_operation
        
        scores.append(HousingTypeScore(
            type="역세권 청년주택",
            total_score=t4_total,
            policy_score=t4_policy,
            location_score=t4_location,
            price_score=t4_price,
            permit_score=t4_permit,
            operation_score=t4_operation,
            rationale="토지가격 부담 존재" if unit_price_sqm > 30000000 else "역세권 입지 활용 가능"
        ))
        
        # T5: 일반 공공임대
        t5_policy = 24
        t5_location = 18
        t5_price = 13
        t5_permit = 12
        t5_operation = 7
        t5_total = t5_policy + t5_location + t5_price + t5_permit + t5_operation
        
        scores.append(HousingTypeScore(
            type="일반 공공임대",
            total_score=t5_total,
            policy_score=t5_policy,
            location_score=t5_location,
            price_score=t5_price,
            permit_score=t5_permit,
            operation_score=t5_operation,
            rationale="범용성 높으나 정책 차별성 부족"
        ))
        
        # 점수 순 정렬
        scores.sort(key=lambda x: x.total_score, reverse=True)
        
        # 추천 유형 (1등)
        recommended = scores[0]
        
        logger.info(f"🏆 추천 공급유형: {recommended.type} ({recommended.total_score}점)")
        
        # 탈락 사유 (70점 미만)
        rejection_reasons = {}
        for score in scores:
            if score.total_score < 70:
                rejection_reasons[score.type] = score.rationale
        
        logger.info(f"❌ 탈락 유형: {len(rejection_reasons)}개")
        
        # LH 설득용 서술 자동 생성
        persuasion_text = (
            f"본 대상지는 {zone_type} 지역으로 "
            f"도심 접근성과 직주근접성이 우수하여 "
            f"{recommended.type} 유형이 "
            f"정책 적합성({recommended.policy_score}점) 및 "
            f"운영 안정성({recommended.operation_score}점) 측면에서 "
            f"가장 높은 심사 통과 가능성을 보입니다."
        )
        
        logger.info(f"✅ M3 분석 완료")
        logger.info("=" * 80)
        
        return M3ResultData(
            recommended_type=recommended.type,
            lh_pass_score=recommended.total_score,
            ranking=scores,
            rejection_reasons=rejection_reasons,
            lh_persuasion_text=persuasion_text,
            context_id=context_id,
            m2_land_value=adjusted_land_value,
            m2_unit_price=unit_price_sqm
        )
        
    except Exception as e:
        logger.error(f"❌ M3 분석 실패: {e}", exc_info=True)
        raise

# ============================================================
# API Endpoints
# ============================================================

@router.post("/analyze", response_model=M3AnalyzeResponse)
async def analyze_housing_type_suitability(
    project_id: str,
    request: M3AnalyzeRequest
):
    """
    M3 공급유형 적합성 분석 실행
    
    실행 전제:
    - M1.status == FROZEN
    - M2.status == COMPLETED
    """
    logger.info(f"🚀 M3 ANALYZE START - Project: {project_id}, Context: {request.context_id}")
    
    try:
        # ① 전제 조건 검증
        is_valid, errors = validate_prerequisites(request.context_id)
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "PREREQUISITES_NOT_MET",
                    "message": "M3 cannot run: prerequisites not met",
                    "errors": errors,
                    "action": "Please complete M1 freeze and M2 calculation first"
                }
            )
        
        logger.info(f"✅ 전제 조건 검증 완료")
        
        # ② 기존 결과 확인
        if not request.force_recalculate and request.context_id in m3_results:
            logger.info(f"♻️ 기존 M3 결과 반환 (캐시)")
            return M3AnalyzeResponse(
                status=M3Status.COMPLETED,
                message="M3 analysis already completed (cached)",
                result_data=m3_results[request.context_id]
            )
        
        # ③ M1, M2 데이터 로드
        m1_data = get_m1_frozen_data(request.context_id)
        m2_data = get_m2_result_data(request.context_id)
        
        # ④ M3 분석 실행
        m3_status[request.context_id] = M3Status.ANALYZING
        
        result_data = calculate_housing_type_scores(m1_data, m2_data, request.context_id)
        
        # ⑤ 결과 저장
        m3_results[request.context_id] = result_data
        m3_status[request.context_id] = M3Status.COMPLETED
        
        logger.info(f"✅ M3 분석 완료 및 저장")
        
        return M3AnalyzeResponse(
            status=M3Status.COMPLETED,
            message="M3 housing type analysis completed successfully",
            result_data=result_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M3 분석 실패: {e}", exc_info=True)
        m3_status[request.context_id] = M3Status.FAILED
        
        return M3AnalyzeResponse(
            status=M3Status.FAILED,
            message=f"M3 analysis failed: {str(e)}",
            errors=[str(e)]
        )

@router.get("/result", response_model=M3ResultData)
async def get_m3_result(
    project_id: str,
    context_id: str
):
    """M3 분석 결과 조회"""
    
    if context_id not in m3_results:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "M3_RESULT_NOT_FOUND",
                "message": "M3 analysis not yet performed",
                "context_id": context_id,
                "action": "Please analyze M3 first: POST /api/projects/{project_id}/modules/M3/analyze"
            }
        )
    
    return m3_results[context_id]

@router.get("/status")
async def get_m3_status(
    project_id: str,
    context_id: str
):
    """M3 상태 조회"""
    
    status = m3_status.get(context_id, M3Status.NOT_STARTED)
    
    return {
        "project_id": project_id,
        "context_id": context_id,
        "status": status,
        "has_result": context_id in m3_results
    }

@router.get("/validate")
async def validate_m3_prerequisites(
    project_id: str,
    context_id: str
):
    """
    M3 실행 가능 여부 검증
    
    검증 항목:
    - M1 FROZEN 상태
    - M2 완료 상태
    """
    
    is_valid, errors = validate_prerequisites(context_id)
    
    if not is_valid:
        return {
            "can_execute": False,
            "reason": "PREREQUISITES_NOT_MET",
            "errors": errors,
            "action": "Please complete M1 freeze and M2 calculation first"
        }
    
    # M2 데이터 요약
    m2_data = get_m2_result_data(context_id)
    
    return {
        "can_execute": True,
        "message": "M3 can be executed",
        "m2_data_summary": {
            "adjusted_land_value": m2_data.get('adjusted_land_value'),
            "unit_price_sqm": m2_data.get('unit_price_sqm'),
            "risk_factors_count": len(m2_data.get('risk_factors', []))
        }
    }
