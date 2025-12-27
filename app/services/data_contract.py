"""
ZeroSite 4.0 Data Contract — 단일 표준 스키마
=============================================

목적: 모든 Renderer/Generator/API가 동일한 데이터 구조 사용

원칙:
1. 단일 진실의 원천: assembled_data
2. 모든 컴포넌트는 이 스키마만 사용
3. 축약키/flat구조/커스텀키 금지

Author: ZeroSite Team
Date: 2025-12-27
Version: 1.0 (Phase 3.5D)
"""

from typing import Dict, Any, TypedDict, Optional


class M6Result(TypedDict, total=False):
    """M6 판단 결과 (Single Source of Truth)"""
    lh_score_total: float
    judgement: str  # GO, CONDITIONAL, NOGO
    grade: str  # A, B, C, D
    fatal_reject: bool
    deduction_reasons: list
    improvement_points: list
    section_scores: Dict[str, float]
    conclusion: str


class ModuleData(TypedDict, total=False):
    """모듈 데이터 표준 구조"""
    summary: Dict[str, Any]  # 핵심 요약 데이터
    details: Dict[str, Any]  # 상세 데이터
    raw_data: Dict[str, Any]  # 원시 데이터


class AssembledData(TypedDict):
    """
    ZeroSite 4.0 표준 Data Contract
    
    모든 Renderer/Generator/API가 반드시 이 구조 사용
    """
    m6_result: M6Result  # Single Source of Truth
    modules: Dict[str, ModuleData]  # M2, M3, M4, M5


# ===== 표준 스키마 예시 =====

STANDARD_SCHEMA_EXAMPLE = {
    "m6_result": {
        "lh_score_total": 75.0,
        "judgement": "CONDITIONAL",
        "grade": "B",
        "fatal_reject": False,
        "deduction_reasons": ["주차 효율 부족 -4점"],
        "improvement_points": ["+6점: 주차 확보"],
        "section_scores": {
            "policy": 15,
            "location": 18,
            "construction": 12,
            "price": 10,
            "business": 10
        },
        "conclusion": "본 사업지는 ZeroSite v4.0 M6 기준에 따라 보완 조건 충족 시 LH 매입이 가능한 사업지로 판단된다."
    },
    "modules": {
        "M2": {
            "summary": {
                "land_value": 6081933538,
                "land_value_per_pyeong": 50000000,
                "confidence_pct": 85.5
            },
            "details": {
                "transaction_cases": [],
                "price_range": {}
            },
            "raw_data": {
                "official_price": 0,
                "cadastral_info": {}
            }
        },
        "M3": {
            "summary": {
                "recommended_type": "youth",
                "total_score": 85.5,
                "confidence": "high"
            },
            "details": {},
            "raw_data": {}
        },
        "M4": {
            "summary": {
                "total_units": 20,
                "gross_area_sqm": 1500,
                "parking_spaces": 15
            },
            "details": {},
            "raw_data": {}
        },
        "M5": {
            "summary": {
                "npv_public_krw": 792999999,
                "irr_pct": 12.5,
                "roi_pct": 15.2,
                "financial_grade": "B"
            },
            "details": {},
            "raw_data": {}
        }
    }
}


# ===== 헬퍼 함수 =====

def get_module_summary(assembled_data: AssembledData, module_id: str) -> Dict[str, Any]:
    """
    모듈 summary 데이터 안전하게 가져오기
    
    Args:
        assembled_data: 표준 스키마 데이터
        module_id: M2, M3, M4, M5
    
    Returns:
        summary 데이터 (없으면 빈 dict)
    """
    return assembled_data.get("modules", {}).get(module_id, {}).get("summary", {})


def get_module_details(assembled_data: AssembledData, module_id: str) -> Dict[str, Any]:
    """모듈 details 데이터 안전하게 가져오기"""
    return assembled_data.get("modules", {}).get(module_id, {}).get("details", {})


def validate_assembled_data(data: Dict[str, Any]) -> bool:
    """
    assembled_data 유효성 검증
    
    Returns:
        True if valid, False otherwise
    """
    # M6 result 필수
    if "m6_result" not in data:
        return False
    
    # modules 필수
    if "modules" not in data:
        return False
    
    # 최소 M2 필수
    if "M2" not in data["modules"]:
        return False
    
    return True


# ===== 금지 패턴 =====

# ❌ 금지 1: 축약키
# data["m2"]  # NO!
# data["modules"]["M2"]  # YES!

# ❌ 금지 2: flat 구조
# data["land_value"]  # NO!
# data["modules"]["M2"]["summary"]["land_value"]  # YES!

# ❌ 금지 3: 커스텀 키
# data["my_custom_key"]  # NO!
# 표준 스키마만 사용  # YES!


if __name__ == "__main__":
    print("=== ZeroSite 4.0 Data Contract ===\n")
    print("표준 스키마:")
    import json
    print(json.dumps(STANDARD_SCHEMA_EXAMPLE, indent=2, ensure_ascii=False))
    print("\n✅ Data Contract 로드 완료")
