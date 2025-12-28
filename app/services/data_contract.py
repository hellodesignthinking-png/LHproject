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
    데이터 바인딩 실패 예외 (Phase 3.5E: User-Friendly + Missing Paths)
    
    발생 조건:
    - assembled_data 구조 불완전
    - 필수 모듈 데이터 누락
    - 출력물에 N/A 포함
    - 기본값 0 사용
    
    효과: 보고서 생성 즉시 중단
    """
    
    def __init__(
        self, 
        technical_message: str, 
        user_message: str = None,
        missing_paths: list = None
    ):
        """
        Args:
            technical_message: 내부 개발자용 상세 메시지
            user_message: 외부 사용자용 요약 메시지 (optional)
            missing_paths: 누락된 데이터 경로 리스트 (e.g., ["modules.M3.summary.preferred_type"])
        """
        self.technical_message = technical_message
        self.user_message = user_message or self._get_default_user_message()
        self.missing_paths = missing_paths or []
        super().__init__(technical_message)
    
    def _get_default_user_message(self) -> str:
        """기본 사용자 친화적 메시지"""
        return (
            "필수 분석 데이터(M2~M5) 중 일부가 누락되어 "
            "보고서를 생성할 수 없습니다. "
            "토지 정보 또는 입력 데이터를 다시 확인해 주세요."
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """API 응답용 딕셔너리"""
        return {
            "error": "DATA_BINDING_ERROR",
            "message": self.user_message,
            "technical_message": self.technical_message,
            "missing_paths": self.missing_paths
        }


class DataValidationError(Exception):
    """
    데이터 검증 실패 예외 (Phase 3.5E: User-Friendly)
    
    발생 조건:
    - M6 결과 없음
    - modules 키 없음
    - M2~M5 중 하나라도 없음
    """
    
    def __init__(self, technical_message: str, user_message: str = None):
        """
        Args:
            technical_message: 내부 개발자용 상세 메시지
            user_message: 외부 사용자용 요약 메시지 (optional)
        """
        self.technical_message = technical_message
        self.user_message = user_message or self._get_default_user_message()
        super().__init__(technical_message)
    
    def _get_default_user_message(self) -> str:
        """기본 사용자 친화적 메시지"""
        return (
            "필수 분석 데이터(M2~M5) 중 일부가 누락되어 "
            "보고서를 생성할 수 없습니다. "
            "토지 정보 또는 입력 데이터를 다시 확인해 주세요."
        )


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
    assembled_data 유효성 검증 (Phase 3.5D FAIL FAST + Missing Paths)
    
    Args:
        data: 검증할 데이터
        strict: True이면 예외 발생, False이면 Boolean 반환
    
    Raises:
        DataValidationError: strict=True이고 검증 실패 시
    
    Returns:
        True if valid, False otherwise (strict=False일 때만)
    """
    errors = []
    missing_paths = []
    
    # FAIL 조건 1: M6 result 없음
    if "m6_result" not in data:
        errors.append("M6 result is missing")
        missing_paths.append("m6_result")
    
    # FAIL 조건 2: modules 없음
    if "modules" not in data:
        errors.append("modules key is missing")
        missing_paths.append("modules")
    
    # FAIL 조건 3: M2~M5 중 하나라도 없음
    required_modules = ["M2", "M3", "M4", "M5"]
    modules = data.get("modules", {})
    
    for module_id in required_modules:
        if module_id not in modules:
            errors.append(f"Module {module_id} is missing")
            missing_paths.append(f"modules.{module_id}")
        else:
            # FAIL 조건 4: summary/details/raw_data 키 중 하나라도 없음
            module_data = modules[module_id]
            required_keys = ["summary", "details", "raw_data"]
            
            for key in required_keys:
                if key not in module_data:
                    errors.append(f"Module {module_id} missing key: {key}")
                    missing_paths.append(f"modules.{module_id}.{key}")
    
    # 검증 결과 처리
    if errors:
        # 🔴 Phase 3.5E: 사용자 친화적 메시지 + Missing Paths
        technical_msg = "\n".join([f"  - {err}" for err in errors])
        full_technical_msg = f"Data validation failed:\n{technical_msg}"
        
        user_msg = (
            "필수 분석 데이터(M2~M5) 중 일부가 누락되어 "
            "보고서를 생성할 수 없습니다. "
            "토지 정보 또는 입력 데이터를 다시 확인해 주세요."
        )
        
        if strict:
            raise DataValidationError(full_technical_msg, user_msg)
        else:
            return False
    
    return True


