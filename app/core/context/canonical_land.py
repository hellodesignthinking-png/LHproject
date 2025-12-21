"""
M1: Canonical Land Context
===========================

토지정보 모듈(M1) 출력 Context

이 Context는 순수한 FACT만 포함합니다:
- 주소, 좌표
- 면적, 지목
- 용도지역, FAR/BCR
- 도로 접면, 지형

⚠️ 포함되지 않는 것:
- land_value (M2로 이동)
- premium (M2로 이동)
- housing_type (M3로 이동)
- 세대수 (M4로 이동)

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple


@dataclass(frozen=True)
class CanonicalLandContext:
    """
    토지정보 Context (M1 출력)
    
    frozen=True: 생성 후 수정 불가 (IMMUTABLE)
    """
    
    # === 기본 정보 ===
    parcel_id: str                      # 필지 ID (PNU 코드)
    address: str                        # 지번 주소
    road_address: Optional[str]         # 도로명 주소
    
    # === 위치 정보 ===
    coordinates: Tuple[float, float]    # (위도, 경도)
    sido: str                           # 시도 (예: 서울특별시)
    sigungu: str                        # 시군구 (예: 강남구)
    dong: str                           # 읍면동 (예: 역삼동)
    
    # === 토지 속성 ===
    area_sqm: float                     # 대지면적 (㎡)
    area_pyeong: float                  # 대지면적 (평)
    land_category: str                  # 지목 (대, 전, 답, 임야 등)
    land_use: str                       # 토지이용 현황
    
    # === 용도지역 ===
    zone_type: str                      # 용도지역 (제2종일반주거지역 등)
    zone_detail: Optional[str]          # 용도지역 상세
    far: float                          # 법정 용적률 (%)
    bcr: float                          # 법정 건폐율 (%)
    
    # === 도로 및 지형 ===
    road_width: float                   # 접면 도로 폭 (m)
    road_type: str                      # 도로 유형 (대로/중로/소로/세로)
    terrain_height: str                 # 지형 높이 (고지/평지/저지)
    terrain_shape: str                  # 지형 형상 (정형/부정형)
    
    # === 규제 정보 ===
    regulations: Dict[str, Any]         # 토지이용규제 정보
    restrictions: list                  # 제약사항 목록
    
    # === 메타데이터 ===
    data_source: str                    # 데이터 출처
    retrieval_date: str                 # 조회 일시
    
    def __post_init__(self):
        """유효성 검증"""
        assert self.area_sqm > 0, "면적은 0보다 커야 합니다"
        assert 0 <= self.far <= 1000, "용적률은 0-1000% 범위여야 합니다"
        assert 0 <= self.bcr <= 100, "건폐율은 0-100% 범위여야 합니다"
        assert self.road_width >= 0, "도로 폭은 0 이상이어야 합니다"
    
    @property
    def is_residential_zone(self) -> bool:
        """주거지역 여부"""
        residential_keywords = ["주거", "residential"]
        return any(kw in self.zone_type.lower() for kw in residential_keywords)
    
    @property
    def is_commercial_zone(self) -> bool:
        """상업지역 여부"""
        commercial_keywords = ["상업", "commercial"]
        return any(kw in self.zone_type.lower() for kw in commercial_keywords)
    
    @property
    def location_summary(self) -> str:
        """위치 요약"""
        return f"{self.sido} {self.sigungu} {self.dong}"
    
    @property
    def zone_summary(self) -> str:
        """용도지역 요약"""
        return f"{self.zone_type} (용적률 {self.far}%, 건폐율 {self.bcr}%)"
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            "parcel_id": self.parcel_id,
            "address": self.address,
            "road_address": self.road_address,
            "coordinates": {
                "lat": self.coordinates[0],
                "lng": self.coordinates[1]
            },
            "location": {
                "sido": self.sido,
                "sigungu": self.sigungu,
                "dong": self.dong
            },
            "land": {
                "area_sqm": self.area_sqm,
                "area_pyeong": self.area_pyeong,
                "category": self.land_category,
                "use": self.land_use
            },
            "zoning": {
                "type": self.zone_type,
                "detail": self.zone_detail,
                "far": self.far,
                "bcr": self.bcr
            },
            "terrain": {
                "road_width": self.road_width,
                "road_type": self.road_type,
                "height": self.terrain_height,
                "shape": self.terrain_shape
            },
            "regulations": self.regulations,
            "restrictions": self.restrictions,
            "metadata": {
                "source": self.data_source,
                "date": self.retrieval_date
            }
        }
