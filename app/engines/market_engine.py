"""
ZeroSite v24 - Market Data Engine

Market data analysis engine with intelligent fallback strategy for sparse transaction data.

Migrated from: backend/services_v9/market_data_processor.py
Engine Priority: NORMAL (existing module migration)

Fallback Strategy:
1. Exact address, 12 months → HIGH confidence (≥5 transactions)
2. 500m radius, 24 months → MEDIUM confidence (≥5 transactions)
3. District average → LOW confidence (with warning)

Author: ZeroSite Development Team
Version: 24.0.0
Date: 2025-12-12
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import random

from .base_engine import BaseEngine

logger = logging.getLogger(__name__)


@dataclass
class TransactionData:
    """Single real estate transaction record"""
    transaction_date: str
    price_per_sqm: float
    land_area_sqm: float
    total_price: float
    address: str
    distance_m: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class MarketEngine(BaseEngine):
    """
    Market Data Engine for ZeroSite v24
    
    Analyzes real estate market data with intelligent fallback mechanisms
    for handling sparse transaction data scenarios.
    """
    
    # District averages (₩ per sqm) - 2024 Q4 Seoul data
    DISTRICT_AVERAGES = {
        '강남구': 15_000_000,
        '서초구': 13_500_000,
        '송파구': 11_000_000,
        '용산구': 12_000_000,
        '마포구': 9_500_000,
        '성동구': 9_000_000,
        '영등포구': 8_500_000,
        '강서구': 7_000_000,
        '노원구': 6_500_000,
        '은평구': 7_500_000,
        '동작구': 8_000_000,
        '관악구': 7_000_000,
        '광진구': 8_500_000,
        '성북구': 7_500_000,
    }
    
    def __init__(self):
        """Initialize Market Engine"""
        super().__init__(engine_name="MarketEngine", version="24.0.0")
        self.logger.info("Market Engine v24.0.0 initialized")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process market data analysis request.
        
        Args:
            input_data: {
                'address': str - Property address
                'land_area_sqm': float - Land area in square meters
            }
            
        Returns:
            Standardized result dictionary with market analysis
        """
        self.log_processing(input_data)
        
        # Validate input
        required_fields = ['address', 'land_area_sqm']
        if not self.validate_input(input_data, required_fields):
            return self.create_result(
                success=False,
                error="Missing required fields: address, land_area_sqm"
            )
        
        try:
            address = input_data['address']
            land_area_sqm = float(input_data['land_area_sqm'])
            
            # Get market data with fallback strategy
            market_data = self.get_market_data_with_fallback(address, land_area_sqm)
            
            return self.create_result(success=True, data=market_data)
            
        except Exception as e:
            self.logger.error(f"Market data processing error: {str(e)}")
            return self.create_result(
                success=False,
                error=f"Market data processing failed: {str(e)}"
            )
    
    def get_market_data_with_fallback(self,
                                     address: str,
                                     land_area_sqm: float) -> Dict:
        """
        Get market data with intelligent fallback strategy.
        
        Returns:
            {
                'transactions': List[TransactionData],
                'confidence': 'HIGH' | 'MEDIUM' | 'LOW',
                'source': 'exact_address' | '500m_radius' | 'district_average',
                'avg_price_per_sqm': float,
                'transaction_count': int,
                'note': str,
                'statistics': dict,
                'raw_data': list
            }
        """
        
        self.logger.info(f"Getting market data for: {address}")
        
        # Strategy 1: Exact address, 12 months
        self.logger.info("Strategy 1: Searching exact address")
        transactions = self._get_transactions_exact(address, months=12)
        
        if len(transactions) >= 5:
            self.logger.info(f"✅ Found {len(transactions)} transactions (exact address)")
            return self._build_result(
                transactions, 'HIGH', 'exact_address', 
                f"최근 12개월 정확한 주소에서 {len(transactions)}건 확인"
            )
        
        # Strategy 2: 500m radius, 24 months
        self.logger.info("Strategy 2: Expanding to 500m radius")
        transactions = self._get_transactions_radius(address, radius_m=500, months=24)
        
        if len(transactions) >= 5:
            self.logger.info(f"✅ Found {len(transactions)} transactions (500m radius)")
            return self._build_result(
                transactions, 'MEDIUM', '500m_radius',
                f"반경 500m 내 {len(transactions)}건 확인 (24개월)"
            )
        
        # Strategy 3: District average (fallback)
        self.logger.warning("Strategy 3: Using district average (sparse data)")
        district = self._extract_district(address)
        district_avg = self._get_district_average(district, land_area_sqm)
        
        # Create synthetic transaction for display
        synthetic_transaction = TransactionData(
            transaction_date=datetime.now().strftime("%Y-%m-%d"),
            price_per_sqm=district_avg,
            land_area_sqm=land_area_sqm,
            total_price=district_avg * land_area_sqm / 100_000_000,  # 억원
            address=f"{district} 평균",
            distance_m=0
        )
        
        return self._build_result(
            [synthetic_transaction], 'LOW', 'district_average',
            f"⚠️ 실거래 데이터 부족. {district} 평균값 사용"
        )
    
    def _get_transactions_exact(self, address: str, months: int) -> List[TransactionData]:
        """
        Get transactions for exact address.
        
        NOTE: This is a MOCK implementation since we don't have real MOLIT API access.
        In production, this would call the actual API.
        """
        
        # Simulate random availability
        has_data = random.random() < 0.2  # 20% chance of having data
        
        if not has_data:
            return []
        
        # Generate 5-10 mock transactions
        num_transactions = random.randint(5, 10)
        district = self._extract_district(address)
        base_price = self.DISTRICT_AVERAGES.get(district, 8_000_000)
        
        transactions = []
        for i in range(num_transactions):
            # Vary price by ±15%
            price_variation = random.uniform(0.85, 1.15)
            price_per_sqm = base_price * price_variation
            
            # Random land area 500-1000㎡
            land_area = random.uniform(500, 1000)
            
            transaction = TransactionData(
                transaction_date=f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                price_per_sqm=price_per_sqm,
                land_area_sqm=land_area,
                total_price=price_per_sqm * land_area / 100_000_000,
                address=address
            )
            transactions.append(transaction)
        
        return transactions
    
    def _get_transactions_radius(self, 
                                address: str, 
                                radius_m: int, 
                                months: int) -> List[TransactionData]:
        """
        Get transactions within radius.
        
        NOTE: Mock implementation
        """
        
        # Simulate: expanding radius increases chance of finding data
        has_data = random.random() < 0.5  # 50% chance with wider search
        
        if not has_data:
            return []
        
        # Generate 8-15 mock transactions
        num_transactions = random.randint(8, 15)
        district = self._extract_district(address)
        base_price = self.DISTRICT_AVERAGES.get(district, 8_000_000)
        
        transactions = []
        for i in range(num_transactions):
            # Vary price by ±20% (wider radius = more variation)
            price_variation = random.uniform(0.80, 1.20)
            price_per_sqm = base_price * price_variation
            
            # Random distance 0-500m
            distance = random.uniform(0, radius_m)
            
            # Random land area
            land_area = random.uniform(400, 1200)
            
            transaction = TransactionData(
                transaction_date=f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                price_per_sqm=price_per_sqm,
                land_area_sqm=land_area,
                total_price=price_per_sqm * land_area / 100_000_000,
                address=f"{district} 인근",
                distance_m=distance
            )
            transactions.append(transaction)
        
        return transactions
    
    def _get_district_average(self, district: str, land_area_sqm: float) -> float:
        """
        Get district average price per sqm.
        
        Uses predefined district averages (2024 Q4 Seoul data)
        """
        
        # Get average for district or use Seoul average
        avg_price = self.DISTRICT_AVERAGES.get(district, 8_000_000)
        
        self.logger.info(f"Using district average for {district}: ₩{avg_price:,}/sqm")
        
        return avg_price
    
    def _build_result(self, 
                     transactions: List[TransactionData],
                     confidence: str,
                     source: str,
                     note: str) -> Dict:
        """Build standardized result dictionary"""
        
        # Calculate average price
        if transactions:
            avg_price = sum(tx.price_per_sqm for tx in transactions) / len(transactions)
        else:
            avg_price = 0
        
        # Calculate statistics
        if len(transactions) > 1:
            prices = [tx.price_per_sqm for tx in transactions]
            mean_price = sum(prices) / len(prices)
            variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
            std_dev = variance ** 0.5
            min_price = min(prices)
            max_price = max(prices)
            median_price = sorted(prices)[len(prices) // 2]
        else:
            mean_price = avg_price
            std_dev = 0
            min_price = avg_price
            max_price = avg_price
            median_price = avg_price
        
        return {
            'transactions': [tx.to_dict() for tx in transactions],
            'confidence': confidence,
            'source': source,
            'avg_price_per_sqm': round(avg_price, 0),
            'transaction_count': len(transactions),
            'note': note,
            'statistics': {
                'mean': round(mean_price, 0),
                'median': round(median_price, 0),
                'std_dev': round(std_dev, 0),
                'min': round(min_price, 0),
                'max': round(max_price, 0),
                'cv_percent': round((std_dev / mean_price * 100) if mean_price > 0 else 0, 1)
            },
            'raw_data': [
                {
                    'date': tx.transaction_date,
                    'price_per_sqm': round(tx.price_per_sqm, 0),
                    'land_area': round(tx.land_area_sqm, 1),
                    'address': tx.address,
                    'distance_m': round(tx.distance_m, 0) if tx.distance_m else None
                }
                for tx in transactions
            ]
        }
    
    def _extract_district(self, address: str) -> str:
        """Extract district (구) from full address"""
        # Example: "서울특별시 마포구 월드컵북로 120" → "마포구"
        parts = address.split()
        for part in parts:
            if part.endswith('구'):
                return part
        return "서울시"  # Default


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    # Test the Market Engine
    engine = MarketEngine()
    
    test_cases = [
        {
            "address": "서울특별시 마포구 월드컵북로 120",
            "land_area_sqm": 660.0
        },
        {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area_sqm": 1650.0
        }
    ]
    
    print("=" * 80)
    print("MARKET ENGINE v24.0.0 TEST")
    print("=" * 80)
    
    for test_case in test_cases:
        print(f"\n{'='*80}")
        print(f"Test Case: {test_case}")
        print(f"{'='*80}")
        
        result = engine.process(test_case)
        
        if result['success']:
            data = result['data']
            print(f"\n✅ Success!")
            print(f"Confidence: {data['confidence']}")
            print(f"Source: {data['source']}")
            print(f"Transaction Count: {data['transaction_count']}건")
            print(f"Avg Price: ₩{data['avg_price_per_sqm']:,}/㎡")
            print(f"Note: {data['note']}")
            
            if data['statistics']:
                stats = data['statistics']
                print(f"\n📊 Statistics:")
                print(f"   Mean: ₩{stats['mean']:,}/㎡")
                print(f"   Median: ₩{stats['median']:,}/㎡")
                print(f"   Std Dev: ₩{stats['std_dev']:,}")
                print(f"   Range: ₩{stats['min']:,} ~ ₩{stats['max']:,}")
                print(f"   CV: {stats['cv_percent']}%")
        else:
            print(f"\n❌ Error: {result['error']}")
