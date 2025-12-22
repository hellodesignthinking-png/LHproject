"""
ZeroSite Final Report Data Contract
====================================

Defines required data fields for each of 6 final report types.

PURPOSE:
- Enforce data integrity before report generation
- Validate that context_id contains ALL necessary module summaries
- Provide clear error messages when data is missing

Version: 1.0
Date: 2025-12-21
Author: ZeroSite Backend Team
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from app.models.final_report_types import FinalReportType


class RequiredDataField(Enum):
    """Required data fields for final reports"""
    # M2 필드
    M2_LAND_VALUE = "M2.land_value"
    M2_PRICE_PER_PYEONG = "M2.price_per_pyeong"
    M2_INTERPRETATION = "M2.interpretation"
    
    # M3 필드
    M3_RECOMMENDED_TYPE = "M3.recommended_type"
    M3_CONFIDENCE = "M3.confidence"
    
    # M4 필드
    M4_LEGAL_UNITS = "M4.legal_units"
    M4_RECOMMENDED_UNITS = "M4.recommended_units"
    M4_INCENTIVE_UNITS = "M4.incentive_units"
    
    # M5 필드
    M5_NPV = "M5.npv"
    M5_IRR = "M5.irr"
    M5_ROI = "M5.roi"
    M5_GRADE = "M5.grade"
    M5_JUDGMENT_GUIDE = "M5.judgment_guide"
    
    # M6 필드
    M6_APPROVAL_PROBABILITY = "M6.approval_probability"
    M6_GRADE = "M6.grade"
    M6_DECISION = "M6.decision"
    M6_NEXT_STEPS = "M6.next_steps"


# Data Contract: 각 보고서 타입별 필수 필드 정의
FINAL_REPORT_DATA_CONTRACTS: Dict[FinalReportType, Dict[str, Any]] = {
    # 1. 종합 최종보고서 (all_in_one)
    FinalReportType.ALL_IN_ONE: {
        "required_modules": ["M2", "M3", "M4", "M5", "M6"],
        "required_fields": [
            RequiredDataField.M2_LAND_VALUE,
            RequiredDataField.M3_RECOMMENDED_TYPE,
            RequiredDataField.M4_LEGAL_UNITS,
            RequiredDataField.M5_NPV,
            RequiredDataField.M6_APPROVAL_PROBABILITY,
        ],
        "critical_fields": [  # 이 필드가 없으면 보고서 생성 불가
            RequiredDataField.M6_DECISION,
            RequiredDataField.M5_GRADE,
        ],
        "min_data_coverage": 0.8,  # 80% 이상 필드 필요
    },
    
    # 2. 토지주 제출용 요약보고서 (landowner_summary)
    FinalReportType.LANDOWNER_SUMMARY: {
        "required_modules": ["M2", "M3", "M6"],
        "required_fields": [
            RequiredDataField.M2_LAND_VALUE,
            RequiredDataField.M3_RECOMMENDED_TYPE,
            RequiredDataField.M6_DECISION,
        ],
        "critical_fields": [
            RequiredDataField.M6_DECISION,
        ],
        "min_data_coverage": 0.7,  # 70% 이상 필드 필요
    },
    
    # 3. LH 제출용 기술검증 보고서 (lh_technical)
    FinalReportType.LH_TECHNICAL: {
        "required_modules": ["M3", "M4", "M6"],
        "required_fields": [
            RequiredDataField.M3_RECOMMENDED_TYPE,
            RequiredDataField.M4_LEGAL_UNITS,
            RequiredDataField.M4_INCENTIVE_UNITS,
            RequiredDataField.M6_APPROVAL_PROBABILITY,
        ],
        "critical_fields": [
            RequiredDataField.M4_LEGAL_UNITS,
            RequiredDataField.M6_DECISION,
        ],
        "min_data_coverage": 0.8,
    },
    
    # 4. 사업성·투자 검토 보고서 (financial_feasibility)
    FinalReportType.FINANCIAL_FEASIBILITY: {
        "required_modules": ["M2", "M4", "M5"],
        "required_fields": [
            RequiredDataField.M2_LAND_VALUE,
            RequiredDataField.M4_RECOMMENDED_UNITS,
            RequiredDataField.M5_NPV,
            RequiredDataField.M5_IRR,
            RequiredDataField.M5_ROI,
            RequiredDataField.M5_GRADE,
        ],
        "critical_fields": [
            RequiredDataField.M5_NPV,
            RequiredDataField.M5_GRADE,
        ],
        "min_data_coverage": 0.9,  # 투자 보고서는 90% 이상 필요
    },
    
    # 5. 사전 검토 리포트 (quick_check)
    FinalReportType.QUICK_CHECK: {
        "required_modules": ["M2", "M6"],
        "required_fields": [
            RequiredDataField.M2_LAND_VALUE,
            RequiredDataField.M6_DECISION,
        ],
        "critical_fields": [
            RequiredDataField.M6_DECISION,
        ],
        "min_data_coverage": 0.5,  # 빠른 체크는 50% 이상이면 OK
    },
    
    # 6. 설명용 프레젠테이션 (presentation)
    FinalReportType.PRESENTATION: {
        "required_modules": ["M2", "M3", "M4", "M5", "M6"],
        "required_fields": [
            RequiredDataField.M2_LAND_VALUE,
            RequiredDataField.M3_RECOMMENDED_TYPE,
            RequiredDataField.M4_LEGAL_UNITS,
            RequiredDataField.M5_GRADE,
            RequiredDataField.M6_DECISION,
        ],
        "critical_fields": [
            RequiredDataField.M6_DECISION,
        ],
        "min_data_coverage": 0.7,
    },
}


class DataContractValidationResult:
    """데이터 계약 검증 결과"""
    
    def __init__(
        self,
        is_valid: bool,
        report_type: FinalReportType,
        missing_modules: List[str],
        missing_fields: List[str],
        data_coverage: float,
        warnings: List[str],
        can_generate: bool
    ):
        self.is_valid = is_valid
        self.report_type = report_type
        self.missing_modules = missing_modules
        self.missing_fields = missing_fields
        self.data_coverage = data_coverage
        self.warnings = warnings
        self.can_generate = can_generate
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "report_type": self.report_type.value,
            "missing_modules": self.missing_modules,
            "missing_fields": self.missing_fields,
            "data_coverage_pct": round(self.data_coverage * 100, 1),
            "warnings": self.warnings,
            "can_generate": self.can_generate
        }


def validate_final_report_data(
    report_type: FinalReportType,
    module_summaries: Dict[str, Dict[str, Any]]
) -> DataContractValidationResult:
    """
    최종보고서 생성 전 데이터 계약 검증
    
    Args:
        report_type: 최종보고서 타입
        module_summaries: 모듈 요약 데이터 딕셔너리 (예: {"M2": {...}, "M3": {...}})
        
    Returns:
        DataContractValidationResult: 검증 결과
        
    Examples:
        >>> result = validate_final_report_data(
        ...     FinalReportType.ALL_IN_ONE,
        ...     {"M2": {...}, "M3": {...}}
        ... )
        >>> if not result.can_generate:
        ...     print(f"Cannot generate: {result.warnings}")
    """
    contract = FINAL_REPORT_DATA_CONTRACTS[report_type]
    required_modules = contract["required_modules"]
    required_fields = contract["required_fields"]
    critical_fields = contract["critical_fields"]
    min_coverage = contract["min_data_coverage"]
    
    # 1. 필수 모듈 체크
    missing_modules = [m for m in required_modules if m not in module_summaries]
    
    # 2. 필수 필드 체크
    missing_fields = []
    for field in required_fields:
        module_id, field_name = field.value.split(".", 1)
        if module_id not in module_summaries:
            missing_fields.append(field.value)
        else:
            module_data = module_summaries[module_id].get("summary", {})
            if field_name not in module_data or module_data[field_name] is None:
                missing_fields.append(field.value)
    
    # 3. Critical 필드 체크 (하나라도 없으면 보고서 생성 불가)
    missing_critical = []
    for field in critical_fields:
        module_id, field_name = field.value.split(".", 1)
        if module_id not in module_summaries:
            missing_critical.append(field.value)
        else:
            module_data = module_summaries[module_id].get("summary", {})
            if field_name not in module_data or module_data[field_name] is None:
                missing_critical.append(field.value)
    
    # 4. 데이터 커버리지 계산
    total_fields = len(required_fields)
    available_fields = total_fields - len(missing_fields)
    data_coverage = available_fields / total_fields if total_fields > 0 else 0.0
    
    # 5. 경고 메시지 생성
    warnings = []
    if missing_modules:
        warnings.append(f"필수 모듈 누락: {', '.join(missing_modules)}")
    if missing_critical:
        warnings.append(f"핵심 필드 누락: {', '.join(missing_critical)}")
    if data_coverage < min_coverage:
        warnings.append(
            f"데이터 커버리지 부족: {data_coverage*100:.1f}% < {min_coverage*100:.1f}% (최소 요구)"
        )
    
    # 6. 생성 가능 여부 판단
    can_generate = (
        len(missing_critical) == 0 and  # Critical 필드 모두 존재
        data_coverage >= min_coverage   # 최소 커버리지 충족
    )
    
    is_valid = len(warnings) == 0
    
    return DataContractValidationResult(
        is_valid=is_valid,
        report_type=report_type,
        missing_modules=missing_modules,
        missing_fields=missing_fields,
        data_coverage=data_coverage,
        warnings=warnings,
        can_generate=can_generate
    )


def get_user_friendly_error_message(validation_result: DataContractValidationResult) -> str:
    """
    사용자 친화적인 에러 메시지 생성
    
    Args:
        validation_result: 검증 결과
        
    Returns:
        str: 한국어 에러 메시지
    """
    if validation_result.can_generate:
        return "✅ 모든 데이터가 준비되었습니다."
    
    report_name_map = {
        FinalReportType.ALL_IN_ONE: "종합 최종보고서",
        FinalReportType.LANDOWNER_SUMMARY: "토지주 제출용 보고서",
        FinalReportType.LH_TECHNICAL: "LH 제출용 기술검증 보고서",
        FinalReportType.FINANCIAL_FEASIBILITY: "사업성·투자 검토 보고서",
        FinalReportType.QUICK_CHECK: "사전 검토 리포트",
        FinalReportType.PRESENTATION: "설명용 프레젠테이션",
    }
    
    report_name = report_name_map.get(validation_result.report_type, "최종보고서")
    
    error_parts = [f"❌ {report_name} 생성에 필요한 데이터가 부족합니다."]
    
    if validation_result.missing_modules:
        module_names = {
            "M2": "토지 감정가 분석",
            "M3": "LH 선호 주택 유형",
            "M4": "건축 규모 및 법규",
            "M5": "사업성 분석",
            "M6": "LH 심사 예측"
        }
        missing_names = [
            module_names.get(m, m) for m in validation_result.missing_modules
        ]
        error_parts.append(f"\n\n📋 필수 분석 모듈이 누락되었습니다:")
        error_parts.append("\n• " + "\n• ".join(missing_names))
    
    if validation_result.data_coverage < 1.0:
        error_parts.append(
            f"\n\n📊 데이터 완성도: {validation_result.data_coverage*100:.0f}%"
        )
    
    error_parts.append("\n\n💡 해결 방법:")
    error_parts.append("1. M1 단계부터 전체 분석을 다시 실행하세요.")
    error_parts.append("2. 모든 필수 항목을 입력했는지 확인하세요.")
    error_parts.append("3. 분석이 중단되지 않고 완료되었는지 확인하세요.")
    
    return "".join(error_parts)
