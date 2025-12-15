"""
ZeroSite Canonical Appraisal Schema
감정평가 표준 출력 스키마 정의

Version: v8.7+
Date: 2025-12-15

This module defines the standard output structure for appraisal results,
ensuring consistency across all engines (Land Diagnosis, LH Analysis, etc.)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ZoningInfo(BaseModel):
    """용도지역 정보"""
    confirmed_type: str = Field(..., description="확정 용도지역 (예: 제2종일반주거지역)")
    building_coverage_ratio: float = Field(..., description="건폐율 (%)")
    floor_area_ratio: float = Field(..., description="용적률 (%)")
    source: str = Field(default="국토부 API", description="데이터 출처")
    verified_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"), description="확인 일자")


class OfficialLandPrice(BaseModel):
    """공시지가 정보"""
    standard_price_per_sqm: float = Field(..., description="표준지 공시지가 (원/㎡)")
    reference_year: int = Field(..., description="기준 연도")
    reference_parcel: str = Field(..., description="표준지 필지 주소")
    distance_to_standard: float = Field(..., description="표준지까지 거리 (m)")
    source: str = Field(default="표준지공시지가", description="데이터 출처")


class TransactionCase(BaseModel):
    """거래사례 정보"""
    price_per_sqm: float = Field(..., description="거래 단가 (원/㎡)")
    transaction_date: str = Field(..., description="거래 일자 (YYYY-MM-DD)")
    distance_m: float = Field(..., description="대상 토지와의 거리 (m)")
    area_sqm: float = Field(..., description="거래 면적 (㎡)")
    similarity_score: float = Field(..., description="유사도 점수 (0-1)")
    adjusted_for_time: bool = Field(default=True, description="시점 보정 여부")
    adjusted_for_location: bool = Field(default=True, description="위치 보정 여부")


class PremiumDetail(BaseModel):
    """프리미엄 항목"""
    rate: float = Field(..., description="프리미엄 비율 (0-1)")
    rationale: str = Field(..., description="적용 근거")


class PremiumInfo(BaseModel):
    """프리미엄 정보"""
    development_potential: PremiumDetail = Field(..., description="개발 잠재력")
    location_premium: PremiumDetail = Field(..., description="입지 프리미엄")
    policy_benefit: PremiumDetail = Field(..., description="정책 혜택")
    total_premium_rate: float = Field(..., description="총 프리미엄 비율 (0-1)")


class CalculationInfo(BaseModel):
    """계산 정보"""
    base_price_per_sqm: float = Field(..., description="기준 단가 (원/㎡)")
    premium_adjusted_per_sqm: float = Field(..., description="프리미엄 적용 단가 (원/㎡)")
    land_area_sqm: float = Field(..., description="토지 면적 (㎡)")
    final_appraised_total: float = Field(..., description="최종 감정가 (원)")


class ConfidenceFactors(BaseModel):
    """신뢰도 요인"""
    data_completeness: float = Field(..., description="데이터 완전성 (0-1)")
    case_similarity: float = Field(..., description="사례 유사도 (0-1)")
    time_relevance: float = Field(..., description="시점 적정성 (0-1)")


class ConfidenceInfo(BaseModel):
    """신뢰도 정보"""
    score: float = Field(..., description="전체 신뢰도 (0-1)")
    factors: ConfidenceFactors = Field(..., description="신뢰도 요인 상세")


class MetadataInfo(BaseModel):
    """메타데이터"""
    appraisal_engine: str = Field(default="ZeroSite v8.7", description="감정평가 엔진 버전")
    calculation_method: str = Field(default="비교방식", description="계산 방법")
    appraiser_note: Optional[str] = Field(None, description="감정평가사 메모")


class CanonicalAppraisalResult(BaseModel):
    """
    감정평가 표준 출력 구조
    
    This is the Single Source of Truth for all subsequent analysis.
    All engines (Land Diagnosis, LH Analysis) must reference this structure.
    """
    version: str = Field(default="v8.7", description="스키마 버전")
    locked: bool = Field(default=False, description="컨텍스트 잠금 상태")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="생성 시각")
    locked_at: Optional[str] = Field(None, description="잠금 시각")
    
    # Core data sections
    zoning: ZoningInfo = Field(..., description="용도지역 정보")
    official_land_price: OfficialLandPrice = Field(..., description="공시지가 정보")
    transaction_cases: List[TransactionCase] = Field(default_factory=list, description="거래사례 목록")
    premium: PremiumInfo = Field(..., description="프리미엄 정보")
    calculation: CalculationInfo = Field(..., description="계산 정보")
    confidence: ConfidenceInfo = Field(..., description="신뢰도 정보")
    metadata: MetadataInfo = Field(default_factory=MetadataInfo, description="메타데이터")
    
    class Config:
        json_schema_extra = {
            "example": {
                "version": "v8.7",
                "locked": True,
                "timestamp": "2025-12-15T10:00:00Z",
                "locked_at": "2025-12-15T10:00:01Z",
                "zoning": {
                    "confirmed_type": "제2종일반주거지역",
                    "building_coverage_ratio": 60.0,
                    "floor_area_ratio": 200.0,
                    "source": "국토부 API",
                    "verified_at": "2025-12-15"
                },
                "official_land_price": {
                    "standard_price_per_sqm": 3200000,
                    "reference_year": 2024,
                    "reference_parcel": "서울특별시 마포구 XX-XX",
                    "distance_to_standard": 150,
                    "source": "표준지공시지가"
                },
                "transaction_cases": [
                    {
                        "price_per_sqm": 4100000,
                        "transaction_date": "2024-08-15",
                        "distance_m": 180,
                        "area_sqm": 650,
                        "similarity_score": 0.92,
                        "adjusted_for_time": True,
                        "adjusted_for_location": True
                    }
                ],
                "premium": {
                    "development_potential": {
                        "rate": 0.08,
                        "rationale": "역세권 개발 가능성"
                    },
                    "location_premium": {
                        "rate": 0.05,
                        "rationale": "지하철 300m, 학교 400m"
                    },
                    "policy_benefit": {
                        "rate": 0.03,
                        "rationale": "LH 우선 매입 지역"
                    },
                    "total_premium_rate": 0.16
                },
                "calculation": {
                    "base_price_per_sqm": 3650000,
                    "premium_adjusted_per_sqm": 4234000,
                    "land_area_sqm": 865.0,
                    "final_appraised_total": 3662410000
                },
                "confidence": {
                    "score": 0.92,
                    "factors": {
                        "data_completeness": 0.95,
                        "case_similarity": 0.90,
                        "time_relevance": 0.91
                    }
                },
                "metadata": {
                    "appraisal_engine": "ZeroSite v8.7",
                    "calculation_method": "비교방식",
                    "appraiser_note": "3개 거래사례 기준, 프리미엄 16% 적용"
                }
            }
        }
    
    def to_context_dict(self) -> Dict[str, Any]:
        """
        Convert to context dictionary format for AppraisalContextLock
        
        Returns:
            Dictionary matching the canonical schema structure
        """
        return {
            "version": self.version,
            "locked": self.locked,
            "timestamp": self.timestamp,
            "locked_at": self.locked_at,
            "zoning": self.zoning.model_dump(),
            "official_land_price": self.official_land_price.model_dump(),
            "transaction_cases": [case.model_dump() for case in self.transaction_cases],
            "premium": self.premium.model_dump(),
            "calculation": self.calculation.model_dump(),
            "confidence": self.confidence.model_dump(),
            "metadata": self.metadata.model_dump()
        }


def create_appraisal_from_analysis(
    zone_info,
    land_area: float,
    official_price: float,
    transaction_price: Optional[float] = None,
    premium_rate: float = 0.0,
    confidence_score: float = 0.85
) -> CanonicalAppraisalResult:
    """
    기존 analysis_engine 결과를 Canonical Schema로 변환
    
    Args:
        zone_info: 용도지역 정보 (ZoneInfo object)
        land_area: 토지 면적 (㎡)
        official_price: 공시지가 (원/㎡)
        transaction_price: 실거래가 (원/㎡, optional)
        premium_rate: 프리미엄 비율 (0-1)
        confidence_score: 신뢰도 (0-1)
    
    Returns:
        CanonicalAppraisalResult object
    """
    
    # Calculate base and final prices
    base_price_per_sqm = official_price * 1.05  # 공시지가 5% 할증
    if transaction_price:
        base_price_per_sqm = max(base_price_per_sqm, transaction_price * 0.95)
    
    premium_adjusted_per_sqm = base_price_per_sqm * (1 + premium_rate)
    final_appraised_total = premium_adjusted_per_sqm * land_area
    
    # Create canonical result
    return CanonicalAppraisalResult(
        zoning=ZoningInfo(
            confirmed_type=zone_info.zone_type,
            building_coverage_ratio=zone_info.building_coverage_ratio or 60.0,
            floor_area_ratio=zone_info.floor_area_ratio or 200.0
        ),
        official_land_price=OfficialLandPrice(
            standard_price_per_sqm=official_price,
            reference_year=datetime.now().year,
            reference_parcel="자동 추정",
            distance_to_standard=0.0
        ),
        transaction_cases=[],  # Will be populated if transaction data available
        premium=PremiumInfo(
            development_potential=PremiumDetail(
                rate=premium_rate * 0.5,  # 50% allocated to development
                rationale="개발 잠재력 평가"
            ),
            location_premium=PremiumDetail(
                rate=premium_rate * 0.3,  # 30% allocated to location
                rationale="입지 프리미엄"
            ),
            policy_benefit=PremiumDetail(
                rate=premium_rate * 0.2,  # 20% allocated to policy
                rationale="정책 혜택"
            ),
            total_premium_rate=premium_rate
        ),
        calculation=CalculationInfo(
            base_price_per_sqm=base_price_per_sqm,
            premium_adjusted_per_sqm=premium_adjusted_per_sqm,
            land_area_sqm=land_area,
            final_appraised_total=final_appraised_total
        ),
        confidence=ConfidenceInfo(
            score=confidence_score,
            factors=ConfidenceFactors(
                data_completeness=confidence_score,
                case_similarity=confidence_score,
                time_relevance=confidence_score
            )
        ),
        metadata=MetadataInfo(
            appraisal_engine="ZeroSite v8.7",
            calculation_method="비교방식",
            appraiser_note=f"프리미엄 {premium_rate*100:.1f}% 적용"
        )
    )


# Type alias for backward compatibility
AppraisalContext = CanonicalAppraisalResult


__all__ = [
    'CanonicalAppraisalResult',
    'ZoningInfo',
    'OfficialLandPrice',
    'TransactionCase',
    'PremiumInfo',
    'PremiumDetail',
    'CalculationInfo',
    'ConfidenceInfo',
    'ConfidenceFactors',
    'MetadataInfo',
    'AppraisalContext',
    'create_appraisal_from_analysis'
]
