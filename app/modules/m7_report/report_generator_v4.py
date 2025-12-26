"""
M7 Report Generator V4 (ZeroSite 4.0)
======================================

M6 LH Comprehensive Judgement 결과를 전문가 보고서로 변환

보고서 구조:
- Executive Summary (경영진 요약)
- LH Scorecard (100점 평가표)
- Section Analysis (5개 섹션 상세 분석)
- Improvement Roadmap (개선 로드맵)
- Financial Analysis (재무 분석)
- Technical Appendix (기술 부록)

Author: ZeroSite M7 Team
Date: 2025-12-26
Version: 4.0
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.appraisal_context import AppraisalContext
from app.core.context.housing_type_context import HousingTypeContext
from app.core.context.capacity_context_v2 import CapacityContextV2
from app.core.context.feasibility_context import FeasibilityContext
from app.modules.m6_lh_review.comprehensive_judgement import M6ComprehensiveResult

logger = logging.getLogger(__name__)


class ReportGeneratorV4:
    """
    ZeroSite 4.0 전문가 보고서 생성기
    
    입력:
    - M1~M6 전체 Context
    
    출력:
    - 구조화된 보고서 데이터 (Dict)
    - HTML/PDF 렌더링 준비 완료
    """
    
    def __init__(self):
        """보고서 생성기 초기화"""
        logger.info("="*80)
        logger.info("📄 ZeroSite v4.0 Report Generator Initialized")
        logger.info("="*80)
    
    def generate(
        self,
        land_ctx: CanonicalLandContext,
        appraisal_ctx: AppraisalContext,
        housing_type_ctx: HousingTypeContext,
        capacity_ctx: CapacityContextV2,
        feasibility_ctx: FeasibilityContext,
        m6_result: M6ComprehensiveResult
    ) -> Dict[str, Any]:
        """
        전문가 보고서 생성
        
        Args:
            land_ctx: M1 토지 정보
            appraisal_ctx: M2 감정 평가
            housing_type_ctx: M3 주거 유형
            capacity_ctx: M4 건축 규모
            feasibility_ctx: M5 사업성
            m6_result: M6 최종 판단
        
        Returns:
            구조화된 보고서 데이터
        """
        logger.info("\n" + "="*80)
        logger.info("📄 GENERATING PROFESSIONAL REPORT")
        logger.info("="*80)
        
        report = {
            "metadata": self._build_metadata(land_ctx),
            "executive_summary": self._build_executive_summary(
                land_ctx, appraisal_ctx, capacity_ctx, feasibility_ctx, m6_result
            ),
            "lh_scorecard": self._build_lh_scorecard(m6_result),
            "section_analysis": self._build_section_analysis(m6_result),
            "improvement_roadmap": self._build_improvement_roadmap(m6_result),
            "financial_analysis": self._build_financial_analysis(
                appraisal_ctx, capacity_ctx, feasibility_ctx
            ),
            "technical_appendix": self._build_technical_appendix(
                land_ctx, housing_type_ctx, capacity_ctx
            ),
            "conclusion": self._build_conclusion(m6_result)
        }
        
        logger.info("✅ Professional report generated successfully")
        logger.info("="*80 + "\n")
        
        return report
    
    def _build_metadata(self, land_ctx: CanonicalLandContext) -> Dict:
        """보고서 메타데이터"""
        return {
            "report_title": "LH 매입임대주택 사업 타당성 검토 보고서",
            "report_version": "ZeroSite v4.0",
            "generated_at": datetime.now().isoformat(),
            "site_address": land_ctx.address,
            "site_coordinates": {
                "lat": land_ctx.coordinates[0],
                "lng": land_ctx.coordinates[1]
            },
            "report_id": f"LH-{land_ctx.parcel_id}-{datetime.now().strftime('%Y%m%d')}"
        }
    
    def _build_executive_summary(
        self,
        land_ctx: CanonicalLandContext,
        appraisal_ctx: AppraisalContext,
        capacity_ctx: CapacityContextV2,
        feasibility_ctx: FeasibilityContext,
        m6_result: M6ComprehensiveResult
    ) -> Dict:
        """경영진 요약 (Executive Summary)"""
        
        # 핵심 지표
        key_metrics = {
            "total_score": f"{m6_result.lh_score_total:.1f}/100",
            "judgement": m6_result.judgement.value,
            "grade": m6_result.grade.value,
            "region": m6_result.region_weight.value,
            "land_value": f"₩{appraisal_ctx.land_value:,.0f}",
            "total_units": capacity_ctx.incentive_capacity.total_units,
            "npv": f"₩{feasibility_ctx.financial_metrics.npv_public:,.0f}",
            "irr": f"{feasibility_ctx.financial_metrics.irr_public:.2f}%"
        }
        
        # 핵심 강점 (Top 3)
        strengths = []
        if m6_result.section_b_location.raw_score >= 18:
            strengths.append("입지 우수 (역세권/생활SOC)")
        if m6_result.section_a_policy.raw_score >= 20:
            strengths.append("정책 부합도 높음")
        if m6_result.section_c_construction.raw_score >= 15:
            strengths.append("건축 가능성 양호")
        
        # 핵심 약점 (Top 3)
        weaknesses = []
        if m6_result.section_e_business.raw_score < 10:
            weaknesses.append("사업성 개선 필요")
        if m6_result.section_c_construction.raw_score < 15:
            weaknesses.append("규모/주차 미달")
        if m6_result.section_d_price.raw_score < 10:
            weaknesses.append("매입가 조정 필요")
        
        # 즉시 대응 필요 항목
        immediate_actions = []
        if m6_result.fatal_reject:
            immediate_actions = m6_result.reject_reasons
        else:
            # 점수 낮은 섹션 우선
            if m6_result.section_e_business.raw_score < 10:
                immediate_actions.append("사업성 개선 방안 수립")
            if m6_result.section_c_construction.raw_score < 12:
                immediate_actions.append("세대수/주차 계획 조정")
            if m6_result.section_d_price.raw_score < 8:
                immediate_actions.append("매입가 협상 전략 수립")
        
        return {
            "title": "경영진 요약 (Executive Summary)",
            "key_metrics": key_metrics,
            "strengths": strengths[:3],
            "weaknesses": weaknesses[:3],
            "immediate_actions": immediate_actions[:3],
            "recommendation": self._get_recommendation(m6_result.judgement)
        }
    
    def _get_recommendation(self, judgement) -> str:
        """최종 권고사항"""
        if judgement.value == "GO":
            return "✅ LH 제안 추천: 즉시 진행 가능"
        elif judgement.value == "CONDITIONAL":
            return "⚠️ 조건부 추천: 개선 방안 이행 후 진행"
        else:
            return "❌ 진행 불가: 근본적 개선 또는 대안 검토 필요"
    
    def _build_lh_scorecard(self, m6_result: M6ComprehensiveResult) -> Dict:
        """LH 100점 평가표"""
        return {
            "title": "LH 100점 평가표 (Comprehensive Scorecard)",
            "total_score": m6_result.lh_score_total,
            "judgement": m6_result.judgement.value,
            "grade": m6_result.grade.value,
            "fatal_reject": m6_result.fatal_reject,
            "sections": {
                "policy": {
                    "name": "[A] 정책·유형 적합성",
                    "raw_score": m6_result.section_a_policy.raw_score,
                    "weighted_score": m6_result.section_a_policy.weighted_score,
                    "max_score": m6_result.section_a_policy.max_score,
                    "percentage": (m6_result.section_a_policy.raw_score / m6_result.section_a_policy.max_score) * 100,
                    "items": m6_result.section_a_policy.items,
                    "status": self._get_status(m6_result.section_a_policy.raw_score, m6_result.section_a_policy.max_score)
                },
                "location": {
                    "name": "[B] 입지·환경 평가",
                    "raw_score": m6_result.section_b_location.raw_score,
                    "weighted_score": m6_result.section_b_location.weighted_score,
                    "max_score": m6_result.section_b_location.max_score,
                    "percentage": (m6_result.section_b_location.raw_score / m6_result.section_b_location.max_score) * 100,
                    "items": m6_result.section_b_location.items,
                    "status": self._get_status(m6_result.section_b_location.raw_score, m6_result.section_b_location.max_score)
                },
                "construction": {
                    "name": "[C] 건축 가능성",
                    "raw_score": m6_result.section_c_construction.raw_score,
                    "weighted_score": m6_result.section_c_construction.weighted_score,
                    "max_score": m6_result.section_c_construction.max_score,
                    "percentage": (m6_result.section_c_construction.raw_score / m6_result.section_c_construction.max_score) * 100,
                    "items": m6_result.section_c_construction.items,
                    "status": self._get_status(m6_result.section_c_construction.raw_score, m6_result.section_c_construction.max_score)
                },
                "price": {
                    "name": "[D] 가격·매입 적정성",
                    "raw_score": m6_result.section_d_price.raw_score,
                    "weighted_score": m6_result.section_d_price.weighted_score,
                    "max_score": m6_result.section_d_price.max_score,
                    "percentage": (m6_result.section_d_price.raw_score / m6_result.section_d_price.max_score) * 100,
                    "items": m6_result.section_d_price.items,
                    "status": self._get_status(m6_result.section_d_price.raw_score, m6_result.section_d_price.max_score)
                },
                "business": {
                    "name": "[E] 사업성",
                    "raw_score": m6_result.section_e_business.raw_score,
                    "weighted_score": m6_result.section_e_business.weighted_score,
                    "max_score": m6_result.section_e_business.max_score,
                    "percentage": (m6_result.section_e_business.raw_score / m6_result.section_e_business.max_score) * 100,
                    "items": m6_result.section_e_business.items,
                    "status": self._get_status(m6_result.section_e_business.raw_score, m6_result.section_e_business.max_score)
                }
            },
            "applied_weights": m6_result.applied_weights,
            "region_weight": m6_result.region_weight.value
        }
    
    def _get_status(self, score: float, max_score: float) -> str:
        """섹션 상태 평가"""
        percentage = (score / max_score) * 100
        if percentage >= 80:
            return "우수"
        elif percentage >= 60:
            return "양호"
        elif percentage >= 40:
            return "보통"
        else:
            return "미흡"
    
    def _build_section_analysis(self, m6_result: M6ComprehensiveResult) -> Dict:
        """섹션별 상세 분석"""
        return {
            "title": "섹션별 상세 분석 (Section Analysis)",
            "sections": [
                {
                    "id": "A",
                    "name": "정책·유형 적합성",
                    "score": m6_result.section_a_policy.raw_score,
                    "max": m6_result.section_a_policy.max_score,
                    "items": m6_result.section_a_policy.items,
                    "analysis": self._analyze_policy_section(m6_result.section_a_policy)
                },
                {
                    "id": "B",
                    "name": "입지·환경 평가",
                    "score": m6_result.section_b_location.raw_score,
                    "max": m6_result.section_b_location.max_score,
                    "items": m6_result.section_b_location.items,
                    "analysis": self._analyze_location_section(m6_result.section_b_location)
                },
                {
                    "id": "C",
                    "name": "건축 가능성",
                    "score": m6_result.section_c_construction.raw_score,
                    "max": m6_result.section_c_construction.max_score,
                    "items": m6_result.section_c_construction.items,
                    "analysis": self._analyze_construction_section(m6_result.section_c_construction)
                },
                {
                    "id": "D",
                    "name": "가격·매입 적정성",
                    "score": m6_result.section_d_price.raw_score,
                    "max": m6_result.section_d_price.max_score,
                    "items": m6_result.section_d_price.items,
                    "analysis": self._analyze_price_section(m6_result.section_d_price)
                },
                {
                    "id": "E",
                    "name": "사업성",
                    "score": m6_result.section_e_business.raw_score,
                    "max": m6_result.section_e_business.max_score,
                    "items": m6_result.section_e_business.items,
                    "analysis": self._analyze_business_section(m6_result.section_e_business)
                }
            ]
        }
    
    def _analyze_policy_section(self, section) -> str:
        """정책 섹션 분석"""
        score_pct = (section.raw_score / section.max_score) * 100
        if score_pct >= 80:
            return "정책 부합도가 우수합니다. 지역 수요와 세대 유형이 LH 정책 방향과 일치합니다."
        elif score_pct >= 60:
            return "정책 부합도가 양호합니다. 일부 조정을 통해 개선 가능합니다."
        else:
            return "정책 부합도 개선이 필요합니다. 세대 유형 변경 또는 지역 수요 재검토를 권장합니다."
    
    def _analyze_location_section(self, section) -> str:
        """입지 섹션 분석"""
        score_pct = (section.raw_score / section.max_score) * 100
        if score_pct >= 80:
            return "입지 조건이 우수합니다. 교통 접근성과 생활편의시설이 충분합니다."
        elif score_pct >= 60:
            return "입지 조건이 양호합니다. 교통 또는 편의시설 일부 보완이 필요할 수 있습니다."
        else:
            return "입지 조건 개선이 필요합니다. 역세권 접근성 또는 생활SOC 보완을 권장합니다."
    
    def _analyze_construction_section(self, section) -> str:
        """건축 섹션 분석"""
        score_pct = (section.raw_score / section.max_score) * 100
        if score_pct >= 80:
            return "건축 계획이 우수합니다. 세대수와 주차 계획이 법규를 충족합니다."
        elif score_pct >= 60:
            return "건축 계획이 양호합니다. 주차 또는 세대수 조정으로 개선 가능합니다."
        else:
            return "건축 계획 개선이 필요합니다. 세대수 증가 또는 주차 계획 재검토가 필요합니다."
    
    def _analyze_price_section(self, section) -> str:
        """가격 섹션 분석"""
        score_pct = (section.raw_score / section.max_score) * 100
        if score_pct >= 80:
            return "매입가가 LH 기준에 부합합니다. 인근 거래 대비 안정적입니다."
        elif score_pct >= 60:
            return "매입가가 LH 기준에 근접합니다. 협상을 통한 조정이 가능합니다."
        else:
            return "매입가 조정이 필요합니다. LH 기준 대비 초과폭이 크므로 협상이 필수입니다."
    
    def _analyze_business_section(self, section) -> str:
        """사업성 섹션 분석"""
        score_pct = (section.raw_score / section.max_score) * 100
        if score_pct >= 80:
            return "사업성이 우수합니다. NPV와 IRR이 LH 기준을 충족합니다."
        elif score_pct >= 60:
            return "사업성이 양호합니다. 공사비 절감 등으로 개선 가능합니다."
        else:
            return "사업성 개선이 필수입니다. 비용 구조 재검토 또는 수익 모델 개선이 필요합니다."
    
    def _build_improvement_roadmap(self, m6_result: M6ComprehensiveResult) -> Dict:
        """개선 로드맵"""
        return {
            "title": "개선 로드맵 (Improvement Roadmap)",
            "improvement_points": m6_result.improvement_points,
            "deduction_reasons": m6_result.deduction_reasons,
            "reject_reasons": m6_result.reject_reasons if m6_result.fatal_reject else [],
            "priority_actions": self._prioritize_actions(m6_result),
            "timeline": self._build_timeline(m6_result)
        }
    
    def _prioritize_actions(self, m6_result: M6ComprehensiveResult) -> List[Dict]:
        """우선순위 액션 항목"""
        actions = []
        
        # 즉시 탈락 사유 해결 (최우선)
        if m6_result.fatal_reject:
            for reason in m6_result.reject_reasons:
                actions.append({
                    "priority": "Critical",
                    "action": f"즉시 해결 필요: {reason}",
                    "timeline": "즉시"
                })
        
        # 섹션별 우선순위
        sections = [
            ("E", m6_result.section_e_business, "사업성"),
            ("C", m6_result.section_c_construction, "건축"),
            ("D", m6_result.section_d_price, "가격"),
            ("A", m6_result.section_a_policy, "정책"),
            ("B", m6_result.section_b_location, "입지")
        ]
        
        for section_id, section, name in sections:
            score_pct = (section.raw_score / section.max_score) * 100
            if score_pct < 60:
                actions.append({
                    "priority": "High",
                    "action": f"{name} 개선 ({score_pct:.0f}% → 80% 목표)",
                    "timeline": "1-2개월"
                })
            elif score_pct < 80:
                actions.append({
                    "priority": "Medium",
                    "action": f"{name} 최적화 ({score_pct:.0f}% → 90% 목표)",
                    "timeline": "2-3개월"
                })
        
        return actions[:5]  # Top 5
    
    def _build_timeline(self, m6_result: M6ComprehensiveResult) -> Dict:
        """개선 일정"""
        if m6_result.fatal_reject:
            return {
                "phase_1": "즉시: 탈락 사유 해결",
                "phase_2": "1개월: 재검토 및 재평가",
                "phase_3": "2개월: LH 제안 준비"
            }
        elif m6_result.judgement.value == "CONDITIONAL":
            return {
                "phase_1": "1개월: 주요 개선 사항 이행",
                "phase_2": "2개월: 검증 및 문서 준비",
                "phase_3": "3개월: LH 제안"
            }
        else:  # GO
            return {
                "phase_1": "즉시: LH 제안 문서 준비",
                "phase_2": "1개월: 제안 제출",
                "phase_3": "2개월: LH 검토 및 협상"
            }
    
    def _build_financial_analysis(
        self,
        appraisal_ctx: AppraisalContext,
        capacity_ctx: CapacityContextV2,
        feasibility_ctx: FeasibilityContext
    ) -> Dict:
        """재무 분석"""
        return {
            "title": "재무 분석 (Financial Analysis)",
            "land_acquisition": {
                "total_land_value": appraisal_ctx.land_value,
                "unit_price_sqm": appraisal_ctx.unit_price_sqm,
                "unit_price_pyeong": appraisal_ctx.unit_price_pyeong,
                "confidence": appraisal_ctx.confidence_score
            },
            "development_scale": {
                "total_units": capacity_ctx.incentive_capacity.total_units,
                "total_gfa_sqm": capacity_ctx.incentive_capacity.target_gfa_sqm,
                "far_applied": capacity_ctx.incentive_capacity.applied_far,
                "bcr_applied": capacity_ctx.incentive_capacity.applied_bcr
            },
            "cost_structure": {
                "total_cost": feasibility_ctx.cost_breakdown.total_cost,
                "land_cost": appraisal_ctx.land_value,
                "construction_cost": feasibility_ctx.cost_breakdown.total_cost - appraisal_ctx.land_value,
                "cost_per_unit": feasibility_ctx.cost_breakdown.total_cost / capacity_ctx.incentive_capacity.total_units
            },
            "revenue_projection": {
                "total_revenue": feasibility_ctx.revenue_projection.total_revenue,
                "revenue_per_unit": feasibility_ctx.revenue_projection.total_revenue / capacity_ctx.incentive_capacity.total_units
            },
            "profitability": {
                "npv_public": feasibility_ctx.financial_metrics.npv_public,
                "irr_public": feasibility_ctx.financial_metrics.irr_public,
                "grade": feasibility_ctx.profitability_grade
            }
        }
    
    def _build_technical_appendix(
        self,
        land_ctx: CanonicalLandContext,
        housing_type_ctx: HousingTypeContext,
        capacity_ctx: CapacityContextV2
    ) -> Dict:
        """기술 부록"""
        return {
            "title": "기술 부록 (Technical Appendix)",
            "site_information": {
                "address": land_ctx.address,
                "parcel_id": land_ctx.parcel_id,
                "area_sqm": land_ctx.area_sqm,
                "zone_type": land_ctx.zone_type,
                "legal_far": land_ctx.far,
                "legal_bcr": land_ctx.bcr,
                "road_width": land_ctx.road_width
            },
            "housing_type": {
                "selected_type": housing_type_ctx.selected_type,
                "selected_type_name": housing_type_ctx.selected_type_name,
                "confidence": housing_type_ctx.selection_confidence,
                "location_score": housing_type_ctx.location_score
            },
            "capacity_scenarios": {
                "legal": {
                    "far": capacity_ctx.legal_capacity.applied_far,
                    "bcr": capacity_ctx.legal_capacity.applied_bcr,
                    "gfa_sqm": capacity_ctx.legal_capacity.target_gfa_sqm,
                    "units": capacity_ctx.legal_capacity.total_units,
                    "parking": capacity_ctx.legal_capacity.required_parking_spaces
                },
                "incentive": {
                    "far": capacity_ctx.incentive_capacity.applied_far,
                    "bcr": capacity_ctx.incentive_capacity.applied_bcr,
                    "gfa_sqm": capacity_ctx.incentive_capacity.target_gfa_sqm,
                    "units": capacity_ctx.incentive_capacity.total_units,
                    "parking": capacity_ctx.incentive_capacity.required_parking_spaces
                }
            }
        }
    
    def _build_conclusion(self, m6_result: M6ComprehensiveResult) -> Dict:
        """결론"""
        return {
            "title": "결론 (Conclusion)",
            "final_judgement": m6_result.judgement.value,
            "total_score": f"{m6_result.lh_score_total:.1f}/100",
            "grade": m6_result.grade.value,
            "confidence_level": m6_result.confidence_level,
            "recommendation": self._get_recommendation(m6_result.judgement),
            "next_steps": self._get_next_steps(m6_result.judgement)
        }
    
    def _get_next_steps(self, judgement) -> List[str]:
        """다음 단계"""
        if judgement.value == "GO":
            return [
                "1. LH 제안서 작성 및 제출",
                "2. LH 실사 대응 준비",
                "3. 협상 전략 수립"
            ]
        elif judgement.value == "CONDITIONAL":
            return [
                "1. 개선 방안 이행",
                "2. 재평가 수행",
                "3. 개선 결과 확인 후 LH 제안"
            ]
        else:
            return [
                "1. 근본적 개선 방안 검토",
                "2. 대안 부지 탐색",
                "3. 사업 구조 재설계"
            ]


__all__ = ["ReportGeneratorV4"]
