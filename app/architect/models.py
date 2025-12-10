"""
ZeroSite Phase 11: Architecture Design Models

Data structures for automated building design based on LH housing standards.

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.0
"""

from typing import List, Dict, Optional, Literal
from dataclasses import dataclass
from enum import Enum


class SupplyType(str, Enum):
    """LH 매입임대 공급유형"""
    YOUTH = "Y"  # 청년형
    NEWLYWED = "N"  # 신혼부부형
    GENERAL = "A"  # 일반형(시세 이하)
    SENIOR = "S"  # 고령자형
    MIXED = "M"  # 혼합형(지자체/특화형)


class DesignStrategy(str, Enum):
    """설계 전략"""
    STABLE = "stable"  # 안정형: LH 점수 최대화
    STANDARD = "standard"  # 표준형: 균형
    PROFIT = "profit"  # 수익형: ROI 최대화


@dataclass
class UnitType:
    """단위 세대 타입"""
    size_sqm: float  # 전용면적 (㎡)
    count: int  # 세대수
    name: str  # 명칭 (예: "소형Ⅰ 22㎡")
    
    @property
    def total_area(self) -> float:
        """총 전용면적"""
        return self.size_sqm * self.count


@dataclass
class BuildableVolume:
    """건축 가능 규모"""
    total_gfa: float  # 총 연면적 (㎡)
    max_units: int  # 최대 세대수
    building_coverage: float  # 건축면적 (㎡)
    floor_count: int  # 층수
    strategy: DesignStrategy  # 적용 전략


@dataclass
class ParkingRequirement:
    """주차 요구사항"""
    required_spots: int  # 법정 주차대수
    provided_spots: int  # 계획 주차대수
    underground_spots: int  # 지하 주차대수
    surface_spots: int  # 지상 주차대수
    disabled_spots: int  # 장애인 주차대수
    
    @property
    def compliance_rate(self) -> float:
        """주차 확보율"""
        if self.required_spots == 0:
            return 1.0
        return self.provided_spots / self.required_spots


@dataclass
class GeometryLayout:
    """배치도 (간단한 블록 레이아웃)"""
    blocks: List[Dict[str, float]]  # [{"x": 0, "y": 0, "width": 10, "height": 20}, ...]
    total_footprint: float  # 건축면적
    site_coverage_ratio: float  # 건폐율
    
    def to_svg(self) -> str:
        """간단한 SVG 생성"""
        svg_parts = ['<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">']
        
        for i, block in enumerate(self.blocks):
            x = block.get("x", 0) * 10
            y = block.get("y", 0) * 10
            w = block.get("width", 0) * 10
            h = block.get("height", 0) * 10
            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                f'fill="#667eea" stroke="#333" stroke-width="2" opacity="0.8"/>'
            )
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)


@dataclass
class DesignMetrics:
    """설계 지표"""
    efficiency_ratio: float  # 전용률 (전용면적/연면적)
    es_ratio: float  # E/S 비율
    common_area_ratio: float  # 공용면적 비율
    green_ratio: float  # 녹지율
    


@dataclass
class BuildingDesign:
    """건축 설계안"""
    design_id: str  # 설계 ID
    strategy: DesignStrategy  # 설계 전략
    supply_type: SupplyType  # 공급유형
    
    # 규모
    volume: BuildableVolume  # 건축 규모
    unit_mix: List[UnitType]  # 평형 구성
    
    # 시설
    parking: ParkingRequirement  # 주차
    layout: GeometryLayout  # 배치도
    
    # 지표
    metrics: DesignMetrics  # 설계 지표
    
    # 평가 (연결 예정)
    financial_score: Optional[float] = None  # 재무 점수
    lh_score: Optional[float] = None  # LH 평가 점수
    
    @property
    def total_units(self) -> int:
        """총 세대수"""
        return sum(u.count for u in self.unit_mix)
    
    @property
    def average_unit_size(self) -> float:
        """평균 세대 면적"""
        if self.total_units == 0:
            return 0
        total_area = sum(u.total_area for u in self.unit_mix)
        return total_area / self.total_units
    
    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        return {
            "design_id": self.design_id,
            "strategy": self.strategy.value,
            "supply_type": self.supply_type.value,
            "total_gfa": self.volume.total_gfa,
            "total_units": self.total_units,
            "average_unit_size": self.average_unit_size,
            "unit_mix": [
                {
                    "size": u.size_sqm,
                    "count": u.count,
                    "name": u.name,
                    "total_area": u.total_area
                }
                for u in self.unit_mix
            ],
            "parking": {
                "required": self.parking.required_spots,
                "provided": self.parking.provided_spots,
                "compliance_rate": self.parking.compliance_rate
            },
            "metrics": {
                "efficiency_ratio": self.metrics.efficiency_ratio,
                "es_ratio": self.metrics.es_ratio,
                "common_area_ratio": self.metrics.common_area_ratio,
                "green_ratio": self.metrics.green_ratio
            },
            "financial_score": self.financial_score,
            "lh_score": self.lh_score
        }


@dataclass
class DesignComparisonResult:
    """설계안 비교 결과"""
    designs: List[BuildingDesign]  # A/B/C 설계안
    recommended: DesignStrategy  # 추천안
    comparison_table: Dict  # 비교표
    
    def get_best_by_lh_score(self) -> Optional[BuildingDesign]:
        """LH 점수 최고안"""
        scored = [d for d in self.designs if d.lh_score is not None]
        if not scored:
            return None
        return max(scored, key=lambda d: d.lh_score)
    
    def get_best_by_roi(self) -> Optional[BuildingDesign]:
        """ROI 최고안"""
        scored = [d for d in self.designs if d.financial_score is not None]
        if not scored:
            return None
        return max(scored, key=lambda d: d.financial_score)


# LH 표준 평형 정의
LH_UNIT_SIZES = {
    "소형Ⅰ": 22.0,  # 18~26㎡
    "소형Ⅱ": 30.0,  # 26~36㎡
    "중형Ⅰ": 42.0,  # 36~46㎡
    "중형Ⅱ": 50.0,  # 46~55㎡
    "중형Ⅲ": 58.0,  # 55~60㎡
}

# LH 공급유형별 권장 구성비율
LH_DISTRIBUTION_RATIOS = {
    SupplyType.YOUTH: {
        "소형Ⅰ": 0.70,
        "소형Ⅱ": 0.30,
        "중형Ⅰ": 0.00,
        "중형Ⅱ": 0.00,
        "중형Ⅲ": 0.00,
    },
    SupplyType.NEWLYWED: {
        "소형Ⅰ": 0.00,
        "소형Ⅱ": 0.50,
        "중형Ⅰ": 0.35,
        "중형Ⅱ": 0.15,
        "중형Ⅲ": 0.00,
    },
    SupplyType.GENERAL: {
        "소형Ⅰ": 0.20,
        "소형Ⅱ": 0.30,
        "중형Ⅰ": 0.30,
        "중형Ⅱ": 0.15,
        "중형Ⅲ": 0.05,
    },
    SupplyType.SENIOR: {
        "소형Ⅰ": 0.20,
        "소형Ⅱ": 0.20,
        "중형Ⅰ": 0.20,
        "중형Ⅱ": 0.20,
        "중형Ⅲ": 0.20,
    },
    SupplyType.MIXED: {
        "소형Ⅰ": 0.25,
        "소형Ⅱ": 0.25,
        "중형Ⅰ": 0.25,
        "중형Ⅱ": 0.15,
        "중형Ⅲ": 0.10,
    },
}
