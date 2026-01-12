"""
M1 상태 머신 (State Machine)
==============================

ZeroSite Decision OS M1 모듈 상태 관리

상태 흐름:
EMPTY → AUTO_FETCHED → EDITABLE → READY_TO_FREEZE → FROZEN

Author: ZeroSite Decision OS
Date: 2026-01-12
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class M1Status(str, Enum):
    """M1 모듈 상태"""
    EMPTY = "EMPTY"                     # 프로젝트 생성 직후
    AUTO_FETCHED = "AUTO_FETCHED"       # API로 일부 데이터 수집
    EDITABLE = "EDITABLE"               # Mock + 수기 수정 가능
    READY_TO_FREEZE = "READY_TO_FREEZE" # 필수값 충족
    FROZEN = "FROZEN"                   # result_data 확정, 수정 불가


class DataSource(str, Enum):
    """데이터 출처"""
    KAKAO_API = "kakao"
    VWORLD_API = "vworld"
    MOIS_API = "mois"
    MOCK = "mock"
    USER_EDIT = "user_edit"
    MOCK_EDIT = "mock+edit"


class M1AutoData(BaseModel):
    """자동 수집 데이터 (Stage 1)"""
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    admin_area: Optional[Dict[str, str]] = None  # {si, gu, dong}
    poi_summary: Optional[Dict[str, int]] = None  # {subway, school, public_facility}
    
    class Config:
        json_schema_extra = {
            "example": {
                "address": "서울특별시 강남구 테헤란로 518",
                "lat": 37.5079,
                "lng": 127.0623,
                "admin_area": {
                    "si": "서울특별시",
                    "gu": "강남구",
                    "dong": "대치동"
                },
                "poi_summary": {
                    "subway": 2,
                    "school": 1,
                    "public_facility": 3
                }
            }
        }


class M1MockData(BaseModel):
    """Mock 데이터 (Stage 2 초기값)"""
    area_sqm: float = Field(default=0, description="대지면적 (㎡)")
    zone_type: str = Field(default="", description="용도지역")
    bcr: float = Field(default=0, description="건폐율 (%)")
    far: float = Field(default=0, description="용적률 (%)")
    official_land_price: float = Field(default=0, description="공시지가 (원/㎡)")
    road_condition: str = Field(default="", description="도로 조건")
    transaction_cases: List[Dict[str, Any]] = Field(default_factory=list, description="거래사례 (최대 10건)")
    regulation_summary: Dict[str, Any] = Field(default_factory=dict, description="규제 요약")
    
    class Config:
        json_schema_extra = {
            "example": {
                "area_sqm": 1200,
                "zone_type": "상업지역",
                "bcr": 60,
                "far": 800,
                "official_land_price": 18000000,
                "road_condition": "8m 접도",
                "transaction_cases": [],
                "regulation_summary": {}
            }
        }


class M1EditableData(BaseModel):
    """수정 가능한 데이터 (Stage 2) - LH 실무 기준 확장"""
    # 자동 수집 데이터 (수정 가능)
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    
    # 기본 토지 정보
    land_area: Optional[float] = Field(None, gt=0, description="대지면적 (㎡)")
    zoning: Optional[str] = Field(None, description="용도지역")
    bcr: Optional[float] = Field(None, ge=0, le=100, description="건폐율 (%)")
    far: Optional[float] = Field(None, ge=0, description="용적률 (%)")
    official_land_price: Optional[float] = Field(None, gt=0, description="공시지가 (원/㎡)")
    
    # 🔴 [A] 도로 조건 (LH 필수)
    road_access_type: Optional[str] = Field(None, description="단일접면 | 코너 | 막다른도로")
    road_width_m: Optional[float] = Field(None, gt=0, description="도로 폭 (m)")
    road_count: Optional[int] = Field(None, ge=1, description="접면 도로 수")
    fire_truck_access: Optional[bool] = Field(None, description="소방차 진입 가능 여부")
    road_legal_status: Optional[str] = Field(None, description="도로 | 사도 | 미지정")
    
    # 🔴 [B] 대지 형상
    site_shape_type: Optional[str] = Field(None, description="정형 | 장방형 | 부정형 | 자루형")
    frontage_m: Optional[float] = Field(None, gt=0, description="전면 길이 (m)")
    depth_m: Optional[float] = Field(None, gt=0, description="깊이 (m)")
    effective_build_ratio: Optional[float] = Field(None, ge=0, le=100, description="실효 건축 가능 비율 (%)")
    
    # 🔴 [C] 방향 / 일조
    main_direction: Optional[str] = Field(None, description="남 | 남동 | 남서 | 동 | 서 | 북")
    sunlight_risk: Optional[str] = Field(None, description="낮음 | 보통 | 높음")
    adjacent_height_risk: Optional[str] = Field(None, description="낮음 | 보통 | 높음")
    
    # 🔴 [D] 시세 정보
    nearby_transaction_price_py: Optional[float] = Field(None, gt=0, description="최근 거래가 (평당, 원)")
    public_land_price_py: Optional[float] = Field(None, gt=0, description="공시지가 (평당, 원)")
    price_gap_ratio: Optional[float] = Field(None, gt=0, description="거래가/공시지가 배율")
    
    # 🔴 [E] 기존 건물
    existing_building_exists: Optional[bool] = Field(None, description="기존 건물 존재 여부")
    existing_building_structure: Optional[str] = Field(None, description="RC | SRC | 조적 | 철골")
    existing_building_floors: Optional[int] = Field(None, ge=1, description="층수")
    existing_building_area_m2: Optional[float] = Field(None, gt=0, description="연면적 (㎡)")
    demolition_required: Optional[bool] = Field(None, description="철거 필요 여부")
    
    # 기존 필드 유지
    transaction_price: Optional[float] = Field(None, description="거래 사례가 (원/㎡)")
    regulation_summary: Optional[str] = Field(None, description="규제 요약")
    lh_compatibility: Optional[str] = Field(None, description="LH 사업 적합성")


class M1ResultData(BaseModel):
    """
    M1 최종 확정 데이터 (FROZEN) - LH 실무 기준
    
    🔥 Single Source of Truth for M2~M7
    """
    # 필수 필드: 기본 정보
    address: str
    lat: float
    lng: float
    land_area: float = Field(..., gt=0, description="대지면적 (㎡)")
    zoning: str = Field(..., min_length=1, description="용도지역")
    bcr: float = Field(..., ge=0, le=100, description="건폐율 (%)")
    far: float = Field(..., ge=0, description="용적률 (%)")
    official_land_price: float = Field(..., gt=0, description="공시지가 (원/㎡)")
    
    # 필수 필드: 도로 조건 (LH 필수)
    road_access_type: str = Field(..., description="단일접면 | 코너 | 막다른도로")
    road_width_m: float = Field(..., gt=0, description="도로 폭 (m)")
    road_count: int = Field(..., ge=1, description="접면 도로 수")
    fire_truck_access: bool = Field(..., description="소방차 진입 가능 여부")
    road_legal_status: str = Field(..., description="도로 | 사도 | 미지정")
    
    # 필수 필드: 대지 형상
    site_shape_type: str = Field(..., description="정형 | 장방형 | 부정형 | 자루형")
    frontage_m: float = Field(..., gt=0, description="전면 길이 (m)")
    depth_m: float = Field(..., gt=0, description="깊이 (m)")
    effective_build_ratio: float = Field(..., ge=0, le=100, description="실효 건축 가능 비율 (%)")
    
    # 필수 필드: 방향
    main_direction: str = Field(..., description="남 | 남동 | 남서 | 동 | 서 | 북")
    
    # 선택 필드: 일조 리스크
    sunlight_risk: Optional[str] = Field(None, description="낮음 | 보통 | 높음")
    adjacent_height_risk: Optional[str] = Field(None, description="낮음 | 보통 | 높음")
    
    # 선택 필드: 시세 (최소 1개 필수)
    nearby_transaction_price_py: Optional[float] = Field(None, gt=0, description="최근 거래가 (평당)")
    public_land_price_py: Optional[float] = Field(None, gt=0, description="공시지가 (평당)")
    price_gap_ratio: Optional[float] = Field(None, gt=0, description="거래가/공시지가 배율")
    
    # 선택 필드: 기존 건물
    existing_building_exists: bool = Field(default=False, description="기존 건물 존재 여부")
    existing_building_structure: Optional[str] = None
    existing_building_floors: Optional[int] = None
    existing_building_area_m2: Optional[float] = None
    demolition_required: Optional[bool] = None
    
    # 선택 필드: 기타
    transaction_price: Optional[float] = None
    regulation_summary: Optional[str] = None
    lh_compatibility: Optional[str] = None
    
    # 메타데이터
    sources: Dict[str, str] = Field(default_factory=dict)  # {field: DataSource}
    frozen_at: datetime
    frozen_by: str = Field(default="human")
    context_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "address": "서울특별시 강남구 테헤란로 518",
                "lat": 37.5079,
                "lng": 127.0623,
                "area_sqm": 1350,
                "zone_type": "상업지역",
                "bcr": 60,
                "far": 800,
                "road_condition": "8m 접도",
                "official_land_price": 19500000,
                "official_price_date": "2024-01-01",
                "transaction_cases": [],
                "regulation_summary": {},
                "sources": {
                    "address": "kakao",
                    "area_sqm": "user_edit",
                    "official_land_price": "mock+edit"
                },
                "frozen_at": "2026-01-12T10:00:00",
                "frozen_by": "human",
                "context_id": "ctx-20260112-0001"
            }
        }


class M1ValidationResult(BaseModel):
    """M1 Freeze 가능 여부 검증 결과"""
    can_freeze: bool
    missing_fields: List[str] = Field(default_factory=list)
    invalid_fields: Dict[str, str] = Field(default_factory=dict)  # {field: reason}
    
    class Config:
        json_schema_extra = {
            "example": {
                "can_freeze": False,
                "missing_fields": ["area_sqm", "official_land_price"],
                "invalid_fields": {
                    "bcr": "건폐율은 0~100% 사이여야 합니다"
                }
            }
        }


class M1StateContext(BaseModel):
    """M1 전체 상태 컨텍스트"""
    project_id: str
    status: M1Status = M1Status.EMPTY
    
    # 각 단계별 데이터
    auto_data: Optional[M1AutoData] = None
    mock_data: Optional[M1MockData] = None
    editable_data: Optional[M1EditableData] = None
    result_data: Optional[M1ResultData] = None
    
    # 메타
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # 상태 전이 이력
    state_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    def transition_to(self, new_status: M1Status, reason: str = ""):
        """
        상태 전이 (State Transition)
        
        Args:
            new_status: 새로운 상태
            reason: 전이 이유
        """
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        
        # 이력 기록
        self.state_history.append({
            "from": old_status.value,
            "to": new_status.value,
            "at": self.updated_at.isoformat(),
            "reason": reason
        })
    
    def can_edit(self) -> bool:
        """편집 가능 여부"""
        return self.status in [M1Status.EDITABLE, M1Status.READY_TO_FREEZE]
    
    def is_frozen(self) -> bool:
        """Freeze 여부"""
        return self.status == M1Status.FROZEN
    
    def validate_for_freeze(self) -> M1ValidationResult:
        """
        FREEZE 가능 여부 검증 - LH 실무 기준
        
        필수 조건:
        1. 기본 토지 정보 (5개)
        2. 도로 조건 (5개 - 100% 필수)
        3. 대지 형상 (4개 - 100% 필수)
        4. 방향 (1개 최소 - main_direction)
        5. 시세 (1개 이상 필수)
        """
        missing = []
        invalid = {}
        
        if not self.editable_data:
            return M1ValidationResult(
                can_freeze=False,
                missing_fields=["모든 필수 데이터가 누락되었습니다"]
            )
        
        data = self.editable_data
        
        # ===== 1. 기본 토지 정보 (5개 필수) =====
        if not data.land_area or data.land_area <= 0:
            missing.append("대지면적")
        
        if not data.zoning:
            missing.append("용도지역")
        
        if data.bcr is None:
            missing.append("건폐율")
        elif data.bcr < 0 or data.bcr > 100:
            invalid["건폐율"] = "0~100% 사이여야 합니다"
        
        if data.far is None:
            missing.append("용적률")
        elif data.far < 0:
            invalid["용적률"] = "0 이상이어야 합니다"
        
        if not data.official_land_price or data.official_land_price <= 0:
            missing.append("공시지가")
        
        # ===== 2. 도로 조건 (5개 필수) =====
        if not data.road_access_type:
            missing.append("도로 접면 유형")
        
        if not data.road_width_m or data.road_width_m <= 0:
            missing.append("도로 폭")
        elif data.road_width_m < 6:
            invalid["도로 폭"] = "⚠️ 6m 미만 시 사업 리스크 높음"
        
        if not data.road_count or data.road_count < 1:
            missing.append("접면 도로 수")
        
        if data.fire_truck_access is None:
            missing.append("소방차 진입 가능 여부")
        
        if not data.road_legal_status:
            missing.append("도로 법적 지위")
        
        # ===== 3. 대지 형상 (4개 필수) =====
        if not data.site_shape_type:
            missing.append("대지 형상 유형")
        
        if not data.frontage_m or data.frontage_m <= 0:
            missing.append("전면 길이")
        
        if not data.depth_m or data.depth_m <= 0:
            missing.append("대지 깊이")
        
        if data.effective_build_ratio is None:
            missing.append("실효 건축 가능 비율")
        elif data.effective_build_ratio < 0 or data.effective_build_ratio > 100:
            invalid["실효 건축 가능 비율"] = "0~100% 사이여야 합니다"
        
        # ===== 4. 방향 (최소 main_direction 필수) =====
        if not data.main_direction:
            missing.append("주 방향")
        
        # ===== 5. 시세 (최소 1개 필수) =====
        has_market_data = (
            (data.nearby_transaction_price_py and data.nearby_transaction_price_py > 0) or
            (data.public_land_price_py and data.public_land_price_py > 0) or
            (data.price_gap_ratio and data.price_gap_ratio > 0)
        )
        
        if not has_market_data:
            missing.append("시세 정보 (거래가/공시지가/배율 중 최소 1개)")
        
        # ===== 검증 완료 =====
        can_freeze = len(missing) == 0 and len(invalid) == 0
        
        return M1ValidationResult(
            can_freeze=can_freeze,
            missing_fields=missing,
            invalid_fields=invalid
        )


# 전역 상태 저장소 (In-memory, Redis로 대체 가능)
m1_state_storage: Dict[str, M1StateContext] = {}


def get_m1_state(project_id: str) -> Optional[M1StateContext]:
    """M1 상태 조회"""
    return m1_state_storage.get(project_id)


def save_m1_state(context: M1StateContext) -> None:
    """M1 상태 저장"""
    m1_state_storage[context.project_id] = context


def create_m1_state(project_id: str) -> M1StateContext:
    """M1 상태 생성"""
    context = M1StateContext(project_id=project_id)
    save_m1_state(context)
    return context
