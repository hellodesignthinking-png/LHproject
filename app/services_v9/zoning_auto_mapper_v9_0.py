"""
Zoning Auto Mapper Service for ZeroSite v9.1

Provides automatic building standards mapping based on zoning type:
- Building coverage ratio
- Floor area ratio
- Height limits
- Parking requirements

Based on Korean Building Act and Urban Planning Act.

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.1
"""

import logging
from typing import Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ZoningStandards:
    """
    용도지역 법정 기준
    
    Attributes:
        zone_type: 용도지역명
        building_coverage_ratio: 건폐율 (%)
        floor_area_ratio: 용적률 (%)
        max_height: 최대 높이 제한 (m, None=무제한)
        parking_ratio: 주차 대수 비율 (세대당 대수)
        description: 용도지역 설명
    """
    zone_type: str
    building_coverage_ratio: float
    floor_area_ratio: float
    max_height: Optional[float] = None
    parking_ratio: float = 1.0
    description: str = ""


class ZoningAutoMapperV9:
    """
    용도지역별 법정 기준 자동 매핑 서비스
    
    Features:
    - 용도지역 → 건폐율/용적률 자동 설정
    - 법정 주차 대수 계산
    - 층수 제한 자동 설정
    - 용도지역별 규제 정보 제공
    
    Based On:
    - 국토의 계획 및 이용에 관한 법률 (국토계획법)
    - 건축법
    - 주차장법
    
    Usage:
        mapper = ZoningAutoMapperV9()
        standards = mapper.get_zoning_standards("제3종일반주거지역")
        
        print(standards.building_coverage_ratio)  # 50.0
        print(standards.floor_area_ratio)         # 300.0
    """
    
    # 용도지역 법정 기준표 (국토계획법 기준)
    ZONING_STANDARDS = {
        # 주거지역
        "제1종전용주거지역": {
            "building_coverage_ratio": 50.0,
            "floor_area_ratio": 100.0,
            "max_height": None,
            "parking_ratio": 1.0,
            "description": "저층 단독주택 중심 지역"
        },
        "제2종전용주거지역": {
            "building_coverage_ratio": 50.0,
            "floor_area_ratio": 150.0,
            "max_height": None,
            "parking_ratio": 1.0,
            "description": "중층 단독/공동주택 중심 지역"
        },
        "제1종일반주거지역": {
            "building_coverage_ratio": 60.0,
            "floor_area_ratio": 200.0,
            "max_height": None,
            "parking_ratio": 1.0,
            "description": "저층 주택 위주 지역, 편리성 고려"
        },
        "제2종일반주거지역": {
            "building_coverage_ratio": 60.0,
            "floor_area_ratio": 250.0,
            "max_height": None,
            "parking_ratio": 1.0,
            "description": "중층 주택 위주 지역"
        },
        "제3종일반주거지역": {
            "building_coverage_ratio": 50.0,
            "floor_area_ratio": 300.0,
            "max_height": None,
            "parking_ratio": 1.0,
            "description": "중고층 주택 위주 지역"
        },
        "준주거지역": {
            "building_coverage_ratio": 70.0,
            "floor_area_ratio": 500.0,
            "max_height": None,
            "parking_ratio": 1.0,
            "description": "주거 + 상업/업무 복합 지역"
        },
        
        # 상업지역
        "중심상업지역": {
            "building_coverage_ratio": 90.0,
            "floor_area_ratio": 1500.0,
            "max_height": None,
            "parking_ratio": 0.5,
            "description": "도심/부도심 중심 상업 지역"
        },
        "일반상업지역": {
            "building_coverage_ratio": 80.0,
            "floor_area_ratio": 1300.0,
            "max_height": None,
            "parking_ratio": 0.5,
            "description": "일반적인 상업 및 업무 지역"
        },
        "근린상업지역": {
            "building_coverage_ratio": 70.0,
            "floor_area_ratio": 900.0,
            "max_height": None,
            "parking_ratio": 0.7,
            "description": "근린 생활 중심 상업 지역"
        },
        "유통상업지역": {
            "building_coverage_ratio": 80.0,
            "floor_area_ratio": 1100.0,
            "max_height": None,
            "parking_ratio": 1.5,
            "description": "도매/물류/유통 중심 지역"
        },
        
        # 공업지역
        "전용공업지역": {
            "building_coverage_ratio": 70.0,
            "floor_area_ratio": 300.0,
            "max_height": None,
            "parking_ratio": 0.3,
            "description": "중화학공업 등 공해성 공업 지역"
        },
        "일반공업지역": {
            "building_coverage_ratio": 70.0,
            "floor_area_ratio": 350.0,
            "max_height": None,
            "parking_ratio": 0.3,
            "description": "환경오염 적은 공업 지역"
        },
        "준공업지역": {
            "building_coverage_ratio": 70.0,
            "floor_area_ratio": 400.0,
            "max_height": None,
            "parking_ratio": 0.5,
            "description": "경공업 및 주거/상업 복합 가능"
        },
        
        # 녹지지역
        "보전녹지지역": {
            "building_coverage_ratio": 20.0,
            "floor_area_ratio": 80.0,
            "max_height": None,
            "parking_ratio": 1.0,
            "description": "자연환경 보전 필요 지역"
        },
        "생산녹지지역": {
            "building_coverage_ratio": 20.0,
            "floor_area_ratio": 100.0,
            "max_height": None,
            "parking_ratio": 1.0,
            "description": "농업 생산 및 환경보호 지역"
        },
        "자연녹지지역": {
            "building_coverage_ratio": 20.0,
            "floor_area_ratio": 100.0,
            "max_height": None,
            "parking_ratio": 1.0,
            "description": "자연환경 보호 + 제한적 개발"
        },
        
        # 미분류/기본값
        "미지정": {
            "building_coverage_ratio": 50.0,
            "floor_area_ratio": 200.0,
            "max_height": None,
            "parking_ratio": 1.0,
            "description": "용도지역 미지정 (기본값)"
        }
    }
    
    # 용도지역 별칭 매핑 (입력 편의성)
    ZONE_ALIASES = {
        # 주거지역 별칭
        "1종전용": "제1종전용주거지역",
        "2종전용": "제2종전용주거지역",
        "1종일반": "제1종일반주거지역",
        "2종일반": "제2종일반주거지역",
        "3종일반": "제3종일반주거지역",
        "준주거": "준주거지역",
        
        # 상업지역 별칭
        "중심상업": "중심상업지역",
        "일반상업": "일반상업지역",
        "근린상업": "근린상업지역",
        "유통상업": "유통상업지역",
        
        # 공업지역 별칭
        "전용공업": "전용공업지역",
        "일반공업": "일반공업지역",
        "준공업": "준공업지역",
        
        # 녹지지역 별칭
        "보전녹지": "보전녹지지역",
        "생산녹지": "생산녹지지역",
        "자연녹지": "자연녹지지역"
    }
    
    def __init__(self):
        """Initialize ZoningAutoMapperV9"""
        logger.info(f"✅ ZoningAutoMapperV9 initialized ({len(self.ZONING_STANDARDS)} zone types)")
    
    def get_zoning_standards(self, zone_type: str) -> Optional[ZoningStandards]:
        """
        용도지역 법정 기준 조회
        
        Args:
            zone_type: 용도지역명
                예: "제3종일반주거지역"
                예: "3종일반" (별칭 가능)
                예: "준주거지역"
        
        Returns:
            ZoningStandards: 법정 기준
                - building_coverage_ratio: 건폐율 (%)
                - floor_area_ratio: 용적률 (%)
                - max_height: 최대 높이 (m)
                - parking_ratio: 주차 비율
                - description: 설명
            
            None: 알 수 없는 용도지역
        
        Example:
            >>> mapper = ZoningAutoMapperV9()
            >>> standards = mapper.get_zoning_standards("3종일반")
            >>> print(standards.building_coverage_ratio)
            50.0
            >>> print(standards.floor_area_ratio)
            300.0
        """
        if not zone_type:
            logger.warning("⚠️ 용도지역이 입력되지 않음 → 기본값 사용")
            zone_type = "미지정"
        
        # 별칭 변환
        original_zone = zone_type
        zone_type = self.ZONE_ALIASES.get(zone_type, zone_type)
        
        if original_zone != zone_type:
            logger.info(f"📝 용도지역 별칭 변환: {original_zone} → {zone_type}")
        
        # 기준 조회
        standards_dict = self.ZONING_STANDARDS.get(zone_type)
        
        if not standards_dict:
            logger.warning(f"⚠️ 알 수 없는 용도지역: {zone_type} → 기본값 사용")
            standards_dict = self.ZONING_STANDARDS["미지정"]
            zone_type = "미지정"
        
        # ZoningStandards 객체 생성
        standards = ZoningStandards(
            zone_type=zone_type,
            building_coverage_ratio=standards_dict["building_coverage_ratio"],
            floor_area_ratio=standards_dict["floor_area_ratio"],
            max_height=standards_dict.get("max_height"),
            parking_ratio=standards_dict.get("parking_ratio", 1.0),
            description=standards_dict.get("description", "")
        )
        
        logger.info(
            f"✅ 용도지역 기준 조회 성공: {zone_type}\n"
            f"   건폐율: {standards.building_coverage_ratio}%\n"
            f"   용적률: {standards.floor_area_ratio}%\n"
            f"   주차비율: {standards.parking_ratio}대/세대"
        )
        
        return standards
    
    def calculate_parking_spaces(
        self,
        zone_type: str,
        unit_count: int
    ) -> int:
        """
        법정 주차 대수 계산
        
        Args:
            zone_type: 용도지역
            unit_count: 세대수
        
        Returns:
            int: 법정 주차 대수
        
        Example:
            >>> mapper = ZoningAutoMapperV9()
            >>> parking = mapper.calculate_parking_spaces("제3종일반주거지역", 50)
            >>> print(parking)
            50  # 세대당 1.0대
        """
        standards = self.get_zoning_standards(zone_type)
        
        if not standards:
            # 기본값: 세대당 1대
            return unit_count
        
        parking_spaces = int(unit_count * standards.parking_ratio)
        
        logger.info(f"🚗 주차 대수 계산: {unit_count}세대 × {standards.parking_ratio} = {parking_spaces}대")
        
        return parking_spaces
    
    def get_all_zone_types(self) -> list[str]:
        """
        전체 용도지역 목록 반환
        
        Returns:
            list[str]: 용도지역 목록
        
        Example:
            >>> mapper = ZoningAutoMapperV9()
            >>> zones = mapper.get_all_zone_types()
            >>> print(zones[:3])
            ['제1종전용주거지역', '제2종전용주거지역', '제1종일반주거지역']
        """
        return list(self.ZONING_STANDARDS.keys())
    
    def is_valid_zone_type(self, zone_type: str) -> bool:
        """
        용도지역 유효성 검증
        
        Args:
            zone_type: 검증할 용도지역명
        
        Returns:
            bool: 유효하면 True, 아니면 False
        
        Example:
            >>> mapper = ZoningAutoMapperV9()
            >>> mapper.is_valid_zone_type("제3종일반주거지역")
            True
            >>> mapper.is_valid_zone_type("존재하지않는지역")
            False
        """
        # 별칭 변환 적용
        zone_type = self.ZONE_ALIASES.get(zone_type, zone_type)
        return zone_type in self.ZONING_STANDARDS


# 전역 인스턴스 (싱글톤)
_zoning_mapper: Optional[ZoningAutoMapperV9] = None


def get_zoning_mapper() -> ZoningAutoMapperV9:
    """
    ZoningAutoMapperV9 싱글톤 인스턴스 획득
    
    Returns:
        ZoningAutoMapperV9: 전역 인스턴스
    
    Usage:
        mapper = get_zoning_mapper()
        standards = mapper.get_zoning_standards("제3종일반주거지역")
    """
    global _zoning_mapper
    
    if _zoning_mapper is None:
        _zoning_mapper = ZoningAutoMapperV9()
    
    return _zoning_mapper
