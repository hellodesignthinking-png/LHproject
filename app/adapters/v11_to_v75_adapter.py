"""
v11.0 AI Engine Results → v7.5 Report Format Adapter
====================================================
Converts v11.0 AI analysis data to v7.5 report generator format

Purpose: Use v7.5's beautiful design with v11.0's latest AI intelligence
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class V11ToV75Adapter:
    """
    Converts v11.0 AI engine results to v7.5 report format
    
    v11.0 Structure:
    - LH Score: 100-point system (0-100)
    - Decision: GO/REVIEW/NO-GO
    - Unit Types: youth, newlywed, senior, general, vulnerable
    - Comprehensive analysis data
    
    v7.5 Structure:
    - LH Score: 110-point system (0-110)
    - Decision: GO/CONDITIONAL/REVISE/NO-GO
    - Unit Types: 청년, 신혼부부 I, 고령자, 일반, 취약계층
    - financial_result, lh_scores, visualizations
    """
    
    def __init__(self):
        logger.info("🔄 v11.0 → v7.5 Adapter initialized")
    
    def convert_v11_to_v75(
        self,
        address: str,
        land_area: float,
        land_appraisal_price: float,
        zone_type: str,
        v11_analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main conversion method
        
        Args:
            address: Land address
            land_area: Land area in m²
            land_appraisal_price: Total land appraisal price (not per m²)
            zone_type: Zone type (e.g., '제2종일반주거지역')
            v11_analysis_result: v11.0 AI engine analysis result
            
        Returns:
            v7.5 format data dictionary ready for LHReportGeneratorV75Final
        """
        logger.info("🔄 Converting v11.0 data to v7.5 format...")
        
        # Extract v11.0 data
        v11_data = v11_analysis_result.get('v11_data', {})
        
        # Extract v11.0 components
        lh_score_v11 = v11_data.get('lh_score', {})
        decision_v11 = v11_data.get('decision', {})
        unit_analysis_v11 = v11_data.get('unit_analysis', {})
        pseudo_data_v11 = v11_data.get('pseudo_data', {})
        feasibility_v11 = v11_data.get('feasibility', {})
        
        # Basic project info
        basic_info = {
            'address': address,
            'land_area': land_area,
            'unit_type': self._convert_unit_type(unit_analysis_v11.get('recommended_type', 'newlywed')),
            'construction_type': 'standard',
            'land_appraisal_price': land_appraisal_price
        }
        
        # Convert LH Score (100-point → 110-point)
        total_score_v11 = lh_score_v11.get('total_score', 0)
        total_score_v75 = self._convert_lh_score(total_score_v11)
        grade_v75 = self._calculate_grade_v75(total_score_v75)
        
        # Convert Decision
        decision_v75 = self._convert_decision(decision_v11.get('decision', 'REVIEW'))
        
        # Build financial_result for v7.5
        financial_result = self._build_financial_result(
            pseudo_data_v11,
            unit_analysis_v11,
            feasibility_v11,
            land_area,
            land_appraisal_price
        )
        
        # Build lh_scores for v7.5
        lh_scores = self._build_lh_scores(lh_score_v11, total_score_v75, grade_v75)
        
        # Build visualizations (optional, can be empty)
        visualizations = {}
        
        # Assemble v7.5 format data
        v75_data = {
            'financial_result': financial_result,
            'lh_scores': lh_scores,
            'visualizations': visualizations,
            'analysis_mode': 'v11.0_AI_ENGINE',
            'basic_info': basic_info,
            'recommendation': decision_v75,
            'v11_source': v11_data  # Keep original v11.0 data for reference
        }
        
        logger.info(f"✅ Conversion complete:")
        logger.info(f"   LH Score: {total_score_v11}/100 → {total_score_v75}/110 (Grade: {grade_v75})")
        logger.info(f"   Decision: {decision_v11.get('decision')} → {decision_v75}")
        logger.info(f"   Unit Type: {unit_analysis_v11.get('recommended_type')} → {basic_info['unit_type']}")
        
        return v75_data
    
    def _convert_lh_score(self, score_100: float) -> float:
        """
        Convert 100-point score to 110-point score
        100-point: 0-100
        110-point: 0-110
        
        Mapping: score_110 = score_100 * 1.1
        """
        return round(score_100 * 1.1, 1)
    
    def _calculate_grade_v75(self, score_110: float) -> str:
        """
        Calculate v7.5 grade from 110-point score
        
        v7.5 Grading:
        - A: 99+ (90%)
        - B: 88-98 (80%)
        - C: 77-87 (70%)
        - D: 66-76 (60%)
        - F: <66 (<60%)
        """
        if score_110 >= 99:
            return 'A'
        elif score_110 >= 88:
            return 'B'
        elif score_110 >= 77:
            return 'C'
        elif score_110 >= 66:
            return 'D'
        else:
            return 'F'
    
    def _convert_decision(self, decision_v11: str) -> str:
        """
        Convert v11.0 decision to v7.5 decision
        
        v11.0: GO, REVIEW, NO-GO (NO_GO)
        v7.5: GO, CONDITIONAL, REVISE, NO-GO
        
        Mapping:
        - GO → GO
        - REVIEW → CONDITIONAL (or REVISE based on score)
        - NO-GO/NO_GO → NO-GO
        """
        decision_upper = decision_v11.upper().replace('-', '_')
        
        if decision_upper == 'GO' or decision_upper == 'PROCEED':
            return 'GO'
        elif decision_upper == 'REVIEW':
            return 'CONDITIONAL'  # v7.5 equivalent
        elif decision_upper in ['NO_GO', 'NOGO', 'REJECT']:
            return 'NO-GO'
        else:
            return 'REVISE'  # Default fallback
    
    def _convert_unit_type(self, unit_type_v11: str) -> str:
        """
        Convert v11.0 unit type to v7.5 unit type
        
        v11.0: youth, newlywed, senior, general, vulnerable
        v7.5: 청년, 신혼부부 I, 고령자, 일반, 취약계층
        """
        unit_mapping = {
            'youth': '청년',
            'newlywed': '신혼부부 I',
            'senior': '고령자',
            'general': '일반',
            'vulnerable': '취약계층'
        }
        return unit_mapping.get(unit_type_v11, '신혼부부 I')  # Default to newlywed
    
    def _build_financial_result(
        self,
        pseudo_data: Dict[str, Any],
        unit_analysis: Dict[str, Any],
        feasibility: Dict[str, Any],
        land_area: float,
        land_appraisal_price: float
    ) -> Dict[str, Any]:
        """
        Build financial_result structure for v7.5
        
        v7.5 expects:
        - summary: {unit_count, total_investment, cap_rate, roi}
        - project_rating: str
        - cap_rate: float
        - roi: float
        """
        # Extract from v11.0 pseudo data
        financial_projections = pseudo_data.get('financial_projections', {})
        unit_count = pseudo_data.get('unit_count', feasibility.get('unit_count', 30))
        
        # Calculate totals
        construction_cost = pseudo_data.get('construction_cost', 0)
        land_cost = land_appraisal_price
        total_investment = construction_cost + land_cost
        
        # Financial metrics
        cap_rate = financial_projections.get('cap_rate', 4.5)
        roi = financial_projections.get('roi_10yr', 15.0)
        irr = financial_projections.get('irr_10yr', 8.0)
        
        # Project rating
        project_rating = self._calculate_project_rating(cap_rate, roi)
        
        return {
            'summary': {
                'unit_count': unit_count,
                'total_investment': total_investment,
                'cap_rate': cap_rate,
                'roi': roi,
                'construction_cost': construction_cost,
                'land_cost': land_cost
            },
            'cap_rate': cap_rate,
            'roi': roi,
            'irr_10yr': irr,
            'project_rating': project_rating,
            'lh_purchase_price': pseudo_data.get('lh_purchase_price', 0),
            'gap_analysis': {
                'gap_amount': pseudo_data.get('lh_gap', 0),
                'gap_percentage': pseudo_data.get('lh_gap_pct', 0)
            }
        }
    
    def _calculate_project_rating(self, cap_rate: float, roi: float) -> str:
        """Calculate project rating based on metrics"""
        if cap_rate >= 5.0 and roi >= 20.0:
            return 'EXCELLENT'
        elif cap_rate >= 4.0 and roi >= 15.0:
            return 'GOOD'
        elif cap_rate >= 3.0 and roi >= 10.0:
            return 'FAIR'
        else:
            return 'POOR'
    
    def _build_lh_scores(
        self,
        lh_score_v11: Dict[str, Any],
        total_score_v75: float,
        grade_v75: str
    ) -> Dict[str, Any]:
        """
        Build lh_scores structure for v7.5
        
        v7.5 expects:
        - total_score: float (0-110)
        - grade: str (A/B/C/D/F)
        - breakdown: dict of category scores
        """
        # Get v11.0 breakdown
        breakdown_v11 = lh_score_v11.get('breakdown', {})
        
        # Convert each category score (multiply by 1.1)
        breakdown_v75 = {}
        for category, score_data in breakdown_v11.items():
            if isinstance(score_data, dict):
                score_100 = score_data.get('score', 0)
                max_100 = score_data.get('max_points', 0)
                breakdown_v75[category] = {
                    'score': round(score_100 * 1.1, 1),
                    'max_points': round(max_100 * 1.1, 1),
                    'percentage': score_data.get('percentage', 0)
                }
        
        return {
            'total_score': total_score_v75,
            'max_score': 110,
            'grade': grade_v75,
            'breakdown': breakdown_v75
        }


# Global adapter instance
v11_to_v75_adapter = V11ToV75Adapter()


def convert_v11_analysis_to_v75_format(
    address: str,
    land_area: float,
    land_appraisal_price: float,
    zone_type: str,
    v11_analysis_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Quick conversion function
    
    Usage:
        v75_data = convert_v11_analysis_to_v75_format(
            address="...",
            land_area=1000,
            land_appraisal_price=9000000000,
            zone_type="제2종일반주거지역",
            v11_analysis_result=analysis_result
        )
        
        # Then use with v7.5 generator
        from app.services.lh_report_generator_v7_5_final import LHReportGeneratorV75Final
        generator = LHReportGeneratorV75Final()
        report = generator.run(
            address=address,
            land_area=land_area,
            land_appraisal_price=land_appraisal_price,
            data=v75_data
        )
    """
    return v11_to_v75_adapter.convert_v11_to_v75(
        address, land_area, land_appraisal_price, zone_type, v11_analysis_result
    )
