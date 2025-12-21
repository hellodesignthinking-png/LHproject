"""
M2 Appraisal Service
====================

토지감정평가 서비스 (🔒 IMMUTABLE)

이 서비스는 CanonicalLandContext를 입력받아
AppraisalContext를 생성하고 LOCK합니다.

⚠️ CRITICAL: 
- 이 파일의 로직은 기존 land_valuation_engine_v9_1.py를 그대로 이동
- 함수 내용 수정 금지 (import와 반환 타입만 변경)
- AppraisalContext는 frozen=True로 생성 후 수정 불가

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from typing import Dict, List, Optional, Any
import statistics
from datetime import datetime
import logging

from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.appraisal_context import (
    AppraisalContext,
    TransactionSample,
    PremiumFactors,
    ConfidenceMetrics
)

logger = logging.getLogger(__name__)


class AppraisalService:
    """
    토지감정평가 서비스
    
    🔒 이 서비스가 반환하는 AppraisalContext는
    생성 후 절대 수정할 수 없습니다 (frozen=True)
    """
    
    def __init__(self, use_enhanced_services: bool = True):
        """
        감정평가 서비스 초기화
        
        Args:
            use_enhanced_services: GenSpark AI 서비스 사용 여부
        """
        self.use_enhanced = use_enhanced_services
        
        if self.use_enhanced:
            try:
                # GenSpark AI Enhanced Services 로드
                from app.modules.m2_appraisal.adapters.geocoding_adapter import EnhancedGeocodingService
                from app.modules.m2_appraisal.transaction.generator import EnhancedTransactionGenerator
                from app.modules.m2_appraisal.premium.price_adjuster import EnhancedPriceAdjuster
                from app.modules.m2_appraisal.premium.confidence_score import EnhancedConfidenceCalculator
                
                self.geocoding_service = EnhancedGeocodingService()
                self.transaction_gen = EnhancedTransactionGenerator()
                self.price_adjuster = EnhancedPriceAdjuster()
                self.confidence_calc = EnhancedConfidenceCalculator()
                
                logger.info("✅ M2 Appraisal Service initialized (Enhanced mode)")
                logger.info("   ├─ GenSpark AI services loaded")
                logger.info("   ├─ Dynamic Transaction Generator")
                logger.info("   ├─ 4-Factor Price Adjuster (35/25/25/15%)")
                logger.info("   └─ Advanced Confidence Calculator")
                
            except Exception as e:
                logger.error(f"⚠️ Failed to load enhanced services: {e}")
                logger.warning("   Falling back to legacy mode")
                self.use_enhanced = False
                self._init_legacy_services()
        else:
            logger.info("⚠️ M2 Appraisal Service initialized (Legacy mode)")
            self._init_legacy_services()
    
    def _init_legacy_services(self):
        """Legacy 서비스 초기화 (placeholder)"""
        self.geocoding_service = None
        self.transaction_gen = None
        self.price_adjuster = None
        self.confidence_calc = None
    
    def run(
        self,
        land_ctx: CanonicalLandContext,
        asking_price: Optional[float] = None
    ) -> AppraisalContext:
        """
        토지감정평가 실행 (M2 모듈 메인 메서드)
        
        Args:
            land_ctx: M1에서 생성된 토지정보 Context
            asking_price: 호가 (있는 경우)
        
        Returns:
            AppraisalContext (🔒 frozen=True, 수정 불가)
        
        ⚠️ 이 메서드가 반환하는 AppraisalContext는
        생성 후 절대 수정할 수 없습니다!
        """
        
        logger.info("="*80)
        logger.info("🔒 M2 APPRAISAL MODULE - Starting Valuation")
        logger.info(f"   Address: {land_ctx.address}")
        logger.info(f"   Size: {land_ctx.area_sqm:,.1f}m²")
        logger.info(f"   Zone: {land_ctx.zone_type}")
        logger.info("="*80)
        
        if self.use_enhanced:
            return self._run_enhanced(land_ctx, asking_price)
        else:
            return self._run_legacy(land_ctx, asking_price)
    
    def _run_enhanced(
        self,
        land_ctx: CanonicalLandContext,
        asking_price: Optional[float]
    ) -> AppraisalContext:
        """
        Enhanced 모드 감정평가
        
        기존 land_valuation_engine_v9_1.py의 로직을 그대로 사용
        """
        
        # Step 1: Geocoding (이미 land_ctx에 좌표 있음, 재확인만)
        logger.info("📍 Step 1: Location Verification")
        lat, lng = land_ctx.coordinates
        logger.info(f"   ✓ Coordinates: ({lat}, {lng})")
        logger.info(f"   ✓ Region: {land_ctx.sido} {land_ctx.sigungu}")
        
        # Step 2: 검색 반경 결정
        search_radius = self._get_search_radius(land_ctx.sido)
        logger.info(f"   ✓ Search radius: {search_radius}km")
        
        # Step 3: 거래사례 동적 생성
        logger.info("🔄 Step 2: Dynamic Transaction Generation")
        transactions = self.transaction_gen.generate_comparables(
            center_lat=lat,
            center_lng=lng,
            region=land_ctx.sido,
            district=land_ctx.sigungu,
            target_zone=land_ctx.zone_type,
            target_size_sqm=land_ctx.area_sqm,
            radius_km=search_radius,
            count=10,
            seed=42  # 🔧 Use fixed seed for deterministic generation
        )
        logger.info(f"   ✓ Generated {len(transactions)} transactions")
        
        # Step 4: 4-Factor 가격 조정
        logger.info("⚖️ Step 3: 4-Factor Price Adjustment")
        adjusted_transactions = self.price_adjuster.adjust_transactions(
            transactions=transactions,
            target_size_sqm=land_ctx.area_sqm,
            target_zone=land_ctx.zone_type
        )
        logger.info(f"   ✓ Applied adjustments (35/25/25/15%)")
        
        # Step 5: 가격 예측
        logger.info("💰 Step 4: Price Prediction")
        prediction = self._calculate_price_prediction(
            adjusted_transactions,
            land_ctx.area_sqm
        )
        logger.info(f"   ✓ Predicted: ₩{prediction['avg']:,.0f}")
        
        # Step 6: 신뢰도 계산
        logger.info("📊 Step 5: Confidence Scoring")
        adjusted_prices = [t.adjusted_price_per_sqm for t in adjusted_transactions]
        distances = [t.transaction.distance_km for t in adjusted_transactions]
        days_since = [t.transaction.days_since_transaction for t in adjusted_transactions]
        
        confidence, conf_level = self.confidence_calc.calculate_confidence(
            transaction_count=len(adjusted_transactions),
            adjusted_prices=adjusted_prices,
            average_price=prediction['price_per_sqm_avg'],
            distances_km=distances,
            days_since_transactions=days_since
        )
        logger.info(f"   ✓ Confidence: {confidence:.0%} ({conf_level})")
        
        # Step 7: 프리미엄 계산
        premium_factors = self._calculate_premium_factors(
            land_ctx, adjusted_transactions
        )
        
        # Step 8: TransactionSample 객체 생성
        transaction_samples = []
        for t in adjusted_transactions:
            # 거래 일자를 문자열로 변환
            trans_date = t.transaction.transaction_date
            if isinstance(trans_date, datetime):
                trans_date_str = trans_date.strftime("%Y-%m-%d")
            else:
                trans_date_str = str(trans_date)
            
            transaction_samples.append(
                TransactionSample(
                    address=t.transaction.address,
                    transaction_date=trans_date_str,
                    price_total=t.transaction.total_price,
                    price_per_sqm=t.transaction.price_per_sqm,
                    area_sqm=t.transaction.size_sqm,
                    distance_km=t.transaction.distance_km,
                    zone_type=t.transaction.zone_type,
                    adjusted_price_per_sqm=t.adjusted_price_per_sqm,
                    adjustment_factors={
                        "distance": t.factors.distance,
                        "time": t.factors.time,
                        "size": t.factors.size,
                        "zone": t.factors.zone,
                        "total": t.factors.total
                    }
                )
            )
        
        # Step 9: ConfidenceMetrics 객체 생성
        confidence_level_str = conf_level.value if hasattr(conf_level, 'value') else str(conf_level)
        confidence_metrics = ConfidenceMetrics(
            sample_count_score=confidence * 0.3,
            price_variance_score=confidence * 0.3,
            distance_score=confidence * 0.25,
            recency_score=confidence * 0.15,
            confidence_score=confidence,
            confidence_level=confidence_level_str
        )
        
        # Step 10: 경고 시스템 (Production Enhancement)
        logger.info("⚠️  Step 6: Warning System Check")
        warnings = []
        
        transaction_count = len(transaction_samples)
        if transaction_count < 3:
            warning = {
                "type": "LOW_SAMPLE_COUNT",
                "severity": "CAUTION",
                "message": "거래사례 수가 제한적이므로 감정가 해석에 유의가 필요합니다.",
                "recommendation": "추가 거래사례 확보 또는 전문가 검증을 권장합니다.",
                "sample_count": transaction_count,
                "min_recommended": 3
            }
            warnings.append(warning)
            logger.warning(f"   ⚠️  LOW SAMPLE WARNING: Only {transaction_count} cases (min 3 recommended)")
        else:
            logger.info(f"   ✓ Sample count OK: {transaction_count} cases")
        
        # Step 11: AppraisalContext 생성 및 LOCK 🔒
        logger.info("🔒 Step 7: Creating AppraisalContext (IMMUTABLE)")
        
        appraisal_context = AppraisalContext(
            # 핵심 감정평가 결과
            land_value=prediction['avg'],
            unit_price_sqm=prediction['price_per_sqm_avg'],
            unit_price_pyeong=prediction['price_per_sqm_avg'] * 3.3058,
            
            # 기준가
            official_price=land_ctx.area_sqm * 1_000_000,  # Mock (실제는 공시지가 API)
            official_price_per_sqm=1_000_000,
            
            # 거래사례
            transaction_samples=transaction_samples,
            transaction_count=len(transaction_samples),
            avg_transaction_price=prediction['price_per_sqm_avg'],
            
            # 프리미엄
            premium_factors=premium_factors,
            premium_rate=premium_factors.total_premium_rate,
            
            # 신뢰도
            confidence_metrics=confidence_metrics,
            confidence_score=confidence,
            confidence_level=confidence_level_str,
            
            # 가격 범위
            price_range_low=prediction['low'],
            price_range_high=prediction['high'],
            
            # 협상 전략 (생성 로직 생략, 간단히)
            negotiation_strategies=[
                {"type": "aggressive", "price": prediction['low']},
                {"type": "balanced", "price": prediction['avg']},
                {"type": "conservative", "price": prediction['high']}
            ],
            
            # 메타데이터
            valuation_date=datetime.now().strftime("%Y-%m-%d"),
            valuation_method="거래사례비교법 (4-Factor Enhanced)",
            appraiser="ZeroSite AI Engine v9.1 (Refactored M2)",
            
            # 호가 비교
            asking_price=asking_price,
            price_gap_pct=((asking_price - prediction['avg']) / prediction['avg'] * 100) if asking_price else None,
            recommendation=self._get_recommendation(asking_price, prediction['avg']) if asking_price else None,
            
            # 경고 시스템 (Production Enhancement)
            warnings=warnings
        )
        
        logger.info("✅ AppraisalContext created and LOCKED (frozen=True)")
        logger.info("   ⚠️ This context is now IMMUTABLE!")
        
        if appraisal_context.has_warnings:
            logger.warning(f"   ⚠️  {len(appraisal_context.warnings)} warning(s) attached")
            for w in appraisal_context.warnings:
                logger.warning(f"      - {w['type']}: {w['message']}")
        
        logger.info("="*80)
        
        return appraisal_context
    
    def _run_legacy(
        self,
        land_ctx: CanonicalLandContext,
        asking_price: Optional[float]
    ) -> AppraisalContext:
        """Legacy 모드 (미구현)"""
        raise NotImplementedError("Legacy mode not yet implemented")
    
    def _get_search_radius(self, region: str) -> float:
        """검색 반경 결정"""
        if "서울" in region:
            return 2.0
        elif any(city in region for city in ["경기", "인천"]):
            return 3.0
        else:
            return 5.0
    
    def _calculate_price_prediction(
        self,
        adjusted_transactions: List[Any],
        land_size_sqm: float
    ) -> Dict[str, float]:
        """가격 예측 계산"""
        prices = [t.adjusted_price_per_sqm for t in adjusted_transactions]
        
        avg_price_per_sqm = statistics.mean(prices)
        low_price_per_sqm = min(prices)
        high_price_per_sqm = max(prices)
        
        return {
            'avg': avg_price_per_sqm * land_size_sqm,
            'low': low_price_per_sqm * land_size_sqm,
            'high': high_price_per_sqm * land_size_sqm,
            'price_per_sqm_avg': avg_price_per_sqm,
            'price_per_sqm_low': low_price_per_sqm,
            'price_per_sqm_high': high_price_per_sqm
        }
    
    def _calculate_premium_factors(
        self,
        land_ctx: CanonicalLandContext,
        adjusted_transactions: List[Any]
    ) -> PremiumFactors:
        """프리미엄 요인 계산"""
        # 도로 점수 (0-10)
        road_score = min(land_ctx.road_width / 2, 10)
        
        # 지형 점수 (0-10)
        terrain_score = {
            "평지": 10,
            "고지": 7,
            "저지": 5
        }.get(land_ctx.terrain_height, 7)
        
        # 입지 점수 (간단히 7로 설정, 실제는 POI 기반)
        location_score = 7
        accessibility_score = 7
        
        # 프리미엄 계산 (간단히)
        distance_premium = 0.05  # 5%
        time_premium = 0.03      # 3%
        size_premium = 0.02      # 2%
        zone_premium = 0.05      # 5%
        
        total_premium_rate = (distance_premium + time_premium + 
                             size_premium + zone_premium) * 100
        
        return PremiumFactors(
            road_score=road_score,
            terrain_score=terrain_score,
            location_score=location_score,
            accessibility_score=accessibility_score,
            distance_premium=distance_premium,
            time_premium=time_premium,
            size_premium=size_premium,
            zone_premium=zone_premium,
            total_premium_rate=total_premium_rate
        )
    
    def _get_recommendation(self, asking_price: float, land_value: float) -> str:
        """호가 대비 추천"""
        gap_pct = (asking_price - land_value) / land_value * 100
        
        if gap_pct < -10:
            return "🔵 저가 (매수 강력 추천)"
        elif gap_pct < 0:
            return "🟢 저가 (매수 추천)"
        elif gap_pct < 10:
            return "🟡 적정가"
        elif gap_pct < 20:
            return "🟠 고가 (신중)"
        else:
            return "🔴 고가 (매수 불가)"
