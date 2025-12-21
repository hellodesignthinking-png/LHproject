"""
M1 Context Freeze V2 API
=========================

Freeze M1 STEP data into immutable M1FinalContext for M2-M6 pipeline.

Key Features:
- 6-category data reorganization (land_info, appraisal_inputs, etc.)
- Transaction case separation (appraisal vs reference)
- frozen=true immutability guarantee
- Redis + in-memory dual storage

Author: ZeroSite M1 Development Team
Date: 2025-12-17
Version: 2.0
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.context.m1_final_context import (
    M1FinalContext,
    LandInfo, AddressInfo, CoordinatesInfo, CadastralInfo, ZoningInfo,
    RoadAccessInfo, TerrainInfo, RoadInfo,
    AppraisalInputs, OfficialPriceInfo, TransactionCase, PremiumFactors,
    DemandInputs, RegionCharacteristics, Competition,
    BuildingConstraints, LegalConstraints, LHIncentive,
    FinancialInputs, ConstructionCostModel, Linkage,
    Metadata, DataSources, ConfidenceScore,
    calculate_data_source_distribution, create_parcel_id
)
from app.services.context_storage import context_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/m1", tags=["M1 Context Freeze V2"])

# In-memory storage (fallback)
frozen_contexts_v2: Dict[str, M1FinalContext] = {}


# ============================================================================
# Request Models
# ============================================================================

class FreezeContextRequestV2(BaseModel):
    """
    M1 Context Freeze Request V2
    
    Collects all STEP 1-8 data and reorganizes into 6 categories
    """
    
    # STEP 1-2: Address & Coordinates
    address: str
    road_address: str
    sido: str
    sigungu: str
    dong: str
    beopjeong_dong: Optional[str] = None
    coordinates: Dict[str, float]  # {lat, lon}
    coordinates_verified: bool = False
    address_source: str = "API"  # API or MANUAL
    coordinates_source: str = "API"
    
    # STEP 3: Cadastral
    bonbun: str
    bubun: str
    jimok: str
    area: float
    cadastral_source: str = "API"  # API, PDF, MANUAL
    cadastral_confidence: Optional[float] = None  # PDF only
    
    # STEP 4: Zoning & Legal
    zone_type: str
    zone_detail: Optional[str] = None
    land_use: str
    far: float
    bcr: float
    height_limit: Optional[float] = None
    regulations: List[str] = Field(default_factory=list)
    restrictions: List[str] = Field(default_factory=list)
    zoning_source: str = "API"
    
    # STEP 5: Road Access
    road_contact: str = "접도"
    road_width: float
    road_type: str
    nearby_roads: List[Dict[str, Any]] = Field(default_factory=list)
    road_source: str = "API"
    
    # STEP 6: Market Data
    official_land_price: Optional[float] = None
    official_land_price_date: Optional[str] = None
    official_price_source: str = "API"
    
    # Transaction cases (분리)
    transaction_cases_appraisal: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="감정평가 계산용 거래사례 (최대 5건)"
    )
    transaction_cases_reference: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="보고서 참고용 거래사례 (무제한)"
    )
    
    # Premium factors
    corner_lot: bool = False
    wide_road: bool = False
    subway_proximity: Optional[float] = None
    school_district: Optional[str] = None
    development_plan: Optional[str] = None
    
    # Optional: Demand inputs (M3)
    population_density: Optional[str] = None
    age_distribution: Optional[str] = None
    income_level: Optional[str] = None
    preferred_lh_types: List[str] = Field(default_factory=list)
    
    # Optional: Financial inputs (M5)
    construction_unit_cost: Optional[float] = None
    linkage_available: bool = False
    linkage_loan_amount: Optional[float] = None
    linkage_interest_rate: Optional[float] = None
    
    # Metadata
    created_by: str = "m1_user"
    data_sources: Optional[Dict[str, Any]] = None


class FreezeContextResponseV2(BaseModel):
    """M1 Context Freeze Response V2"""
    context_id: str
    parcel_id: str
    frozen: bool = True
    frozen_at: str
    confidence_score: float
    missing_fields: List[str] = Field(default_factory=list)
    message: str


# ============================================================================
# STEP 8: Freeze Context V2 (분석 시작)
# ============================================================================

@router.options("/freeze-context-v2")
async def freeze_context_v2_options():
    """Handle CORS preflight for freeze-context-v2 endpoint"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )

