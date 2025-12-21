"""
M1 Final Context (분석용 불변 컨텍스트)
======================================

M1 → M2-M6 파이프라인 간 데이터 계약

Author: ZeroSite Development Team
Date: 2025-12-17
Version: 2.0
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator


# ============================================================================
# 1. Land Info (토지 기본 정보)
# ============================================================================

class AddressInfo(BaseModel):
    """주소 정보 (STEP 1, 2)"""
    road_address: str
    jibun_address: str
    sido: str
    sigungu: str
    dong: str
    beopjeong_dong: Optional[str] = None
    source: Literal["API", "MANUAL"]


class CoordinatesInfo(BaseModel):
    """좌표 정보 (STEP 2)"""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    source: Literal["API", "MANUAL"]
    verified: bool = False  # 사용자 확인 여부


class CadastralInfo(BaseModel):
    """지적 정보 (STEP 3)"""
    bonbun: str
    bubun: str
    jimok: str  # 대지, 전, 답, 임야 등
    area_sqm: float = Field(..., gt=0)
    area_pyeong: float = Field(..., gt=0)  # 자동 계산: sqm / 3.3058
    source: Literal["API", "PDF", "MANUAL"]
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)  # PDF일 경우
    
    @validator('area_pyeong', always=True)
    def calculate_area_pyeong(cls, v, values):
        if 'area_sqm' in values:
            return round(values['area_sqm'] / 3.3058, 2)
        return v


class ZoningInfo(BaseModel):
    """용도지역·지구 (STEP 4)"""
    zone_type: str  # 제1종, 제2종, 제3종 일반주거지역 등
    zone_detail: Optional[str] = None
    land_use: str  # 주거용, 상업용 등
    source: Literal["API", "MANUAL"]


class RoadInfo(BaseModel):
    """도로 정보 (STEP 5)"""
    name: str
    width: float
    distance: float


class RoadAccessInfo(BaseModel):
    """도로 접근 정보 (STEP 5)"""
    road_contact: str  # 접도, 각지, 맹지 등
    road_width: float = Field(..., gt=0)
    road_type: str  # 대로, 중로, 소로 등
    nearby_roads: List[RoadInfo] = Field(default_factory=list)
    source: Literal["API", "MANUAL"]


class TerrainInfo(BaseModel):
    """지형 정보"""
    height: Optional[str] = None  # 평지, 구릉지 등
    shape: Optional[str] = None  # 정형지, 부정형지 등
    source: Literal["MANUAL"] = "MANUAL"


class LandInfo(BaseModel):
    """토지 기본 정보 (M2, M3, M4, M5, M6 공통)"""
    address: AddressInfo
    coordinates: CoordinatesInfo
    cadastral: CadastralInfo
    zoning: ZoningInfo
    road_access: RoadAccessInfo
    terrain: Optional[TerrainInfo] = None


# ============================================================================
# 2. Appraisal Inputs (감정평가 입력)
# ============================================================================

class OfficialPriceInfo(BaseModel):
    """공시지가 (STEP 6)"""
    amount: Optional[float] = Field(None, gt=0)  # 원/㎡
    date: Optional[str] = None  # YYYYMMDD
    source: Literal["API", "MANUAL"]


class TransactionCase(BaseModel):
    """거래사례"""
    date: str  # YYYYMMDD
    area: float = Field(..., gt=0)  # ㎡
    amount: int = Field(..., gt=0)  # 거래금액 (원)
    distance: float = Field(..., ge=0)  # 대상지로부터 거리 (m)
    address: str
    use_in_calculation: bool = True  # M2에서 사용 여부


class PremiumFactors(BaseModel):
    """프리미엄 요소 (M2 보정용)"""
    corner_lot: bool = False  # 각지
    wide_road: bool = False  # 광로 접면
    subway_proximity: Optional[float] = None  # 지하철역 거리 (m)
    school_district: Optional[str] = None  # 학군 정보
    development_plan: Optional[str] = None  # 개발 계획


class AppraisalInputs(BaseModel):
    """감정평가 입력 (M2 전용)"""
    official_price: Optional[OfficialPriceInfo] = None
    transaction_cases_for_appraisal: List[TransactionCase] = Field(
        default_factory=list, max_items=5
    )
    premium_factors: Optional[PremiumFactors] = None


# ============================================================================
# 3. Demand Inputs (수요 분석 입력)
# ============================================================================

class RegionCharacteristics(BaseModel):
    """지역 특성"""
    population_density: Optional[str] = None  # 고밀도, 중밀도, 저밀도
    age_distribution: Optional[str] = None  # 청장년층 집중, 고령화 등
    income_level: Optional[str] = None  # 고소득, 중소득, 저소득
    source: Literal["API", "MANUAL"]


class Competition(BaseModel):
    """경쟁 물건 현황"""
    nearby_lh_count: Optional[int] = Field(None, ge=0)  # 반경 1km 내
    nearby_apartments: Optional[int] = Field(None, ge=0)  # 반경 500m 내
    source: Literal["MANUAL"] = "MANUAL"


class DemandInputs(BaseModel):
    """수요 분석 입력 (M3 전용)"""
    region_characteristics: Optional[RegionCharacteristics] = None
    preferred_lh_types: List[str] = Field(default_factory=list)
    competition: Optional[Competition] = None


# ============================================================================
# 4. Building Constraints (건축 제약)
# ============================================================================

class LegalConstraints(BaseModel):
    """법정 제약 (STEP 4)"""
    far_max: float = Field(..., gt=0, le=1000)  # 용적률 상한 (%)
    bcr_max: float = Field(..., gt=0, le=100)  # 건폐율 상한 (%)
    height_limit: Optional[float] = Field(None, gt=0)  # 최고 높이 (m)
    source: Literal["API", "MANUAL"]


class LHIncentive(BaseModel):
    """LH 인센티브"""
    available: bool = False
    far_bonus: Optional[float] = None  # % 추가
    reason: Optional[str] = None


class BuildingConstraints(BaseModel):
    """건축 제약 (M4 전용)"""
    legal: LegalConstraints
    lh_incentive: Optional[LHIncentive] = None
    regulations: List[str] = Field(default_factory=list)
    restrictions: List[str] = Field(default_factory=list)


# ============================================================================
# 5. Financial Inputs (재무 입력)
# ============================================================================

class ConstructionCostModel(BaseModel):
    """건축비 모델"""
    unit_cost_per_sqm: Optional[float] = Field(None, gt=0)  # ㎡당 건축비
    method: Literal["STANDARD", "CUSTOM"] = "STANDARD"
    source: Literal["AUTO", "MANUAL"] = "AUTO"


class Linkage(BaseModel):
    """연계 대출"""
    available: bool = False
    loan_amount: Optional[float] = Field(None, gt=0)  # 대출 가능 금액
    interest_rate: Optional[float] = Field(None, gt=0, le=100)  # 금리 (%)


class FinancialInputs(BaseModel):
    """재무 입력 (M5 전용)"""
    construction_cost_model: Optional[ConstructionCostModel] = None
    linkage: Optional[Linkage] = None


# ============================================================================
# 6. Metadata
# ============================================================================

class DataSources(BaseModel):
    """데이터 소스 분포"""
    api_count: int = 0
    pdf_count: int = 0
    manual_count: int = 0


class ConfidenceScore(BaseModel):
    """신뢰도 점수"""
    overall: float = Field(..., ge=0.0, le=1.0)
    cadastral: Optional[float] = Field(None, ge=0.0, le=1.0)
    market_data: Optional[float] = Field(None, ge=0.0, le=1.0)


class Metadata(BaseModel):
    """메타데이터"""
    data_sources: DataSources
    confidence_score: Optional[ConfidenceScore] = None
    created_by: str
    created_at: str  # ISO 8601
    frozen_at: str  # ISO 8601
    version: str = "2.0"


# ============================================================================
# M1 Final Context (Main)
# ============================================================================

class M1FinalContext(BaseModel):
    """
    M1 Final Context (분석용 불변 컨텍스트)
    
    - STEP 8에서 "분석 시작" 버튼 클릭 시 생성
    - frozen=true 상태로 Redis에 저장
    - M2-M6 파이프라인은 이 Context만 사용
    """
    
    context_id: str  # UUID
    parcel_id: str  # 토지 고유 식별자
    frozen_at: str  # ISO 8601
    frozen: bool = True
    
    # 6개 카테고리
    land_info: LandInfo
    appraisal_inputs: Optional[AppraisalInputs] = None
    demand_inputs: Optional[DemandInputs] = None
    building_constraints: BuildingConstraints
    financial_inputs: Optional[FinancialInputs] = None
    metadata: Metadata
    
    @validator('frozen_at', always=True)
    def set_frozen_at(cls, v):
        if not v:
            return datetime.now().isoformat()
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Dict 변환"""
        return self.dict(exclude_none=False)
    
    def validate_minimal_requirements(self) -> tuple[bool, List[str]]:
        """
        최소 필수 필드 검증 (Level 1)
        
        Returns:
            (is_valid, missing_fields)
        """
        missing = []
        
        # Land Info 검증
        if not self.land_info.address.road_address:
            missing.append("land_info.address.road_address")
        if not self.land_info.coordinates.lat or not self.land_info.coordinates.lon:
            missing.append("land_info.coordinates")
        if not self.land_info.cadastral.area_sqm:
            missing.append("land_info.cadastral.area_sqm")
        if not self.land_info.zoning.zone_type:
            missing.append("land_info.zoning.zone_type")
        
        # Building Constraints 검증
        if not self.building_constraints.legal.far_max:
            missing.append("building_constraints.legal.far_max")
        if not self.building_constraints.legal.bcr_max:
            missing.append("building_constraints.legal.bcr_max")
        
        return (len(missing) == 0, missing)
    
    def calculate_confidence_score(self) -> float:
        """
        전체 신뢰도 점수 계산
        
        Returns:
            overall confidence (0.0 - 1.0)
        """
        scores = []
        
        # API 소스: 1.0
        # PDF 소스: confidence 값 사용
        # MANUAL 소스: 0.8
        
        if self.land_info.cadastral.source == "API":
            scores.append(1.0)
        elif self.land_info.cadastral.source == "PDF":
            scores.append(self.land_info.cadastral.confidence or 0.7)
        else:
            scores.append(0.8)
        
        if self.appraisal_inputs and self.appraisal_inputs.official_price:
            if self.appraisal_inputs.official_price.source == "API":
                scores.append(1.0)
            else:
                scores.append(0.8)
        
        return sum(scores) / len(scores) if scores else 0.8