def check_for_na_in_output(output_str: str) -> None:
    """
    출력물에 N/A 포함 여부 검사 (Phase 3.5E: User-Friendly)
    
    Args:
        output_str: 검사할 출력 문자열 (HTML, JSON 등)
    
    Raises:
        DataBindingError: N/A 발견 시
    """
    if "N/A" in output_str or "n/a" in output_str:
        technical_msg = (
            "Output contains 'N/A'. This indicates missing data binding. "
            "Report generation aborted."
        )
        user_msg = (
            "필수 분석 데이터(M2~M5) 중 일부가 누락되어 "
            "보고서를 생성할 수 없습니다. "
            "토지 정보 또는 입력 데이터를 다시 확인해 주세요."
        )
        raise DataBindingError(technical_msg, user_msg)


def check_for_default_zeros(data: Dict[str, Any], context: str = "") -> None:
    """
    숫자 0이 기본값으로 사용되는지 검사 (Phase 3.5E: User-Friendly)
    
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
            technical_msg = (
                f"Suspicious default value detected: {key}=0 in {context}. "
                "This may indicate missing data binding. Report generation aborted."
            )
            user_msg = (
                "필수 분석 데이터(M2~M5) 중 일부가 누락되어 "
                "보고서를 생성할 수 없습니다. "
                "토지 정보 또는 입력 데이터를 다시 확인해 주세요."
            )
            raise DataBindingError(technical_msg, user_msg)


# ===== 🔥 NEW: 필수 필드 검증 (100% 실데이터 기반) =====

def validate_m3_required_fields(m3_summary: Dict[str, Any], strict: bool = True) -> bool:
    """
    M3 필수 필드 검증 (N/A 금지, 0점 방지)
    
    Required fields:
    - preferred_type: str (NOT "N/A", NOT "", NOT None)
    - stability_grade: str (A/B/C)
    - confidence_score: float (0~100, NOT 0)
    - key_reasons: list[str] (len >= 3)
    
    Args:
        m3_summary: M3 summary 데이터
        strict: True이면 예외 발생
    
    Raises:
        DataBindingError: 필수 필드 누락 또는 N/A 값
    
    Returns:
        True if valid
    """
    errors = []
    missing_paths = []
    
    # preferred_type 검증
    preferred_type = m3_summary.get("preferred_type")
    if not preferred_type or preferred_type in ("N/A", "", "null"):
        errors.append("M3.preferred_type is missing or N/A")
        missing_paths.append("modules.M3.summary.preferred_type")
    
    # stability_grade 검증
    stability_grade = m3_summary.get("stability_grade")
    if not stability_grade or stability_grade not in ("A", "B", "C"):
        errors.append(f"M3.stability_grade invalid: {stability_grade}")
        missing_paths.append("modules.M3.summary.stability_grade")
    
    # confidence_score 검증
    confidence_score = m3_summary.get("confidence_score", 0)
    if confidence_score == 0:
        errors.append("M3.confidence_score is 0 (must be > 0)")
        missing_paths.append("modules.M3.summary.confidence_score")
    
    # key_reasons 검증
    key_reasons = m3_summary.get("key_reasons", [])
    if not key_reasons or len(key_reasons) < 3:
        errors.append(f"M3.key_reasons has {len(key_reasons)} items (need >= 3)")
        missing_paths.append("modules.M3.summary.key_reasons")
    
    if errors and strict:
        technical_msg = "M3 필수 필드 검증 실패:\n" + "\n".join([f"  - {err}" for err in errors])
        user_msg = "M3(LH 선호유형) 분석 결과가 불완전합니다. 분석을 다시 실행해 주세요."
        raise DataBindingError(technical_msg, user_msg, missing_paths)
    
    return len(errors) == 0


def validate_m4_required_fields(m4_summary: Dict[str, Any], strict: bool = True) -> bool:
    """
    M4 필수 필드 검증 (N/A 금지, 0% 방지)
    
    Required fields:
    - total_units: int (> 0)
    - gross_floor_area_sqm: float (> 0)
    - far_ratio: float (> 0)
    - coverage_ratio: float (> 0)
    
    Args:
        m4_summary: M4 summary 데이터
        strict: True이면 예외 발생
    
    Raises:
        DataBindingError: 필수 필드 누락 또는 0 값
    
    Returns:
        True if valid
    """
    errors = []
    missing_paths = []
    
    # total_units 검증
    total_units = m4_summary.get("total_units", 0)
    if total_units <= 0:
        errors.append(f"M4.total_units is {total_units} (must be > 0)")
        missing_paths.append("modules.M4.summary.total_units")
    
    # gross_floor_area_sqm 검증
    gross_floor_area = m4_summary.get("gross_floor_area", 0) or m4_summary.get("gross_floor_area_sqm", 0)
    if gross_floor_area <= 0:
        errors.append(f"M4.gross_floor_area is {gross_floor_area} (must be > 0)")
        missing_paths.append("modules.M4.summary.gross_floor_area")
    
    # far_ratio 검증
    far_ratio = m4_summary.get("far_ratio", 0)
    if far_ratio <= 0:
        errors.append(f"M4.far_ratio is {far_ratio}% (must be > 0)")
        missing_paths.append("modules.M4.summary.far_ratio")
    
    # coverage_ratio 검증
    coverage_ratio = m4_summary.get("coverage_ratio", 0)
    if coverage_ratio <= 0:
        errors.append(f"M4.coverage_ratio is {coverage_ratio}% (must be > 0)")
        missing_paths.append("modules.M4.summary.coverage_ratio")
    
    if errors and strict:
        technical_msg = "M4 필수 필드 검증 실패:\n" + "\n".join([f"  - {err}" for err in errors])
        user_msg = "M4(건축규모 분석) 결과가 불완전합니다. 용적률, 세대수 등을 다시 확인해 주세요."
        raise DataBindingError(technical_msg, user_msg, missing_paths)
    
    return len(errors) == 0


def validate_m6_required_fields(m6_result: Dict[str, Any], strict: bool = True) -> bool:
    """
    M6 필수 필드 검증 (N/A 금지, narrative 필수)
    
    Required fields:
    - decision: str (GO/CONDITIONAL/NO-GO, NOT "N/A")
    - grade: str (A/B/C/D)
    - lh_score_total: float (> 0)
    - decision_rationale: list[str] (len >= 3)
    - conclusion_text: str (len >= 40)
    - approval_probability: float or None (0~100, 0 금지)
    
    Args:
        m6_result: M6 result 데이터
        strict: True이면 예외 발생
    
    Raises:
        DataBindingError: 필수 필드 누락 또는 N/A 값
    
    Returns:
        True if valid
    """
    errors = []
    missing_paths = []
    
    # decision 검증
    decision = m6_result.get("decision") or m6_result.get("judgement")
    if not decision or decision == "N/A":
        errors.append("M6.decision is missing or N/A")
        missing_paths.append("m6_result.decision")
    elif decision not in ("GO", "CONDITIONAL", "NO-GO", "NOGO"):
        errors.append(f"M6.decision invalid: {decision}")
        missing_paths.append("m6_result.decision")
    
    # grade 검증
    grade = m6_result.get("grade")
    if not grade or grade not in ("A", "B", "C", "D", "F"):
        errors.append(f"M6.grade invalid: {grade}")
        missing_paths.append("m6_result.grade")
    
    # lh_score_total 검증
    lh_score_total = m6_result.get("lh_score_total", 0)
    if lh_score_total <= 0:
        errors.append(f"M6.lh_score_total is {lh_score_total} (must be > 0)")
        missing_paths.append("m6_result.lh_score_total")
    
    # decision_rationale 검증
    decision_rationale = m6_result.get("decision_rationale") or m6_result.get("deduction_reasons", [])
    if not decision_rationale or len(decision_rationale) < 3:
        errors.append(f"M6.decision_rationale has {len(decision_rationale)} items (need >= 3)")
        missing_paths.append("m6_result.decision_rationale")
    
    # conclusion_text 검증
    conclusion_text = m6_result.get("conclusion") or m6_result.get("conclusion_text", "")
    if not conclusion_text or len(conclusion_text) < 40:
        errors.append(f"M6.conclusion is too short: {len(conclusion_text)} chars (need >= 40)")
        missing_paths.append("m6_result.conclusion")
    
    # approval_probability 검증 (0% 고정 금지, None은 허용)
    approval_probability = m6_result.get("approval_probability")
    if approval_probability is not None and approval_probability == 0:
        errors.append("M6.approval_probability is 0% (not allowed, use None for '미산정')")
        missing_paths.append("m6_result.approval_probability")
    
    if errors and strict:
        technical_msg = "M6 필수 필드 검증 실패:\n" + "\n".join([f"  - {err}" for err in errors])
        user_msg = "M6(LH 심사예측) 결과가 불완전합니다. 판정 근거, 결론 등을 다시 확인해 주세요."
        raise DataBindingError(technical_msg, user_msg, missing_paths)
    
    return len(errors) == 0


def validate_all_required_fields(assembled_data: Dict[str, Any], strict: bool = True) -> bool:
    """
    M3/M4/M6 모든 필수 필드 검증
    
    Args:
        assembled_data: 전체 assembled_data
        strict: True이면 예외 발생
    
    Raises:
        DataBindingError: 필수 필드 누락
    
    Returns:
        True if all valid
    """
    # M3 검증
    m3_summary = assembled_data.get("modules", {}).get("M3", {}).get("summary", {})
    if m3_summary:
        validate_m3_required_fields(m3_summary, strict)
    
    # M4 검증
    m4_summary = assembled_data.get("modules", {}).get("M4", {}).get("summary", {})
    if m4_summary:
        validate_m4_required_fields(m4_summary, strict)
    
    # M6 검증
    m6_result = assembled_data.get("m6_result", {})
    if m6_result:
        validate_m6_required_fields(m6_result, strict)
    
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
