"""
ZeroSite v24.1 - Alias Engine Tests
Tests for expanded alias system (250+ aliases)

Author: ZeroSite Development Team
Version: v24.1.0
Created: 2025-12-12
"""

import pytest
from app.engines.alias_engine_v241 import AliasEngineV241


class TestAliasEngineBasics:
    """Basic Alias Engine functionality tests"""
    
    @pytest.fixture
    def engine(self):
        """Create alias engine instance"""
        return AliasEngineV241()
    
    def test_initialization(self, engine):
        """Test engine initializes correctly"""
        assert engine.version == "24.1.0"
        assert engine.aliases is not None
        assert len(engine.aliases) >= 250
    
    def test_get_alias(self, engine):
        """Test getting alias value"""
        # Test common aliases
        total_gfa = engine.get("total_gfa")
        assert total_gfa is not None
        
        far_legal = engine.get("far_legal")
        assert far_legal is not None
    
    def test_get_with_default(self, engine):
        """Test get with default value"""
        result = engine.get("nonexistent_alias", "default_value")
        assert result == "default_value"


class TestCurrencyFormatting:
    """Tests for Korean currency formatting"""
    
    @pytest.fixture
    def engine(self):
        return AliasEngineV241()
    
    def test_format_in_eok(self, engine):
        """Test formatting in 억원 (hundred million)"""
        # 500억원
        formatted = engine.format_value(50000000000, "currency")
        assert "500" in formatted
        assert "억" in formatted
    
    def test_format_in_man(self, engine):
        """Test formatting in 만원 (ten thousand)"""
        # 5000만원
        formatted = engine.format_value(50000000, "currency")
        assert "5000" in formatted or "5,000" in formatted
        assert "만" in formatted
    
    def test_format_in_jo(self, engine):
        """Test formatting in 조원 (trillion)"""
        # 2조원
        formatted = engine.format_value(2000000000000, "currency")
        assert "2" in formatted
        assert "조" in formatted or "兆" in formatted
    
    def test_format_zero(self, engine):
        """Test formatting zero value"""
        formatted = engine.format_value(0, "currency")
        assert formatted is not None
        assert "0" in formatted


class TestUnitConversions:
    """Tests for unit conversion system"""
    
    @pytest.fixture
    def engine(self):
        return AliasEngineV241()
    
    def test_sqm_to_pyeong(self, engine):
        """Test square meter to pyeong conversion"""
        # 100㎡ ≈ 30.25평
        result = engine.convert_unit(100, "sqm_to_pyeong")
        assert 30 < result < 31
    
    def test_pyeong_to_sqm(self, engine):
        """Test pyeong to square meter conversion"""
        # 30평 ≈ 99㎡
        result = engine.convert_unit(30, "pyeong_to_sqm")
        assert 98 < result < 100
    
    def test_meter_to_foot(self, engine):
        """Test meter to foot conversion"""
        # 10m ≈ 32.8 feet
        result = engine.convert_unit(10, "m_to_ft")
        assert 32 < result < 33
    
    def test_invalid_conversion_type(self, engine):
        """Test handling of invalid conversion type"""
        with pytest.raises((ValueError, KeyError)):
            engine.convert_unit(100, "invalid_type")


class TestAliasCategories:
    """Tests for different alias categories"""
    
    @pytest.fixture
    def engine(self):
        return AliasEngineV241()
    
    def test_land_information_aliases(self, engine):
        """Test land information aliases (30+ aliases)"""
        land_aliases = [
            "land_area",
            "land_area_pyeong",
            "land_price",
            "land_price_per_sqm",
            "land_use_type",
            "cadastral_area"
        ]
        
        for alias in land_aliases:
            result = engine.get(alias)
            # Should have a mapping (not None)
            assert result is not None or engine.get(alias, "NOT_FOUND") != "NOT_FOUND"
    
    def test_zoning_aliases(self, engine):
        """Test zoning & regulations aliases (40+ aliases)"""
        zoning_aliases = [
            "zone_type",
            "far_legal",
            "far_final",
            "bcr_legal",
            "height_limit",
            "setback_front",
            "setback_side"
        ]
        
        for alias in zoning_aliases:
            result = engine.get(alias)
            assert result is not None or engine.get(alias, "NOT_FOUND") != "NOT_FOUND"
    
    def test_building_capacity_aliases(self, engine):
        """Test building capacity aliases (50+ aliases)"""
        capacity_aliases = [
            "total_gfa",
            "building_coverage",
            "floor_count",
            "unit_count",
            "parking_spaces"
        ]
        
        for alias in capacity_aliases:
            result = engine.get(alias)
            assert result is not None or engine.get(alias, "NOT_FOUND") != "NOT_FOUND"
    
    def test_financial_aliases(self, engine):
        """Test financial aliases (50+ aliases)"""
        financial_aliases = [
            "construction_cost",
            "total_revenue",
            "net_profit",
            "roi",
            "irr",
            "npv",
            "payback_period"
        ]
        
        for alias in financial_aliases:
            result = engine.get(alias)
            assert result is not None or engine.get(alias, "NOT_FOUND") != "NOT_FOUND"
    
    def test_market_analysis_aliases(self, engine):
        """Test market analysis aliases (30+ aliases)"""
        market_aliases = [
            "market_price",
            "price_volatility",
            "supply_demand_ratio",
            "market_trend"
        ]
        
        for alias in market_aliases:
            result = engine.get(alias)
            assert result is not None or engine.get(alias, "NOT_FOUND") != "NOT_FOUND"
    
    def test_risk_compliance_aliases(self, engine):
        """Test risk & compliance aliases (20+ aliases)"""
        risk_aliases = [
            "risk_level",
            "design_risk",
            "legal_risk",
            "financial_risk"
        ]
        
        for alias in risk_aliases:
            result = engine.get(alias)
            assert result is not None or engine.get(alias, "NOT_FOUND") != "NOT_FOUND"


