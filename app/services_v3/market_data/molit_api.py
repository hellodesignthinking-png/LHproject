"""
ZeroSite Phase 7.7: MOLIT API Interface

Interfaces with Korean Ministry of Land, Infrastructure and Transport (MOLIT) APIs
for real transaction data and market information.

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class MOLITApi:
    """
    Interface for MOLIT (Ministry of Land, Infrastructure and Transport) APIs
    
    Provides:
    - Real transaction prices (실거래가)
    - Market average prices
    - Transaction volumes
    - Supply data
    """
    
    def __init__(self, config_path: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize MOLIT API interface
        
        Args:
            config_path: Path to market_parameters.json
            api_key: Optional MOLIT API key
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent.parent / "config" / "market_data" / "market_parameters.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.api_config = self.config['api_config']['molit_api']
        self.use_mock = self.config['mock_data'].get('enabled', True)
        self.mock_regions = self.config['mock_data']['regions']
        self.api_key = api_key
        
        logger.info(f"✅ MOLITApi initialized (mock_mode={self.use_mock})")
    
    def get_market_data(
        self,
        address: str,
        coordinates: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive market data for a location
        
        Args:
            address: Full address string
            coordinates: Optional (latitude, longitude)
        
        Returns:
            Dictionary with market data:
                - avg_price_per_m2: Average transaction price
                - median_price_per_m2: Median transaction price
                - listing_avg_price_per_m2: Average listing price
                - vacancy_rate: Vacancy rate
                - transaction_volume: Transaction volume
                - price_trend: 'up', 'flat', or 'down'
                - supply_volume: New supply volume
        
        Example:
            >>> api = MOLITApi()
            >>> data = api.get_market_data("서울특별시 강남구")
            >>> print(data['avg_price_per_m2'])
            4500000
        """
        logger.info(f"📊 Fetching market data for: {address}")
        
        # Extract region for mock data lookup
        region = self._extract_region(address)
        
        if self.use_mock:
            data = self._get_mock_market_data(region)
        else:
            data = self._get_real_market_data(address, coordinates)
        
        logger.info(f"✅ Market data retrieved: avg_price={data['avg_price_per_m2']/1e6:.1f}M원/㎡")
        
        return data
    
    def get_transaction_history(
        self,
        address: str,
        months: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Get recent transaction history
        
        Args:
            address: Full address string
            months: Number of months to look back
        
        Returns:
            List of transactions
        """
        logger.info(f"📜 Fetching transaction history for: {address} (last {months} months)")
        
        region = self._extract_region(address)
        
        if self.use_mock:
            return self._get_mock_transaction_history(region, months)
        else:
            return self._get_real_transaction_history(address, months)
    
    def get_listing_prices(
        self,
        address: str,
        property_type: str = "apartment"
    ) -> Dict[str, Any]:
        """
        Get current listing prices (매물가격)
        
        Args:
            address: Full address string
            property_type: Property type filter
        
        Returns:
            Dictionary with listing price statistics
        """
        logger.info(f"🏠 Fetching listing prices for: {address}")
        
        region = self._extract_region(address)
        
        if self.use_mock:
            return self._get_mock_listing_prices(region)
        else:
            return self._get_real_listing_prices(address, property_type)
    
    def _extract_region(self, address: str) -> str:
        """Extract region code from address for mock data lookup"""
        address_lower = address.lower()
        
        # Gangnam area
        if any(kw in address_lower for kw in ['강남', '서초', '송파', 'gangnam']):
            return 'gangnam'
        
        # Bundang area
        if any(kw in address_lower for kw in ['분당', '판교', '수지', 'bundang']):
            return 'bundang'
        
        # Gyeongbuk area
        if any(kw in address_lower for kw in ['경북', '경상북도', 'gyeongbuk']):
            return 'gyeongbuk'
        
        # Default
        return 'default'
    
    def _get_mock_market_data(self, region: str) -> Dict[str, Any]:
        """Get mock market data for testing"""
        region_data = self.mock_regions.get(region, self.mock_regions['default'])
        return region_data.copy()
    
    def _get_mock_transaction_history(self, region: str, months: int) -> List[Dict[str, Any]]:
        """Get mock transaction history"""
        region_data = self.mock_regions.get(region, self.mock_regions['default'])
        avg_price = region_data['avg_price_per_m2']
        
        # Generate mock transactions
        transactions = []
        for month in range(months):
            transaction = {
                'month': f"2024-{12-month:02d}",
                'price_per_m2': avg_price * (0.95 + 0.1 * (month / months)),
                'area_m2': 85,
                'total_price': avg_price * 85 * (0.95 + 0.1 * (month / months)),
                'floor': 10
            }
            transactions.append(transaction)
        
        return transactions
    
    def _get_mock_listing_prices(self, region: str) -> Dict[str, Any]:
        """Get mock listing prices"""
        region_data = self.mock_regions.get(region, self.mock_regions['default'])
        
        return {
            'avg_price_per_m2': region_data['listing_avg_price_per_m2'],
            'median_price_per_m2': region_data['listing_avg_price_per_m2'] * 0.97,
            'count': 50,
            'avg_deposit': region_data.get('avg_deposit', 0),
            'avg_monthly_rent': region_data.get('avg_monthly_rent', 0)
        }
    
    def _get_real_market_data(
        self,
        address: str,
        coordinates: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Get real market data from MOLIT API
        
        TODO: Implement real MOLIT API calls:
        - 부동산 실거래가 API
        - 주택 가격 동향 API
        - 공실 현황 API
        
        For now, falls back to mock data
        """
        logger.warning("⚠️ Real MOLIT API not implemented, falling back to mock data")
        region = self._extract_region(address)
        return self._get_mock_market_data(region)
    
    def _get_real_transaction_history(
        self,
        address: str,
        months: int
    ) -> List[Dict[str, Any]]:
        """
        Get real transaction history from MOLIT API
        
        TODO: Implement real MOLIT API calls
        
        For now, falls back to mock data
        """
        logger.warning("⚠️ Real MOLIT API not implemented, falling back to mock data")
        region = self._extract_region(address)
        return self._get_mock_transaction_history(region, months)
    
    def _get_real_listing_prices(
        self,
        address: str,
        property_type: str
    ) -> Dict[str, Any]:
        """
        Get real listing prices from external sources
        
        TODO: Implement real listing scraper/API:
        - NAVER 부동산
        - 직방
        - 다방
        
        For now, falls back to mock data
        """
        logger.warning("⚠️ Real listing API not implemented, falling back to mock data")
        region = self._extract_region(address)
        return self._get_mock_listing_prices(region)


# Convenience function
def get_market_data(address: str, coordinates: Optional[tuple] = None) -> Dict[str, Any]:
    """
    Convenience function to get market data
    
    Args:
        address: Full address string
        coordinates: Optional (latitude, longitude)
    
    Returns:
        Market data dictionary
    """
    api = MOLITApi()
    return api.get_market_data(address, coordinates)
