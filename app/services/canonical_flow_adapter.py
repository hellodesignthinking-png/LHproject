"""
Canonical Flow Adapter
Bridges existing AnalysisEngine with new Canonical Flow architecture

This adapter:
1. Extracts appraisal data from AnalysisEngine output
2. Creates CanonicalAppraisalResult
3. Locks it in AppraisalContextLock
4. Provides it to downstream engines (Land Diagnosis, LH Analysis)

Version: v8.7+
Date: 2025-12-15
"""

from typing import Dict, Any, Optional
from app.services.canonical_schema import (
    CanonicalAppraisalResult,
    ZoningInfo,
    OfficialLandPrice,
    TransactionCase,
    PremiumInfo,
    PremiumDetail,
    CalculationInfo,
    ConfidenceInfo,
    ConfidenceFactors,
    MetadataInfo,
    create_appraisal_from_analysis
)
from app.services.appraisal_context import AppraisalContextLock
from datetime import datetime


class CanonicalFlowAdapter:
    """
    Adapter to convert existing analysis results to canonical flow
    
    Usage:
        adapter = CanonicalFlowAdapter()
        
        # After running analysis_engine
        analysis_result = await engine.analyze_land(request)
        
        # Create and lock appraisal context
        appraisal_ctx = adapter.create_appraisal_context(
            analysis_result=analysis_result,
            land_area=request.land_area,
            official_price=request.official_land_price or 0,
            transaction_price=request.recent_transaction_price
        )
        
        # Now use appraisal_ctx in subsequent engines
        # Land Diagnosis, LH Analysis, etc.
    """
    
    def __init__(self):
        self.context_lock = AppraisalContextLock()
    
    def create_appraisal_context(
        self,
        analysis_result: Dict[str, Any],
        land_area: float,
        official_price: float,
        transaction_price: Optional[float] = None,
        premium_rate: Optional[float] = None
    ) -> AppraisalContextLock:
        """
        Create and lock appraisal context from analysis result
        
        Args:
            analysis_result: Output from AnalysisEngine.analyze_land()
            land_area: Land area in sqm
            official_price: Official land price per sqm
            transaction_price: Recent transaction price per sqm (optional)
            premium_rate: Premium rate to apply (0-1), if None will calculate
        
        Returns:
            Locked AppraisalContextLock instance
        """
        
        # Extract zone info from analysis result
        zone_info = analysis_result.get('zone_info')
        
        # Calculate premium rate if not provided
        if premium_rate is None:
            premium_rate = self._calculate_premium_rate(analysis_result)
        
        # Create canonical appraisal result
        appraisal_result = create_appraisal_from_analysis(
            zone_info=zone_info,
            land_area=land_area,
            official_price=official_price,
            transaction_price=transaction_price,
            premium_rate=premium_rate,
            confidence_score=self._calculate_confidence(analysis_result)
        )
        
        # Create new context lock
        context_lock = AppraisalContextLock()
        
        # Lock the appraisal result
        context_lock.lock(appraisal_result.to_context_dict())
        
        return context_lock
    
    def _calculate_premium_rate(self, analysis_result: Dict[str, Any]) -> float:
        """
        Calculate premium rate based on analysis factors
        
        Premium components:
        - Development potential: High accessibility, good demographics
        - Location premium: Near subway, amenities
        - Policy benefit: LH priority area
        
        Returns:
            Premium rate (0-1, typically 0-0.20)
        """
        premium = 0.0
        
        # 1. Development potential (max 8%)
        accessibility = analysis_result.get('accessibility', {})
        accessibility_score = accessibility.get('accessibility_score', 0)
        if accessibility_score >= 80:
            premium += 0.08
        elif accessibility_score >= 60:
            premium += 0.05
        elif accessibility_score >= 40:
            premium += 0.03
        
        # 2. Location premium (max 5%)
        subway_distance = accessibility.get('subway_distance', 9999)
        if subway_distance < 300:
            premium += 0.05
        elif subway_distance < 500:
            premium += 0.03
        elif subway_distance < 800:
            premium += 0.02
        
        # 3. Policy benefit (max 3%)
        # Check if in LH priority area (metro regions with high demand)
        summary = analysis_result.get('summary', {})
        overall_score = summary.get('overall_score', 0)
        if overall_score >= 80:
            premium += 0.03
        elif overall_score >= 70:
            premium += 0.02
        elif overall_score >= 60:
            premium += 0.01
        
        # 4. Demographics bonus (max 2%)
        demographic_info = analysis_result.get('demographic_info', {})
        youth_ratio = demographic_info.get('youth_ratio', 0)
        if youth_ratio >= 30:
            premium += 0.02
        elif youth_ratio >= 20:
            premium += 0.01
        
        # Cap total premium at 20%
        return min(premium, 0.20)
    
    def _calculate_confidence(self, analysis_result: Dict[str, Any]) -> float:
        """
        Calculate confidence score for appraisal
        
        Factors:
        - Data completeness: All required data available
        - API success rate: All APIs returned data
        - Risk factors: Fewer risks = higher confidence
        
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.85  # Base confidence
        
        # Check data completeness
        required_fields = ['zone_info', 'accessibility', 'demographic_info', 'summary']
        missing_fields = sum(1 for field in required_fields if not analysis_result.get(field))
        
        if missing_fields == 0:
            confidence += 0.05
        elif missing_fields >= 2:
            confidence -= 0.10
        
        # Check risk factors
        risk_factors = analysis_result.get('risk_factors', [])
        if len(risk_factors) == 0:
            confidence += 0.05
        elif len(risk_factors) >= 3:
            confidence -= 0.05
        
        # Ensure confidence is in valid range
        return max(0.70, min(confidence, 0.95))
    
    def extract_for_land_diagnosis(
        self,
        appraisal_ctx: AppraisalContextLock,
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract data needed for Land Diagnosis from locked appraisal context
        
        Land Diagnosis should NOT re-query APIs or recalculate appraisal values.
        It should only interpret the locked appraisal data.
        
        Args:
            appraisal_ctx: Locked appraisal context
            analysis_result: Original analysis result (for non-appraisal data)
        
        Returns:
            Dictionary with data for Land Diagnosis
        """
        return {
            'zoning': appraisal_ctx.get('zoning.confirmed_type'),
            'building_coverage_ratio': appraisal_ctx.get('zoning.building_coverage_ratio'),
            'floor_area_ratio': appraisal_ctx.get('zoning.floor_area_ratio'),
            'appraised_value': appraisal_ctx.get('calculation.final_appraised_total'),
            'premium_rate': appraisal_ctx.get('premium.total_premium_rate'),
            'confidence': appraisal_ctx.get('confidence.score'),
            'land_area': appraisal_ctx.get('calculation.land_area_sqm'),
            
            # Non-appraisal data (from analysis_result)
            'risk_factors': analysis_result.get('risk_factors', []),
            'accessibility': analysis_result.get('accessibility', {}),
            'hazardous_facilities': analysis_result.get('hazardous_facilities', []),
            
            # Metadata
            'based_on_appraisal': True,
            'appraisal_version': appraisal_ctx.get('metadata.appraisal_engine')
        }
    
    def extract_for_lh_analysis(
        self,
        appraisal_ctx: AppraisalContextLock,
        expected_units: int,
        total_floor_area: float
    ) -> Dict[str, Any]:
        """
        Extract data needed for LH Analysis from locked appraisal context
        
        LH Analysis should use the appraised land value as the definitive
        land cost, without recalculating it.
        
        Args:
            appraisal_ctx: Locked appraisal context
            expected_units: Expected number of units
            total_floor_area: Total floor area (sqm)
        
        Returns:
            Dictionary with data for LH Analysis
        """
        return {
            'land_appraised_value': appraisal_ctx.get('calculation.final_appraised_total'),
            'land_area': appraisal_ctx.get('calculation.land_area_sqm'),
            'appraised_price_per_sqm': appraisal_ctx.get('calculation.premium_adjusted_per_sqm'),
            'zoning': appraisal_ctx.get('zoning.confirmed_type'),
            'expected_units': expected_units,
            'total_floor_area': total_floor_area,
            
            # Metadata
            'based_on_appraisal': True,
            'appraisal_version': appraisal_ctx.get('metadata.appraisal_engine'),
            'appraisal_confidence': appraisal_ctx.get('confidence.score')
        }
    
    def get_appraisal_summary(self, appraisal_ctx: AppraisalContextLock) -> Dict[str, Any]:
        """
        Get human-readable summary of appraisal context
        
        Args:
            appraisal_ctx: Locked appraisal context
        
        Returns:
            Summary dictionary
        """
        return appraisal_ctx.get_summary()


def create_canonical_adapter() -> CanonicalFlowAdapter:
    """
    Factory function to create canonical flow adapter
    
    Returns:
        CanonicalFlowAdapter instance
    """
    return CanonicalFlowAdapter()


__all__ = [
    'CanonicalFlowAdapter',
    'create_canonical_adapter'
]
