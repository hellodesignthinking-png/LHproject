"""
ZeroSite v24.1 - FAR Engine (용적률 엔진)
Floor Area Ratio Calculation with 6 Types of Relaxation Bonuses

Calculates final FAR considering:
- Legal base FAR by zone
- 6 types of relaxation bonuses
- Cumulative bonus calculations
- Maximum FAR caps
- Policy compliance

Author: ZeroSite Development Team
Version: 24.1.0
Date: 2025-12-12
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

try:
    from .base_engine import BaseEngine
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from engines.base_engine import BaseEngine

logger = logging.getLogger(__name__)


class RelaxationType(Enum):
    """6 types of FAR relaxation bonuses"""
    GREEN_BUILDING = "녹색건축물 인증"
    PUBLIC_FACILITY = "공공시설 제공"
    UNDERGROUND_PARKING = "지하주차장 설치"
    SMALL_UNIT = "소형주택 건설"
    ENERGY_EFFICIENCY = "에너지 효율 1등급"
    BARRIER_FREE = "장애인 편의시설"


@dataclass
class RelaxationBonus:
    """Individual relaxation bonus"""
    type: RelaxationType
    percentage: float  # Bonus percentage (e.g., 15.0 for +15%)
    description: str
    requirements: List[str]
    applicable: bool
    approved: bool = False


@dataclass
class FARCalculationResult:
    """Complete FAR calculation result"""
    # Base values
    legal_far: float
    zone_type: str
    land_area: float
    
    # Relaxation bonuses
    relaxation_bonuses: List[Dict]
    total_bonus_percentage: float
    
    # Final calculation
    relaxed_far: float
    final_far: float  # After max cap
    max_far_cap: float
    capped: bool
    
    # Floor area calculations
    legal_floor_area: float  # Based on legal FAR
    final_floor_area: float  # Based on final FAR
    bonus_floor_area: float  # Additional area from bonuses
    
    # Summary
    total_bonus_applied: float
    calculation_steps: List[str]
    recommendations: List[str]


class FAREngineV241(BaseEngine):
    """
    FAR Calculation Engine with 6 Relaxation Types
    
    Features:
    - Legal FAR by zone type
    - 6 types of relaxation bonuses
    - Cumulative bonus calculation
    - Maximum FAR cap enforcement
    - Detailed step-by-step breakdown
    
    6 Relaxation Types:
    1. Green Building Certification (+15%)
    2. Public Facility Provision (+10%)
    3. Underground Parking (+5%)
    4. Small Unit Housing (+5%)
    5. Energy Efficiency Grade 1 (+10%)
    6. Barrier-Free Design (+5%)
    
    Maximum Total Bonus: +50% (policy limit)
    
    Input:
        zone_type: str
        legal_far: float
        land_area: float
        relaxation_options: Dict[str, bool]
    
    Output:
        FARCalculationResult with complete breakdown
    """
    
    # Relaxation bonus rates
    BONUS_RATES = {
        RelaxationType.GREEN_BUILDING: 15.0,
        RelaxationType.PUBLIC_FACILITY: 10.0,
        RelaxationType.UNDERGROUND_PARKING: 5.0,
        RelaxationType.SMALL_UNIT: 5.0,
        RelaxationType.ENERGY_EFFICIENCY: 10.0,
        RelaxationType.BARRIER_FREE: 5.0
    }
    
    # Requirements for each bonus type
    BONUS_REQUIREMENTS = {
        RelaxationType.GREEN_BUILDING: [
            "녹색건축 인증 본인증 취득",
            "에너지 절감률 30% 이상",
            "신재생에너지 사용"
        ],
        RelaxationType.PUBLIC_FACILITY: [
            "대지면적의 10% 이상 공공시설 제공",
            "어린이놀이터, 경로당 등 주민편의시설",
            "공공에 무상 제공"
        ],
        RelaxationType.UNDERGROUND_PARKING: [
            "주차장의 100% 지하화",
            "지상 녹지공간 확보",
            "우수저류시설 설치"
        ],
        RelaxationType.SMALL_UNIT: [
            "전용면적 60㎡ 이하 세대 50% 이상",
            "청년·신혼부부 우선 공급",
            "임대료 인근 시세의 80% 이하"
        ],
        RelaxationType.ENERGY_EFFICIENCY: [
            "건축물 에너지효율등급 1등급 인증",
            "고효율 설비 사용",
            "단열 성능 강화"
        ],
        RelaxationType.BARRIER_FREE: [
            "장애인 편의시설 설치 확인서 취득",
            "BF(Barrier Free) 인증 본인증",
            "최우수 등급 취득"
        ]
    }
    
    # Maximum total bonus cap
    MAX_TOTAL_BONUS = 50.0  # 50% maximum
    
    # Zone-specific max FAR caps (after relaxation)
    ZONE_MAX_CAPS = {
        "제1종일반주거지역": 250.0,
        "제2종일반주거지역": 350.0,
        "제3종일반주거지역": 400.0,
        "준주거지역": 600.0,
        "준공업지역": 500.0,
        "상업지역": 1500.0
    }
    
    def __init__(self):
        super().__init__(engine_name="FAREngine", version="24.1.0")
    
    def process(self, input_data: Dict) -> Dict:
        """
        Main processing method (BaseEngine interface)
        
        Args:
            input_data: {
                'zone_type': str,
                'legal_far': float,
                'land_area': float,
                'relaxation_options': {
                    'green_building': bool,
                    'public_facility': bool,
                    'underground_parking': bool,
                    'small_unit': bool,
                    'energy_efficiency': bool,
                    'barrier_free': bool
                }
            }
        
        Returns:
            Complete FAR calculation
        """
        self.validate_input(input_data, ['zone_type', 'legal_far', 'land_area'])
        
        zone_type = input_data['zone_type']
        legal_far = input_data['legal_far']
        land_area = input_data['land_area']
        relaxation_opts = input_data.get('relaxation_options', {})
        
        # Calculate FAR with relaxations
        result = self.calculate_final_far(
            zone_type=zone_type,
            legal_far=legal_far,
            land_area=land_area,
            relaxation_options=relaxation_opts
        )
        
        self.logger.info(
            f"FAR calculation complete: {legal_far}% → {result.final_far}% "
            f"(+{result.total_bonus_percentage}%)"
        )
        
        return self._result_to_dict(result)
    
    def calculate_final_far(self,
                           zone_type: str,
                           legal_far: float,
                           land_area: float,
                           relaxation_options: Dict[str, bool]) -> FARCalculationResult:
        """
        Calculate final FAR with all relaxation bonuses
        
        Steps:
        1. Start with legal FAR
        2. Calculate each applicable bonus
        3. Sum all bonuses (max 50%)
        4. Apply bonus to legal FAR
        5. Check zone-specific max cap
        6. Calculate floor areas
        """
        
        calculation_steps = []
        calculation_steps.append(f"기준 용적률: {legal_far}%")
        
        # Step 1: Determine applicable relaxations
        bonuses = self._calculate_bonuses(relaxation_options)
        
        # Step 2: Sum bonuses (with max cap)
        total_bonus = sum(b['percentage'] for b in bonuses)
        original_total = total_bonus
        
        if total_bonus > self.MAX_TOTAL_BONUS:
            calculation_steps.append(
                f"⚠️ 완화율 합계 {total_bonus}%가 상한 {self.MAX_TOTAL_BONUS}%를 초과"
            )
            total_bonus = self.MAX_TOTAL_BONUS
        
        calculation_steps.append(f"적용 완화율 합계: {total_bonus}%")
        
        # Step 3: Calculate relaxed FAR
        relaxed_far = legal_far * (1 + total_bonus / 100.0)
        calculation_steps.append(
            f"완화 후 용적률: {legal_far}% × (1 + {total_bonus}%) = {relaxed_far:.1f}%"
        )
        
        # Step 4: Apply zone-specific max cap
        max_cap = self._get_max_far_cap(zone_type)
        capped = relaxed_far > max_cap
        final_far = min(relaxed_far, max_cap)
        
        if capped:
            calculation_steps.append(
                f"⚠️ 용도지역 상한 적용: {relaxed_far:.1f}% → {final_far:.1f}%"
            )
        
        calculation_steps.append(f"최종 용적률: {final_far:.1f}%")
        
        # Step 5: Calculate floor areas
        legal_floor_area = land_area * (legal_far / 100.0)
        final_floor_area = land_area * (final_far / 100.0)
        bonus_floor_area = final_floor_area - legal_floor_area
        
        calculation_steps.append(f"\n[연면적 계산]")
        calculation_steps.append(f"법정 연면적: {legal_floor_area:,.1f}㎡")
        calculation_steps.append(f"최종 연면적: {final_floor_area:,.1f}㎡")
        calculation_steps.append(f"추가 확보: +{bonus_floor_area:,.1f}㎡")
        
        # Step 6: Generate recommendations
        recommendations = self._generate_recommendations(
            bonuses=bonuses,
            total_bonus=total_bonus,
            max_possible=original_total,
            capped=capped
        )
        
        return FARCalculationResult(
            legal_far=legal_far,
            zone_type=zone_type,
            land_area=land_area,
            relaxation_bonuses=bonuses,
            total_bonus_percentage=total_bonus,
            relaxed_far=relaxed_far,
            final_far=final_far,
            max_far_cap=max_cap,
            capped=capped,
            legal_floor_area=legal_floor_area,
            final_floor_area=final_floor_area,
            bonus_floor_area=bonus_floor_area,
            total_bonus_applied=total_bonus,
            calculation_steps=calculation_steps,
            recommendations=recommendations
        )
    
    def _calculate_bonuses(self, options: Dict[str, bool]) -> List[Dict]:
        """Calculate all applicable bonuses"""
        bonuses = []
        
        # Map option keys to RelaxationType
        option_mapping = {
            'green_building': RelaxationType.GREEN_BUILDING,
            'public_facility': RelaxationType.PUBLIC_FACILITY,
            'underground_parking': RelaxationType.UNDERGROUND_PARKING,
            'small_unit': RelaxationType.SMALL_UNIT,
            'energy_efficiency': RelaxationType.ENERGY_EFFICIENCY,
            'barrier_free': RelaxationType.BARRIER_FREE
        }
        
        for key, relax_type in option_mapping.items():
            if options.get(key, False):
                bonus = {
                    'type': relax_type.value,
                    'percentage': self.BONUS_RATES[relax_type],
                    'description': self._get_bonus_description(relax_type),
                    'requirements': self.BONUS_REQUIREMENTS[relax_type],
                    'applicable': True
                }
                bonuses.append(bonus)
        
        return bonuses
    
    def _get_bonus_description(self, relax_type: RelaxationType) -> str:
        """Get description for bonus type"""
        descriptions = {
            RelaxationType.GREEN_BUILDING: "녹색건축물 인증 취득 시 용적률 15% 추가 확보",
            RelaxationType.PUBLIC_FACILITY: "공공시설 제공 시 용적률 10% 추가 확보",
            RelaxationType.UNDERGROUND_PARKING: "주차장 지하화 시 용적률 5% 추가 확보",
            RelaxationType.SMALL_UNIT: "소형주택 50% 이상 건설 시 용적률 5% 추가 확보",
            RelaxationType.ENERGY_EFFICIENCY: "에너지효율 1등급 취득 시 용적률 10% 추가 확보",
            RelaxationType.BARRIER_FREE: "장애인 편의시설 최우수 등급 시 용적률 5% 추가 확보"
        }
        return descriptions.get(relax_type, "")
    
    def _get_max_far_cap(self, zone_type: str) -> float:
        """Get maximum FAR cap for zone type"""
        # Try exact match first
        if zone_type in self.ZONE_MAX_CAPS:
            return self.ZONE_MAX_CAPS[zone_type]
        
        # Try partial match
        for zone_key, cap in self.ZONE_MAX_CAPS.items():
            if zone_key in zone_type or zone_type in zone_key:
                return cap
        
        # Default cap
        return 500.0
    
    def _generate_recommendations(self,
                                 bonuses: List[Dict],
                                 total_bonus: float,
                                 max_possible: float,
                                 capped: bool) -> List[str]:
        """Generate recommendations based on calculation"""
        recommendations = []
        
        if not bonuses:
            recommendations.append("💡 용적률 완화 제도를 활용하여 최대 50% 추가 확보 가능")
            recommendations.append("💡 추천: 녹색건축물 인증(+15%) + 에너지효율 1등급(+10%)")
        
        if len(bonuses) < 3:
            recommendations.append(f"💡 현재 {len(bonuses)}개 완화 적용 - 추가 완화 검토 권장")
        
        if max_possible > self.MAX_TOTAL_BONUS:
            recommendations.append(
                f"⚠️ 선택한 완화율 합계({max_possible}%)가 상한({self.MAX_TOTAL_BONUS}%)을 초과하여 "
                f"{self.MAX_TOTAL_BONUS}%만 적용됨"
            )
        
        if capped:
            recommendations.append("⚠️ 용도지역 상한 규제로 인해 추가 완화 불가")
        else:
            remaining = self.MAX_TOTAL_BONUS - total_bonus
            if remaining > 0:
                recommendations.append(f"💡 추가로 {remaining}%p의 용적률 완화 여력 있음")
        
        if total_bonus >= 30:
            recommendations.append("✅ 높은 용적률 완화 적용으로 사업성 우수")
        
        return recommendations
    
    def _result_to_dict(self, result: FARCalculationResult) -> Dict:
        """Convert result to dictionary"""
        return {
            'base': {
                'legal_far': result.legal_far,
                'zone_type': result.zone_type,
                'land_area': result.land_area
            },
            'relaxation': {
                'bonuses': result.relaxation_bonuses,
                'total_bonus_percentage': result.total_bonus_percentage,
                'max_bonus_cap': self.MAX_TOTAL_BONUS
            },
            'calculation': {
                'legal_far': result.legal_far,
                'relaxed_far': result.relaxed_far,
                'final_far': result.final_far,
                'max_far_cap': result.max_far_cap,
                'capped': result.capped
            },
            'floor_area': {
                'legal_floor_area': result.legal_floor_area,
                'final_floor_area': result.final_floor_area,
                'bonus_floor_area': result.bonus_floor_area,
                'unit': '㎡'
            },
            'summary': {
                'total_bonus_applied': result.total_bonus_applied,
                'calculation_steps': result.calculation_steps,
                'recommendations': result.recommendations
            }
        }
    
    def get_all_relaxation_types(self) -> List[Dict]:
        """Get all available relaxation types with details"""
        types = []
        for relax_type in RelaxationType:
            types.append({
                'type': relax_type.value,
                'percentage': self.BONUS_RATES[relax_type],
                'description': self._get_bonus_description(relax_type),
                'requirements': self.BONUS_REQUIREMENTS[relax_type]
            })
        return types


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("FAR ENGINE v24.1 - CLI TEST")
    print("=" * 80)
    
    engine = FAREngineV241()
    
    # Test case: 제3종일반주거지역 with all 6 relaxations
    print("\n[TEST] 제3종일반주거지역 - 전체 완화 적용")
    print("-" * 80)
    
    test_input = {
        'zone_type': '제3종일반주거지역',
        'legal_far': 250.0,
        'land_area': 1500.0,
        'relaxation_options': {
            'green_building': True,
            'public_facility': True,
            'underground_parking': True,
            'small_unit': True,
            'energy_efficiency': True,
            'barrier_free': True
        }
    }
    
    result = engine.process(test_input)
    
    print(f"\n✅ Engine: {engine.engine_name} v{engine.version}")
    print(f"✅ Timestamp: {engine.created_at.isoformat()}")
    
    print(f"\n기준 정보:")
    print(f"  용도지역: {result['base']['zone_type']}")
    print(f"  법정 용적률: {result['base']['legal_far']}%")
    print(f"  대지면적: {result['base']['land_area']:,.0f}㎡")
    
    print(f"\n적용 완화:")
    for bonus in result['relaxation']['bonuses']:
        print(f"  ✓ {bonus['type']}: +{bonus['percentage']}%")
    
    print(f"\n계산 결과:")
    print(f"  완화 전 용적률: {result['calculation']['legal_far']}%")
    print(f"  완화율 합계: +{result['relaxation']['total_bonus_percentage']}%")
    print(f"  완화 후 용적률: {result['calculation']['relaxed_far']:.1f}%")
    print(f"  최종 용적률: {result['calculation']['final_far']:.1f}%")
    if result['calculation']['capped']:
        print(f"  ⚠️ 상한 적용: {result['calculation']['max_far_cap']}%")
    
    print(f"\n연면적:")
    print(f"  법정 연면적: {result['floor_area']['legal_floor_area']:,.1f}㎡")
    print(f"  최종 연면적: {result['floor_area']['final_floor_area']:,.1f}㎡")
    print(f"  추가 확보: +{result['floor_area']['bonus_floor_area']:,.1f}㎡")
    
    print(f"\n권장사항:")
    for rec in result['summary']['recommendations']:
        print(f"  {rec}")
    
    print("\n" + "=" * 80)
    print("All 6 relaxation types available:")
    for relax in engine.get_all_relaxation_types():
        print(f"  • {relax['type']}: +{relax['percentage']}%")
    print("=" * 80)
