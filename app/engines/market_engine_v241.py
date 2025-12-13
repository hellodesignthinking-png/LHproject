"""
ZeroSite v24.1 - Market Engine Enhancement
GAP #6: Market Engine Enhancement (Standard Deviation, CV, Volatility Analysis)

Author: ZeroSite Development Team
Version: v24.1.0
Created: 2025-12-12
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import statistics
import math


@dataclass
class MarketMetrics:
    """Market analysis metrics with statistical measures"""
    
    # Price Statistics
    mean_price: float
    median_price: float
    std_deviation: float
    coefficient_of_variation: float  # NEW in v24.1
    
    # Volatility Analysis (NEW in v24.1)
    price_volatility: float
    volatility_index: str  # "LOW", "MEDIUM", "HIGH", "EXTREME"
    
    # Trend Analysis
    trend_direction: str  # "RISING", "STABLE", "DECLINING"
    trend_strength: float  # 0.0 to 1.0
    
    # Market Confidence
    market_confidence: float  # 0.0 to 1.0
    confidence_level: str  # "VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"
    
    # Risk Indicators (NEW in v24.1)
    price_risk_score: float  # 0.0 to 100.0
    market_stability: float  # 0.0 to 1.0


@dataclass
class VolatilityAnalysis:
    """Detailed volatility analysis (NEW in v24.1)"""
    
    historical_volatility: float
    annualized_volatility: float
    volatility_trend: str  # "INCREASING", "STABLE", "DECREASING"
    
    # Risk Metrics
    value_at_risk_95: float  # 95% VaR
    expected_shortfall: float  # Conditional VaR
    
    # Statistical Measures
    skewness: float
    kurtosis: float
    
    # Recommendations
    risk_assessment: str
    investment_timing: str


class MarketEngineV241:
    """
    Enhanced Market Analysis Engine for ZeroSite v24.1
    
    NEW FEATURES (GAP #6):
    - Standard Deviation & Coefficient of Variation
    - Price Volatility Analysis
    - Risk-Adjusted Market Metrics
    
    Features:
    - Statistical price analysis with CV
    - Historical volatility calculation
    - Risk-adjusted confidence scoring
    - Market stability assessment
    """
    
    def __init__(self):
        """Initialize Market Engine v24.1"""
        self.version = "24.1.0"
        
        # Volatility thresholds (configurable)
        self.volatility_thresholds = {
            "LOW": 0.10,      # < 10%
            "MEDIUM": 0.20,   # 10-20%
            "HIGH": 0.35,     # 20-35%
            "EXTREME": 1.0    # > 35%
        }
        
        # CV interpretation thresholds
        self.cv_thresholds = {
            "VERY_LOW": 0.15,
            "LOW": 0.30,
            "MEDIUM": 0.50,
            "HIGH": 1.0
        }
    
    def analyze_market(
        self,
        price_data: List[float],
        time_period_days: int = 365
    ) -> MarketMetrics:
        """
        Comprehensive market analysis with statistical measures
        
        Args:
            price_data: List of historical prices (KRW/㎡)
            time_period_days: Time period for analysis
            
        Returns:
            MarketMetrics with enhanced statistical analysis
        """
        if not price_data or len(price_data) < 2:
            raise ValueError("Insufficient price data for analysis")
        
        # Basic statistics
        mean_price = statistics.mean(price_data)
        median_price = statistics.median(price_data)
        std_dev = statistics.stdev(price_data) if len(price_data) > 1 else 0.0
        
        # NEW: Coefficient of Variation (CV) - GAP #6
        cv = (std_dev / mean_price) if mean_price > 0 else 0.0
        
        # NEW: Volatility Analysis - GAP #6
        volatility = self._calculate_volatility(price_data, time_period_days)
        volatility_index = self._classify_volatility(volatility)
        
        # Trend analysis
        trend_dir, trend_strength = self._analyze_trend(price_data)
        
        # Market confidence (adjusted for volatility)
        confidence = self._calculate_market_confidence(
            cv, volatility, trend_strength
        )
        confidence_level = self._classify_confidence(confidence)
        
        # NEW: Risk indicators - GAP #6
        risk_score = self._calculate_price_risk(cv, volatility)
        stability = self._calculate_market_stability(volatility, cv)
        
        return MarketMetrics(
            mean_price=mean_price,
            median_price=median_price,
            std_deviation=std_dev,
            coefficient_of_variation=cv,
            price_volatility=volatility,
            volatility_index=volatility_index,
            trend_direction=trend_dir,
            trend_strength=trend_strength,
            market_confidence=confidence,
            confidence_level=confidence_level,
            price_risk_score=risk_score,
            market_stability=stability
        )
    
    def calculate_volatility_analysis(
        self,
        price_data: List[float],
        time_period_days: int = 365
    ) -> VolatilityAnalysis:
        """
        Detailed volatility analysis (NEW in v24.1)
        
        Args:
            price_data: Historical price data
            time_period_days: Analysis time period
            
        Returns:
            Comprehensive volatility analysis
        """
        if len(price_data) < 3:
            raise ValueError("Need at least 3 data points for volatility analysis")
        
        # Calculate returns
        returns = self._calculate_returns(price_data)
        
        # Historical volatility
        hist_vol = statistics.stdev(returns) if len(returns) > 1 else 0.0
        
        # Annualized volatility
        periods_per_year = 365.0 / time_period_days if time_period_days > 0 else 1.0
        annual_vol = hist_vol * math.sqrt(periods_per_year)
        
        # Volatility trend
        vol_trend = self._analyze_volatility_trend(returns)
        
        # Risk metrics
        var_95 = self._calculate_value_at_risk(returns, 0.95)
        expected_shortfall = self._calculate_expected_shortfall(returns, 0.95)
        
        # Statistical measures
        skewness = self._calculate_skewness(returns)
        kurtosis = self._calculate_kurtosis(returns)
        
        # Recommendations
        risk_assessment = self._assess_overall_risk(annual_vol, skewness, kurtosis)
        timing = self._recommend_investment_timing(annual_vol, vol_trend)
        
        return VolatilityAnalysis(
            historical_volatility=hist_vol,
            annualized_volatility=annual_vol,
            volatility_trend=vol_trend,
            value_at_risk_95=var_95,
            expected_shortfall=expected_shortfall,
            skewness=skewness,
            kurtosis=kurtosis,
            risk_assessment=risk_assessment,
            investment_timing=timing
        )
    
    def _calculate_volatility(
        self,
        price_data: List[float],
        time_period_days: int
    ) -> float:
        """
        Calculate price volatility
        
        Returns:
            Volatility as decimal (e.g., 0.15 = 15%)
        """
        if len(price_data) < 2:
            return 0.0
        
        returns = self._calculate_returns(price_data)
        
        if not returns:
            return 0.0
        
        # Standard deviation of returns
        std_dev = statistics.stdev(returns) if len(returns) > 1 else 0.0
        
        # Annualize if needed
        periods_per_year = 365.0 / time_period_days if time_period_days > 0 else 1.0
        volatility = std_dev * math.sqrt(periods_per_year)
        
        return volatility
    
    def _calculate_returns(self, price_data: List[float]) -> List[float]:
        """Calculate logarithmic returns"""
        returns = []
        for i in range(1, len(price_data)):
            if price_data[i-1] > 0:
                ret = math.log(price_data[i] / price_data[i-1])
                returns.append(ret)
        return returns
    
    def _classify_volatility(self, volatility: float) -> str:
        """Classify volatility level"""
        if volatility < self.volatility_thresholds["LOW"]:
            return "LOW"
        elif volatility < self.volatility_thresholds["MEDIUM"]:
            return "MEDIUM"
        elif volatility < self.volatility_thresholds["HIGH"]:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _analyze_trend(self, price_data: List[float]) -> Tuple[str, float]:
        """Analyze price trend direction and strength"""
        if len(price_data) < 2:
            return "STABLE", 0.0
        
        # Simple linear regression slope
        n = len(price_data)
        x = list(range(n))
        y = price_data
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0.0
        
        # Normalize slope to strength (0.0 to 1.0)
        strength = min(abs(slope) / (y_mean * 0.001), 1.0) if y_mean > 0 else 0.0
        
        # Direction
        if slope > 0.001 * y_mean:
            direction = "RISING"
        elif slope < -0.001 * y_mean:
            direction = "DECLINING"
        else:
            direction = "STABLE"
        
        return direction, strength
    
    def _calculate_market_confidence(
        self,
        cv: float,
        volatility: float,
        trend_strength: float
    ) -> float:
        """
        Calculate market confidence score (0.0 to 1.0)
        Lower CV and volatility = higher confidence
        """
        # Base confidence from CV (lower is better)
        cv_score = max(0.0, 1.0 - (cv / 0.5))
        
        # Volatility score (lower is better)
        vol_score = max(0.0, 1.0 - (volatility / 0.35))
        
        # Trend strength bonus (stable trend is good)
        trend_bonus = 0.2 * (1.0 - trend_strength)
        
        confidence = (0.4 * cv_score + 0.4 * vol_score + 0.2 * trend_bonus)
        
        return max(0.0, min(1.0, confidence))
    
    def _classify_confidence(self, confidence: float) -> str:
        """Classify confidence level"""
        if confidence >= 0.8:
            return "VERY_HIGH"
        elif confidence >= 0.6:
            return "HIGH"
        elif confidence >= 0.4:
            return "MEDIUM"
        elif confidence >= 0.2:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _calculate_price_risk(self, cv: float, volatility: float) -> float:
        """Calculate price risk score (0.0 to 100.0)"""
        # Higher CV and volatility = higher risk
        cv_risk = min(cv * 100, 50.0)
        vol_risk = min(volatility * 100, 50.0)
        
        return cv_risk + vol_risk
    
    def _calculate_market_stability(self, volatility: float, cv: float) -> float:
        """Calculate market stability (0.0 to 1.0)"""
        # Inverse of risk
        instability = (volatility + cv) / 2.0
        stability = max(0.0, 1.0 - instability)
        
        return stability
    
    def _analyze_volatility_trend(self, returns: List[float]) -> str:
        """Analyze if volatility is increasing or decreasing"""
        if len(returns) < 6:
            return "STABLE"
        
        # Split into two halves
        mid = len(returns) // 2
        first_half = returns[:mid]
        second_half = returns[mid:]
        
        vol_first = statistics.stdev(first_half) if len(first_half) > 1 else 0.0
        vol_second = statistics.stdev(second_half) if len(second_half) > 1 else 0.0
        
        # Compare
        if vol_second > vol_first * 1.15:
            return "INCREASING"
        elif vol_second < vol_first * 0.85:
            return "DECREASING"
        else:
            return "STABLE"
    
    def _calculate_value_at_risk(
        self,
        returns: List[float],
        confidence_level: float
    ) -> float:
        """Calculate Value at Risk (VaR)"""
        if not returns:
            return 0.0
        
        sorted_returns = sorted(returns)
        index = int((1.0 - confidence_level) * len(sorted_returns))
        
        return abs(sorted_returns[index]) if index < len(sorted_returns) else 0.0
    
    def _calculate_expected_shortfall(
        self,
        returns: List[float],
        confidence_level: float
    ) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        if not returns:
            return 0.0
        
        sorted_returns = sorted(returns)
        cutoff_index = int((1.0 - confidence_level) * len(sorted_returns))
        
        tail_returns = sorted_returns[:cutoff_index] if cutoff_index > 0 else [sorted_returns[0]]
        
        return abs(statistics.mean(tail_returns)) if tail_returns else 0.0
    
    def _calculate_skewness(self, returns: List[float]) -> float:
        """Calculate skewness of returns distribution"""
        if len(returns) < 3:
            return 0.0
        
        mean = statistics.mean(returns)
        std_dev = statistics.stdev(returns)
        
        if std_dev == 0:
            return 0.0
        
        n = len(returns)
        skewness = sum(((x - mean) / std_dev) ** 3 for x in returns) / n
        
        return skewness
    
    def _calculate_kurtosis(self, returns: List[float]) -> float:
        """Calculate kurtosis of returns distribution"""
        if len(returns) < 4:
            return 0.0
        
        mean = statistics.mean(returns)
        std_dev = statistics.stdev(returns)
        
        if std_dev == 0:
            return 0.0
        
        n = len(returns)
        kurtosis = sum(((x - mean) / std_dev) ** 4 for x in returns) / n
        
        # Excess kurtosis (subtract 3 for normal distribution baseline)
        return kurtosis - 3.0
    
    def _assess_overall_risk(
        self,
        volatility: float,
        skewness: float,
        kurtosis: float
    ) -> str:
        """Assess overall risk based on multiple factors"""
        risk_score = 0
        
        # Volatility contribution
        if volatility > 0.35:
            risk_score += 3
        elif volatility > 0.20:
            risk_score += 2
        elif volatility > 0.10:
            risk_score += 1
        
        # Skewness (negative skew is risky)
        if skewness < -0.5:
            risk_score += 2
        elif skewness < -0.2:
            risk_score += 1
        
        # Kurtosis (fat tails are risky)
        if kurtosis > 3.0:
            risk_score += 2
        elif kurtosis > 1.0:
            risk_score += 1
        
        # Classification
        if risk_score >= 6:
            return "VERY_HIGH_RISK"
        elif risk_score >= 4:
            return "HIGH_RISK"
        elif risk_score >= 2:
            return "MODERATE_RISK"
        else:
            return "LOW_RISK"
    
    def _recommend_investment_timing(
        self,
        volatility: float,
        vol_trend: str
    ) -> str:
        """Recommend investment timing based on volatility"""
        if volatility < 0.10 and vol_trend in ["STABLE", "DECREASING"]:
            return "EXCELLENT_TIMING"
        elif volatility < 0.20 and vol_trend != "INCREASING":
            return "GOOD_TIMING"
        elif volatility < 0.35:
            return "MODERATE_TIMING"
        else:
            return "WAIT_FOR_STABILITY"


# Module exports
__all__ = [
    "MarketEngineV241",
    "MarketMetrics",
    "VolatilityAnalysis"
]
