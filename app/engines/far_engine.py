"""
FAR Engine v24.0
용적률 상한/하한 분석 엔진 for ZeroSite v24

Features:
- 법정 용적률 상한선/하한선 계산
- 인센티브 적용 최대 용적률 산정
- 용적률 활용률 분석
- 개발 밀도 최적화 제안

Author: ZeroSite v24 Team
Date: 2025-12-12
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from .base_engine import BaseEngine

logger = logging.getLogger(__name__)


@dataclass
class FARAnalysis:
    """용적률 분석 결과"""
    legal_max_far: float  # 법정 최대 용적률 (%)
    legal_min_far: Optional[float]  # 법정 최소 용적률 (%)
    incentive_bonus: float  # 인센티브 용적률 (%)
    achievable_max_far: float  # 달성 가능 최대 용적률 (%)
    recommended_far: float  # 권장 용적률 (%)
    utilization_rate: float  # 용적률 활용률 (%)
    density_level: str  # 개발 밀도 수준


class FAREngine(BaseEngine):
    """
    용적률 상한/하한 분석 엔진
    
    Inherits from BaseEngine for v24 standardization
    
    Key Features:
    - 법정 용적률 기준 자동 산정
    - 인센티브 용적률 완화 계산
    - 최적 용적률 제안
    - 개발 밀도 분석
    
    Input:
        {
            'zoning_code': str,
            'land_area_sqm': float,
            'location': str (optional),
            'incentive_applicable': bool (optional),
            'target_use': str (optional)
        }
    
    Output:
        {
            'legal_max_far': float,
            'legal_min_far': float,
            'incentive_bonus': float,
            'achievable_max_far': float,
            'recommended_far': float,
            'utilization_rate': float,
            'density_level': str,
            'far_breakdown': {...}
        }
    """
    
    def __init__(self):
        super().__init__(engine_name="FAREngine", version="24.0")
        self.far_rules = self._initialize_far_rules()
    
    @property
    def timestamp(self):
        return self.created_at.isoformat()
    
    def process(self, input_data: Dict) -> Dict:
        """
        Main processing method (BaseEngine interface)
        
        Args:
            input_data: {
                'zoning_code': str,
                'land_area_sqm': float,
                'location': str (optional),
                'incentive_applicable': bool (optional),
                'target_use': str (optional)
            }
        
        Returns:
            Complete FAR analysis
        """
        self.validate_input(input_data, ['zoning_code', 'land_area_sqm'])
        
        zoning_code = input_data['zoning_code']
        land_area = input_data['land_area_sqm']
        location = input_data.get('location', 'seoul')
        incentive_applicable = input_data.get('incentive_applicable', False)
        target_use = input_data.get('target_use', '주택')
        
        # Get base FAR rules
        far_rules = self._get_far_rules(zoning_code)
        
        if not far_rules:
            return {
                'success': False,
                'error': f'Unknown zoning code: {zoning_code}',
                'zoning_code': zoning_code
            }
        
        # Calculate incentive bonus
        incentive_bonus = 0.0
        if incentive_applicable:
            incentive_bonus = self._calculate_incentive_bonus(
                zoning_code, land_area, location, target_use
            )
        
        # Calculate achievable max FAR
        achievable_max_far = far_rules['max_far'] + incentive_bonus
        
        # Calculate recommended FAR (80-90% of achievable max)
        recommended_far = achievable_max_far * 0.85
        
        # Ensure minimum FAR if required
        if far_rules['min_far']:
            recommended_far = max(recommended_far, far_rules['min_far'])
        
        # Calculate utilization rate
        utilization_rate = (recommended_far / achievable_max_far) * 100
        
        # Determine density level
        density_level = self._determine_density_level(recommended_far, zoning_code)
        
        result = {
            'success': True,
            'zoning_code': zoning_code,
            'legal_max_far': far_rules['max_far'],
            'legal_min_far': far_rules['min_far'],
            'incentive_bonus': incentive_bonus,
            'achievable_max_far': round(achievable_max_far, 1),
            'recommended_far': round(recommended_far, 1),
            'utilization_rate': round(utilization_rate, 1),
            'density_level': density_level,
            'far_breakdown': {
                'base_legal_far': far_rules['max_far'],
                'incentive_far': incentive_bonus,
                'total_achievable_far': round(achievable_max_far, 1),
                'recommended_far': round(recommended_far, 1),
                'buffer_margin': round(achievable_max_far - recommended_far, 1)
            }
        }
        
        self.logger.info(f"FAR analysis complete: {zoning_code}, Recommended FAR {recommended_far}%")
        return result
    
    def _initialize_far_rules(self) -> Dict[str, Dict]:
        """
        Initialize FAR rules database
        Based on Korean Urban Planning Act
        """
        rules = {}
        
        # 주거지역
        rules['제1종전용주거지역'] = {'max_far': 100.0, 'min_far': None}
        rules['제2종전용주거지역'] = {'max_far': 150.0, 'min_far': None}
        rules['제1종일반주거지역'] = {'max_far': 200.0, 'min_far': 100.0}
        rules['제2종일반주거지역'] = {'max_far': 250.0, 'min_far': 150.0}
        rules['제3종일반주거지역'] = {'max_far': 300.0, 'min_far': 200.0}
        rules['준주거지역'] = {'max_far': 500.0, 'min_far': 200.0}
        
        # 상업지역
        rules['중심상업지역'] = {'max_far': 1500.0, 'min_far': 200.0}
        rules['일반상업지역'] = {'max_far': 1300.0, 'min_far': 150.0}
        rules['근린상업지역'] = {'max_far': 900.0, 'min_far': 100.0}
        rules['유통상업지역'] = {'max_far': 1100.0, 'min_far': 150.0}
        
        # 공업지역
        rules['전용공업지역'] = {'max_far': 300.0, 'min_far': None}
        rules['일반공업지역'] = {'max_far': 350.0, 'min_far': None}
        rules['준공업지역'] = {'max_far': 400.0, 'min_far': 150.0}
        
        # 녹지지역
        rules['보전녹지지역'] = {'max_far': 80.0, 'min_far': None}
        rules['생산녹지지역'] = {'max_far': 100.0, 'min_far': None}
        rules['자연녹지지역'] = {'max_far': 100.0, 'min_far': None}
        
        return rules
    
    def _get_far_rules(self, zoning_code: str) -> Optional[Dict]:
        """Get FAR rules by zoning code"""
        # Try exact match
        if zoning_code in self.far_rules:
            return self.far_rules[zoning_code]
        
        # Try partial match
        for key, rules in self.far_rules.items():
            if zoning_code in key or key in zoning_code:
                return rules
        
        return None
    
    def _calculate_incentive_bonus(self,
                                   zoning_code: str,
                                   land_area: float,
                                   location: str,
                                   target_use: str) -> float:
        """
        Calculate incentive bonus FAR
        
        Korean incentive rules:
        - 임대주택 건설: +20~30%
        - 주택단지 계획: +10~20%
        - 공개공지 제공: +10~15%
        - 친환경 건축: +5~10%
        """
        bonus = 0.0
        
        # Residential incentives
        if '주거' in zoning_code:
            if target_use == '임대주택':
                bonus += 30.0  # 임대주택 최대 30%
            elif target_use == '주택':
                bonus += 20.0  # 일반 주택 20%
            
            if land_area >= 1000:
                bonus += 15.0  # 대규모 단지 추가 15%
        
        # Commercial incentives
        if '상업' in zoning_code:
            bonus += 15.0  # 공개공지 제공
            
            if location == 'seoul':
                bonus += 10.0  # 서울시 추가 인센티브
        
        # 준공업지역 special case
        if zoning_code == '준공업지역':
            if '주거' in target_use or '주택' in target_use:
                bonus += 50.0  # 주거복합 최대 50%
        
        return bonus
    
    def _determine_density_level(self, recommended_far: float, zoning_code: str) -> str:
        """
        Determine development density level
        
        Levels:
        - 초저밀 (Ultra-low): FAR < 100%
        - 저밀 (Low): 100% ≤ FAR < 200%
        - 중밀 (Medium): 200% ≤ FAR < 400%
        - 고밀 (High): 400% ≤ FAR < 800%
        - 초고밀 (Ultra-high): FAR ≥ 800%
        """
        if recommended_far < 100:
            return '초저밀 (Ultra-low density)'
        elif recommended_far < 200:
            return '저밀 (Low density)'
        elif recommended_far < 400:
            return '중밀 (Medium density)'
        elif recommended_far < 800:
            return '고밀 (High density)'
        else:
            return '초고밀 (Ultra-high density)'
    
    def calculate_floor_area(self,
                            land_area_sqm: float,
                            target_far: float) -> Dict[str, float]:
        """
        Calculate total floor area from FAR
        
        Args:
            land_area_sqm: Land area in square meters
            target_far: Target FAR in percentage
        
        Returns:
            Floor area calculations
        """
        total_floor_area = (land_area_sqm * target_far) / 100
        
        return {
            'land_area_sqm': land_area_sqm,
            'target_far_percent': target_far,
            'total_floor_area_sqm': round(total_floor_area, 2),
            'total_floor_area_pyeong': round(total_floor_area / 3.3058, 2)
        }


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("FAR ENGINE v24.0 - CLI TEST")
    print("=" * 80)
    
    engine = FAREngine()
    
    # Test cases
    test_cases = [
        {
            'name': 'Test 1: 제2종일반주거지역 (일반 주택)',
            'input': {
                'zoning_code': '제2종일반주거지역',
                'land_area_sqm': 660.0,
                'location': 'seoul',
                'incentive_applicable': True,
                'target_use': '주택'
            }
        },
        {
            'name': 'Test 2: 준주거지역 (주거복합)',
            'input': {
                'zoning_code': '준주거지역',
                'land_area_sqm': 2000.0,
                'location': 'seoul',
                'incentive_applicable': True,
                'target_use': '주택'
            }
        },
        {
            'name': 'Test 3: 일반상업지역',
            'input': {
                'zoning_code': '일반상업지역',
                'land_area_sqm': 500.0,
                'location': 'seoul',
                'incentive_applicable': True,
                'target_use': '업무시설'
            }
        },
        {
            'name': 'Test 4: 준공업지역 (주거복합)',
            'input': {
                'zoning_code': '준공업지역',
                'land_area_sqm': 1500.0,
                'location': 'seoul',
                'incentive_applicable': True,
                'target_use': '주거복합'
            }
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"{test['name']}")
        print("=" * 80)
        
        result = engine.process(test['input'])
        
        if result.get('success'):
            print(f"✅ Engine: {engine.engine_name} v{engine.version}")
            print(f"✅ Timestamp: {engine.timestamp}")
            print(f"\n용도지역: {result['zoning_code']}")
            print(f"\n용적률 분석:")
            print(f"  - 법정 최대 용적률: {result['legal_max_far']}%")
            if result['legal_min_far']:
                print(f"  - 법정 최소 용적률: {result['legal_min_far']}%")
            print(f"  - 인센티브 용적률: +{result['incentive_bonus']}%")
            print(f"  - 달성 가능 최대: {result['achievable_max_far']}%")
            print(f"  - 권장 용적률: {result['recommended_far']}% (활용률 {result['utilization_rate']}%)")
            print(f"  - 개발 밀도: {result['density_level']}")
            
            # Calculate floor area
            floor_calc = engine.calculate_floor_area(
                test['input']['land_area_sqm'],
                result['recommended_far']
            )
            print(f"\n연면적 산정:")
            print(f"  - 대지면적: {floor_calc['land_area_sqm']:.1f}㎡")
            print(f"  - 총 연면적: {floor_calc['total_floor_area_sqm']:.1f}㎡ ({floor_calc['total_floor_area_pyeong']:.1f}평)")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)
