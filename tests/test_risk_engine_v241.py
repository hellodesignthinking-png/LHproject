"""
Tests for Risk Engine v24.1
GAP #7: Risk Engine Enhancement (Design Risk, Legal Risk)
"""

import pytest
from app.engines.risk_engine_v241 import (
    RiskEngineV241,
    DesignRiskAssessment,
    LegalRiskAssessment,
    ComprehensiveRiskProfile,
    RiskLevel,
    RiskCategory
)


@pytest.fixture
def risk_engine():
    """Risk Engine fixture"""
    return RiskEngineV241()


class TestDesignRiskAssessment:
    """Test design risk assessment (NEW in v24.1)"""
    
    def test_design_risk_calculation(self, risk_engine):
        """Test design risk assessment"""
        assessment = risk_engine.assess_design_risks(
            land_area=660.0,
            floors=10,
            unit_count=33,
            floor_area_ratio=200.0,
            building_coverage_ratio=60.0,
            height_limit=35.0,
            sunlight_compliant=True,
            parking_ratio=1.0
        )
        
        assert isinstance(assessment, DesignRiskAssessment)
        assert 0 <= assessment.overall_design_risk <= 1.0
        assert assessment.risk_level in list(RiskLevel)
        assert len(assessment.recommendations) > 0
    
    def test_high_risk_design(self, risk_engine):
        """Test high-risk design scenario"""
        assessment = risk_engine.assess_design_risks(
            land_area=200.0,  # Small site
            floors=20,  # Many floors
            unit_count=100,  # High density
            floor_area_ratio=400.0,
            building_coverage_ratio=80.0,
            height_limit=30.0,  # Height violation
            sunlight_compliant=False,
            parking_ratio=0.5
        )
        
        assert assessment.overall_design_risk > 0.5
        assert assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    def test_space_efficiency_score(self, risk_engine):
        """Test space efficiency calculation"""
        assessment = risk_engine.assess_design_risks(
            land_area=1000.0,
            floors=10,
            unit_count=40,
            floor_area_ratio=200.0,
            building_coverage_ratio=50.0
        )
        
        assert 0 <= assessment.space_efficiency_score <= 1.0
    
    def test_lighting_and_ventilation(self, risk_engine):
        """Test lighting and ventilation scores"""
        assessment = risk_engine.assess_design_risks(
            land_area=800.0,
            floors=8,
            unit_count=30,
            floor_area_ratio=180.0,
            building_coverage_ratio=45.0,
            sunlight_compliant=True
        )
        
        assert 0 <= assessment.natural_lighting_score <= 1.0
        assert 0 <= assessment.ventilation_score <= 1.0
        assert 0 <= assessment.accessibility_score <= 1.0


class TestLegalRiskAssessment:
    """Test legal risk assessment (NEW in v24.1)"""
    
    def test_legal_risk_calculation(self, risk_engine):
        """Test legal risk assessment"""
        assessment = risk_engine.assess_legal_risks(
            zone_type="제3종일반주거지역",
            floor_area_ratio=200.0,
            far_limit=250.0,
            building_coverage_ratio=55.0,
            bcr_limit=60.0,
            height=30.0,
            height_limit=35.0,
            environmental_impact="LOW",
            title_status="CLEAR",
            neighbor_agreements=True
        )
        
        assert isinstance(assessment, LegalRiskAssessment)
        assert 0 <= assessment.overall_legal_risk <= 1.0
        assert assessment.risk_level in list(RiskLevel)
        assert len(assessment.critical_issues) > 0
        assert len(assessment.recommended_actions) > 0
    
    def test_zoning_violation(self, risk_engine):
        """Test zoning violation scenario"""
        assessment = risk_engine.assess_legal_risks(
            zone_type="주거지역",
            floor_area_ratio=300.0,  # Exceeds limit
            far_limit=200.0,
            building_coverage_ratio=70.0,  # Exceeds limit
            bcr_limit=50.0,
            height=40.0,
            height_limit=30.0  # Height violation
        )
        
        assert assessment.zoning_compliance_risk > 0.5
        assert assessment.overall_legal_risk > 0.4
    
    def test_property_rights_risk(self, risk_engine):
        """Test property rights risk"""
        assessment = risk_engine.assess_legal_risks(
            zone_type="주거지역",
            floor_area_ratio=200.0,
            far_limit=250.0,
            building_coverage_ratio=50.0,
            bcr_limit=60.0,
            height=30.0,
            title_status="DISPUTED",
            neighbor_agreements=False
        )
        
        assert assessment.property_rights_risk > 0.7
        assert assessment.neighbor_dispute_risk > 0.5
    
    def test_permit_approval_risk(self, risk_engine):
        """Test permit approval risk calculation"""
        assessment = risk_engine.assess_legal_risks(
            zone_type="주거지역",
            floor_area_ratio=250.0,
            far_limit=250.0,
            building_coverage_ratio=60.0,
            bcr_limit=60.0,
            height=35.0,
            environmental_impact="HIGH"
        )
        
        assert assessment.permit_approval_risk > 0.2


