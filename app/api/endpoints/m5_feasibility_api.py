"""
M5 Feasibility & Risk Module API
=====================================

ZeroSite Decision OS - M5 모듈
목적: LH 매입 논리 중심의 사업성·리스크 검증

핵심 역할:
- "이 사업이 돈이 되느냐"가 아니라
- "LH가 왜 이 사업을 매입해도 위험하지 않은가"를 증명

Author: ZeroSite Decision OS
Date: 2026-01-12
Module: M5 – FEASIBILITY & RISK (LH-SAFE)
"""

from fastapi import APIRouter, HTTPException, Path, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio

# ========================================
# Router 초기화
# ========================================
router = APIRouter(
    prefix="/api/projects/{project_id}/modules/M5",
    tags=["M5 - Feasibility & Risk (LH-SAFE)"]
)

# ========================================
# Pydantic Models
# ========================================

class RiskItem(BaseModel):
    """리스크 항목"""
    risk: str = Field(..., description="리스크 명")
    level: str = Field(..., description="리스크 수준: LOW/MEDIUM/HIGH")
    probability: str = Field(..., description="발생 가능성")
    impact: str = Field(..., description="영향도")
    mitigation: str = Field(..., description="대응 전략")

class CostBreakdown(BaseModel):
    """총사업비 구성"""
    land_cost: float = Field(..., description="토지비 (원)")
    construction_cost: float = Field(..., description="건축비 (원)")
    design_supervision: float = Field(..., description="설계·감리비 (원)")
    contingency: float = Field(..., description="예비비 (원)")
    total_cost: float = Field(..., description="총사업비 (원)")

class LHPurchaseStructure(BaseModel):
    """LH 매입 구조"""
    base_price: float = Field(..., description="기본 매입가 (원)")
    community_bonus: float = Field(0.0, description="커뮤니티 가점 (원)")
    total_purchase_price: float = Field(..., description="총 매입가 (원)")
    buffer_ratio: float = Field(..., description="안전 마진 비율 (%)")

class M5ResultData(BaseModel):
    """M5 출력 데이터"""
    cost_breakdown: CostBreakdown
    lh_purchase: LHPurchaseStructure
    risk_summary: List[RiskItem]
    stability_assessment: str = Field(..., description="안정성 평가")
    feasibility_conclusion: str = Field(..., description="사업성 결론")
    calculated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class M5CalculateRequest(BaseModel):
    """M5 계산 요청"""
    context_id: str = Field(..., description="M1 Context ID (FROZEN)")
    force_recalculate: bool = Field(False, description="강제 재계산 여부")
    custom_params: Optional[Dict[str, Any]] = Field(None, description="사용자 정의 파라미터")

class M5StatusResponse(BaseModel):
    """M5 상태 응답"""
    project_id: str
    context_id: str
    status: str  # NOT_STARTED, IN_PROGRESS, COMPLETED, FAILED
    calculated_at: Optional[str]
    error: Optional[str]

# ========================================
# In-Memory Storage (실제 구현 시 DB 사용)
# ========================================
M5_CACHE: Dict[str, Dict[str, Any]] = {}

# ========================================
# LH 표준 단가 테이블 (실제 데이터로 교체 필요)
# ========================================
LH_STANDARD_COSTS = {
    "construction_unit_price": 2800000,  # 원/㎡ (표준 건축비)
    "design_supervision_ratio": 0.09,     # 건축비의 9%
    "contingency_ratio": 0.05,            # 총사업비의 5%
}

LH_PURCHASE_UNIT_PRICE = {
    "청년 매입임대": 3200000,    # 원/㎡
    "신혼부부 매입임대": 3500000,
    "고령자 복지주택": 3800000,
    "일반 공공임대": 3000000,
    "역세권 청년주택": 3400000,
}

# ========================================
# Helper Functions
# ========================================

def get_m1_frozen_data(context_id: str) -> Dict[str, Any]:
    """M1 FROZEN 데이터 가져오기"""
    # 실제 구현: DB에서 M1 result_data 조회
    # Fail Fast: M1이 FROZEN이 아니면 예외 발생
    
    # Mock 데이터 (실제 구현 시 DB 연동)
    return {
        "area_sqm": 1500,
        "zone_type": "준주거지역",
        "bcr": 60,
        "far": 300,
        "official_land_price": 25000000,
        "frozen_at": "2026-01-12T10:00:00Z"
    }

def get_m2_result(context_id: str) -> Dict[str, Any]:
    """M2 토지 감정평가 결과 가져오기"""
    # Mock 데이터
    return {
        "adjusted_land_value": 42000000000,  # 420억
        "value_range": {
            "lower": 38000000000,
            "upper": 46000000000
        },
        "unit_price_sqm": 28000000,
        "confidence_score": 0.82
    }

