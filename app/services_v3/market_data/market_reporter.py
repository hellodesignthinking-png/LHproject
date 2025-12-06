"""
ZeroSite Phase 7.7: Market Reporter

Generates comprehensive market reports combining transaction data, signals, and analysis.

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

from typing import Dict, Any, Optional
import logging

from .molit_api import MOLITApi
from .market_signal_analyzer import MarketSignalAnalyzer

logger = logging.getLogger(__name__)


class MarketReporter:
    """
    Market report generation engine
    
    Combines:
    - MOLIT transaction data
    - Market signal analysis
    - Temperature analysis
    - Investment recommendations
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize market reporter
        
        Args:
            config_path: Path to market_parameters.json
            api_key: Optional MOLIT API key
        """
        self.molit_api = MOLITApi(config_path, api_key)
        self.signal_analyzer = MarketSignalAnalyzer(config_path)
        
        logger.info("✅ MarketReporter initialized")
    
    def generate_market_report(
        self,
        address: str,
        coordinates: Optional[tuple] = None,
        zerosite_value: Optional[float] = None,
        financial_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive market report
        
        Args:
            address: Full address string
            coordinates: Optional (latitude, longitude)
            zerosite_value: Optional ZeroSite calculated value (per m²)
            financial_metrics: Optional financial metrics (IRR, NPV, etc.)
        
        Returns:
            Dictionary with comprehensive market analysis:
                - market_data: Transaction and price data
                - market_signal: Signal analysis (if zerosite_value provided)
                - market_temperature: Temperature analysis
                - investment_recommendation: Investment recommendation
        
        Example:
            >>> reporter = MarketReporter()
            >>> report = reporter.generate_market_report(
            ...     "서울특별시 강남구",
            ...     zerosite_value=3200000
            ... )
            >>> print(report['market_signal']['signal'])
            'UNDERVALUED'
        """
        logger.info(f"📊 Generating market report for: {address}")
        
        # Step 1: Get market data from MOLIT
        market_data = self.molit_api.get_market_data(address, coordinates)
        
        # Step 2: Analyze market signal (if ZeroSite value provided)
        market_signal = None
        if zerosite_value:
            market_signal = self.signal_analyzer.compare(
                zerosite_value=zerosite_value,
                market_value=market_data['avg_price_per_m2'],
                context={'address': address}
            )
        
        # Step 3: Analyze market temperature
        market_temperature = self.signal_analyzer.analyze_market_temperature(
            vacancy_rate=market_data['vacancy_rate'],
            transaction_volume=market_data['transaction_volume'],
            price_trend=market_data['price_trend']
        )
        
        # Step 4: Generate investment recommendation
        investment_recommendation = None
        if market_signal:
            investment_recommendation = self.signal_analyzer.generate_investment_recommendation(
                market_signal=market_signal['signal'],
                market_temperature=market_temperature['temperature'],
                financial_metrics=financial_metrics
            )
        
        # Compile report
        report = {
            'market_data': market_data,
            'market_signal': market_signal,
            'market_temperature': market_temperature,
            'investment_recommendation': investment_recommendation,
            'address': address
        }
        
        logger.info(f"✅ Market report generated")
        if market_signal:
            logger.info(f"   Signal: {market_signal['signal']} ({market_signal['delta_percent']:+.1f}%)")
        logger.info(f"   Temperature: {market_temperature['temperature']}")
        
        return report
    
    def get_quick_comparison(
        self,
        address: str,
        zerosite_value: float
    ) -> Dict[str, Any]:
        """
        Quick comparison of ZeroSite value with market
        
        Args:
            address: Full address string
            zerosite_value: ZeroSite calculated value (per m²)
        
        Returns:
            Quick comparison result
        """
        market_data = self.molit_api.get_market_data(address)
        market_signal = self.signal_analyzer.compare(
            zerosite_value=zerosite_value,
            market_value=market_data['avg_price_per_m2']
        )
        
        return {
            'zerosite_value': zerosite_value,
            'market_avg': market_data['avg_price_per_m2'],
            'market_median': market_data['median_price_per_m2'],
            'signal': market_signal['signal'],
            'delta_percent': market_signal['delta_percent'],
            'explanation': market_signal['explanation']
        }
    
    def get_market_summary(self, address: str) -> str:
        """
        Get human-readable market summary
        
        Args:
            address: Full address string
        
        Returns:
            Formatted summary string
        """
        market_data = self.molit_api.get_market_data(address)
        temperature = self.signal_analyzer.analyze_market_temperature(
            vacancy_rate=market_data['vacancy_rate'],
            transaction_volume=market_data['transaction_volume'],
            price_trend=market_data['price_trend']
        )
        
        summary = f"""
🏢 시장 분석: {address}

📊 가격 정보:
  • 평균 실거래가: {market_data['avg_price_per_m2']/1e6:.1f}M원/㎡
  • 중위 실거래가: {market_data['median_price_per_m2']/1e6:.1f}M원/㎡
  • 평균 매물가: {market_data['listing_avg_price_per_m2']/1e6:.1f}M원/㎡

📈 시장 현황:
  • 공실률: {market_data['vacancy_rate']*100:.1f}%
  • 거래량: {market_data['transaction_volume']}건
  • 가격 추세: {market_data['price_trend']}
  • 시장 온도: {temperature['temperature']} ({temperature['description']})
""".strip()
        
        return summary


# Convenience function
def generate_market_report(
    address: str,
    coordinates: Optional[tuple] = None,
    zerosite_value: Optional[float] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate market report
    
    Args:
        address: Full address string
        coordinates: Optional (latitude, longitude)
        zerosite_value: Optional ZeroSite calculated value
    
    Returns:
        Market report dictionary
    """
    reporter = MarketReporter()
    return reporter.generate_market_report(address, coordinates, zerosite_value)
