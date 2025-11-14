"""
사업성 시뮬레이션 데이터 모델

이 모듈은 건축비 계산, LH 매입가 시뮬레이션, ROI/IRR 분석을 위한
Pydantic 데이터 모델을 정의합니다.
"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime


class UnitType(str, Enum):
    """주택 유형"""
    YOUTH = "YOUTH"  # 청년주택
    NEWLYWED = "NEWLYWED"  # 신혼희망타운
    PUBLIC_RENTAL = "PUBLIC_RENTAL"  # 공공임대


class Region(str, Enum):
    """지역"""
    SEOUL = "서울특별시"
    GYEONGGI = "경기도"
    INCHEON = "인천광역시"
    SEJONG = "세종특별자치시"
    DAEJEON = "대전광역시"
    DAEGU = "대구광역시"
    BUSAN = "부산광역시"
    GWANGJU = "광주광역시"
    ULSAN = "울산광역시"
    OTHER = "기타"


# ============================================================================
# 건축비 계산 모델
# ============================================================================

class CostCalculationRequest(BaseModel):
    """건축비 계산 요청"""
    unit_type: UnitType = Field(description="주택 유형")
    gross_area: float = Field(gt=0, description="연면적 (㎡)")
    region: str = Field(description="지역명 (예: 서울특별시, 경기도)")
    num_units: int = Field(gt=0, description="총 세대수")
    num_floors: Optional[int] = Field(default=4, ge=1, description="층수")
    
    class Config:
        json_schema_extra = {
            "example": {
                "unit_type": "YOUTH",
                "gross_area": 1000.0,
                "region": "서울특별시",
                "num_units": 20,
                "num_floors": 4
            }
        }


class CostBreakdown(BaseModel):
    """공사 항목별 비용 상세"""
    civil: float = Field(description="토목공사비 (원)")
    architecture: float = Field(description="건축공사비 (원)")
    mechanical: float = Field(description="기계설비비 (원)")
    electrical: float = Field(description="전기공사비 (원)")
    landscaping: float = Field(description="조경공사비 (원)")
    others: float = Field(description="기타 비용 (원)")


class CostCalculationResponse(BaseModel):
    """건축비 계산 결과"""
    total_cost: float = Field(description="총 건축비 (원)")
    cost_per_pyeong: float = Field(description="평당 건축비 (원/평)")
    cost_per_sqm: float = Field(description="㎡당 건축비 (원/㎡)")
    cost_breakdown: CostBreakdown = Field(description="공사 항목별 비용")
    additional_costs: float = Field(description="부대비용 - 설계/감리/인허가 등 (원)")
    grand_total: float = Field(description="총 사업비 (원)")
    
    # 추가 정보
    base_cost_per_pyeong: float = Field(description="기본 평당 단가 (원/평)")
    regional_multiplier: float = Field(description="지역 할증률")
    total_pyeong: float = Field(description="총 평수")
    
    calculated_at: datetime = Field(default_factory=datetime.now, description="계산 시각")


# ============================================================================
# LH 매입가 시뮬레이션 모델
# ============================================================================

class PurchaseSimulationRequest(BaseModel):
    """LH 매입가 시뮬레이션 요청"""
    unit_type: UnitType = Field(description="주택 유형")
    land_value: float = Field(gt=0, description="토지 감정평가액 (원)")
    construction_cost: float = Field(gt=0, description="건축비 (원)")
    gross_area: float = Field(gt=0, description="연면적 (㎡)")
    num_units: int = Field(gt=0, description="총 세대수")
    region: str = Field(description="지역명")
    
    # 선택적 파라미터
    custom_profit_rate: Optional[float] = Field(
        default=None,
        ge=0,
        le=0.20,
        description="사용자 지정 이윤율 (0~20%, 미입력시 자동 계산)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "unit_type": "YOUTH",
                "land_value": 3000000000,
                "construction_cost": 2000000000,
                "gross_area": 1000.0,
                "num_units": 20,
                "region": "서울특별시"
            }
        }


class PurchaseSimulationResponse(BaseModel):
    """LH 매입가 시뮬레이션 결과"""
    # 입력 값
    land_value: float = Field(description="토지비 (원)")
    construction_cost: float = Field(description="건축비 (원)")
    
    # 계산 결과
    profit_rate: float = Field(description="적용된 이윤율 (%)")
    profit_amount: float = Field(description="적정이윤 (원)")
    total_purchase_price: float = Field(description="LH 총 매입가 (원)")
    
    # 단가 정보
    price_per_unit: float = Field(description="세대당 매입가 (원/세대)")
    price_per_pyeong: float = Field(description="평당 매입가 (원/평)")
    price_per_sqm: float = Field(description="㎡당 매입가 (원/㎡)")
    
    # ROI 정보
    total_investment: float = Field(description="총 투자액 (원)")
    expected_profit: float = Field(description="예상 수익 (원)")
    roi_percentage: float = Field(description="투자수익률 ROI (%)")
    
    # LH 매입 가능 여부
    is_eligible: bool = Field(description="LH 매입 기준 충족 여부")
    eligibility_notes: List[str] = Field(default=[], description="매입 기준 검토 메모")
    
    calculated_at: datetime = Field(default_factory=datetime.now, description="계산 시각")


# ============================================================================
# ROI/IRR 분석 모델
# ============================================================================

class CashFlowItem(BaseModel):
    """현금흐름 항목"""
    year: int = Field(ge=0, description="연도 (0부터 시작)")
    amount: float = Field(description="금액 (원, 음수는 지출, 양수는 수입)")
    description: str = Field(description="항목 설명")


class ROIAnalysisRequest(BaseModel):
    """ROI/IRR 분석 요청"""
    project_name: str = Field(description="프로젝트 명")
    
    # 투자 정보
    land_acquisition_cost: float = Field(gt=0, description="토지 매입비 (원)")
    construction_cost: float = Field(gt=0, description="건축비 (원)")
    other_costs: float = Field(default=0, description="기타 비용 (원)")
    
    # 수익 정보
    lh_purchase_price: float = Field(gt=0, description="LH 매입가 (원)")
    
    # 일정 정보
    land_acquisition_year: int = Field(default=0, ge=0, description="토지 매입 시점 (년)")
    construction_start_year: int = Field(default=0, ge=0, description="건축 시작 시점 (년)")
    construction_duration_years: int = Field(default=2, ge=1, le=5, description="건축 기간 (년)")
    lh_purchase_year: int = Field(default=2, ge=1, description="LH 매입 시점 (년)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "서울 강남 청년주택",
                "land_acquisition_cost": 3000000000,
                "construction_cost": 2000000000,
                "other_costs": 200000000,
                "lh_purchase_price": 5800000000,
                "land_acquisition_year": 0,
                "construction_start_year": 0,
                "construction_duration_years": 2,
                "lh_purchase_year": 2
            }
        }


class ROIAnalysisResponse(BaseModel):
    """ROI/IRR 분석 결과"""
    project_name: str = Field(description="프로젝트 명")
    
    # 투자 수익률
    total_investment: float = Field(description="총 투자액 (원)")
    total_revenue: float = Field(description="총 수익 (원)")
    net_profit: float = Field(description="순이익 (원)")
    roi_percentage: float = Field(description="투자수익률 ROI (%)")
    
    # 내부수익률
    irr_percentage: Optional[float] = Field(description="내부수익률 IRR (%)")
    
    # 회수 기간
    payback_period_years: float = Field(description="투자 회수 기간 (년)")
    
    # 현금흐름
    cash_flows: List[CashFlowItem] = Field(description="연도별 현금흐름")
    
    # NPV (순현재가치)
    npv: Optional[float] = Field(default=None, description="순현재가치 NPV (원, 할인율 10% 기준)")
    
    calculated_at: datetime = Field(default_factory=datetime.now, description="계산 시각")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "서울 강남 청년주택",
                "total_investment": 5200000000,
                "total_revenue": 5800000000,
                "net_profit": 600000000,
                "roi_percentage": 11.54,
                "irr_percentage": 9.87,
                "payback_period_years": 2.0,
                "cash_flows": [
                    {"year": 0, "amount": -3000000000, "description": "토지 매입"},
                    {"year": 1, "amount": -1500000000, "description": "건축비 (1차)"},
                    {"year": 2, "amount": -700000000, "description": "건축비 (2차) + 기타"},
                    {"year": 2, "amount": 5800000000, "description": "LH 매입"}
                ]
            }
        }


# ============================================================================
# 민감도 분석 모델
# ============================================================================

class SensitivityVariable(str, Enum):
    """민감도 분석 변수"""
    LAND_PRICE = "land_price"  # 토지 가격
    CONSTRUCTION_COST = "construction_cost"  # 건축비
    PROFIT_RATE = "profit_rate"  # 이윤율
    INTEREST_RATE = "interest_rate"  # 금리


class SensitivityAnalysisRequest(BaseModel):
    """민감도 분석 요청"""
    base_scenario: ROIAnalysisRequest = Field(description="기본 시나리오")
    variables: List[SensitivityVariable] = Field(
        default=[SensitivityVariable.LAND_PRICE, SensitivityVariable.CONSTRUCTION_COST],
        description="분석할 변수 목록"
    )
    variation_percentages: List[float] = Field(
        default=[-20, -10, -5, 0, 5, 10, 20],
        description="변동 비율 (%, 예: -10은 10% 감소)"
    )


class SensitivityScenario(BaseModel):
    """민감도 분석 시나리오"""
    variable: SensitivityVariable = Field(description="변수명")
    change_percentage: float = Field(description="변동 비율 (%)")
    roi: float = Field(description="ROI (%)")
    irr: Optional[float] = Field(description="IRR (%)")
    net_profit: float = Field(description="순이익 (원)")


class SensitivityAnalysisResponse(BaseModel):
    """민감도 분석 결과"""
    base_roi: float = Field(description="기본 시나리오 ROI (%)")
    base_irr: Optional[float] = Field(description="기본 시나리오 IRR (%)")
    
    scenarios: List[SensitivityScenario] = Field(description="시나리오별 분석 결과")
    
    # 요약 통계
    most_sensitive_variable: SensitivityVariable = Field(description="가장 민감한 변수")
    roi_range: Dict[str, float] = Field(description="ROI 범위 (min, max)")
    
    calculated_at: datetime = Field(default_factory=datetime.now, description="계산 시각")


# ============================================================================
# 종합 분석 모델
# ============================================================================

class ComprehensiveAnalysisRequest(BaseModel):
    """종합 사업성 분석 요청"""
    project_name: str = Field(description="프로젝트 명")
    address: str = Field(description="주소")
    unit_type: UnitType = Field(description="주택 유형")
    
    # 토지 정보
    land_area: float = Field(gt=0, description="토지 면적 (㎡)")
    land_price_per_sqm: float = Field(gt=0, description="토지 단가 (원/㎡)")
    
    # 건축 정보
    gross_area: float = Field(gt=0, description="연면적 (㎡)")
    num_units: int = Field(gt=0, description="총 세대수")
    num_floors: int = Field(default=4, ge=1, description="층수")
    
    # 지역
    region: str = Field(description="지역명")
    
    # 일정
    construction_duration_years: int = Field(default=2, ge=1, le=5, description="건축 기간 (년)")


class ComprehensiveAnalysisResponse(BaseModel):
    """종합 사업성 분석 결과"""
    project_name: str = Field(description="프로젝트 명")
    address: str = Field(description="주소")
    
    # 건축비 분석
    construction_analysis: CostCalculationResponse = Field(description="건축비 분석 결과")
    
    # LH 매입가 분석
    purchase_analysis: PurchaseSimulationResponse = Field(description="LH 매입가 분석 결과")
    
    # ROI/IRR 분석
    roi_analysis: ROIAnalysisResponse = Field(description="ROI/IRR 분석 결과")
    
    # 종합 평가
    overall_rating: str = Field(description="종합 평가 (우수/양호/보통/미흡)")
    recommendations: List[str] = Field(description="권장 사항")
    risk_factors: List[str] = Field(description="리스크 요인")
    
    calculated_at: datetime = Field(default_factory=datetime.now, description="계산 시각")
