"""
Risk Engine v24.0
리스크 분석 엔진 for ZeroSite v24

Features:
- 법적 리스크 평가
- 재무적 리스크 평가
- 기술적 리스크 평가
- 시장 리스크 평가
- 종합 리스크 스코어

Author: ZeroSite v24 Team  
Date: 2025-12-12
"""

from typing import Dict, List
from enum import Enum
import logging
from .base_engine import BaseEngine

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """리스크 수준"""
    LOW = "낮음"
    MEDIUM = "보통"
    HIGH = "높음"
    CRITICAL = "매우높음"


class RiskEngine(BaseEngine):
    """리스크 분석 엔진"""
    
    def __init__(self):
        super().__init__(engine_name="RiskEngine", version="24.0")
    
    @property
    def timestamp(self):
        return self.created_at.isoformat()
    
    def process(self, input_data: Dict) -> Dict:
        """Main processing"""
        self.validate_input(input_data, ['land_area_sqm', 'zoning_code'])
        
        # Analyze different risk categories
        legal_risk = self._analyze_legal_risk(input_data)
        financial_risk = self._analyze_financial_risk(input_data)
        technical_risk = self._analyze_technical_risk(input_data)
        market_risk = self._analyze_market_risk(input_data)
        
        # Calculate overall risk score
        overall_score = self._calculate_overall_score(
            legal_risk, financial_risk, technical_risk, market_risk
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        # Generate mitigation strategies
        mitigations = self._generate_mitigations(
            legal_risk, financial_risk, technical_risk, market_risk
        )
        
        result = {
            'success': True,
            'overall_risk_score': round(overall_score, 1),
            'risk_level': risk_level.value,
            'legal_risk': legal_risk,
            'financial_risk': financial_risk,
            'technical_risk': technical_risk,
            'market_risk': market_risk,
            'mitigation_strategies': mitigations,
            'recommendation': self._get_recommendation(risk_level)
        }
        
        self.logger.info(f"Risk analysis complete: Overall score {overall_score}/100, Level: {risk_level.value}")
        return result
    
    def _analyze_legal_risk(self, data: Dict) -> Dict:
        """Analyze legal risks"""
        score = 20.0  # Base score (lower is better)
        
        zoning = data.get('zoning_code', '')
        if '녹지' in zoning:
            score += 30  # Green zone has high legal risk
        if data.get('land_area_sqm', 0) < 200:
            score += 15  # Small lots have higher risk
        
        return {
            'score': min(100, score),
            'level': self._score_to_level(score),
            'factors': [
                '용도지역 규제',
                '건축 허가 제한',
                '인근 민원 가능성'
            ]
        }
    
    def _analyze_financial_risk(self, data: Dict) -> Dict:
        """Analyze financial risks"""
        score = 25.0
        
        land_price = data.get('avg_land_price_per_sqm', 10000000)
        if land_price > 15000000:  # High land price
            score += 25
        
        return {
            'score': min(100, score),
            'level': self._score_to_level(score),
            'factors': [
                '초기 투자비 규모',
                '금융 비용',
                'ROI 불확실성'
            ]
        }
    
    def _analyze_technical_risk(self, data: Dict) -> Dict:
        """Analyze technical risks"""
        score = 15.0
        
        slope = data.get('slope_percent', 0)
        if slope > 15:
            score += 30  # Steep slope = high technical risk
        
        return {
            'score': min(100, score),
            'level': self._score_to_level(score),
            'factors': [
                '지형 조건',
                '지반 안정성',
                '공사 난이도'
            ]
        }
    
    def _analyze_market_risk(self, data: Dict) -> Dict:
        """Analyze market risks"""
        score = 30.0
        
        location = data.get('location', 'seoul')
        if location != 'seoul':
            score += 20  # Non-Seoul has higher market risk
        
        return {
            'score': min(100, score),
            'level': self._score_to_level(score),
            'factors': [
                '시장 수요 변동성',
                '경쟁 공급 물량',
                '경기 민감도'
            ]
        }
    
    def _calculate_overall_score(self, legal, financial, technical, market) -> float:
        """Calculate weighted overall risk score"""
        weights = {
            'legal': 0.30,
            'financial': 0.30,
            'technical': 0.25,
            'market': 0.15
        }
        
        overall = (
            legal['score'] * weights['legal'] +
            financial['score'] * weights['financial'] +
            technical['score'] * weights['technical'] +
            market['score'] * weights['market']
        )
        
        return overall
    
    def _score_to_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score < 30:
            return RiskLevel.LOW.value
        elif score < 50:
            return RiskLevel.MEDIUM.value
        elif score < 70:
            return RiskLevel.HIGH.value
        else:
            return RiskLevel.CRITICAL.value
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine overall risk level"""
        if score < 30:
            return RiskLevel.LOW
        elif score < 50:
            return RiskLevel.MEDIUM
        elif score < 70:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _generate_mitigations(self, legal, financial, technical, market) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = []
        
        if legal['score'] > 40:
            strategies.append("법률 자문 및 사전 인허가 검토 필수")
        if financial['score'] > 40:
            strategies.append("재무 구조 최적화 및 금융 비용 절감 방안 강구")
        if technical['score'] > 40:
            strategies.append("기술 용역사 사전 검토 및 시공 계획 정밀화")
        if market['score'] > 40:
            strategies.append("시장 조사 강화 및 수요 분석 정밀화")
        
        if not strategies:
            strategies.append("현재 리스크 수준 양호 - 정기적 모니터링 권장")
        
        return strategies
    
    def _get_recommendation(self, level: RiskLevel) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            RiskLevel.LOW: "✅ 사업 진행 권장 - 리스크 관리 기본 수준",
            RiskLevel.MEDIUM: "⚠️ 조건부 진행 - 리스크 저감 대책 수립 필요",
            RiskLevel.HIGH: "🔴 신중한 검토 필요 - 리스크 저감 후 진행",
            RiskLevel.CRITICAL: "❌ 사업 재검토 권장 - 근본적 리스크 해소 필요"
        }
        return recommendations[level]


if __name__ == "__main__":
    print("="*80)
    print("RISK ENGINE v24.0 - CLI TEST")
    print("="*80)
    
    engine = RiskEngine()
    
    tests = [
        {
            'name': 'Test 1: 서울 일반주거 (저위험)',
            'data': {
                'land_area_sqm': 660,
                'zoning_code': '제2종일반주거지역',
                'avg_land_price_per_sqm': 10000000,
                'slope_percent': 3,
                'location': 'seoul'
            }
        },
        {
            'name': 'Test 2: 경사지 녹지 (고위험)',
            'data': {
                'land_area_sqm': 150,
                'zoning_code': '자연녹지지역',
                'avg_land_price_per_sqm': 5000000,
                'slope_percent': 20,
                'location': 'other'
            }
        }
    ]
    
    for test in tests:
        print(f"\n{'='*80}")
        print(f"{test['name']}")
        print("="*80)
        
        result = engine.process(test['data'])
        
        print(f"✅ Engine: {engine.engine_name} v{engine.version}")
        print(f"\n⭐ 종합 리스크: {result['overall_risk_score']}/100 - {result['risk_level']}")
        print(f"\n📊 세부 리스크:")
        print(f"  - 법적: {result['legal_risk']['score']:.1f} ({result['legal_risk']['level']})")
        print(f"  - 재무: {result['financial_risk']['score']:.1f} ({result['financial_risk']['level']})")
        print(f"  - 기술: {result['technical_risk']['score']:.1f} ({result['technical_risk']['level']})")
        print(f"  - 시장: {result['market_risk']['score']:.1f} ({result['market_risk']['level']})")
        print(f"\n💡 완화 전략:")
        for s in result['mitigation_strategies']:
            print(f"  - {s}")
        print(f"\n{result['recommendation']}")
    
    print("\n" + "="*80)
