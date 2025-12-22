"""
LH Analysis Engine - Canonical Flow Version
Uses AppraisalContextLock as Single Source of Truth

This engine:
1. Accepts locked appraisal context (NO recalculation of land value)
2. Calculates LH-specific metrics (construction cost, LH purchase price)
3. Performs ROI analysis and decision making
4. Returns judgment results (not appraisal facts)

Version: v8.7+
Date: 2025-12-15
"""

from typing import Dict, Any, Optional
from app.services.appraisal_context import AppraisalContextLock


class LHAnalysisCanonical:
    """
    LH사업성 분석 엔진 (Canonical Flow)
    
    핵심 원칙:
    - 토지 가액은 감정평가 컨텍스트에서만 가져옴 (재계산 금지)
    - LH 관련 건축비, 매입가, 사업비만 계산
    - ROI 기반 의사결정 수행
    
    Usage:
        lh_engine = LHAnalysisCanonical()
        
        # appraisal_ctx is already locked
        result = lh_engine.analyze(
            appraisal_ctx=appraisal_ctx,
            expected_units=56,
            total_floor_area=2464.0,
            unit_type='신혼부부 I'
        )
    """
    
    # Metro regions for LH_LINKED mode
    METRO_REGIONS = ['서울특별시', '서울시', '경기도', '인천광역시', '인천시']
    
    # Unit threshold for LH_LINKED mode
    THRESHOLD_UNITS = 50
    
    # LH standard construction cost (2025)
    LH_STANDARD_UNIT_COST = 2800000  # 2.8M KRW/㎡
    
    def __init__(self):
        """Initialize LH analysis engine"""
        pass
    
    def analyze(
        self,
        appraisal_ctx: AppraisalContextLock,
        expected_units: int,
        total_floor_area: float,
        unit_type: str = '신혼부부 I',
        address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        LH 사업성 분석 수행
        
        Args:
            appraisal_ctx: 잠긴 감정평가 컨텍스트 (READ-ONLY)
            expected_units: 예상 세대수
            total_floor_area: 총 연면적 (㎡)
            unit_type: 주택 유형
            address: 주소 (분석 모드 결정용)
        
        Returns:
            LH 분석 결과 딕셔너리
        """
        
        # 1. Extract land appraised value from context (NO recalculation!)
        land_appraised_value = appraisal_ctx.get('calculation.final_appraised_total')
        land_area = appraisal_ctx.get('calculation.land_area_sqm')
        
        print(f"\n🏛️  LH Analysis (Canonical Flow)")
        print(f"   📊 Using locked appraisal data:")
        print(f"      Land appraised value: {land_appraised_value:,.0f}원")
        print(f"      Land area: {land_area:.0f}㎡")
        
        # 2. Determine analysis mode
        analysis_mode = self._determine_mode(expected_units, address)
        print(f"   🔍 Analysis mode: {analysis_mode}")
        
        # 3. Calculate based on mode
        if analysis_mode == 'LH_LINKED':
            result = self._calculate_lh_linked(
                land_appraised_value=land_appraised_value,
                total_floor_area=total_floor_area,
                expected_units=expected_units
            )
        else:
            result = self._calculate_standard(
                land_appraised_value=land_appraised_value,
                expected_units=expected_units
            )
        
        # 4. Add metadata
        result['analysis_mode'] = analysis_mode
        result['unit_type'] = unit_type
        result['based_on_appraisal'] = True
        result['appraisal_reference'] = {
            'land_appraised_value': land_appraised_value,
            'land_area': land_area,
            'appraisal_version': appraisal_ctx.get('metadata.appraisal_engine'),
            'appraisal_confidence': appraisal_ctx.get('confidence.score')
        }
        
        return result
    
    def _determine_mode(self, units: int, address: Optional[str]) -> str:
        """
        Determine analysis mode (LH_LINKED or STANDARD)
        
        LH_LINKED: 50+ units AND in metro region
        STANDARD: Otherwise
        """
        if units < self.THRESHOLD_UNITS:
            return 'STANDARD'
        
        if address:
            for region in self.METRO_REGIONS:
                if region in address:
                    return 'LH_LINKED'
        
        return 'STANDARD'
    
    def _calculate_lh_linked(
        self,
        land_appraised_value: float,
        total_floor_area: float,
        expected_units: int
    ) -> Dict[str, Any]:
        """
        Calculate LH-linked model (공사비 연동제)
        
        Formula:
        - Verified Cost = total_floor_area * LH_STANDARD_UNIT_COST * (1 + indirect_costs)
        - LH Purchase = land_appraised_value + Verified Cost
        - Total Cost = land_appraised_value + Verified Cost + financing + ancillary
        - ROI = (LH Purchase - Total Cost) / Total Cost * 100
        """
        
        print(f"   💰 LH-Linked Model (공사비 연동제)")
        
        # 1. Verified Construction Cost
        base_construction_cost = total_floor_area * self.LH_STANDARD_UNIT_COST
        
        # Indirect costs
        indirect_cost_rate = 0.18  # 간접비 18%
        admin_fee_rate = 0.03  # 일반관리비 3%
        profit_rate = 0.05  # 이윤 5%
        design_supervision_rate = 0.037  # 설계·감리 3.7%
        contingency_rate = 0.02  # 예비비 2%
        
        total_indirect_rate = (
            indirect_cost_rate +
            admin_fee_rate +
            profit_rate +
            design_supervision_rate +
            contingency_rate
        )  # Total: 30.7%
        
        verified_cost = base_construction_cost * (1 + total_indirect_rate)
        
        print(f"      Base construction: {base_construction_cost:,.0f}원")
        print(f"      Indirect costs ({total_indirect_rate*100:.1f}%): {verified_cost - base_construction_cost:,.0f}원")
        print(f"      Verified Cost: {verified_cost:,.0f}원")
        
        # 2. LH Purchase Price
        lh_purchase_price = land_appraised_value + verified_cost
        
        print(f"      Land (appraisal): {land_appraised_value:,.0f}원")
        print(f"      LH Purchase Price: {lh_purchase_price:,.0f}원")
        
        # 3. Total Project Cost
        financing_cost_rate = 0.032  # 금융비용 3.2%
        ancillary_cost_rate = 0.015  # 부대비용 1.5%
        
        financing_cost = (land_appraised_value + verified_cost) * financing_cost_rate
        ancillary_cost = (land_appraised_value + verified_cost) * ancillary_cost_rate
        
        total_project_cost = (
            land_appraised_value +
            verified_cost +
            financing_cost +
            ancillary_cost
        )
        
        print(f"      Financing cost ({financing_cost_rate*100:.1f}%): {financing_cost:,.0f}원")
        print(f"      Ancillary cost ({ancillary_cost_rate*100:.1f}%): {ancillary_cost:,.0f}원")
        print(f"      Total Project Cost: {total_project_cost:,.0f}원")
        
        # 4. Project Profit & ROI
        project_profit = lh_purchase_price - total_project_cost
        roi = (project_profit / total_project_cost) * 100
        
        print(f"      Project Profit: {project_profit:,.0f}원")
        print(f"      ROI: {roi:.2f}%")
        
        # 5. Rating & Decision
        rating = self._calculate_rating(roi)
        decision = self._make_decision(roi, expected_units)
        
        print(f"      Rating: {rating}")
        print(f"      Decision: {decision}")
        
        return {
            'land_appraisal': land_appraised_value,
            'verified_cost': verified_cost,
            'lh_purchase_price': lh_purchase_price,
            'financing_cost': financing_cost,
            'ancillary_cost': ancillary_cost,
            'total_project_cost': total_project_cost,
            'project_profit': project_profit,
            'roi': roi,
            'rating': rating,
            'decision': decision,
            'expected_units': expected_units,
            'lh_purchase_per_unit': lh_purchase_price / expected_units if expected_units > 0 else 0,
            'cost_breakdown': {
                'land': land_appraised_value,
                'verified_construction': verified_cost,
                'financing': financing_cost,
                'ancillary': ancillary_cost,
                'total': total_project_cost
            }
        }
    
    def _calculate_standard(
        self,
        land_appraised_value: float,
        expected_units: int
    ) -> Dict[str, Any]:
        """
        Calculate standard model (비연동제)
        
        Simplified calculation for small projects or non-metro areas
        """
        
        print(f"   💰 Standard Model (비연동제)")
        
        # Estimated construction cost per unit
        construction_cost_per_unit = 150000000  # 1.5억원/세대
        total_construction_cost = construction_cost_per_unit * expected_units
        
        # Total project cost (land + construction + fees)
        total_project_cost = (
            land_appraised_value +
            total_construction_cost +
            (land_appraised_value + total_construction_cost) * 0.05  # 5% fees
        )
        
        # Estimated revenue (assume 3억/세대)
        estimated_revenue_per_unit = 300000000  # 3억원/세대
        total_revenue = estimated_revenue_per_unit * expected_units
        
        # ROI
        project_profit = total_revenue - total_project_cost
        roi = (project_profit / total_project_cost) * 100
        
        print(f"      Land (appraisal): {land_appraised_value:,.0f}원")
        print(f"      Construction: {total_construction_cost:,.0f}원")
        print(f"      Total Cost: {total_project_cost:,.0f}원")
        print(f"      Estimated Revenue: {total_revenue:,.0f}원")
        print(f"      ROI: {roi:.2f}%")
        
        rating = self._calculate_rating(roi)
        decision = self._make_decision(roi, expected_units)
        
        return {
            'land_appraisal': land_appraised_value,
            'construction_cost': total_construction_cost,
            'total_project_cost': total_project_cost,
            'estimated_revenue': total_revenue,
            'project_profit': project_profit,
            'roi': roi,
            'rating': rating,
            'decision': decision,
            'expected_units': expected_units
        }
    
    def _calculate_rating(self, roi: float) -> str:
        """Calculate project rating based on ROI"""
        if roi >= 8.0:
            return 'A'
        elif roi >= 5.0:
            return 'B'
        elif roi >= 3.0:
            return 'C'
        else:
            return 'D'
    
    def _make_decision(self, roi: float, units: int) -> str:
        """Make final project decision"""
        if roi >= 8.0 and units >= 50:
            return 'GO'
        elif roi >= 5.0 and units >= 50:
            return 'CONDITIONAL'
        else:
            return 'NO-GO'


def create_lh_analysis_engine() -> LHAnalysisCanonical:
    """
    Factory function to create LH analysis engine
    
    Returns:
        LHAnalysisCanonical instance
    """
    return LHAnalysisCanonical()


__all__ = [
    'LHAnalysisCanonical',
    'create_lh_analysis_engine'
]
