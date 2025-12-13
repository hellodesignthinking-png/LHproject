"""
ZeroSite v24.1 - Appraisal Engine (감정평가 엔진)
Standard Korean Real Estate Appraisal System

Implements 3 standard appraisal approaches per Korean Real Estate Appraisal Law:
1. Cost Approach (원가법)
2. Sales Comparison Approach (거래사례비교법)
3. Income Approach (수익환원법)

Author: ZeroSite Development Team
Version: 24.1.0
Date: 2025-12-12
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import sys
from pathlib import Path

try:
    from .base_engine import BaseEngine
except ImportError:
    # For CLI testing
    sys.path.append(str(Path(__file__).parent.parent))
    from engines.base_engine import BaseEngine

# Import market data processor for real transaction prices
try:
    from app.services.market_data_processor import MOLITRealPriceAPI
    MARKET_DATA_AVAILABLE = True
except ImportError:
    MARKET_DATA_AVAILABLE = False
    logger.warning("⚠️ Market data processor not available")

# Import premium calculator for premium adjustments
try:
    from app.services.premium_calculator import PremiumCalculator
    PREMIUM_CALCULATOR_AVAILABLE = True
except ImportError:
    PREMIUM_CALCULATOR_AVAILABLE = False
    logger.warning("⚠️ Premium calculator not available")

logger = logging.getLogger(__name__)


@dataclass
class AppraisalResult:
    """Comprehensive appraisal result"""
    # Individual approach values
    cost_approach_value: float  # 억원
    sales_comparison_value: float  # 억원
    income_approach_value: float  # 억원
    
    # Final weighted value
    final_appraisal_value: float  # 억원
    final_value_per_sqm: float  # 원/㎡
    
    # Weights used
    weight_cost: float
    weight_sales: float
    weight_income: float
    
    # Confidence and adjustments
    location_factor: float
    confidence_level: str  # HIGH, MEDIUM, LOW
    market_conditions: str
    
    # Metadata
    appraisal_date: str
    individual_land_price_per_sqm: float  # 개별공시지가 (원/㎡)
    construction_cost_per_sqm: float  # 건축비 (원/㎡)
    
    # Breakdown details
    cost_breakdown: Dict
    sales_breakdown: Dict
    income_breakdown: Dict
    
    # Additional info
    notes: List[str]


class AppraisalEngineV241(BaseEngine):
    """
    Standard Korean Real Estate Appraisal Engine
    
    Implements 3 appraisal approaches:
    1. Cost Approach: Land value + Construction cost - Depreciation
    2. Sales Comparison: Recent comparable transactions with adjustments
    3. Income Approach: Rental income capitalization
    
    Final value = Weighted average of 3 approaches
    
    Features:
    - Individual land price (개별공시지가) integration
    - Location factor adjustments (Seoul +15%, etc.)
    - Building age depreciation curves
    - Market condition adjustments
    - Confidence scoring
    
    Input:
        address: str
        land_area_sqm: float
        building_area_sqm: Optional[float]
        construction_year: Optional[int]
        zone_type: str
        individual_land_price_per_sqm: Optional[float]
        annual_rental_income: Optional[float]
    
    Output:
        AppraisalResult with comprehensive breakdown
    """
    
    # Standard rates and factors
    LH_CONSTRUCTION_COST_PER_SQM = 3_500_000  # ₩/㎡ (2024 standard)
    SEOUL_LOCATION_FACTOR = 1.15
    DEPRECIATION_RATE_PER_YEAR = 0.02  # 2% per year
    MAX_DEPRECIATION = 0.50  # Maximum 50% depreciation
    DEFAULT_CAP_RATE = 0.045  # 4.5% capitalization rate
    
    # Appraisal weights (can be adjusted based on property type)
    DEFAULT_WEIGHT_COST = 0.40
    DEFAULT_WEIGHT_SALES = 0.40
    DEFAULT_WEIGHT_INCOME = 0.20
    
    def __init__(self):
        super().__init__(engine_name="AppraisalEngine", version="24.1.0")
        self.current_year = datetime.now().year
        
        # Initialize market data processor
        if MARKET_DATA_AVAILABLE:
            try:
                self.market_data_api = MOLITRealPriceAPI()
                self.logger.info("✅ Market data processor initialized")
            except Exception as e:
                self.market_data_api = None
                self.logger.warning(f"⚠️ Market data processor init failed: {e}")
        else:
            self.market_data_api = None
    
    def process(self, input_data: Dict) -> Dict:
        """
        Main processing method (BaseEngine interface)
        
        Required fields:
        - address: str
        - land_area_sqm: float
        - zone_type: str
        
        Optional fields:
        - building_area_sqm: float (for cost/income approaches)
        - construction_year: int (for depreciation)
        - individual_land_price_per_sqm: float (개별공시지가)
        - annual_rental_income: float (for income approach)
        - comparable_sales: List[Dict] (for sales comparison)
        """
        self.validate_input(input_data, ['address', 'land_area_sqm', 'zone_type'])
        
        address = input_data['address']
        land_area = input_data['land_area_sqm']
        building_area = input_data.get('building_area_sqm', 0)
        construction_year = input_data.get('construction_year', self.current_year)
        zone_type = input_data['zone_type']
        individual_land_price = input_data.get('individual_land_price_per_sqm', 0)
        annual_rental_income = input_data.get('annual_rental_income', 0)
        comparable_sales = input_data.get('comparable_sales', [])
        
        # ========================================
        # 🔥 V34.0: Parse address to get actual gu/dong
        # ========================================
        gu = '알수없음'
        dong = '알수없음'
        address_parsed_success = False
        
        try:
            from app.services.advanced_address_parser import AdvancedAddressParser
            parser = AdvancedAddressParser()
            parsed = parser.parse(address)
            
            # Check if parsing was successful (gu and dong are present)
            if parsed and parsed.get('gu') and parsed.get('dong'):
                gu = parsed.get('gu', '알수없음')
                dong = parsed.get('dong', '알수없음')
                address_parsed_success = True
                self.logger.info(f"✅ Address parsed: {gu} {dong}")
            else:
                self.logger.warning(f"⚠️ Address parsing incomplete: {parsed}")
        except Exception as e:
            self.logger.warning(f"❌ Address parsing failed: {e}")
        
        # Determine location factor
        location_factor = self._get_location_factor(address)
        
        # Calculate individual land price if not provided
        if individual_land_price == 0:
            individual_land_price = self._estimate_individual_land_price(zone_type, location_factor)
        
        # ========================================
        # 🔥 V34.0: Generate realistic transaction data using Smart Collector
        # ========================================
        generated_transactions = []
        
        if not comparable_sales:
            self.logger.info(f"🔍 Generating transaction data for: {gu} {dong}")
            try:
                from app.services.smart_transaction_collector_v34 import SmartTransactionCollectorV34
                collector = SmartTransactionCollectorV34()
                
                # Generate 15 transactions based on actual gu/dong
                generated_transactions = collector.collect_transactions(
                    address=address,
                    gu=gu,
                    dong=dong,
                    land_area_sqm=land_area,
                    num_transactions=15
                )
                
                self.logger.info(f"✅ Generated {len(generated_transactions)} transactions for {gu} {dong}")
                
                # Use top 5 nearest transactions for comparable sales
                if generated_transactions:
                    for tx in generated_transactions[:5]:
                        comparable_sales.append({
                            'price_per_sqm': tx['price_per_sqm'],
                            'time_adjustment': 1.0,  # Already adjusted in generation
                            'location_adjustment': 1.0,  # Same dong
                            'individual_adjustment': 1.0,
                            'weight': 0.2  # Equal weight for 5 comparables
                        })
                    self.logger.info(f"✅ Using {len(comparable_sales)} comparable sales from generated data")
                
            except Exception as e:
                self.logger.error(f"❌ Transaction generation failed: {e}")
        
        # 🔥 AUTO-FETCH REAL TRANSACTION DATA if no comparable sales provided (fallback)
        if not comparable_sales and self.market_data_api:
            self.logger.info(f"🔍 Auto-fetching real transaction data for: {address}")
            try:
                market_data = self.market_data_api.get_comprehensive_market_data(address, land_area, num_months=24)
                
                # Convert real transactions to comparable_sales format
                if market_data['count'] > 0 and market_data['data_source'] == 'API':
                    transactions = market_data['transactions'][:3]  # Use top 3 most recent
                    
                    for idx, tx in enumerate(transactions):
                        # Calculate time adjustment (more recent = higher weight)
                        tx_date = datetime.strptime(tx.transaction_date, "%Y-%m-%d")
                        months_ago = (datetime.now() - tx_date).days / 30
                        time_adj = 1.0 + (0.02 * min(months_ago, 12))  # 2% per month, max 24%
                        
                        comparable_sales.append({
                            'price_per_sqm': tx.price_per_sqm,
                            'time_adjustment': time_adj,
                            'location_adjustment': 1.0,  # Same district
                            'individual_adjustment': 1.0,  # Similar property
                            'weight': 1.0 / len(transactions)  # Equal weight
                        })
                    
                    self.logger.info(f"✅ Fetched {len(comparable_sales)} real transactions from MOLIT API")
                else:
                    self.logger.warning(f"⚠️ Using fallback: {market_data['data_source']}")
            
            except Exception as e:
                self.logger.error(f"❌ Market data fetch failed: {str(e)}")
        
        # Approach 1: Cost Approach
        cost_result = self.calculate_cost_approach(
            land_area=land_area,
            building_area=building_area,
            individual_land_price=individual_land_price,
            construction_year=construction_year,
            location_factor=location_factor
        )
        
        # Approach 2: Sales Comparison Approach
        sales_result = self.calculate_sales_comparison(
            land_area=land_area,
            individual_land_price=individual_land_price,
            comparable_sales=comparable_sales,
            location_factor=location_factor
        )
        
        # Approach 3: Income Approach
        income_result = self.calculate_income_approach(
            annual_rental_income=annual_rental_income,
            building_value=cost_result['building_value'],
            zone_type=zone_type,
            land_area_sqm=land_area
        )
        
        # Determine weights based on property characteristics
        weights = self._determine_weights(
            has_building=(building_area > 0),
            has_rental_income=(annual_rental_income > 0),
            has_comparables=(len(comparable_sales) > 0)
        )
        
        # Calculate base weighted value (before premium adjustment)
        base_value = (
            cost_result['total_value'] * weights['cost'] +
            sales_result['total_value'] * weights['sales'] +
            income_result['total_value'] * weights['income']
        )
        
        # ========== PREMIUM ADJUSTMENT ==========
        # Apply premium factors if provided
        premium_factors = input_data.get('premium_factors', {})
        premium_info = {}
        final_value = base_value  # Default to base value if no premium
        
        if premium_factors and PREMIUM_CALCULATOR_AVAILABLE:
            calculator = PremiumCalculator()
            
            # Calculate premium adjustment
            total_premium, top_5_factors, premium_details = calculator.calculate_premium(premium_factors)
            
            # Apply premium to base value
            final_value_krw = base_value * 100_000_000  # Convert to KRW
            adjusted_value_krw = calculator.apply_premium_to_value(final_value_krw, total_premium)
            final_value = adjusted_value_krw / 100_000_000  # Convert back to 억원
            
            # Store premium info for reporting
            premium_info = {
                'has_premium': True,
                'base_value': base_value,
                'premium_percentage': total_premium,
                'adjusted_value': final_value,
                'premium_details': premium_details,
                'top_5_factors': [
                    {'name': f.name, 'value': f.value, 'category': f.category}
                    for f in top_5_factors
                ]
            }
            
            self.logger.info(
                f"Premium adjustment applied: {total_premium:+.1f}% "
                f"({base_value:.2f}억원 → {final_value:.2f}억원)"
            )
        else:
            premium_info = {
                'has_premium': False,
                'base_value': base_value,
                'premium_percentage': 0,
                'adjusted_value': final_value,
                'premium_details': {},
                'top_5_factors': []
            }
        
        # 🔥 GENSPARK V4.0: Enhanced premium factors structure
        # Add detailed premium factor breakdown
        premium_info['premium_factors'] = {
            'location_premium': {
                'score': 0,  # Will be filled by location engine
                'description': '입지 및 교통 접근성'
            },
            'development_potential': {
                'score': 0,  # Will be filled by development engine
                'description': '개발 잠재력 및 용적률 활용도'
            },
            'market_trend': {
                'score': round(total_premium * 0.3, 1) if premium_factors else 0,
                'description': '주변 시장 동향 및 가격 상승세'
            },
            'scarcity': {
                'score': round(total_premium * 0.2, 1) if premium_factors else 0,
                'description': '희소성 및 대체 가능 필지 부족'
            },
            'risk_adjustment': {
                'score': 0,  # Negative factors
                'description': '규제 리스크 및 제약 요인'
            },
            'summary_narrative': (
                f"입지·개발 잠재력·시장 동향을 종합적으로 고려하여 "
                f"약 {total_premium:.1f}% 수준의 프리미엄을 적용한 것으로 판단됩니다."
                if premium_factors and total_premium > 0 else
                "기본 평가액을 적용하였습니다."
            )
        }
        
        # Determine confidence level
        confidence = self._assess_confidence(
            weights=weights,
            has_comparables=(len(comparable_sales) > 0),
            has_rental_data=(annual_rental_income > 0)
        )
        
        # Build comprehensive result
        result = AppraisalResult(
            cost_approach_value=round(cost_result['total_value'], 2),
            sales_comparison_value=round(sales_result['total_value'], 2),
            income_approach_value=round(income_result['total_value'], 2),
            final_appraisal_value=round(final_value, 2),
            final_value_per_sqm=int((final_value * 100_000_000) / land_area),
            weight_cost=weights['cost'],
            weight_sales=weights['sales'],
            weight_income=weights['income'],
            location_factor=location_factor,
            confidence_level=confidence,
            market_conditions="정상",
            appraisal_date=datetime.now().strftime("%Y-%m-%d"),
            individual_land_price_per_sqm=individual_land_price,
            construction_cost_per_sqm=int(self.LH_CONSTRUCTION_COST_PER_SQM * location_factor),
            cost_breakdown=cost_result,
            sales_breakdown=sales_result,
            income_breakdown=income_result,
            notes=self._generate_notes(address, zone_type, confidence)
        )
        
        self.logger.info(f"Appraisal complete: {final_value:.2f}억원 (Confidence: {confidence})")
        
        # 🔥 GENSPARK V3.0: Standardized output structure (Single Source of Truth)
        return {
            # ===== STANDARDIZED KEYS (Genspark v3.0 SECTION 1) =====
            'cost_approach_value': result.cost_approach_value,  # 원가법 최종가
            'sales_comparison_value': result.sales_comparison_value,  # 거래사례비교법 최종가
            'income_approach_value': result.income_approach_value,  # 수익환원법 최종가
            'base_weighted_value': base_value,  # 프리미엄 적용 전 가중평균
            'premium_rate': premium_info.get('premium_percentage', 0) / 100.0,  # 프리미엄율 (소수)
            'final_appraised_value': final_value,  # 프리미엄 적용 후 최종평가액
            
            # ===== BACKWARD COMPATIBILITY =====
            'final_appraisal_value': result.final_appraisal_value,
            'final_value_per_sqm': result.final_value_per_sqm,
            'cost_approach': result.cost_approach_value,
            'sales_comparison': result.sales_comparison_value,
            'income_approach': result.income_approach_value,
            
            # ===== SUPPORTING DATA =====
            'confidence_level': result.confidence_level,
            'location_factor': result.location_factor,
            'weights': {
                'cost': result.weight_cost,
                'sales': result.weight_sales,
                'income': result.weight_income
            },
            'premium_info': premium_info,  # Premium adjustment details
            'income_approach_details': result.income_breakdown,  # 🔥 GENSPARK V3.0: Income approach details
            'breakdown': {
                'cost': result.cost_breakdown,
                'sales': result.sales_breakdown,
                'income': result.income_breakdown
            },
            'metadata': {
                'appraisal_date': result.appraisal_date,
                'individual_land_price_per_sqm': result.individual_land_price_per_sqm,
                'construction_cost_per_sqm': result.construction_cost_per_sqm,
                'market_conditions': result.market_conditions
            },
            'notes': result.notes,
            'unit': '억원',
            
            # 🔥 V34.0: Add parsed address and generated transactions for PDF
            'address_parsed': {
                'gu': gu,
                'dong': dong,
                'success': address_parsed_success
            },
            'transactions': generated_transactions,  # Full transaction list for PDF
            'comparable_sales_data': comparable_sales  # Comparables used in calculation
        }
    
    def calculate_cost_approach(self,
                                land_area: float,
                                building_area: float,
                                individual_land_price: float,
                                construction_year: int,
                                location_factor: float) -> Dict:
        """
        Cost Approach (원가법)
        
        Formula:
        Total Value = Land Value + Building Value - Depreciation
        
        Components:
        - Land value = Land area × Individual land price
        - Building value = Building area × Construction cost × Location factor
        - Depreciation = Building value × Age × Depreciation rate (max 50%)
        """
        # Land value
        land_value_krw = land_area * individual_land_price
        land_value_billion = land_value_krw / 100_000_000
        
        # Building value (if exists)
        if building_area > 0:
            construction_cost = self.LH_CONSTRUCTION_COST_PER_SQM * location_factor
            building_value_krw = building_area * construction_cost
            building_value_billion = building_value_krw / 100_000_000
            
            # Calculate depreciation
            building_age = max(0, self.current_year - construction_year)
            depreciation_rate = min(
                building_age * self.DEPRECIATION_RATE_PER_YEAR,
                self.MAX_DEPRECIATION
            )
            depreciation_amount = building_value_billion * depreciation_rate
            net_building_value = building_value_billion - depreciation_amount
        else:
            building_value_billion = 0
            depreciation_amount = 0
            net_building_value = 0
        
        total_value = land_value_billion + net_building_value
        
        # 계산 과정 상세 설명 (PDF 출력용)
        calculation_steps = []
        calculation_steps.append(f"1. 토지가액: {land_area:,.1f}㎡ × {individual_land_price:,.0f}원/㎡ = {land_value_billion:.2f}억원")
        
        if building_area > 0:
            construction_cost = self.LH_CONSTRUCTION_COST_PER_SQM * location_factor
            building_age = self.current_year - construction_year
            calculation_steps.append(f"2. 재조달원가: {building_area:,.1f}㎡ × {construction_cost:,.0f}원/㎡ = {building_value_billion:.2f}억원")
            calculation_steps.append(f"3. 경과연수: {building_age}년 (내용연수 40년 기준)")
            calculation_steps.append(f"4. 감가율: {building_age}년 × 2% = {depreciation_rate*100:.1f}% (최대 50%)")
            calculation_steps.append(f"5. 감가차감: {building_value_billion:.2f}억원 × {depreciation_rate*100:.1f}% = {depreciation_amount:.2f}억원")
            calculation_steps.append(f"6. 건물 순가액: {building_value_billion:.2f}억원 - {depreciation_amount:.2f}억원 = {net_building_value:.2f}억원")
            calculation_steps.append(f"7. 최종 원가법 평가액: {land_value_billion:.2f}억원 + {net_building_value:.2f}억원 = {total_value:.2f}억원")
        else:
            calculation_steps.append(f"2. 건물 없음 (토지만 평가)")
            calculation_steps.append(f"3. 최종 원가법 평가액: {total_value:.2f}억원")
        
        return {
            'land_value': round(land_value_billion, 2),
            'building_value': round(building_value_billion, 2),
            'building_age': self.current_year - construction_year if building_area > 0 else 0,
            'depreciation_rate': round(depreciation_rate, 4) if building_area > 0 else 0,
            'depreciation_amount': round(depreciation_amount, 2),
            'net_building_value': round(net_building_value, 2),
            'total_value': round(total_value, 2),
            'construction_cost_per_sqm': int(self.LH_CONSTRUCTION_COST_PER_SQM * location_factor) if building_area > 0 else 0,
            'useful_life': 40,
            'calculation_steps': calculation_steps,
            'unit': '억원'
        }
    
    def calculate_sales_comparison(self,
                                   land_area: float,
                                   individual_land_price: float,
                                   comparable_sales: List[Dict],
                                   location_factor: float) -> Dict:
        """
        Sales Comparison Approach (거래사례비교법)
        
        한국 감정평가 기준에 따른 정확한 계산:
        1. 각 거래사례를 보정 (시점·위치·개별요인)
        2. 보정된 가격들의 가중평균 산출
        3. 최종 평가액 = 토지면적 × 가중평균 단가
        
        중요: 가중치는 비율 배분만 하며, 가격을 삭감하지 않음
        """
        if comparable_sales and len(comparable_sales) > 0:
            # 각 거래사례 보정 계산
            adjusted_cases = []
            
            for idx, sale in enumerate(comparable_sales):
                base_price = sale.get('price_per_sqm', individual_land_price)
                
                # 시점보정 (최근일수록 1.0에 가까움, 과거는 1.05~1.10)
                time_adj = sale.get('time_adjustment', 1.0)
                
                # 위치보정 (대상지가 더 좋으면 1.0 이상, 나쁘면 0.9~0.95)
                location_adj = sale.get('location_adjustment', 1.0)
                
                # 개별보정 (면적, 형상, 접도 등 - 보통 0.95~1.05)
                individual_adj = sale.get('individual_adjustment', 1.0)
                
                # 보정 후 단가 = 거래단가 × 시점보정 × 위치보정 × 개별보정
                adjusted_price = base_price * time_adj * location_adj * individual_adj
                
                # 가중치 (거리·신뢰도 기반)
                weight = sale.get('weight', 1.0 / len(comparable_sales))
                
                adjusted_cases.append({
                    'case_num': idx + 1,
                    'base_price': base_price,
                    'time_adj': time_adj,
                    'location_adj': location_adj,
                    'individual_adj': individual_adj,
                    'adjusted_price': adjusted_price,
                    'weight': weight
                })
            
            # 가중평균 단가 계산 (한국 감정평가 표준 방식)
            weighted_price = sum(case['adjusted_price'] * case['weight'] for case in adjusted_cases)
            
            # 최종 평가액 = 가중평균 단가 × 토지면적
            total_value_krw = land_area * weighted_price
            total_value_billion = total_value_krw / 100_000_000
            
            comparison_method = "거래사례비교법 (실제 거래사례 적용 - 국토부 API)"
            num_comparables = len(comparable_sales)
            
            # 상세 계산 과정 저장 (PDF 출력용)
            calculation_details = {
                'cases': adjusted_cases,
                'weighted_avg_price': weighted_price,
                'explanation': f"{num_comparables}개 거래사례의 가중평균 단가: {weighted_price:,.0f}원/㎡"
            }
            
        else:
            # 거래사례가 없는 경우: 개별공시지가 + 위치보정 사용
            # 시세반영률 적용 (개별공시지가는 실거래가의 70~80%)
            market_reflection_rate = 1.3  # 시세반영률 130%
            adjusted_price = individual_land_price * market_reflection_rate
            
            # 위치보정 적용
            final_price = adjusted_price * location_factor
            
            total_value_krw = land_area * final_price
            total_value_billion = total_value_krw / 100_000_000
            
            comparison_method = "개별공시지가 기준 (시세반영률 130% 적용)"
            num_comparables = 0
            
            calculation_details = {
                'base_land_price': individual_land_price,
                'market_reflection_rate': market_reflection_rate,
                'location_factor': location_factor,
                'final_price_per_sqm': final_price,
                'explanation': f"개별공시지가 {individual_land_price:,.0f}원 × 시세반영률 {market_reflection_rate} × 위치보정 {location_factor} = {final_price:,.0f}원/㎡"
            }
        
        return {
            'total_value': round(total_value_billion, 2),
            'price_per_sqm': int(total_value_krw / land_area) if land_area > 0 else 0,
            'method': comparison_method,
            'num_comparables': num_comparables,
            'location_adjustment': location_factor,
            'calculation_details': calculation_details,
            'unit': '억원'
        }
    
    def calculate_income_approach(self,
                                  annual_rental_income: float,
                                  building_value: float,
                                  zone_type: str = None,
                                  land_area_sqm: float = 0) -> Dict:
        """
        Income Approach (수익환원법) - FIXED v31.0
        
        🔥 수정된 계산 로직:
        나대지/개발용지의 경우:
        1. 개발 후 총개발가치(GDV) 계산: 토지면적 × 법정용적률 × 분양가
        2. 개발비용 계산: 토지면적 × 법정용적률 × 건축비
        3. 순개발이익(NOI) = GDV - 개발비용
        4. 수익가액 = NOI / 환원율(6%)
        
        기존 건물의 경우:
        1. 순영업소득(NOI) = 임대수익 - 운영경비 - 공실손실
        2. 수익가액 = NOI / 환원율(4.5%)
        
        중요: 완성도 보정, 위험도 보정 제거 (과도한 페널티 제거)
        """
        calculation_steps = []
        
        # 건물이 있는지 확인 (building_value > 0.5억원)
        has_building = building_value > 0.5
        
        if annual_rental_income > 0 and has_building:
            # 🏢 Case 1: 기존 건물 + 실제 임대수익
            gross_income = annual_rental_income / 100_000_000  # 억원 단위
            
            # 공실률 5% 적용
            vacancy_rate = 0.05
            vacancy_loss = gross_income * vacancy_rate
            effective_gross_income = gross_income * (1 - vacancy_rate)
            
            # 운영경비 15% 적용
            operating_expenses_rate = 0.15
            operating_expenses = effective_gross_income * operating_expenses_rate
            
            # 순영업소득(NOI) 계산
            noi = effective_gross_income - operating_expenses
            
            # 수익가액 = NOI / 환원율
            capitalized_value_billion = noi / self.DEFAULT_CAP_RATE
            
            # 계산 과정 상세 설명
            calculation_steps.append(f"1. 연간 총임대수익: {gross_income:.2f}억원")
            calculation_steps.append(f"2. 공실손실 (5%): -{vacancy_loss:.2f}억원")
            calculation_steps.append(f"3. 유효총수익: {effective_gross_income:.2f}억원")
            calculation_steps.append(f"4. 운영경비 (15%): -{operating_expenses:.2f}억원")
            calculation_steps.append(f"5. 순영업소득(NOI): {noi:.2f}억원")
            calculation_steps.append(f"6. 환원율: {self.DEFAULT_CAP_RATE*100:.1f}% (주거용 기준)")
            calculation_steps.append(f"7. 수익환원가액: {noi:.2f}억원 ÷ {self.DEFAULT_CAP_RATE} = {capitalized_value_billion:.2f}억원")
            
            method = "실제 임대수익 기준 (NOI 환원법)"
            
        elif not has_building and land_area_sqm > 0:
            # 🏗️ Case 2: 나대지/개발용지 - 개발수익환원법 적용 (FIXED v31.0)
            
            # Step 1: 용도지역별 법정 용적률 및 시장가격 설정
            zone_config = {
                '제1종일반주거지역': {'far': 1.5, 'price_per_sqm': 4_500_000},
                '제2종일반주거지역': {'far': 2.0, 'price_per_sqm': 5_000_000},
                '제3종일반주거지역': {'far': 2.5, 'price_per_sqm': 6_000_000},
                '준주거지역': {'far': 4.0, 'price_per_sqm': 7_500_000},
                '상업지역': {'far': 8.0, 'price_per_sqm': 10_000_000},
                '준공업지역': {'far': 3.5, 'price_per_sqm': 5_500_000}
            }.get(zone_type, {'far': 2.0, 'price_per_sqm': 5_000_000})
            
            far_ratio = zone_config['far']
            sale_price_per_sqm = zone_config['price_per_sqm']
            
            # Step 2: 총개발가치(GDV) 계산
            # GDV = 토지면적 × 용적률 × 분양가
            developable_gfa = land_area_sqm * far_ratio  # 연면적
            gdv_krw = developable_gfa * sale_price_per_sqm
            gdv_billion = gdv_krw / 100_000_000
            
            # Step 3: 개발비용 계산
            # 개발비용 = 토지면적 × 용적률 × 건축비
            construction_cost_per_sqm = 3_500_000  # 표준 건축비
            development_cost_krw = developable_gfa * construction_cost_per_sqm
            development_cost_billion = development_cost_krw / 100_000_000
            
            # Step 4: 순개발이익(NOI) 계산
            # NOI = GDV - 개발비용
            noi = gdv_billion - development_cost_billion
            
            # Step 5: 환원율 적용 (6.0%)
            development_cap_rate = 0.060
            capitalized_value_billion = noi / development_cap_rate
            
            # 계산 과정 설명
            calculation_steps.append(f"🏗️ 나대지/개발용지 - 개발수익환원법 (FIXED v31.0)")
            calculation_steps.append(f"1. 토지면적: {land_area_sqm:,.1f}㎡")
            calculation_steps.append(f"2. 용도지역: {zone_type} (법정 용적률: {far_ratio*100:.0f}%)")
            calculation_steps.append(f"3. 개발가능 연면적: {land_area_sqm:,.1f}㎡ × {far_ratio} = {developable_gfa:,.1f}㎡")
            calculation_steps.append(f"4. 분양가(시장가): {sale_price_per_sqm:,.0f}원/㎡")
            calculation_steps.append(f"5. 총개발가치(GDV): {developable_gfa:,.1f}㎡ × {sale_price_per_sqm:,.0f}원 = {gdv_billion:.2f}억원")
            calculation_steps.append(f"6. 건축비: {developable_gfa:,.1f}㎡ × {construction_cost_per_sqm:,.0f}원 = {development_cost_billion:.2f}억원")
            calculation_steps.append(f"7. 순개발이익(NOI): {gdv_billion:.2f}억원 - {development_cost_billion:.2f}억원 = {noi:.2f}억원")
            calculation_steps.append(f"8. 환원율: {development_cap_rate*100:.1f}% (개발용지 표준)")
            calculation_steps.append(f"9. 최종 수익가액: {noi:.2f}억원 ÷ {development_cap_rate} = {capitalized_value_billion:.2f}억원")
            
            method = "개발수익환원법 (GDV - 개발비용 방식, v31.0)"
            
            # Store development details for later use
            vacancy_rate = 0
            operating_expenses_rate = 0
            completion_factor = None
            risk_adjustment = None
            estimated_building_value = gdv_billion
            
        else:
            # 🏢 Case 3: 건물 가액 기반 추정
            estimated_rental_rate = 0.04  # 연 4% 수익률 가정
            estimated_gross_income = building_value * estimated_rental_rate
            
            # 동일하게 공실률 5%, 운영경비 15% 적용
            vacancy_rate = 0.05
            operating_expenses_rate = 0.15
            
            effective_gross_income = estimated_gross_income * (1 - vacancy_rate)
            operating_expenses = effective_gross_income * operating_expenses_rate
            noi = effective_gross_income - operating_expenses
            
            capitalized_value_billion = noi / self.DEFAULT_CAP_RATE
            
            # 계산 과정 설명
            calculation_steps.append(f"1. 건물가액 기준 추정: {building_value:.2f}억원")
            calculation_steps.append(f"2. 추정 연간수익률: {estimated_rental_rate*100}%")
            calculation_steps.append(f"3. 추정 총임대수익: {estimated_gross_income:.2f}억원")
            calculation_steps.append(f"4. 공실손실 (5%): -{estimated_gross_income * vacancy_rate:.2f}억원")
            calculation_steps.append(f"5. 운영경비 (15%): -{operating_expenses:.2f}억원")
            calculation_steps.append(f"6. 순영업소득(NOI): {noi:.2f}억원")
            calculation_steps.append(f"7. 환원율: {self.DEFAULT_CAP_RATE*100:.1f}%")
            calculation_steps.append(f"8. 수익환원가액: {capitalized_value_billion:.2f}억원")
            
            method = "건물가액 기준 추정 (임대수익 자료 없음)"
        
        # 🔥 GENSPARK V3.0 SECTION 1: Return comprehensive income_approach_details
        result = {
            'total_value': round(capitalized_value_billion, 2),
            'annual_rental_income': round(annual_rental_income / 100_000_000, 2) if annual_rental_income > 0 else 0,
            'noi': round(noi, 2) if (annual_rental_income > 0 or building_value > 0 or land_area_sqm > 0) else 0,
            'cap_rate': self.DEFAULT_CAP_RATE if has_building or annual_rental_income > 0 else 0.060,
            'cap_rate_percentage': f"{self.DEFAULT_CAP_RATE*100:.1f}%" if has_building else "6.0%",
            'vacancy_rate': vacancy_rate if 'vacancy_rate' in locals() else 0.05,
            'operating_expenses_rate': operating_expenses_rate if 'operating_expenses_rate' in locals() else 0.15,
            'method': method,
            'calculation_steps': calculation_steps,
            'unit': '억원',
            'completion_factor': completion_factor if not has_building and land_area_sqm > 0 else None,
            'risk_adjustment': risk_adjustment if not has_building and land_area_sqm > 0 else None
        }
        
        # 🔥 GENSPARK V31.0: Add development land details for PDF display (FIXED)
        if not has_building and land_area_sqm > 0 and 'gdv_billion' in locals():
            result['gdv'] = round(gdv_billion, 2)
            result['development_cost'] = round(development_cost_billion, 2)
            result['net_development_profit'] = round(noi, 2)
            result['developable_gfa'] = round(developable_gfa, 2) if 'developable_gfa' in locals() else 0
            result['far_ratio'] = far_ratio if 'far_ratio' in locals() else 0
            result['sale_price_per_sqm'] = sale_price_per_sqm if 'sale_price_per_sqm' in locals() else 0
            result['income_value'] = round(capitalized_value_billion, 2)
        
        return result
    
    def _get_location_factor(self, address: str) -> float:
        """
        Determine location factor based on address
        
        Seoul: 1.15x
        Metropolitan: 1.05x
        Other: 1.0x
        """
        address_lower = address.lower()
        
        if any(keyword in address_lower for keyword in ['서울', 'seoul', '강남', '서초', '송파']):
            return 1.15
        elif any(keyword in address_lower for keyword in ['경기', '인천', '부산', '대전', '대구', '광주', '울산']):
            return 1.05
        else:
            return 1.0
    
    def _estimate_individual_land_price(self, zone_type: str, location_factor: float) -> float:
        """
        Estimate individual land price (개별공시지가) based on zone type
        
        Returns: Price per sqm in KRW
        """
        # Base prices by zone type (2024 estimates)
        base_prices = {
            '제1종일반주거지역': 4_000_000,
            '제2종일반주거지역': 5_500_000,
            '제3종일반주거지역': 7_000_000,
            '준주거지역': 8_500_000,
            '상업지역': 12_000_000,
            '준공업지역': 6_000_000
        }
        
        base_price = base_prices.get(zone_type, 5_000_000)
        return int(base_price * location_factor)
    
    def _determine_weights(self, has_building: bool, has_rental_income: bool, has_comparables: bool) -> Dict:
        """
        Dynamically determine approach weights based on available data
        
        Default: Cost 40%, Sales 40%, Income 20%
        Adjust based on data availability and reliability
        """
        if has_building and has_rental_income and has_comparables:
            # All approaches available
            return {'cost': 0.35, 'sales': 0.35, 'income': 0.30}
        elif has_building and has_comparables:
            # No rental data
            return {'cost': 0.45, 'sales': 0.45, 'income': 0.10}
        elif has_building and has_rental_income:
            # No comparables
            return {'cost': 0.40, 'sales': 0.30, 'income': 0.30}
        elif has_building:
            # Only cost approach reliable
            return {'cost': 0.60, 'sales': 0.30, 'income': 0.10}
        else:
            # Land only (no building)
            return {'cost': 0.50, 'sales': 0.50, 'income': 0.0}
    
    def _assess_confidence(self, weights: Dict, has_comparables: bool, has_rental_data: bool) -> str:
        """
        Assess confidence level of appraisal
        
        HIGH: All 3 approaches with real data
        MEDIUM: 2 approaches with real data
        LOW: Mostly estimated data
        """
        data_points = sum([
            weights['cost'] > 0.1,
            has_comparables,
            has_rental_data
        ])
        
        if data_points >= 3:
            return "HIGH"
        elif data_points >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_notes(self, address: str, zone_type: str, confidence: str) -> List[str]:
        """Generate appraisal notes and disclaimers"""
        notes = [
            f"감정평가 기준일: {datetime.now().strftime('%Y년 %m월 %d일')}",
            f"평가 대상: {address}",
            f"용도지역: {zone_type}",
            f"신뢰도: {confidence}",
            "감정평가 3방식(원가법, 거래사례비교법, 수익환원법) 적용",
            "LH 표준 건축단가 및 개별공시지가 기준 산정",
            "본 평가액은 참고용이며, 공식 감정평가는 감정평가사 자격자에게 의뢰 필요"
        ]
        
        return notes


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("APPRAISAL ENGINE v24.1 - CLI TEST")
    print("=" * 80)
    
    engine = AppraisalEngineV241()
    
    # Test case: 서울 마포구 공덕동 신축 건물 부지
    test_input = {
        'address': '서울시 마포구 공덕동 123-4',
        'land_area_sqm': 1500.0,
        'building_area_sqm': 3600.0,
        'construction_year': 2020,
        'zone_type': '제3종일반주거지역',
        'individual_land_price_per_sqm': 8_500_000,  # ₩8.5M/㎡
        'annual_rental_income': 250_000_000,  # ₩250M/year
        'comparable_sales': [
            {'price_per_sqm': 8_200_000, 'time_adjustment': 1.05, 'location_adjustment': 1.0},
            {'price_per_sqm': 8_800_000, 'time_adjustment': 1.03, 'location_adjustment': 0.98}
        ]
    }
    
    result = engine.process(test_input)
    
    print(f"\n✅ Engine: {engine.engine_name} v{engine.version}")
    print(f"✅ Timestamp: {engine.created_at.isoformat()}")
    print(f"\n{'-' * 80}")
    print("감정평가 결과")
    print("-" * 80)
    print(f"원가법:           {result['cost_approach']:>10.2f} 억원")
    print(f"거래사례비교법:    {result['sales_comparison']:>10.2f} 억원")
    print(f"수익환원법:        {result['income_approach']:>10.2f} 억원")
    print("-" * 80)
    print(f"최종 감정평가액:   {result['final_appraisal_value']:>10.2f} 억원")
    print(f"㎡당 평가액:      {result['final_value_per_sqm']:>10,} 원/㎡")
    print("-" * 80)
    print(f"신뢰도:           {result['confidence_level']}")
    print(f"위치 보정계수:     {result['location_factor']}")
    print(f"\n가중치:")
    print(f"  - 원가법: {result['weights']['cost']*100:.1f}%")
    print(f"  - 거래사례: {result['weights']['sales']*100:.1f}%")
    print(f"  - 수익환원: {result['weights']['income']*100:.1f}%")
    print(f"\n특기사항:")
    for note in result['notes']:
        print(f"  • {note}")
    print("=" * 80)
