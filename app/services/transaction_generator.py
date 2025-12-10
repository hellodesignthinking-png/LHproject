"""
Transaction Generator Service

Purpose: Convert Phase 7 comparable valuation results into standardized JSON format
Input: Phase 7 comparable results (raw)
Output: List of 10 comparable transactions sorted by recency and distance

Author: ZeroSite Development Team
Date: 2024-12-10
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TransactionGenerator:
    """
    Generate standardized transaction list from Phase 7 comparable results
    
    Sorting priority:
    1. Most recent transactions (within 1 year)
    2. Closest distance (<2km)
    3. Similar size (±30%)
    """
    
    def __init__(self):
        """Initialize transaction generator"""
        self.max_transactions = 10
        logger.info("✅ TransactionGenerator initialized")
    
    def generate_from_phase7(
        self, 
        comparable_results: List[Dict[str, Any]],
        target_size_sqm: float,
        target_zone: str
    ) -> List[Dict[str, Any]]:
        """
        Convert Phase 7 results to standardized transaction format
        
        Args:
            comparable_results: Raw Phase 7 comparable data
            target_size_sqm: Target land size for similarity comparison
            target_zone: Target zone type for filtering
        
        Returns:
            List of 10 standardized comparable transactions
        """
        try:
            logger.info(f"📋 Generating transactions from {len(comparable_results)} Phase 7 results")
            
            # Convert to standardized format
            transactions = []
            for idx, comp in enumerate(comparable_results[:self.max_transactions]):
                transaction = self._standardize_comparable(comp, idx)
                if transaction:
                    transactions.append(transaction)
            
            # Sort by recency and distance
            sorted_txns = self._sort_transactions(
                transactions, 
                target_size_sqm,
                target_zone
            )
            
            logger.info(f"✅ Generated {len(sorted_txns)} standardized transactions")
            return sorted_txns[:self.max_transactions]
            
        except Exception as e:
            logger.error(f"❌ Transaction generation failed: {e}")
            return []
    
    def _standardize_comparable(
        self, 
        comp: Dict[str, Any], 
        index: int
    ) -> Optional[Dict[str, Any]]:
        """
        Convert single comparable to standard format
        
        Standard format:
        {
            "id": int,
            "address": str,
            "lat": float,
            "lng": float,
            "size_sqm": float,
            "price_per_sqm": float,
            "total_price": float,
            "zone_type": str,
            "transaction_date": str (ISO format),
            "days_ago": int,
            "distance_km": float
        }
        """
        try:
            # Extract from Phase 7 format
            return {
                "id": index + 1,
                "address": comp.get("address", "주소 정보 없음"),
                "lat": comp.get("lat", 37.5665),  # Default Seoul
                "lng": comp.get("lng", 126.9780),
                "size_sqm": float(comp.get("area", comp.get("size_sqm", 1000.0))),
                "price_per_sqm": float(comp.get("price_per_sqm", comp.get("unit_price", 10000000))),
                "total_price": float(comp.get("total_price", 
                                            comp.get("price_per_sqm", 10000000) * 
                                            comp.get("area", 1000.0))),
                "zone_type": comp.get("zone", comp.get("zone_type", "제2종일반주거지역")),
                "transaction_date": comp.get("date", datetime.now().strftime("%Y-%m-%d")),
                "days_ago": self._calculate_days_ago(comp.get("date")),
                "distance_km": float(comp.get("distance", comp.get("distance_km", 1.0)))
            }
        except Exception as e:
            logger.warning(f"⚠️ Failed to standardize comparable {index}: {e}")
            return None
    
    def _calculate_days_ago(self, date_str: Optional[str]) -> int:
        """Calculate days since transaction"""
        if not date_str:
            return 180  # Default 6 months
        
        try:
            txn_date = datetime.strptime(date_str, "%Y-%m-%d")
            days = (datetime.now() - txn_date).days
            return max(0, days)
        except:
            return 180
    
    def _sort_transactions(
        self,
        transactions: List[Dict[str, Any]],
        target_size_sqm: float,
        target_zone: str
    ) -> List[Dict[str, Any]]:
        """
        Sort transactions by priority:
        1. Most recent (days_ago)
        2. Closest distance (distance_km)
        3. Similar size (size_sqm)
        """
        def sort_key(txn):
            # Recency score (0-1, higher = better)
            recency_score = max(0, 1 - (txn["days_ago"] / 730))  # 2 years max
            
            # Distance score (0-1, higher = better)
            distance_score = max(0, 1 - (txn["distance_km"] / 3.0))  # 3km max
            
            # Size similarity score (0-1, higher = better)
            size_ratio = txn["size_sqm"] / target_size_sqm if target_size_sqm > 0 else 1.0
            size_score = 1 - abs(1 - size_ratio) if 0.5 <= size_ratio <= 1.5 else 0.5
            
            # Zone match bonus
            zone_bonus = 0.2 if txn["zone_type"] == target_zone else 0
            
            # Weighted total (recency 40%, distance 35%, size 25%)
            total_score = (
                recency_score * 0.40 +
                distance_score * 0.35 +
                size_score * 0.25 +
                zone_bonus
            )
            
            return -total_score  # Negative for descending sort
        
        return sorted(transactions, key=sort_key)
    
    def format_for_display(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Format transactions for UI display
        
        Returns:
            List with formatted strings for display
        """
        formatted = []
        for txn in transactions:
            formatted.append({
                "id": str(txn["id"]),
                "address": txn["address"],
                "size": f"{txn['size_sqm']:,.1f}m²",
                "price_per_sqm": f"₩{txn['price_per_sqm']:,.0f}/m²",
                "total_price": f"₩{txn['total_price']:,.0f}",
                "zone": txn["zone_type"],
                "date": txn["transaction_date"],
                "days_ago": f"{txn['days_ago']}일 전",
                "distance": f"{txn['distance_km']:.2f}km"
            })
        
        return formatted


# Test
if __name__ == "__main__":
    # Mock Phase 7 results
    mock_phase7 = [
        {
            "address": "서울특별시 강남구 역삼동 123-45",
            "lat": 37.5172,
            "lng": 127.0473,
            "area": 1000.0,
            "price_per_sqm": 15000000,
            "total_price": 15000000000,
            "zone": "제2종일반주거지역",
            "date": "2024-10-15",
            "distance": 0.5
        },
        {
            "address": "서울특별시 강남구 논현동 100-1",
            "lat": 37.5100,
            "lng": 127.0400,
            "area": 950.0,
            "price_per_sqm": 14500000,
            "total_price": 13775000000,
            "zone": "제2종일반주거지역",
            "date": "2024-08-20",
            "distance": 0.8
        }
    ]
    
    generator = TransactionGenerator()
    transactions = generator.generate_from_phase7(
        comparable_results=mock_phase7,
        target_size_sqm=1000.0,
        target_zone="제2종일반주거지역"
    )
    
    print("\n✅ Transaction Generator Test")
    print("="*60)
    for txn in transactions:
        print(f"\n#{txn['id']} {txn['address']}")
        print(f"   Size: {txn['size_sqm']:.1f}m² | Price: ₩{txn['price_per_sqm']:,}/m²")
        print(f"   Distance: {txn['distance_km']}km | {txn['days_ago']} days ago")
