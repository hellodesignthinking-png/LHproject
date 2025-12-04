"""
ZeroSite v8.6 - Data Mapping Layer

CRITICAL FIX: Bridge v8.5 Financial Engine → v7.5 Report Template
- Standardizes financial_result JSON structure
- Maps v8.5 data to report template keys
- Eliminates all KeyError issues
- Removes v7.5 GAP model and dummy logic

Purpose:
- 100% compatibility between v8.5 backend and v7.5/v8.6 report templates
- Automatic detection and mapping of all required keys
- Fallback handling for missing data

Key Mappings:
1. financial_result structure standardization
2. lh_scores_v85 → report template keys
3. POI distances → actual values (not 9999m)
4. analysis_mode (LH_LINKED vs STANDARD)
5. per_unit costs and LH prices
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DataMapperV86:
    """
    v8.6 Data Mapping Layer
    
    Converts v8.5 financial_result and analysis_data into standardized format
    that works with all report templates without KeyError
    """
    
    def __init__(self):
        self.version = "v8.6"
        logger.info(f"🔄 {self.version} Data Mapper initialized")
    
    def standardize_financial_result(
        self, 
        financial_result: Dict[str, Any],
        analysis_data: Dict[str, Any],
        basic_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Standardize v8.5 financial_result into v8.6 format
        
        Ensures all required keys exist for report generation:
        - analysis_mode (LH_LINKED or STANDARD)
        - land_appraisal (total land price)
        - verified_cost (total construction cost)
        - lh_purchase_price (LH acquisition price)
        - roi (return on investment)
        - cap_rate (capitalization rate)
        - project_rating (A/B/C/D)
        - decision (GO/CONDITIONAL/REVISE/NO-GO)
        - per_unit_cost (construction cost per unit)
        - per_unit_lh_price (LH price per unit)
        - gap_percentage (ROI as percentage)
        - explanation (recommendation explanation)
        """
        try:
            logger.info("🔄 Standardizing financial_result (v8.5 → v8.6)...")
            
            # Extract v8.5 summary data
            summary = financial_result.get('summary', {})
            capex = financial_result.get('capex', {})
            noi_data = financial_result.get('noi', {})
            returns = financial_result.get('returns', {})
            lh_sim = financial_result.get('lh_simulation', {})
            
            # Get basic metrics
            unit_count = summary.get('unit_count', 0)
            total_capex = summary.get('total_investment', 0)
            cap_rate = summary.get('cap_rate', 0)
            irr_estimate = returns.get('irr_estimate', 0)
            
            # Determine analysis mode
            analysis_mode = 'LH_LINKED' if unit_count >= 50 else 'STANDARD'
            
            # Calculate land appraisal (total land price)
            land_area = basic_info.get('land_area', 0)
            land_appraisal_price = basic_info.get('land_appraisal_price', 0)
            
            if land_appraisal_price and land_area:
                # User provided appraisal price per sqm
                land_appraisal_total = land_appraisal_price * land_area
                logger.info(f"  ✓ Land appraisal: {land_appraisal_price:,.0f} KRW/㎡ × {land_area:.0f}㎡ = {land_appraisal_total:,.0f} KRW")
            else:
                # Fallback to capex land acquisition
                land_acquisition = capex.get('land_acquisition', {})
                land_appraisal_total = land_acquisition.get('land_purchase_price', 0)
                logger.info(f"  ✓ Land appraisal (from capex): {land_appraisal_total:,.0f} KRW")
            
            # Calculate verified cost (total construction)
            construction_hard_costs = capex.get('construction_hard_costs', {})
            soft_costs = capex.get('soft_costs', {})
            ffe = capex.get('ffe', {})
            
            verified_cost = (
                construction_hard_costs.get('total', 0) +
                soft_costs.get('total', 0) +
                ffe.get('total', 0)
            )
            
            logger.info(f"  ✓ Verified cost (construction): {verified_cost:,.0f} KRW")
            
            # Get LH purchase price
            lh_purchase_price = lh_sim.get('lh_purchase_price', 0)
            market_value = lh_sim.get('market_value', total_capex)
            
            logger.info(f"  ✓ LH purchase price: {lh_purchase_price:,.0f} KRW")
            logger.info(f"  ✓ Market value: {market_value:,.0f} KRW")
            
            # Calculate ROI (as percentage)
            if total_capex > 0:
                roi = ((lh_purchase_price - total_capex) / total_capex) * 100
            else:
                roi = 0
            
            logger.info(f"  ✓ ROI: {roi:.2f}%")
            
            # Calculate gap percentage (same as ROI)
            gap_percentage = roi
            gap_amount = lh_purchase_price - total_capex
            
            # Determine project rating based on Cap Rate and ROI
            if cap_rate >= 6.0 and roi >= 8.0:
                project_rating = 'A'
            elif cap_rate >= 4.5 and roi >= 5.0:
                project_rating = 'B'
            elif cap_rate >= 3.0 and roi >= 2.0:
                project_rating = 'C'
            else:
                project_rating = 'D'
            
            # Determine decision based on rating
            if project_rating == 'A':
                decision = 'GO'
            elif project_rating == 'B':
                decision = 'CONDITIONAL'
            elif project_rating == 'C':
                decision = 'REVISE'
            else:
                decision = 'NO-GO'
            
            # Calculate per-unit costs
            if unit_count > 0:
                per_unit_cost = verified_cost / unit_count
                per_unit_lh_price = lh_purchase_price / unit_count
            else:
                per_unit_cost = 0
                per_unit_lh_price = 0
            
            logger.info(f"  ✓ Per-unit cost: {per_unit_cost:,.0f} KRW")
            logger.info(f"  ✓ Per-unit LH price: {per_unit_lh_price:,.0f} KRW")
            
            # Generate explanation
            explanation = self._generate_recommendation_explanation(
                decision=decision,
                cap_rate=cap_rate,
                roi=roi,
                unit_count=unit_count,
                project_rating=project_rating
            )
            
            # Get LH recommendation
            profitability_score = lh_sim.get('profitability_score', 0)
            lh_recommendation = lh_sim.get('recommendation', decision)
            
            # Create standardized v8.6 structure
            standardized = {
                # Original v8.5 data
                **financial_result,
                
                # v8.6 standardized fields
                'analysis_mode': analysis_mode,
                'land_appraisal': land_appraisal_total,
                'verified_cost': verified_cost,
                'lh_purchase_price': lh_purchase_price,
                'market_value': market_value,
                'roi': roi,
                'cap_rate': cap_rate,
                'project_rating': project_rating,
                'decision': decision,
                'per_unit_cost': per_unit_cost,
                'per_unit_lh_price': per_unit_lh_price,
                'gap_percentage': gap_percentage,
                'gap_amount': gap_amount,
                'explanation': explanation,
                'recommendation': lh_recommendation,
                'profitability_score': profitability_score,
                
                # Ensure lh_simulation has all keys
                'lh_simulation': {
                    **lh_sim,
                    'gap_percentage': gap_percentage,
                    'gap_amount': gap_amount,
                    'recommendation': lh_recommendation,
                    'explanation': explanation,
                    'profitability_score': profitability_score,
                    'lh_purchase_price': lh_purchase_price,
                    'market_value': market_value,
                },
                
                # Add price_per_unit_lh for template compatibility
                'price_per_unit_lh': per_unit_lh_price,
            }
            
            logger.info(f"✅ v8.6 standardization complete:")
            logger.info(f"  • Analysis Mode: {analysis_mode}")
            logger.info(f"  • Project Rating: {project_rating}")
            logger.info(f"  • Decision: {decision}")
            logger.info(f"  • Unit Count: {unit_count}")
            logger.info(f"  • Cap Rate: {cap_rate:.2f}%")
            logger.info(f"  • ROI: {roi:.2f}%")
            
            return standardized
            
        except Exception as e:
            logger.error(f"❌ Error in standardize_financial_result: {e}")
            import traceback
            traceback.print_exc()
            
            # Return safe fallback
            return {
                **financial_result,
                'analysis_mode': 'STANDARD',
                'land_appraisal': 0,
                'verified_cost': 0,
                'lh_purchase_price': 0,
                'market_value': 0,
                'roi': 0,
                'cap_rate': 0,
                'project_rating': 'D',
                'decision': 'NO-GO',
                'per_unit_cost': 0,
                'per_unit_lh_price': 0,
                'price_per_unit_lh': 0,
                'gap_percentage': 0,
                'gap_amount': 0,
                'explanation': 'Data processing error occurred',
                'recommendation': 'REVISE',
                'profitability_score': 0,
                'lh_simulation': {
                    'gap_percentage': 0,
                    'gap_amount': 0,
                    'recommendation': 'REVISE',
                    'explanation': 'Data processing error occurred',
                    'profitability_score': 0,
                    'lh_purchase_price': 0,
                    'market_value': 0,
                }
            }
    
    def _generate_recommendation_explanation(
        self, 
        decision: str, 
        cap_rate: float, 
        roi: float, 
        unit_count: int, 
        project_rating: str
    ) -> str:
        """Generate detailed recommendation explanation"""
        
        if decision == 'GO':
            return (
                f"이 프로젝트는 우수한 재무 지표를 보이고 있습니다 (Cap Rate: {cap_rate:.2f}%, ROI: {roi:.2f}%). "
                f"총 {unit_count}세대 규모로 LH 매입 조건을 충족하며, 투자 타당성이 높은 {project_rating}등급 사업입니다. "
                f"즉시 사업 추진을 권장합니다."
            )
        elif decision == 'CONDITIONAL':
            return (
                f"이 프로젝트는 양호한 재무 지표를 보이나 (Cap Rate: {cap_rate:.2f}%, ROI: {roi:.2f}%) "
                f"일부 개선이 필요합니다. {unit_count}세대 규모이며 {project_rating}등급으로 평가됩니다. "
                f"리스크 관리 조치 이행 후 사업 추진을 권장합니다."
            )
        elif decision == 'REVISE':
            return (
                f"이 프로젝트는 재무 지표 개선이 필요합니다 (Cap Rate: {cap_rate:.2f}%, ROI: {roi:.2f}%). "
                f"{unit_count}세대 규모로 {project_rating}등급이며, 사업 구조 재검토 후 재평가가 필요합니다."
            )
        else:  # NO-GO
            return (
                f"이 프로젝트는 현재 재무 타당성이 부족합니다 (Cap Rate: {cap_rate:.2f}%, ROI: {roi:.2f}%). "
                f"{unit_count}세대 규모로 {project_rating}등급이며, 사업 조건 대폭 개선 없이는 추진을 권장하지 않습니다."
            )
    
    def map_accessibility_distances(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map POI distances to actual values (not 9999m)
        
        Fixes:
        - subway_distance: 9999m → actual distance or '2km 이상'
        - school_distance: 9999m → actual distance or '2km 이상'
        - hospital_distance: 9999m → actual distance or '2km 이상'
        """
        try:
            logger.info("🔄 Mapping POI accessibility distances...")
            
            accessibility = analysis_data.get('accessibility', {})
            if isinstance(accessibility, dict):
                # Get distances
                subway_distance = accessibility.get('nearest_subway_distance', 9999)
                school_distance = accessibility.get('nearest_school_distance', 9999)
                hospital_distance = accessibility.get('nearest_hospital_distance', 9999)
                
                # Convert 9999m to human-readable format
                if subway_distance >= 2000:
                    accessibility['nearest_subway_distance_display'] = '2km 이상'
                elif subway_distance > 0:
                    accessibility['nearest_subway_distance_display'] = f'{subway_distance:.0f}m'
                else:
                    accessibility['nearest_subway_distance_display'] = '데이터 없음'
                
                if school_distance >= 2000:
                    accessibility['nearest_school_distance_display'] = '2km 이상'
                elif school_distance > 0:
                    accessibility['nearest_school_distance_display'] = f'{school_distance:.0f}m'
                else:
                    accessibility['nearest_school_distance_display'] = '데이터 없음'
                
                if hospital_distance >= 2000:
                    accessibility['nearest_hospital_distance_display'] = '2km 이상'
                elif hospital_distance > 0:
                    accessibility['nearest_hospital_distance_display'] = f'{hospital_distance:.0f}m'
                else:
                    accessibility['nearest_hospital_distance_display'] = '데이터 없음'
                
                logger.info(f"  ✓ Subway: {accessibility['nearest_subway_distance_display']}")
                logger.info(f"  ✓ School: {accessibility['nearest_school_distance_display']}")
                logger.info(f"  ✓ Hospital: {accessibility['nearest_hospital_distance_display']}")
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"❌ Error in map_accessibility_distances: {e}")
            return analysis_data
    
    def ensure_risk_structure(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure risk analysis structure exists
        
        Adds missing keys:
        - risk['executive_summary']['overall_risk_level']
        """
        try:
            if 'risk' not in analysis_data:
                analysis_data['risk'] = {}
            
            risk = analysis_data['risk']
            
            if 'executive_summary' not in risk:
                risk['executive_summary'] = {}
            
            if 'overall_risk_level' not in risk['executive_summary']:
                # Determine risk level from risk_factors
                risk_factors = analysis_data.get('risk_factors', [])
                high_risk_count = sum(1 for r in risk_factors if getattr(r, 'severity', '') == 'HIGH')
                
                if high_risk_count >= 3:
                    overall_risk = 'HIGH'
                elif high_risk_count >= 1:
                    overall_risk = 'MEDIUM'
                else:
                    overall_risk = 'LOW'
                
                risk['executive_summary']['overall_risk_level'] = overall_risk
                logger.info(f"  ✓ Risk level determined: {overall_risk}")
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"❌ Error in ensure_risk_structure: {e}")
            return analysis_data
    
    def process_all(
        self,
        financial_result: Dict[str, Any],
        analysis_data: Dict[str, Any],
        basic_info: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process all data mappings at once
        
        Returns:
            (standardized_financial_result, enhanced_analysis_data)
        """
        logger.info("🔄 Processing all v8.6 data mappings...")
        
        # 1. Standardize financial result
        standardized_financial = self.standardize_financial_result(
            financial_result, analysis_data, basic_info
        )
        
        # 2. Map accessibility distances
        enhanced_analysis = self.map_accessibility_distances(analysis_data)
        
        # 3. Ensure risk structure
        enhanced_analysis = self.ensure_risk_structure(enhanced_analysis)
        
        logger.info("✅ All v8.6 data mappings complete")
        
        return standardized_financial, enhanced_analysis
