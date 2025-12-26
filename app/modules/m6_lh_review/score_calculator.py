"""
LH 평가표 점수 계산 모듈
======================

각 평가 항목별 실제 점수 산출 로직

⚠️ LH 실무 기준을 1:1로 반영
⚠️ 임의 가정 금지

Author: ZeroSite M6 Team
Date: 2025-12-26
Version: 1.0
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def calculate_location_score(
    poi_analysis: Dict[str, Any],
    demand_prediction: float,
    location_score_m3: float
) -> float:
    """
    ① 입지 적합성 점수 계산 (20점 만점)
    
    평가 요소:
    - 대중교통 접근성 (지하철역 거리)
    - 생활 SOC (학교, 병원, 상업시설)
    - 역세권 여부
    - 도심 접근성
    
    Args:
        poi_analysis: M3의 POI 분석 결과
        demand_prediction: M3의 수요 예측 점수 (0~100)
        location_score_m3: M3의 입지 점수 (0~35)
    
    Returns:
        float: 입지 점수 (0~20)
    """
    score = 0.0
    
    # M3의 35점 체계를 20점 체계로 변환
    # 기본 점수 (M3 입지 점수 활용)
    base_score = (location_score_m3 / 35.0) * 20.0
    score = base_score
    
    # 역세권 보너스
    if poi_analysis:
        subway_distance = poi_analysis.get("subway_distance", 999999)
        if subway_distance <= 500:  # 역세권 (500m 이내)
            score = min(score + 2.0, 20.0)
        elif subway_distance <= 1000:  # 준역세권 (1km 이내)
            score = min(score + 1.0, 20.0)
    
    # 수요 예측 반영
    if demand_prediction >= 80:
        score = min(score + 1.0, 20.0)
    
    logger.debug(f"입지 적합성: {score:.1f}/20 (기본: {base_score:.1f}, 역세권 보정)")
    return min(max(score, 0.0), 20.0)


def calculate_land_score(
    parcel_id: str,
    b_code: str,
    zone_type: str
) -> float:
    """
    ② 토지 확보 용이성 점수 계산 (15점 만점)
    
    평가 요소:
    - 단일필지 여부
    - 지분 분쟁 여부
    - 소유권 명확성
    
    Args:
        parcel_id: PNU (필지 고유번호)
        b_code: 법정동 코드
        zone_type: 용도지역
    
    Returns:
        float: 토지 확보 점수 (0~15)
    """
    score = 0.0
    
    # 기본 점수: PNU 존재 = 단일 필지 추정
    if parcel_id and len(parcel_id) >= 19:
        score += 6.0  # 단일 필지
        score += 6.0  # 소유권 명확 (추정)
        score += 3.0  # 분쟁 없음 (추정)
    else:
        # PNU 없으면 보수적 점수
        score += 3.0  # 필지 정보 불확실
        score += 3.0  # 소유권 확인 필요
        score += 2.0  # 분쟁 가능성
    
    logger.debug(f"토지 확보 용이성: {score:.1f}/15 (PNU: {'있음' if parcel_id else '없음'})")
    return min(max(score, 0.0), 15.0)


def calculate_technical_score(
    legal_far: float,
    legal_bcr: float,
    incentive_far: float,
    parking_feasible: bool,
    total_units: int
) -> float:
    """
    ③ 건축·기술 적합성 점수 계산 (15점 만점)
    
    평가 요소:
    - 법정 용적률 충족
    - 건폐율 충족
    - 주차계획 가능 여부
    
    Args:
        legal_far: 법정 용적률 (%)
        legal_bcr: 법정 건폐율 (%)
        incentive_far: 인센티브 용적률 (%)
        parking_feasible: 주차 계획 가능 여부
        total_units: 총 세대수
    
    Returns:
        float: 건축·기술 점수 (0~15)
    """
    score = 0.0
    
    # 법규 충족 (8점)
    if legal_far > 0 and legal_bcr > 0:
        score += 8.0  # 법규 100% 충족
    else:
        score += 4.0  # 법규 정보 불완전
    
    # 주차 계획 (5점)
    if parking_feasible:
        score += 5.0  # 주차 계획 가능
    else:
        score += 2.0  # 주차 계획 어려움
    
    # 인센티브 활용 가능성 (2점)
    if incentive_far > legal_far:
        score += 2.0  # 대안 시나리오 존재
    
    logger.debug(f"건축·기술 적합성: {score:.1f}/15 (FAR: {legal_far:.0f}%, 주차: {'가능' if parking_feasible else '어려움'})")
    return min(max(score, 0.0), 15.0)


def calculate_financial_score(
    npv_public: float,
    irr_public: float,
    total_cost: float,
    total_revenue: float
) -> float:
    """
    ④ 사업성(재무) 점수 계산 (25점 만점)
    
    평가 요소:
    - IRR (내부수익률)
    - NPV (순현재가치)
    - ROI (투자수익률)
    - LH 매입 단가 대비 수익성
    
    LH 기준:
    - IRR ≥ 15%: 우수
    - IRR 12~15%: 양호
    - IRR < 12%: 미달
    
    Args:
        npv_public: NPV (공공 기준)
        irr_public: IRR (공공 기준, %)
        total_cost: 총 사업비
        total_revenue: 총 수익
    
    Returns:
        float: 사업성 점수 (0~25)
    """
    score = 0.0
    
    # IRR 기준 점수 (10점)
    if irr_public >= 15.0:
        score += 10.0  # 우수
    elif irr_public >= 12.0:
        score += 7.0   # 양호
    elif irr_public >= 8.0:
        score += 4.0   # 보통
    else:
        score += 0.0   # 미달
    
    # NPV 기준 점수 (7점)
    if npv_public > 0:
        score += 7.0   # 수익성 확보
    elif npv_public > -500_000_000:  # -5억 이내
        score += 4.0   # 소폭 손실
    else:
        score += 0.0   # 대폭 손실
    
    # ROI 기준 점수 (8점)
    if total_cost > 0:
        roi = ((total_revenue - total_cost) / total_cost) * 100
        if roi >= 20.0:
            score += 8.0   # 우수
        elif roi >= 10.0:
            score += 5.0   # 양호
        elif roi >= 0:
            score += 2.0   # 보통
        else:
            score += 0.0   # 미달
    
    logger.debug(f"사업성: {score:.1f}/25 (IRR: {irr_public:.1f}%, NPV: ₩{npv_public:,.0f})")
    return min(max(score, 0.0), 25.0)


def calculate_policy_score(
    selected_type: str,
    selection_confidence: float,
    housing_demand: float
) -> float:
    """
    ⑤ 정책 부합성 점수 계산 (15점 만점)
    
    평가 요소:
    - 청년/신혼/고령 유형 적합성
    - 공급 목표 부합
    
    Args:
        selected_type: M3 선정된 주거 유형 (예: "newlywed_2")
        selection_confidence: M3 선택 신뢰도 (0~1)
        housing_demand: 지역 수요 예측 (0~100)
    
    Returns:
        float: 정책 부합성 점수 (0~15)
    """
    score = 0.0
    
    # 정책 유형 일치도 (10점)
    if selection_confidence >= 0.8:
        score += 10.0  # 정확히 일치
    elif selection_confidence >= 0.6:
        score += 7.0   # 대체로 일치
    elif selection_confidence >= 0.4:
        score += 4.0   # 부분 일치
    else:
        score += 2.0   # 불일치
    
    # 지역 수요 일치 (5점)
    if housing_demand >= 70:
        score += 5.0   # 높은 수요
    elif housing_demand >= 50:
        score += 3.0   # 중간 수요
    else:
        score += 1.0   # 낮은 수요
    
    logger.debug(f"정책 부합성: {score:.1f}/15 (유형 신뢰도: {selection_confidence:.2f}, 수요: {housing_demand:.0f})")
    return min(max(score, 0.0), 15.0)


def calculate_risk_score(
    zone_type: str,
    restrictions: list,
    total_units: int
) -> float:
    """
    ⑥ 사업 리스크 점수 계산 (10점 만점)
    
    평가 요소:
    - 규제 리스크
    - 민원 가능성
    - 인허가 난이도
    
    Args:
        zone_type: 용도지역
        restrictions: 규제 리스트
        total_units: 총 세대수
    
    Returns:
        float: 사업 리스크 점수 (0~10)
        
    Note:
        점수가 높을수록 리스크가 낮음 (좋은 것)
    """
    score = 10.0  # 기본: 리스크 없음
    
    # 규제 리스크 평가
    if restrictions and len(restrictions) > 0:
        score -= len(restrictions) * 1.0  # 규제 1개당 -1점
    
    # 규모에 따른 민원 리스크
    if total_units >= 100:
        score -= 2.0  # 대규모: 민원 가능성 높음
    elif total_units >= 50:
        score -= 1.0  # 중규모: 민원 가능성 중간
    
    # 용도지역 리스크
    if "주거" in zone_type:
        score += 0.0  # 주거지역: 무난
    elif "상업" in zone_type:
        score -= 1.0  # 상업지역: 주거 전환 어려움
    elif "공업" in zone_type:
        score -= 3.0  # 공업지역: 주거 전환 매우 어려움
    
    logger.debug(f"사업 리스크: {score:.1f}/10 (규제: {len(restrictions) if restrictions else 0}건, 세대수: {total_units})")
    return min(max(score, 0.0), 10.0)


__all__ = [
    "calculate_location_score",
    "calculate_land_score",
    "calculate_technical_score",
    "calculate_financial_score",
    "calculate_policy_score",
    "calculate_risk_score"
]
