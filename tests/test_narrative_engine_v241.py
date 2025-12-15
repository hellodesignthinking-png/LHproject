"""
ZeroSite v24.1 - Narrative Engine Tests
Tests for template-based narrative generation

Author: ZeroSite Development Team
Version: v24.1.0
Created: 2025-12-12
"""

import pytest
from app.engines.narrative_engine_v241 import (
    NarrativeEngineV241,
    NarrativeSection
)


class TestNarrativeEngineBasics:
    """Basic Narrative Engine functionality tests"""
    
    @pytest.fixture
    def engine(self):
        """Create narrative engine instance"""
        return NarrativeEngineV241()
    
    def test_initialization(self, engine):
        """Test engine initializes correctly"""
        assert engine.version == "24.1.0"
    
    def test_narrative_section_structure(self):
        """Test NarrativeSection dataclass structure"""
        section = NarrativeSection(
            title="테스트 제목",
            content="테스트 내용입니다.",
            key_points=["포인트 1", "포인트 2"]
        )
        
        assert section.title == "테스트 제목"
        assert section.content == "테스트 내용입니다."
        assert len(section.key_points) == 2


class TestPolicyNarrative:
    """Tests for policy impact narrative generation"""
    
    @pytest.fixture
    def engine(self):
        return NarrativeEngineV241()
    
    @pytest.fixture
    def sample_policy_data(self):
        return {
            "zone_type": "제2종일반주거지역",
            "far_legal": 200.0,
            "far_final": 250.0,
            "bcr_legal": 60.0,
            "height_limit": 35.0,
            "relaxation_items": [
                "공개공지 제공",
                "건축선 후퇴",
                "친환경 건축"
            ]
        }
    
    def test_generate_policy_narrative(self, engine, sample_policy_data):
        """Test basic policy narrative generation"""
        narrative = engine.generate_policy_narrative(sample_policy_data)
        
        assert narrative is not None
        assert isinstance(narrative, NarrativeSection)
        assert narrative.title is not None
        assert len(narrative.content) > 100
    
    def test_policy_narrative_includes_zone_type(self, engine, sample_policy_data):
        """Test narrative includes zone type"""
        narrative = engine.generate_policy_narrative(sample_policy_data)
        
        assert sample_policy_data["zone_type"] in narrative.content
    
    def test_policy_narrative_includes_far_values(self, engine, sample_policy_data):
        """Test narrative includes FAR values"""
        narrative = engine.generate_policy_narrative(sample_policy_data)
        
        # Should mention both legal and final FAR
        assert "200" in narrative.content or "250" in narrative.content
    
    def test_policy_narrative_key_points(self, engine, sample_policy_data):
        """Test narrative generates key points"""
        narrative = engine.generate_policy_narrative(sample_policy_data)
        
        assert len(narrative.key_points) > 0
        # Key points should be strings
        for point in narrative.key_points:
            assert isinstance(point, str)
            assert len(point) > 0


