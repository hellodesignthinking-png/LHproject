"""
ZeroSite Expert v3 - Enhanced Land Valuation Engine v9.1

Integrates GenSpark AI enhanced backend services for improved accuracy
Provides standalone land valuation with dynamic transaction generation

Features:
- Enhanced mode: Uses algorithms from backend/services/ (recommended)
- Dynamic transaction generation with price gradients
- Professional 4-factor weighted adjustments (거리/시점/규모/용도)
- Advanced 4-factor confidence scoring (표본수/가격분산/거리/최신성)

Author: ZeroSite Development Team + GenSpark AI
Date: 2025-12-10
Version: v9.1 Enhanced
"""

from typing import Dict, List, Optional, Any, Tuple
import statistics
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LandValuationEngineV91:
    """
    Enhanced Land Valuation Engine v9.1
    
    Integrates GenSpark AI backend services for professional land appraisal
    
    Process:
    1. Enhanced Geocoding (comprehensive Korean coverage)
    2. Dynamic Transaction Generation (distance/time-based gradients)
    3. Professional 4-Factor Price Adjustment (35/25/25/15% weighting)
    4. Advanced Confidence Scoring (30/30/25/15% weighting)
    5. Financial Analysis & Negotiation Strategies
    """
    
    def __init__(self, use_enhanced_services: bool = True):
        """
        Initialize valuation engine
        
        Args:
            use_enhanced_services: Toggle between enhanced and legacy algorithms
        """
        self.use_enhanced = use_enhanced_services
        
        if self.use_enhanced:
            # Import enhanced services from backend/services/
            try:
                import sys
                import os
                # Add backend to path
                backend_path = os.path.join(os.path.dirname(__file__), '../..')
                if backend_path not in sys.path:
                    sys.path.insert(0, backend_path)
                
                from backend.services.geocoding import EnhancedGeocodingService
                from backend.services.transaction_generator import EnhancedTransactionGenerator
                from backend.services.price_adjuster import EnhancedPriceAdjuster
                from backend.services.confidence_calculator import EnhancedConfidenceCalculator
                
                self.geocoding_service = EnhancedGeocodingService()
                self.transaction_gen = EnhancedTransactionGenerator()
                self.price_adjuster = EnhancedPriceAdjuster()
                self.confidence_calc = EnhancedConfidenceCalculator()
                
                logger.info("✅ Enhanced services loaded (GenSpark AI)")
                logger.info("   ├─ Dynamic Transaction Generator")
                logger.info("   ├─ 4-Factor Price Adjuster (35/25/25/15%)")
                logger.info("   ├─ Advanced Confidence Calculator (30/30/25/15%)")
                logger.info("   └─ Enhanced Geocoding Service")
                
            except Exception as e:
                logger.error(f"⚠️ Failed to load enhanced services: {e}")
                logger.warning("   Falling back to legacy mode")
                self.use_enhanced = False
                self._init_legacy_services()
        else:
            logger.info("⚠️ Legacy mode (v9.0 original)")
            self._init_legacy_services()
    
    def _init_legacy_services(self):
        """Initialize legacy services (placeholder)"""
        self.geocoding_service = None
        self.transaction_gen = None
        self.price_adjuster = None
        self.confidence_calc = None
    
    def evaluate_land(
        self,
        address: str,
        land_size_sqm: float,
        zone_type: str,
        asking_price: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main land valuation method
        
        Args:
            address: Korean address
            land_size_sqm: Land size in square meters
            zone_type: Zone type (용도지역)
            asking_price: Optional asking price for comparison
            **kwargs: Additional parameters (contract_months, etc.)
        
        Returns:
            Complete valuation result dictionary
        """
        
        if self.use_enhanced:
            return self._evaluate_with_enhanced_services(
                address, land_size_sqm, zone_type, asking_price, **kwargs
            )
        else:
            raise NotImplementedError("Legacy mode not yet implemented. Use use_enhanced_services=True")
    
    def _evaluate_with_enhanced_services(
        self,
        address: str,
        land_size_sqm: float,
        zone_type: str,
        asking_price: Optional[float],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Valuation using enhanced backend services
        
        Process:
        1. Enhanced Geocoding
        2. Dynamic Transaction Generation
        3. Professional 4-Factor Price Adjustment
        4. Advanced Confidence Scoring
        5. Financial Analysis
        6. Negotiation Strategies
        """
        
        logger.info("="*80)
        logger.info("🎯 Land Valuation Engine v9.1 Enhanced - Starting Analysis")
        logger.info(f"   Address: {address}")
        logger.info(f"   Size: {land_size_sqm:,.1f}m²")
        logger.info(f"   Zone: {zone_type}")
        logger.info("="*80)
        
        # Step 1: Enhanced Geocoding
        logger.info("📍 Step 1: Enhanced Geocoding")
        coords = self.geocoding_service.geocode(address)
        logger.info(f"   ✓ Location: ({coords.lat}, {coords.lng})")
        logger.info(f"   ✓ Region: {coords.region} {coords.district}")
        
        # Step 2: Determine search radius
        search_radius = self._get_search_radius(coords.region)
        logger.info(f"   ✓ Search radius: {search_radius}km")
        
        # Step 3: Generate transactions dynamically
        logger.info("🔄 Step 2: Dynamic Transaction Generation")
        transactions = self.transaction_gen.generate_comparables(
            center_lat=coords.lat,
            center_lng=coords.lng,
            region=coords.region,
            district=coords.district,
            target_zone=zone_type,
            target_size_sqm=land_size_sqm,
            radius_km=search_radius,
            count=10
        )
        logger.info(f"   ✓ Generated {len(transactions)} comparable transactions")
        
        # Step 4: Apply professional 4-factor adjustments
        logger.info("⚖️ Step 3: Professional 4-Factor Price Adjustment")
        adjusted_transactions = self.price_adjuster.adjust_transactions(
            transactions=transactions,
            target_size_sqm=land_size_sqm,
            target_zone=zone_type
        )
        logger.info(f"   ✓ Applied adjustments (Distance 35%, Time 25%, Size 25%, Zone 15%)")
        
        # Step 5: Calculate predicted price
        logger.info("💰 Step 4: Price Prediction")
        prediction = self._calculate_price_prediction(
            adjusted_transactions, land_size_sqm
        )
        logger.info(f"   ✓ Predicted price: ₩{prediction['avg']:,.0f}")
        logger.info(f"   ✓ Price range: ₩{prediction['low']:,.0f} ~ ₩{prediction['high']:,.0f}")
        
        # Step 6: Calculate advanced confidence score
        logger.info("📊 Step 5: Advanced Confidence Scoring")
        adjusted_prices = [at.adjusted_price_per_sqm for at in adjusted_transactions]
        distances = [at.transaction.distance_km for at in adjusted_transactions]
        days_since = [at.transaction.days_since_transaction for at in adjusted_transactions]
        
        confidence, conf_level = self.confidence_calc.calculate_confidence(
            transaction_count=len(adjusted_transactions),
            adjusted_prices=adjusted_prices,
            average_price=prediction['price_per_sqm_avg'],
            distances_km=distances,
            days_since_transactions=days_since
        )
        
        prediction['confidence'] = confidence
        prediction['confidence_level'] = conf_level.value
        logger.info(f"   ✓ Confidence: {confidence:.0%} ({conf_level.value})")
        
        # Step 7: Format comparables for output
        logger.info("📋 Step 6: Format Comparables")
        comparables = self._format_comparables(adjusted_transactions)
        logger.info(f"   ✓ Formatted {len(comparables)} comparables")
        
        # Step 8: Financial analysis
        logger.info("💵 Step 7: Financial Analysis")
        financial = self._calculate_financial_summary(
            prediction['avg'],
            kwargs.get('contract_months', 6)
        )
        logger.info(f"   ✓ Total acquisition cost: ₩{financial['total_cost']:,.0f}")
        
        # Step 9: Asking price analysis
        asking_analysis = None
        if asking_price and asking_price > 0:
            logger.info("📈 Step 8: Asking Price Analysis")
            asking_analysis = self._analyze_asking_price(
                asking_price, prediction['avg']
            )
            logger.info(f"   ✓ Status: {asking_analysis['status']} ({asking_analysis['percentage']:+.1f}%)")
        
        # Step 10: Generate negotiation strategies
        logger.info("🎯 Step 9: Negotiation Strategies")
        strategies = self._generate_negotiation_strategies(
            prediction['avg'],
            adjusted_transactions,
            asking_price,
            land_size_sqm
        )
        logger.info(f"   ✓ Generated {len(strategies)} strategies")
        
        logger.info("="*80)
        logger.info("✅ Land Valuation Complete")
        logger.info("="*80)
        
        # Assemble result
        return {
            'address': address,
            'coordinates': {
                'lat': coords.lat,
                'lng': coords.lng,
                'region': coords.region,
                'district': coords.district
            },
            'land_size_sqm': land_size_sqm,
            'zone_type': zone_type,
            'prediction': prediction,
            'asking_analysis': asking_analysis,
            'comparables': comparables,
            'financial': financial,
            'strategies': strategies,
            'mode': 'enhanced',
            'version': 'v9.1',
            'enhanced_features': {
                'dynamic_transactions': True,
                'weighted_adjustments': True,
                'advanced_confidence': True,
                'adjustment_weights': {
                    'distance': '35%',
                    'time': '25%',
                    'size': '25%',
                    'zone': '15%'
                },
                'confidence_weights': {
                    'sample_size': '30%',
                    'price_variance': '30%',
                    'distance': '25%',
                    'recency': '15%'
                }
            }
        }
    
    def _get_search_radius(self, region: str) -> float:
        """Get search radius based on region"""
        radius_map = {
            "서울특별시": 1.0,
            "인천광역시": 1.5,
            "경기도": 2.0,
            "부산광역시": 2.0,
            "대구광역시": 2.0,
            "대전광역시": 2.0,
            "광주광역시": 2.0,
            "울산광역시": 2.0
        }
        return radius_map.get(region, 3.0)
    
    def _calculate_price_prediction(
        self,
        adjusted_transactions: List,
        target_size: float
    ) -> Dict[str, float]:
        """
        Calculate price prediction with range
        
        Method:
        1. Extract adjusted prices
        2. Remove outliers (IQR method)
        3. Calculate mean and std dev
        4. Return low/avg/high range
        """
        # Extract prices
        prices = [at.adjusted_price_per_sqm for at in adjusted_transactions]
        
        # Remove outliers using IQR
        filtered_prices = self._remove_outliers_iqr(prices)
        
        # Statistics
        avg_price_per_sqm = statistics.mean(filtered_prices)
        std_dev = statistics.stdev(filtered_prices) if len(filtered_prices) > 1 else 0
        
        # Price range (±1 std dev)
        low_price_per_sqm = avg_price_per_sqm - std_dev
        high_price_per_sqm = avg_price_per_sqm + std_dev
        
        # Total prices
        avg_total = avg_price_per_sqm * target_size
        low_total = low_price_per_sqm * target_size
        high_total = high_price_per_sqm * target_size
        
        return {
            'low': low_total,
            'avg': avg_total,
            'high': high_total,
            'price_per_sqm_avg': avg_price_per_sqm,
            'price_per_sqm_low': low_price_per_sqm,
            'price_per_sqm_high': high_price_per_sqm,
            'price_per_sqm_std': std_dev,
            'confidence': 0.0  # Will be filled by confidence calculator
        }
    
    def _remove_outliers_iqr(self, prices: List[float]) -> List[float]:
        """Remove outliers using Interquartile Range method"""
        if len(prices) < 4:
            return prices
        
        sorted_prices = sorted(prices)
        n = len(sorted_prices)
        
        q1 = sorted_prices[n // 4]
        q3 = sorted_prices[(3 * n) // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        filtered = [p for p in prices if lower_bound <= p <= upper_bound]
        
        return filtered if filtered else prices
    
    def _format_comparables(self, adjusted_transactions: List) -> List[Dict]:
        """Format adjusted transactions for API output"""
        result = []
        
        for adj in adjusted_transactions:
            txn = adj.transaction
            factors = adj.factors
            
            result.append({
                'address': txn.address,
                'distance_km': round(txn.distance_km, 2),
                'size_sqm': round(txn.size_sqm, 1),
                'zone_type': txn.zone_type,
                'price_per_sqm': int(txn.price_per_sqm),
                'total_price': int(txn.total_price),
                'transaction_date': txn.transaction_date.strftime('%Y-%m-%d'),
                'days_ago': txn.days_since_transaction,
                'adjustments': {
                    'distance': f"{factors.distance*100:+.1f}%",
                    'time': f"{factors.time*100:+.1f}%",
                    'size': f"{factors.size*100:+.1f}%",
                    'zone': f"{factors.zone*100:+.1f}%",
                    'total': f"{factors.total*100:+.1f}%"
                },
                'adjusted_price_per_sqm': int(adj.adjusted_price_per_sqm),
                'adjusted_total_price': int(adj.adjusted_total_price)
            })
        
        return result
    
    def _calculate_financial_summary(
        self,
        land_price: float,
        contract_months: int = 6
    ) -> Dict[str, float]:
        """
        Calculate total acquisition cost
        
        Components:
        - Land price
        - Acquisition tax (5%)
        - Legal cost (0.3%)
        - Interest (LTV 60%, 5.25% annual)
        """
        # Financial constants
        LTV = 0.60
        ANNUAL_RATE = 0.0525
        TAX_RATE = 0.05
        LEGAL_RATE = 0.003
        
        acquisition_tax = land_price * TAX_RATE
        legal_cost = land_price * LEGAL_RATE
        loan_amount = land_price * LTV
        interest_cost = loan_amount * ANNUAL_RATE * (contract_months / 12.0)
        
        total_cost = land_price + acquisition_tax + legal_cost + interest_cost
        
        return {
            'land_price': land_price,
            'acquisition_tax': acquisition_tax,
            'legal_cost': legal_cost,
            'interest_cost': interest_cost,
            'loan_amount': loan_amount,
            'equity_required': land_price - loan_amount,
            'total_cost': total_cost,
            'ltv': LTV,
            'annual_rate': ANNUAL_RATE
        }
    
    def _analyze_asking_price(
        self,
        asking_price: float,
        predicted_price: float
    ) -> Dict[str, Any]:
        """Analyze asking price vs predicted price"""
        difference = asking_price - predicted_price
        percentage = (difference / predicted_price) * 100
        
        if percentage > 5:
            status = "고가 (협상 필요)"
            emoji = "🔴"
        elif percentage < -5:
            status = "저가 (매수 추천)"
            emoji = "🔵"
        else:
            status = "적정가"
            emoji = "🟢"
        
        return {
            'asking_price': asking_price,
            'predicted_price': predicted_price,
            'difference': difference,
            'percentage': percentage,
            'status': status,
            'emoji': emoji
        }
    
    def _generate_negotiation_strategies(
        self,
        predicted_avg: float,
        adjusted_transactions: List,
        asking_price: Optional[float],
        land_size_sqm: float
    ) -> List[Dict]:
        """Generate 3 negotiation strategies"""
        strategies = []
        
        # Strategy 1: Market average
        strategies.append({
            'name': '시장평균가 제시',
            'price': predicted_avg,
            'price_per_sqm': predicted_avg / land_size_sqm,
            'conditions': '일반 매매 조건',
            'rationale': f'{len(adjusted_transactions)}건 거래사례 평균 기반, 객관적 시장가'
        })
        
        # Strategy 2: Top 3 average
        top_3_prices = sorted(
            [at.adjusted_price_per_sqm for at in adjusted_transactions],
            reverse=True
        )[:3]
        top_3_avg = statistics.mean(top_3_prices)
        top_3_total = top_3_avg * land_size_sqm
        
        strategies.append({
            'name': '상위 3건 평균가 제시 (권장)',
            'price': top_3_total,
            'price_per_sqm': top_3_avg,
            'conditions': '1개월 내 신속 계약',
            'rationale': '최근 고가 거래 기반, 빠른 거래 인센티브'
        })
        
        # Strategy 3: Compromise or discount
        if asking_price and asking_price > predicted_avg:
            face_saving = (asking_price + predicted_avg) / 2
            strategies.append({
                'name': '중도가 제시',
                'price': face_saving,
                'price_per_sqm': face_saving / land_size_sqm,
                'conditions': '중도금 일정 조정',
                'rationale': '매도자 체면 세워주면서 시장가 근접'
            })
        else:
            discount_price = predicted_avg * 0.95
            strategies.append({
                'name': '시장가 대비 5% 할인',
                'price': discount_price,
                'price_per_sqm': discount_price / land_size_sqm,
                'conditions': '현금 즉시 결제',
                'rationale': '빠른 현금화 조건으로 할인 협상'
            })
        
        return strategies


# ============================================================================
# BACKWARD COMPATIBILITY ALIAS
# ============================================================================

class LandValuationEngine(LandValuationEngineV91):
    """Alias for backward compatibility"""
    pass


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Test enhanced mode
    print("\n" + "="*80)
    print("Testing Land Valuation Engine v9.1 Enhanced")
    print("="*80 + "\n")
    
    try:
        engine = LandValuationEngineV91(use_enhanced_services=True)
        
        result = engine.evaluate_land(
            address="서울특별시 강남구 역삼동 123-45",
            land_size_sqm=1000.0,
            zone_type="제2종일반주거지역",
            asking_price=10_000_000_000,
            contract_months=6
        )
        
        print(f"\n{'='*80}")
        print("📊 VALUATION RESULTS")
        print(f"{'='*80}\n")
        
        print(f"🏠 주소: {result['address']}")
        print(f"📍 좌표: ({result['coordinates']['lat']}, {result['coordinates']['lng']})")
        print(f"🗺️ 지역: {result['coordinates']['region']} {result['coordinates']['district']}")
        print(f"📐 면적: {result['land_size_sqm']:,.1f}m²")
        print(f"🏘️ 용도: {result['zone_type']}")
        
        print(f"\n💰 예상가:")
        print(f"   최저가: ₩{result['prediction']['low']:,.0f}")
        print(f"   평균가: ₩{result['prediction']['avg']:,.0f} ⭐")
        print(f"   최고가: ₩{result['prediction']['high']:,.0f}")
        
        print(f"\n📊 신뢰도: {result['prediction']['confidence']:.0%} ({result['prediction']['confidence_level']})")
        print(f"📋 거래사례: {len(result['comparables'])}건")
        print(f"⚙️ 모드: {result['mode']} (v{result['version']})")
        
        if 'enhanced_features' in result:
            print(f"\n✨ Enhanced Features:")
            print(f"   ✓ Dynamic Transaction Generation")
            print(f"   ✓ Weighted Adjustments: {result['enhanced_features']['adjustment_weights']}")
            print(f"   ✓ Advanced Confidence: {result['enhanced_features']['confidence_weights']}")
        
        if result.get('asking_analysis'):
            print(f"\n📈 요청가 분석:")
            print(f"   요청가: ₩{result['asking_analysis']['asking_price']:,.0f}")
            print(f"   차액: ₩{result['asking_analysis']['difference']:,.0f} ({result['asking_analysis']['percentage']:+.1f}%)")
            print(f"   판단: {result['asking_analysis']['emoji']} {result['asking_analysis']['status']}")
        
        print(f"\n💵 필요 자금:")
        print(f"   토지가: ₩{result['financial']['land_price']:,.0f}")
        print(f"   총비용: ₩{result['financial']['total_cost']:,.0f}")
        
        print(f"\n🎯 협상전략: {len(result['strategies'])}가지")
        for i, strategy in enumerate(result['strategies'], 1):
            print(f"   {i}. {strategy['name']}: ₩{strategy['price']:,.0f}")
        
        print(f"\n{'='*80}")
        print("✅ Test Complete!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
