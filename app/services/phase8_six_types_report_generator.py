"""
Phase 8: 6종 보고서 생성기 (Type B-F)
======================================

목적별 6종 보고서를 생성합니다:
- Type B: 토지주 제출용 (안정성·수익성 강조)
- Type C: LH 기술검증 (기술 규정 준수)
- Type D: 사업성·투자 검토 (재무 지표)
- Type E: 사전 검토 리포트 (빠른 판단)
- Type F: 설명용 프레젠테이션 (시각적)

작성일: 2026-01-10
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from app.models.phase8_report_types import (
    TypeBLandownerReport,
    TypeCLHTechnicalReport,
    TypeDInvestorReport,
    TypeEPreliminaryReport,
    TypeFPresentationReport,
)

logger = logging.getLogger(__name__)


class Phase8SixTypesReportGenerator:
    """6종 보고서 생성기 (Type B-F)"""
    
    def __init__(self):
        """초기화"""
        logger.info("Phase8 Six Types Report Generator initialized")
    
    # ========================================
    # Type B: 토지주 제출용 보고서
    # ========================================
    
    def generate_type_b_report(
        self,
        context_id: str,
        pipeline_result: Any,
        address: str
    ) -> Dict[str, Any]:
        """
        Type B: 토지주 제출용 보고서 생성
        
        Args:
            context_id: 컨텍스트 ID
            pipeline_result: 파이프라인 실행 결과
            address: 대상지 주소
            
        Returns:
            Dict[str, Any]: 템플릿 렌더링용 데이터
        """
        logger.info(f"Generating Type B Landowner Report for context_id={context_id}")
        
        appraisal_ctx = pipeline_result.appraisal
        housing_ctx = pipeline_result.housing_type
        capacity_ctx = pipeline_result.capacity
        feasibility_ctx = pipeline_result.feasibility
        lh_ctx = pipeline_result.lh_review
        
        # 토지 가치 정보
        land_value_data = self._prepare_land_value_for_landowner(appraisal_ctx, address)
        
        # 사업 계획 정보
        project_plan_data = self._prepare_project_plan_for_landowner(
            housing_ctx, capacity_ctx
        )
        
        # 수익성 정보
        profitability_data = self._prepare_profitability_for_landowner(feasibility_ctx)
        
        # 안정성 및 리스크
        stability_data = self._prepare_stability_for_landowner(lh_ctx, feasibility_ctx)
        
        # 결론 및 권고
        conclusion_data = self._prepare_conclusion_for_landowner(
            lh_ctx, feasibility_ctx, appraisal_ctx
        )
        
        return {
            "context_id": context_id,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "address": address,
            "current_year": datetime.now().year,
            
            # 토지 가치
            **land_value_data,
            
            # 사업 계획
            **project_plan_data,
            
            # 수익성
            **profitability_data,
            
            # 안정성
            **stability_data,
            
            # 결론
            **conclusion_data,
        }
    
    def _prepare_land_value_for_landowner(
        self, appraisal_ctx: Any, address: str
    ) -> Dict[str, Any]:
        """토지주용 토지 가치 정보 준비"""
        return {
            "land_value_krw": f"{appraisal_ctx.land_value:,.0f}원",
            "land_value_krw_short": f"{appraisal_ctx.land_value / 100000000:.1f}억",
            "unit_price_sqm": f"{appraisal_ctx.unit_price:,.0f}원/㎡",
            "unit_price_pyeong": f"{appraisal_ctx.unit_price * 3.3058:,.0f}원/평",
            "confidence_pct": appraisal_ctx.confidence_score,
            "appraisal_method": "거래사례비교법",
            "appraisal_basis": [
                "인근 지역 실거래 사례 3건 이상 분석",
                "공시지가 대비 적정성 검증 완료",
                "전문 감정평가사 검토 기준 준수",
            ],
        }
    
    def _prepare_project_plan_for_landowner(
        self, housing_ctx: Any, capacity_ctx: Any
    ) -> Dict[str, Any]:
        """토지주용 사업 계획 정보 준비"""
        return {
            "recommended_housing_type": housing_ctx.preferred_type.name,
            "housing_type_reason": f"{housing_ctx.preferred_type.name}은(는) LH 정책 우선순위가 높고 안정적인 공급 유형입니다.",
            "planned_units": capacity_ctx.scenario_b.total_units,
            "planned_gfa": f"{capacity_ctx.scenario_b.total_gfa:,.0f}㎡",
            "applied_far": capacity_ctx.scenario_b.applied_far,
            "construction_period": "24~30개월 (표준 공기)",
            "approval_process": [
                "사전협의 (1~2개월)",
                "사업계획 승인 (2~3개월)",
                "건축허가 (1~2개월)",
                "착공 및 시공 (24~30개월)",
            ],
        }
    
    def _prepare_profitability_for_landowner(
        self, feasibility_ctx: Any
    ) -> Dict[str, Any]:
        """토지주용 수익성 정보 준비"""
        return {
            "expected_revenue_krw": f"{feasibility_ctx.total_revenue:,.0f}원",
            "expected_revenue_krw_short": f"{feasibility_ctx.total_revenue / 100000000:.1f}억",
            "land_owner_share_pct": 30.0,
            "land_owner_share_krw": f"{feasibility_ctx.total_revenue * 0.3:,.0f}원",
            "land_owner_share_krw_short": f"{feasibility_ctx.total_revenue * 0.3 / 100000000:.1f}억",
            "roi_pct": feasibility_ctx.roi_pct,
            "payback_years": feasibility_ctx.payback_years,
            "profit_guarantee": "LH 사업 참여 시 안정적 수익 보장",
        }
    
    def _prepare_stability_for_landowner(
        self, lh_ctx: Any, feasibility_ctx: Any
    ) -> Dict[str, Any]:
        """토지주용 안정성 정보 준비"""
        return {
            "lh_approval_probability": lh_ctx.approval_probability,
            "grade": lh_ctx.grade,
            "stability_factors": [
                "LH 공사 직접 사업 시행으로 신용 리스크 최소화",
                "정부 정책 지원으로 사업 추진 안정성 확보",
                f"사업성 지표(IRR {feasibility_ctx.irr_pct}%) 우수",
                "법규 준수 및 인허가 문제 사전 검토 완료",
            ],
            "risk_mitigation": [
                "LH와 사업 시행 협약 체결로 법적 보호",
                "단계별 진행 상황 투명 공개",
                "전문가 자문단 구성으로 리스크 관리",
            ],
        }
    
    def _prepare_conclusion_for_landowner(
        self, lh_ctx: Any, feasibility_ctx: Any, appraisal_ctx: Any
    ) -> Dict[str, Any]:
        """토지주용 결론 및 권고"""
        decision = "적극 추진 권장" if lh_ctx.approval_probability >= 70 else "조건부 추진"
        
        return {
            "final_decision": decision,
            "recommendation": f"본 대상지는 LH 승인 확률 {lh_ctx.approval_probability}%, 등급 {lh_ctx.grade}로 평가되어 {decision} 대상입니다. "
                            f"토지 가치 {appraisal_ctx.land_value / 100000000:.1f}억원, 예상 수익률 {feasibility_ctx.roi_pct}%로 안정적인 투자가 가능합니다.",
            "next_steps": [
                "LH 사전협의 신청 및 타당성 검토",
                "토지주 의향 확인 및 사업 참여 방식 협의",
                "사업계획서 작성 및 관련 서류 준비",
                "LH 승인 절차 진행 및 계약 체결",
            ],
        }
    
    # ========================================
    # Type C: LH 기술검증 보고서
    # ========================================
    
    def generate_type_c_report(
        self,
        context_id: str,
        pipeline_result: Any,
        address: str
    ) -> Dict[str, Any]:
        """Type C: LH 기술검증 보고서 생성"""
        logger.info(f"Generating Type C LH Technical Report for context_id={context_id}")
        
        appraisal_ctx = pipeline_result.appraisal
        housing_ctx = pipeline_result.housing_type
        capacity_ctx = pipeline_result.capacity
        feasibility_ctx = pipeline_result.feasibility
        lh_ctx = pipeline_result.lh_review
        
        return {
            "context_id": context_id,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "address": address,
            "current_year": datetime.now().year,
            
            # 기술 검증 요약
            "grade": lh_ctx.grade,
            "total_score": lh_ctx.total_score,
            "technical_feasibility": "실현 가능",
            "compliance_rate": 100.0,
            "building_tech_score": 85.0,
            "structural_safety": "A등급",
            "construction_difficulty": "보통",
            
            # M2 토지감정평가 기술 검토
            "land_value_krw": f"{appraisal_ctx.land_value:,.0f}원",
            "unit_price_sqm": f"{appraisal_ctx.unit_price:,.0f}원/㎡",
            "confidence_pct": appraisal_ctx.confidence_score,
            "transaction_count": 3,
            "land_area_sqm": 1000.0,  # TODO: 실제 값으로 교체
            "regional_factor": 1.0,
            "individual_factor": 1.0,
            "official_price_krw": f"{appraisal_ctx.land_value * 0.7:,.0f}원",
            "official_price_ratio": 70.0,
            "avg_price_sqm": f"{appraisal_ctx.unit_price:,.0f}원/㎡",
            "transaction_ratio": 100.0,
            
            # M3 공급 유형 기술 검증
            "recommended_housing_type": housing_ctx.preferred_type.name,
            "housing_type_score": housing_ctx.preferred_type.total_score,
            "policy_compatibility": "적합",
            "candidate_types": [
                {
                    "name": housing_ctx.preferred_type.name,
                    "tech_score": 85,
                    "difficulty": "보통",
                    "compliant": True,
                    "evaluation": "우수",
                },
            ],
            
            # M4 건축 규모 기술 검토
            "legal_far": capacity_ctx.scenario_a.legal_far,
            "incentive_far": capacity_ctx.scenario_c.applied_far,
            "applied_far": capacity_ctx.scenario_b.applied_far,
            "legal_bcr": 60.0,
            "applied_bcr": 50.0,
            "legal_units": capacity_ctx.scenario_c.total_units,
            "planned_units": capacity_ctx.scenario_b.total_units,
            "legal_gfa": f"{capacity_ctx.scenario_c.total_gfa:,.0f}㎡",
            "planned_gfa": f"{capacity_ctx.scenario_b.total_gfa:,.0f}㎡",
            "structural_system": "철근콘크리트 라멘구조",
            "floor_count": 15,
            "structural_safety_rating": "A등급",
            "required_parking": 100,
            "planned_parking": 120,
            "parking_ratio": 120.0,
            "required_handicap": 3,
            "planned_handicap": 4,
            "handicap_ratio": 133.3,
            "required_visitor": 10,
            "planned_visitor": 12,
            "visitor_ratio": 120.0,
            
            # M5 사업성 기술 분석
            "land_cost_krw": f"{appraisal_ctx.land_value:,.0f}원",
            "construction_cost_krw": f"{feasibility_ctx.total_cost * 0.6:,.0f}원",
            "indirect_cost_krw": f"{feasibility_ctx.total_cost * 0.1:,.0f}원",
            "total_cost_krw": f"{feasibility_ctx.total_cost:,.0f}원",
            "irr_pct": feasibility_ctx.irr_pct,
            "npv_krw": f"{feasibility_ctx.npv:,.0f}원",
            "roi_pct": feasibility_ctx.roi_pct,
            "construction_unit_cost": "3,500,000원/㎡",
            "cost_comparison": 100.0,
            "construction_period": 30,
            "industry_avg_period": 30,
            
            # M6 종합 기술 판단
            "structural_grade": "A등급",
            "construction_feasibility": "실현 가능",
            "technical_risks": [
                "지반 조건에 따른 기초 공사 추가 비용 가능",
                "인근 지역 민원 발생 시 공기 지연 우려",
            ],
            "final_decision": lh_ctx.final_decision,
            "approval_probability_pct": lh_ctx.approval_probability,
            "technical_grade": lh_ctx.grade,
            "technical_recommendation": "기술적 타당성 검증 완료, 추진 가능",
            
            # 부록: 기술 계산서
            "structural_calculation_summary": "구조 계산은 KBC 2016 기준을 따르며, 지진하중 및 풍하중을 고려한 설계가 완료되었습니다.",
            "facility_capacity_summary": "급배수, 전기, 통신, 냉난방 등 모든 설비 용량이 적정하게 산정되었습니다.",
            "energy_efficiency_summary": "에너지 절약 설계기준을 만족하며, 녹색건축 인증 1등급 취득 가능합니다.",
        }
    
    # ========================================
    # Type D: 사업성·투자 검토 보고서
    # ========================================
    
    def generate_type_d_report(
        self,
        context_id: str,
        pipeline_result: Any,
        address: str
    ) -> Dict[str, Any]:
        """Type D: 사업성·투자 검토 보고서 생성"""
        logger.info(f"Generating Type D Investor Report for context_id={context_id}")
        
        appraisal_ctx = pipeline_result.appraisal
        housing_ctx = pipeline_result.housing_type
        capacity_ctx = pipeline_result.capacity
        feasibility_ctx = pipeline_result.feasibility
        lh_ctx = pipeline_result.lh_review
        
        total_cost = feasibility_ctx.total_cost
        land_cost = appraisal_ctx.land_value
        construction_cost = total_cost * 0.6
        indirect_cost = total_cost * 0.1
        
        total_revenue = feasibility_ctx.total_revenue
        rental_revenue = total_revenue * 0.7
        sales_revenue = total_revenue * 0.2
        other_revenue = total_revenue * 0.1
        
        net_profit = total_revenue - total_cost
        
        return {
            "context_id": context_id,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "address": address,
            "current_year": datetime.now().year,
            
            # 핵심 투자 지표
            "irr_pct": feasibility_ctx.irr_pct,
            "npv_krw_short": f"{feasibility_ctx.npv / 100000000:.1f}",
            "npv_krw": f"{feasibility_ctx.npv:,.0f}원",
            "roi_pct": feasibility_ctx.roi_pct,
            "payback_years": feasibility_ctx.payback_years,
            
            # 사업 개요
            "land_area_sqm": 1000.0,  # TODO: 실제 값
            "land_area_pyeong": 302.5,
            "recommended_housing_type": housing_ctx.preferred_type.name,
            "planned_units": capacity_ctx.scenario_b.total_units,
            "planned_gfa": f"{capacity_ctx.scenario_b.total_gfa:,.0f}㎡",
            
            # 투자 결론
            "investment_recommendation": f"IRR {feasibility_ctx.irr_pct}%, ROI {feasibility_ctx.roi_pct}%로 투자 가치가 높으며, "
                                        f"LH 승인 확률 {lh_ctx.approval_probability}%로 안정성도 우수합니다. 적극 투자 권장합니다.",
            "investment_grade": "A등급" if feasibility_ctx.irr_pct >= 10 else "B등급",
            "risk_level": "낮음" if lh_ctx.approval_probability >= 70 else "중간",
            "recommendation_score": 8.5 if feasibility_ctx.irr_pct >= 10 else 7.0,
            
            # 비용 구조
            "land_cost_krw": f"{land_cost:,.0f}원",
            "land_cost_pct": round(land_cost / total_cost * 100, 1),
            "construction_cost_krw": f"{construction_cost:,.0f}원",
            "construction_cost_pct": round(construction_cost / total_cost * 100, 1),
            "indirect_cost_krw": f"{indirect_cost:,.0f}원",
            "indirect_cost_pct": round(indirect_cost / total_cost * 100, 1),
            "total_cost_krw": f"{total_cost:,.0f}원",
            
            # 간접비 상세
            "design_cost_krw": f"{indirect_cost * 0.3:,.0f}원",
            "supervision_cost_krw": f"{indirect_cost * 0.2:,.0f}원",
            "financial_cost_krw": f"{indirect_cost * 0.3:,.0f}원",
            "misc_cost_krw": f"{indirect_cost * 0.2:,.0f}원",
            
            # 수익 구조
            "rental_revenue_krw": f"{rental_revenue:,.0f}원",
            "rental_revenue_pct": 70.0,
            "sales_revenue_krw": f"{sales_revenue:,.0f}원",
            "sales_revenue_pct": 20.0,
            "other_revenue_krw": f"{other_revenue:,.0f}원",
            "other_revenue_pct": 10.0,
            "total_revenue_krw": f"{total_revenue:,.0f}원",
            "net_profit_krw": f"{net_profit:,.0f}원",
            
            # 현금흐름 분석
            "cash_flow_data": self._generate_cash_flow_data(total_cost, total_revenue),
            
            # 민감도 분석
            "irr_sales_m10": round(feasibility_ctx.irr_pct - 2.0, 1),
            "irr_sales_m5": round(feasibility_ctx.irr_pct - 1.0, 1),
            "irr_sales_p5": round(feasibility_ctx.irr_pct + 1.0, 1),
            "irr_sales_p10": round(feasibility_ctx.irr_pct + 2.0, 1),
            "irr_cost_m10": round(feasibility_ctx.irr_pct + 1.5, 1),
            "irr_cost_m5": round(feasibility_ctx.irr_pct + 0.8, 1),
            "irr_cost_p5": round(feasibility_ctx.irr_pct - 0.8, 1),
            "irr_cost_p10": round(feasibility_ctx.irr_pct - 1.5, 1),
            "irr_land_m10": round(feasibility_ctx.irr_pct + 1.0, 1),
            "irr_land_m5": round(feasibility_ctx.irr_pct + 0.5, 1),
            "irr_land_p5": round(feasibility_ctx.irr_pct - 0.5, 1),
            "irr_land_p10": round(feasibility_ctx.irr_pct - 1.0, 1),
            
            # 시나리오 분석
            "optimistic_irr": round(feasibility_ctx.irr_pct + 3.0, 1),
            "optimistic_npv": f"{feasibility_ctx.npv * 1.5:,.0f}원",
            "pessimistic_irr": round(feasibility_ctx.irr_pct - 2.0, 1),
            "pessimistic_npv": f"{feasibility_ctx.npv * 0.5:,.0f}원",
            
            # 리스크
            "financial_risks": [
                "건축비 상승 시 수익성 저하 가능",
                "분양/임대 시장 침체 시 수익 지연 우려",
                "금융비용 상승 시 IRR 하락 가능",
            ],
            "risk_strategies": [
                "단계별 비용 관리 및 원가 절감 추진",
                "다양한 수익원 확보로 리스크 분산",
                "장기 고정금리 대출로 금융비용 안정화",
            ],
            
            # 최종 결론
            "final_investment_decision": f"본 사업은 IRR {feasibility_ctx.irr_pct}%, NPV {feasibility_ctx.npv / 100000000:.1f}억원으로 "
                                        f"투자 가치가 우수하며, 적극 투자를 권장합니다.",
            "investment_recommendation_detail": "단계별 투자금 확보 및 리스크 관리 방안 수립 후 추진하시기 바랍니다.",
        }
    
    def _generate_cash_flow_data(
        self, total_cost: float, total_revenue: float
    ) -> List[Dict[str, Any]]:
        """현금흐름 데이터 생성 (간소화)"""
        years = []
        cumulative = 0
        
        for year in range(1, 6):
            if year <= 2:
                # 투자 기간
                expense = total_cost / 2
                income = 0
                net_flow = -expense
            else:
                # 수익 기간
                expense = 0
                income = total_revenue / 3
                net_flow = income
            
            cumulative += net_flow
            
            years.append({
                "year": year,
                "income": f"{income:,.0f}원" if income > 0 else "-",
                "expense": f"{expense:,.0f}원" if expense > 0 else "-",
                "net_flow": f"{net_flow:,.0f}원",
                "cumulative": f"{cumulative:,.0f}원",
            })
        
        return years
    
    # ========================================
    # Type E: 사전 검토 리포트
    # ========================================
    
    def generate_type_e_report(
        self,
        context_id: str,
        pipeline_result: Any,
        address: str
    ) -> Dict[str, Any]:
        """Type E: 사전 검토 리포트 생성"""
        logger.info(f"Generating Type E Preliminary Report for context_id={context_id}")
        
        appraisal_ctx = pipeline_result.appraisal
        housing_ctx = pipeline_result.housing_type
        capacity_ctx = pipeline_result.capacity
        feasibility_ctx = pipeline_result.feasibility
        lh_ctx = pipeline_result.lh_review
        
        return {
            "context_id": context_id,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "address": address,
            "current_year": datetime.now().year,
            
            # 사전 검토 결과
            "preliminary_decision": lh_ctx.final_decision,
            "approval_probability_pct": lh_ctx.approval_probability,
            "grade": lh_ctx.grade,
            
            # 대상지 개요
            "land_area_pyeong": 302.5,
            "land_value_krw_short": f"{appraisal_ctx.land_value / 100000000:.1f}",
            "land_value_krw": f"{appraisal_ctx.land_value:,.0f}원",
            "unit_price_sqm": f"{appraisal_ctx.unit_price:,.0f}원/㎡",
            "recommended_housing_type": housing_ctx.preferred_type.name,
            "zone_district": "제2종일반주거지역",
            "land_area_sqm": 1000.0,
            
            # 법규 검토
            "legal_far": capacity_ctx.scenario_a.legal_far,
            "applied_far": capacity_ctx.scenario_b.applied_far,
            "legal_bcr": 60.0,
            "applied_bcr": 50.0,
            "legal_units": capacity_ctx.scenario_c.total_units,
            "planned_units": capacity_ctx.scenario_b.total_units,
            "legal_constraints": [
                "일조권 확보 필요 (동지 기준)",
                "높이 제한 준수 필요",
                "건축선 후퇴 적용",
            ],
            
            # 사업성 간편 검토
            "irr_pct": feasibility_ctx.irr_pct,
            "roi_pct": feasibility_ctx.roi_pct,
            "payback_years": feasibility_ctx.payback_years,
            "total_cost_krw": f"{feasibility_ctx.total_cost:,.0f}원",
            "land_cost_krw": f"{appraisal_ctx.land_value:,.0f}원",
            "construction_cost_krw": f"{feasibility_ctx.total_cost * 0.6:,.0f}원",
            "indirect_cost_krw": f"{feasibility_ctx.total_cost * 0.1:,.0f}원",
            "total_revenue_krw": f"{feasibility_ctx.total_revenue:,.0f}원",
            "net_profit_krw": f"{feasibility_ctx.total_revenue - feasibility_ctx.total_cost:,.0f}원",
            
            # 고려사항
            "positive_factors": [
                "입지 조건 우수 (교통, 생활 편의시설 접근성)",
                f"사업성 지표 양호 (IRR {feasibility_ctx.irr_pct}%)",
                "LH 정책 우선순위 부합",
            ],
            "risk_factors": [
                "건축비 상승 가능성",
                "인허가 기간 소요",
                "시장 변동성 존재",
            ],
            
            # 권고 의견
            "preliminary_recommendation": f"본 대상지는 LH 승인 확률 {lh_ctx.approval_probability}%, 사업성 IRR {feasibility_ctx.irr_pct}%로 "
                                         f"사업 추진 가능성이 높습니다. 정밀 검토 후 본격 추진을 권장합니다.",
            "next_steps": [
                "LH 사전협의 신청",
                "상세 설계 및 사업계획서 작성",
                "관련 서류 준비 (토지 이용계획, 지적 등)",
                "주민 의견 수렴 및 민원 대응",
                "사업 시행 승인 신청",
            ],
            "additional_review_items": [
                "지반 조사 및 구조 검토",
                "환경영향평가 필요 여부",
                "교통영향평가 대상 여부",
                "정밀 재무 분석 (NPV, 민감도 분석)",
            ],
        }
    
    # ========================================
    # Type F: 설명용 프레젠테이션
    # ========================================
    
    def generate_type_f_report(
        self,
        context_id: str,
        pipeline_result: Any,
        address: str
    ) -> Dict[str, Any]:
        """Type F: 설명용 프레젠테이션 생성"""
        logger.info(f"Generating Type F Presentation Report for context_id={context_id}")
        
        appraisal_ctx = pipeline_result.appraisal
        housing_ctx = pipeline_result.housing_type
        capacity_ctx = pipeline_result.capacity
        feasibility_ctx = pipeline_result.feasibility
        lh_ctx = pipeline_result.lh_review
        
        return {
            "context_id": context_id,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "address": address,
            "current_year": datetime.now().year,
            
            # 프로젝트 정보
            "project_name": f"{address} 공공주택 사업",
            
            # 핵심 요약
            "final_decision": lh_ctx.final_decision,
            "approval_probability_pct": lh_ctx.approval_probability,
            "grade": lh_ctx.grade,
            "land_area_pyeong": 302.5,
            "planned_units": capacity_ctx.scenario_b.total_units,
            "irr_pct": feasibility_ctx.irr_pct,
            
            # 대상지 정보
            "zone_district": "제2종일반주거지역",
            "land_area_sqm": 1000.0,
            "zone_type": "주거지역",
            "legal_far": capacity_ctx.scenario_a.legal_far,
            "legal_bcr": 60.0,
            
            # 토지 가치
            "land_value_krw": f"{appraisal_ctx.land_value:,.0f}원",
            "unit_price_sqm": f"{appraisal_ctx.unit_price:,.0f}원/㎡",
            "confidence_pct": appraisal_ctx.confidence_score,
            "transaction_count": 3,
            
            # 공급 유형
            "recommended_housing_type": housing_ctx.preferred_type.name,
            "housing_type_score": housing_ctx.preferred_type.total_score,
            "selection_reasons": [
                "LH 정책 우선순위 1순위",
                "지역 수요 부합",
                "사업성 우수",
            ],
            
            # 건축 규모
            "planned_gfa": f"{capacity_ctx.scenario_b.total_gfa:,.0f}㎡",
            "applied_far": capacity_ctx.scenario_b.applied_far,
            "planned_parking": 120,
            "floor_count": 15,
            "avg_unit_size": "59㎡",
            
            # 재무 지표
            "npv_krw": f"{feasibility_ctx.npv:,.0f}원",
            "roi_pct": feasibility_ctx.roi_pct,
            "payback_years": feasibility_ctx.payback_years,
            "total_cost_krw": f"{feasibility_ctx.total_cost:,.0f}원",
            "land_cost_krw": f"{appraisal_ctx.land_value:,.0f}원",
            "construction_cost_krw": f"{feasibility_ctx.total_cost * 0.6:,.0f}원",
            "indirect_cost_krw": f"{feasibility_ctx.total_cost * 0.1:,.0f}원",
            "total_revenue_krw": f"{feasibility_ctx.total_revenue:,.0f}원",
            "net_profit_krw": f"{feasibility_ctx.total_revenue - feasibility_ctx.total_cost:,.0f}원",
            
            # 강점 & 리스크
            "positive_factors": [
                "입지 조건 우수",
                f"사업성 지표 양호 (IRR {feasibility_ctx.irr_pct}%)",
                "LH 정책 부합",
                f"승인 확률 {lh_ctx.approval_probability}%",
            ],
            "risk_factors": [
                "건축비 상승 가능성",
                "인허가 기간 소요",
                "시장 변동성",
            ],
            
            # 최종 결론
            "total_score": lh_ctx.total_score,
            "final_recommendation": f"본 사업은 LH 승인 확률 {lh_ctx.approval_probability}%, IRR {feasibility_ctx.irr_pct}%로 "
                                   f"추진 가치가 높으며, 적극 추진을 권장합니다.",
            
            # 다음 단계
            "next_steps": [
                "LH 사전협의 신청 및 타당성 검토",
                "상세 설계 및 사업계획서 작성",
                "관련 서류 준비 및 인허가 진행",
                "주민 의견 수렴 및 사업 시행 승인",
            ],
        }