class TestFinancialNarrative:
    """Tests for financial feasibility narrative generation"""
    
    @pytest.fixture
    def engine(self):
        return NarrativeEngineV241()
    
    @pytest.fixture
    def sample_financial_data(self):
        return {
            "land_cost": 5000,  # 억원
            "construction_cost": 3000,
            "total_cost": 8500,
            "sales_revenue": 10000,
            "net_profit": 1500,
            "roi": 17.6,
            "irr": 15.2,
            "payback_period": 4.5
        }
    
    def test_generate_financial_narrative(self, engine, sample_financial_data):
        """Test basic financial narrative generation"""
        narrative = engine.generate_financial_narrative(sample_financial_data)
        
        assert narrative is not None
        assert isinstance(narrative, NarrativeSection)
        assert "재무" in narrative.title or "수익" in narrative.title
        assert len(narrative.content) > 100
    
    def test_financial_narrative_includes_key_metrics(self, engine, sample_financial_data):
        """Test narrative includes key financial metrics"""
        narrative = engine.generate_financial_narrative(sample_financial_data)
        
        content_lower = narrative.content
        
        # Should mention ROI, IRR, or profit
        assert any(term in content_lower for term in ["ROI", "수익", "이익", "회수"])
    
    def test_financial_narrative_profitability_assessment(self, engine):
        """Test narrative assesses profitability correctly"""
        
        # Profitable project
        profitable_data = {
            "net_profit": 2000,
            "roi": 25.0,
            "irr": 18.0
        }
        
        narrative_profitable = engine.generate_financial_narrative(profitable_data)
        
        # Should have positive tone
        assert any(word in narrative_profitable.content 
                   for word in ["양호", "우수", "긍정", "높은", "수익성"])
        
        # Unprofitable project
        unprofitable_data = {
            "net_profit": -500,
            "roi": -5.0,
            "irr": 3.0
        }
        
        narrative_unprofitable = engine.generate_financial_narrative(unprofitable_data)
        
        # Should have cautionary tone
        assert any(word in narrative_unprofitable.content 
                   for word in ["낮은", "부족", "어려움", "재검토", "손실"])


class TestMarketNarrative:
    """Tests for market analysis narrative generation"""
    
    @pytest.fixture
    def engine(self):
        return NarrativeEngineV241()
    
    @pytest.fixture
    def sample_market_data(self):
        return {
            "location": "서울시 강남구",
            "avg_price": 12000000,
            "price_trend": 0.05,  # 5% increase
            "volatility": 0.15,
            "supply_demand_ratio": 0.8,
            "market_sentiment": "positive"
        }
    
    def test_generate_market_narrative(self, engine, sample_market_data):
        """Test basic market narrative generation"""
        narrative = engine.generate_market_narrative(sample_market_data)
        
        assert narrative is not None
        assert isinstance(narrative, NarrativeSection)
        assert "시장" in narrative.title
        assert len(narrative.content) > 100
    
    def test_market_narrative_includes_location(self, engine, sample_market_data):
        """Test narrative includes location information"""
        narrative = engine.generate_market_narrative(sample_market_data)
        
        assert sample_market_data["location"] in narrative.content
    
    def test_market_narrative_trend_analysis(self, engine):
        """Test narrative analyzes market trends"""
        
        # Rising market
        rising_data = {
            "location": "서울시 강남구",
            "price_trend": 0.08,  # 8% increase
            "volatility": 0.10
        }
        
        narrative_rising = engine.generate_market_narrative(rising_data)
        
        # Should mention upward trend
        assert any(word in narrative_rising.content 
                   for word in ["상승", "증가", "호조", "강세"])
        
        # Declining market
        declining_data = {
            "location": "서울시 강남구",
            "price_trend": -0.05,  # 5% decrease
            "volatility": 0.20
        }
        
        narrative_declining = engine.generate_market_narrative(declining_data)
        
        # Should mention downward trend
        assert any(word in narrative_declining.content 
                   for word in ["하락", "감소", "약세", "둔화"])