@router.post("/freeze-context-v2", response_model=FreezeContextResponseV2)
async def freeze_context_v2(request: FreezeContextRequestV2):
    """
    🔒 M1 Context Freeze V2 - 분석용 불변 컨텍스트 생성
    
    **Phase:**
    - STEP 8에서 "분석 시작 (M1 Lock)" 버튼 클릭 시 호출
    
    **Features:**
    1. 6개 카테고리로 데이터 재정렬
    2. 거래사례 분리 (appraisal vs reference)
    3. frozen=true 불변성 보장
    4. Redis + in-memory 이중 저장
    5. ✅ 입력값 검증 (0 값, 빈 문자열 거부)
    
    **Returns:**
    - context_id: 분석 세션 UUID
    - parcel_id: 토지 고유 ID
    - confidence_score: 데이터 신뢰도 (0.0-1.0)
    - missing_fields: 누락된 권장 필드 목록
    """
    try:
        logger.info("🔒 M1 Context Freeze V2 initiated")
        
        # ✅ VALIDATION: 필수 필드 검증
        validation_errors = []
        
        # 1. 주소
        if not request.address or not request.road_address:
            validation_errors.append("주소 (address, road_address) 필수")
        
        # 2. 좌표
        if not request.coordinates or request.coordinates.get("lat") == 0 or request.coordinates.get("lon") == 0:
            validation_errors.append("좌표 (lat, lon) 필수")
        
        # 3. 지번
        if not request.bonbun or request.bonbun.strip() == "":
            validation_errors.append("본번 (bonbun) 필수")
        
        # 4. 면적 (> 0)
        if request.area <= 0:
            validation_errors.append("면적 (area)은 0보다 커야 합니다")
        
        # 5. 지목 (비어있지 않음)
        if not request.jimok or request.jimok.strip() == "":
            validation_errors.append("지목 (jimok) 필수")
        
        # 6. 용도지역 (비어있지 않음)
        if not request.zone_type or request.zone_type.strip() == "":
            validation_errors.append("용도지역 (zone_type) 필수")
        
        # 7. 토지이용 (비어있지 않음)
        if not request.land_use or request.land_use.strip() == "":
            validation_errors.append("토지이용 (land_use) 필수")
        
        # 8. FAR (> 0)
        if request.far <= 0:
            validation_errors.append("용적률 (far)은 0보다 커야 합니다")
        
        # 9. BCR (> 0)
        if request.bcr <= 0:
            validation_errors.append("건폐율 (bcr)은 0보다 커야 합니다")
        
        # 10. 도로 폭 (> 0)
        if request.road_width <= 0:
            validation_errors.append("도로 폭 (road_width)은 0보다 커야 합니다")
        
        # 11. 도로 유형 (비어있지 않음)
        if not request.road_type or request.road_type.strip() == "":
            validation_errors.append("도로 유형 (road_type) 필수")
        
        # ❌ 검증 실패 시 에러 반환
        if validation_errors:
            logger.error(f"❌ Validation failed: {validation_errors}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "필수 입력값이 누락되었거나 유효하지 않습니다",
                    "validation_errors": validation_errors
                }
            )
        
        # Generate IDs
        context_id = str(uuid.uuid4())
        parcel_id = create_parcel_id(
            request.sido,
            request.sigungu,
            request.dong,
            request.bonbun,
            request.bubun
        )
        
        # 1. Build Land Info
        land_info = LandInfo(
            address=AddressInfo(
                road_address=request.road_address,
                jibun_address=request.address,
                sido=request.sido,
                sigungu=request.sigungu,
                dong=request.dong,
                beopjeong_dong=request.beopjeong_dong,
                source=request.address_source
            ),
            coordinates=CoordinatesInfo(
                lat=request.coordinates["lat"],
                lon=request.coordinates["lon"],
                source=request.coordinates_source,
                verified=request.coordinates_verified
            ),
            cadastral=CadastralInfo(
                bonbun=request.bonbun,
                bubun=request.bubun,
                jimok=request.jimok,
                area_sqm=request.area,
                area_pyeong=request.area / 3.3058,
                source=request.cadastral_source,
                confidence=request.cadastral_confidence
            ),
            zoning=ZoningInfo(
                zone_type=request.zone_type,
                zone_detail=request.zone_detail,
                land_use=request.land_use,
                source=request.zoning_source
            ),
            road_access=RoadAccessInfo(
                road_contact=request.road_contact,
                road_width=request.road_width,
                road_type=request.road_type,
                nearby_roads=[
                    RoadInfo(**r) for r in request.nearby_roads
                ] if request.nearby_roads else [],
                source=request.road_source
            ),
            terrain=TerrainInfo(
                height="평지",  # Default
                shape="정형",  # Default
                source="MANUAL"
            )
        )
        
        # 2. Build Appraisal Inputs
        appraisal_inputs = None
        if request.official_land_price or request.transaction_cases_appraisal:
            appraisal_inputs = AppraisalInputs(
                official_price=OfficialPriceInfo(
                    amount=request.official_land_price,
                    date=request.official_land_price_date,
                    source=request.official_price_source
                ) if request.official_land_price else None,
                transaction_cases_for_appraisal=[
                    TransactionCase(**tc) for tc in request.transaction_cases_appraisal[:5]
                ],
                premium_factors=PremiumFactors(
                    corner_lot=request.corner_lot,
                    wide_road=request.wide_road,
                    subway_proximity=request.subway_proximity,
                    school_district=request.school_district,
                    development_plan=request.development_plan
                )
            )
        
        # 3. Build Demand Inputs (optional)
        demand_inputs = None
        if request.population_density or request.preferred_lh_types:
            demand_inputs = DemandInputs(
                region_characteristics=RegionCharacteristics(
                    population_density=request.population_density,
                    age_distribution=request.age_distribution,
                    income_level=request.income_level,
                    source="MANUAL"
                ) if request.population_density else None,
                preferred_lh_types=request.preferred_lh_types
            )
        
        # 4. Build Building Constraints
        building_constraints = BuildingConstraints(
            legal=LegalConstraints(
                far_max=request.far,
                bcr_max=request.bcr,
                height_limit=request.height_limit,
                source=request.zoning_source
            ),
            lh_incentive=LHIncentive(
                available=False,  # M4에서 자동 판정
                far_bonus=None,
                reason=None
            ),
            regulations=request.regulations,
            restrictions=request.restrictions
        )
        
        # 5. Build Financial Inputs (optional)
        financial_inputs = None
        if request.construction_unit_cost or request.linkage_available:
            financial_inputs = FinancialInputs(
                construction_cost_model=ConstructionCostModel(
                    unit_cost_per_sqm=request.construction_unit_cost,
                    method="CUSTOM" if request.construction_unit_cost else "STANDARD",
                    source="MANUAL" if request.construction_unit_cost else "AUTO"
                ) if request.construction_unit_cost else None,
                linkage=Linkage(
                    available=request.linkage_available,
                    loan_amount=request.linkage_loan_amount,
                    interest_rate=request.linkage_interest_rate
                ) if request.linkage_available else None
            )
        
        # 6. Create M1 Final Context
        frozen_at = datetime.now().isoformat()
        
        final_context = M1FinalContext(
            context_id=context_id,
            parcel_id=parcel_id,
            frozen_at=frozen_at,
            frozen=True,
            land_info=land_info,
            appraisal_inputs=appraisal_inputs,
            demand_inputs=demand_inputs,
            building_constraints=building_constraints,
            financial_inputs=financial_inputs,
            metadata=Metadata(
                data_sources=DataSources(api_count=0, pdf_count=0, manual_count=0),
                created_by=request.created_by,
                created_at=frozen_at,
                frozen_at=frozen_at,
                version="2.0"
            )
        )
        
        # Calculate data source distribution
        final_context.metadata.data_sources = calculate_data_source_distribution(final_context)
        
        # Calculate confidence score
        confidence_score = final_context.calculate_confidence_score()
        
        # Validate minimal requirements
        is_valid, missing_fields = final_context.validate_minimal_requirements()
        
        if not is_valid:
            logger.warning(f"⚠️ Context created but missing required fields: {missing_fields}")
        
        # Store in Redis (primary) + in-memory (fallback)
        try:
            context_storage.store_frozen_context(
                context_id,
                final_context.to_dict(),
                ttl_hours=24
            )
        except Exception as redis_error:
            logger.error(f"⚠️ Redis storage failed: {redis_error}")
        
        frozen_contexts_v2[context_id] = final_context
        
        logger.info(f"✅ M1 Final Context created - ID: {context_id}, Confidence: {confidence_score:.2f}")
        
        return FreezeContextResponseV2(
            context_id=context_id,
            parcel_id=parcel_id,
            frozen=True,
            frozen_at=frozen_at,
            confidence_score=confidence_score,
            missing_fields=missing_fields if not is_valid else [],
            message=f"분석용 컨텍스트가 확정되었습니다. (신뢰도: {confidence_score:.0%})"
        )
        
    except Exception as e:
        logger.error(f"❌ Context freeze V2 failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Context freeze failed: {str(e)}"
        )


