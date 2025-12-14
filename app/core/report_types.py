"""
ZeroSite v40.4 - Report Type Definitions
보고서 5종 체계 정의 및 구조 명세

목적:
- 독자별 맞춤형 보고서 제공
- 명확한 보고서 타입 분류
- 일관된 보고서 구조 유지

Created: 2025-12-14
Version: 40.4
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class ReportType(str, Enum):
    """
    보고서 타입 정의
    
    기획서 기준 5종 + 기존 1종
    """
    # v40.4 신규 5종 체계
    LANDOWNER_BRIEF = "landowner_brief"           # 토지주용 간략 보고서 (3p)
    LH_SUBMISSION = "lh_submission"               # LH 제출용 보고서 (10~15p)
    POLICY_IMPACT = "policy_impact"               # 정책 영향 분석 (15p)
    DEVELOPER_FEASIBILITY = "developer_feasibility" # 개발사업자용 타당성 (15~20p)
    EXTENDED_PROFESSIONAL = "extended_professional" # 전문가용 상세 보고서 (25~40p)
    
    # v39 기존 (하위 호환)
    APPRAISAL_V39 = "appraisal_v39"               # 기존 감정평가서 (23~30p)


@dataclass
class ReportSpec:
    """보고서 명세"""
    type: ReportType
    name_kr: str
    name_en: str
    target_audience: str
    page_count: str
    description: str
    sections: List[str]
    includes_lh_review: bool = False
    
    
# ============================================
# 보고서 타입별 명세
# ============================================

REPORT_SPECS: Dict[ReportType, ReportSpec] = {
    
    # 1. 토지주용 간략 보고서 (3p)
    ReportType.LANDOWNER_BRIEF: ReportSpec(
        type=ReportType.LANDOWNER_BRIEF,
        name_kr="토지주용 간략 보고서",
        name_en="Landowner Brief Report",
        target_audience="토지 소유주 (일반인)",
        page_count="3 pages",
        description="토지주가 빠르게 이해할 수 있는 핵심 요약 보고서",
        sections=[
            "1. 보고서 표지",
            "2. 핵심 요약 (Executive Summary)",
            "   - 감정가 및 평당 가격",
            "   - 용도지역 및 개발 가능성",
            "   - LH 심사예측 결과 (통과확률, 리스크)",
            "   - 추천 시나리오",
            "3. 다음 단계 (Next Steps)",
            "   - 권장 조치사항",
            "   - 전문가 상담 안내"
        ],
        includes_lh_review=True
    ),
    
    # 2. LH 제출용 보고서 (10~15p)
    ReportType.LH_SUBMISSION: ReportSpec(
        type=ReportType.LH_SUBMISSION,
        name_kr="LH 제출용 보고서",
        name_en="LH Submission Report",
        target_audience="LH 공사 담당자",
        page_count="10~15 pages",
        description="LH 공공주택 사전심사 제출용 공식 보고서",
        sections=[
            "1. 표지 및 목차",
            "2. 사업 개요",
            "   - 토지 위치 및 면적",
            "   - 사업 목적 및 주택 유형",
            "3. 토지 감정평가",
            "   - 감정가 산정 근거",
            "   - 거래사례 분석",
            "   - 프리미엄 요인",
            "4. 토지 진단",
            "   - 용도지역 및 규제사항",
            "   - 정책 적합성",
            "   - 입지 분석",
            "5. 규모 검토",
            "   - 건폐율/용적률",
            "   - 예상 세대수",
            "   - 주차대수 계산",
            "6. 시나리오 분석 (A/B/C)",
            "   - 청년형/신혼형/고령자형",
            "   - 정책 점수 비교",
            "   - 사업성 분석",
            "7. LH 심사예측 (AI Judge)",
            "   - 통과 확률 예측",
            "   - 6개 평가요소 점수",
            "   - 리스크 요인 및 개선 제안",
            "8. 종합 결론 및 권고사항"
        ],
        includes_lh_review=True
    ),
    
    # 3. 정책 영향 분석 (15p)
    ReportType.POLICY_IMPACT: ReportSpec(
        type=ReportType.POLICY_IMPACT,
        name_kr="정책 영향 분석 보고서",
        name_en="Policy Impact Analysis Report",
        target_audience="정책 입안자, 공공기관",
        page_count="15 pages",
        description="공공주택 정책 관점에서의 사업 타당성 및 영향 분석",
        sections=[
            "1. 표지 및 목차",
            "2. Executive Summary",
            "3. 정책 환경 분석",
            "   - 관련 정책 (청년주택, 신혼부부, 고령자)",
            "   - 지역 정책 적합성",
            "   - 인센티브 및 지원 사항",
            "4. 시나리오별 정책 기여도",
            "   - A안: 청년형 (정책 점수 88/100)",
            "   - B안: 신혼형 (정책 점수 92/100)",
            "   - C안: 고령자형 (정책 점수 85/100)",
            "5. LH 심사예측",
            "   - 정책 요인 가중치 분석",
            "   - 정책 목표 달성도",
            "6. 사회적 영향 평가",
            "   - 주거 복지 기여도",
            "   - 지역 사회 영향",
            "7. 종합 정책 제언"
        ],
        includes_lh_review=True
    ),
    
    # 4. 개발사업자용 타당성 (15~20p)
    ReportType.DEVELOPER_FEASIBILITY: ReportSpec(
        type=ReportType.DEVELOPER_FEASIBILITY,
        name_kr="개발사업자용 사업타당성 보고서",
        name_en="Developer Feasibility Study",
        target_audience="민간 개발사업자, 시공사",
        page_count="15~20 pages",
        description="사업성 및 재무적 타당성 중심 보고서",
        sections=[
            "1. 표지 및 목차",
            "2. Executive Summary",
            "   - 추정 사업비",
            "   - 예상 수익률 (IRR/NPV)",
            "   - LH 통과 확률",
            "3. 사업 개요",
            "   - 토지 개요",
            "   - 사업 구조",
            "4. 감정평가 및 토지 비용",
            "   - 감정가 분석",
            "   - 취득세 및 부대비용",
            "5. 규모 검토 및 건축 계획",
            "   - 건폐율/용적률 활용",
            "   - 세대 구성",
            "   - 건축 비용 추정",
            "6. 재무 분석",
            "   - 시나리오별 IRR/NPV",
            "   - 손익분기점 (BEP)",
            "   - 민감도 분석",
            "7. 리스크 분석",
            "   - LH 심사 리스크",
            "   - 시장 리스크",
            "   - 규제 리스크",
            "8. LH 심사예측 (통과 전략)",
            "   - 예상 점수 및 확률",
            "   - 개선 방안",
            "9. 종합 결론 및 GO/NO-GO 판단"
        ],
        includes_lh_review=True
    ),
    
    # 5. 전문가용 상세 보고서 (25~40p)
    ReportType.EXTENDED_PROFESSIONAL: ReportSpec(
        type=ReportType.EXTENDED_PROFESSIONAL,
        name_kr="전문가용 상세 분석 보고서",
        name_en="Extended Professional Report",
        target_audience="감정평가사, 전문 컨설턴트",
        page_count="25~40 pages",
        description="모든 분석 결과를 포함한 종합 전문 보고서",
        sections=[
            "1. 표지 및 목차",
            "2. Executive Summary (LH 심사예측 포함)",
            "3. 토지 감정평가 (상세)",
            "   - 3가지 방식 (거래사례/원가/수익환원)",
            "   - 지역 시세 동향",
            "   - 조정 요인 분석",
            "   - 프리미엄 분석",
            "4. 토지 진단 (상세)",
            "   - 용도지역 및 규제",
            "   - POI 분석",
            "   - 접근성 분석",
            "5. 규모 검토 (상세)",
            "   - 건축 계획",
            "   - 법규 검토",
            "6. 시나리오 분석 (A/B/C)",
            "   - 정책 점수",
            "   - 재무 분석",
            "   - 리스크 평가",
            "7. LH 심사예측 (AI Judge)",
            "   - 6개 평가요소 상세 분석",
            "   - Feature Engineering",
            "   - 개선 전략",
            "8. 종합 위험 평가",
            "9. 법률 및 세무 검토",
            "10. 부록 (거래사례, 법규, 참고자료)"
        ],
        includes_lh_review=True
    ),
    
    # 6. 기존 v39 감정평가서 (하위 호환)
    ReportType.APPRAISAL_V39: ReportSpec(
        type=ReportType.APPRAISAL_V39,
        name_kr="토지 감정평가서 (v39)",
        name_en="Real Estate Appraisal Report v39",
        target_audience="일반 목적 (기존 사용자)",
        page_count="23~30 pages",
        description="v39 기존 감정평가서 (하위 호환)",
        sections=[
            "기존 v39 PDF Generator 사용",
            "LH 심사예측 미포함"
        ],
        includes_lh_review=False
    ),
}


def get_report_spec(report_type: ReportType) -> ReportSpec:
    """보고서 타입에 따른 명세 조회"""
    return REPORT_SPECS.get(report_type)


def list_available_reports() -> List[ReportSpec]:
    """사용 가능한 모든 보고서 목록"""
    return list(REPORT_SPECS.values())


def get_reports_with_lh_review() -> List[ReportSpec]:
    """LH 심사예측이 포함된 보고서 목록"""
    return [spec for spec in REPORT_SPECS.values() if spec.includes_lh_review]


# ============================================
# Report Validation
# ============================================

def validate_report_request(
    report_type: ReportType,
    context: Dict,
    include_lh_review: bool = False
) -> Dict[str, any]:
    """
    보고서 생성 요청 검증
    
    Returns:
        Dict: {
            "valid": bool,
            "errors": List[str],
            "warnings": List[str]
        }
    """
    errors = []
    warnings = []
    
    spec = get_report_spec(report_type)
    if not spec:
        errors.append(f"Invalid report type: {report_type}")
        return {"valid": False, "errors": errors, "warnings": warnings}
    
    # 필수 Context 데이터 확인
    if "appraisal" not in context:
        errors.append("Appraisal 데이터 필수")
    
    # LH Review 필요 시 확인
    if spec.includes_lh_review or include_lh_review:
        if "lh_review" not in context:
            warnings.append("LH 심사예측 데이터 없음 (먼저 /api/v40/lh-review/predict 실행 필요)")
    
    # 보고서 타입별 추가 검증
    if report_type in [ReportType.LH_SUBMISSION, ReportType.POLICY_IMPACT]:
        if "scenario" not in context:
            errors.append("Scenario 분석 데이터 필수")
    
    if report_type == ReportType.DEVELOPER_FEASIBILITY:
        if "scenario" not in context:
            errors.append("재무 분석을 위한 Scenario 데이터 필수")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "spec": spec
    }