# ============================================================================
# Helper Functions
# ============================================================================

def create_parcel_id(sido: str, sigungu: str, dong: str, bonbun: str, bubun: str) -> str:
    """
    Parcel ID 생성
    
    Format: {sido_code}{sigungu_code}{dong_code}{bonbun}{bubun}
    Example: 1168010100100010001
    """
    # TODO: 실제 행정구역 코드 매핑 로직 구현
    return f"1168010100{bonbun.zfill(4)}{bubun.zfill(4)}"


def calculate_data_source_distribution(context: M1FinalContext) -> DataSources:
    """데이터 소스 분포 계산"""
    api_count = 0
    pdf_count = 0
    manual_count = 0
    
    # Land Info
    if context.land_info.address.source == "API":
        api_count += 1
    else:
        manual_count += 1
    
    if context.land_info.coordinates.source == "API":
        api_count += 1
    else:
        manual_count += 1
    
    if context.land_info.cadastral.source == "API":
        api_count += 1
    elif context.land_info.cadastral.source == "PDF":
        pdf_count += 1
    else:
        manual_count += 1
    
    if context.land_info.zoning.source == "API":
        api_count += 1
    else:
        manual_count += 1
    
    if context.land_info.road_access.source == "API":
        api_count += 1
    else:
        manual_count += 1
    
    # Appraisal Inputs
    if context.appraisal_inputs and context.appraisal_inputs.official_price:
        if context.appraisal_inputs.official_price.source == "API":
            api_count += 1
        else:
            manual_count += 1
    
    return DataSources(
        api_count=api_count,
        pdf_count=pdf_count,
        manual_count=manual_count
    )
