"""
ZeroSite 4.0 - M6 Centered Report Base
======================================

모든 보고서는 M6 결과를 Single Source of Truth로 사용

핵심 원칙:
1. M6 판단이 유일한 결론
2. M1~M5는 M6 결론의 근거 데이터
3. 모든 보고서는 동일한 결론을 다른 언어로 표현
4. 보고서 간 점수/판단/표현 절대 불일치 금지

Author: ZeroSite 4.0 Team
Date: 2025-12-27
Version: 1.0
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ============================================================================
# Phase 2/3: Exception for Report Consistency Violations
# ============================================================================

class ReportConsistencyError(Exception):
    """
    M6 Single Source of Truth 위반 시 발생
    
    Phase 2/3 원칙:
    - 보고서 간 점수/판단/등급이 불일치하면 생성 중단
    - FAIL FAST: 문제가 있으면 즉시 실패
    """
    pass


# ============================================================================
# M6 Single Source of Truth Data Structures
# ============================================================================

class M6Judgement(str, Enum):
    """M6 최종 판단 (Single Source of Truth)"""
    GO = "GO"
    CONDITIONAL = "CONDITIONAL"
    NOGO = "NOGO"


class M6Grade(str, Enum):
    """M6 등급 (Single Source of Truth)"""
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C_PLUS = "C+"
    C = "C"
    D = "D"
    F = "F"


@dataclass
class M6SingleSourceOfTruth:
    """
    M6 판단 결과 - 모든 보고서의 유일한 진실
    
    이 데이터는 절대 변경되지 않으며, 모든 보고서에서 동일하게 사용됨
    """
    # 핵심 판단 (변경 불가)
    lh_total_score: float  # 예: 75.0
    judgement: M6Judgement  # GO/CONDITIONAL/NOGO
    grade: M6Grade  # A+, A, B+, B, C+, C, D, F
    fatal_reject: bool  # 즉시 탈락 여부
    
    # 감점 요인 (변경 불가)
    key_deductions: List[str]  # 예: ["주차 효율 부족 (-4)", "인근 공급 과잉 (-3)"]
    
    # 개선 포인트 (변경 불가)
    improvement_points: List[str]  # 예: ["세대유형을 신혼형으로 변경 시 +6"]
    
    # 섹션별 점수 (변경 불가)
    section_scores: Dict[str, float]  # 예: {"policy": 20, "location": 18, ...}
    
    # 승인 가능성 (변경 불가)
    approval_probability_pct: float  # 예: 75.0
    
    # M6 결론 문장 (변경 불가)
    final_conclusion: str  # 예: "본 사업지는 ZeroSite v4.0 M6 기준에 따라..."
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "lh_total_score": self.lh_total_score,
            "judgement": self.judgement.value,
            "grade": self.grade.value,
            "fatal_reject": self.fatal_reject,
            "key_deductions": self.key_deductions,
            "improvement_points": self.improvement_points,
            "section_scores": self.section_scores,
            "approval_probability_pct": self.approval_probability_pct,
            "final_conclusion": self.final_conclusion
        }


class M6CenteredReportBase:
    """
    M6 중심 보고서 베이스 클래스
    
    모든 6종 보고서는 이 클래스를 상속받아 작성됨
    """
    
    def __init__(self, m6_truth: M6SingleSourceOfTruth):
        """
        Args:
            m6_truth: M6 판단 결과 (Single Source of Truth)
        """
        self.m6_truth = m6_truth
        logger.info(f"✅ M6 Centered Report Base initialized with judgement: {m6_truth.judgement.value}")
    
    def get_conclusion_sentence(self) -> str:
        """
        모든 보고서에서 사용하는 동일한 결론 문장
        
        Returns:
            통일된 결론 문장
        """
        judgement = self.m6_truth.judgement
        
        if judgement == M6Judgement.GO:
            return (
                "본 사업지는 ZeroSite v4.0 M6 기준에 따라 "
                "LH 매입이 가능한 사업지로 판단된다."
            )
        elif judgement == M6Judgement.CONDITIONAL:
            return (
                "본 사업지는 ZeroSite v4.0 M6 기준에 따라 "
                "보완 조건 충족 시 LH 매입이 가능한 사업지로 판단된다."
            )
        else:  # NOGO
            return (
                "본 사업지는 ZeroSite v4.0 M6 기준에 따라 "
                "LH 매입이 어려운 사업지로 판단된다."
            )
    
    def get_color_code(self) -> str:
        """
        판단 결과에 따른 색상 코드
        
        Returns:
            색상 코드 (Green/Amber/Red)
        """
        judgement = self.m6_truth.judgement
        
        if judgement == M6Judgement.GO:
            return "#16A34A"  # Green
        elif judgement == M6Judgement.CONDITIONAL:
            return "#F59E0B"  # Amber
        else:  # NOGO
            return "#DC2626"  # Red
    
    def get_executive_summary(self) -> Dict[str, Any]:
        """
        경영진 요약 (모든 보고서 공통)
        
        Returns:
            경영진 요약 데이터
        """
        return {
            "judgement": self.m6_truth.judgement.value,
            "total_score": f"{self.m6_truth.lh_total_score:.1f}/100",
            "grade": self.m6_truth.grade.value,
            "approval_probability": f"{self.m6_truth.approval_probability_pct:.0f}%",
            "key_deductions": self.m6_truth.key_deductions,
            "improvement_points": self.m6_truth.improvement_points,
            "final_conclusion": self.get_conclusion_sentence()
        }
    
    def validate_consistency(self, report_data: Dict[str, Any]) -> bool:
        """
        보고서 데이터의 일관성 검증
        
        Args:
            report_data: 생성된 보고서 데이터
            
        Returns:
            일관성 검증 통과 여부
        """
        # 1. 점수 일치 확인
        if "total_score" in report_data:
            reported_score = float(report_data["total_score"].split("/")[0])
            if abs(reported_score - self.m6_truth.lh_total_score) > 0.1:
                logger.error(
                    f"❌ Score mismatch: M6={self.m6_truth.lh_total_score}, "
                    f"Report={reported_score}"
                )
                return False
        
        # 2. 판단 일치 확인
        if "judgement" in report_data:
            if report_data["judgement"] != self.m6_truth.judgement.value:
                logger.error(
                    f"❌ Judgement mismatch: M6={self.m6_truth.judgement.value}, "
                    f"Report={report_data['judgement']}"
                )
                return False
        
        # 3. 등급 일치 확인
        if "grade" in report_data:
            if report_data["grade"] != self.m6_truth.grade.value:
                logger.error(
                    f"❌ Grade mismatch: M6={self.m6_truth.grade.value}, "
                    f"Report={report_data['grade']}"
                )
                return False
        
        logger.info("✅ Report consistency validation PASSED")
        return True
    
    def get_m1_m5_as_evidence(self, m1_m5_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        M1~M5 데이터를 M6 결론의 근거로 변환
        
        Args:
            m1_m5_data: M1~M5 원본 데이터
            
        Returns:
            M6 결론을 뒷받침하는 근거 데이터
        """
        return {
            "evidence_note": "아래 데이터는 M6 판단의 근거로 사용되었습니다.",
            "m1_land_info": m1_m5_data.get("m1", {}),
            "m2_appraisal": m1_m5_data.get("m2", {}),
            "m3_housing_type": m1_m5_data.get("m3", {}),
            "m4_capacity": m1_m5_data.get("m4", {}),
            "m5_feasibility": m1_m5_data.get("m5", {}),
            "evidence_summary": (
                f"위 데이터를 종합한 결과, M6는 다음과 같이 판단하였습니다: "
                f"{self.m6_truth.judgement.value} (점수: {self.m6_truth.lh_total_score:.1f}/100)"
            )
        }


