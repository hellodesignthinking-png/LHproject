"""
ZeroSite v30.0 - Appraisal Engine
Three Korean Standard Approaches:
1. Cost Approach (원가법)
2. Sales Comparison Approach (거래사례비교법)
3. Income Approach (수익환원법)
"""
from typing import Dict, List
from datetime import datetime


class AppraisalEngineV30:
    """Complete appraisal with 3 standard approaches"""
    
    def __init__(self):
        self.current_year = datetime.now().year
        
    def run_appraisal(self, land_info: Dict, transactions: List[Dict], 
                     premium_info: Dict) -> Dict[str, any]:
        """
        Complete appraisal with all 3 approaches
        
        Args:
            land_info: {
                'address': str,
                'land_area': float (sqm),
                'official_price': float (won/sqm),
                'zone_type': str,
                'lat': float,
                'lng': float
            }
            transactions: List of comparable sales
            premium_info: Premium analysis result
            
        Returns:
            Complete appraisal result with final value
        """
        # 1. Cost Approach (원가법)
        cost_value = self._cost_approach(land_info)
        
        # 2. Sales Comparison Approach (거래사례비교법)
        sales_value = self._sales_comparison_approach(land_info, transactions)
        
        # 3. Income Approach (수익환원법)
        income_value = self._income_approach(land_info)
        
        # Determine weights
        weights = self._determine_weights(land_info['zone_type'])
        
        # Calculate final value
        final_value = (
            cost_value * weights['cost'] +
            sales_value * weights['sales'] +
            income_value * weights['income']
        )
        
        # Apply premium
        premium_multiplier = 1 + (premium_info['premium_percentage'] / 100)
        final_value_with_premium = final_value * premium_multiplier
        
        return {
            'final_value': int(final_value_with_premium),
            'value_per_sqm': int(final_value_with_premium / land_info['land_area']),
            'approaches': {
                'cost': {
                    'value': int(cost_value),
                    'value_per_sqm': int(cost_value / land_info['land_area']),
                    'weight': weights['cost'],
                    'details': self._get_cost_details(land_info)
                },
                'sales_comparison': {
                    'value': int(sales_value),
                    'value_per_sqm': int(sales_value / land_info['land_area']),
                    'weight': weights['sales'],
                    'details': self._get_sales_details(transactions)
                },
                'income': {
                    'value': int(income_value),
                    'value_per_sqm': int(income_value / land_info['land_area']),
                    'weight': weights['income'],
                    'details': self._get_income_details(land_info)
                }
            },
            'weights': weights,
            'premium': {
                'percentage': premium_info['premium_percentage'],
                'factors': premium_info['top_5_factors']
            },
            'confidence_level': self._calculate_confidence(transactions, land_info)
        }
    
    def _cost_approach(self, land_info: Dict) -> float:
        """
        Cost Approach (원가법)
        Formula: Land Value = Official Land Price × Area × Location Factor
        """
        land_area = land_info['land_area']
        official_price = land_info['official_price']
        
        # Location factor (공시지가는 시세의 60~70% 수준)
        location_factor = 1.45  # 공시지가 → 시세 환산
        
        # Zoning adjustment
        zone_factor = self._get_zone_factor(land_info['zone_type'])
        
        land_value = official_price * land_area * location_factor * zone_factor
        
        return land_value
    
    def _sales_comparison_approach(self, land_info: Dict, transactions: List[Dict]) -> float:
        """
        Sales Comparison Approach (거래사례비교법)
        Formula: Adjusted Price = Comparable Price × Adjustments
        """
        if not transactions:
            # Fallback to cost approach if no transactions
            return self._cost_approach(land_info)
        
        # Use top 10 comparable sales
        top_comps = transactions[:10]
        
        adjusted_values = []
        for comp in top_comps:
            # Base price
            base_price = comp['price_per_sqm']
            
            # Time adjustment (±3% per year)
            time_adj = 1 + (comp['days_ago'] / 365) * 0.03
            
            # Distance adjustment (±2% per km)
            distance_adj = 1 - (comp['distance_km'] * 0.02)
            distance_adj = max(0.8, min(1.2, distance_adj))
            
            # Size adjustment (larger parcels have lower per-sqm price)
            size_ratio = comp['size_sqm'] / land_info['land_area']
            if size_ratio > 1:
                size_adj = 0.98  # Larger comp
            elif size_ratio < 1:
                size_adj = 1.02  # Smaller comp
            else:
                size_adj = 1.0
            
            # Adjusted price
            adjusted_price = base_price * time_adj * distance_adj * size_adj
            adjusted_values.append(adjusted_price)
        
        # Average of adjusted prices
        avg_price_per_sqm = sum(adjusted_values) / len(adjusted_values)
        
        return avg_price_per_sqm * land_info['land_area']
    
    def _income_approach(self, land_info: Dict) -> float:
        """
        Income Approach (수익환원법)
        Formula: Value = NOI / Cap Rate
        """
        zone_type = land_info['zone_type']
        land_area = land_info['land_area']
        official_price = land_info['official_price']
        
        # Estimate potential annual rent
        if '상업' in zone_type:
            # Commercial: Higher rent
            monthly_rent_per_sqm = official_price * 0.008  # 0.8% of value
            cap_rate = 0.055  # 5.5%
        elif '주거' in zone_type:
            # Residential: Moderate rent
            monthly_rent_per_sqm = official_price * 0.006  # 0.6% of value
            cap_rate = 0.045  # 4.5%
        else:
            # Others: Lower rent
            monthly_rent_per_sqm = official_price * 0.005  # 0.5% of value
            cap_rate = 0.06  # 6.0%
        
        # Annual NOI (Net Operating Income)
        annual_rent = monthly_rent_per_sqm * 12 * land_area
        operating_expenses = annual_rent * 0.20  # 20% expenses
        noi = annual_rent - operating_expenses
        
        # Value = NOI / Cap Rate
        value = noi / cap_rate
        
        return value
    
    def _get_zone_factor(self, zone_type: str) -> float:
        """Get zone type adjustment factor"""
        if '상업' in zone_type:
            return 1.2
        elif '주거' in zone_type:
            return 1.0
        elif '공업' in zone_type:
            return 0.9
        elif '녹지' in zone_type or '관리' in zone_type:
            return 0.85
        else:
            return 1.0
    
    def _determine_weights(self, zone_type: str) -> Dict[str, float]:
        """Determine approach weights based on zone type"""
        if '상업' in zone_type:
            # Commercial: Income approach is most relevant
            return {
                'cost': 0.20,
                'sales': 0.40,
                'income': 0.40
            }
        elif '주거' in zone_type:
            # Residential: Sales comparison is key
            return {
                'cost': 0.25,
                'sales': 0.55,
                'income': 0.20
            }
        else:
            # Others: Cost approach dominates
            return {
                'cost': 0.50,
                'sales': 0.35,
                'income': 0.15
            }
    
    def _get_cost_details(self, land_info: Dict) -> Dict:
        """Get cost approach details"""
        return {
            'official_land_price': int(land_info['official_price']),
            'land_area': land_info['land_area'],
            'location_factor': 1.45,
            'zone_factor': self._get_zone_factor(land_info['zone_type'])
        }
    
    def _get_sales_details(self, transactions: List[Dict]) -> Dict:
        """Get sales comparison details"""
        if not transactions:
            return {'comparable_count': 0}
        
        return {
            'comparable_count': len(transactions),
            'avg_price_per_sqm': int(sum(t['price_per_sqm'] for t in transactions[:10]) / min(10, len(transactions))),
            'date_range': f"{transactions[-1]['transaction_date']} ~ {transactions[0]['transaction_date']}"
        }
    
    def _get_income_details(self, land_info: Dict) -> Dict:
        """Get income approach details"""
        zone_type = land_info['zone_type']
        
        if '상업' in zone_type:
            cap_rate = 0.055
        elif '주거' in zone_type:
            cap_rate = 0.045
        else:
            cap_rate = 0.06
        
        return {
            'cap_rate': cap_rate,
            'zone_type': zone_type
        }
    
    def _calculate_confidence(self, transactions: List[Dict], land_info: Dict) -> str:
        """Calculate confidence level"""
        if len(transactions) >= 10:
            return "높음"
        elif len(transactions) >= 5:
            return "중간"
        else:
            return "낮음"


# Test function
if __name__ == "__main__":
    engine = AppraisalEngineV30()
    
    # Test data
    land_info = {
        'address': '서울특별시 강남구 역삼동 680-11',
        'land_area': 400,
        'official_price': 27_200_000,
        'zone_type': '근린상업지역',
        'lat': 37.5172,
        'lng': 127.0473
    }
    
    transactions = [
        {'price_per_sqm': 32_000_000, 'days_ago': 90, 'distance_km': 0.5, 'size_sqm': 380},
        {'price_per_sqm': 31_500_000, 'days_ago': 120, 'distance_km': 0.8, 'size_sqm': 420},
    ]
    
    premium_info = {
        'premium_percentage': 25.0,
        'top_5_factors': [
            {'factor': '강남 프리미엄', 'impact': 15.0},
            {'factor': '역세권', 'impact': 10.0}
        ]
    }
    
    result = engine.run_appraisal(land_info, transactions, premium_info)
    print(f"Final Value: ₩{result['final_value']:,}")
    print(f"Value per sqm: ₩{result['value_per_sqm']:,}")
    print(f"Confidence: {result['confidence_level']}")
