"""
LH Decision Engine Configuration
=================================

Phase 3: LH Decision Engine - Configuration Module
정부 LH 공공임대주택 심사 기준 공식 설정

Author: ZeroSite Development Team
Date: 2025-12-06
"""

from typing import Dict, Any, List
from dataclasses import dataclass

# ======================
# LH 공식 심사 기준 (2024)
# ======================

@dataclass
class LHScoringWeights:
    """LH 심사 100점 만점 배점 기준"""
    
    # 1. 입지 조건 (Location) - 25점
    location_score: float = 25.0
    location_weights = {
        "subway_proximity": 8.0,      # 지하철 접근성 (300m 이내: 8점, 500m 이내: 6점, 1km 이내: 4점)
        "school_proximity": 7.0,       # 학교 접근성 (초/중학교 500m 이내)
        "commercial_area": 5.0,        # 상업시설 접근성
        "public_transport": 5.0        # 버스정류장/대중교통
    }
    
    # 2. 사업성 (Feasibility) - 30점
    feasibility_score: float = 30.0
    feasibility_weights = {
        "financial_gap": 15.0,         # LH 매입가격 갭 (Gap < -20%: 0점, -10~0%: 10점, 0~10%: 15점)
        "construction_cost": 8.0,      # 공사비 적정성 (㎡당 350만원 이하)
        "roi": 4.0,                    # ROI 수익성 (3% 이상)
        "irr": 3.0                     # IRR (5% 이상)
    }
    
    # 3. 설계 적합성 (Design Compliance) - 20점
    design_score: float = 20.0
    design_weights = {
        "unit_mix": 8.0,               # 세대구성 적정성 (59㎡ 중심, 84㎡ 혼합)
        "parking_ratio": 6.0,          # 주차장 확보 (세대당 1.0대 이상)
        "common_facilities": 6.0       # 공용시설 확보 (관리사무소, 커뮤니티시설)
    }
    
    # 4. 법규 준수 (Legal Compliance) - 15점
    legal_score: float = 15.0
    legal_weights = {
        "zoning_compliance": 8.0,      # 용도지역 적합성
        "building_coverage": 4.0,      # 건폐율 준수
        "floor_area_ratio": 3.0        # 용적률 준수
    }
    
    # 5. 리스크 관리 (Risk Management) - 10점
    risk_score: float = 10.0
    risk_weights = {
        "market_stability": 5.0,       # 시장 안정성
        "construction_risk": 3.0,      # 시공 리스크
        "approval_risk": 2.0           # 인허가 리스크
    }


@dataclass
class LHDecisionThresholds:
    """LH 의사결정 임계값 (GO / REVIEW / NO-GO)"""
    
    # 총점 기준
    go_threshold: float = 70.0         # 70점 이상: GO (즉시 사업 추진)
    review_threshold: float = 55.0     # 55~70점: REVIEW (조건부 검토)
    # 55점 미만: NO-GO (사업 보류)
    
    # 개별 항목 최소 기준
    min_location_score: float = 15.0   # 입지 최소 15점 (25점 중)
    min_feasibility_score: float = 18.0 # 사업성 최소 18점 (30점 중)
    min_design_score: float = 12.0     # 설계 최소 12점 (20점 중)
    
    # Critical Blockers (하나라도 해당시 NO-GO)
    max_financial_gap: float = -30.0   # LH 갭이 -30% 초과시 NO-GO
    min_parking_ratio: float = 0.7     # 주차비율 0.7대/세대 미만시 NO-GO
    max_construction_cost_per_sqm: float = 6000000  # ㎡당 600만원 초과시 NO-GO (건축비 + 토지비 포함)


@dataclass
class LHCriteriaData:
    """LH 기준 데이터 (실제 정부 고시 기준)"""
    
    # 1. 매입가격 기준 (지역별, 2024년 기준)
    acquisition_price_per_sqm: Dict[str, float] = None
    
    def __post_init__(self):
        if self.acquisition_price_per_sqm is None:
            self.acquisition_price_per_sqm = {
                "서울": 5500000,      # ㎡당 550만원
                "경기": 4200000,      # ㎡당 420만원
                "인천": 4000000,      # ㎡당 400만원
                "부산": 3800000,
                "대구": 3500000,
                "광주": 3300000,
                "대전": 3600000,
                "울산": 3400000,
                "세종": 4000000,
                "기타": 3000000
            }
    
    # 2. 표준 건축비 (㎡당, 공사비 기준)
    standard_construction_cost = {
        "일반주거지역": 3500000,    # ㎡당 350만원
        "준주거지역": 3800000,
        "상업지역": 4200000
    }
    
    # 3. 세대당 필수 주차대수
    required_parking_per_unit = {
        "서울": 1.0,
        "경기": 1.0,
        "인천": 1.0,
        "기타": 0.8
    }
    
    # 4. 선호 세대 타입 분포
    preferred_unit_distribution = {
        "type_59": 0.60,   # 59㎡ 60%
        "type_74": 0.20,   # 74㎡ 20%
        "type_84": 0.15,   # 84㎡ 15%
        "type_100": 0.05   # 100㎡ 5%
    }


