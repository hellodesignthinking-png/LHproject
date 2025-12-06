"""
ZeroSite Full Stack MVP - Stage 1: Land Review Service
======================================================
토지 조회 및 기본 정보 수집

기능:
- 주소 → 좌표 변환 (Kakao API)
- 용도지역 조회 (NSDI API)
- 건폐율, 용적률 매핑
- 기본 법규 확인
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# 용도지역별 기본 건축기준
ZONE_STANDARDS = {
    "제1종일반주거지역": {
        "building_coverage_ratio": 60.0,
        "floor_area_ratio": 150.0,
        "max_floors": 4,
        "max_height": 15.0
    },
    "제2종일반주거지역": {
        "building_coverage_ratio": 60.0,
        "floor_area_ratio": 200.0,
        "max_floors": 7,
        "max_height": 21.0
    },
    "제3종일반주거지역": {
        "building_coverage_ratio": 50.0,
        "floor_area_ratio": 250.0,
        "max_floors": 15,
        "max_height": 45.0
    },
    "준주거지역": {
        "building_coverage_ratio": 70.0,
        "floor_area_ratio": 400.0,
        "max_floors": 20,
        "max_height": 60.0
    },
    "중심상업지역": {
        "building_coverage_ratio": 90.0,
        "floor_area_ratio": 1500.0,
        "max_floors": 50,
        "max_height": 150.0
    },
    "일반상업지역": {
        "building_coverage_ratio": 80.0,
        "floor_area_ratio": 800.0,
        "max_floors": 30,
        "max_height": 90.0
    },
    "근린상업지역": {
        "building_coverage_ratio": 70.0,
        "floor_area_ratio": 500.0,
        "max_floors": 15,
        "max_height": 45.0
    }
}


class LandReviewService:
    """
    토지 조회 서비스
    
    Landywork의 토지 정보 조회 경험을 ZeroSite에 통합
    """
    
    def __init__(self, kakao_service, land_regulation_service):
        self.kakao_service = kakao_service
        self.land_regulation_service = land_regulation_service
    
    async def review_land(
        self,
        address: str,
        zone_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        토지 기본 정보 조회 및 검토
        
        Args:
            address: 주소 또는 지번
            zone_type: 사용자가 지정한 용도지역 (optional)
            
        Returns:
            {
                "address": str,
                "coordinates": {"lat": float, "lon": float},
                "zone_type": str,
                "building_coverage_ratio": float,
                "floor_area_ratio": float,
                "max_floors": int,
                "max_height": float,
                "planning_area": bool,
                "legal_restrictions": [...],
                "review_status": "OK" | "WARNING" | "ERROR"
            }
        """
        logger.info(f"🔍 Stage 1: Land Review - {address}")
        
        result = {
            "address": address,
            "coordinates": None,
            "zone_type": None,
            "building_coverage_ratio": 0,
            "floor_area_ratio": 0,
            "max_floors": 0,
            "max_height": 0,
            "planning_area": False,
            "legal_restrictions": [],
            "review_status": "OK"
        }
        
        # Step 1: 주소 → 좌표 변환
        try:
            coord = await self.kakao_service.address_to_coordinates(address)
            result["coordinates"] = {
                "lat": coord['latitude'],
                "lon": coord['longitude']
            }
            logger.info(f"   ✅ 좌표 변환 성공: {coord['latitude']}, {coord['longitude']}")
        except Exception as e:
            logger.warning(f"   ⚠️  좌표 변환 실패: {str(e)}")
            # 기본값 사용
            result["coordinates"] = {"lat": 37.5665, "lon": 126.9780}
            result["review_status"] = "WARNING"
        
        # Step 2: 용도지역 조회 (API)
        api_zone_type = None
        if result["coordinates"]:
            try:
                zone_info = await self.land_regulation_service.get_land_use_zone(
                    latitude=result["coordinates"]["lat"],
                    longitude=result["coordinates"]["lon"]
                )
                api_zone_type = zone_info.get('landUseZone')
                logger.info(f"   ✅ 용도지역 조회 성공: {api_zone_type}")
            except Exception as e:
                logger.warning(f"   ⚠️  용도지역 조회 실패: {str(e)}")
        
        # Step 3: 용도지역 결정 (사용자 입력 우선)
        final_zone_type = zone_type or api_zone_type
        
        if not final_zone_type:
            logger.warning("   ⚠️  용도지역 정보 없음 - 기본값 사용")
            final_zone_type = "제2종일반주거지역"
            result["review_status"] = "WARNING"
        
        result["zone_type"] = final_zone_type
        
        # Step 4: 건축기준 매핑
        standards = ZONE_STANDARDS.get(
            final_zone_type,
            ZONE_STANDARDS["제2종일반주거지역"]  # 기본값
        )
        
        result["building_coverage_ratio"] = standards["building_coverage_ratio"]
        result["floor_area_ratio"] = standards["floor_area_ratio"]
        result["max_floors"] = standards["max_floors"]
        result["max_height"] = standards["max_height"]
        
        # Step 5: 기본 법규 검토
        restrictions = self._check_legal_restrictions(
            final_zone_type,
            standards
        )
        result["legal_restrictions"] = restrictions
        
        # Step 6: 지구단위계획 여부 (간단 판단)
        result["planning_area"] = self._check_planning_area(final_zone_type)
        
        logger.info(f"   ✅ Stage 1 완료: {result['review_status']}")
        
        return result
    
    def _check_legal_restrictions(
        self,
        zone_type: str,
        standards: Dict[str, float]
    ) -> list:
        """
        기본 법규 제한사항 체크
        """
        restrictions = []
        
        # 주거지역 특수 규정
        if "주거지역" in zone_type:
            restrictions.append({
                "type": "높이제한",
                "description": f"최대 {standards['max_height']}m",
                "severity": "INFO"
            })
            restrictions.append({
                "type": "용도제한",
                "description": "주거용 외 용도 제한",
                "severity": "INFO"
            })
        
        # 상업지역
        if "상업지역" in zone_type:
            restrictions.append({
                "type": "용도혼합",
                "description": "상업+주거 복합 가능",
                "severity": "INFO"
            })
        
        # 일조권 (주거지역만)
        if "주거지역" in zone_type:
            restrictions.append({
                "type": "일조권",
                "description": "인접 대지 일조권 확보 필요",
                "severity": "WARNING"
            })
        
        return restrictions
    
    def _check_planning_area(self, zone_type: str) -> bool:
        """
        지구단위계획 구역 여부 간단 판단
        (실제로는 API로 확인 필요, MVP에서는 패턴 기반)
        """
        # 준주거, 상업지역은 지구단위계획 가능성 높음
        if any(x in zone_type for x in ["준주거", "상업"]):
            return True
        
        return False


def create_land_review_service(kakao_service, land_regulation_service):
    """
    Factory function for LandReviewService
    """
    return LandReviewService(kakao_service, land_regulation_service)
