"""
ZeroSite v3.3 Module Configuration
3-Layer 분리 원칙에 따른 모듈 설정

Layer 구조:
- FACT Layer: 감정평가 결과 (수정 불가)
- INTERPRETATION Layer: 토지진단 및 분석 (파라미터만 수정 가능)
- JUDGMENT Layer: LH 판단 및 재무 분석 (임계값만 수정 가능)
- REPORT Layer: 보고서 생성 (자유롭게 수정 가능)
"""

from typing import Dict, List, Any


MODULE_CONFIG = {
    # ========== FACT Layer - 수정 불가 ==========
    "appraisal_context": {
        "version": "1.0",
        "editable": False,
        "hash_protected": True,
        "description": "감정평가 결과 - AppraisalContextLock으로 보호",
        "locked_fields": [
            "calculation.final_appraised_total",
            "calculation.land_area_sqm",
            "zoning.confirmed_type",
            "zoning.floor_area_ratio",
            "zoning.building_coverage_ratio",
            "premium.total_premium_rate",
            "official_land_price.standard_price_per_sqm"
        ],
        "access_mode": "READ_ONLY"
    },
    
    # ========== INTERPRETATION Layer - 파라미터만 수정 가능 ==========
    "land_diagnosis": {
        "version": "1.2",
        "editable_fields": [
            "calculation_parameters",
            "thresholds",
            "weights"
        ],
        "locked_fields": [
            "output_schema",
            "calculation_logic",
            "data_validation_rules"
        ],
        "description": "토지진단 - 분석 로직은 고정, 파라미터만 조정 가능",
        "access_mode": "PARAMETER_ONLY"
    },
    
    "ch4_scoring": {
        "version": "1.1",
        "editable_fields": [
            "weights",              # 공급유형별 가중치
            "thresholds",           # 수요 판단 임계값
            "regional_factors"      # 지역별 보정 계수
        ],
        "locked_fields": [
            "score_categories",     # 점수 카테고리 (청년/신혼/고령/일반/공공임대)
            "score_formula",        # 점수 계산 공식
            "normalization_logic"   # 정규화 로직
        ],
        "description": "CH4 수요 분석 - 가중치와 임계값만 조정 가능",
        "access_mode": "PARAMETER_ONLY"
    },
    
    "risk_matrix": {
        "version": "1.0",
        "editable_fields": [
            "risk_items"  # 리스크 항목 추가만 가능
        ],
        "locked_fields": [
            "existing_items",       # 기존 리스크 항목은 삭제 불가
            "evaluation_logic",     # 평가 로직
            "probability_levels",   # 발생확률 레벨 (LOW/MEDIUM/HIGH)
            "impact_levels"         # 영향도 레벨 (LOW/MEDIUM/HIGH)
        ],
        "description": "리스크 매트릭스 - 항목 추가만 가능, 기존 항목 삭제 불가",
        "access_mode": "ADD_ONLY"
    },
    
    # ========== JUDGMENT Layer - 임계값만 수정 가능 ==========
    "financial_engine": {
        "version": "1.1",
        "editable_fields": [
            "interest_rate",        # 금리
            "scenario_values",      # 시나리오 분석 파라미터
            "discount_rate",        # 할인율
            "contingency_rate"      # 예비비 비율
        ],
        "locked_fields": [
            "irr_formula",          # IRR 계산 공식
            "roi_formula",          # ROI 계산 공식
            "npv_formula",          # NPV 계산 공식
            "payback_logic"         # 회수 기간 계산 로직
        ],
        "description": "재무 분석 - 금리/할인율만 조정 가능, 공식은 고정",
        "access_mode": "THRESHOLD_ONLY"
    },
    
    "lh_judgment": {
        "version": "1.0",
        "editable_fields": [
            "thresholds"  # Pass/Fail 임계값
        ],
        "locked_fields": [
            "pass_fail_logic",      # Pass/Fail 판정 로직
            "deduction_rules",      # 감점 규칙
            "adequacy_formula"      # 적정성 판단 공식
        ],
        "threshold_values": {
            "roi_pass": 15.0,       # ROI 15% 이상 PASS
            "roi_conditional": 10.0, # ROI 10% 이상 CONDITIONAL
            "far_minimum": 200.0,   # 용적률 최소 200%
            "adequacy_tolerance": 0.1  # 매입가 적정성 허용 오차 ±10%
        },
        "description": "LH 판단 - 임계값만 조정 가능, 판정 로직은 고정",
        "access_mode": "THRESHOLD_ONLY"
    },
    
    # ========== REPORT Layer - 자유롭게 수정 가능 ==========
    "report_templates": {
        "pre_report": {
            "version": "3.3",
            "fully_editable": True,
            "description": "Pre-Report (2 pages) - 영업 도구",
            "pages": 2,
            "target_audience": ["landowner", "investor"]
        },
        "comprehensive": {
            "version": "3.3",
            "fully_editable": True,
            "description": "Comprehensive Report (15-20 pages) - 정식 계약 후 제공",
            "pages": "15-20",
            "target_audience": ["landowner", "investor"]
        },
        "lh_decision": {
            "version": "3.3",
            "fully_editable": True,
            "description": "LH Decision Report (4 parts) - LH 제출용",
            "pages": "TBD",
            "target_audience": ["landowner", "lh"]
        },
        "investor": {
            "version": "1.0",
            "fully_editable": True,
            "description": "Investor Report - 투자자 대상 수익성 분석",
            "pages": "10-12",
            "target_audience": ["investor"],
            "status": "COMPLETE"
        },
        "land_price": {
            "version": "1.0",
            "fully_editable": True,
            "description": "Land Price Report - 토지가격 분석",
            "pages": "5-8",
            "target_audience": ["landowner"],
            "status": "COMPLETE"
        },
        "full_report": {
            "version": "8.8",
            "fully_editable": True,
            "description": "Full Report (60 pages) - FACT/INTERPRETATION/JUDGMENT 전체",
            "pages": 60,
            "target_audience": ["all"]
        },
        "internal": {
            "version": "1.0",
            "fully_editable": True,
            "description": "Internal Assessment - 내부 검토용",
            "pages": "5",
            "target_audience": ["internal"],
            "status": "COMPLETE"
        }
    }
}


