"""
Premium Calculator for Land Appraisal System
Antenna Holdings Co., Ltd.

This module calculates premium adjustments for land appraisal based on various factors:
- Physical characteristics (shape, slope, direction, road facing)
- Location/Amenities (subway, school district, park, shopping, hospital, river view)
- Development/Regulation (redevelopment status, GTX, greenbelt, cultural heritage)

Algorithm:
1. Collect all premium elements from input data
2. Sort by absolute value (descending)
3. Select top 5 elements
4. Calculate total sum of top 5 premiums
5. Apply 50% adjustment (total_premium_adjusted = sum_top5 * 0.5)

This prevents over-adjustment when multiple premium factors exist.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PremiumFactor:
    """Represents a single premium factor"""
    name: str
    value: float  # Percentage value (e.g., 15 for +15%, -20 for -20%)
    category: str  # 'physical', 'location', 'development'
    
    @property
    def abs_value(self) -> float:
        """Absolute value for sorting"""
        return abs(self.value)


class PremiumCalculator:
    """
    Premium Calculator for Land Appraisal
    
    Calculates adjusted premium based on top 5 factors with 50% adjustment.
    """
    
    # Premium factor definitions with categories
    FACTOR_DEFINITIONS = {
        # Physical Characteristics
        'land_shape': {'name': '토지형상', 'category': 'physical'},
        'land_slope': {'name': '토지경사도', 'category': 'physical'},
        'direction': {'name': '향(向)', 'category': 'physical'},
        'road_facing': {'name': '접도조건', 'category': 'physical'},
        
        # Location/Amenities
        'subway_distance': {'name': '지하철역 거리', 'category': 'location'},
        'school_district_8': {'name': '8학군', 'category': 'location'},
        'large_park': {'name': '대형공원', 'category': 'location'},
        'department_store': {'name': '백화점/쇼핑몰', 'category': 'location'},
        'large_hospital': {'name': '대형병원', 'category': 'location'},
        'han_river_view': {'name': '한강 조망권', 'category': 'location'},
        
        # Development/Regulation
        'redevelopment_status': {'name': '재개발 상황', 'category': 'development'},
        'gtx_station': {'name': 'GTX역 거리', 'category': 'development'},
        'greenbelt': {'name': '그린벨트', 'category': 'development'},
        'cultural_heritage_zone': {'name': '문화재보호구역', 'category': 'development'}
    }
    
    def __init__(self):
        """Initialize Premium Calculator"""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate_premium(
        self, 
        premium_factors: Dict[str, float]
    ) -> Tuple[float, List[PremiumFactor], Dict]:
        """
        Calculate adjusted premium based on top 5 factors
        
        Args:
            premium_factors: Dictionary of factor_name -> percentage value
        
        Returns:
            Tuple of (total_adjusted_premium, top_5_factors, calculation_details)
        
        Example:
            premium_factors = {
                'land_shape': 15,
                'subway_distance': 30,
                'school_district_8': 25,
                'redevelopment_status': 60,
                'gtx_station': 50,
                'han_river_view': 25,
                'greenbelt': -40
            }
            
            Returns: (32.5, [list of top 5], details_dict)
            # (60 + 50 + 30 + 25 + 25) * 0.5 = 95 * 0.5 = 47.5%
            # But in case of negative like greenbelt: (60 + 50 + 30 - 40 + 25) * 0.5 = 62.5%
        """
        
        # Step 1: Collect all premium factors
        factors: List[PremiumFactor] = []
        
        for factor_key, value in premium_factors.items():
            if value == 0:
                continue  # Skip zero values
            
            factor_def = self.FACTOR_DEFINITIONS.get(factor_key)
            if not factor_def:
                self.logger.warning(f"Unknown premium factor: {factor_key}")
                continue
            
            factor = PremiumFactor(
                name=factor_def['name'],
                value=value,
                category=factor_def['category']
            )
            factors.append(factor)
        
        if not factors:
            return 0.0, [], {
                'total_factors': 0,
                'top_5_sum': 0.0,
                'adjustment_rate': 0.5,
                'final_premium': 0.0
            }
        
        # Step 2: Sort by absolute value (descending)
        sorted_factors = sorted(factors, key=lambda f: f.abs_value, reverse=True)
        
        # Step 3: Select top 5
        top_5 = sorted_factors[:5]
        
        # Step 4: Calculate sum of top 5
        top_5_sum = sum(f.value for f in top_5)
        
        # Step 5: Apply 50% adjustment
        adjustment_rate = 0.5
        total_adjusted_premium = top_5_sum * adjustment_rate
        
        # Prepare calculation details
        details = {
            'total_factors': len(factors),
            'top_5_sum': top_5_sum,
            'adjustment_rate': adjustment_rate,
            'final_premium': total_adjusted_premium,
            'all_factors': [
                {'name': f.name, 'value': f.value, 'category': f.category}
                for f in sorted_factors
            ],
            'top_5_factors': [
                {'name': f.name, 'value': f.value, 'category': f.category}
                for f in top_5
            ]
        }
        
        self.logger.info(
            f"Premium calculation: {len(factors)} factors, "
            f"top 5 sum = {top_5_sum:.1f}%, "
            f"final adjusted = {total_adjusted_premium:.1f}%"
        )
        
        return total_adjusted_premium, top_5, details
    
    def apply_premium_to_value(
        self,
        base_value: float,
        premium_percentage: float
    ) -> float:
        """
        Apply premium adjustment to base value
        
        Args:
            base_value: Base appraisal value (KRW)
            premium_percentage: Premium percentage (e.g., 32.5 for +32.5%)
        
        Returns:
            Adjusted value
        
        Example:
            base_value = 5_300_000_000  # 53억원
            premium_percentage = 32.5
            
            Returns: 5_300_000_000 * (1 + 0.325) = 7_022_500_000  # 약 70억원
        """
        multiplier = 1.0 + (premium_percentage / 100.0)
        adjusted_value = base_value * multiplier
        
        self.logger.info(
            f"Applied premium {premium_percentage:.1f}% to {base_value:,.0f} KRW "
            f"→ {adjusted_value:,.0f} KRW"
        )
        
        return adjusted_value
    
    def get_premium_summary_text(
        self,
        top_5_factors: List[PremiumFactor],
        total_premium: float
    ) -> str:
        """
        Generate human-readable summary text for PDF/reports
        
        Args:
            top_5_factors: List of top 5 premium factors
            total_premium: Total adjusted premium percentage
        
        Returns:
            Formatted summary text
        """
        if not top_5_factors:
            return "프리미엄 요인 없음"
        
        summary_lines = []
        summary_lines.append("**상위 5개 프리미엄 요인:**\n")
        
        for i, factor in enumerate(top_5_factors, 1):
            sign = '+' if factor.value >= 0 else ''
            summary_lines.append(f"{i}. {factor.name}: {sign}{factor.value:.1f}%")
        
        top_5_sum = sum(f.value for f in top_5_factors)
        summary_lines.append(f"\n합계: {top_5_sum:+.1f}%")
        summary_lines.append(f"조정률 적용 (×50%): **{total_premium:+.1f}%**")
        
        return '\n'.join(summary_lines)


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create calculator
    calc = PremiumCalculator()
    
    # Example 1: Multiple high premium factors
    print("=" * 60)
    print("Example 1: 강남 재개발구역, GTX, 8학군")
    print("=" * 60)
    
    premium_data = {
        'land_shape': 15,           # 정방형
        'subway_distance': 30,      # 300m 이내
        'school_district_8': 25,    # 8학군
        'redevelopment_status': 60, # 사업승인
        'gtx_station': 50,          # 500m 이내
        'han_river_view': 25        # 한강 조망
    }
    
    total_premium, top_5, details = calc.calculate_premium(premium_data)
    
    print(f"\n전체 요인 수: {details['total_factors']}")
    print(f"상위 5개 합계: {details['top_5_sum']:.1f}%")
    print(f"최종 조정 프리미엄: {total_premium:.1f}%\n")
    
    print("상위 5개 요인:")
    for i, f in enumerate(top_5, 1):
        print(f"  {i}. {f.name}: {f.value:+.1f}%")
    
    # Apply to base value
    base_value = 5_300_000_000  # 53억원
    adjusted_value = calc.apply_premium_to_value(base_value, total_premium)
    print(f"\n기본 평가액: {base_value:,.0f} 원 ({base_value/100_000_000:.1f}억원)")
    print(f"조정 평가액: {adjusted_value:,.0f} 원 ({adjusted_value/100_000_000:.1f}억원)")
    print(f"증가액: {adjusted_value - base_value:,.0f} 원 "
          f"(+{((adjusted_value/base_value - 1) * 100):.1f}%)")
    
    # Example 2: With negative factors (greenbelt)
    print("\n" + "=" * 60)
    print("Example 2: 그린벨트, 문화재보호구역 (마이너스 요인)")
    print("=" * 60)
    
    premium_data_2 = {
        'land_shape': 15,           # 정방형
        'subway_distance': 20,      # 500m 이내
        'greenbelt': -40,           # 그린벨트
        'cultural_heritage_zone': -30,  # 문화재보호구역
        'direction': 12             # 남향
    }
    
    total_premium_2, top_5_2, details_2 = calc.calculate_premium(premium_data_2)
    
    print(f"\n전체 요인 수: {details_2['total_factors']}")
    print(f"상위 5개 합계: {details_2['top_5_sum']:.1f}%")
    print(f"최종 조정 프리미엄: {total_premium_2:.1f}%\n")
    
    print("상위 5개 요인 (절대값 기준):")
    for i, f in enumerate(top_5_2, 1):
        print(f"  {i}. {f.name}: {f.value:+.1f}%")
    
    # Apply to base value
    adjusted_value_2 = calc.apply_premium_to_value(base_value, total_premium_2)
    print(f"\n기본 평가액: {base_value:,.0f} 원 ({base_value/100_000_000:.1f}억원)")
    print(f"조정 평가액: {adjusted_value_2:,.0f} 원 ({adjusted_value_2/100_000_000:.1f}억원)")
    change = adjusted_value_2 - base_value
    change_pct = (adjusted_value_2/base_value - 1) * 100
    print(f"변동액: {change:,.0f} 원 ({change_pct:+.1f}%)")
    
    # Generate summary text
    print("\n" + "=" * 60)
    print("Summary Text for PDF:")
    print("=" * 60)
    summary_text = calc.get_premium_summary_text(top_5, total_premium)
    print(summary_text)
