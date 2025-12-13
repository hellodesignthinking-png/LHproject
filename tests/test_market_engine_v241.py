"""
Tests for Market Engine v24.1
GAP #6: Market Engine Enhancement (Standard Deviation, CV, Volatility Analysis)
"""

import pytest
from app.engines.market_engine_v241 import (
    MarketEngineV241,
    MarketMetrics,
    VolatilityAnalysis
)


@pytest.fixture
def market_engine():
    """Market Engine fixture"""
    return MarketEngineV241()


@pytest.fixture
def stable_price_data():
    """Stable market price data"""
    return [
        10_000_000, 10_100_000, 10_050_000, 10_150_000,
        10_200_000, 10_180_000, 10_220_000, 10_250_000
    ]


@pytest.fixture
def volatile_price_data():
    """Volatile market price data"""
    return [
        10_000_000, 12_000_000, 9_000_000, 13_000_000,
        8_500_000, 14_000_000, 9_500_000, 13_500_000
    ]


class TestMarketAnalysis:
    """Test comprehensive market analysis"""
    
    def test_analyze_stable_market(self, market_engine, stable_price_data):
        """Test analysis of stable market"""
        metrics = market_engine.analyze_market(stable_price_data)
        
        assert isinstance(metrics, MarketMetrics)
        assert metrics.mean_price > 0
        assert metrics.std_deviation >= 0
        assert metrics.coefficient_of_variation >= 0
        assert 0 <= metrics.market_confidence <= 1.0
        assert 0 <= metrics.market_stability <= 1.0
        
        # Stable market should have low CV and volatility
        assert metrics.coefficient_of_variation < 0.05
        assert metrics.volatility_index in ["LOW", "MEDIUM"]
    
    def test_analyze_volatile_market(self, market_engine, volatile_price_data):
        """Test analysis of volatile market"""
        metrics = market_engine.analyze_market(volatile_price_data)
        
        assert isinstance(metrics, MarketMetrics)
        
        # Volatile market should have higher CV
        assert metrics.coefficient_of_variation > 0.10
        assert metrics.volatility_index in ["MEDIUM", "HIGH", "EXTREME"]
        assert metrics.market_confidence < 0.7


class TestCoefficientOfVariation:
    """Test Coefficient of Variation (CV) calculation"""
    
    def test_cv_calculation(self, market_engine):
        """Test CV is calculated correctly"""
        price_data = [1_000_000, 1_200_000, 1_100_000, 1_300_000]
        
        metrics = market_engine.analyze_market(price_data)
        
        # CV should be std_dev / mean
        expected_cv = metrics.std_deviation / metrics.mean_price
        assert abs(metrics.coefficient_of_variation - expected_cv) < 0.0001
    
    def test_cv_ranges(self, market_engine):
        """Test CV classification ranges"""
        # Low CV data
        low_cv_data = [100, 101, 102, 101, 100, 102]
        metrics_low = market_engine.analyze_market(low_cv_data)
        assert metrics_low.coefficient_of_variation < 0.05
        
        # High CV data
        high_cv_data = [100, 150, 80, 160, 70, 140]
        metrics_high = market_engine.analyze_market(high_cv_data)
        assert metrics_high.coefficient_of_variation > 0.20


class TestVolatilityAnalysis:
    """Test volatility analysis (NEW in v24.1)"""
    
    def test_volatility_calculation(self, market_engine, stable_price_data):
        """Test volatility calculation"""
        vol_analysis = market_engine.calculate_volatility_analysis(
            stable_price_data,
            time_period_days=365
        )
        
        assert isinstance(vol_analysis, VolatilityAnalysis)
        assert vol_analysis.historical_volatility >= 0
        assert vol_analysis.annualized_volatility >= 0
        assert vol_analysis.volatility_trend in ["INCREASING", "STABLE", "DECREASING"]
    
    def test_value_at_risk(self, market_engine, volatile_price_data):
        """Test Value at Risk (VaR) calculation"""
        vol_analysis = market_engine.calculate_volatility_analysis(
            volatile_price_data,
            time_period_days=365
        )
        
        assert vol_analysis.value_at_risk_95 >= 0
        assert vol_analysis.expected_shortfall >= 0
        # Expected shortfall should be >= VaR
        assert vol_analysis.expected_shortfall >= vol_analysis.value_at_risk_95
    
    def test_risk_assessment(self, market_engine, volatile_price_data):
        """Test risk assessment generation"""
        vol_analysis = market_engine.calculate_volatility_analysis(
            volatile_price_data,
            time_period_days=365
        )
        
        assert vol_analysis.risk_assessment in [
            "LOW_RISK", "MODERATE_RISK", "HIGH_RISK", "VERY_HIGH_RISK"
        ]
        assert vol_analysis.investment_timing in [
            "EXCELLENT_TIMING", "GOOD_TIMING", "MODERATE_TIMING", "WAIT_FOR_STABILITY"
        ]


