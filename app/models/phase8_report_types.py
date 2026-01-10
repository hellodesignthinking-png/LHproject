"""
Phase 8: 최종 통합 출력 확대 시스템 - 데이터 모델
M2-M6 분석 결과를 활용한 6종 보고서 + 모듈별 보고서 데이터 모델

작성일: 2026-01-10
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ========================================
# 보고서 타입 Enum
# ========================================

class ReportTypeEnum(str, Enum):
    """6종 보고서 타입"""
    TYPE_A_COMPREHENSIVE = "A"  # 종합 최종보고서 (Master Comprehensive)
    TYPE_B_LANDOWNER = "B"      # 토지주 제출용
    TYPE_C_LH_TECHNICAL = "C"    # LH 기술검증
    TYPE_D_INVESTOR = "D"        # 사업성·투자 검토
    TYPE_E_PRELIMINARY = "E"     # 사전 검토 리포트
    TYPE_F_PRESENTATION = "F"    # 설명용 프레젠테이션


class ModuleEnum(str, Enum):
    """분석 모듈"""
    M1 = "M1"  # 입지 분석
    M2 = "M2"  # 토지감정평가
    M3 = "M3"  # 공급 유형 판단
    M4 = "M4"  # 건축 규모 검토
    M5 = "M5"  # 사업성 분석
    M6 = "M6"  # 종합 판단
    M7 = "M7"  # 커뮤니티 계획


# ========================================
# 모듈별 보고서 데이터 모델
# ========================================

class TransactionCase(BaseModel):
    """거래 사례 (M2용)"""
    case_id: str
    address: str
    trade_date: str
    area_sqm: float
    price_total: int
    price_per_sqm: int
    price_per_pyeong: int
    distance_meters: Optional[int] = None
    comparison_logic: str
    adjustment_factor: float = 1.0


class M2LandAppraisalReport(BaseModel):
    """M2: 토지감정평가 보고서"""
    module_name: str = "M2"
    module_title: str = "토지감정평가"
    
    # 기본 정보
    context_id: str
    address: str
    generated_at: str
    
    # 감정평가 결과
    land_value_krw: str
    unit_price_sqm: str
    unit_price_pyeong: str
    confidence_pct: float
    
    # 거래사례 분석
    transaction_cases: List[TransactionCase] = []
    transaction_count: int
    avg_price_sqm: str
    price_range_min: str
    price_range_max: str
    
    # 공시지가 비교
    official_price_krw: str
    official_price_ratio: float
    
    # 기획 의도 설명
    purpose_statement: str = Field(
        default="본 감정평가는 LH 공공매입임대 사업을 위한 토지 가치 평가로, 실거래가 분석, 공시지가 비교, 지역 시세 등을 종합하여 합리적인 매입 가격을 산정하기 위한 목적으로 수행되었습니다."
    )
    
    # 가격 형성 논리
    price_formation_logic: str
    
    # 리스크 요인
    risk_factors: List[str] = []
    
    # 한계점 및 유의사항
    limitations: List[str] = []


class HousingTypeCandidate(BaseModel):
    """공급 유형 후보 (M3용)"""
    type_name: str
    type_code: str
    score: float
    rank: int
    pros: List[str]
    cons: List[str]
    policy_fitness: str
    selection_reason: Optional[str] = None
    exclusion_reason: Optional[str] = None


class M3SupplyTypeReport(BaseModel):
    """M3: 공급 유형 판단 보고서"""
    module_name: str = "M3"
    module_title: str = "공급 유형 판단"
    
    # 기본 정보
    context_id: str
    address: str
    generated_at: str
    
    # 추천 유형
    recommended_housing_type: str
    recommended_type_code: str
    housing_type_score: float
    second_choice_type: str
    
    # 후보 유형 전체
    candidate_types: List[HousingTypeCandidate]
    
    # 라이프스타일 요인
    lifestyle_factors: List[Dict[str, Any]]
    
    # 정책 적합성 매트릭스
    policy_matrix: Dict[str, Any]
    
    # 최종 선택 논리
    selection_logic: str
    
    # 탈락 유형 배제 근거
    exclusion_explanations: List[Dict[str, str]]


class BuildingScenario(BaseModel):
    """건축 규모 시나리오 (M4용)"""
    scenario_name: str
    scenario_code: str
    far_pct: float
    bcr_pct: float
    units_count: int
    gfa_sqm: float
    pros: List[str]
    cons: List[str]
    is_recommended: bool = False


class M4BuildingScaleReport(BaseModel):
    """M4: 건축 규모 검토 보고서"""
    module_name: str = "M4"
    module_title: str = "건축 규모 검토"
    
    # 기본 정보
    context_id: str
    address: str
    generated_at: str
    
    # 법적 최대 규모
    legal_far: float
    legal_bcr: float
    legal_units: int
    legal_gfa: float
    
    # 인센티브 적용 규모
    incentive_far: float
    incentive_units: int
    incentive_gfa: float
    units_increase: int
    
    # 시나리오 비교
    scenarios: List[BuildingScenario]
    
    # 주차 계획
    parking_alternatives: List[Dict[str, Any]]
    
    # 동선 효율 분석
    circulation_efficiency: str
    
    # 구조 효율 분석
    structural_efficiency: str
    
    # 최적 규모 선택 논리
    optimal_selection_logic: str


class M5FeasibilityReport(BaseModel):
    """M5: 사업성 분석 보고서"""
    module_name: str = "M5"
    module_title: str = "사업성 분석"
    
    # 기본 정보
    context_id: str
    address: str
    generated_at: str
    
    # 재무지표
    irr_pct: float
    npv_krw: str
    roi_pct: float
    payback_years: float
    
    # 비용 구조
    land_cost_krw: str
    land_cost_ratio: float
    construction_cost_krw: str
    construction_cost_ratio: float
    indirect_cost_krw: str
    indirect_cost_ratio: float
    total_cost_krw: str
    
    # 수익 구조
    rental_revenue_krw: str
    total_revenue_krw: str
    net_profit_krw: str
    
    # 사업비 구조 설명
    cost_structure_explanation: str
    
    # IRR/NPV 해석
    irr_interpretation: str
    npv_interpretation: str
    
    # Sensitivity 분석
    sensitivity_analysis: Dict[str, Any]
    
    # 리스크 해석
    risk_interpretation: str
    
    # 투자 결정 권고
    investment_recommendation: str


class M6ComprehensiveDecisionReport(BaseModel):
    """M6: 종합 판단 보고서"""
    module_name: str = "M6"
    module_title: str = "종합 판단"
    
    # 기본 정보
    context_id: str
    address: str
    generated_at: str
    
    # 종합 점수 및 등급
    m6_total_score: float
    m6_grade: str
    m6_approval_probability: float
    m6_decision: str
    
    # 모듈별 결과 요약
    m2_summary: str
    m3_summary: str
    m4_summary: str
    m5_summary: str
    
    # 세부 점수
    location_score: float
    location_max: float
    location_ratio: float
    scale_score: float
    scale_max: float
    scale_ratio: float
    feasibility_score: float
    feasibility_max: float
    feasibility_ratio: float
    compliance_score: float
    compliance_max: float
    compliance_ratio: float
    
    # 긍정 요인
    positive_factors: List[str]
    
    # 리스크 요인
    risk_factors: List[str]
    
    # 필수 요건 검증
    hard_fail_items: List[Dict[str, Any]]
    
    # 조건부 추진 시나리오
    conditional_scenarios: List[str]
    
    # 다음 단계 실사 계획
    next_steps: List[str]
    
    # 최종 권고사항
    final_recommendations: List[str]


# ========================================
# 6종 보고서 데이터 모델
# ========================================

class ReportMetadata(BaseModel):
    """보고서 메타데이터"""
    report_type: ReportTypeEnum
    report_title: str
    report_subtitle: str
    context_id: str
    address: str
    generated_at: str
    version: str = "2.0"


class TypeAComprehensiveReport(BaseModel):
    """Type A: 종합 최종보고서 (Master Comprehensive)"""
    metadata: ReportMetadata
    
    # Executive Summary
    final_decision: str
    final_decision_interpretation: str
    decision_class: str  # "positive", "conditional", "negative"
    approval_probability_pct: float
    grade: str
    total_score: float
    key_findings: List[str]
    key_risks: List[str]
    
    # 모듈별 데이터
    m2_data: Optional[M2LandAppraisalReport] = None
    m3_data: Optional[M3SupplyTypeReport] = None
    m4_data: Optional[M4BuildingScaleReport] = None
    m5_data: Optional[M5FeasibilityReport] = None
    m6_data: Optional[M6ComprehensiveDecisionReport] = None
    
    # M7 커뮤니티 계획 (선택)
    community_plan: Optional[Dict[str, Any]] = None
    
    # 부록 데이터
    appendix_transaction_cases: List[TransactionCase] = []
    appendix_regulations: List[str] = []
    appendix_calculations: Dict[str, Any] = {}


class TypeBLandownerReport(BaseModel):
    """Type B: 토지주 제출용 보고서"""
    metadata: ReportMetadata
    
    # 대상지 개요
    site_overview: str
    
    # LH 공공매입임대 소개
    lh_program_intro: str
    
    # 토지 가치 평가 (M2 요약)
    land_value_summary: str
    land_value_krw: str
    
    # 건축 계획 개요 (M4 요약)
    building_plan_summary: str
    
    # 안정성 및 신뢰성
    stability_explanation: str
    
    # 예상 일정 및 절차
    schedule_and_process: List[str]
    
    # Q&A
    faq_items: List[Dict[str, str]]


class TypeCLHTechnicalReport(BaseModel):
    """Type C: LH 기술검증 보고서"""
    metadata: ReportMetadata
    
    # 사업 개요
    project_overview: str
    
    # 입지 분석 (M1 요약)
    location_analysis_summary: str
    
    # 토지 평가 (M2 요약)
    land_appraisal_summary: str
    
    # 공급 유형 분석 (M3)
    supply_type_analysis: str
    
    # 건축 계획 (M4)
    building_plan: str
    
    # 사업성 검토 (M5 요약)
    feasibility_summary: str
    
    # 커뮤니티 계획 (M7 요약)
    community_plan_summary: str
    
    # LH 심사 기준 충족 여부 (M6)
    lh_compliance_check: Dict[str, Any]
    
    # 첨부 자료
    attachments: List[str]


class TypeDInvestorReport(BaseModel):
    """Type D: 사업성·투자 검토 보고서"""
    metadata: ReportMetadata
    
    # Executive Summary (투자 관점)
    investment_summary: str
    
    # 사업 개요
    project_overview: str
    
    # 재무지표 분석 (M5 중심)
    financial_metrics: Dict[str, Any]
    
    # 비용 구조 상세
    cost_structure_detail: Dict[str, Any]
    
    # 수익 구조 상세
    revenue_structure_detail: Dict[str, Any]
    
    # Sensitivity 분석
    sensitivity_analysis: Dict[str, Any]
    
    # 리스크 평가
    risk_assessment: Dict[str, Any]
    
    # 투자 의견
    investment_opinion: str
    
    # 첨부 자료
    attachments: List[str]


class TypeEPreliminaryReport(BaseModel):
    """Type E: 사전 검토 리포트"""
    metadata: ReportMetadata
    
    # Executive Summary (1페이지)
    executive_summary: str
    
    # M2 토지평가 요약 (1페이지)
    m2_summary: str
    
    # M3 공급 유형 요약 (1페이지)
    m3_summary: str
    
    # M4 건축 규모 요약 (1페이지)
    m4_summary: str
    
    # M5 사업성 요약 (1페이지)
    m5_summary: str
    
    # M6 종합 판단 (1페이지)
    m6_summary: str
    
    # 다음 단계 (1페이지)
    next_steps: List[str]


class TypeFPresentationReport(BaseModel):
    """Type F: 설명용 프레젠테이션"""
    metadata: ReportMetadata
    
    # 슬라이드 데이터
    slides: List[Dict[str, Any]]
    
    # 대상지 위치 (지도 URL)
    map_url: Optional[str] = None
    
    # 핵심 지표 (카드 형식)
    key_metrics: Dict[str, Any]
    
    # 토지 가치 (차트 데이터)
    land_value_chart: Dict[str, Any]
    
    # 공급 유형 (비교표)
    supply_type_comparison: Dict[str, Any]
    
    # 건축 계획 (다이어그램)
    building_plan_diagram: Optional[str] = None
    
    # 사업성 (재무 차트)
    feasibility_chart: Dict[str, Any]
    
    # 종합 판단 (결정 카드)
    decision_card: Dict[str, Any]


# ========================================
# API Response 모델
# ========================================

class ModuleReportResponse(BaseModel):
    """모듈별 보고서 응답"""
    success: bool
    message: str
    module: ModuleEnum
    context_id: str
    html_content: Optional[str] = None
    pdf_url: Optional[str] = None
    generated_at: str


class SixTypesReportResponse(BaseModel):
    """6종 보고서 응답"""
    success: bool
    message: str
    report_type: ReportTypeEnum
    context_id: str
    html_content: Optional[str] = None
    pdf_url: Optional[str] = None
    generated_at: str
    page_count: Optional[int] = None


# ========================================
# 보고서 생성 요청 모델
# ========================================

class ReportGenerationRequest(BaseModel):
    """보고서 생성 요청"""
    context_id: str
    report_type: Optional[ReportTypeEnum] = None
    module: Optional[ModuleEnum] = None
    include_m7: bool = Field(default=True, description="M7 커뮤니티 계획 포함 여부")
    expand_appendix: bool = Field(default=True, description="부록 확장 여부")
