"""
ZeroSite v9.1 Enhanced Normalization Layer

Normalization with Auto Input Integration:
- Automatic address → coordinate conversion (AddressResolver)
- Automatic zoning standards lookup (ZoningMapper)
- Automatic unit count estimation (UnitEstimator)
- User input priority maintained

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.1
"""

from typing import Dict, Any
from app.models_v9.standard_schema_v9_0 import SiteInfo

# v9.1 자동화 서비스
from app.services_v9.address_resolver_v9_0 import get_address_resolver
from app.services_v9.zoning_auto_mapper_v9_0 import get_zoning_mapper
from app.services_v9.unit_estimator_v9_0 import get_unit_estimator

# Import base normalization layer
from app.services_v9.normalization_layer_v9_0 import NormalizationLayerV90

import logging

logger = logging.getLogger(__name__)


class NormalizationLayerV91(NormalizationLayerV90):
    """
    v9.1 Enhanced Normalization Layer
    
    Extends v9.0 normalization with automatic input calculation:
    - Address → Coordinates (AddressResolver)
    - Zone Type → Building Standards (ZoningMapper)
    - Building Parameters → Unit Count (UnitEstimator)
    
    User input always takes priority over auto-calculated values.
    """
    
    def __init__(self):
        super().__init__()
        self.version = "v9.1"
        
        # v9.1 자동화 서비스 (lazy loading)
        self.address_resolver = None
        self.zoning_mapper = None
        self.unit_estimator = None
    
    async def normalize_site_info(self, raw_input: Dict[str, Any]) -> SiteInfo:
        """
        입력 데이터 → SiteInfo 변환 (v9.1 Enhanced)
        
        v9.1 Auto Features:
        1. 주소 미입력 시 자동 좌표 획득 (AddressResolver)
        2. 용도지역 선택 시 자동 건폐율/용적률 설정 (ZoningMapper)
        3. 사용자 입력 우선순위 유지
        
        Args:
            raw_input: 사용자 입력 데이터
                Required: address, land_area, zone_type
                Optional: latitude, longitude, building_coverage_ratio, floor_area_ratio
        
        Returns:
            SiteInfo: 정규화된 site 정보 (자동 계산 값 포함)
        """
        try:
            # 기본 입력값
            address = raw_input.get("address", "주소 없음")
            land_area = float(raw_input.get("land_area", 0))
            zone_type = raw_input.get("zone_type", "미지정")
            
            # 좌표 입력값 (optional)
            latitude = raw_input.get("latitude")
            longitude = raw_input.get("longitude")
            
            # 건축 기준 입력값 (optional)
            building_coverage_ratio = raw_input.get("building_coverage_ratio")
            floor_area_ratio = raw_input.get("floor_area_ratio")
            
            # ===== v9.1 AUTO: Address → Coordinates =====
            if (not latitude or not longitude) and address and address != "주소 없음":
                try:
                    logger.info(f"🔄 [v9.1 Auto] 주소 자동 변환 시작: {address}")
                    
                    # AddressResolver lazy loading
                    if not self.address_resolver:
                        self.address_resolver = get_address_resolver()
                    
                    # 주소 → 좌표 변환
                    address_info = await self.address_resolver.resolve_address(address)
                    
                    if address_info:
                        latitude = address_info.latitude
                        longitude = address_info.longitude
                        
                        # 도로명 주소로 업데이트 (있는 경우)
                        if address_info.road_address:
                            address = address_info.road_address
                        
                        logger.info(
                            f"✅ [v9.1 Auto] 좌표 자동 획득 성공\n"
                            f"   주소: {address}\n"
                            f"   좌표: ({latitude:.6f}, {longitude:.6f})"
                        )
                    else:
                        logger.warning(f"⚠️  [v9.1 Auto] 주소 변환 실패: {address}")
                
                except Exception as e:
                    logger.error(f"❌ [v9.1 Auto] 주소 변환 오류: {e}")
            
            # ===== v9.1 AUTO: Zone Type → Building Standards =====
            if (not building_coverage_ratio or not floor_area_ratio) and zone_type != "미지정":
                try:
                    logger.info(f"🔄 [v9.1 Auto] 용도지역 기준 자동 설정: {zone_type}")
                    
                    # ZoningMapper lazy loading
                    if not self.zoning_mapper:
                        self.zoning_mapper = get_zoning_mapper()
                    
                    # 용도지역 기준 조회
                    standards = self.zoning_mapper.get_zoning_standards(zone_type)
                    
                    if standards:
                        # 사용자 입력 우선, 없으면 법정 기준 적용
                        if not building_coverage_ratio:
                            building_coverage_ratio = standards.building_coverage_ratio
                            logger.info(f"✅ [v9.1 Auto] 건폐율 자동 설정: {building_coverage_ratio}%")
                        
                        if not floor_area_ratio:
                            floor_area_ratio = standards.floor_area_ratio
                            logger.info(f"✅ [v9.1 Auto] 용적률 자동 설정: {floor_area_ratio}%")
                    else:
                        logger.warning(f"⚠️  [v9.1 Auto] 용도지역 기준 조회 실패: {zone_type}")
                
                except Exception as e:
                    logger.error(f"❌ [v9.1 Auto] 용도지역 자동 설정 오류: {e}")
            
            # 기본값 처리
            if not building_coverage_ratio:
                building_coverage_ratio = 50.0
                logger.info(f"⚠️  건폐율 미입력 → 기본값: {building_coverage_ratio}%")
            
            if not floor_area_ratio:
                floor_area_ratio = 200.0
                logger.info(f"⚠️  용적률 미입력 → 기본값: {floor_area_ratio}%")
            
            # land_appraisal_price 기본값 처리
            land_appraisal_price_raw = raw_input.get("land_appraisal_price")
            if land_appraisal_price_raw is None or float(land_appraisal_price_raw) == 0:
                # 서울 평균 평당가 기준
                land_appraisal_price = 9_000_000.0
                logger.info(f"⚠️  감정평가액 미입력 → 기본값 적용: {land_appraisal_price:,.0f}원/m²")
            else:
                land_appraisal_price = float(land_appraisal_price_raw)
            
            return SiteInfo(
                address=address,
                land_area=land_area,
                zone_type=zone_type,
                land_appraisal_price=land_appraisal_price,
                total_land_price=land_area * land_appraisal_price,
                latitude=latitude,
                longitude=longitude,
                building_coverage_ratio=float(building_coverage_ratio),
                floor_area_ratio=float(floor_area_ratio),
                height_limit=raw_input.get("height_limit")
            )
        
        except Exception as e:
            logger.error(f"[v9.1] Site info normalization error: {e}")
            # 기본값 반환
            return SiteInfo(
                address="주소 오류",
                land_area=100.0,
                zone_type="미지정",
                land_appraisal_price=1000000,
                total_land_price=100000000,
                building_coverage_ratio=50.0,
                floor_area_ratio=200.0
            )
    
    async def auto_estimate_unit_count(
        self,
        land_area: float,
        floor_area_ratio: float,
        building_coverage_ratio: float,
        zone_type: str,
        user_input_unit_count: int = None
    ) -> int:
        """
        v9.1 세대수 자동 산정
        
        사용자가 unit_count를 입력하지 않은 경우 자동 계산
        
        Args:
            land_area: 대지 면적 (m²)
            floor_area_ratio: 용적률 (%)
            building_coverage_ratio: 건폐율 (%)
            zone_type: 용도지역
            user_input_unit_count: 사용자 입력 세대수 (우선순위)
        
        Returns:
            int: 세대수 (사용자 입력 또는 자동 계산)
        """
        # 사용자 입력 우선
        if user_input_unit_count and user_input_unit_count > 0:
            logger.info(f"✅ [v9.1] 사용자 입력 세대수 사용: {user_input_unit_count}세대")
            return user_input_unit_count
        
        try:
            logger.info(f"🔄 [v9.1 Auto] 세대수 자동 산정 시작")
            
            # UnitEstimator lazy loading
            if not self.unit_estimator:
                self.unit_estimator = get_unit_estimator()
            
            # Zoning Mapper를 통해 주차 비율 조회
            if not self.zoning_mapper:
                self.zoning_mapper = get_zoning_mapper()
            
            standards = self.zoning_mapper.get_zoning_standards(zone_type)
            parking_ratio = standards.parking_ratio if standards else 1.0
            
            # 세대수 자동 산정
            estimate = self.unit_estimator.estimate_units(
                land_area=land_area,
                floor_area_ratio=floor_area_ratio,
                building_coverage_ratio=building_coverage_ratio,
                parking_ratio=parking_ratio
            )
            
            logger.info(
                f"✅ [v9.1 Auto] 세대수 자동 산정 완료\n"
                f"   총 세대수: {estimate.total_units}세대\n"
                f"   층수: {estimate.floors}층\n"
                f"   주차 대수: {estimate.parking_spaces}대"
            )
            
            return estimate.total_units
        
        except Exception as e:
            logger.error(f"❌ [v9.1 Auto] 세대수 자동 산정 오류: {e}")
            # 기본값: 대지면적 기반 간단한 추정
            default_estimate = int((land_area * floor_area_ratio / 100) * 0.85 / 60)
            logger.warning(f"⚠️  세대수 기본값 적용: {default_estimate}세대")
            return default_estimate


def get_normalization_layer_v91() -> NormalizationLayerV91:
    """
    Get v9.1 Enhanced Normalization Layer instance
    
    Returns:
        NormalizationLayerV91: v9.1 normalization layer with auto input
    """
    return NormalizationLayerV91()
