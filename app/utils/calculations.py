"""
건축 규모 계산 유틸리티
"""

import math
from typing import Dict, Any
from app.schemas import ZoneInfo, BuildingCapacity


class BuildingCalculator:
    """건축 규모 계산기"""
    
    # 세대 유형별 전용면적 (㎡)
    UNIT_AREAS = {
        "청년형": 30,      # 청년 1인 가구용
        "신혼부부형": 50,  # 신혼부부 2-3인
        "고령자형": 40     # 고령자 1-2인
    }
    
    # 공용면적 비율
    COMMON_AREA_RATIO = 0.15  # 15%
    
    # 주차대수 산정 기준
    PARKING_RATIOS = {
        "청년형": 0.5,      # 세대당 0.5대
        "신혼부부형": 0.7,  # 세대당 0.7대
        "고령자형": 0.3     # 세대당 0.3대
    }
    
    # 층고 (m)
    FLOOR_HEIGHT = 3.0
    
    def calculate_capacity(
        self,
        land_area: float,
        zone_info: ZoneInfo,
        unit_type: str
    ) -> BuildingCapacity:
        """
        건축 규모 계산
        
        Args:
            land_area: 토지 면적(㎡)
            zone_info: 용도지역 정보
            unit_type: 세대 유형
            
        Returns:
            BuildingCapacity 객체
        """
        
        # 1. 건축면적 계산 (토지면적 × 건폐율)
        building_area = land_area * (zone_info.building_coverage_ratio / 100)
        
        # 2. 연면적 계산 (토지면적 × 용적률)
        total_floor_area = land_area * (zone_info.floor_area_ratio / 100)
        
        # 3. 층수 계산
        # 연면적을 건축면적으로 나누어 층수 산출
        calculated_floors = math.ceil(total_floor_area / building_area)
        
        # 높이제한 확인
        if zone_info.height_limit:
            max_floors_by_height = math.floor(zone_info.height_limit / self.FLOOR_HEIGHT)
            floors = min(calculated_floors, max_floors_by_height)
        else:
            # 일반적인 주거지역 층수 제한 적용
            max_floors = self._get_max_floors_by_zone(zone_info.zone_type)
            floors = min(calculated_floors, max_floors)
        
        # 4. 실제 연면적 재계산 (층수 제한 반영)
        actual_total_floor_area = building_area * floors
        
        # 5. 전용면적 계산 (공용면적 제외)
        net_area = actual_total_floor_area * (1 - self.COMMON_AREA_RATIO)
        
        # 6. 세대수 계산
        unit_area = self.UNIT_AREAS.get(unit_type, 30)
        units = math.floor(net_area / unit_area)
        
        # 7. 주차대수 계산
        parking_ratio = self.PARKING_RATIOS.get(unit_type, 0.5)
        parking_spaces = math.ceil(units * parking_ratio)
        
        return BuildingCapacity(
            building_area=round(building_area, 2),
            total_floor_area=round(actual_total_floor_area, 2),
            floors=floors,
            units=units,
            parking_spaces=parking_spaces
        )
    
    def _get_max_floors_by_zone(self, zone_type: str) -> int:
        """
        용도지역별 최대 층수 반환
        
        Args:
            zone_type: 용도지역
            
        Returns:
            최대 층수
        """
        zone_floor_limits = {
            "제1종전용주거지역": 4,
            "제2종전용주거지역": 5,
            "제1종일반주거지역": 7,
            "제2종일반주거지역": 15,
            "제3종일반주거지역": 20,
            "준주거지역": 20,
            "상업지역": 30,
            "준공업지역": 20,
        }
        
        for zone_name, limit in zone_floor_limits.items():
            if zone_name in zone_type:
                return limit
        
        # 기본값: 15층
        return 15
    
    def calculate_construction_cost(
        self,
        building_capacity: BuildingCapacity,
        unit_type: str
    ) -> Dict[str, Any]:
        """
        건축 비용 추정
        
        Args:
            building_capacity: 건축 규모
            unit_type: 세대 유형
            
        Returns:
            비용 정보 딕셔너리
        """
        # 평당 건축비 (만원/평)
        cost_per_pyeong = {
            "청년형": 450,      # 일반 마감
            "신혼부부형": 500,  # 중급 마감
            "고령자형": 520     # 고급 마감 + 편의시설
        }
        
        # 평수 계산 (1평 = 3.3058㎡)
        total_pyeong = building_capacity.total_floor_area / 3.3058
        
        # 건축비 계산
        base_cost_per_pyeong = cost_per_pyeong.get(unit_type, 450)
        construction_cost = total_pyeong * base_cost_per_pyeong * 10000  # 원 단위
        
        # 부대비용 (건축비의 15%)
        additional_cost = construction_cost * 0.15
        
        # 총 사업비
        total_cost = construction_cost + additional_cost
        
        return {
            "construction_cost": int(construction_cost),
            "additional_cost": int(additional_cost),
            "total_cost": int(total_cost),
            "cost_per_unit": int(total_cost / building_capacity.units),
            "cost_per_pyeong": base_cost_per_pyeong
        }
    
    def calculate_lh_purchase_feasibility(
        self,
        land_price: float,
        building_capacity: BuildingCapacity,
        unit_type: str,
        land_area: float = 0
    ) -> Dict[str, Any]:
        """
        LH 매입 타당성 분석 (강화버전)
        
        Args:
            land_price: 토지 가격 (원)
            building_capacity: 건축 규모
            unit_type: 세대 유형
            land_area: 대지 면적 (㎡)
            
        Returns:
            상세 타당성 분석 결과
        """
        # 건축비 계산
        cost_info = self.calculate_construction_cost(building_capacity, unit_type)
        
        # 총 사업비 (토지비 + 건축비)
        total_project_cost = land_price + cost_info['total_cost']
        
        # 세대당 사업비
        cost_per_unit = total_project_cost / building_capacity.units if building_capacity.units > 0 else 0
        
        # LH 매입 기준가 (세대당 1억 5천만원 가정)
        lh_purchase_price_per_unit = 150_000_000
        
        # 매입 가능성 판단
        is_feasible = cost_per_unit <= lh_purchase_price_per_unit * 1.1  # 10% 여유
        
        # 수익률 계산
        expected_revenue = building_capacity.units * lh_purchase_price_per_unit
        profit = expected_revenue - total_project_cost
        profit_rate = (profit / total_project_cost) * 100 if total_project_cost > 0 else 0
        
        # 토지비 비중
        land_cost_ratio = (land_price / total_project_cost * 100) if total_project_cost > 0 else 0
        
        # 건축비 비중
        construction_cost_ratio = (cost_info['construction_cost'] / total_project_cost * 100) if total_project_cost > 0 else 0
        
        # 평균 세대 면적
        average_unit_area = (building_capacity.total_floor_area * 0.85) / building_capacity.units if building_capacity.units > 0 else 0
        
        # ROI (투자수익률)
        roi = (profit / total_project_cost * 100) if total_project_cost > 0 else 0
        
        # 세대당 토지비
        land_cost_per_unit = land_price / building_capacity.units if building_capacity.units > 0 else 0
        
        # 세대당 건축비
        construction_cost_per_unit = cost_info['construction_cost'] / building_capacity.units if building_capacity.units > 0 else 0
        
        return {
            # 기본 정보
            "total_project_cost": int(total_project_cost),
            "cost_per_unit": int(cost_per_unit),
            "lh_purchase_price_per_unit": lh_purchase_price_per_unit,
            
            # 수익성
            "expected_revenue": int(expected_revenue),
            "profit": int(profit),
            "profit_rate": round(profit_rate, 2),
            "roi": round(roi, 2),
            
            # 비용 구성
            "land_cost": int(land_price),
            "land_cost_ratio": round(land_cost_ratio, 2),
            "land_cost_per_unit": int(land_cost_per_unit),
            "construction_cost": cost_info['construction_cost'],
            "construction_cost_ratio": round(construction_cost_ratio, 2),
            "construction_cost_per_unit": int(construction_cost_per_unit),
            "additional_cost": cost_info['additional_cost'],
            
            # 평형 정보
            "average_unit_area": round(average_unit_area, 2),
            "cost_per_pyeong": cost_info['cost_per_pyeong'],
            
            # 판정
            "is_feasible": is_feasible,
            "feasibility_message": "매입 가능" if is_feasible else "사업비 초과",
            
            # 추가 지표
            "units": building_capacity.units,
            "floors": building_capacity.floors,
            "parking_spaces": building_capacity.parking_spaces,
            "land_area": land_area
        }
