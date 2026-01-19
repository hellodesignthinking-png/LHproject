"""
M1 Land Info Service
====================

토지정보 수집 서비스 (순수 FACT만)

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from typing import Optional
from datetime import datetime
import logging

from app.core.context.canonical_land import CanonicalLandContext

logger = logging.getLogger(__name__)


class LandInfoService:
    """
    토지정보 수집 서비스
    
    ⚠️ 이 서비스는 순수 FACT만 수집합니다:
    - land_value 계산 금지 (M2로 이동)
    - premium 계산 금지 (M2로 이동)
    - housing_type 결정 금지 (M3로 이동)
    """
    
    def __init__(self):
        logger.info("✅ M1 Land Info Service initialized")
    
    def run(
        self,
        parcel_id: str,
        address: Optional[str] = None
    ) -> CanonicalLandContext:
        """
        토지정보 수집 실행
        
        Args:
            parcel_id: 필지 ID (PNU 코드)
            address: 지번 주소 (선택)
        
        Returns:
            CanonicalLandContext (토지정보 FACT)
        """
        
        logger.info("="*80)
        logger.info("📋 M1 LAND INFO MODULE - Starting Data Collection")
        logger.info(f"   Parcel ID: {parcel_id}")
        logger.info("="*80)
        
        # 🔥 CRITICAL FIX: Load frozen context from storage
        # Pipeline needs actual user input, not mock data!
        try:
            from app.services.context_storage import context_storage
            from app.api.endpoints.m1_context_freeze_v2 import frozen_contexts_v2
            
            logger.info(f"🔍 Looking for frozen context with parcel_id: {parcel_id}")
            
            # Try to find context by parcel_id
            frozen_context = None
            
            # Search in-memory storage first
            for ctx_id, ctx in frozen_contexts_v2.items():
                if ctx.parcel_id == parcel_id:
                    frozen_context = ctx
                    logger.info(f"✅ Found frozen context in memory: {ctx_id}")
                    break
            
            if not frozen_context:
                # 🚨 ZeroSite Decision OS 헌법 3️⃣: Fail Fast
                # M1 데이터가 승인(FREEZE)되지 않았으면 후속 분석 불가
                logger.error(f"❌ CRITICAL: No frozen context found for parcel_id: {parcel_id}")
                logger.error("❌ M1 데이터가 승인되지 않았습니다")
                logger.error("❌ M2~M6 분석은 M1 승인 후에만 가능합니다")
                
                raise ValueError(
                    f"M1_DATA_NOT_FROZEN: "
                    f"M1 데이터가 승인되지 않았습니다. "
                    f"M1 검증 페이지에서 데이터를 확인하고 승인하세요. "
                    f"(parcel_id: {parcel_id})"
                )
            else:
                # Convert M1FinalContext to CanonicalLandContext
                land_info = frozen_context.land_info
                cadastral = land_info.cadastral
                zoning = land_info.zoning
                road_access = land_info.road_access
                terrain = land_info.terrain
                
                land_context = CanonicalLandContext(
                    parcel_id=frozen_context.parcel_id,
                    address=land_info.address.jibun_address,
                    road_address=land_info.address.road_address,
                    coordinates=(land_info.coordinates.lat, land_info.coordinates.lon),
                    sido=land_info.address.sido,
                    sigungu=land_info.address.sigungu,
                    dong=land_info.address.dong,
                    area_sqm=cadastral.area_sqm,
                    area_pyeong=cadastral.area_pyeong,
                    land_category=cadastral.jimok,
                    land_use=zoning.land_use,
                    zone_type=zoning.zone_type,
                    zone_detail=zoning.zone_detail,
                    far=frozen_context.building_constraints.legal.far_max,
                    bcr=frozen_context.building_constraints.legal.bcr_max,
                    road_width=road_access.road_width,
                    road_type=road_access.road_type,
                    terrain_height=terrain.height if terrain else "평지",
                    terrain_shape=terrain.shape if terrain else "정형",
                    regulations=frozen_context.building_constraints.regulations or {},
                    restrictions=frozen_context.building_constraints.restrictions or [],
                    data_source=f"Frozen Context (ID: {frozen_context.context_id[:8]}...)",
                    retrieval_date=frozen_context.frozen_at
                )
                
                logger.info("✅ CanonicalLandContext created from frozen context")
                logger.info(f"   Address: {land_context.address}")
                logger.info(f"   Area: {land_context.area_sqm}m² ({land_context.area_pyeong}평)")
                logger.info(f"   Zone: {land_context.zone_type}")
                logger.info("="*80)
                
                return land_context
                
        except Exception as e:
            # 🚨 ZeroSite Decision OS 헌법 3️⃣: Fail Fast
            logger.error(f"❌ CRITICAL: Failed to load frozen context: {e}")
            logger.error("❌ M1 데이터 로드 실패 - 시스템 분석 불가")
            
            raise ValueError(
                f"M1_DATA_LOAD_FAILED: "
                f"M1 데이터 로드 중 오류가 발생했습니다. "
                f"M1 검증 페이지에서 데이터를 다시 확인하고 승인하세요. "
                f"(parcel_id: {parcel_id}, error: {str(e)})"
            )
