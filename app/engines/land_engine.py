"""
Land Engine v24.0
토지 분석 엔진 for ZeroSite v24

Features:
- 지형 분석 (평탄도, 경사도)
- 접도 조건 평가 (도로 폭, 접도 길이)
- 필지 형상 분석 (정형/부정형)
- 고저차 분석
- 개발 용이성 평가

Author: ZeroSite v24 Team
Date: 2025-12-12
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging
from .base_engine import BaseEngine

logger = logging.getLogger(__name__)


class TerrainType(Enum):
    """지형 유형"""
    FLAT = "평탄지"
    GENTLE_SLOPE = "완경사지"
    STEEP_SLOPE = "급경사지"
    IRREGULAR = "부정형지"


class RoadAccessLevel(Enum):
    """접도 수준"""
    EXCELLENT = "우수"
    GOOD = "양호"
    FAIR = "보통"
    POOR = "불량"


@dataclass
class LandCharacteristics:
    """토지 특성"""
    terrain_type: TerrainType
    slope_percent: float
    elevation_diff: float
    road_width: float
    road_access_length: float
    shape_regularity: float  # 0-100 (100 = perfect rectangle)
    development_difficulty: str


class LandEngine(BaseEngine):
    """
    토지 분석 엔진
    
    Key Features:
    - 지형 분석 (평탄도, 경사도)
    - 접도 조건 평가
    - 필지 형상 분석
    - 고저차 분석
    - 개발 용이성 종합 평가
    
    Input:
        {
            'land_area_sqm': float,
            'land_width': float (m),
            'land_depth': float (m),
            'slope_percent': float (optional),
            'elevation_diff': float (optional, m),
            'road_width': float (optional, m),
            'road_access_length': float (optional, m)
        }
    
    Output:
        {
            'terrain_analysis': {...},
            'road_access': {...},
            'shape_analysis': {...},
            'development_score': float (0-100),
            'recommendations': List[str]
        }
    """
    
    def __init__(self):
        super().__init__(engine_name="LandEngine", version="24.0")
    
    @property
    def timestamp(self):
        return self.created_at.isoformat()
    
    def process(self, input_data: Dict) -> Dict:
        """Main processing method"""
        self.validate_input(input_data, ['land_area_sqm'])
        
        land_area = input_data['land_area_sqm']
        width = input_data.get('land_width', 0)
        depth = input_data.get('land_depth', 0)
        slope = input_data.get('slope_percent', 0)
        elevation_diff = input_data.get('elevation_diff', 0)
        road_width = input_data.get('road_width', 6.0)
        road_access_length = input_data.get('road_access_length', width)
        
        # If width/depth not provided, estimate from area
        if width == 0 or depth == 0:
            width, depth = self._estimate_dimensions(land_area)
        
        # Analyze terrain
        terrain_analysis = self._analyze_terrain(slope, elevation_diff)
        
        # Analyze road access
        road_access = self._analyze_road_access(
            road_width, road_access_length, width
        )
        
        # Analyze shape
        shape_analysis = self._analyze_shape(
            land_area, width, depth
        )
        
        # Calculate development score
        dev_score = self._calculate_development_score(
            terrain_analysis, road_access, shape_analysis
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            terrain_analysis, road_access, shape_analysis
        )
        
        result = {
            'success': True,
            'land_area_sqm': land_area,
            'dimensions': {
                'width': round(width, 2),
                'depth': round(depth, 2),
                'width_depth_ratio': round(width / depth if depth > 0 else 0, 2)
            },
            'terrain_analysis': terrain_analysis,
            'road_access': road_access,
            'shape_analysis': shape_analysis,
            'development_score': round(dev_score, 1),
            'development_grade': self._get_grade(dev_score),
            'recommendations': recommendations
        }
        
        self.logger.info(f"Land analysis complete: Score {dev_score}/100, Grade {result['development_grade']}")
        return result
    
    def _estimate_dimensions(self, area: float) -> tuple:
        """Estimate land dimensions from area"""
        # Assume 1:1.5 ratio (typical Korean urban plot)
        width = (area / 1.5) ** 0.5
        depth = width * 1.5
        return width, depth
    
    def _analyze_terrain(self, slope: float, elevation_diff: float) -> Dict:
        """Analyze terrain characteristics"""
        if slope < 5:
            terrain_type = TerrainType.FLAT
            difficulty = "쉬움"
            cost_impact = 1.0
        elif slope < 15:
            terrain_type = TerrainType.GENTLE_SLOPE
            difficulty = "보통"
            cost_impact = 1.1
        elif slope < 30:
            terrain_type = TerrainType.STEEP_SLOPE
            difficulty = "어려움"
            cost_impact = 1.3
        else:
            terrain_type = TerrainType.IRREGULAR
            difficulty = "매우 어려움"
            cost_impact = 1.5
        
        return {
            'terrain_type': terrain_type.value,
            'slope_percent': slope,
            'elevation_diff_m': elevation_diff,
            'development_difficulty': difficulty,
            'cost_impact_multiplier': cost_impact,
            'requires_retaining_wall': slope > 15 or elevation_diff > 3,
            'requires_cut_fill': slope > 10 or elevation_diff > 2
        }
    
    def _analyze_road_access(self, 
                            road_width: float, 
                            access_length: float,
                            land_width: float) -> Dict:
        """Analyze road access conditions"""
        # Determine access level
        if road_width >= 12:
            access_level = RoadAccessLevel.EXCELLENT
            score = 100
        elif road_width >= 8:
            access_level = RoadAccessLevel.GOOD
            score = 85
        elif road_width >= 6:
            access_level = RoadAccessLevel.FAIR
            score = 70
        else:
            access_level = RoadAccessLevel.POOR
            score = 50
        
        # Bonus for good access ratio
        access_ratio = (access_length / land_width) * 100 if land_width > 0 else 0
        if access_ratio > 80:
            score = min(100, score + 10)
        
        return {
            'road_width_m': road_width,
            'road_access_length_m': access_length,
            'access_ratio_percent': round(access_ratio, 1),
            'access_level': access_level.value,
            'access_score': score,
            'meets_building_code': road_width >= 4,  # 건축법 최소 4m
            'allows_parking': road_width >= 6,
            'allows_large_vehicles': road_width >= 8
        }
    
    def _analyze_shape(self, area: float, width: float, depth: float) -> Dict:
        """Analyze land shape regularity"""
        # Calculate regularity score (0-100)
        ratio = width / depth if depth > 0 else 0
        ideal_ratio = 1.5  # Korean standard
        
        # Score based on deviation from ideal
        deviation = abs(ratio - ideal_ratio) / ideal_ratio
        regularity = max(0, 100 - (deviation * 100))
        
        # Shape classification
        if regularity > 85:
            shape_class = "정형지 (Regular)"
            usable_ratio = 0.95
        elif regularity > 70:
            shape_class = "준정형지 (Semi-regular)"
            usable_ratio = 0.90
        elif regularity > 50:
            shape_class = "부정형지 (Irregular)"
            usable_ratio = 0.85
        else:
            shape_class = "극부정형지 (Highly irregular)"
            usable_ratio = 0.75
        
        usable_area = area * usable_ratio
        
        return {
            'shape_classification': shape_class,
            'regularity_score': round(regularity, 1),
            'width_depth_ratio': round(ratio, 2),
            'ideal_ratio': ideal_ratio,
            'usable_area_ratio': usable_ratio,
            'usable_area_sqm': round(usable_area, 2),
            'wasted_area_sqm': round(area - usable_area, 2)
        }
    
    def _calculate_development_score(self,
                                     terrain: Dict,
                                     road: Dict,
                                     shape: Dict) -> float:
        """Calculate overall development score (0-100)"""
        # Weighted average
        terrain_score = 100 - (terrain['slope_percent'] * 2)  # Max deduction 60
        terrain_score = max(40, min(100, terrain_score))
        
        road_score = road['access_score']
        shape_score = shape['regularity_score']
        
        # Weights: terrain 30%, road 40%, shape 30%
        total_score = (
            terrain_score * 0.3 +
            road_score * 0.4 +
            shape_score * 0.3
        )
        
        return total_score
    
    def _get_grade(self, score: float) -> str:
        """Convert score to grade"""
        if score >= 90:
            return "A+ (최우수)"
        elif score >= 80:
            return "A (우수)"
        elif score >= 70:
            return "B (양호)"
        elif score >= 60:
            return "C (보통)"
        else:
            return "D (불량)"
    
    def _generate_recommendations(self,
                                 terrain: Dict,
                                 road: Dict,
                                 shape: Dict) -> List[str]:
        """Generate development recommendations"""
        recommendations = []
        
        # Terrain recommendations
        if terrain['requires_retaining_wall']:
            recommendations.append("옹벽 또는 절토/성토 공사 필요")
        if terrain['slope_percent'] > 15:
            recommendations.append("지하주차장 계획 시 경사 고려 필요")
        
        # Road access recommendations
        if not road['allows_large_vehicles']:
            recommendations.append("대형 차량 진입 불가 - 공사 동선 사전 계획 필요")
        if road['access_ratio_percent'] < 50:
            recommendations.append("접도율 부족 - 필지 결합 또는 도로 확보 검토")
        
        # Shape recommendations
        if shape['regularity_score'] < 70:
            recommendations.append("부정형 필지 - 건축 배치 최적화 필요")
        if shape['wasted_area_sqm'] > 50:
            recommendations.append(f"활용 불가 면적 {shape['wasted_area_sqm']:.0f}㎡ - 조경 또는 부속 시설 계획")
        
        if not recommendations:
            recommendations.append("양호한 개발 여건 - 특별한 제약 사항 없음")
        
        return recommendations


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("LAND ENGINE v24.0 - CLI TEST")
    print("=" * 80)
    
    engine = LandEngine()
    
    test_cases = [
        {
            'name': 'Test 1: 평탄한 정형지 (이상적)',
            'input': {
                'land_area_sqm': 660.0,
                'land_width': 22.0,
                'land_depth': 30.0,
                'slope_percent': 3.0,
                'elevation_diff': 1.0,
                'road_width': 8.0,
                'road_access_length': 22.0
            }
        },
        {
            'name': 'Test 2: 경사지 부정형',
            'input': {
                'land_area_sqm': 500.0,
                'land_width': 15.0,
                'land_depth': 35.0,
                'slope_percent': 18.0,
                'elevation_diff': 5.0,
                'road_width': 6.0,
                'road_access_length': 10.0
            }
        },
        {
            'name': 'Test 3: 소형 필지 좁은 도로',
            'input': {
                'land_area_sqm': 300.0,
                'land_width': 10.0,
                'land_depth': 30.0,
                'slope_percent': 2.0,
                'elevation_diff': 0.5,
                'road_width': 4.0,
                'road_access_length': 10.0
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"{test['name']}")
        print("=" * 80)
        
        result = engine.process(test['input'])
        
        if result.get('success'):
            print(f"✅ Engine: {engine.engine_name} v{engine.version}")
            print(f"\n📐 필지 규모: {result['land_area_sqm']}㎡")
            print(f"   - 폭: {result['dimensions']['width']}m")
            print(f"   - 깊이: {result['dimensions']['depth']}m")
            print(f"   - 폭/깊이 비율: {result['dimensions']['width_depth_ratio']}")
            
            print(f"\n🏔️ 지형 분석:")
            print(f"   - 유형: {result['terrain_analysis']['terrain_type']}")
            print(f"   - 경사도: {result['terrain_analysis']['slope_percent']}%")
            print(f"   - 고저차: {result['terrain_analysis']['elevation_diff_m']}m")
            print(f"   - 개발 난이도: {result['terrain_analysis']['development_difficulty']}")
            
            print(f"\n🛣️ 접도 조건:")
            print(f"   - 도로 폭: {result['road_access']['road_width_m']}m")
            print(f"   - 접도 길이: {result['road_access']['road_access_length_m']}m")
            print(f"   - 접도율: {result['road_access']['access_ratio_percent']}%")
            print(f"   - 평가: {result['road_access']['access_level']}")
            
            print(f"\n📏 형상 분석:")
            print(f"   - 분류: {result['shape_analysis']['shape_classification']}")
            print(f"   - 정형도: {result['shape_analysis']['regularity_score']}/100")
            print(f"   - 활용 가능 면적: {result['shape_analysis']['usable_area_sqm']}㎡")
            
            print(f"\n⭐ 종합 평가:")
            print(f"   - 개발 점수: {result['development_score']}/100")
            print(f"   - 등급: {result['development_grade']}")
            
            print(f"\n💡 권장 사항:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"   {i}. {rec}")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)