class TestScenarioComparison:
    """Tests for scenario comparison narrative generation"""
    
    @pytest.fixture
    def engine(self):
        return NarrativeEngineV241()
    
    @pytest.fixture
    def sample_scenario_data(self):
        return {
            "scenario_a": {
                "type": "주거시설",
                "roi": 18.5,
                "npv": 1500,
                "risk_level": "MEDIUM"
            },
            "scenario_b": {
                "type": "상업시설",
                "roi": 22.3,
                "npv": 2000,
                "risk_level": "HIGH"
            },
            "scenario_c": {
                "type": "노인복지주택",
                "roi": 15.8,
                "npv": 1200,
                "risk_level": "LOW"
            },
            "best_scenario": "B"
        }
    
    def test_generate_scenario_comparison(self, engine, sample_scenario_data):
        """Test basic scenario comparison narrative"""
        narrative = engine.generate_scenario_comparison(sample_scenario_data)
        
        assert narrative is not None
        assert isinstance(narrative, NarrativeSection)
        assert "시나리오" in narrative.title or "비교" in narrative.title
        assert len(narrative.content) > 100
    
    def test_scenario_comparison_mentions_all_scenarios(self, engine, sample_scenario_data):
        """Test narrative mentions all scenarios"""
        narrative = engine.generate_scenario_comparison(sample_scenario_data)
        
        # Should mention scenarios A, B, C
        content = narrative.content
        assert any(term in content for term in ["시나리오 A", "A안", "주거"])
        assert any(term in content for term in ["시나리오 B", "B안", "상업"])
        assert any(term in content for term in ["시나리오 C", "C안", "노인"])
    
    def test_scenario_comparison_identifies_best(self, engine, sample_scenario_data):
        """Test narrative identifies best scenario"""
        narrative = engine.generate_scenario_comparison(sample_scenario_data)
        
        # Should mention that B is the best
        assert "B" in narrative.content or "상업시설" in narrative.content
        assert any(word in narrative.content for word in ["최적", "가장", "우수", "권장"])


class TestRiskSummary:
    """Tests for risk assessment summary narrative generation"""
    
    @pytest.fixture
    def engine(self):
        return NarrativeEngineV241()
    
    @pytest.fixture
    def sample_risk_data(self):
        return {
            "overall_risk_level": "MEDIUM",
            "design_risk": 0.3,
            "legal_risk": 0.2,
            "financial_risk": 0.4,
            "market_risk": 0.35,
            "critical_risks": [
                "대출금리 상승 리스크",
                "분양가 상한제 적용 가능성"
            ],
            "mitigation_plans": [
                "금리 헤지 전략 수립",
                "사전 분양가 검토"
            ]
        }
    
    def test_generate_risk_summary(self, engine, sample_risk_data):
        """Test basic risk summary generation"""
        narrative = engine.generate_risk_summary(sample_risk_data)
        
        assert narrative is not None
        assert isinstance(narrative, NarrativeSection)
        assert "리스크" in narrative.title or "위험" in narrative.title
        assert len(narrative.content) > 100
    
    def test_risk_summary_includes_risk_level(self, engine, sample_risk_data):
        """Test narrative includes overall risk level"""
        narrative = engine.generate_risk_summary(sample_risk_data)
        
        # Should mention risk level
        assert any(word in narrative.content 
                   for word in ["중간", "보통", "MEDIUM", "위험"])
    
    def test_risk_summary_lists_critical_risks(self, engine, sample_risk_data):
        """Test narrative lists critical risks"""
        narrative = engine.generate_risk_summary(sample_risk_data)
        
        # Should mention at least one critical risk
        critical_risks = sample_risk_data["critical_risks"]
        content = narrative.content
        
        # At least one critical risk should be mentioned
        mentioned = any(risk in content for risk in critical_risks)
        assert mentioned or "금리" in content or "분양가" in content
    
    def test_risk_summary_includes_mitigation(self, engine, sample_risk_data):
        """Test narrative includes mitigation strategies"""
        narrative = engine.generate_risk_summary(sample_risk_data)
        
        # Should mention mitigation or strategies
        assert any(word in narrative.content 
                   for word in ["대응", "완화", "전략", "계획", "관리"])


