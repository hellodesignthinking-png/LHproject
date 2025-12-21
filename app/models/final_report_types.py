"""
ZeroSite Final Report Types Definition
최종보고서 6종 타입 정의 및 조립 로직

⚠️ Critical: Data Contract Based Assembly
각 보고서 타입은 명확한 required fields를 가지며,
누락 시 명시적으로 경고를 표시합니다.

Version: 2.0 (Data Contract Implementation)
Date: 2025-12-20
"""

from enum import Enum
from typing import Dict, List, Optional


class FinalReportType(str, Enum):
    """최종보고서 6종 타입 정의"""
    
    # 종합 최종보고서 (모든 분석 포함)
    ALL_IN_ONE = "all_in_one"
    
    # 토지주 제출용 요약보고서 (설득용, 점수 미노출)
    LANDOWNER_SUMMARY = "landowner_summary"
    
    # LH 제출용 기술검증 보고서 (기준 중심, 사실 기반)
    LH_TECHNICAL = "lh_technical"
    
    # 사업성·투자 검토 보고서 (M4, M5, M6 중심)
    FINANCIAL_FEASIBILITY = "financial_feasibility"
    
    # 사전 검토 리포트 (Quick Check, 5-8 페이지)
    QUICK_CHECK = "quick_check"
    
    # 설명용 프레젠테이션 보고서 (슬라이드 톤)
    PRESENTATION = "presentation"


# ⚠️ NEW: 데이터 계약 (Data Contract)
# 각 보고서 타입이 반드시 가져야 할 필수 필드 정의
REPORT_DATA_CONTRACTS = {
    FinalReportType.ALL_IN_ONE: {
        "M2": ["land_value_total_krw", "confidence_pct"],
        "M3": ["recommended_type", "total_score"],
        "M4": ["legal_units", "incentive_units"],
        "M5": ["npv_public_krw", "irr_pct", "grade"],
        "M6": ["decision", "approval_probability_pct", "total_score"]
    },
    FinalReportType.LANDOWNER_SUMMARY: {
        "M2": ["land_value_total_krw"],
        "M4": ["legal_units"],
        "M6": ["decision"]
    },
    FinalReportType.LH_TECHNICAL: {
        "M2": ["land_value_total_krw", "confidence_pct"],
        "M3": ["recommended_type"],
        "M4": ["legal_units", "parking_alt_a"],
        "M5": ["npv_public_krw", "grade"],
        "M6": ["decision", "total_score"]
    },
    FinalReportType.FINANCIAL_FEASIBILITY: {
        "M4": ["legal_units", "incentive_units"],
        "M5": ["npv_public_krw", "irr_pct", "roi_pct", "grade"],
        "M6": ["decision", "approval_probability_pct"]
    },
    FinalReportType.QUICK_CHECK: {
        "M3": ["recommended_type"],
        "M4": ["legal_units"],
        "M6": ["decision"]
    },
    FinalReportType.PRESENTATION: {
        "M3": ["recommended_type", "total_score"],
        "M4": ["legal_units"],
        "M5": ["npv_public_krw", "grade"],
        "M6": ["decision", "approval_probability_pct"]
    }
}