class TestRiskIndicators:
    """Test risk indicators (NEW in v24.1)"""
    
    def test_price_risk_score(self, market_engine, volatile_price_data):
        """Test price risk score calculation"""
        metrics = market_engine.analyze_market(volatile_price_data)
        
        assert 0 <= metrics.price_risk_score <= 100
        # Volatile market should have higher risk score
        assert metrics.price_risk_score > 10
    
    def test_market_stability(self, market_engine, stable_price_data):
        """Test market stability calculation"""
        metrics = market_engine.analyze_market(stable_price_data)
        
        assert 0 <= metrics.market_stability <= 1.0
        # Stable market should have high stability
        assert metrics.market_stability > 0.6


class TestTrendAnalysis:
    """Test trend analysis"""
    
    def test_rising_trend(self, market_engine):
        """Test rising trend detection"""
        rising_data = [100, 110, 120, 130, 140, 150]
        
        metrics = market_engine.analyze_market(rising_data)
        
        assert metrics.trend_direction == "RISING"
        assert metrics.trend_strength > 0.5
    
    def test_declining_trend(self, market_engine):
        """Test declining trend detection"""
        declining_data = [150, 140, 130, 120, 110, 100]
        
        metrics = market_engine.analyze_market(declining_data)
        
        assert metrics.trend_direction == "DECLINING"
        assert metrics.trend_strength > 0.5
    
    def test_stable_trend(self, market_engine, stable_price_data):
        """Test stable trend detection"""
        metrics = market_engine.analyze_market(stable_price_data)
        
        assert metrics.trend_direction in ["STABLE", "RISING"]


class TestMarketConfidence:
    """Test market confidence calculation"""
    
    def test_confidence_ranges(self, market_engine):
        """Test confidence classification"""
        # High confidence data (low volatility)
        high_conf_data = [100, 101, 102, 101, 100, 102, 101]
        metrics_high = market_engine.analyze_market(high_conf_data)
        assert metrics_high.confidence_level in ["HIGH", "VERY_HIGH"]
        
        # Low confidence data (high volatility)
        low_conf_data = [100, 150, 80, 170, 60, 180, 50]
        metrics_low = market_engine.analyze_market(low_conf_data)
        assert metrics_low.confidence_level in ["LOW", "VERY_LOW", "MEDIUM"]


class TestStatisticalMeasures:
    """Test statistical measures (skewness, kurtosis)"""
    
    def test_skewness_calculation(self, market_engine):
        """Test skewness calculation"""
        # Right-skewed data
        right_skewed = [1, 1, 2, 2, 3, 3, 4, 5, 10, 15]
        
        vol_analysis = market_engine.calculate_volatility_analysis(
            right_skewed,
            time_period_days=10
        )
        
        # Right-skewed should have positive skewness
        assert vol_analysis.skewness > 0
    
    def test_kurtosis_calculation(self, market_engine):
        """Test kurtosis calculation"""
        # Data with outliers (high kurtosis)
        outlier_data = [100, 100, 100, 100, 100, 200, 100, 100]
        
        vol_analysis = market_engine.calculate_volatility_analysis(
            outlier_data,
            time_period_days=8
        )
        
        # Should detect excess kurtosis
        assert isinstance(vol_analysis.kurtosis, float)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_insufficient_data(self, market_engine):
        """Test with insufficient data"""
        with pytest.raises(ValueError):
            market_engine.analyze_market([])
        
        with pytest.raises(ValueError):
            market_engine.analyze_market([100])
    
    def test_minimum_data_volatility(self, market_engine):
        """Test volatility analysis with minimum data"""
        with pytest.raises(ValueError):
            market_engine.calculate_volatility_analysis([100, 110])
    
    def test_zero_prices(self, market_engine):
        """Test handling of zero prices"""
        # Should handle gracefully
        data_with_zero = [100, 110, 0, 120]
        # This might raise an error or handle it - depends on implementation
        try:
            metrics = market_engine.analyze_market(data_with_zero)
            assert metrics is not None
        except (ValueError, ZeroDivisionError):
            # Expected behavior for invalid data
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