# ======================
# Global Config Instance
# ======================

LH_SCORING_WEIGHTS = LHScoringWeights()
LH_DECISION_THRESHOLDS = LHDecisionThresholds()
LH_CRITERIA_DATA = LHCriteriaData()


# ======================
# Helper Functions
# ======================

def get_region_from_address(address: str) -> str:
    """주소에서 지역 추출"""
    if "서울" in address:
        return "서울"
    elif "경기" in address:
        return "경기"
    elif "인천" in address:
        return "인천"
    elif "부산" in address:
        return "부산"
    elif "대구" in address:
        return "대구"
    elif "광주" in address:
        return "광주"
    elif "대전" in address:
        return "대전"
    elif "울산" in address:
        return "울산"
    elif "세종" in address:
        return "세종"
    else:
        return "기타"


def get_lh_acquisition_price(region: str, residential_gfa: float) -> float:
    """
    LH 매입가격 계산
    
    Args:
        region: 지역명
        residential_gfa: 주거 전용면적 (㎡)
    
    Returns:
        float: 예상 LH 매입가격 (원)
    """
    price_per_sqm = LH_CRITERIA_DATA.acquisition_price_per_sqm.get(region, 3000000)
    return residential_gfa * price_per_sqm


def get_standard_construction_cost(zone_type: str, total_gfa: float) -> float:
    """
    표준 건축비 계산
    
    Args:
        zone_type: 용도지역
        total_gfa: 총 연면적 (㎡)
    
    Returns:
        float: 표준 건축비 (원)
    """
    if "일반주거" in zone_type:
        cost_per_sqm = LH_CRITERIA_DATA.standard_construction_cost["일반주거지역"]
    elif "준주거" in zone_type:
        cost_per_sqm = LH_CRITERIA_DATA.standard_construction_cost["준주거지역"]
    elif "상업" in zone_type:
        cost_per_sqm = LH_CRITERIA_DATA.standard_construction_cost["상업지역"]
    else:
        cost_per_sqm = 3500000  # 기본값
    
    return total_gfa * cost_per_sqm


def validate_critical_blockers(
    financial_gap_ratio: float,
    parking_ratio: float,
    construction_cost_per_sqm: float
) -> tuple[bool, List[str]]:
    """
    Critical Blocker 검증
    
    Returns:
        tuple[bool, List[str]]: (is_blocked, blocker_reasons)
    """
    blockers = []
    
    if financial_gap_ratio < LH_DECISION_THRESHOLDS.max_financial_gap:
        blockers.append(f"재무 갭 초과: {financial_gap_ratio:.1f}% < {LH_DECISION_THRESHOLDS.max_financial_gap}%")
    
    if parking_ratio < LH_DECISION_THRESHOLDS.min_parking_ratio:
        blockers.append(f"주차비율 미달: {parking_ratio:.2f} < {LH_DECISION_THRESHOLDS.min_parking_ratio}")
    
    if construction_cost_per_sqm > LH_DECISION_THRESHOLDS.max_construction_cost_per_sqm:
        blockers.append(f"㎡당 공사비 초과: ₩{construction_cost_per_sqm:,.0f} > ₩{LH_DECISION_THRESHOLDS.max_construction_cost_per_sqm:,.0f}")
    
    return len(blockers) > 0, blockers


# ======================
# Export All
# ======================

__all__ = [
    'LHScoringWeights',
    'LHDecisionThresholds',
    'LHCriteriaData',
    'LH_SCORING_WEIGHTS',
    'LH_DECISION_THRESHOLDS',
    'LH_CRITERIA_DATA',
    'get_region_from_address',
    'get_lh_acquisition_price',
    'get_standard_construction_cost',
    'validate_critical_blockers'
]
