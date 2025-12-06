"""
ZeroSite Phase 7.7: Market Signal Analyzer

Analyzes market signals by comparing ZeroSite's calculated value with real market prices.

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class MarketSignalAnalyzer:
    """
    Market signal analysis engine
    
    Compares ZeroSite's calculated value with market reality:
    - UNDERVALUED: ZeroSite value < market value (opportunity)
    - FAIR: ZeroSite value ≈ market value (aligned)
    - OVERVALUED: ZeroSite value > market value (caution)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize market signal analyzer
        
        Args:
            config_path: Path to market_parameters.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent.parent / "config" / "market_data" / "market_parameters.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.thresholds = self.config['signal_thresholds']
        self.undervalued_threshold = self.thresholds['undervalued']  # -0.10
        self.overvalued_threshold = self.thresholds['overvalued']    # +0.10
        
        logger.info("✅ MarketSignalAnalyzer initialized")
    
    def compare(
        self,
        zerosite_value: float,
        market_value: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare ZeroSite value with market value
        
        Args:
            zerosite_value: Value calculated by ZeroSite (per m²)
            market_value: Average market price (per m²)
            context: Optional context (region, housing type, etc.)
        
        Returns:
            Dictionary with:
                - signal: 'UNDERVALUED', 'FAIR', or 'OVERVALUED'
                - delta: Price difference as ratio
                - delta_absolute: Absolute price difference
                - delta_percent: Percentage difference
                - explanation: Human-readable explanation
        
        Example:
            >>> analyzer = MarketSignalAnalyzer()
            >>> result = analyzer.compare(3200000, 4000000)
            >>> print(result['signal'])
            'UNDERVALUED'
            >>> print(result['delta_percent'])
            -20.0
        """
        if market_value == 0:
            logger.warning("Market value is 0, cannot calculate delta")
            return self._create_result('UNKNOWN', 0, 0, 0, "Insufficient market data")
        
        # Calculate delta
        delta_absolute = zerosite_value - market_value
        delta = delta_absolute / market_value
        delta_percent = delta * 100
        
        # Determine signal
        if delta <= self.undervalued_threshold:
            signal = 'UNDERVALUED'
            explanation = self._explain_undervalued(delta_percent, context)
        elif delta >= self.overvalued_threshold:
            signal = 'OVERVALUED'
            explanation = self._explain_overvalued(delta_percent, context)
        else:
            signal = 'FAIR'
            explanation = self._explain_fair(delta_percent, context)
        
        logger.info(f"📊 Market Signal: {signal} (delta: {delta_percent:+.1f}%)")
        
        return self._create_result(signal, delta, delta_absolute, delta_percent, explanation, context)
    
    def _create_result(
        self,
        signal: str,
        delta: float,
        delta_absolute: float,
        delta_percent: float,
        explanation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create standardized result dictionary"""
        result = {
            'signal': signal,
            'delta': round(delta, 4),
            'delta_absolute': round(delta_absolute, 0),
            'delta_percent': round(delta_percent, 2),
            'explanation': explanation,
            'timestamp': None  # TODO: Add timestamp
        }
        
        if context:
            result['context'] = context
        
        return result
    
    def _explain_undervalued(self, delta_percent: float, context: Optional[Dict] = None) -> str:
        """Generate explanation for UNDERVALUED signal"""
        abs_delta = abs(delta_percent)
        
        if abs_delta >= 30:
            intensity = "매우 저평가"
            recommendation = "높은 투자 기회로 판단됨"
        elif abs_delta >= 20:
            intensity = "상당한 저평가"
            recommendation = "투자 검토 권장"
        else:
            intensity = "다소 저평가"
            recommendation = "적정한 가격 수준"
        
        return f"ZeroSite 분석가가 시장가격 대비 {abs_delta:.1f}% 낮게 평가됨 ({intensity}). {recommendation}."
    
    def _explain_overvalued(self, delta_percent: float, context: Optional[Dict] = None) -> str:
        """Generate explanation for OVERVALUED signal"""
        if delta_percent >= 30:
            intensity = "매우 고평가"
            recommendation = "신중한 검토 필요"
        elif delta_percent >= 20:
            intensity = "상당한 고평가"
            recommendation = "추가 분석 권장"
        else:
            intensity = "다소 고평가"
            recommendation = "현실적인 가격 조정 고려"
        
        return f"ZeroSite 분석가가 시장가격 대비 {delta_percent:.1f}% 높게 평가됨 ({intensity}). {recommendation}."
    
    def _explain_fair(self, delta_percent: float, context: Optional[Dict] = None) -> str:
        """Generate explanation for FAIR signal"""
        if abs(delta_percent) <= 3:
            return f"ZeroSite 분석가와 시장가격이 거의 일치함 (차이: {delta_percent:+.1f}%). 매우 적정한 수준."
        else:
            direction = "높게" if delta_percent > 0 else "낮게"
            return f"ZeroSite 분석가가 시장가격 대비 {abs(delta_percent):.1f}% {direction} 평가됨. 적정 범위 내 차이."
    
    def analyze_market_temperature(
        self,
        vacancy_rate: float,
        transaction_volume: int,
        price_trend: str
    ) -> Dict[str, Any]:
        """
        Analyze market temperature (hot/stable/cold)
        
        Args:
            vacancy_rate: Vacancy rate (0.0-1.0)
            transaction_volume: Number of transactions
            price_trend: 'up', 'flat', or 'down'
        
        Returns:
            Dictionary with market temperature analysis
        """
        categories = self.config['market_categories']
        
        # Determine temperature
        if (vacancy_rate <= categories['hot']['vacancy_rate_max'] and
            transaction_volume >= categories['hot']['transaction_volume_min'] and
            price_trend == 'up'):
            temperature = 'HOT'
            description = "매우 활발한 시장 (낮은 공실률, 높은 거래량, 상승 추세)"
        elif (vacancy_rate >= categories['cold']['vacancy_rate_min'] or
              transaction_volume <= categories['cold'].get('transaction_volume_max', 50) or
              price_trend == 'down'):
            temperature = 'COLD'
            description = "침체된 시장 (높은 공실률, 낮은 거래량, 하락 추세)"
        else:
            temperature = 'STABLE'
            description = "안정적인 시장 (적정 공실률, 보통 거래량, 평탄 추세)"
        
        return {
            'temperature': temperature,
            'description': description,
            'vacancy_rate': vacancy_rate,
            'transaction_volume': transaction_volume,
            'price_trend': price_trend
        }
    
    def generate_investment_recommendation(
        self,
        market_signal: str,
        market_temperature: str,
        financial_metrics: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Generate investment recommendation based on multiple factors
        
        Args:
            market_signal: UNDERVALUED/FAIR/OVERVALUED
            market_temperature: HOT/STABLE/COLD
            financial_metrics: Optional financial metrics (IRR, NPV, etc.)
        
        Returns:
            Investment recommendation string
        """
        # Combination analysis
        if market_signal == 'UNDERVALUED' and market_temperature == 'HOT':
            return "🔥 강력 추천: 저평가 + 활발한 시장 → 높은 투자 기회"
        elif market_signal == 'UNDERVALUED' and market_temperature == 'STABLE':
            return "✅ 추천: 저평가 + 안정적 시장 → 양호한 투자 기회"
        elif market_signal == 'FAIR' and market_temperature in ['HOT', 'STABLE']:
            return "✅ 적정: 공정가격 + 양호한 시장 → 안정적 투자"
        elif market_signal == 'OVERVALUED' and market_temperature == 'HOT':
            return "⚠️ 주의: 고평가 + 활발한 시장 → 버블 가능성 검토"
        elif market_signal == 'OVERVALUED':
            return "❌ 비추천: 고평가 시장 → 신중한 접근 필요"
        elif market_temperature == 'COLD':
            return "⚠️ 주의: 침체 시장 → 추가 분석 필요"
        else:
            return "➡️ 중립: 추가 정보 필요"


# Convenience function
def analyze_market_signal(
    zerosite_value: float,
    market_value: float,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to analyze market signal
    
    Args:
        zerosite_value: ZeroSite calculated value
        market_value: Market average price
        context: Optional context
    
    Returns:
        Market signal analysis result
    """
    analyzer = MarketSignalAnalyzer()
    return analyzer.compare(zerosite_value, market_value, context)
