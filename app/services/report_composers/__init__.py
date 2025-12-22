"""
ZeroSite Report Composers v3.3 Phase 2

새로운 보고서 타입을 위한 Composer 모듈
- 기존 Full Report (60p)는 report_generator_v8_8.py에 있음
- 이 모듈은 추가 보고서 타입 구현

Composers (v3.3 Phase 2 - 100% Complete):
- PreReportComposer: 2페이지 사전진단 보고서 (v3.3 updated)
- ComprehensiveReportComposer: 15-20페이지 종합보고서 (v3.3)
- LHDecisionReportComposer: LH 심사용 대응 문서 (v3.3)
- InvestorReportComposer: 투자자용 수익성 보고서 (v1.0 - Phase 2)
- LandPriceReportComposer: 토지가격 분석 보고서 (v1.0 - Phase 2)
- InternalAssessmentComposer: 내부 의사결정용 평가서 (v1.0 - Phase 2)

Total: 7/7 Report Types Implemented (100%)
"""

from .pre_report_composer import PreReportComposer
from .comprehensive_report_composer import ComprehensiveReportComposer
from .lh_decision_report_composer import LHDecisionReportComposer
from .investor_report_composer import InvestorReportComposer
from .land_price_report_composer import LandPriceReportComposer
from .internal_assessment_composer import InternalAssessmentComposer

__all__ = [
    'PreReportComposer',
    'ComprehensiveReportComposer',
    'LHDecisionReportComposer',
    'InvestorReportComposer',
    'LandPriceReportComposer',
    'InternalAssessmentComposer',
]
