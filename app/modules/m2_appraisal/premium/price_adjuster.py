"""
Enhanced Price Adjuster for ZeroSite Expert v3

Professional 4-factor adjustment methodology
Based on Korean certified appraiser standards
"""

from dataclasses import dataclass
from typing import List


@dataclass
class AdjustmentFactors:
    """Individual adjustment factors"""
    distance: float  # -12% ~ 0%
    time: float      # -12% ~ 0%
    size: float      # -8% ~ 0%
    zone: float      # -5% ~ 0%
    total: float     # Weighted sum


@dataclass
class AdjustedTransaction:
    """Transaction with adjustments applied"""
    transaction: any  # Transaction from transaction_generator
    factors: AdjustmentFactors
    adjusted_price_per_sqm: float
    adjusted_total_price: float


class EnhancedPriceAdjuster:
    """
    Professional price adjustment engine
    
    Improvements over existing:
    - Proper weighted formula (not simple average)
    - Korean appraiser methodology (감정평가사 기준)
    - Clear tier-based adjustments
    - Total cap at -15%
    """
    
    # Adjustment weights (must sum to 1.0)
    WEIGHTS = {
        'distance': 0.35,  # 35% - Most important
        'time': 0.25,      # 25% - Second
        'size': 0.25,      # 25% - Third
        'zone': 0.15       # 15% - Least important
    }
    
    def __init__(self):
        """Initialize and validate weights"""
        total = sum(self.WEIGHTS.values())
        assert abs(total - 1.0) < 0.01, f"Weights must sum to 1.0, got {total}"
    
    def adjust_transactions(
        self,
        transactions: List,
        target_size_sqm: float,
        target_zone: str
    ) -> List[AdjustedTransaction]:
        """
        Apply 4-factor adjustments to all transactions
        
        Args:
            transactions: List of comparable transactions
            target_size_sqm: Target land size
            target_zone: Target zone type
        
        Returns:
            List of AdjustedTransaction objects
        """
        adjusted = []
        
        for txn in transactions:
            factors = self._calculate_factors(
                distance_km=txn.distance_km,
                days_since=txn.days_since_transaction,
                comp_size=txn.size_sqm,
                target_size=target_size_sqm,
                comp_zone=txn.zone_type,
                target_zone=target_zone
            )
            
            # Apply adjustment
            adjustment_multiplier = 1.0 + factors.total
            adjusted_price = txn.price_per_sqm * adjustment_multiplier
            adjusted_total = adjusted_price * txn.size_sqm
            
            adjusted.append(AdjustedTransaction(
                transaction=txn,
                factors=factors,
                adjusted_price_per_sqm=adjusted_price,
                adjusted_total_price=adjusted_total
            ))
        
        return adjusted
    
    def _calculate_factors(
        self,
        distance_km: float,
        days_since: int,
        comp_size: float,
        target_size: float,
        comp_zone: str,
        target_zone: str
    ) -> AdjustmentFactors:
        """Calculate all 4 adjustment factors"""
        
        # Individual factors (all negative or zero)
        distance_adj = self._distance_adjustment(distance_km)
        time_adj = self._time_adjustment(days_since)
        size_adj = self._size_adjustment(comp_size, target_size)
        zone_adj = self._zone_adjustment(comp_zone, target_zone)
        
        # Weighted total
        total_adj = (
            distance_adj * self.WEIGHTS['distance'] +
            time_adj * self.WEIGHTS['time'] +
            size_adj * self.WEIGHTS['size'] +
            zone_adj * self.WEIGHTS['zone']
        )
        
        # Cap at -15%
        total_adj = max(total_adj, -0.15)
        
        return AdjustmentFactors(
            distance=distance_adj,
            time=time_adj,
            size=size_adj,
            zone=zone_adj,
            total=total_adj
        )
    
    def _distance_adjustment(self, distance_km: float) -> float:
        """
        Distance adjustment (거리보정)
        
        Tiers:
        - 0 ~ 0.3km: 0% (perfect proximity)
        - 0.3 ~ 1.0km: -3% (good)
        - 1.0 ~ 2.0km: -6% (moderate)
        - 2.0km+: -12% (far)
        """
        if distance_km < 0.3:
            return 0.0
        elif distance_km < 1.0:
            return -0.03
        elif distance_km < 2.0:
            return -0.06
        else:
            return -0.12
    
    def _time_adjustment(self, days_since: int) -> float:
        """
        Time adjustment (시점보정)
        
        Tiers:
        - < 6 months: 0%
        - 6-12 months: -3%
        - 12-24 months: -6%
        - 24+ months: -12%
        """
        if days_since < 180:
            return 0.0
        elif days_since < 365:
            return -0.03
        elif days_since < 730:
            return -0.06
        else:
            return -0.12
    
    def _size_adjustment(self, comp_size: float, target_size: float) -> float:
        """
        Size adjustment (면적보정)
        
        Tiers:
        - Ratio 0.7~1.3 (±30%): 0%
        - Ratio 0.5~0.7 or 1.3~1.5 (±50%): -4%
        - Other: -8%
        """
        ratio = comp_size / target_size
        
        if 0.7 <= ratio <= 1.3:
            return 0.0
        elif 0.5 <= ratio < 0.7 or 1.3 < ratio <= 1.5:
            return -0.04
        else:
            return -0.08
    
    def _zone_adjustment(self, comp_zone: str, target_zone: str) -> float:
        """
        Zone adjustment (용도보정)
        
        Tiers:
        - Same: 0%
        - Similar residential: -3%
        - Different: -5%
        """
        if comp_zone == target_zone:
            return 0.0
        
        # Residential zones
        residential = {
            "제1종일반주거지역", "제2종일반주거지역",
            "제3종일반주거지역", "준주거지역"
        }
        
        if comp_zone in residential and target_zone in residential:
            return -0.03
        
        return -0.05


# Test
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from backend.services.transaction_generator import EnhancedTransactionGenerator
    
    # Generate test data
    gen = EnhancedTransactionGenerator()
    txns = gen.generate_comparables(
        center_lat=37.5172,
        center_lng=127.0473,
        region="서울특별시",
        district="강남구",
        target_zone="제2종일반주거지역",
        target_size_sqm=1000.0,
        radius_km=1.5,
        count=10
    )
    
    # Apply adjustments
    adjuster = EnhancedPriceAdjuster()
    adjusted = adjuster.adjust_transactions(
        transactions=txns,
        target_size_sqm=1000.0,
        target_zone="제2종일반주거지역"
    )
    
    print("Enhanced Price Adjuster Test\n" + "="*50)
    print(f"\n{'#':<3} {'거리':<8} {'시점':<8} {'규모':<8} {'용도':<8} {'총계':<8} {'가격변화':<12}")
    print("-" * 60)
    
    for i, adj in enumerate(adjusted, 1):
        f = adj.factors
        price_change = adj.adjusted_price_per_sqm - adj.transaction.price_per_sqm
        
        print(f"{i:<3} "
              f"{f.distance*100:>+6.1f}% "
              f"{f.time*100:>+6.1f}% "
              f"{f.size*100:>+6.1f}% "
              f"{f.zone*100:>+6.1f}% "
              f"{f.total*100:>+6.1f}% "
              f"₩{price_change:>+10,.0f}")
