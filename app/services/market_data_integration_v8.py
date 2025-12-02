#!/usr/bin/env python3
"""
ZeroSite v8.0 - Market Data Integration Service
================================================

Integrates external API data into comprehensive land analysis:
- Real estate transaction analysis
- Crime risk assessment
- Environmental impact evaluation
- LH pricing comparison

Author: ZeroSite Development Team
Date: 2025-12-02
Version: v8.0
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import statistics
from datetime import datetime

from app.services.external_api_client import (
    ExternalAPIClient,
    RealEstateTransaction,
    CrimeRiskData,
    EnvironmentalData,
    calculate_lh_pricing_gap,
    score_location_safety,
    score_environmental_risk
)


@dataclass
class MarketAnalysisV8:
    """v8.0 시장 분석 결과"""
    
    # 실거래가 분석
    avg_land_price_per_sqm: int
    median_land_price_per_sqm: int
    land_price_range: tuple  # (min, max)
    recent_transactions_count: int
    market_activity_level: str  # 매우활발/활발/보통/저조
    
    # 아파트 시장 분석
    avg_apt_price_per_sqm: int
    apt_transaction_volume: int
    avg_rent_yield: float
    
    # LH 매입가 비교
    lh_pricing_gap: Dict
    lh_feasibility_score: float  # 0-100
    
    # 안전 분석
    crime_risk_data: CrimeRiskData
    safety_analysis: Dict
    
    # 환경 분석
    environmental_data: EnvironmentalData
    environmental_analysis: Dict
    
    # 종합 평가
    overall_market_score: float  # 0-100
    investment_grade: str  # A+/A/B+/B/C/D/F
    key_findings: List[str]
    risk_warnings: List[str]
    recommendations: List[str]


class MarketDataIntegrationV8:
    """v8.0 시장 데이터 통합 서비스"""
    
    def __init__(
        self,
        molit_api_key: str = None,
        safemap_api_key: str = None
    ):
        """Initialize with API keys"""
        self.api_client = ExternalAPIClient(
            molit_api_key=molit_api_key,
            safemap_api_key=safemap_api_key
        )
    
    def analyze_comprehensive_market(
        self,
        address: str,
        land_area: float,
        lat: float,
        lng: float,
        lh_purchase_price: Optional[int] = None
    ) -> MarketAnalysisV8:
        """
        종합 시장 분석 수행
        
        Args:
            address: 토지 주소
            land_area: 토지 면적 (㎡)
            lat: 위도
            lng: 경도
            lh_purchase_price: LH 매입 예정가 (원)
            
        Returns:
            MarketAnalysisV8 object
        """
        print(f"\n{'='*80}")
        print(f"🔍 ZeroSite v8.0 - Comprehensive Market Analysis")
        print(f"{'='*80}")
        print(f"📍 Address: {address}")
        print(f"📏 Land Area: {land_area:,.1f}㎡")
        print(f"🌐 Coordinates: ({lat:.6f}, {lng:.6f})")
        print()
        
        # 1. Get comprehensive data from external APIs
        print("📊 Step 1: Fetching external API data...")
        market_data = self.api_client.get_comprehensive_market_analysis(
            address=address,
            land_area=land_area,
            lat=lat,
            lng=lng
        )
        
        # 2. Analyze land transactions
        print("📊 Step 2: Analyzing land transactions...")
        land_analysis = self._analyze_land_transactions(
            market_data['land_transactions'],
            land_area
        )
        
        # 3. Analyze apartment market
        print("📊 Step 3: Analyzing apartment market...")
        apt_analysis = self._analyze_apartment_market(
            market_data['apt_transactions'],
            market_data['apt_rent_transactions']
        )
        
        # 4. Calculate LH pricing gap
        print("📊 Step 4: Calculating LH pricing gap...")
        if lh_purchase_price:
            lh_gap = calculate_lh_pricing_gap(
                land_analysis['avg_price_per_sqm'],
                int(lh_purchase_price / land_area)
            )
            lh_feasibility = self._calculate_lh_feasibility(lh_gap)
        else:
            lh_gap = {
                'market_price': land_analysis['avg_price_per_sqm'],
                'lh_price': 0,
                'gap_amount': 0,
                'gap_percentage': 0,
                'gap_assessment': '데이터 없음'
            }
            lh_feasibility = 50.0
        
        # 5. Safety analysis
        print("📊 Step 5: Analyzing safety and crime risk...")
        crime_data = market_data['crime_risk']
        safety_analysis = score_location_safety(crime_data)
        
        # 6. Environmental analysis
        print("📊 Step 6: Analyzing environmental factors...")
        env_data = market_data['environmental']
        env_analysis = score_environmental_risk(env_data)
        
        # 7. Calculate overall score
        print("📊 Step 7: Calculating overall market score...")
        overall_score, grade, findings, warnings, recommendations = \
            self._calculate_overall_assessment(
                land_analysis,
                apt_analysis,
                lh_feasibility,
                safety_analysis,
                env_analysis
            )
        
        print(f"\n✅ Analysis complete!")
        print(f"📈 Overall Market Score: {overall_score:.1f}/100")
        print(f"🎯 Investment Grade: {grade}")
        print(f"{'='*80}\n")
        
        return MarketAnalysisV8(
            avg_land_price_per_sqm=land_analysis['avg_price_per_sqm'],
            median_land_price_per_sqm=land_analysis['median_price_per_sqm'],
            land_price_range=land_analysis['price_range'],
            recent_transactions_count=land_analysis['transaction_count'],
            market_activity_level=land_analysis['activity_level'],
            avg_apt_price_per_sqm=apt_analysis['avg_price_per_sqm'],
            apt_transaction_volume=apt_analysis['transaction_volume'],
            avg_rent_yield=apt_analysis['avg_rent_yield'],
            lh_pricing_gap=lh_gap,
            lh_feasibility_score=lh_feasibility,
            crime_risk_data=crime_data,
            safety_analysis=safety_analysis,
            environmental_data=env_data,
            environmental_analysis=env_analysis,
            overall_market_score=overall_score,
            investment_grade=grade,
            key_findings=findings,
            risk_warnings=warnings,
            recommendations=recommendations
        )
    
    def _analyze_land_transactions(
        self,
        transactions: List[RealEstateTransaction],
        target_land_area: float
    ) -> Dict:
        """토지 거래 분석"""
        if not transactions:
            return {
                'avg_price_per_sqm': 0,
                'median_price_per_sqm': 0,
                'price_range': (0, 0),
                'transaction_count': 0,
                'activity_level': '데이터 없음'
            }
        
        # Filter transactions similar to target area (±30%)
        similar_txns = [
            t for t in transactions
            if 0.7 * target_land_area <= t.area <= 1.3 * target_land_area
        ]
        
        if not similar_txns:
            similar_txns = transactions  # Use all if no similar found
        
        prices = [t.unit_price for t in similar_txns if t.unit_price > 0]
        
        if not prices:
            return {
                'avg_price_per_sqm': 0,
                'median_price_per_sqm': 0,
                'price_range': (0, 0),
                'transaction_count': 0,
                'activity_level': '데이터 없음'
            }
        
        avg_price = int(statistics.mean(prices))
        median_price = int(statistics.median(prices))
        price_range = (min(prices), max(prices))
        
        # Activity level based on transaction count
        count = len(similar_txns)
        if count >= 20:
            activity = "매우 활발"
        elif count >= 10:
            activity = "활발"
        elif count >= 5:
            activity = "보통"
        else:
            activity = "저조"
        
        return {
            'avg_price_per_sqm': avg_price,
            'median_price_per_sqm': median_price,
            'price_range': price_range,
            'transaction_count': count,
            'activity_level': activity
        }
    
    def _analyze_apartment_market(
        self,
        trade_transactions: List[RealEstateTransaction],
        rent_transactions: List[RealEstateTransaction]
    ) -> Dict:
        """아파트 시장 분석"""
        # Trade analysis
        if trade_transactions:
            trade_prices = [t.unit_price for t in trade_transactions if t.unit_price > 0]
            avg_trade_price = int(statistics.mean(trade_prices)) if trade_prices else 0
        else:
            avg_trade_price = 0
        
        # Rent yield calculation
        if rent_transactions and trade_transactions:
            # Simple rent yield estimation
            avg_rent_yield = 3.5  # Mock value, needs proper calculation
        else:
            avg_rent_yield = 0.0
        
        return {
            'avg_price_per_sqm': avg_trade_price,
            'transaction_volume': len(trade_transactions),
            'avg_rent_yield': avg_rent_yield
        }
    
    def _calculate_lh_feasibility(self, lh_gap: Dict) -> float:
        """LH 사업 타당성 점수 계산"""
        gap_pct = lh_gap['gap_percentage']
        
        # Score based on gap percentage
        if gap_pct >= 20:
            return 95.0
        elif gap_pct >= 15:
            return 85.0
        elif gap_pct >= 10:
            return 75.0
        elif gap_pct >= 5:
            return 65.0
        elif gap_pct >= 0:
            return 55.0
        elif gap_pct >= -5:
            return 40.0
        elif gap_pct >= -10:
            return 25.0
        else:
            return 10.0
    
    def _calculate_overall_assessment(
        self,
        land_analysis: Dict,
        apt_analysis: Dict,
        lh_feasibility: float,
        safety_analysis: Dict,
        env_analysis: Dict
    ) -> tuple:
        """종합 평가 계산"""
        
        # Calculate weighted overall score
        weights = {
            'market': 0.30,      # 30% - Market activity and pricing
            'lh_feasibility': 0.25,  # 25% - LH pricing gap
            'safety': 0.25,      # 25% - Safety score
            'environment': 0.20  # 20% - Environmental score
        }
        
        # Market score
        market_score = 50  # Base score
        if land_analysis['transaction_count'] >= 20:
            market_score = 90
        elif land_analysis['transaction_count'] >= 10:
            market_score = 75
        elif land_analysis['transaction_count'] >= 5:
            market_score = 60
        
        # Overall score
        overall_score = (
            market_score * weights['market'] +
            lh_feasibility * weights['lh_feasibility'] +
            safety_analysis['safety_score'] * weights['safety'] +
            env_analysis['environmental_score'] * weights['environment']
        )
        
        # Investment grade
        if overall_score >= 90:
            grade = "A+ (최우수)"
        elif overall_score >= 80:
            grade = "A (우수)"
        elif overall_score >= 70:
            grade = "B+ (양호)"
        elif overall_score >= 60:
            grade = "B (보통 상)"
        elif overall_score >= 50:
            grade = "C (보통)"
        elif overall_score >= 40:
            grade = "D (주의)"
        else:
            grade = "F (부적합)"
        
        # Key findings
        findings = []
        if land_analysis['activity_level'] in ['매우 활발', '활발']:
            findings.append(f"시장 활동성 우수 ({land_analysis['transaction_count']}건 거래)")
        if lh_feasibility >= 80:
            findings.append("LH 매입가 조건 매우 유리")
        if safety_analysis['safety_score'] >= 80:
            findings.append("입지 안전성 우수")
        if env_analysis['environmental_score'] >= 80:
            findings.append("환경 조건 양호")
        
        # Risk warnings
        warnings = []
        if land_analysis['transaction_count'] < 5:
            warnings.append("시장 거래 빈도 낮음 - 유동성 리스크")
        if lh_feasibility < 50:
            warnings.append("LH 매입가 조건 불리")
        if safety_analysis['safety_score'] < 50:
            warnings.append("입지 안전성 우려")
        if env_analysis['environmental_score'] < 50:
            warnings.append("환경 리스크 존재")
        
        # Recommendations
        recommendations = []
        if land_analysis['transaction_count'] < 10:
            recommendations.append("추가 시장 조사 및 유사 사례 분석 필요")
        if lh_feasibility < 60:
            recommendations.append("LH 협상 전략 수립 및 대안 검토")
        recommendations.extend(safety_analysis.get('recommendations', []))
        if env_analysis['environmental_score'] < 70:
            recommendations.append("환경영향평가 사전 준비 및 대책 수립")
        
        return overall_score, grade, findings, warnings, recommendations
    
    def format_analysis_for_report(
        self,
        analysis: MarketAnalysisV8
    ) -> Dict:
        """
        보고서용 분석 결과 포맷팅
        
        Returns formatted data for v8.0 report integration
        """
        return {
            'market_data': {
                'avg_land_price_per_sqm': f"{analysis.avg_land_price_per_sqm:,}원/㎡",
                'price_range': f"{analysis.land_price_range[0]:,}~{analysis.land_price_range[1]:,}원/㎡",
                'transaction_volume': f"{analysis.recent_transactions_count}건",
                'market_activity': analysis.market_activity_level,
                'apt_avg_price': f"{analysis.avg_apt_price_per_sqm:,}원/㎡",
                'rent_yield': f"{analysis.avg_rent_yield:.2f}%"
            },
            'lh_pricing': {
                'market_price': f"{analysis.lh_pricing_gap['market_price']:,}원/㎡",
                'lh_price': f"{analysis.lh_pricing_gap['lh_price']:,}원/㎡",
                'gap_amount': f"{analysis.lh_pricing_gap['gap_amount']:,}원/㎡",
                'gap_percentage': f"{analysis.lh_pricing_gap['gap_percentage']:.1f}%",
                'assessment': analysis.lh_pricing_gap['gap_assessment'],
                'feasibility_score': f"{analysis.lh_feasibility_score:.1f}/100"
            },
            'safety': {
                'crime_score': f"{analysis.crime_risk_data.crime_score:.1f}/100",
                'safety_score': f"{analysis.safety_analysis['safety_score']:.1f}/100",
                'safety_grade': analysis.safety_analysis['safety_grade'],
                'risk_level': analysis.crime_risk_data.risk_level,
                'risk_factors': analysis.safety_analysis.get('risk_factors', []),
                'has_crime_hotspot': analysis.crime_risk_data.has_crime_hotspot
            },
            'environment': {
                'pm10': f"{analysis.environmental_data.pm10:.1f}㎍/㎥" if analysis.environmental_data.pm10 else "N/A",
                'pm25': f"{analysis.environmental_data.pm25:.1f}㎍/㎥" if analysis.environmental_data.pm25 else "N/A",
                'aqi': analysis.environmental_data.air_quality_index or "N/A",
                'env_score': f"{analysis.environmental_analysis['environmental_score']:.1f}/100",
                'risk_level': analysis.environmental_analysis['risk_level'],
                'construction_risk': analysis.environmental_analysis['construction_risk'],
                'permit_risk': analysis.environmental_analysis['permit_risk']
            },
            'overall': {
                'score': f"{analysis.overall_market_score:.1f}/100",
                'grade': analysis.investment_grade,
                'key_findings': analysis.key_findings,
                'risk_warnings': analysis.risk_warnings,
                'recommendations': analysis.recommendations
            }
        }
