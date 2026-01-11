"""
M5 Feasibility Service
======================

사업성 검토 서비스

이 서비스는 M2 감정평가와 M4 건축규모를 기반으로
사업성(NPV, IRR, ROI)을 검토합니다.

⚠️ 중요: M2 AppraisalContext는 READ-ONLY로만 사용
land_value 재계산 절대 금지!

계산 요소:
- LH 매입가 (감정가 기준)
- 공사비 (연동제)
- NPV, IRR, ROI
- Cash Flow 분석

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

import logging
from datetime import datetime

from typing import Union

from app.core.context.appraisal_context import AppraisalContext
from app.core.context.capacity_context import CapacityContext  # V1 (legacy)
from app.core.context.capacity_context_v2 import CapacityContextV2  # V2 (new)
from app.core.context.feasibility_context import (
    FeasibilityContext,
    CostBreakdown,
    RevenueProjection,
    FinancialMetrics
)

logger = logging.getLogger(__name__)


class FeasibilityService:
    """
    사업성 검토 서비스 (M5)
    
    입력: AppraisalContext (M2, 🔒 READ-ONLY), CapacityContext (M4)
    출력: FeasibilityContext (사업성 결과)
    
    ⚠️ AppraisalContext의 land_value는 절대 재계산하지 않습니다!
    """
    
    def __init__(self):
        """서비스 초기화"""
        logger.info("✅ M5 Feasibility Service initialized")
        logger.info("   ⚠️ AppraisalContext is READ-ONLY!")
    
    def run(
        self,
        appraisal_ctx: AppraisalContext,
        capacity_ctx: Union[CapacityContext, CapacityContextV2]
    ) -> FeasibilityContext:
        """
        사업성 검토 실행
        
        Args:
            appraisal_ctx: M2 감정평가 결과 (🔒 READ-ONLY)
            capacity_ctx: M4 건축규모 (V1 or V2)
        
        Returns:
            FeasibilityContext (frozen=True)
        
        ⚠️ appraisal_ctx.land_value는 참조만 하고 수정하지 않습니다!
        """
        
        # Detect V1 or V2 and extract units
        if isinstance(capacity_ctx, CapacityContextV2):
            recommended_units = capacity_ctx.incentive_capacity.total_units
            total_gfa_sqm = capacity_ctx.incentive_capacity.target_gfa_sqm
            logger.info("="*80)
            logger.info("📊 M5 FEASIBILITY MODULE - Analyzing Project Feasibility")
            logger.info(f"   Land Value (🔒): ₩{appraisal_ctx.land_value:,.0f}")
            logger.info(f"   Capacity V2: Incentive {recommended_units}세대 / {total_gfa_sqm:,.0f}㎡")
            logger.info("="*80)
        else:
            # Support both V1 (unit_plan) and V2 (unit_summary) capacity context
            if hasattr(capacity_ctx, 'unit_summary'):
                recommended_units = capacity_ctx.unit_summary.total_units
                total_gfa_sqm = capacity_ctx.legal_capacity.gfa_breakdown.total_gfa_sqm
            else:
                recommended_units = capacity_ctx.unit_plan.recommended_units
                total_gfa_sqm = capacity_ctx.building_specs.total_gfa_sqm
            logger.info("="*80)
            logger.info("📊 M5 FEASIBILITY MODULE - Analyzing Project Feasibility")
            logger.info(f"   Land Value (🔒): ₩{appraisal_ctx.land_value:,.0f}")
            logger.info(f"   Recommended Units: {recommended_units}")
            logger.info("="*80)
        
        # TODO: 실제 로직 구현
        # Step 1: LH 매입가 = 감정가 기준 (appraisal_ctx.land_value 사용)
        # Step 2: 공사비 = LH 연동제 기준
        # Step 3: 총사업비 = 토지비 + 공사비 + 부대비용
        # Step 4: 수익 = LH 매입가 × 세대수
        # Step 5: NPV, IRR 계산
        
        # Mock 데이터
        feasibility_ctx = self._create_mock_context(appraisal_ctx, capacity_ctx)
        
        logger.info(f"✅ Feasibility Analyzed")
        logger.info(f"   NPV (Public): ₩{feasibility_ctx.financial_metrics.npv_public:,.0f}")
        logger.info(f"   IRR (Public): {feasibility_ctx.financial_metrics.irr_public:.1f}%")
        logger.info(f"   Profitability Grade: {feasibility_ctx.profitability_grade}")
        logger.info("="*80)
        
        return feasibility_ctx
    
    def _create_mock_context(
        self,
        appraisal_ctx: AppraisalContext,
        capacity_ctx: Union[CapacityContext, CapacityContextV2]
    ) -> FeasibilityContext:
        """Mock 사업성 계산 (테스트용)"""
        # TODO: 실제 로직으로 교체
        
        # 🔒 감정가 참조 (READ-ONLY!)
        land_cost = appraisal_ctx.land_value
        unit_price = appraisal_ctx.unit_price_sqm
        
        # Extract values from V1 or V2
        if isinstance(capacity_ctx, CapacityContextV2):
            total_gfa_sqm = capacity_ctx.incentive_capacity.target_gfa_sqm
            recommended_units = capacity_ctx.incentive_capacity.total_units
        else:
            # Support both V1 (unit_plan) and V2 (unit_summary) capacity context
            if hasattr(capacity_ctx, 'unit_summary'):
                total_gfa_sqm = capacity_ctx.legal_capacity.gfa_breakdown.total_gfa_sqm
                recommended_units = capacity_ctx.unit_summary.total_units
            else:
                total_gfa_sqm = capacity_ctx.building_specs.total_gfa_sqm
                recommended_units = capacity_ctx.unit_plan.recommended_units
        
        # 공사비 (㎡당 300만원)
        construction_cost = total_gfa_sqm * 3_000_000
        design_cost = construction_cost * 0.03
        indirect_cost = construction_cost * 0.05
        financing_cost = land_cost * 0.05
        contingency = (land_cost + construction_cost) * 0.05
        
        total_cost = (land_cost + construction_cost + design_cost + 
                      indirect_cost + financing_cost + contingency)
        
        # Cost Breakdown
        cost_breakdown = CostBreakdown(
            land_acquisition_cost=land_cost,
            construction_cost=construction_cost,
            design_cost=design_cost,
            indirect_cost=indirect_cost,
            financing_cost=financing_cost,
            contingency=contingency,
            total_cost=total_cost
        )
        
        # LH 매입가 (감정가 기준 110%)
        lh_purchase_price = land_cost * 1.1
        lh_unit_price = unit_price * 1.1
        purchase_premium_rate = 10.0  # 10%
        
        # 수익
        private_sale = 0.0  # LH 전량 매입
        rental_income = recommended_units * 1_000_000 * 12  # 월 100만원
        total_revenue = lh_purchase_price + (recommended_units * 200_000_000)
        
        revenue_projection = RevenueProjection(
            lh_purchase_price=lh_purchase_price,
            private_sale_revenue=private_sale,
            rental_income_annual=rental_income,
            total_revenue=total_revenue
        )
        
        # NPV & IRR
        npv_public = total_revenue - total_cost  # 공공 할인율 2%
        npv_market = (total_revenue * 0.95) - total_cost  # 시장 할인율 5.5%
        irr_public = (npv_public / total_cost) * 100 if total_cost > 0 else 0
        irr_market = (npv_market / total_cost) * 100 if total_cost > 0 else 0
        roi = (npv_public / total_cost) * 100 if total_cost > 0 else 0
        payback_years = (total_cost / (rental_income + (npv_public/10))) if (rental_income > 0) else 10
        profitability_index = (total_revenue / total_cost) if total_cost > 0 else 0
        
        financial_metrics = FinancialMetrics(
            npv_public=npv_public,
            npv_market=npv_market,
            irr_public=irr_public,
            irr_market=irr_market,
            roi=roi,
            payback_years=min(payback_years, 10.0),
            profitability_index=profitability_index
        )
        
        # 사업성 판단
        is_profitable = npv_public > 0
        
        if roi >= 20:
            profitability_grade = "A"
        elif roi >= 15:
            profitability_grade = "B"
        elif roi >= 10:
            profitability_grade = "C"
        elif roi >= 5:
            profitability_grade = "D"
        else:
            profitability_grade = "F"
        
        # 사업성 점수 (40점 만점)
        if roi >= 20:
            profitability_score = 40.0
        elif roi >= 15:
            profitability_score = 35.0
        elif roi >= 10:
            profitability_score = 30.0
        elif roi >= 5:
            profitability_score = 20.0
        else:
            profitability_score = 10.0
        
        return FeasibilityContext(
            appraised_value=land_cost,
            appraised_unit_price=unit_price,
            lh_purchase_price=lh_purchase_price,
            lh_unit_price=lh_unit_price,
            purchase_premium_rate=purchase_premium_rate,
            cost_breakdown=cost_breakdown,
            revenue_projection=revenue_projection,
            financial_metrics=financial_metrics,
            is_profitable=is_profitable,
            profitability_grade=profitability_grade,
            profitability_score=profitability_score,
            financial_risks=["LH 매입가 변동 리스크", "공사비 상승 리스크"] if is_profitable else ["수익성 부족"],
            risk_mitigation=["공사비 연동제 적용", "단계별 LH 협의"] if is_profitable else ["입지 개선 필요"],
            best_case_npv=npv_public * 1.2,
            worst_case_npv=npv_public * 0.8,
            analysis_date=datetime.now().strftime("%Y-%m-%d"),
            construction_cost_base_year=datetime.now().year,  # ✅ Base Year
            assumptions={
                "감정가 참조": "M2.AppraisalContext (READ-ONLY)",
                "공사비 단가": "3,000,000원/㎡",
                "LH 매입 프리미엄": "10%",
                "할인율_공공": "2%",
                "할인율_시장": "5.5%"
            }
        )


__all__ = ["FeasibilityService"]
