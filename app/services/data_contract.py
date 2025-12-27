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


# ===== Phase 3.5D FAIL FAST Exceptions =====

class DataBindingError(Exception):
    """
    데이터 바인딩 실패 예외
    
    발생 조건:
    - assembled_data 구조 불완전
    - 필수 모듈 데이터 누락
    - 출력물에 N/A 포함
    - 기본값 0 사용
    
    효과: 보고서 생성 즉시 중단
    """
    pass


class DataValidationError(Exception):
    """
    데이터 검증 실패 예외
    
    발생 조건:
    - M6 결과 없음
    - modules 키 없음
    - M2~M5 중 하나라도 없음
    """
    pass


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


def validate_assembled_data(data: Dict[str, Any], strict: bool = True) -> bool:
    """
    assembled_data 유효성 검증 (Phase 3.5D FAIL FAST)
    
    Args:
        data: 검증할 데이터
        strict: True이면 예외 발생, False이면 Boolean 반환
    
    Raises:
        DataValidationError: strict=True이고 검증 실패 시
    
    Returns:
        True if valid, False otherwise (strict=False일 때만)
    """
    errors = []
    
    # FAIL 조건 1: M6 result 없음
    if "m6_result" not in data:
        errors.append("M6 result is missing")
    
    # FAIL 조건 2: modules 없음
    if "modules" not in data:
        errors.append("modules key is missing")
    
    # FAIL 조건 3: M2~M5 중 하나라도 없음
    required_modules = ["M2", "M3", "M4", "M5"]
    modules = data.get("modules", {})
    
    for module_id in required_modules:
        if module_id not in modules:
            errors.append(f"Module {module_id} is missing")
        else:
            # FAIL 조건 4: summary/details/raw_data 키 중 하나라도 없음
            module_data = modules[module_id]
            required_keys = ["summary", "details", "raw_data"]
            
            for key in required_keys:
                if key not in module_data:
                    errors.append(f"Module {module_id} missing key: {key}")
    
    # 검증 결과 처리
    if errors:
        error_msg = "\n".join([f"  - {err}" for err in errors])
        full_msg = f"Data validation failed:\n{error_msg}"
        
        if strict:
            raise DataValidationError(full_msg)
        else:
            return False
    
    return True


def check_for_na_in_output(output_str: str) -> None:
    """
    출력물에 N/A 포함 여부 검사 (Phase 3.5D FAIL FAST)
    
    Args:
        output_str: 검사할 출력 문자열 (HTML, JSON 등)
    
    Raises:
        DataBindingError: N/A 발견 시
    """
    if "N/A" in output_str or "n/a" in output_str:
        raise DataBindingError(
            "Output contains 'N/A'. This indicates missing data binding. "
            "Report generation aborted."
        )


def check_for_default_zeros(data: Dict[str, Any], context: str = "") -> None:
    """
    숫자 0이 기본값으로 사용되는지 검사 (Phase 3.5D FAIL FAST)
    
    Args:
        data: 검사할 데이터
        context: 에러 메시지용 컨텍스트
    
    Raises:
        DataBindingError: 의심스러운 0 값 발견 시
    """
    # 의심스러운 0 값들
    suspicious_keys = [
        "land_value",  # 토지가치 0은 의심
        "total_units",  # 세대수 0은 의심
        "npv_public_krw",  # NPV 0은 의심 (음수는 가능)
    ]
    
    for key in suspicious_keys:
        if key in data and data[key] == 0:
            raise DataBindingError(
                f"Suspicious default value detected: {key}=0 in {context}. "
                "This may indicate missing data binding. Report generation aborted."
            )


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