def get_m3_result(context_id: str) -> Dict[str, Any]:
    """M3 공급유형 적합성 결과 가져오기"""
    # Mock 데이터
    return {
        "recommended_type": "청년 매입임대",
        "lh_pass_score": 85,
        "policy_alignment": "청년 주거 안정 정책과 부합"
    }

def get_m4_result(context_id: str) -> Dict[str, Any]:
    """M4 건축 규모 결과 가져오기"""
    # Mock 데이터
    return {
        "lh_recommended": {
            "total_floor_area": 10200,  # ㎡
            "units": 240,
            "floors_estimated": 12
        },
        "parking_plan": {
            "applied": 90
        }
    }

def calculate_cost_breakdown(
    m1_data: Dict[str, Any],
    m2_data: Dict[str, Any],
    m4_data: Dict[str, Any]
) -> CostBreakdown:
    """총사업비 구조 계산 (보수 기준)"""
    
    # 1. 토지비 (M2 적정 매입가 하단값)
    land_cost = m2_data["value_range"]["lower"]
    
    # 2. 건축비 (LH 표준 건축비 × 연면적)
    total_floor_area = m4_data["lh_recommended"]["total_floor_area"]
    construction_cost = total_floor_area * LH_STANDARD_COSTS["construction_unit_price"]
    
    # 3. 설계·감리비 (건축비의 9%)
    design_supervision = construction_cost * LH_STANDARD_COSTS["design_supervision_ratio"]
    
    # 4. 예비비 (총사업비의 5% - 재귀적 계산)
    subtotal = land_cost + construction_cost + design_supervision
    contingency = subtotal * (LH_STANDARD_COSTS["contingency_ratio"] / (1 - LH_STANDARD_COSTS["contingency_ratio"]))
    
    # 5. 총사업비
    total_cost = land_cost + construction_cost + design_supervision + contingency
    
    return CostBreakdown(
        land_cost=land_cost,
        construction_cost=construction_cost,
        design_supervision=design_supervision,
        contingency=contingency,
        total_cost=total_cost
    )

def calculate_lh_purchase(
    m3_data: Dict[str, Any],
    m4_data: Dict[str, Any],
    cost_breakdown: CostBreakdown
) -> LHPurchaseStructure:
    """LH 매입가 구조 계산"""
    
    # 1. 기본 매입가 (연면적 × 표준 매입단가)
    housing_type = m3_data["recommended_type"]
    unit_price = LH_PURCHASE_UNIT_PRICE.get(housing_type, 3000000)
    total_floor_area = m4_data["lh_recommended"]["total_floor_area"]
    
    base_price = total_floor_area * unit_price
    
    # 2. 커뮤니티 가점 보정 (향후 M7 연계)
    community_bonus = 0.0  # M7 구현 후 연동
    
    # 3. 총 매입가
    total_purchase_price = base_price + community_bonus
    
    # 4. 안전 마진 비율 (%)
    buffer_ratio = ((total_purchase_price - cost_breakdown.total_cost) / cost_breakdown.total_cost) * 100
    
    return LHPurchaseStructure(
        base_price=base_price,
        community_bonus=community_bonus,
        total_purchase_price=total_purchase_price,
        buffer_ratio=round(buffer_ratio, 2)
    )

def identify_risks(
    m1_data: Dict[str, Any],
    m2_data: Dict[str, Any],
    m4_data: Dict[str, Any],
    buffer_ratio: float
) -> List[RiskItem]:
    """리스크 식별 (필수 3~5개)"""
    
    risks = []
    
    # 1. 공사비 변동 리스크
    risks.append(RiskItem(
        risk="공사비 상승",
        level="MEDIUM",
        probability="중간",
        impact="총사업비 5~10% 증가 가능",
        mitigation="표준형 설계 적용 및 예비비 5% 확보"
    ))
    
    # 2. 인허가 리스크
    if m1_data.get("regulation_summary"):
        risks.append(RiskItem(
            risk="인허가 지연",
            level="LOW",
            probability="낮음",
            impact="사업 일정 1~2개월 지연",
            mitigation="보수적 건축 규모(법정의 85%) 적용으로 허가 가능성 높음"
        ))
    
    # 3. LH 매입가 조정 리스크
    if buffer_ratio < 5:
        risks.append(RiskItem(
            risk="LH 매입가 하향 조정",
            level="HIGH",
            probability="높음",
            impact="사업 수익성 악화",
            mitigation="매입가 협상 시 커뮤니티 가점 활용"
        ))
    elif buffer_ratio > 15:
        risks.append(RiskItem(
            risk="과도한 사업자 마진",
            level="MEDIUM",
            probability="중간",
            impact="LH 심사 시 부정적 평가",
            mitigation="총사업비 재검토 및 커뮤니티 투자 확대"
        ))
    else:
        risks.append(RiskItem(
            risk="LH 매입가 조정",
            level="LOW",
            probability="낮음",
            impact="안전 마진(8~12%) 적정 범위",
            mitigation="현재 구조 유지"
        ))
    
    # 4. 민원·커뮤니티 갈등 리스크
    risks.append(RiskItem(
        risk="민원 및 지역 갈등",
        level="MEDIUM",
        probability="중간",
        impact="사업 지연 및 조건 추가",
        mitigation="M7 커뮤니티 계획 수립 및 주민 설명회 개최"
    ))
    
    # 5. 장기 운영 리스크
    risks.append(RiskItem(
        risk="장기 운영 안정성",
        level="LOW",
        probability="낮음",
        impact="LH 직영 운영으로 안정적",
        mitigation="입주자 선정 기준 및 관리 규정 명문화"
    ))
    
    return risks