class TestComprehensiveRiskProfile:
    """Test comprehensive risk profiling"""
    
    def test_risk_profile_generation(self, risk_engine):
        """Test comprehensive risk profile generation"""
        design = risk_engine.assess_design_risks(
            land_area=660.0,
            floors=10,
            unit_count=33,
            floor_area_ratio=200.0,
            building_coverage_ratio=60.0
        )
        
        legal = risk_engine.assess_legal_risks(
            zone_type="주거지역",
            floor_area_ratio=200.0,
            far_limit=250.0,
            building_coverage_ratio=60.0,
            bcr_limit=60.0,
            height=30.0
        )
        
        profile = risk_engine.generate_comprehensive_risk_profile(
            design_assessment=design,
            legal_assessment=legal,
            financial_risk=0.3,
            construction_risk=0.2,
            market_risk=0.2
        )
        
        assert isinstance(profile, ComprehensiveRiskProfile)
        assert 0 <= profile.total_risk_score <= 1.0
        assert len(profile.risk_distribution) == 5
        assert profile.project_risk_level in list(RiskLevel)
        assert len(profile.investment_recommendation) > 0
    
    def test_high_risk_profile(self, risk_engine):
        """Test high-risk profile generation"""
        design = risk_engine.assess_design_risks(
            land_area=200.0,
            floors=20,
            unit_count=80,
            floor_area_ratio=400.0,
            building_coverage_ratio=80.0,
            sunlight_compliant=False,
            parking_ratio=0.5
        )
        
        legal = risk_engine.assess_legal_risks(
            zone_type="주거지역",
            floor_area_ratio=400.0,
            far_limit=200.0,
            building_coverage_ratio=80.0,
            bcr_limit=50.0,
            height=60.0,
            height_limit=30.0,
            title_status="DISPUTED"
        )
        
        profile = risk_engine.generate_comprehensive_risk_profile(
            design_assessment=design,
            legal_assessment=legal,
            financial_risk=0.7,
            construction_risk=0.6,
            market_risk=0.5
        )
        
        assert profile.total_risk_score > 0.5
        assert len(profile.high_priority_risks) > 0  # High risks instead of critical
        assert "CAUTION" in profile.investment_recommendation.upper() or "NOT RECOMMENDED" in profile.investment_recommendation.upper()
    
    def test_mitigation_plan(self, risk_engine):
        """Test mitigation plan generation"""
        design = risk_engine.assess_design_risks(
            land_area=660.0,
            floors=10,
            unit_count=33,
            floor_area_ratio=200.0,
            building_coverage_ratio=60.0
        )
        
        legal = risk_engine.assess_legal_risks(
            zone_type="주거지역",
            floor_area_ratio=200.0,
            far_limit=250.0,
            building_coverage_ratio=60.0,
            bcr_limit=60.0,
            height=30.0
        )
        
        profile = risk_engine.generate_comprehensive_risk_profile(
            design_assessment=design,
            legal_assessment=legal
        )
        
        assert "immediate_actions" in profile.risk_mitigation_plan
        assert "short_term" in profile.risk_mitigation_plan
        assert "long_term" in profile.risk_mitigation_plan
        assert profile.estimated_mitigation_cost >= 0


class TestRiskLevelClassification:
    """Test risk level classification"""
    
    def test_risk_level_thresholds(self, risk_engine):
        """Test risk level classification thresholds"""
        assert risk_engine._classify_risk_level(0.9) == RiskLevel.CRITICAL
        assert risk_engine._classify_risk_level(0.6) == RiskLevel.HIGH
        assert risk_engine._classify_risk_level(0.4) == RiskLevel.MEDIUM
        assert risk_engine._classify_risk_level(0.2) == RiskLevel.LOW
        assert risk_engine._classify_risk_level(0.05) == RiskLevel.MINIMAL


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_minimal_risk_scenario(self, risk_engine):
        """Test minimal risk scenario"""
        design = risk_engine.assess_design_risks(
            land_area=1000.0,
            floors=5,
            unit_count=20,
            floor_area_ratio=150.0,
            building_coverage_ratio=40.0,
            sunlight_compliant=True,
            parking_ratio=1.2
        )
        
        legal = risk_engine.assess_legal_risks(
            zone_type="주거지역",
            floor_area_ratio=150.0,
            far_limit=200.0,
            building_coverage_ratio=40.0,
            bcr_limit=60.0,
            height=15.0,
            height_limit=30.0,
            environmental_impact="MINIMAL",
            title_status="CLEAR",
            neighbor_agreements=True
        )
        
        profile = risk_engine.generate_comprehensive_risk_profile(
            design_assessment=design,
            legal_assessment=legal,
            financial_risk=0.1,
            construction_risk=0.1,
            market_risk=0.1
        )
        
        assert profile.project_risk_level in [RiskLevel.LOW, RiskLevel.MINIMAL]
        assert "RECOMMENDED" in profile.investment_recommendation.upper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