class AllInOneReport(M6CenteredReportBase):
    """종합 보고서 - M6를 가장 상세히 설명"""
    
    def generate(self, m1_m5_data: Dict[str, Any]) -> Dict[str, Any]:
        """종합 보고서 생성"""
        return {
            "report_type": "all_in_one",
            "report_name": "ZeroSite 종합 보고서",
            "executive_summary": self.get_executive_summary(),
            "m6_scorecard": {
                "total_score": self.m6_truth.lh_total_score,
                "grade": self.m6_truth.grade.value,
                "judgement": self.m6_truth.judgement.value,
                "section_scores": self.m6_truth.section_scores,
                "key_deductions": self.m6_truth.key_deductions,
                "improvement_points": self.m6_truth.improvement_points
            },
            "evidence_data": self.get_m1_m5_as_evidence(m1_m5_data),
            "final_conclusion": self.get_conclusion_sentence(),
            "color_code": self.get_color_code()
        }


class LandownerSummaryReport(M6CenteredReportBase):
    """토지주 요약 보고서 - "지금 팔 수 있는가?"에 대한 답변"""
    
    def generate(self, m1_m5_data: Dict[str, Any]) -> Dict[str, Any]:
        """토지주 요약 보고서 생성 - Phase 3.5A 완전 통일"""
        return {
            "report_type": "landowner_summary",
            "report_name": "토지주 요약 보고서",
            # Phase 3.5A: 모든 보고서가 동일한 결론 사용
            "judgement": self.m6_truth.judgement.value,
            "simple_message": self.get_conclusion_sentence(),  # 통일
            "key_points": {
                "현재 점수": f"{self.m6_truth.lh_total_score:.0f}점/100점",
                "등급": self.m6_truth.grade.value,
                "개선 가능 항목": len(self.m6_truth.improvement_points)
            },
            "what_to_do_next": self.m6_truth.improvement_points[:3],  # Top 3만
            "final_conclusion": self.get_conclusion_sentence(),  # 통일
            "color_code": self.get_color_code()
        }


