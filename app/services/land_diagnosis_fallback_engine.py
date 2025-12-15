"""
Land Diagnosis Fallback Engine
Ensures no data loss and complete report generation even with missing inputs

ZeroSite v24.1 - Auto-Recovery System
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class LandDiagnosisFallbackEngine:
    """
    자동 복구 엔진 - 데이터 누락 시 기본값 적용
    
    핵심 원칙:
    1. 데이터가 없어도 서비스는 계속된다
    2. 모든 계산식은 Zero-Division으로부터 안전하다
    3. 보고서의 모든 섹션은 반드시 출력된다
    4. 사용자에게 어떤 값이 Fallback인지 명확히 알린다
    """
    
    # 서울시 구별 기본 공시지가 (원/㎡)
    DEFAULT_LAND_PRICES = {
        '강남구': 12000000,
        '서초구': 10500000,
        '송파구': 9500000,
        '용산구': 9000000,
        '마포구': 8500000,
        '영등포구': 8000000,
        '성동구': 7500000,
        '강서구': 6500000,
        '강동구': 6500000,
        '강북구': 5500000,
        '관악구': 5500000,
        'default': 6500000  # 서울시 평균
    }
    
    # 용도지역별 기본 법정 비율
    ZONE_DEFAULTS = {
        '제1종일반주거지역': {'bcr': 60, 'far': 150, 'floors': 4},
        '제2종일반주거지역': {'bcr': 60, 'far': 200, 'floors': 7},
        '제3종일반주거지역': {'bcr': 50, 'far': 250, 'floors': 15},
        '준주거지역': {'bcr': 70, 'far': 400, 'floors': 20},
        '상업지역': {'bcr': 60, 'far': 800, 'floors': 30},
        '준공업지역': {'bcr': 70, 'far': 400, 'floors': 20},
        'default': {'bcr': 60, 'far': 200, 'floors': 7}  # 제2종 기본
    }
    
    def __init__(self):
        self.fallback_log = []
        logger.info("✅ LandDiagnosisFallbackEngine initialized")
    
    def validate_and_fix_input(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        입력 데이터 검증 및 자동 복구
        
        Returns:
            fixed_input: 복구된 입력 데이터
        """
        logger.info("🔍 Validating input data with Fallback Engine")
        
        fixed = raw_input.copy()
        self.fallback_log = []
        
        # 1. 주소 검증
        if not fixed.get('address') or fixed['address'].strip() == '':
            fixed['address'] = '주소 미입력(Unknown Address)'
            self._log_fallback('address', '주소 미입력', '기본값 적용')
        
        # 2. 필지면적 검증 (Zero Division 방지)
        land_area = fixed.get('land_area_sqm', 0)
        if not land_area or land_area <= 0:
            fixed['land_area_sqm'] = 100.0  # 최소 100㎡
            self._log_fallback('land_area_sqm', f'{land_area}', '100㎡ (최소값)')
        
        # 3. 용도지역 검증
        zone = fixed.get('zone_type', '')
        if not zone or zone.strip() == '':
            fixed['zone_type'] = '제2종일반주거지역'
            self._log_fallback('zone_type', '미입력', '제2종일반주거지역 (기본)')
        
        # 4. 건폐율/용적률 검증
        bcr = fixed.get('bcr', 0)
        far = fixed.get('far', 0)
        
        zone_defaults = self.ZONE_DEFAULTS.get(fixed['zone_type'], self.ZONE_DEFAULTS['default'])
        
        if not bcr or bcr <= 0:
            fixed['bcr'] = zone_defaults['bcr']
            self._log_fallback('bcr', f'{bcr}%', f"{zone_defaults['bcr']}% (법정)")
        
        if not far or far <= 0:
            fixed['far'] = zone_defaults['far']
            self._log_fallback('far', f'{far}%', f"{zone_defaults['far']}% (법정)")
        
        # 5. 개별공시지가 검증
        std_price = fixed.get('individual_land_price_per_sqm', 0)
        if not std_price or std_price <= 0:
            # 주소에서 구 추출
            gu_name = self._extract_gu_from_address(fixed['address'])
            fixed['individual_land_price_per_sqm'] = self.DEFAULT_LAND_PRICES.get(
                gu_name, 
                self.DEFAULT_LAND_PRICES['default']
            )
            self._log_fallback(
                'individual_land_price_per_sqm', 
                '미입력',
                f"{fixed['individual_land_price_per_sqm']:,}원/㎡ (지역 평균)"
            )
        
        # 6. LH 단가 검증
        lh_cost = fixed.get('lh_unit_cost_per_sqm', 0)
        if not lh_cost or lh_cost <= 0:
            fixed['lh_unit_cost_per_sqm'] = 5200000  # 520만원/㎡ (평균)
            self._log_fallback('lh_unit_cost_per_sqm', '미입력', '5,200,000원/㎡ (LH 평균)')
        
        # 7. 도로조건
        if 'road_condition' not in fixed or not fixed.get('road_condition'):
            fixed['road_condition'] = '일반도로'
            self._log_fallback('road_condition', '미입력', '일반도로 (기본)')
        
        # 8. 형상조건
        if 'land_shape' not in fixed or not fixed.get('land_shape'):
            fixed['land_shape'] = '정방형'
            self._log_fallback('land_shape', '미입력', '정방형 (기본)')
        
        logger.info(f"✅ Input validation complete: {len(self.fallback_log)} fallbacks applied")
        
        return fixed
    
    def generate_fallback_comparable_sales(
        self, 
        address: str, 
        land_area_sqm: float,
        zone_type: str,
        count: int = 3
    ) -> List[Dict]:
        """
        주변 거래사례 자동 생성 (최소 3개)
        
        Returns:
            List of comparable sales with realistic values
        """
        logger.info(f"📊 Generating {count} fallback comparable sales")
        
        gu_name = self._extract_gu_from_address(address)
        base_price = self.DEFAULT_LAND_PRICES.get(gu_name, self.DEFAULT_LAND_PRICES['default'])
        
        sales = []
        for i in range(count):
            # 가격 변동 ±15%
            variation = 1.0 + random.uniform(-0.15, 0.15)
            price_per_sqm = int(base_price * variation)
            
            # 면적 변동 ±20%
            area_variation = 1.0 + random.uniform(-0.20, 0.20)
            tx_area = int(land_area_sqm * area_variation)
            
            # 거래일 (최근 6개월)
            days_ago = random.randint(30, 180)
            tx_date = datetime.now() - timedelta(days=days_ago)
            
            sales.append({
                'transaction_date': tx_date.strftime('%Y-%m-%d'),
                'location': f'{gu_name} 인근 {i+1}',
                'land_area_sqm': tx_area,
                'price_per_sqm': price_per_sqm,
                'total_price': price_per_sqm * tx_area,
                'distance_km': round(random.uniform(0.3, 1.5), 2),
                'source': 'Fallback Generated'
            })
        
        self._log_fallback('comparable_sales', '데이터 없음', f'{count}개 자동 생성')
        
        return sales
    
    def safe_divide(self, numerator: float, denominator: float, default: float = 0.0) -> float:
        """
        안전한 나눗셈 (Zero Division 방지)
        
        Args:
            numerator: 분자
            denominator: 분모
            default: 분모가 0일 때 반환값
        
        Returns:
            계산 결과 또는 기본값
        """
        if denominator == 0 or denominator is None:
            logger.warning(f"⚠️ Zero division prevented: {numerator} / {denominator}")
            return default
        return numerator / denominator
    
    def safe_percentage(self, value: float, total: float) -> float:
        """안전한 백분율 계산"""
        result = self.safe_divide(value, total, 0.0) * 100
        return round(result, 2)
    
    def ensure_positive(self, value: float, minimum: float = 1.0) -> float:
        """값이 양수임을 보장"""
        if value is None or value <= 0:
            return minimum
        return max(value, minimum)
    
    def generate_fallback_summary(self) -> Dict:
        """
        Fallback 적용 요약 생성
        
        Returns:
            {
                'fallback_used': bool,
                'fallback_count': int,
                'fallback_details': List[Dict]
            }
        """
        return {
            'fallback_used': len(self.fallback_log) > 0,
            'fallback_count': len(self.fallback_log),
            'fallback_details': self.fallback_log.copy(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _log_fallback(self, field: str, original_value: str, fallback_value: str):
        """Fallback 로그 기록"""
        log_entry = {
            'field': field,
            'original': original_value,
            'fallback': fallback_value,
            'timestamp': datetime.now().isoformat()
        }
        self.fallback_log.append(log_entry)
        logger.info(f"🔄 Fallback: {field} = {original_value} → {fallback_value}")
    
    def _extract_gu_from_address(self, address: str) -> str:
        """주소에서 구 이름 추출"""
        seoul_gu = [
            '강남구', '서초구', '송파구', '강동구', '강서구',
            '용산구', '마포구', '영등포구', '성동구', '강북구',
            '관악구', '광진구', '구로구', '금천구', '노원구',
            '도봉구', '동대문구', '동작구', '서대문구', '성북구',
            '양천구', '은평구', '종로구', '중구', '중랑구'
        ]
        
        for gu in seoul_gu:
            if gu in address:
                return gu
        
        return 'default'


# Singleton instance
_fallback_engine_instance = None

def get_fallback_engine() -> LandDiagnosisFallbackEngine:
    """Fallback Engine 싱글톤 인스턴스 반환"""
    global _fallback_engine_instance
    if _fallback_engine_instance is None:
        _fallback_engine_instance = LandDiagnosisFallbackEngine()
    return _fallback_engine_instance
