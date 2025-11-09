"""
API 요청/응답 스키마 정의
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UnitType(str, Enum):
    """세대 유형"""
    YOUTH = "청년형"
    NEWLYWED = "신혼부부형"
    ELDERLY = "고령자형"


class LandAnalysisRequest(BaseModel):
    """토지 분석 요청"""
    address: str = Field(..., description="토지 주소", example="서울특별시 강남구 역삼동 123-45")
    land_area: float = Field(..., description="토지 면적(㎡)", example=500.0, gt=0)
    unit_type: UnitType = Field(default=UnitType.YOUTH, description="세대 유형")
    
    class Config:
        json_schema_extra = {
            "example": {
                "address": "서울특별시 강남구 역삼동 123-45",
                "land_area": 500.0,
                "unit_type": "청년형"
            }
        }


class Coordinates(BaseModel):
    """좌표 정보"""
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")


class ZoneInfo(BaseModel):
    """용도지역 정보"""
    zone_type: str = Field(..., description="용도지역")
    building_coverage_ratio: float = Field(..., description="건폐율(%)")
    floor_area_ratio: float = Field(..., description="용적률(%)")
    height_limit: Optional[float] = Field(None, description="높이제한(m)")


class BuildingCapacity(BaseModel):
    """건축 규모"""
    building_area: float = Field(..., description="건축면적(㎡)")
    total_floor_area: float = Field(..., description="연면적(㎡)")
    floors: int = Field(..., description="층수")
    units: int = Field(..., description="세대수")
    parking_spaces: int = Field(..., description="주차대수")


class RiskFactor(BaseModel):
    """리스크 요인"""
    category: str = Field(..., description="리스크 카테고리")
    description: str = Field(..., description="리스크 상세 설명")
    severity: str = Field(..., description="심각도 (low/medium/high/critical)")


class DemographicInfo(BaseModel):
    """인구통계 정보"""
    total_population: int = Field(..., description="총 인구")
    youth_population: int = Field(..., description="청년 인구 (20-39세)")
    youth_ratio: float = Field(..., description="청년 인구 비율(%)")
    single_households: int = Field(..., description="1인 가구 수")
    single_household_ratio: float = Field(..., description="1인 가구 비율(%)")


class NearbyFacility(BaseModel):
    """주변 시설 정보"""
    name: str = Field(..., description="시설명")
    category: str = Field(..., description="시설 카테고리")
    distance: float = Field(..., description="거리(m)")
    address: str = Field(..., description="주소")


class DemandAnalysis(BaseModel):
    """수요 분석 결과"""
    demand_score: float = Field(..., description="수요 점수 (0-100)", ge=0, le=100)
    key_factors: List[str] = Field(..., description="핵심 수요 요인")
    recommendation: str = Field(..., description="적합성 판단")
    nearby_facilities: List[NearbyFacility] = Field(default=[], description="주변 시설")


class AnalysisSummary(BaseModel):
    """분석 요약"""
    is_eligible: bool = Field(..., description="LH 매입 적격 여부")
    estimated_units: int = Field(..., description="예상 세대수")
    demand_score: float = Field(..., description="수요 점수")
    recommendation: str = Field(..., description="종합 판단")
    risk_count: int = Field(default=0, description="리스크 요인 개수")


class LandAnalysisResponse(BaseModel):
    """토지 분석 응답"""
    status: str = Field(..., description="처리 상태")
    analysis_id: str = Field(..., description="분석 ID")
    
    # 입력 정보
    address: str
    land_area: float
    unit_type: str
    
    # 분석 결과
    coordinates: Optional[Coordinates] = None
    zone_info: Optional[ZoneInfo] = None
    building_capacity: Optional[BuildingCapacity] = None
    risk_factors: List[RiskFactor] = Field(default=[])
    demographic_info: Optional[DemographicInfo] = None
    demand_analysis: Optional[DemandAnalysis] = None
    
    # 종합 결과
    summary: AnalysisSummary
    report_text: Optional[str] = Field(None, description="AI 생성 보고서 텍스트")
    pdf_url: Optional[str] = Field(None, description="PDF 다운로드 URL")
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "analysis_id": "abc123",
                "address": "서울특별시 강남구 역삼동 123-45",
                "land_area": 500.0,
                "unit_type": "청년형",
                "summary": {
                    "is_eligible": True,
                    "estimated_units": 15,
                    "demand_score": 85.0,
                    "recommendation": "적합",
                    "risk_count": 0
                },
                "pdf_url": "/api/reports/abc123.pdf",
                "created_at": "2024-01-15T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """에러 응답"""
    status: str = "error"
    error_code: str
    message: str
    details: Optional[dict] = None