# 각 최종보고서 타입별 메타데이터
FINAL_REPORT_METADATA = {
    FinalReportType.ALL_IN_ONE: {
        "name": "종합 최종보고서",
        "description": "M2~M6 모든 분석을 포함한 완전한 보고서",
        "modules": ["M2", "M3", "M4", "M5", "M6"],
        "tone": "formal",
        "target_pages": "15-20"
    },
    FinalReportType.LANDOWNER_SUMMARY: {
        "name": "토지주 제출용 요약보고서",
        "description": "토지주 설득용, 긍정적 측면 강조",
        "modules": ["M2", "M4", "M6"],
        "tone": "persuasive",
        "target_pages": "8-10",
        "exclude": ["detailed_scores", "irr_roi"]
    },
    FinalReportType.LH_TECHNICAL: {
        "name": "LH 제출용 기술검증 보고서",
        "description": "LH 기준 중심, 객관적 사실 기반",
        "modules": ["M2", "M3", "M4", "M5", "M6"],
        "tone": "technical",
        "target_pages": "18-22",
        "emphasis": "standards_compliance"
    },
    FinalReportType.FINANCIAL_FEASIBILITY: {
        "name": "사업성·투자 검토 보고서",
        "description": "투자자용, M4/M5/M6 중심",
        "modules": ["M4", "M5", "M6"],
        "tone": "investment",
        "target_pages": "10-12",
        "exclude": ["M2_details"]
    },
    FinalReportType.QUICK_CHECK: {
        "name": "사전 검토 리포트",
        "description": "빠른 검토용, 핵심 요약",
        "modules": ["M3", "M4", "M6"],
        "tone": "summary",
        "target_pages": "5-8",
        "exclude": ["detailed_tables"]
    },
    FinalReportType.PRESENTATION: {
        "name": "설명용 프레젠테이션 보고서",
        "description": "화면 공유용, 시각 자료 중심",
        "modules": ["M3", "M4", "M5", "M6"],
        "tone": "presentation",
        "target_pages": "12-15",
        "emphasis": "visuals"
    }
}


def get_modules_for_report(report_type: FinalReportType) -> List[str]:
    """
    최종보고서 타입별 필요한 모듈 목록 반환
    
    Args:
        report_type: 최종보고서 타입
        
    Returns:
        포함할 모듈 ID 리스트 (예: ["M2", "M3", "M4"])
    """
    metadata = FINAL_REPORT_METADATA.get(report_type)
    if not metadata:
        return []
    
    return metadata.get("modules", [])


def get_report_metadata(report_type: FinalReportType) -> Dict:
    """
    최종보고서 타입별 메타데이터 반환
    
    Args:
        report_type: 최종보고서 타입
        
    Returns:
        메타데이터 딕셔너리
    """
    return FINAL_REPORT_METADATA.get(report_type, {})


def assemble_final_report(
    report_type: FinalReportType,
    module_summaries: Dict[str, Dict]
) -> Dict:
    """
    최종보고서 조립 함수 (Content Productized)
    
    M2~M6 모듈 summary를 받아서 최종보고서 타입에 맞게 재조합
    ⚠️ 내부 모듈명(M2-M6)은 절대 최종 출력에 노출되지 않음
    
    Args:
        report_type: 최종보고서 타입
        module_summaries: 모듈별 summary 데이터
                         {"M2": {...}, "M3": {...}, ...}
    
    Returns:
        조립된 최종보고서 데이터 (사용자 친화적 섹션명으로 변환)
    """
    metadata = get_report_metadata(report_type)
    required_modules = get_modules_for_report(report_type)
    
    # 필요한 모듈만 필터링
    assembled_data = {
        "report_type": report_type.value,
        "report_name": metadata.get("name", ""),
        "description": metadata.get("description", ""),
        "tone": metadata.get("tone", "formal"),
        "target_pages": metadata.get("target_pages", ""),
        "modules": {},
        "show_module_codes": False  # 최종보고서에서는 모듈 코드 숨김
    }
    
    # 종합 최종보고서의 경우 결론 요약 카드 추가
    if report_type == FinalReportType.ALL_IN_ONE:
        assembled_data["executive_summary"] = _create_executive_summary(module_summaries)
    
    # 각 모듈 데이터 추가 (보고서 타입별 제외 항목 적용)
    exclude_items = metadata.get("exclude", [])
    
    for module_id in required_modules:
        if module_id in module_summaries:
            module_data = module_summaries[module_id].copy()
            
            # 제외 항목 처리
            if "detailed_scores" in exclude_items and module_id in ["M3", "M6"]:
                # 상세 점수 제거
                if "details" in module_data:
                    module_data.pop("details", None)
            
            if "irr_roi" in exclude_items and module_id == "M5":
                # IRR/ROI 제거 (토지주용)
                if "summary" in module_data:
                    module_data["summary"].pop("irr_pct", None)
                    module_data["summary"].pop("roi_pct", None)
            
            if "M2_details" in exclude_items and module_id == "M2":
                # M2 상세 제거
                if "details" in module_data:
                    module_data.pop("details", None)
            
            if "detailed_tables" in exclude_items:
                # 상세 표 제거 (Quick Check용)
                if "details" in module_data:
                    if "transactions" in module_data["details"]:
                        module_data["details"].pop("transactions", None)
            
            # 보고서 타입별 언어 조정
            module_data = _adjust_language_for_report_type(module_data, module_id, report_type)
            
            assembled_data["modules"][module_id] = module_data
    
    return assembled_data