class TestTemplateSubstitution:
    """Tests for template variable substitution"""
    
    @pytest.fixture
    def engine(self):
        return AliasEngineV241()
    
    def test_simple_substitution(self, engine):
        """Test simple variable substitution"""
        template = "토지면적: {{land_area}}㎡"
        data = {"land_area": 1000}
        
        result = engine.substitute_template(template, data)
        assert "1000" in result
        assert "㎡" in result
    
    def test_nested_data_access(self, engine):
        """Test nested data access with dot notation"""
        template = "ROI: {{financial.roi}}%"
        data = {
            "financial": {
                "roi": 15.5
            }
        }
        
        result = engine.substitute_template(template, data)
        assert "15.5" in result
    
    def test_multiple_substitutions(self, engine):
        """Test multiple variable substitutions"""
        template = "{{zone_type}}, 용적률: {{far}}%, 건폐율: {{bcr}}%"
        data = {
            "zone_type": "제2종일반주거지역",
            "far": 200,
            "bcr": 60
        }
        
        result = engine.substitute_template(template, data)
        assert "제2종일반주거지역" in result
        assert "200" in result
        assert "60" in result


class TestPerformance:
    """Performance tests for Alias Engine"""
    
    @pytest.fixture
    def engine(self):
        return AliasEngineV241()
    
    def test_lookup_performance(self, engine):
        """Test alias lookup performance"""
        import time
        
        start = time.time()
        
        # Perform 1000 lookups
        for _ in range(1000):
            engine.get("total_gfa")
            engine.get("far_legal")
            engine.get("construction_cost")
        
        elapsed = time.time() - start
        
        # Should complete in under 0.1 seconds
        assert elapsed < 0.1
    
    def test_formatting_performance(self, engine):
        """Test formatting performance"""
        import time
        
        start = time.time()
        
        # Format 1000 values
        for i in range(1000):
            engine.format_value(50000000 * i, "currency")
        
        elapsed = time.time() - start
        
        # Should complete in under 1 second
        assert elapsed < 1.0


class TestEdgeCases:
    """Edge case tests"""
    
    @pytest.fixture
    def engine(self):
        return AliasEngineV241()
    
    def test_very_large_numbers(self, engine):
        """Test formatting very large numbers"""
        # 100조원
        result = engine.format_value(100000000000000, "currency")
        assert result is not None
        assert len(result) > 0
    
    def test_very_small_numbers(self, engine):
        """Test formatting very small numbers"""
        # 1만원
        result = engine.format_value(10000, "currency")
        assert result is not None
        assert "1" in result
        assert "만" in result
    
    def test_decimal_formatting(self, engine):
        """Test formatting decimal values"""
        # 5.5억원
        result = engine.format_value(550000000, "currency")
        assert result is not None
        # Should handle decimals appropriately
    
    def test_negative_values(self, engine):
        """Test handling negative values"""
        # -5억원 (손실)
        result = engine.format_value(-500000000, "currency")
        assert result is not None
        assert "-" in result or "손실" in result or "마이너스" in result


class TestAliasExpansion:
    """Tests to verify 250+ alias expansion"""
    
    @pytest.fixture
    def engine(self):
        return AliasEngineV241()
    
    def test_alias_count(self, engine):
        """Test that we have 250+ aliases"""
        assert len(engine.aliases) >= 250
    
    def test_new_aliases_v241(self, engine):
        """Test new aliases added in v24.1"""
        # These should be new in v24.1
        new_aliases = [
            "carbon_footprint",
            "social_value_score",
            "market_competitiveness",
            "design_risk_score",
            "legal_risk_score",
            "comprehensive_risk_level"
        ]
        
        for alias in new_aliases:
            result = engine.get(alias)
            # Should exist (not return default)
            assert result is not None or engine.get(alias, "MISSING") != "MISSING"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