# 보고서-모듈 의존성
REPORT_DEPENDENCIES = {
    "pre_report": [
        "appraisal_context",
        "land_diagnosis",
        "ch4_scoring"
    ],
    "comprehensive": [
        "appraisal_context",
        "land_diagnosis",
        "ch4_scoring",
        "risk_matrix",
        "financial_engine",
        "lh_judgment"
    ],
    "lh_decision": [
        "appraisal_context",
        "land_diagnosis",
        "ch4_scoring",
        "risk_matrix",
        "lh_judgment"
    ],
    "investor": [
        "appraisal_context",
        "land_diagnosis",
        "risk_matrix",
        "financial_engine"
    ],
    "land_price": [
        "appraisal_context",
        "land_diagnosis",
        "lh_judgment"
    ],
    "internal": [
        "appraisal_context",
        "land_diagnosis",
        "ch4_scoring",
        "risk_matrix",
        "financial_engine",
        "lh_judgment"
    ],
    "full_report": [
        "appraisal_context",
        "land_diagnosis",
        "ch4_scoring",
        "risk_matrix",
        "financial_engine",
        "lh_judgment"
    ],
    "internal": [
        "appraisal_context",
        "land_diagnosis",
        "ch4_scoring",
        "risk_matrix",
        "financial_engine",
        "lh_judgment"
    ]
}


# 모듈 수정 권한 체크 함수
def can_modify_field(module_name: str, field_name: str) -> bool:
    """
    특정 모듈의 필드 수정 가능 여부 확인
    
    Args:
        module_name: 모듈 이름 (예: 'appraisal_context', 'ch4_scoring')
        field_name: 필드 이름 (예: 'calculation.final_appraised_total')
    
    Returns:
        수정 가능 여부 (True/False)
    """
    if module_name not in MODULE_CONFIG:
        return False
    
    module = MODULE_CONFIG[module_name]
    
    # FACT Layer (appraisal_context)는 모두 불가
    if module_name == "appraisal_context":
        return False
    
    # editable_fields 체크
    editable_fields = module.get("editable_fields", [])
    locked_fields = module.get("locked_fields", [])
    
    # locked_fields에 있으면 수정 불가
    if field_name in locked_fields:
        return False
    
    # editable_fields에 있으면 수정 가능
    if field_name in editable_fields:
        return True
    
    # fully_editable이면 모두 가능
    if module.get("fully_editable", False):
        return True
    
    return False


def get_module_dependencies(report_type: str) -> List[str]:
    """
    특정 보고서 타입에 필요한 모듈 목록 반환
    
    Args:
        report_type: 보고서 타입 (예: 'pre_report', 'comprehensive')
    
    Returns:
        의존 모듈 리스트
    """
    return REPORT_DEPENDENCIES.get(report_type, [])


def get_access_mode(module_name: str) -> str:
    """
    모듈의 접근 모드 반환
    
    Args:
        module_name: 모듈 이름
    
    Returns:
        접근 모드 ('READ_ONLY', 'PARAMETER_ONLY', 'THRESHOLD_ONLY', 'ADD_ONLY', 'FULL_EDIT')
    """
    if module_name not in MODULE_CONFIG:
        return "UNKNOWN"
    
    module = MODULE_CONFIG[module_name]
    
    if module.get("fully_editable", False):
        return "FULL_EDIT"
    
    return module.get("access_mode", "READ_ONLY")


def validate_module_modification(module_name: str, modifications: Dict[str, Any]) -> Dict[str, Any]:
    """
    모듈 수정 요청 검증
    
    Args:
        module_name: 모듈 이름
        modifications: 수정 요청 (key: 필드명, value: 새 값)
    
    Returns:
        검증 결과 {'valid': bool, 'errors': List[str], 'warnings': List[str]}
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    if module_name not in MODULE_CONFIG:
        result['valid'] = False
        result['errors'].append(f"Unknown module: {module_name}")
        return result
    
    module = MODULE_CONFIG[module_name]
    
    # FACT Layer 수정 시도 시 즉시 거부
    if module_name == "appraisal_context":
        result['valid'] = False
        result['errors'].append(
            f"Cannot modify FACT Layer (appraisal_context). "
            f"Appraisal results are immutable and protected by AppraisalContextLock."
        )
        return result
    
    # 각 필드 검증
    for field_name, new_value in modifications.items():
        if not can_modify_field(module_name, field_name):
            result['valid'] = False
            result['errors'].append(
                f"Field '{field_name}' in module '{module_name}' is locked and cannot be modified."
            )
        else:
            result['warnings'].append(
                f"Field '{field_name}' will be modified. "
                f"Ensure this change does not break dependent modules."
            )
    
    return result


# Export
__all__ = [
    'MODULE_CONFIG',
    'REPORT_DEPENDENCIES',
    'can_modify_field',
    'get_module_dependencies',
    'get_access_mode',
    'validate_module_modification'
]