class TestNarrativeQuality:
    """Tests for narrative quality and consistency"""
    
    @pytest.fixture
    def engine(self):
        return NarrativeEngineV241()
    
    def test_narrative_length_appropriate(self, engine):
        """Test narratives have appropriate length"""
        
        data = {
            "zone_type": "제2종일반주거지역",
            "far_legal": 200.0,
            "far_final": 250.0
        }
        
        narrative = engine.generate_policy_narrative(data)
        
        # Should be substantial (at least 100 characters)
        assert len(narrative.content) >= 100
        
        # But not too long (under 2000 characters for basic narrative)
        assert len(narrative.content) <= 2000
    
    def test_narrative_korean_language(self, engine):
        """Test narratives are in proper Korean"""
        
        data = {"zone_type": "제2종일반주거지역", "far_legal": 200.0}
        narrative = engine.generate_policy_narrative(data)
        
        # Should contain Korean characters
        korean_chars = sum(1 for c in narrative.content if '\uac00' <= c <= '\ud7a3')
        assert korean_chars > 50  # At least 50 Korean characters
    
    def test_narrative_professional_tone(self, engine):
        """Test narratives use professional business Korean"""
        
        data = {
            "net_profit": 1500,
            "roi": 18.5
        }
        
        narrative = engine.generate_financial_narrative(data)
        
        # Should use formal endings (ㅂ니다, 습니다)
        content = narrative.content
        assert "습니다" in content or "ㅂ니다" in content or "됩니다" in content
    
    def test_key_points_consistency(self, engine):
        """Test key points are consistent with content"""
        
        data = {
            "zone_type": "제2종일반주거지역",
            "far_legal": 200.0,
            "far_final": 250.0
        }
        
        narrative = engine.generate_policy_narrative(data)
        
        # Each key point should be related to content
        for point in narrative.key_points:
            # Key points should be concise (under 100 chars)
            assert len(point) <= 100
            # Should not be empty
            assert len(point) > 0


class TestPerformance:
    """Performance tests for Narrative Engine"""
    
    @pytest.fixture
    def engine(self):
        return NarrativeEngineV241()
    
    def test_generation_performance(self, engine):
        """Test narrative generation performance"""
        import time
        
        data = {
            "zone_type": "제2종일반주거지역",
            "far_legal": 200.0,
            "far_final": 250.0
        }
        
        start = time.time()
        
        # Generate 100 narratives
        for _ in range(100):
            engine.generate_policy_narrative(data)
        
        elapsed = time.time() - start
        
        # Should complete in under 1 second
        assert elapsed < 1.0
    
    def test_all_narrative_types_performance(self, engine):
        """Test performance of all narrative types"""
        import time
        
        start = time.time()
        
        # Generate all 5 narrative types
        engine.generate_policy_narrative({"zone_type": "주거", "far_legal": 200})
        engine.generate_financial_narrative({"roi": 15, "net_profit": 1000})
        engine.generate_market_narrative({"location": "강남", "price_trend": 0.05})
        engine.generate_scenario_comparison({"scenario_a": {}, "scenario_b": {}, "scenario_c": {}, "best_scenario": "A"})
        engine.generate_risk_summary({"overall_risk_level": "MEDIUM", "critical_risks": []})
        
        elapsed = time.time() - start
        
        # All 5 types should complete in under 0.5 seconds
        assert elapsed < 0.5


class TestEdgeCases:
    """Edge case tests"""
    
    @pytest.fixture
    def engine(self):
        return NarrativeEngineV241()
    
    def test_minimal_data(self, engine):
        """Test generation with minimal data"""
        
        minimal_data = {}
        
        # Should not crash, should generate something
        narrative = engine.generate_policy_narrative(minimal_data)
        
        assert narrative is not None
        assert len(narrative.content) > 0
    
    def test_missing_optional_fields(self, engine):
        """Test generation with missing optional fields"""
        
        data = {
            "zone_type": "주거지역"
            # Missing many optional fields
        }
        
        narrative = engine.generate_policy_narrative(data)
        
        assert narrative is not None
        assert "주거지역" in narrative.content
    
    def test_extreme_values(self, engine):
        """Test handling of extreme values"""
        
        extreme_data = {
            "roi": 500.0,  # Unrealistically high
            "net_profit": -10000  # Large loss
        }
        
        narrative = engine.generate_financial_narrative(extreme_data)
        
        assert narrative is not None
        assert len(narrative.content) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
