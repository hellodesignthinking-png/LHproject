"""
Market Data Processor for ZeroSite v22
======================================

Handles market intelligence data with automatic fallback generation.

Key Features:
- Region name normalization
- Market data fallback generator
- Price estimation by region
- Automatic comp generation

Author: ZeroSite Development Team
Date: 2025-12-10
Version: v22.0.0
"""

import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random


class MarketDataProcessor:
    """Process market intelligence data with fallback support"""
    
    # Seoul region price database (원/㎡)
    REGION_BASE_PRICES = {
        # Premium regions
        "강남구": 8_000_000, "서초구": 7_500_000, "송파구": 7_000_000,
        "용산구": 6_800_000, "강동구": 6_500_000,
        
        # High-value regions
        "마포구": 6_500_000, "성동구": 6_200_000, "영등포구": 6_200_000,
        "양천구": 6_000_000, "구로구": 5_800_000,
        
        # Mid-value regions
        "광진구": 5_800_000, "동작구": 5_500_000, "관악구": 5_200_000,
        "성북구": 5_000_000, "중랑구": 4_800_000,
        
        # Standard regions
        "노원구": 4_500_000, "강북구": 4_300_000, "도봉구": 4_200_000,
        "은평구": 4_200_000, "금천구": 4_000_000,
        
        # Outer regions
        "종로구": 7_200_000, "중구": 6_500_000, "동대문구": 5_000_000,
        "서대문구": 5_500_000, "강서구": 5_300_000,
        
        # Default
        "default": 5_000_000
    }
    
    # Region name mapping for normalization
    REGION_MAPPING = {
        "강남": "강남구", "서초": "서초구", "송파": "송파구",
        "용산": "용산구", "강동": "강동구", "마포": "마포구",
        "성동": "성동구", "영등포": "영등포구", "양천": "양천구",
        "구로": "구로구", "광진": "광진구", "동작": "동작구",
        "관악": "관악구", "성북": "성북구", "중랑": "중랑구",
        "노원": "노원구", "강북": "강북구", "도봉": "도봉구",
        "은평": "은평구", "금천": "금천구", "종로": "종로구",
        "중": "중구", "동대문": "동대문구", "서대문": "서대문구",
        "강서": "강서구"
    }
    
    @classmethod
    def normalize_region_name(cls, address: str) -> str:
        """
        Normalize region name for consistent lookup
        
        Examples:
            "서울특별시 강남구 역삼동" → "강남구"
            "강남구 역삼동" → "강남구"
            "강남 역삼동" → "강남구"
        """
        # Try direct mapping first
        for short_name, full_name in cls.REGION_MAPPING.items():
            if short_name in address:
                return full_name
        
        # Try regex extraction
        match = re.search(r'(서울특별시\s+)?(\S+구)', address)
        if match:
            return match.group(2)
        
        # Default fallback
        return "default"
    
    @classmethod
    def estimate_base_price(cls, region: str) -> float:
        """
        Estimate base land price by region (원/㎡)
        
        Args:
            region: Normalized region name (e.g., "강남구")
            
        Returns:
            Base price in KRW per sqm
        """
        return cls.REGION_BASE_PRICES.get(region, cls.REGION_BASE_PRICES["default"])
    
    @classmethod
    def generate_realistic_comps(
        cls, 
        address: str, 
        count: int = 3,
        price_variance: float = 0.10
    ) -> List[Dict]:
        """
        Generate realistic comparable transactions
        
        Args:
            address: Target address
            count: Number of comps to generate (default: 3)
            price_variance: Price variance ratio (default: 0.10 = ±10%)
            
        Returns:
            List of comp dictionaries with realistic data
        """
        region = cls.normalize_region_name(address)
        base_price = cls.estimate_base_price(region)
        
        comps = []
        base_date = datetime.now()
        
        for i in range(count):
            # Generate price with variance
            price_multiplier = 1.0 + random.uniform(-price_variance, price_variance)
            comp_price = int(base_price * price_multiplier)
            
            # Generate transaction date (recent 12 months)
            days_ago = random.randint(30 * i, 30 * (i + 4))
            transaction_date = (base_date - timedelta(days=days_ago)).strftime("%Y-%m")
            
            # Generate land area (realistic range)
            land_area = random.randint(1200, 2500)
            
            comps.append({
                "address": f"{address.split()[0]} {region} 인근 {chr(65+i)}단지",
                "price_per_sqm": comp_price,
                "transaction_date": transaction_date,
                "land_area_sqm": land_area,
                "source": "estimated",
                "distance_m": random.randint(100, 800)
            })
        
        # Sort by date (most recent first)
        comps.sort(key=lambda x: x["transaction_date"], reverse=True)
        
        return comps
    
    @classmethod
    def get_market_data_with_fallback(
        cls,
        address: str,
        real_comps: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Get market comps with automatic fallback generation
        
        Args:
            address: Target address
            real_comps: Optional real comparable transactions
            
        Returns:
            Dictionary with market data and metadata
        """
        region = cls.normalize_region_name(address)
        
        # Try to use real data first
        if real_comps and len(real_comps) >= 3:
            comps = real_comps[:3]  # Use top 3
            data_source = "real_transactions"
        else:
            # Generate fallback data
            comps = cls.generate_realistic_comps(address, count=3)
            data_source = "estimated"
        
        # Calculate statistics
        prices = [comp["price_per_sqm"] for comp in comps]
        avg_price = sum(prices) / len(prices) if prices else 0
        median_price = sorted(prices)[len(prices) // 2] if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        # Calculate standard deviation
        if len(prices) > 1:
            variance = sum((p - avg_price) ** 2 for p in prices) / len(prices)
            std_dev = variance ** 0.5
        else:
            std_dev = 0
        
        return {
            "region": region,
            "comps": comps,
            "data_source": data_source,
            "statistics": {
                "avg_price": int(avg_price),
                "median_price": int(median_price),
                "min_price": int(min_price),
                "max_price": int(max_price),
                "std_dev": int(std_dev),
                "cv": (std_dev / avg_price * 100) if avg_price > 0 else 0,  # Coefficient of Variation
                "sample_size": len(comps)
            }
        }
    
    @classmethod
    def calculate_price_positioning(
        cls,
        target_price: float,
        market_data: Dict
    ) -> Dict:
        """
        Calculate target price positioning vs market
        
        Args:
            target_price: Target land price (원/㎡)
            market_data: Market data from get_market_data_with_fallback()
            
        Returns:
            Dictionary with positioning analysis
        """
        stats = market_data["statistics"]
        avg_price = stats["avg_price"]
        
        if avg_price == 0:
            return {
                "price_vs_avg_pct": 0,
                "price_vs_median_pct": 0,
                "positioning": "unknown"
            }
        
        price_vs_avg_pct = ((target_price - avg_price) / avg_price) * 100
        price_vs_median_pct = ((target_price - stats["median_price"]) / stats["median_price"]) * 100
        
        # Determine positioning
        if price_vs_avg_pct <= -10:
            positioning = "매우 저평가"
        elif price_vs_avg_pct <= -5:
            positioning = "저평가"
        elif price_vs_avg_pct <= 5:
            positioning = "시장 평균"
        elif price_vs_avg_pct <= 10:
            positioning = "고평가"
        else:
            positioning = "매우 고평가"
        
        return {
            "price_vs_avg_pct": round(price_vs_avg_pct, 1),
            "price_vs_median_pct": round(price_vs_median_pct, 1),
            "positioning": positioning,
            "competitive_advantage": price_vs_avg_pct <= 0
        }


# Convenience functions for easy import
def normalize_region(address: str) -> str:
    """Normalize region name"""
    return MarketDataProcessor.normalize_region_name(address)


def get_market_data(address: str, real_comps: Optional[List[Dict]] = None) -> Dict:
    """Get market data with fallback"""
    return MarketDataProcessor.get_market_data_with_fallback(address, real_comps)


def estimate_price(region: str) -> float:
    """Estimate base price for region"""
    return MarketDataProcessor.estimate_base_price(region)