class LHTechnicalReport(M6CenteredReportBase):
    """LH 기술검토 보고서 - LH 내부 검토 문서처럼"""
    
    def generate(self, m1_m5_data: Dict[str, Any]) -> Dict[str, Any]:
        """LH 기술검토 보고서 생성"""
        return {
            "report_type": "lh_technical",
            "report_name": "LH 기술검토 보고서",
            "m6_scorecard": {
                "total_score": f"{self.m6_truth.lh_total_score:.1f}",
                "grade": self.m6_truth.grade.value,
                "judgement": self.m6_truth.judgement.value,
                "fatal_reject": self.m6_truth.fatal_reject,
                "section_breakdown": self.m6_truth.section_scores
            },
            "deduction_reasons": self.m6_truth.key_deductions,
            "compliance_status": "통과" if not self.m6_truth.fatal_reject else "미통과",
            "technical_recommendation": self.get_conclusion_sentence(),
            "color_code": self.get_color_code()
        }


class FinancialFeasibilityReport(M6CenteredReportBase):
    """사업타당성 보고서 - 재무는 M6에 종속"""
    
    def generate(self, m1_m5_data: Dict[str, Any]) -> Dict[str, Any]:
        """사업타당성 보고서 생성"""
        m5_data = m1_m5_data.get("m5", {})
        
        # 중요: M5는 절대 독립된 결론 아님
        financial_note = (
            "본 사업의 재무성은 단독으로는 판단 대상이 아니며, "
            "LH 매입 판단(M6)에 종속됩니다."
        )
        
        return {
            "report_type": "financial_feasibility",
            "report_name": "사업타당성 보고서",
            "important_note": financial_note,
            "m6_final_judgement": {
                "judgement": self.m6_truth.judgement.value,
                "score": self.m6_truth.lh_total_score,
                "grade": self.m6_truth.grade.value
            },
            "financial_data_from_m5": m5_data,  # M5는 참고 데이터일 뿐
            "final_conclusion": self.get_conclusion_sentence(),
            "color_code": self.get_color_code()
        }


class QuickCheckReport(M6CenteredReportBase):
    """간편 체크 보고서 - 1분 요약"""
    
    def generate(self, m1_m5_data: Dict[str, Any]) -> Dict[str, Any]:
        """간편 체크 보고서 생성"""
        return {
            "report_type": "quick_check",
            "report_name": "간편 체크 보고서",
            "quick_result": {
                "icon": "✅" if self.m6_truth.judgement == M6Judgement.GO else 
                        "⚠️" if self.m6_truth.judgement == M6Judgement.CONDITIONAL else "❌",
                "judgement": self.m6_truth.judgement.value,
                "score": f"{self.m6_truth.lh_total_score:.0f}/100",
                "grade": self.m6_truth.grade.value,
                "one_line_reason": self.m6_truth.key_deductions[0] if self.m6_truth.key_deductions else "해당 없음"
            },
            "final_conclusion": self.get_conclusion_sentence(),
            "color_code": self.get_color_code()
        }


class PresentationReport(M6CenteredReportBase):
    """프레젠테이션 보고서 - 말로 설명하기 위한 자료"""
    
    def generate(self, m1_m5_data: Dict[str, Any]) -> Dict[str, Any]:
        """프레젠테이션 보고서 생성"""
        return {
            "report_type": "presentation",
            "report_name": "프레젠테이션 보고서",
            "slides": [
                {
                    "slide_number": 1,
                    "title": "M6 결론",
                    "content": {
                        "judgement": self.m6_truth.judgement.value,
                        "score": f"{self.m6_truth.lh_total_score:.0f}점",
                        "grade": self.m6_truth.grade.value
                    }
                },
                {
                    "slide_number": 2,
                    "title": "왜 이 결론인가?",
                    "content": {
                        "key_deductions": self.m6_truth.key_deductions[:3]
                    }
                },
                {
                    "slide_number": 3,
                    "title": "개선 전략",
                    "content": {
                        "improvement_points": self.m6_truth.improvement_points[:3]
                    }
                },
                {
                    "slide_number": 4,
                    "title": "최종 결론",
                    "content": {
                        "conclusion": self.get_conclusion_sentence()
                    }
                }
            ],
            "color_code": self.get_color_code()
        }