def assess_stability(
    cost_breakdown: CostBreakdown,
    lh_purchase: LHPurchaseStructure,
    risks: List[RiskItem]
) -> str:
    """안정성 평가"""
    
    buffer = lh_purchase.buffer_ratio
    high_risks = [r for r in risks if r.level == "HIGH"]
    
    if buffer < 5:
        return "⚠️ 주의: 안전 마진 부족. LH 매입 구조 재검토 필요."
    elif buffer > 15:
        return "⚠️ 주의: 과도한 마진. LH 심사에서 부정적 평가 가능."
    elif high_risks:
        return "⚠️ 주의: 고위험 요소 존재. 리스크 완화 전략 필수."
    else:
        return "✅ 안정적: LH 매입 기준에서 적정 범위. 사업 추진 가능."

def generate_feasibility_conclusion(
    stability_assessment: str,
    buffer_ratio: float
) -> str:
    """사업성 결론"""
    
    if "안정적" in stability_assessment:
        return f"LH 매입 구조 기준으로 사업성 확보. 안전 마진 {buffer_ratio:.1f}%로 리스크 흡수 가능."
    else:
        return f"현재 구조에서 리스크 요소 존재. 안전 마진 {buffer_ratio:.1f}%이나 보완 필요."

# ========================================
# API Endpoints
# ========================================

@router.post(
    "/calculate",
    response_model=M5ResultData,
    summary="M5 사업성·리스크 계산",
    description="""
    M5 사업성·리스크 검증 모듈 계산을 실행합니다.
    
    **전제 조건:**
    - M1 FACT FROZEN
    - M2 토지 감정평가 완료
    - M3 공급유형 확정
    - M4 건축 규모 확정
    
    **계산 내용:**
    1. 총사업비 구조 (보수 기준)
    2. LH 매입가 구조
    3. 리스크 식별 (3~5개)
    4. 안정성 평가
    
    **핵심 원칙:**
    - "수익 극대화"가 아닌 "실패하지 않을 이유" 증명
    - LH 매입 논리 중심
    - 안전 마진 8~12% 적정 범위
    """
)
async def calculate_m5(
    project_id: str = Path(..., description="프로젝트 ID"),
    request: M5CalculateRequest = Body(...)
):
    """M5 계산 실행"""
    
    context_id = request.context_id
    
    # 1. M1 FROZEN 체크
    try:
        m1_data = get_m1_frozen_data(context_id)
        if not m1_data.get("frozen_at"):
            raise HTTPException(
                status_code=400,
                detail="M1이 FROZEN 상태가 아닙니다. M5를 실행할 수 없습니다."
            )
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"M1 데이터를 찾을 수 없습니다: {str(e)}"
        )
    
    # 2. M2, M3, M4 결과 가져오기
    try:
        m2_data = get_m2_result(context_id)
        m3_data = get_m3_result(context_id)
        m4_data = get_m4_result(context_id)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"M2/M3/M4 데이터를 찾을 수 없습니다: {str(e)}"
        )
    
    # 3. 총사업비 계산
    cost_breakdown = calculate_cost_breakdown(m1_data, m2_data, m4_data)
    
    # 4. LH 매입가 계산
    lh_purchase = calculate_lh_purchase(m3_data, m4_data, cost_breakdown)
    
    # 5. 리스크 식별
    risks = identify_risks(m1_data, m2_data, m4_data, lh_purchase.buffer_ratio)
    
    # 6. 안정성 평가
    stability_assessment = assess_stability(cost_breakdown, lh_purchase, risks)
    
    # 7. 사업성 결론
    feasibility_conclusion = generate_feasibility_conclusion(
        stability_assessment,
        lh_purchase.buffer_ratio
    )
    
    # 8. 결과 생성
    result_data = M5ResultData(
        cost_breakdown=cost_breakdown,
        lh_purchase=lh_purchase,
        risk_summary=risks,
        stability_assessment=stability_assessment,
        feasibility_conclusion=feasibility_conclusion
    )
    
    # 9. 캐시에 저장
    cache_key = f"{project_id}:{context_id}"
    M5_CACHE[cache_key] = {
        "status": "COMPLETED",
        "result_data": result_data.dict(),
        "calculated_at": result_data.calculated_at
    }
    
    return result_data

