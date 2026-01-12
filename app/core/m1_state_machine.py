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
    """수정 가능한 데이터 (Stage 2)"""
    # 자동 수집 데이터 (수정 가능)
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    
    # Mock + 수정 데이터
    area_sqm: Optional[float] = Field(None, gt=0)
    zone_type: Optional[str] = None
    bcr: Optional[float] = Field(None, ge=0, le=100)
    far: Optional[float] = Field(None, ge=0)
    road_condition: Optional[str] = None
    official_land_price: Optional[float] = Field(None, gt=0)
    official_price_date: Optional[str] = None
    
    # 거래사례
    transaction_cases: Optional[List[Dict[str, Any]]] = None
    
    # 규제
    regulation_summary: Optional[Dict[str, Any]] = None


class M1ResultData(BaseModel):
    """
    M1 최종 확정 데이터 (FROZEN)
    
    🔥 Single Source of Truth for M2~M7
    """
    # 필수 필드
    address: str
    lat: float
    lng: float
    area_sqm: float = Field(..., gt=0)
    zone_type: str = Field(..., min_length=1)
    bcr: float = Field(..., ge=0, le=100)
    far: float = Field(..., ge=0)
    road_condition: str
    official_land_price: float = Field(..., gt=0)
    
    # 선택 필드
    official_price_date: Optional[str] = None
    transaction_cases: List[Dict[str, Any]] = Field(default_factory=list)
    regulation_summary: Dict[str, Any] = Field(default_factory=dict)
    
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
        """Freeze 가능 여부 검증"""
        missing = []
        invalid = {}
        
        if not self.editable_data:
            return M1ValidationResult(
                can_freeze=False,
                missing_fields=["모든 필수 데이터"]
            )
        
        data = self.editable_data
        
        # 필수 필드 검증
        if not data.area_sqm or data.area_sqm <= 0:
            missing.append("area_sqm")
        
        if not data.zone_type:
            missing.append("zone_type")
        
        if data.bcr is None:
            missing.append("bcr")
        elif data.bcr < 0 or data.bcr > 100:
            invalid["bcr"] = "건폐율은 0~100% 사이여야 합니다"
        
        if data.far is None:
            missing.append("far")
        elif data.far < 0:
            invalid["far"] = "용적률은 0 이상이어야 합니다"
        
        if not data.official_land_price or data.official_land_price <= 0:
            missing.append("official_land_price")
        
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
