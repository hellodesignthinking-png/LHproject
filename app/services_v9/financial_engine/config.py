"""
Financial Engine Configuration
===============================

모든 단가, 계수, 지수를 외부에서 제어 가능
매년 업데이트 가능한 구조

Author: ZeroSite Development Team
Date: 2025-12-06
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


class ConstructionCostConfig(BaseModel):
    """공사비 설정"""
    
    # 공사비연동제 기준 단가 (원/m²)
    base_unit_price: float = Field(
        default=2800000,
        description="기본 공사비 단가 (원/m²) - LH 2025 기준"
    )
    
    # 지역별 계수
    regional_coefficients: Dict[str, float] = Field(
        default={
            "서울": 1.00,
            "경기": 0.95,
            "인천": 0.93,
            "대전": 0.90,
            "대구": 0.88,
            "부산": 0.90,
            "광주": 0.88,
            "울산": 0.88,
            "세종": 0.92,
            "기타": 0.85
        },
        description="지역별 공사비 계수"
    )
    
    # 공사비 연동지수 (매년 업데이트)
    cost_indices: Dict[str, float] = Field(
        default={
            "2023": 1.000,
            "2024": 1.047,
            "2025": 1.092,
            "2026": 1.120  # 예상치
        },
        description="연도별 공사비 연동지수"
    )
    
    # 용도지역별 가산율
    zone_premiums: Dict[str, float] = Field(
        default={
            "제1종일반주거지역": 0.00,
            "제2종일반주거지역": 0.02,
            "제3종일반주거지역": 0.05,
            "준주거지역": 0.07,
            "상업지역": 0.10,
            "준공업지역": 0.03
        },
        description="용도지역별 공사비 가산율"
    )
    
    # 주차장 공사비 (지상/지하)
    parking_costs: Dict[str, float] = Field(
        default={
            "surface": 3000000,    # 지상 주차 (대당)
            "basement": 15000000,  # 지하 주차 (대당)
            "mechanical": 25000000 # 기계식 주차 (대당)
        },
        description="주차장 형태별 공사비 (대당)"
    )


class IndirectCostConfig(BaseModel):
    """간접비 설정"""
    
    # 간접비율
    indirect_rate: float = Field(
        default=0.18,
        description="간접비율 (직접공사비의 %)"
    )
    
    # 간접비 세부 구성
    breakdown: Dict[str, float] = Field(
        default={
            "design": 0.03,        # 설계비
            "supervision": 0.02,   # 감리비
            "permit": 0.01,        # 인허가
            "insurance": 0.01,     # 보험료
            "contingency": 0.05,   # 예비비
            "overhead": 0.03,      # 일반관리비
            "profit": 0.03         # 이윤
        },
        description="간접비 세부 구성비율"
    )


class FinanceCostConfig(BaseModel):
    """금융비용 설정"""
    
    # 금리
    interest_rate: float = Field(
        default=0.045,
        description="연 이자율 (4.5%)"
    )
    
    # 공사기간 (개월)
    default_construction_period: int = Field(
        default=24,
        description="기본 공사기간 (개월)"
    )
    
    # 중도금 비율
    interim_payment_ratio: float = Field(
        default=0.60,
        description="중도금 비율 (60%)"
    )
    
    # 대출비율
    loan_to_cost_ratio: float = Field(
        default=0.70,
        description="총 사업비 대비 대출비율 (LTV)"
    )


class OPEXConfig(BaseModel):
    """운영비 설정"""
    
    # 연간 운영비 (m²당)
    annual_opex_per_sqm: float = Field(
        default=50000,
        description="연간 운영비 단가 (원/m²)"
    )
    
    # 운영비 구성
    breakdown: Dict[str, float] = Field(
        default={
            "maintenance": 0.40,   # 유지보수 40%
            "management": 0.30,    # 관리비 30%
            "utilities": 0.15,     # 공과금 15%
            "insurance": 0.10,     # 보험료 10%
            "other": 0.05          # 기타 5%
        },
        description="운영비 구성 비율"
    )


class RevenueConfig(BaseModel):
    """수익 설정"""
    
    # 평균 임대료 (월/m²)
    rent_per_sqm_per_month: float = Field(
        default=15000,
        description="평균 임대료 (원/m²/월)"
    )
    
    # 입주율
    occupancy_rate: float = Field(
        default=0.95,
        description="평균 입주율 (95%)"
    )
    
    # 지역별 임대료 계수
    rent_regional_factors: Dict[str, float] = Field(
        default={
            "서울": 1.20,
            "경기": 1.00,
            "인천": 0.95,
            "대전": 0.85,
            "대구": 0.85,
            "부산": 0.90,
            "광주": 0.80,
            "기타": 0.75
        },
        description="지역별 임대료 계수"
    )


class LHPriceConfig(BaseModel):
    """LH 매입가 설정"""
    
    # LH 기준 단가 (원/m²)
    lh_base_price_per_sqm: float = Field(
        default=2500000,
        description="LH 기준 매입단가 (원/m²) - 공급면적 기준"
    )
    
    # LH 지역계수
    lh_regional_factors: Dict[str, float] = Field(
        default={
            "서울": 1.15,
            "경기": 1.05,
            "인천": 1.00,
            "대전": 0.95,
            "대구": 0.95,
            "부산": 1.00,
            "광주": 0.90,
            "기타": 0.85
        },
        description="LH 매입가 지역계수"
    )
    
    # LH 유형별 단가 조정
    unit_type_factors: Dict[str, float] = Field(
        default={
            "청년": 0.90,
            "신혼·신생아 I": 1.00,
            "신혼·신생아 II": 1.05,
            "다자녀": 1.10,
            "고령자": 0.95,
            "일반": 1.15
        },
        description="LH 유형별 단가 조정계수"
    )
    
    # 연도별 상승률
    annual_increase_rate: float = Field(
        default=0.03,
        description="LH 매입가 연간 상승률 (3%)"
    )


class FinancialConfig(BaseModel):
    """
    전체 재무 설정
    
    모든 단가와 계수를 한 곳에서 관리
    """
    construction: ConstructionCostConfig = Field(
        default_factory=ConstructionCostConfig
    )
    indirect: IndirectCostConfig = Field(
        default_factory=IndirectCostConfig
    )
    finance: FinanceCostConfig = Field(
        default_factory=FinanceCostConfig
    )
    opex: OPEXConfig = Field(
        default_factory=OPEXConfig
    )
    revenue: RevenueConfig = Field(
        default_factory=RevenueConfig
    )
    lh_price: LHPriceConfig = Field(
        default_factory=LHPriceConfig
    )
    
    # Metadata
    last_updated: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="최종 업데이트 일시"
    )
    version: str = Field(
        default="2025.1",
        description="설정 버전"
    )


# Global configuration instance
_financial_config: Optional[FinancialConfig] = None


def get_financial_config() -> FinancialConfig:
    """Get or create financial configuration singleton"""
    global _financial_config
    if _financial_config is None:
        _financial_config = FinancialConfig()
    return _financial_config


def update_financial_config(**kwargs) -> FinancialConfig:
    """
    Update financial configuration
    
    Example:
        >>> config = update_financial_config(
        ...     construction__base_unit_price=3000000,
        ...     finance__interest_rate=0.05
        ... )
    """
    global _financial_config
    if _financial_config is None:
        _financial_config = FinancialConfig()
    
    # Update nested fields
    for key, value in kwargs.items():
        if '__' in key:
            # Handle nested updates
            parts = key.split('__')
            obj = _financial_config
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
        else:
            setattr(_financial_config, key, value)
    
    # Update timestamp
    _financial_config.last_updated = datetime.now().isoformat()
    
    return _financial_config


def reset_financial_config():
    """Reset to default configuration"""
    global _financial_config
    _financial_config = FinancialConfig()
    return _financial_config