# ============================================================================
# Get Frozen Context V2
# ============================================================================

@router.get("/context-v2/{context_id}")
async def get_frozen_context_v2(context_id: str):
    """
    📖 Get M1 Final Context (Read-Only)
    
    **Usage:**
    - M2, M3, M4, M5, M6가 분석 입력값으로 사용
    - frozen=true 불변 보장
    
    **Returns:**
    - M1FinalContext (6-category structure)
    """
    try:
        logger.info(f"📖 Retrieving M1 Final Context - ID: {context_id}")
        
        # Try Redis first
        try:
            context_dict = context_storage.get_frozen_context(context_id)
            if context_dict:
                return JSONResponse(content={
                    "context_id": context_id,
                    "final_context": context_dict,
                    "frozen": True,
                    "source": "redis",
                    "message": "M1 Final Context retrieved (read-only)"
                })
        except Exception as redis_error:
            logger.warning(f"⚠️ Redis retrieval failed: {redis_error}")
        
        # Fallback to in-memory
        if context_id not in frozen_contexts_v2:
            raise HTTPException(
                status_code=404,
                detail=f"Context not found: {context_id}"
            )
        
        final_context = frozen_contexts_v2[context_id]
        
        return JSONResponse(content={
            "context_id": context_id,
            "final_context": final_context.to_dict(),
            "frozen": True,
            "source": "memory",
            "message": "M1 Final Context retrieved (read-only)"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Context retrieval V2 failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Context retrieval failed: {str(e)}"
        )


# ============================================================================
# Health Check
# ============================================================================

@router.get("/context-v2/health")
async def context_v2_health():
    """Health check for M1 Context V2 API"""
    return JSONResponse(content={
        "status": "healthy",
        "module": "M1 Context Freeze V2",
        "version": "2.0",
        "frozen_contexts_count": len(frozen_contexts_v2)
    })