def _create_executive_summary(module_summaries: Dict[str, Dict]) -> Dict:
    """
    종합 최종보고서용 최상단 결론 요약 카드 생성
    
    Args:
        module_summaries: 모듈별 summary 데이터
        
    Returns:
        결론 요약 딕셔너리
    """
    m6_summary = module_summaries.get("M6", {}).get("summary", {})
    m5_summary = module_summaries.get("M5", {}).get("summary", {})
    
    decision = m6_summary.get("decision", "CONDITIONAL")
    approval_probability = m6_summary.get("approval_probability_pct", 0)
    grade = m6_summary.get("grade", "")
    
    # 핵심 리스크 도출
    key_risks = []
    if approval_probability < 50:
        key_risks.append("승인 가능성 낮음")
    if m5_summary.get("grade", "") in ["C", "D"]:
        key_risks.append("사업성 제한적")
    
    if not key_risks:
        key_risks = ["특이사항 없음"]
    
    return {
        "decision": decision,
        "decision_text": {
            "GO": "승인 추진 권장",
            "CONDITIONAL": "조건부 추진 가능",
            "NOGO": "추진 재검토 필요"
        }.get(decision, decision),
        "approval_probability_pct": approval_probability,
        "grade": grade,
        "key_risks": key_risks[:3],  # 최대 3개
        "quick_insight": _generate_quick_insight(decision, approval_probability, grade)
    }


def _generate_quick_insight(decision: str, approval_pct: float, grade: str) -> str:
    """30초 안에 파악할 수 있는 한 줄 인사이트 생성"""
    if decision == "GO" and approval_pct >= 70:
        return "본 사업은 승인 가능성이 높으며, 추진을 권장합니다."
    elif decision == "CONDITIONAL":
        return "조건부 승인이 예상되며, 핵심 리스크 관리가 필요합니다."
    else:
        return "현 상태에서는 승인 가능성이 제한적이며, 추가 검토가 필요합니다."


def _adjust_language_for_report_type(
    module_data: Dict,
    module_id: str,
    report_type: FinalReportType
) -> Dict:
    """
    보고서 타입별 언어 조정 (권고 vs 사실 vs 투자)
    
    Args:
        module_data: 모듈 데이터
        module_id: 모듈 ID (M2-M6)
        report_type: 보고서 타입
        
    Returns:
        언어 조정된 모듈 데이터
    """
    if not module_data.get("summary"):
        return module_data
    
    summary = module_data["summary"]
    
    # LH 기술검증 보고서: 권고·의견 표현 제거
    if report_type == FinalReportType.LH_TECHNICAL:
        # "권장", "추천" 등의 단어를 "해당", "적합" 등으로 변경
        if module_id == "M3" and "recommended_type" in summary:
            summary["recommended_type_label"] = "적합 유형"  # "추천 유형" → "적합 유형"
        
        if module_id == "M6" and "decision" in summary:
            decision = summary["decision"]
            summary["decision_factual"] = {
                "GO": "기준 충족",
                "CONDITIONAL": "조건부 충족",
                "NOGO": "기준 미충족"
            }.get(decision, decision)
    
    # 토지주 제출용: 숫자 최소화, 긍정적 표현
    elif report_type == FinalReportType.LANDOWNER_SUMMARY:
        if module_id == "M6" and "decision" in summary:
            decision = summary["decision"]
            summary["decision_simple"] = {
                "GO": "추진 가능",
                "CONDITIONAL": "조건부 가능",
                "NOGO": "검토 필요"
            }.get(decision, decision)
    
    # 투자 검토 보고서: 투자 언어
    elif report_type == FinalReportType.FINANCIAL_FEASIBILITY:
        if module_id == "M5":
            summary["investor_language"] = True  # 투자자 관점 플래그
    
    return module_data