@router.get(
    "/result",
    response_model=M5ResultData,
    summary="M5 계산 결과 조회",
    description="M5 사업성·리스크 검증 결과를 조회합니다."
)
async def get_m5_result(
    project_id: str = Path(..., description="프로젝트 ID"),
    context_id: str = ...
):
    """M5 결과 조회"""
    
    cache_key = f"{project_id}:{context_id}"
    
    if cache_key not in M5_CACHE:
        raise HTTPException(
            status_code=404,
            detail="M5 계산 결과를 찾을 수 없습니다. /calculate를 먼저 실행하세요."
        )
    
    cached = M5_CACHE[cache_key]
    
    if cached["status"] != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail=f"M5 계산이 완료되지 않았습니다. 상태: {cached['status']}"
        )
    
    return M5ResultData(**cached["result_data"])

@router.get(
    "/status",
    response_model=M5StatusResponse,
    summary="M5 계산 상태 확인",
    description="M5 사업성·리스크 검증 상태를 확인합니다."
)
async def get_m5_status(
    project_id: str = Path(..., description="프로젝트 ID"),
    context_id: str = ...
):
    """M5 상태 확인"""
    
    cache_key = f"{project_id}:{context_id}"
    
    if cache_key not in M5_CACHE:
        return M5StatusResponse(
            project_id=project_id,
            context_id=context_id,
            status="NOT_STARTED",
            calculated_at=None,
            error=None
        )
    
    cached = M5_CACHE[cache_key]
    
    return M5StatusResponse(
        project_id=project_id,
        context_id=context_id,
        status=cached["status"],
        calculated_at=cached.get("calculated_at"),
        error=cached.get("error")
    )

@router.get(
    "/validate",
    summary="M5 실행 가능 여부 검증",
    description="""
    M5 사업성·리스크 검증을 실행할 수 있는지 검증합니다.
    
    **검증 항목:**
    - M1 FROZEN 여부
    - M2 결과 존재 여부
    - M3 결과 존재 여부
    - M4 결과 존재 여부
    """
)
async def validate_m5(
    project_id: str = Path(..., description="프로젝트 ID"),
    context_id: str = ...
):
    """M5 실행 가능 여부 검증"""
    
    validation_result = {
        "can_execute": False,
        "checks": {},
        "errors": []
    }
    
    # 1. M1 FROZEN 체크
    try:
        m1_data = get_m1_frozen_data(context_id)
        validation_result["checks"]["m1_frozen"] = bool(m1_data.get("frozen_at"))
        if not validation_result["checks"]["m1_frozen"]:
            validation_result["errors"].append("M1이 FROZEN 상태가 아닙니다.")
    except Exception as e:
        validation_result["checks"]["m1_frozen"] = False
        validation_result["errors"].append(f"M1 데이터 없음: {str(e)}")
    
    # 2. M2 결과 체크
    try:
        m2_data = get_m2_result(context_id)
        validation_result["checks"]["m2_completed"] = bool(m2_data.get("adjusted_land_value"))
    except Exception:
        validation_result["checks"]["m2_completed"] = False
        validation_result["errors"].append("M2 결과가 없습니다.")
    
    # 3. M3 결과 체크
    try:
        m3_data = get_m3_result(context_id)
        validation_result["checks"]["m3_completed"] = bool(m3_data.get("recommended_type"))
    except Exception:
        validation_result["checks"]["m3_completed"] = False
        validation_result["errors"].append("M3 결과가 없습니다.")
    
    # 4. M4 결과 체크
    try:
        m4_data = get_m4_result(context_id)
        validation_result["checks"]["m4_completed"] = bool(m4_data.get("lh_recommended"))
    except Exception:
        validation_result["checks"]["m4_completed"] = False
        validation_result["errors"].append("M4 결과가 없습니다.")
    
    # 5. 최종 판단
    validation_result["can_execute"] = all([
        validation_result["checks"].get("m1_frozen"),
        validation_result["checks"].get("m2_completed"),
        validation_result["checks"].get("m3_completed"),
        validation_result["checks"].get("m4_completed")
    ])
    
    return validation_result
