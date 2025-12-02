"""
API 요청/응답 스키마 정의
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UnitType(str, Enum):
    """세대 유형 (LH 공식 6개 유형)"""
    YOUTH = "청년"
    NEWLYWED_1 = "신혼·신생아 I"
    NEWLYWED_2 = "신혼·신생아 II"
    MULTI_CHILD = "다자녀"
    ELDERLY = "고령자"
    GENERAL = "일반"
    SECURE_JEONSE = "든든전세"


class ConsultantInfo(BaseModel):
    """컨설팅 담당자 정보"""
    name: Optional[str] = Field(None, description="담당자 이름", example="홍길동")
    phone: Optional[str] = Field(None, description="담당자 연락처", example="010-1234-5678")
    department: Optional[str] = Field(None, description="담당자 부서", example="토지개발팀")
    email: Optional[str] = Field(None, description="담당자 이메일", example="hong@example.com")


class CategoryWeights(BaseModel):
    """카테고리별 가중치 설정"""
    location: float = Field(30, description="입지 가중치 (%)", ge=0, le=100)
    scale: float = Field(25, description="규모 가중치 (%)", ge=0, le=100)
    business: float = Field(30, description="사업성 가중치 (%)", ge=0, le=100)
    regulation: float = Field(15, description="법규 가중치 (%)", ge=0, le=100)
    
    def validate_total(self):
        """가중치 합계가 100인지 검증"""
        total = self.location + self.scale + self.business + self.regulation
        if abs(total - 100) > 0.01:  # 부동소수점 오차 허용
            raise ValueError(f"가중치 합계는 100이어야 합니다 (현재: {total})")
        return True


class LandAnalysisRequest(BaseModel):
    """토지 분석 요청"""
    address: str = Field(..., description="토지 주소", example="서울특별시 강남구 역삼동 123-45")
    land_area: float = Field(..., description="토지 면적(㎡)", example=500.0, gt=0)
    unit_type: Optional[UnitType] = Field(None, description="세대 유형 (선택사항, None이면 전체 분석)")
    zone_type: Optional[str] = Field(None, description="용도지역 (사용자 선택)")
    land_status: Optional[str] = Field("나대지", description="종전 대지 이용상태")
    land_appraisal_price: Optional[float] = Field(None, description="토지 탁상감정평가액 (원/㎡)", gt=0)
    consultant: Optional[ConsultantInfo] = Field(None, description="컨설팅 담당자 정보")
    weights: Optional[CategoryWeights] = Field(None, description="카테고리별 가중치 (선택사항, 기본값 사용)")
    lh_version: str = Field("2024", description="LH 기준 버전 (2024/2025/2026)")
    report_mode: str = Field("v7_5_final", description="보고서 모드 ('v7_5_final': 60-page LH public standard, 'v7_3_legacy': 25-40 pages, 'v7_2_extended': 25-40 pages, 'v7_2_basic': 8-10 pages)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "address": "서울특별시 강남구 역삼동 123-45",
                "land_area": 500.0,
                "unit_type": "청년",
                "zone_type": "제2종일반주거지역",
                "land_status": "나대지",
                "land_appraisal_price": 5500000,
                "lh_version": "2024",
                "consultant": {
                    "name": "홍길동",
                    "phone": "010-1234-5678",
                    "department": "토지개발팀",
                    "email": "hong@example.com"
                }
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
    elderly_ratio: float = Field(15.0, description="고령 인구 비율(%) (65세 이상)")


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


class CheckItemSchema(BaseModel):
    """체크리스트 항목"""
    category: str = Field(..., description="카테고리")
    item: str = Field(..., description="항목명")
    status: str = Field(..., description="상태 (통과/부적합/주의/참고)")
    value: str = Field(..., description="실제 값")
    standard: str = Field(..., description="기준 값")
    description: str = Field(..., description="상세 설명")
    score: float = Field(..., description="점수 (0-100)")


class GradeInfo(BaseModel):
    """등급 정보"""
    grade: str = Field(..., description="등급 (A/B/C)")
    total_score: float = Field(..., description="총점 (0-100)")
    category_scores: Dict[str, float] = Field(..., description="카테고리별 점수")
    summary: str = Field(..., description="종합 의견")
    recommendations: List[str] = Field(default=[], description="개선 권장사항")


class AnalysisSummary(BaseModel):
    """분석 요약"""
    is_eligible: bool = Field(..., description="LH 매입 적격 여부")
    estimated_units: int = Field(..., description="예상 세대수")
    demand_score: float = Field(..., description="수요 점수")
    recommendation: str = Field(..., description="종합 판단")
    risk_count: int = Field(default=0, description="리스크 요인 개수")
    grade: Optional[str] = Field(None, description="사업 등급 (A/B/C)")
    total_score: Optional[float] = Field(None, description="종합 점수 (0-100)")


class UnitTypeScore(BaseModel):
    """유형별 점수 정보"""
    unit_type: str = Field(..., description="세대 유형")
    score: float = Field(..., description="수요 점수 (0-100)", ge=0, le=100)
    size: str = Field(..., description="평형 정보")


class LandAnalysisResponse(BaseModel):
    """토지 분석 응답"""
    status: str = Field(..., description="처리 상태")
    analysis_id: str = Field(..., description="분석 ID")
    
    # 입력 정보
    address: str
    land_area: float
    unit_type: str
    recommended_unit_type: Optional[str] = Field(None, description="추천 세대 유형 (최고 점수)")
    all_types_scores: List[UnitTypeScore] = Field(default=[], description="전체 유형 점수 목록")
    
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
    
    # 등급 및 체크리스트 (신규)
    grade_info: Optional[GradeInfo] = Field(None, description="등급 평가 결과")
    checklist: List[CheckItemSchema] = Field(default=[], description="체크리스트")
    checklist_details: Optional[Dict[str, Any]] = Field(None, description="체크리스트 상세 정보 (PDF 생성용)")
    
    # ✨ v5.0: 유형별 수요점수 완전 분리
    type_demand_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="유형별 독립 수요점수 (청년, 신혼I, 신혼II, 다자녀, 고령자)"
    )
    
    # ✨ v5.0: AI Auto Corrector, Geo Optimizer, Parcel Clustering
    corrected_input: Optional[Dict[str, Any]] = Field(
        None,
        description="AI 자동 교정 결과 (주소/면적 교정, 경고, 제안)"
    )
    geo_optimization: Optional[Dict[str, Any]] = Field(
        None,
        description="지리적 최적화 분석 결과 (추천 대안 위치, 점수)"
    )
    clusters: Optional[Dict[str, Any]] = Field(
        None,
        description="다필지 클러스터링 결과 (준비용, 단일 필지는 선택사항)"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "analysis_id": "abc123",
                "address": "서울특별시 강남구 역삼동 123-45",
                "land_area": 500.0,
                "unit_type": "청년",
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


# ✨ v5.0: Multi-Parcel Analysis Schemas
class MultiParcelRequest(BaseModel):
    """다필지 분석 요청"""
    parcels: List[str] = Field(..., description="필지 주소 리스트", min_items=1, max_items=10)
    land_area: float = Field(..., description="총 토지 면적(㎡)", example=1500.0, gt=0)
    unit_type: Optional[UnitType] = Field(None, description="세대 유형 (선택사항)")
    lh_version: str = Field("2024", description="LH 기준 버전")
    
    class Config:
        json_schema_extra = {
            "example": {
                "parcels": [
                    "서울특별시 마포구 월드컵북로 120",
                    "서울특별시 마포구 월드컵북로 121"
                ],
                "land_area": 900.0,
                "unit_type": "청년",
                "lh_version": "2024"
            }
        }


class ParcelAnalysisResult(BaseModel):
    """개별 필지 분석 결과"""
    address: str
    success: bool
    error_message: Optional[str] = None
    
    # 분석 결과 (성공 시)
    coordinates: Optional[Coordinates] = None
    demand_score: Optional[float] = None
    building_capacity: Optional[int] = None
    risk_factors: List[RiskFactor] = Field(default=[])
    summary: Optional[AnalysisSummary] = None


class MultiParcelResponse(BaseModel):
    """다필지 분석 응답"""
    status: str = "success"
    analysis_id: str
    
    # 통계
    total_parcels: int
    successful: int
    failed: int
    
    # 개별 필지 결과
    results: List[ParcelAnalysisResult]
    
    # 종합 분석 (선택사항)
    cluster_analysis: Optional[Dict[str, Any]] = Field(
        None, 
        description="다필지 클러스터링 분석 결과"
    )
    
    # 추천
    recommended_parcels: List[str] = Field(
        default=[],
        description="점수 기반 추천 필지 목록"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)
