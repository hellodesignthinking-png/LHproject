"""
Enhanced Confidence Calculator for ZeroSite Expert v3

Professional confidence scoring based on 4 weighted factors
"""

import statistics
from typing import List, Tuple
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence classification"""
    HIGH = "HIGH"      # 0.75-1.0: Very reliable
    MEDIUM = "MEDIUM"  # 0.50-0.75: Moderately reliable
    LOW = "LOW"        # 0.0-0.50: Caution needed


class EnhancedConfidenceCalculator:
    """
    Professional confidence scoring engine
    
    Improvements over existing:
    - 4-factor weighted algorithm (not simple heuristic)
    - Sample size factor (30%)
    - Price variance factor (30%)
    - Distance proximity factor (25%)
    - Recency factor (15%)
    """
    
    # Confidence weights (must sum to 1.0)
    WEIGHTS = {
        'sample_size': 0.30,
        'price_variance': 0.30,
        'distance': 0.25,
        'recency': 0.15
    }
    
    def __init__(self):
        """Initialize and validate weights"""
        total = sum(self.WEIGHTS.values())
        assert abs(total - 1.0) < 0.01, f"Weights must sum to 1.0, got {total}"
    
    def calculate_confidence(
        self,
        transaction_count: int,
        adjusted_prices: List[float],
        average_price: float,
        distances_km: List[float],
        days_since_transactions: List[int]
    ) -> Tuple[float, ConfidenceLevel]:
        """
        Calculate overall confidence score
        
        Args:
            transaction_count: Number of comparables
            adjusted_prices: List of adjusted prices per m²
            average_price: Predicted average price
            distances_km: List of distances from target
            days_since_transactions: List of days since each transaction
        
        Returns:
            (confidence_score, confidence_level)
        """
        
        # Calculate 4 factor scores
        sample_score = self._sample_size_score(transaction_count)
        variance_score = self._price_variance_score(adjusted_prices, average_price)
        distance_score = self._distance_score(distances_km)
        recency_score = self._recency_score(days_since_transactions)
        
        # Weighted average
        confidence = (
            sample_score * self.WEIGHTS['sample_size'] +
            variance_score * self.WEIGHTS['price_variance'] +
            distance_score * self.WEIGHTS['distance'] +
            recency_score * self.WEIGHTS['recency']
        )
        
        confidence = round(confidence, 2)
        level = self._get_level(confidence)
        
        return confidence, level
    
    def _sample_size_score(self, count: int) -> float:
        """
        Sample size factor (거래사례 수)
        
        Scoring:
        - 10+: 1.0 (perfect)
        - 7-9: 0.8
        - 5-6: 0.65
        - 3-4: 0.55
        - 1-2: 0.50 (minimum)
        """
        if count >= 10:
            return 1.0
        elif count >= 7:
            return 0.8
        elif count >= 5:
            return 0.65
        elif count >= 3:
            return 0.55
        else:
            return 0.50
    
    def _price_variance_score(self, prices: List[float], average: float) -> float:
        """
        Price variance factor (가격 일관성)
        
        Uses Coefficient of Variation (CV = std_dev / mean)
        
        Scoring:
        - CV < 5%: 1.0 (very consistent)
        - CV < 10%: 0.85
        - CV < 15%: 0.70
        - CV < 20%: 0.60
        - CV >= 20%: 0.50
        """
        if len(prices) < 2:
            return 0.70  # Default
        
        std_dev = statistics.stdev(prices)
        cv = std_dev / average if average > 0 else 1.0
        
        if cv < 0.05:
            return 1.0
        elif cv < 0.10:
            return 0.85
        elif cv < 0.15:
            return 0.70
        elif cv < 0.20:
            return 0.60
        else:
            return 0.50
    
    def _distance_score(self, distances: List[float]) -> float:
        """
        Distance proximity factor (거리 근접성)
        
        Scoring:
        - Avg < 0.5km: 1.0
        - Avg < 1.0km: 0.85
        - Avg < 1.5km: 0.70
        - Avg < 2.0km: 0.60
        - Avg >= 2.0km: 0.50
        """
        if not distances:
            return 0.50
        
        avg_distance = statistics.mean(distances)
        
        if avg_distance < 0.5:
            return 1.0
        elif avg_distance < 1.0:
            return 0.85
        elif avg_distance < 1.5:
            return 0.70
        elif avg_distance < 2.0:
            return 0.60
        else:
            return 0.50
    
    def _recency_score(self, days_list: List[int]) -> float:
        """
        Recency factor (최신성)
        
        Scoring:
        - Avg < 90 days: 1.0
        - Avg < 180 days: 0.85
        - Avg < 365 days: 0.70
        - Avg < 540 days: 0.60
        - Avg >= 540 days: 0.50
        """
        if not days_list:
            return 0.50
        
        avg_days = statistics.mean(days_list)
        
        if avg_days < 90:
            return 1.0
        elif avg_days < 180:
            return 0.85
        elif avg_days < 365:
            return 0.70
        elif avg_days < 540:
            return 0.60
        else:
            return 0.50
    
    def _get_level(self, score: float) -> ConfidenceLevel:
        """Convert score to level"""
        if score >= 0.75:
            return ConfidenceLevel.HIGH
        elif score >= 0.50:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW


# Test
if __name__ == "__main__":
    calc = EnhancedConfidenceCalculator()
    
    print("Enhanced Confidence Calculator Test\n" + "="*50)
    
    # Scenario 1: High confidence
    print("\nScenario 1: High Confidence")
    score1, level1 = calc.calculate_confidence(
        transaction_count=10,
        adjusted_prices=[9.5e6, 9.6e6, 9.55e6, 9.58e6, 9.52e6, 
                        9.56e6, 9.54e6, 9.57e6, 9.53e6, 9.59e6],
        average_price=9.56e6,
        distances_km=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.2, 0.4],
        days_since_transactions=[45, 60, 75, 80, 90, 100, 110, 120, 50, 70]
    )
    print(f"Score: {score1:.2f} | Level: {level1.value}")
    
    # Scenario 2: Medium confidence
    print("\nScenario 2: Medium Confidence")
    score2, level2 = calc.calculate_confidence(
        transaction_count=7,
        adjusted_prices=[9.0e6, 9.8e6, 9.4e6, 9.6e6, 9.2e6, 9.7e6, 9.3e6],
        average_price=9.43e6,
        distances_km=[1.2, 1.5, 1.8, 1.3, 1.6, 1.4, 1.7],
        days_since_transactions=[200, 250, 280, 220, 260, 240, 230]
    )
    print(f"Score: {score2:.2f} | Level: {level2.value}")
    
    # Scenario 3: Low confidence
    print("\nScenario 3: Low Confidence")
    score3, level3 = calc.calculate_confidence(
        transaction_count=3,
        adjusted_prices=[8.0e6, 11.0e6, 9.0e6],
        average_price=9.33e6,
        distances_km=[2.5, 3.0, 2.8],
        days_since_transactions=[600, 650, 700]
    )
    print(f"Score: {score3:.2f} | Level: {level3.value}")
