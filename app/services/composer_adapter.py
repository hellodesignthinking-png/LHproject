"""
ZeroSite v3.3 Composer Data Adapter
====================================

Adapter layer to convert unified AppraisalContext data into
the specific data structures required by each Composer.

This solves the impedance mismatch between:
- API: Unified AppraisalContextLock with all data
- Composers: Specific __init__ parameters (land_diagnosis, lh_result, etc.)

Author: ZeroSite Development Team
Date: 2025-12-15
Version: v1.0
"""

from typing import Dict, Any, Optional
from app.services.appraisal_context import AppraisalContextLock


class ComposerDataAdapter:
    """
    Extracts Composer-specific data structures from unified AppraisalContext
    
    Usage:
        ctx = AppraisalContextLock()
        ctx.lock(appraisal_data)
        
        # For Pre-Report
        data = ComposerDataAdapter.for_pre_report(ctx)
        composer = PreReportComposer(**data)
        
        # For Investor Report
        data = ComposerDataAdapter.for_investor(ctx)
        composer = InvestorReportComposer(**data)
    """
    
    # ============================================================================
    # Type-Specific Extractors (One method per Composer)
    # ============================================================================
    
    @staticmethod
    def for_pre_report(ctx: AppraisalContextLock) -> Dict[str, Any]:
        """
        Extract data for PreReportComposer
        
        Required params:
        - appraisal_ctx: AppraisalContextLock
        - land_diagnosis: Dict
        - lh_result: Dict
        - ch4_scores: Optional[Dict]
        """
        return {
            'appraisal_ctx': ctx,
            'land_diagnosis': ComposerDataAdapter.extract_land_diagnosis(ctx),
            'lh_result': ComposerDataAdapter.extract_lh_result(ctx),
            'ch4_scores': ComposerDataAdapter.extract_ch4_scores(ctx)
        }
    
    @staticmethod
    def for_comprehensive(ctx: AppraisalContextLock) -> Dict[str, Any]:
        """
        Extract data for ComprehensiveReportComposer
        
        Required params:
        - appraisal_ctx: AppraisalContextLock
        - land_diagnosis: Dict
        - lh_result: Dict
        - ch3_scores: Optional[Dict]
        - ch4_scores: Optional[Dict]
        - risk_matrix: Optional[Dict]
        - financial_analysis: Optional[Dict]
        """
        return {
            'appraisal_ctx': ctx,
            'land_diagnosis': ComposerDataAdapter.extract_land_diagnosis(ctx),
            'lh_result': ComposerDataAdapter.extract_lh_result(ctx),
            'ch3_scores': ComposerDataAdapter.extract_ch3_scores(ctx),
            'ch4_scores': ComposerDataAdapter.extract_ch4_scores(ctx),
            'risk_matrix': ComposerDataAdapter.extract_risk_matrix(ctx),
            'financial_analysis': ComposerDataAdapter.extract_financial_analysis(ctx)
        }
    
    @staticmethod
    def for_lh_decision(ctx: AppraisalContextLock) -> Dict[str, Any]:
        """
        Extract data for LHDecisionReportComposer
        
        Required params:
        - appraisal_ctx: AppraisalContextLock
        - lh_result: Dict
        - ch3_scores: Optional[Dict]
        - ch4_scores: Optional[Dict]
        """
        return {
            'appraisal_ctx': ctx,
            'lh_result': ComposerDataAdapter.extract_lh_result(ctx),
            'ch3_scores': ComposerDataAdapter.extract_ch3_scores(ctx),
            'ch4_scores': ComposerDataAdapter.extract_ch4_scores(ctx)
        }
    
    @staticmethod
    def for_investor(ctx: AppraisalContextLock) -> Dict[str, Any]:
        """
        Extract data for InvestorReportComposer
        
        Required params:
        - appraisal_ctx: AppraisalContextLock
        - land_diagnosis: Dict
        - lh_result: Dict
        - risk_matrix: Optional[Dict]
        - financial_analysis: Optional[Dict]
        """
        return {
            'appraisal_ctx': ctx,
            'land_diagnosis': ComposerDataAdapter.extract_land_diagnosis(ctx),
            'lh_result': ComposerDataAdapter.extract_lh_result(ctx),
            'risk_matrix': ComposerDataAdapter.extract_risk_matrix(ctx),
            'financial_analysis': ComposerDataAdapter.extract_financial_analysis(ctx)
        }
    
    @staticmethod
    def for_land_price(ctx: AppraisalContextLock) -> Dict[str, Any]:
        """
        Extract data for LandPriceReportComposer
        
        Required params:
        - appraisal_ctx: AppraisalContextLock
        - land_diagnosis: Dict
        - lh_result: Optional[Dict]
        """
        return {
            'appraisal_ctx': ctx,
            'land_diagnosis': ComposerDataAdapter.extract_land_diagnosis(ctx),
            'lh_result': ComposerDataAdapter.extract_lh_result(ctx)
        }
    
    @staticmethod
    def for_internal(ctx: AppraisalContextLock) -> Dict[str, Any]:
        """
        Extract data for InternalAssessmentComposer
        
        Required params:
        - appraisal_ctx: AppraisalContextLock
        - land_diagnosis: Dict
        - lh_result: Dict
        - ch4_scores: Optional[Dict]
        - risk_matrix: Optional[Dict]
        - financial_analysis: Optional[Dict]
        """
        return {
            'appraisal_ctx': ctx,
            'land_diagnosis': ComposerDataAdapter.extract_land_diagnosis(ctx),
            'lh_result': ComposerDataAdapter.extract_lh_result(ctx),
            'ch4_scores': ComposerDataAdapter.extract_ch4_scores(ctx),
            'risk_matrix': ComposerDataAdapter.extract_risk_matrix(ctx),
            'financial_analysis': ComposerDataAdapter.extract_financial_analysis(ctx)
        }
    
    # ============================================================================
    # Data Extraction Methods
    # ============================================================================
    
    @staticmethod
    def extract_land_diagnosis(ctx: AppraisalContextLock) -> Dict[str, Any]:
        """
        Extract land diagnosis data (INTERPRETATION layer)
        
        Returns:
            {
                'development_potential': str,
                'buildable_area': float,
                'expected_units': dict,
                'floor_plan': dict,
                'parking': dict,
                'access_quality': str,
                'infrastructure': str,
                'risk_level': str
            }
        """
        # Get basic metrics from context
        land_area = ctx.get('calculation.land_area_sqm', 0)
        far = ctx.get('zoning.floor_area_ratio', 250.0)
        bcr = ctx.get('zoning.building_coverage_ratio', 50.0)
        
        # Calculate buildable area
        buildable_area = land_area * (far / 100.0)
        
        # Estimate units (assuming ~30-35 sqm per unit)
        min_units = int(buildable_area / 35)
        max_units = int(buildable_area / 30)
        
        # Estimate floors (assuming 3m per floor)
        max_height = far * 3  # Rough estimate
        max_floors = int(max_height / 3)
        
        # Parking calculation (0.5 per unit)
        required_parking = int((min_units + max_units) / 2 * 0.5)
        possible_parking = int(land_area * 0.15)  # 15% of land for parking
        
        # Determine development potential
        if far >= 300 and land_area >= 500:
            potential = 'HIGH'
        elif far >= 250 or land_area >= 300:
            potential = 'MEDIUM'
        else:
            potential = 'LOW'
        
        # Infrastructure and risk assessment
        access_quality = 'GOOD'  # Default (would come from location analysis)
        infrastructure = 'ADEQUATE'
        
        # Risk level based on constraints
        risk_level = 'LOW'
        if required_parking > possible_parking:
            risk_level = 'MEDIUM'
        if land_area < 200:
            risk_level = 'HIGH'
        
        return {
            'development_potential': potential,
            'buildable_area': buildable_area,
            'expected_units': {
                'min': min_units,
                'max': max_units,
                'average': int((min_units + max_units) / 2)
            },
            'floor_plan': {
                'max_floors': max_floors,
                'allowable_use': ['residential', 'mixed_use']
            },
            'parking': {
                'required': required_parking,
                'possible': possible_parking,
                'feasible': possible_parking >= required_parking
            },
            'access_quality': access_quality,
            'infrastructure': infrastructure,
            'risk_level': risk_level
        }
    
    @staticmethod
    def extract_lh_result(ctx: AppraisalContextLock) -> Dict[str, Any]:
        """
        Extract LH evaluation result (JUDGMENT layer)
        
        Returns:
            {
                'decision': str,  # GO/CONDITIONAL/NO-GO
                'pass_probability': float,
                'roi': float,
                'lh_purchase_price': float,
                'analysis_result': dict,
                'predicted_result': str,
                'adequacy': str
            }
        """
        # Get financial data from context
        appraised_value = ctx.get('calculation.final_appraised_total', 0)
        land_area = ctx.get('calculation.land_area_sqm', 0)
        far = ctx.get('zoning.floor_area_ratio', 250.0)
        
        # Calculate buildable area and construction cost
        buildable_area = land_area * (far / 100.0)
        construction_cost_per_sqm = 2_500_000  # 평당 250만원 = sqm당 ~250만원
        total_construction_cost = buildable_area * construction_cost_per_sqm
        
        # Soft costs and indirect costs
        soft_cost = total_construction_cost * 0.05
        indirect_cost = total_construction_cost * 0.08
        supervision_cost = total_construction_cost * 0.03
        
        verified_cost = soft_cost + indirect_cost + supervision_cost
        total_cost = total_construction_cost + verified_cost + appraised_value
        
        # LH purchase price (typically 120% of total cost)
        lh_purchase_price = total_cost * 1.20
        
        # Calculate ROI
        profit = lh_purchase_price - total_cost
        roi = (profit / total_cost) * 100 if total_cost > 0 else 0
        
        # Determine pass probability
        base_probability = 0.50
        
        # Bonuses
        if far >= 300:
            base_probability += 0.15
        elif far >= 250:
            base_probability += 0.10
        
        if land_area >= 500:
            base_probability += 0.10
        elif land_area >= 300:
            base_probability += 0.05
        
        if roi >= 25:
            base_probability += 0.10
        elif roi >= 20:
            base_probability += 0.05
        
        pass_probability = min(base_probability, 0.95)
        
        # Decision logic
        if pass_probability >= 0.75:
            decision = 'GO'
            predicted_result = 'PASS'
            adequacy = 'ADEQUATE'
        elif pass_probability >= 0.45:
            decision = 'CONDITIONAL'
            predicted_result = 'CONDITIONAL'
            adequacy = 'MARGINAL'
        else:
            decision = 'NO-GO'
            predicted_result = 'FAIL'
            adequacy = 'INADEQUATE'
        
        return {
            'decision': decision,
            'pass_probability': pass_probability,
            'predicted_result': predicted_result,
            'roi': roi,
            'lh_purchase_price': lh_purchase_price,
            'adequacy': adequacy,
            'analysis_result': {
                'construction_cost': total_construction_cost,
                'verified_cost': verified_cost,
                'total_cost': total_cost,
                'expected_profit': profit
            },
            'deduction_factors': []
        }
    
    @staticmethod
    def extract_risk_matrix(ctx: AppraisalContextLock) -> Dict[str, Any]:
        """
        Extract risk assessment matrix (INTERPRETATION layer)
        
        Returns:
            {
                'total_risk_score': int,
                'risk_level': str,
                'risk_items': list
            }
        """
        risk_items = []
        total_score = 0
        
        # Check various risk factors
        land_area = ctx.get('calculation.land_area_sqm', 0)
        far = ctx.get('zoning.floor_area_ratio', 250.0)
        
        # Size risk
        if land_area < 300:
            risk_items.append({
                'category': 'land_size',
                'level': 'MEDIUM',
                'score': 10,
                'description': '토지 면적 소형 (300㎡ 미만)'
            })
            total_score += 10
        
        # Development capacity risk
        if far < 250:
            risk_items.append({
                'category': 'development_capacity',
                'level': 'MEDIUM',
                'score': 8,
                'description': '용적률 제한 (250% 미만)'
            })
            total_score += 8
        
        # Financial risk (from confidence score)
        confidence_score = ctx.get('confidence.score', 85)
        if confidence_score < 70:
            risk_items.append({
                'category': 'valuation_confidence',
                'level': 'HIGH',
                'score': 15,
                'description': f'감정평가 신뢰도 낮음 ({confidence_score}점)'
            })
            total_score += 15
        elif confidence_score < 80:
            risk_items.append({
                'category': 'valuation_confidence',
                'level': 'MEDIUM',
                'score': 8,
                'description': f'감정평가 신뢰도 중간 ({confidence_score}점)'
            })
            total_score += 8
        
        # Determine overall risk level
        if total_score >= 40:
            risk_level = 'HIGH'
        elif total_score >= 20:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'total_risk_score': total_score,
            'risk_level': risk_level,
            'risk_items': risk_items
        }
    
    @staticmethod
    def extract_financial_analysis(ctx: AppraisalContextLock) -> Dict[str, Any]:
        """
        Extract financial analysis data (JUDGMENT layer)
        
        Returns:
            {
                'irr': float,
                'roi': float,
                'npv': float,
                'payback_months': int,
                'scenarios': dict
            }
        """
        # Get LH result for financial calculations
        lh_result = ComposerDataAdapter.extract_lh_result(ctx)
        
        roi = lh_result['roi']
        total_cost = lh_result['analysis_result']['total_cost']
        expected_profit = lh_result['analysis_result']['expected_profit']
        
        # Calculate IRR (simplified: IRR ≈ ROI * 0.6 for typical project timeline)
        irr = roi * 0.6
        
        # Calculate NPV (discount rate 8%)
        discount_rate = 0.08
        project_years = 3
        npv = expected_profit / ((1 + discount_rate) ** project_years)
        
        # Payback period
        if roi >= 30:
            payback_months = 18
        elif roi >= 20:
            payback_months = 24
        elif roi >= 15:
            payback_months = 30
        else:
            payback_months = 36
        
        # Scenario analysis
        scenarios = {
            'best': {
                'irr': irr * 1.3,
                'roi': roi * 1.3,
                'npv': npv * 1.3,
                'probability': 0.20
            },
            'base': {
                'irr': irr,
                'roi': roi,
                'npv': npv,
                'probability': 0.60
            },
            'worst': {
                'irr': irr * 0.6,
                'roi': roi * 0.6,
                'npv': npv * 0.6,
                'probability': 0.20
            }
        }
        
        return {
            'irr': irr,
            'roi': roi,
            'npv': npv,
            'payback_months': payback_months,
            'scenarios': scenarios,
            'break_even_months': int(payback_months * 0.8)
        }
    
    @staticmethod
    def extract_ch3_scores(ctx: AppraisalContextLock) -> Optional[Dict[str, Any]]:
        """
        Extract CH3 (location/infrastructure) scores
        
        Returns None if not available (optional parameter)
        """
        # CH3 scores would come from location analysis
        # For now, return default/mock scores
        return {
            'subway_proximity': 85,
            'bus_accessibility': 75,
            'school_proximity': 80,
            'commercial_proximity': 70,
            'park_proximity': 65,
            'total_score': 75
        }
    
    @staticmethod
    def extract_ch4_scores(ctx: AppraisalContextLock) -> Optional[Dict[str, Any]]:
        """
        Extract CH4 (supply type demand) scores
        
        Returns:
            {
                'youth_score': float,
                'newlyweds_score': float,
                'senior_score': float,
                'general_score': float,
                'family_score': float,
                'recommended_types': list
            }
        """
        # Get location and size factors
        land_area = ctx.get('calculation.land_area_sqm', 0)
        far = ctx.get('zoning.floor_area_ratio', 250.0)
        
        # Base scores (50-70 range)
        base_score = 60
        
        # Adjust based on development capacity
        capacity_bonus = 0
        if far >= 300:
            capacity_bonus = 15
        elif far >= 250:
            capacity_bonus = 10
        elif far >= 200:
            capacity_bonus = 5
        
        # Adjust based on land size
        size_bonus = 0
        if land_area >= 600:
            size_bonus = 10
        elif land_area >= 400:
            size_bonus = 5
        
        # Calculate type-specific scores
        scores = {
            '행복주택': base_score + capacity_bonus + size_bonus,
            '청년': base_score + capacity_bonus + size_bonus - 5,
            '신혼부부': base_score + capacity_bonus + size_bonus - 3,
            '일반': base_score + capacity_bonus,
            '공공임대': base_score + size_bonus
        }
        
        # Get top 2 recommended types
        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        recommended = [t[0] for t in sorted_types[:2]]
        
        return {
            '행복주택': scores['행복주택'],
            '청년': scores['청년'],
            '신혼부부': scores['신혼부부'],
            '일반': scores['일반'],
            '공공임대': scores['공공임대'],
            'recommended_types': recommended
        }
