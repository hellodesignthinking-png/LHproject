"""
Financial Engine Core Calculator
=================================

사업성 분석 핵심 계산 로직
3가지 모드 지원:
1. Cost Index Mode (공사비연동제)
2. General Construction Mode (민간 건축)
3. Developer Feasibility Mode (IRR/ROI)

Author: ZeroSite Development Team
Date: 2025-12-06
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
import numpy_financial as npf

from .config import get_financial_config, FinancialConfig
from .output_schema import (
    FinancialInput,
    FinancialResult,
    CAPEXBreakdown,
    OPEXBreakdown,
    RevenueBreakdown,
    FinancialMetrics,
    LHGapAnalysis,
    CalculationMode
)

logger = logging.getLogger(__name__)


class FinancialCalculator:
    """
    재무 계산 엔진
    
    모든 계산은 이 클래스에서 수행
    보고서 생성과 완전 분리
    """
    
    def __init__(self, config: Optional[FinancialConfig] = None):
        """Initialize calculator with configuration"""
        self.config = config or get_financial_config()
        logger.info("✅ FinancialCalculator initialized")
    
    def calculate_capex(
        self,
        input_data: FinancialInput
    ) -> CAPEXBreakdown:
        """
        총 투자비 (CAPEX) 계산
        
        Formula:
            CAPEX = 직접공사비 + 간접비 + 금융비용 + 토지비
        """
        logger.info(f"📊 Calculating CAPEX for {input_data.gross_floor_area:.0f}m²")
        
        # 1. 직접 공사비 계산
        direct_cost = self._calculate_direct_construction_cost(input_data)
        
        # 2. 간접비 계산
        indirect_cost = self._calculate_indirect_cost(direct_cost)
        
        # 3. 금융비용 계산
        finance_cost = self._calculate_finance_cost(
            direct_cost + indirect_cost,
            input_data.construction_period
        )
        
        # 4. 토지비
        land_cost = input_data.land_appraisal_price or 0
        
        # 5. 총 투자비
        total_capex = direct_cost + indirect_cost + finance_cost + land_cost
        
        # Get calculation details
        unit_price = self._get_construction_unit_price(input_data)
        regional_coef = self.config.construction.regional_coefficients.get(
            input_data.region, 1.0
        )
        cost_index = self._get_cost_index()
        
        logger.info(f"   ✅ Direct: ₩{direct_cost:,.0f}")
        logger.info(f"   ✅ Indirect: ₩{indirect_cost:,.0f}")
        logger.info(f"   ✅ Finance: ₩{finance_cost:,.0f}")
        logger.info(f"   ✅ Total CAPEX: ₩{total_capex:,.0f}")
        
        return CAPEXBreakdown(
            direct_construction=direct_cost,
            indirect_cost=indirect_cost,
            finance_cost=finance_cost,
            land_cost=land_cost,
            total_capex=total_capex,
            construction_unit_price=unit_price,
            regional_coefficient=regional_coef,
            cost_index=cost_index
        )
    
    def calculate_opex(
        self,
        input_data: FinancialInput
    ) -> OPEXBreakdown:
        """
        연간 운영비 (OPEX) 계산
        
        Formula:
            OPEX = 연면적 × 운영비 단가
        """
        logger.info("💰 Calculating OPEX")
        
        # 연간 총 운영비
        annual_opex_per_sqm = self.config.opex.annual_opex_per_sqm
        total_opex = input_data.gross_floor_area * annual_opex_per_sqm
        
        # 세부 구성
        breakdown = self.config.opex.breakdown
        maintenance = total_opex * breakdown["maintenance"]
        management = total_opex * breakdown["management"]
        utilities = total_opex * breakdown["utilities"]
        insurance = total_opex * breakdown["insurance"]
        other = total_opex * breakdown["other"]
        
        logger.info(f"   ✅ Annual OPEX: ₩{total_opex:,.0f}")
        
        return OPEXBreakdown(
            maintenance=maintenance,
            management=management,
            utilities=utilities,
            insurance=insurance,
            other=other,
            total_opex=total_opex
        )
    
    def calculate_revenue(
        self,
        input_data: FinancialInput
    ) -> RevenueBreakdown:
        """
        수익 구조 계산
        
        Formula:
            총수입 = 세대수 × 세대당 임대료 × 12개월 × 입주율
            NOI = 총수입 - OPEX
        """
        logger.info("💵 Calculating Revenue")
        
        # 세대당 평균 면적 (주거 연면적 / 세대수)
        avg_unit_area = input_data.residential_gfa / input_data.unit_count
        
        # 세대당 임대료 (월)
        rent_per_sqm = self.config.revenue.rent_per_sqm_per_month
        regional_factor = self.config.revenue.rent_regional_factors.get(
            input_data.region, 1.0
        )
        rent_per_unit = avg_unit_area * rent_per_sqm * regional_factor
        
        # 입주율
        occupancy_rate = self.config.revenue.occupancy_rate
        
        # 총 수입 (연간)
        gross_income = (
            input_data.unit_count *
            rent_per_unit *
            12 *
            occupancy_rate
        )
        
        # OPEX 계산
        opex = self.calculate_opex(input_data)
        
        # NOI
        noi = gross_income - opex.total_opex
        
        logger.info(f"   ✅ Rent/Unit: ₩{rent_per_unit:,.0f}/month")
        logger.info(f"   ✅ Gross Income: ₩{gross_income:,.0f}/year")
        logger.info(f"   ✅ NOI: ₩{noi:,.0f}/year")
        
        return RevenueBreakdown(
            rent_per_unit=rent_per_unit,
            total_units=input_data.unit_count,
            occupancy_rate=occupancy_rate,
            gross_income=gross_income,
            net_operating_income=noi
        )
    
    def calculate_metrics(
        self,
        capex: CAPEXBreakdown,
        revenue: RevenueBreakdown
    ) -> FinancialMetrics:
        """
        재무 지표 계산
        
        - ROI: Return on Investment
        - IRR: Internal Rate of Return (10년)
        - Cap Rate: Capitalization Rate
        - Payback Period: 투자회수기간
        """
        logger.info("📈 Calculating Financial Metrics")
        
        noi = revenue.net_operating_income
        total_investment = capex.total_capex
        
        # ROI
        roi = noi / total_investment if total_investment > 0 else 0
        
        # Cap Rate
        cap_rate = noi / (total_investment - capex.land_cost) if (total_investment - capex.land_cost) > 0 else 0
        
        # IRR (10년 기준)
        irr_10yr = self._calculate_irr(
            initial_investment=-total_investment,
            annual_cashflow=noi,
            years=10,
            terminal_value=total_investment * 0.7  # 10년 후 자산가치 70% 가정
        )
        
        # Payback Period
        payback_period = total_investment / noi if noi > 0 else 999
        
        logger.info(f"   ✅ ROI: {roi:.1%}")
        logger.info(f"   ✅ IRR (10yr): {irr_10yr:.1%}")
        logger.info(f"   ✅ Cap Rate: {cap_rate:.1%}")
        logger.info(f"   ✅ Payback: {payback_period:.1f} years")
        
        return FinancialMetrics(
            roi=roi,
            irr_10yr=irr_10yr,
            cap_rate=cap_rate,
            payback_period=payback_period,
            debt_service_coverage=None  # TODO: Implement if needed
        )
    
    def calculate_lh_gap(
        self,
        input_data: FinancialInput,
        capex: CAPEXBreakdown
    ) -> LHGapAnalysis:
        """
        LH 매입가 갭 분석
        
        Formula:
            LH 매입가 = 공급면적 × LH 단가 × 지역계수
            갭 = LH 매입가 - 총사업비
        """
        logger.info("🎯 Calculating LH Gap Analysis")
        
        # LH 매입가 계산
        lh_base_price = self.config.lh_price.lh_base_price_per_sqm
        regional_factor = self.config.lh_price.lh_regional_factors.get(
            input_data.region, 1.0
        )
        
        # 공급면적 = 주거연면적 (전용면적 기준)
        supply_area = input_data.residential_gfa
        
        # LH 예상 매입가
        estimated_lh_price = supply_area * lh_base_price * regional_factor
        
        # 총 사업비
        total_project_cost = capex.total_capex
        
        # 갭 분석
        gap_amount = estimated_lh_price - total_project_cost
        gap_ratio = (gap_amount / total_project_cost * 100) if total_project_cost > 0 else 0
        is_profitable = gap_amount > 0
        
        logger.info(f"   ✅ LH Price: ₩{estimated_lh_price:,.0f}")
        logger.info(f"   ✅ Project Cost: ₩{total_project_cost:,.0f}")
        logger.info(f"   ✅ Gap: ₩{gap_amount:,.0f} ({gap_ratio:.1f}%)")
        logger.info(f"   ✅ Profitable: {is_profitable}")
        
        return LHGapAnalysis(
            estimated_lh_price=estimated_lh_price,
            total_project_cost=total_project_cost,
            gap_amount=gap_amount,
            gap_ratio=gap_ratio,
            is_profitable=is_profitable,
            lh_base_price=lh_base_price,
            lh_regional_factor=regional_factor,
            lh_calculation_method="공급면적 × 기준단가 × 지역계수"
        )
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _calculate_direct_construction_cost(
        self,
        input_data: FinancialInput
    ) -> float:
        """직접 공사비 계산"""
        # 기본 단가
        unit_price = self._get_construction_unit_price(input_data)
        
        # 연면적 기준 공사비
        building_cost = input_data.gross_floor_area * unit_price
        
        # 주차장 공사비 (지하 가정)
        parking_cost = (
            input_data.parking_count *
            self.config.construction.parking_costs["basement"]
        )
        
        # 총 직접 공사비
        total_direct = building_cost + parking_cost
        
        return total_direct
    
    def _get_construction_unit_price(
        self,
        input_data: FinancialInput
    ) -> float:
        """공사비 단가 계산 (지역계수 + 연동지수 + 용도지역 가산)"""
        base_price = self.config.construction.base_unit_price
        regional_coef = self.config.construction.regional_coefficients.get(
            input_data.region, 1.0
        )
        cost_index = self._get_cost_index()
        zone_premium = self.config.construction.zone_premiums.get(
            input_data.zone_type, 0.0
        )
        
        unit_price = base_price * regional_coef * cost_index * (1 + zone_premium)
        
        return unit_price
    
    def _get_cost_index(self) -> float:
        """현재 연도의 공사비 연동지수"""
        current_year = str(datetime.now().year)
        return self.config.construction.cost_indices.get(current_year, 1.0)
    
    def _calculate_indirect_cost(self, direct_cost: float) -> float:
        """간접비 계산"""
        indirect_rate = self.config.indirect.indirect_rate
        return direct_cost * indirect_rate
    
    def _calculate_finance_cost(
        self,
        construction_cost: float,
        construction_period: int
    ) -> float:
        """
        금융비용 계산
        
        Formula:
            금융비용 = (직접공사비 + 간접비) × 대출비율 × 금리 × (공사기간/12)
        """
        interest_rate = self.config.finance.interest_rate
        ltc = self.config.finance.loan_to_cost_ratio
        
        # 연간 이자 → 공사기간 비례
        finance_cost = (
            construction_cost *
            ltc *
            interest_rate *
            (construction_period / 12.0)
        )
        
        return finance_cost
    
    def _calculate_irr(
        self,
        initial_investment: float,
        annual_cashflow: float,
        years: int,
        terminal_value: float
    ) -> float:
        """
        IRR 계산 (10년)
        
        Uses numpy_financial.irr()
        """
        try:
            # Cashflow: [초기투자, 연간NOI×9, 마지막년(NOI+자산가치)]
            cashflows = [initial_investment]
            for i in range(years - 1):
                cashflows.append(annual_cashflow)
            cashflows.append(annual_cashflow + terminal_value)
            
            irr = npf.irr(cashflows)
            
            # NaN 체크
            if np.isnan(irr):
                return 0.0
            
            return irr
        except Exception as e:
            logger.warning(f"IRR calculation error: {e}")
            return 0.0


class FinancialEngine:
    """
    사업성 분석 엔진 (Facade)
    
    Usage:
        engine = FinancialEngine()
        result = engine.analyze(input_data)
    """
    
    def __init__(self, config: Optional[FinancialConfig] = None):
        """Initialize engine"""
        self.config = config or get_financial_config()
        self.calculator = FinancialCalculator(self.config)
        logger.info("🚀 FinancialEngine initialized")
    
    def analyze(
        self,
        input_data: FinancialInput
    ) -> FinancialResult:
        """
        완전한 사업성 분석 실행
        
        Returns:
            FinancialResult: JSON 형식 결과
        """
        start_time = datetime.now()
        
        logger.info("="*80)
        logger.info(f"🏗️ Financial Analysis Started")
        logger.info(f"   Mode: {input_data.calculation_mode}")
        logger.info(f"   Land: {input_data.land_area:.0f}m²")
        logger.info(f"   GFA: {input_data.gross_floor_area:.0f}m²")
        logger.info(f"   Units: {input_data.unit_count}")
        logger.info("="*80)
        
        # 1. CAPEX
        capex = self.calculator.calculate_capex(input_data)
        
        # 2. OPEX
        opex = self.calculator.calculate_opex(input_data)
        
        # 3. Revenue
        revenue = self.calculator.calculate_revenue(input_data)
        
        # 4. Financial Metrics
        metrics = self.calculator.calculate_metrics(capex, revenue)
        
        # 5. LH Gap Analysis
        lh_gap = self.calculator.calculate_lh_gap(input_data, capex)
        
        # 6. Feasibility Assessment
        is_feasible, risk_level, recommendation = self._assess_feasibility(
            metrics, lh_gap
        )
        
        # Create result
        result = FinancialResult(
            calculation_mode=input_data.calculation_mode,
            calculation_timestamp=datetime.now().isoformat(),
            input_data=input_data,
            capex=capex,
            opex=opex,
            revenue=revenue,
            metrics=metrics,
            lh_gap=lh_gap,
            is_feasible=is_feasible,
            risk_level=risk_level,
            recommendation=recommendation,
            assumptions={
                "construction_period": input_data.construction_period,
                "occupancy_rate": self.config.revenue.occupancy_rate,
                "interest_rate": self.config.finance.interest_rate,
                "cost_index": self.calculator._get_cost_index()
            }
        )
        
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        logger.info("\n" + "="*80)
        logger.info(f"✅ Financial Analysis Complete ({duration_ms}ms)")
        logger.info(f"   Recommendation: {recommendation}")
        logger.info(f"   ROI: {metrics.roi:.1%}")
        logger.info(f"   IRR: {metrics.irr_10yr:.1%}")
        logger.info(f"   LH Gap: ₩{lh_gap.gap_amount:,.0f}")
        logger.info("="*80)
        
        return result
    
    def _assess_feasibility(
        self,
        metrics: FinancialMetrics,
        lh_gap: LHGapAnalysis
    ) -> tuple[bool, str, str]:
        """
        사업 타당성 평가
        
        Returns:
            (is_feasible, risk_level, recommendation)
        """
        # Feasibility check
        is_feasible = True
        risk_level = "LOW"
        recommendation = "GO"
        
        # Check ROI
        if metrics.roi < 0.03:  # ROI < 3%
            is_feasible = False
            risk_level = "HIGH"
            recommendation = "NO-GO"
        elif metrics.roi < 0.05:  # ROI < 5%
            risk_level = "MEDIUM"
            recommendation = "REVIEW"
        
        # Check IRR
        if metrics.irr_10yr < 0.05:  # IRR < 5%
            risk_level = "MEDIUM" if risk_level == "LOW" else "HIGH"
            if recommendation == "GO":
                recommendation = "REVIEW"
        
        # Check LH Gap
        if not lh_gap.is_profitable:
            risk_level = "HIGH"
            recommendation = "REVIEW" if recommendation != "NO-GO" else "NO-GO"
        
        # Check Payback Period
        if metrics.payback_period > 15:  # > 15 years
            risk_level = "MEDIUM" if risk_level == "LOW" else "HIGH"
        
        return is_feasible, risk_level, recommendation


# Helper function
def analyze_financial_feasibility(
    land_area: float,
    gross_floor_area: float,
    residential_gfa: float,
    unit_count: int,
    parking_count: int,
    zone_type: str,
    **kwargs
) -> FinancialResult:
    """
    Convenience function for quick analysis
    
    Usage:
        result = analyze_financial_feasibility(
            land_area=850,
            gross_floor_area=2125,
            residential_gfa=1806,
            unit_count=30,
            parking_count=30,
            zone_type="제2종일반주거지역"
        )
    """
    input_data = FinancialInput(
        land_area=land_area,
        gross_floor_area=gross_floor_area,
        residential_gfa=residential_gfa,
        unit_count=unit_count,
        parking_count=parking_count,
        zone_type=zone_type,
        **kwargs
    )
    
    engine = FinancialEngine()
    return engine.analyze(input_data)


# Fix numpy import
import numpy as np
