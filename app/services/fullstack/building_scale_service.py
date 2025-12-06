"""
ZeroSite Full Stack MVP - Stage 2: Building Scale Service
=========================================================
건축 규모 검토 및 계산

기능:
- 건축면적, 연면적 계산
- 층수 추정
- 건축 가능 여부 판단
"""

from typing import Dict, Any
import logging
import math

logger = logging.getLogger(__name__)


class BuildingScaleService:
    """
    건축 규모 검토 서비스
    
    ZeroSite 핵심: 토지 정보로부터 최적 건축 규모 계산
    """
    
    def calculate_building_scale(
        self,
        land_area: float,
        building_coverage_ratio: float,
        floor_area_ratio: float,
        max_floors: int
    ) -> Dict[str, Any]:
        """
        건축 규모 계산
        
        Args:
            land_area: 대지면적 (㎡)
            building_coverage_ratio: 건폐율 (%)
            floor_area_ratio: 용적률 (%)
            max_floors: 최대 층수
            
        Returns:
            {
                "total_gfa": 총 연면적,
                "floor_gfa": 층당 면적,
                "building_area": 건축면적,
                "floors": 계산된 층수,
                "actual_floors": 실제 층수 (정수),
                "buildable": bool,
                "warnings": [...]
            }
        """
        logger.info(f"🏗️  Stage 2: Building Scale Review")
        logger.info(f"   대지면적: {land_area}㎡")
        logger.info(f"   건폐율: {building_coverage_ratio}%")
        logger.info(f"   용적률: {floor_area_ratio}%")
        
        result = {
            "total_gfa": 0,
            "floor_gfa": 0,
            "building_area": 0,
            "floors": 0,
            "actual_floors": 0,
            "buildable": False,
            "warnings": []
        }
        
        # 1. 건축면적 계산 (대지면적 × 건폐율)
        building_area = land_area * (building_coverage_ratio / 100)
        result["building_area"] = round(building_area, 2)
        
        # 2. 총 연면적 계산 (대지면적 × 용적률)
        total_gfa = land_area * (floor_area_ratio / 100)
        result["total_gfa"] = round(total_gfa, 2)
        
        # 3. 층당 면적
        result["floor_gfa"] = result["building_area"]
        
        # 4. 층수 계산
        if building_area > 0:
            calculated_floors = total_gfa / building_area
            result["floors"] = round(calculated_floors, 2)
            result["actual_floors"] = max(1, int(calculated_floors))
        else:
            result["floors"] = 0
            result["actual_floors"] = 0
            result["warnings"].append({
                "type": "건축면적_부족",
                "message": "건폐율이 너무 낮아 건축이 어렵습니다"
            })
        
        # 5. 최대 층수 제한 체크
        if result["actual_floors"] > max_floors:
            result["warnings"].append({
                "type": "층수_초과",
                "message": f"계산된 층수({result['actual_floors']})가 최대 층수({max_floors})를 초과합니다"
            })
            # 최대 층수로 조정
            result["actual_floors"] = max_floors
            result["total_gfa"] = round(building_area * max_floors, 2)
        
        # 6. 최소 대지면적 체크 (200㎡)
        MIN_LAND_AREA = 200
        if land_area < MIN_LAND_AREA:
            result["warnings"].append({
                "type": "대지면적_부족",
                "message": f"대지면적이 최소 기준({MIN_LAND_AREA}㎡)보다 작습니다"
            })
        
        # 7. 건축 가능 여부 판단
        result["buildable"] = (
            land_area >= MIN_LAND_AREA and
            total_gfa > 0 and
            building_area > 0
        )
        
        # 8. 추가 검토사항
        self._add_scale_recommendations(result, land_area)
        
        logger.info(f"   ✅ 연면적: {result['total_gfa']}㎡")
        logger.info(f"   ✅ 건축면적: {result['building_area']}㎡")
        logger.info(f"   ✅ 층수: {result['actual_floors']}층")
        logger.info(f"   ✅ 건축 가능: {result['buildable']}")
        
        return result
    
    def _add_scale_recommendations(
        self,
        result: Dict[str, Any],
        land_area: float
    ):
        """
        규모 관련 권장사항 추가
        """
        # 대규모 건축물 (3000㎡ 이상)
        if result["total_gfa"] >= 3000:
            result["warnings"].append({
                "type": "대규모_건축물",
                "message": "대규모 건축물로 관련 법규 추가 검토 필요",
                "severity": "INFO"
            })
        
        # 소규모 토지 (500㎡ 미만)
        if land_area < 500:
            result["warnings"].append({
                "type": "소규모_토지",
                "message": "소규모 토지로 사업성 면밀 검토 필요",
                "severity": "WARNING"
            })
        
        # 고층 건물 (10층 이상)
        if result["actual_floors"] >= 10:
            result["warnings"].append({
                "type": "고층_건물",
                "message": "고층 건물로 구조·소방 추가 규정 적용",
                "severity": "INFO"
            })
    
    def calculate_parking_requirement(
        self,
        unit_count: int,
        zone_type: str
    ) -> Dict[str, Any]:
        """
        주차 대수 계산
        
        Args:
            unit_count: 세대수
            zone_type: 용도지역
            
        Returns:
            {
                "required_parking": 필요 주차대수,
                "parking_ratio": 세대당 주차비율,
                "standard": 기준 설명
            }
        """
        # 용도지역별 주차 비율
        if "주거지역" in zone_type:
            ratio = 1.0  # 세대당 1대
            standard = "주거지역 기준 (세대당 1대)"
        elif "상업지역" in zone_type:
            ratio = 0.7  # 세대당 0.7대
            standard = "상업지역 기준 (세대당 0.7대)"
        else:
            ratio = 0.8  # 기본
            standard = "일반 기준 (세대당 0.8대)"
        
        required = math.ceil(unit_count * ratio)
        
        return {
            "required_parking": required,
            "parking_ratio": ratio,
            "standard": standard
        }


def create_building_scale_service():
    """
    Factory function for BuildingScaleService
    """
    return BuildingScaleService()
