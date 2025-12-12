"""
Zoning Engine v24.0
용도지역 분석 엔진 for ZeroSite v24

Features:
- 용도지역 자동 분류 (주거/상업/공업/녹지지역)
- 법정 건폐율/용적률 자동 조회
- 용도지역별 규제 사항 분석
- 허용 용도 판정
- 인센티브 적용 가능 여부

Author: ZeroSite v24 Team
Date: 2025-12-12
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from .base_engine import BaseEngine

logger = logging.getLogger(__name__)


class ZoningCategory(Enum):
    """용도지역 대분류"""
    RESIDENTIAL = "주거지역"
    COMMERCIAL = "상업지역"
    INDUSTRIAL = "공업지역"
    GREEN = "녹지지역"
    UNPLANNED = "미지정"


@dataclass
class ZoningRegulations:
    """용도지역별 법정 규제"""
    zoning_code: str  # 용도지역 코드
    zoning_name: str  # 용도지역 명칭
    category: ZoningCategory  # 대분류
    max_bcr: float  # 법정 최대 건폐율 (%)
    max_far: float  # 법정 최대 용적률 (%)
    min_far: Optional[float]  # 법정 최소 용적률 (%)
    max_height: Optional[float]  # 최고 높이 제한 (m)
    allowed_uses: List[str]  # 허용 용도
    restricted_uses: List[str]  # 제한 용도
    incentive_available: bool  # 인센티브 적용 가능 여부


class ZoningEngine(BaseEngine):
    """
    용도지역 분석 엔진
    
    Inherits from BaseEngine for v24 standardization
    
    Key Features:
    - 용도지역 자동 분류 및 규제 조회
    - 법정 건폐율/용적률 기준 제공
    - 허용/제한 용도 판정
    - 인센티브 적용 가능성 분석
    
    Input:
        {
            'zoning_code': str (예: '제2종일반주거지역', 'UQA200'),
            'land_area_sqm': float (optional),
            'location': str (optional, 예: 'seoul')
        }
    
    Output:
        {
            'zoning_code': str,
            'zoning_name': str,
            'category': str,
            'regulations': {
                'max_bcr': float,
                'max_far': float,
                'min_far': float,
                'max_height': float
            },
            'allowed_uses': List[str],
            'restricted_uses': List[str],
            'incentive_available': bool,
            'incentive_details': {...}
        }
    """
    
    def __init__(self):
        super().__init__(engine_name="ZoningEngine", version="24.0")
        self.zoning_db = self._initialize_zoning_database()
    
    @property
    def timestamp(self):
        return self.created_at.isoformat()
    
    def process(self, input_data: Dict) -> Dict:
        """
        Main processing method (BaseEngine interface)
        
        Args:
            input_data: {
                'zoning_code': str,
                'land_area_sqm': float (optional),
                'location': str (optional)
            }
        
        Returns:
            Complete zoning analysis
        """
        self.validate_input(input_data, ['zoning_code'])
        
        zoning_code = input_data['zoning_code']
        land_area = input_data.get('land_area_sqm', 0)
        location = input_data.get('location', 'seoul')
        
        # Normalize zoning code
        normalized_code = self._normalize_zoning_code(zoning_code)
        
        # Get regulations
        regulations = self._get_zoning_regulations(normalized_code)
        
        if not regulations:
            return {
                'success': False,
                'error': f'Unknown zoning code: {zoning_code}',
                'zoning_code': zoning_code
            }
        
        # Analyze incentives
        incentive_analysis = self._analyze_incentives(
            regulations, land_area, location
        )
        
        result = {
            'success': True,
            'zoning_code': normalized_code,
            'zoning_name': regulations.zoning_name,
            'category': regulations.category.value,
            'regulations': {
                'max_bcr': regulations.max_bcr,
                'max_far': regulations.max_far,
                'min_far': regulations.min_far,
                'max_height': regulations.max_height
            },
            'allowed_uses': regulations.allowed_uses,
            'restricted_uses': regulations.restricted_uses,
            'incentive_available': regulations.incentive_available,
            'incentive_details': incentive_analysis
        }
        
        self.logger.info(f"Zoning analysis complete: {regulations.zoning_name}, FAR {regulations.max_far}%")
        return result
    
    def _initialize_zoning_database(self) -> Dict[str, ZoningRegulations]:
        """
        Initialize zoning regulations database
        Based on Korean Urban Planning Act (국토의 계획 및 이용에 관한 법률)
        """
        db = {}
        
        # 주거지역 (Residential)
        db['제1종전용주거지역'] = ZoningRegulations(
            zoning_code='UQA100',
            zoning_name='제1종전용주거지역',
            category=ZoningCategory.RESIDENTIAL,
            max_bcr=50.0,
            max_far=100.0,
            min_far=None,
            max_height=None,
            allowed_uses=['단독주택', '공동주택(4층 이하)'],
            restricted_uses=['상업시설', '공장'],
            incentive_available=False
        )
        
        db['제2종전용주거지역'] = ZoningRegulations(
            zoning_code='UQA110',
            zoning_name='제2종전용주거지역',
            category=ZoningCategory.RESIDENTIAL,
            max_bcr=50.0,
            max_far=150.0,
            min_far=None,
            max_height=None,
            allowed_uses=['단독주택', '공동주택', '근린생활시설'],
            restricted_uses=['공장', '위험물저장시설'],
            incentive_available=True
        )
        
        db['제1종일반주거지역'] = ZoningRegulations(
            zoning_code='UQA200',
            zoning_name='제1종일반주거지역',
            category=ZoningCategory.RESIDENTIAL,
            max_bcr=60.0,
            max_far=200.0,
            min_far=100.0,
            max_height=None,
            allowed_uses=['단독주택', '공동주택', '근린생활시설', '학교'],
            restricted_uses=['공장', '유흥시설'],
            incentive_available=True
        )
        
        db['제2종일반주거지역'] = ZoningRegulations(
            zoning_code='UQA210',
            zoning_name='제2종일반주거지역',
            category=ZoningCategory.RESIDENTIAL,
            max_bcr=60.0,
            max_far=250.0,
            min_far=150.0,
            max_height=None,
            allowed_uses=['단독주택', '공동주택', '근린생활시설', '학교', '문화시설'],
            restricted_uses=['공장', '위험물저장시설'],
            incentive_available=True
        )
        
        db['제3종일반주거지역'] = ZoningRegulations(
            zoning_code='UQA220',
            zoning_name='제3종일반주거지역',
            category=ZoningCategory.RESIDENTIAL,
            max_bcr=50.0,
            max_far=300.0,
            min_far=200.0,
            max_height=None,
            allowed_uses=['단독주택', '공동주택', '근린생활시설', '판매시설', '업무시설'],
            restricted_uses=['공장'],
            incentive_available=True
        )
        
        db['준주거지역'] = ZoningRegulations(
            zoning_code='UQA230',
            zoning_name='준주거지역',
            category=ZoningCategory.RESIDENTIAL,
            max_bcr=70.0,
            max_far=500.0,
            min_far=200.0,
            max_height=None,
            allowed_uses=['주택', '판매시설', '업무시설', '숙박시설', '위락시설'],
            restricted_uses=['중공업'],
            incentive_available=True
        )
        
        # 상업지역 (Commercial)
        db['중심상업지역'] = ZoningRegulations(
            zoning_code='UCB100',
            zoning_name='중심상업지역',
            category=ZoningCategory.COMMERCIAL,
            max_bcr=90.0,
            max_far=1500.0,
            min_far=200.0,
            max_height=None,
            allowed_uses=['판매시설', '업무시설', '숙박시설', '문화시설'],
            restricted_uses=['공장', '창고'],
            incentive_available=True
        )
        
        db['일반상업지역'] = ZoningRegulations(
            zoning_code='UCB200',
            zoning_name='일반상업지역',
            category=ZoningCategory.COMMERCIAL,
            max_bcr=80.0,
            max_far=1300.0,
            min_far=150.0,
            max_height=None,
            allowed_uses=['판매시설', '업무시설', '숙박시설', '근린생활시설'],
            restricted_uses=['공장'],
            incentive_available=True
        )
        
        db['근린상업지역'] = ZoningRegulations(
            zoning_code='UCB300',
            zoning_name='근린상업지역',
            category=ZoningCategory.COMMERCIAL,
            max_bcr=70.0,
            max_far=900.0,
            min_far=100.0,
            max_height=None,
            allowed_uses=['근린생활시설', '판매시설', '업무시설'],
            restricted_uses=['공장', '위험물저장시설'],
            incentive_available=True
        )
        
        db['유통상업지역'] = ZoningRegulations(
            zoning_code='UCB400',
            zoning_name='유통상업지역',
            category=ZoningCategory.COMMERCIAL,
            max_bcr=80.0,
            max_far=1100.0,
            min_far=150.0,
            max_height=None,
            allowed_uses=['판매시설', '운수시설', '창고시설'],
            restricted_uses=['위험물저장시설'],
            incentive_available=True
        )
        
        # 공업지역 (Industrial)
        db['전용공업지역'] = ZoningRegulations(
            zoning_code='UMA100',
            zoning_name='전용공업지역',
            category=ZoningCategory.INDUSTRIAL,
            max_bcr=70.0,
            max_far=300.0,
            min_far=None,
            max_height=None,
            allowed_uses=['공장', '창고시설', '위험물저장시설'],
            restricted_uses=['주택', '학교', '병원'],
            incentive_available=False
        )
        
        db['일반공업지역'] = ZoningRegulations(
            zoning_code='UMA200',
            zoning_name='일반공업지역',
            category=ZoningCategory.INDUSTRIAL,
            max_bcr=70.0,
            max_far=350.0,
            min_far=None,
            max_height=None,
            allowed_uses=['공장', '창고시설', '운수시설'],
            restricted_uses=['주택', '학교'],
            incentive_available=False
        )
        
        db['준공업지역'] = ZoningRegulations(
            zoning_code='UMA300',
            zoning_name='준공업지역',
            category=ZoningCategory.INDUSTRIAL,
            max_bcr=70.0,
            max_far=400.0,
            min_far=150.0,
            max_height=None,
            allowed_uses=['공장', '주택', '판매시설', '업무시설'],
            restricted_uses=['위험물저장시설'],
            incentive_available=True
        )
        
        # 녹지지역 (Green)
        db['보전녹지지역'] = ZoningRegulations(
            zoning_code='UGA100',
            zoning_name='보전녹지지역',
            category=ZoningCategory.GREEN,
            max_bcr=20.0,
            max_far=80.0,
            min_far=None,
            max_height=None,
            allowed_uses=['농림어업시설', '휴양시설'],
            restricted_uses=['주택', '상업시설', '공장'],
            incentive_available=False
        )
        
        db['생산녹지지역'] = ZoningRegulations(
            zoning_code='UGA200',
            zoning_name='생산녹지지역',
            category=ZoningCategory.GREEN,
            max_bcr=20.0,
            max_far=100.0,
            min_far=None,
            max_height=None,
            allowed_uses=['농림어업시설', '창고시설'],
            restricted_uses=['상업시설', '공장'],
            incentive_available=False
        )
        
        db['자연녹지지역'] = ZoningRegulations(
            zoning_code='UGA300',
            zoning_name='자연녹지지역',
            category=ZoningCategory.GREEN,
            max_bcr=20.0,
            max_far=100.0,
            min_far=None,
            max_height=None,
            allowed_uses=['농림어업시설', '단독주택', '근린생활시설'],
            restricted_uses=['공장', '위험물저장시설'],
            incentive_available=False
        )
        
        return db
    
    def _normalize_zoning_code(self, code: str) -> str:
        """
        Normalize zoning code to standard format
        
        Examples:
            '제2종일반주거지역' → '제2종일반주거지역'
            '제2종일반주거' → '제2종일반주거지역'
            'UQA210' → '제2종일반주거지역'
        """
        code = code.strip()
        
        # If already in database, return as is
        if code in self.zoning_db:
            return code
        
        # Try to match by official code
        for key, reg in self.zoning_db.items():
            if reg.zoning_code == code:
                return key
        
        # Try partial match
        for key in self.zoning_db.keys():
            if code in key or key in code:
                return key
        
        # Return original if no match
        return code
    
    def _get_zoning_regulations(self, code: str) -> Optional[ZoningRegulations]:
        """Get zoning regulations by code"""
        return self.zoning_db.get(code)
    
    def _analyze_incentives(self, 
                           regulations: ZoningRegulations,
                           land_area: float,
                           location: str) -> Dict:
        """
        Analyze incentive possibilities
        
        Korean urban planning incentives include:
        - 용적률 완화 (FAR bonus for public contributions)
        - 높이 완화 (Height limit relaxation)
        - 건폐율 완화 (BCR relaxation)
        """
        incentives = {
            'available': regulations.incentive_available,
            'types': [],
            'max_far_bonus': 0.0,
            'conditions': []
        }
        
        if not regulations.incentive_available:
            return incentives
        
        # Residential area incentives
        if regulations.category == ZoningCategory.RESIDENTIAL:
            if '일반주거지역' in regulations.zoning_name:
                incentives['types'].append('임대주택 건설')
                incentives['max_far_bonus'] = 30.0  # Up to 30% FAR bonus
                incentives['conditions'].append('임대주택 50% 이상 공급')
                
            if land_area >= 1000:
                incentives['types'].append('주택단지 계획')
                incentives['max_far_bonus'] = max(incentives['max_far_bonus'], 20.0)
                incentives['conditions'].append('1,000㎡ 이상 단지 계획')
        
        # Commercial area incentives
        if regulations.category == ZoningCategory.COMMERCIAL:
            incentives['types'].append('공개공지 제공')
            incentives['max_far_bonus'] = 20.0
            incentives['conditions'].append('대지 면적의 10% 공개공지')
            
            if location == 'seoul':
                incentives['types'].append('주차장 추가 확보')
                incentives['max_far_bonus'] = max(incentives['max_far_bonus'], 15.0)
                incentives['conditions'].append('법정 주차대수 120% 확보')
        
        # Industrial area incentives
        if regulations.zoning_name == '준공업지역':
            incentives['types'].append('주거복합 개발')
            incentives['max_far_bonus'] = 50.0
            incentives['conditions'].append('주거용도 30% 이상 포함')
        
        return incentives


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ZONING ENGINE v24.0 - CLI TEST")
    print("=" * 80)
    
    engine = ZoningEngine()
    
    # Test cases
    test_cases = [
        {
            'name': 'Test 1: 제2종일반주거지역',
            'input': {
                'zoning_code': '제2종일반주거지역',
                'land_area_sqm': 660.0,
                'location': 'seoul'
            }
        },
        {
            'name': 'Test 2: 준주거지역 (대형 필지)',
            'input': {
                'zoning_code': '준주거지역',
                'land_area_sqm': 2000.0,
                'location': 'seoul'
            }
        },
        {
            'name': 'Test 3: 일반상업지역',
            'input': {
                'zoning_code': '일반상업지역',
                'land_area_sqm': 500.0,
                'location': 'seoul'
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
            print(f"\n용도지역: {result['zoning_name']} ({result['category']})")
            print(f"\n법정 규제:")
            print(f"  - 최대 건폐율: {result['regulations']['max_bcr']}%")
            print(f"  - 최대 용적률: {result['regulations']['max_far']}%")
            if result['regulations']['min_far']:
                print(f"  - 최소 용적률: {result['regulations']['min_far']}%")
            
            print(f"\n허용 용도: {', '.join(result['allowed_uses'][:3])}...")
            print(f"제한 용도: {', '.join(result['restricted_uses'][:2])}...")
            
            if result['incentive_available']:
                print(f"\n✅ 인센티브 적용 가능")
                print(f"  - 종류: {', '.join(result['incentive_details']['types'])}")
                print(f"  - 최대 용적률 완화: +{result['incentive_details']['max_far_bonus']}%")
                print(f"  - 조건: {result['incentive_details']['conditions'][0]}")
            else:
                print(f"\n❌ 인센티브 적용 불가")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)