def create_m6_centered_report(
    report_type: str,
    m6_result: Any,
    m1_m5_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    M6 중심 보고서 생성 팩토리 함수
    
    Args:
        report_type: 보고서 타입 (all_in_one, landowner_summary, etc.)
        m6_result: M6 최종 판단 결과 (M6ComprehensiveResult 객체 또는 dict)
        m1_m5_data: M1~M5 데이터 (근거로만 사용)
        
    Returns:
        생성된 보고서 데이터
    """
    # M6 결과를 SingleSourceOfTruth로 변환
    # dict 형식과 객체 형식 모두 지원
    if isinstance(m6_result, dict):
        # Dict 형식 (파이프라인 결과에서 직접 전달된 경우)
        m6_truth = M6SingleSourceOfTruth(
            lh_total_score=m6_result.get('lh_score_total', 75.0),
            judgement=M6Judgement(m6_result.get('judgement', 'CONDITIONAL')),
            grade=M6Grade(m6_result.get('grade', 'B')),
            fatal_reject=m6_result.get('fatal_reject', False),
            key_deductions=m6_result.get('deduction_reasons', []),
            improvement_points=m6_result.get('improvement_points', []),
            section_scores=m6_result.get('section_scores', {
                "policy": 15, "location": 18, "construction": 12,
                "price": 10, "business": 10
            }),
            approval_probability_pct=m6_result.get('lh_score_total', 75.0) * 0.9,
            final_conclusion=""  # Will be generated
        )
    else:
        # 객체 형식 (M6ComprehensiveResult)
        m6_truth = M6SingleSourceOfTruth(
            lh_total_score=getattr(m6_result, 'lh_score_total', 75.0),
            judgement=M6Judgement(getattr(m6_result, 'judgement', 'CONDITIONAL').value if hasattr(getattr(m6_result, 'judgement', 'CONDITIONAL'), 'value') else 'CONDITIONAL'),
            grade=M6Grade(getattr(m6_result, 'grade', 'B').value if hasattr(getattr(m6_result, 'grade', 'B'), 'value') else 'B'),
            fatal_reject=getattr(m6_result, 'fatal_reject', False),
            key_deductions=getattr(m6_result, 'deduction_reasons', []),
            improvement_points=getattr(m6_result, 'improvement_points', []),
            section_scores={
                "policy": getattr(m6_result.section_a_policy, 'raw_score', 0) if hasattr(m6_result, 'section_a_policy') else 0,
                "location": getattr(m6_result.section_b_location, 'raw_score', 0) if hasattr(m6_result, 'section_b_location') else 0,
                "construction": getattr(m6_result.section_c_construction, 'raw_score', 0) if hasattr(m6_result, 'section_c_construction') else 0,
                "price": getattr(m6_result.section_d_price, 'raw_score', 0) if hasattr(m6_result, 'section_d_price') else 0,
                "business": getattr(m6_result.section_e_business, 'raw_score', 0) if hasattr(m6_result, 'section_e_business') else 0,
            },
            approval_probability_pct=getattr(m6_result, 'lh_score_total', 75.0) * 0.9,  # 근사값
            final_conclusion=""  # Will be generated
        )
    
    logger.info(f"🔥 Creating M6-centered {report_type} report")
    logger.info(f"   M6 Judgement: {m6_truth.judgement.value}")
    logger.info(f"   M6 Total Score: {m6_truth.lh_total_score:.1f}/100")
    logger.info(f"   M6 Grade: {m6_truth.grade.value}")
    
    # 보고서 타입에 따라 생성
    report_classes = {
        "all_in_one": AllInOneReport,
        "landowner_summary": LandownerSummaryReport,
        "lh_technical": LHTechnicalReport,
        "financial_feasibility": FinancialFeasibilityReport,
        "quick_check": QuickCheckReport,
        "presentation": PresentationReport
    }
    
    report_class = report_classes.get(report_type)
    if not report_class:
        raise ValueError(f"Unknown report type: {report_type}")
    
    # 보고서 생성
    report_generator = report_class(m6_truth)
    report_data = report_generator.generate(m1_m5_data)
    
    # 일관성 검증
    if not report_generator.validate_consistency(report_data):
        logger.warning(f"⚠️ Report consistency validation failed for {report_type}")
    else:
        logger.info(f"✅ Report consistency validation passed for {report_type}")
    
    logger.info(f"✅ M6-centered {report_type} report generated successfully")
    return report_data


__all__ = [
    # Core Data Structures
    "M6SingleSourceOfTruth",
    "M6Judgement",
    "M6Grade",
    # Exceptions
    "ReportConsistencyError",
    # Report Generators
    "M6CenteredReportBase",
    "AllInOneReport",
    "LandownerSummaryReport",
    "LHTechnicalReport",
    "FinancialFeasibilityReport",
    "QuickCheckReport",
    "PresentationReport",
    # Factory Function
    "create_m6_centered_report"
]
