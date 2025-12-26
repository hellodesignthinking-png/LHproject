"""
M6 Section Score Calculators (ZeroSite 4.0 FIX)
================================================

LH 100점 평가표의 5개 섹션 점수 계산

⚠️ FIX 규칙:
- 각 섹션의 배점 고정
- 즉시 탈락 조건 변경 금지
- 감점 기준 고정

Author: ZeroSite M6 Team
Date: 2025-12-26
"""

import logging
from typing import Dict, Tuple, List

logger = logging.getLogger(__name__)


def calculate_section_a_policy(
    housing_type_ctx,
    land_ctx
) -> Tuple[float, Dict[str, float], bool, List[str]]:
    """
    [A] 정책·유형 적합성 (25점)
    
    항목:
    - 지역별 공급 필요도: 10점
    - 세대유형 적합성: 10점
    - 정책 우선 대상 여부: 5점
    
    즉시 탈락:
    - 공급 제한 지역 + 비우선 유형
    
    Returns:
        (total_score, item_scores, fatal_reject, reject_reasons)
    """
    items = {}
    fatal_reject = False
    reject_reasons = []
    
    # 1. 지역별 공급 필요도 (10점)
    demand = housing_type_ctx.demand_prediction  # 0~100
    supply_need_score = (demand / 100.0) * 10.0
    items["지역별 공급 필요도"] = supply_need_score
    
    # 2. 세대유형 적합성 (10점)
    confidence = housing_type_ctx.selection_confidence  # 0~1
    type_fit_score = confidence * 10.0
    items["세대유형 적합성"] = type_fit_score
    
    # 3. 정책 우선 대상 여부 (5점)
    # 신혼·청년·고령 유형은 우선
    priority_types = ["youth", "newlywed_1", "newlywed_2", "senior"]
    if housing_type_ctx.selected_type in priority_types:
        priority_score = 5.0
    else:
        priority_score = 3.0
    items["정책 우선 대상"] = priority_score
    
    # 즉시 탈락 체크: 공급 제한 + 비우선
    if demand < 30 and housing_type_ctx.selected_type not in priority_types:
        fatal_reject = True
        reject_reasons.append("공급 제한 지역 + 비우선 유형")
    
    total = supply_need_score + type_fit_score + priority_score
    
    logger.debug(f"[A] 정책·유형: {total:.1f}/25 (수요 {supply_need_score:.1f}, 유형 {type_fit_score:.1f}, 우선 {priority_score:.1f})")
    
    return total, items, fatal_reject, reject_reasons


def calculate_section_b_location(
    land_ctx,
    housing_type_ctx
) -> Tuple[float, Dict[str, float], bool, List[str]]:
    """
    [B] 입지·환경 평가 (20점)
    
    항목:
    - 교통 접근성: 6점
    - 생활 인프라: 6점
    - 민원/혐오시설 리스크: 8점
    
    즉시 탈락:
    - 학교/주거 부적합 시설 인접
    
    Returns:
        (total_score, item_scores, fatal_reject, reject_reasons)
    """
    items = {}
    fatal_reject = False
    reject_reasons = []
    
    # 1. 교통 접근성 (6점)
    if housing_type_ctx.poi_analysis:
        subway_dist = housing_type_ctx.poi_analysis.subway_distance
        if subway_dist <= 500:
            transport_score = 6.0  # 역세권
        elif subway_dist <= 1000:
            transport_score = 4.5  # 준역세권
        elif subway_dist <= 2000:
            transport_score = 3.0  # 도보 가능
        else:
            transport_score = 1.5  # 버스 이용
    else:
        transport_score = 3.0  # 정보 없음 (중간값)
    items["교통 접근성"] = transport_score
    
    # 2. 생활 인프라 (6점)
    if housing_type_ctx.poi_analysis:
        poi = housing_type_ctx.poi_analysis
        infra_score = 0.0
        
        # 학교 (2점)
        if poi.school_distance <= 500:
            infra_score += 2.0
        elif poi.school_distance <= 1000:
            infra_score += 1.5
        else:
            infra_score += 1.0
        
        # 병원 (2점)
        if poi.hospital_distance <= 1000:
            infra_score += 2.0
        elif poi.hospital_distance <= 2000:
            infra_score += 1.5
        else:
            infra_score += 1.0
        
        # 상업시설 (2점)
        if poi.commercial_distance <= 500:
            infra_score += 2.0
        elif poi.commercial_distance <= 1000:
            infra_score += 1.5
        else:
            infra_score += 1.0
    else:
        infra_score = 3.0  # 정보 없음
    items["생활 인프라"] = infra_score
    
    # 3. 민원/혐오시설 리스크 (8점)
    # 기본 만점, 문제 발견 시 감점
    risk_score = 8.0
    
    # 용도지역 체크
    if "공업" in land_ctx.zone_type:
        risk_score -= 3.0  # 공업지역 주거 부적합
    
    # 규제 체크
    if land_ctx.restrictions and len(land_ctx.restrictions) > 0:
        risk_score -= min(len(land_ctx.restrictions) * 0.5, 2.0)
    
    items["민원/혐오시설 리스크"] = max(risk_score, 0.0)
    
    # 즉시 탈락 체크
    if "공업" in land_ctx.zone_type or "위험" in str(land_ctx.restrictions):
        fatal_reject = True
        reject_reasons.append("학교/주거 부적합 시설 인접")
    
    total = transport_score + infra_score + max(risk_score, 0.0)
    
    logger.debug(f"[B] 입지·환경: {total:.1f}/20 (교통 {transport_score:.1f}, 인프라 {infra_score:.1f}, 리스크 {risk_score:.1f})")
    
    return total, items, fatal_reject, reject_reasons


def calculate_section_c_construction(
    capacity_ctx,
    land_ctx
) -> Tuple[float, Dict[str, float], bool, List[str]]:
    """
    [C] 건축 가능성 (20점)
    
    항목:
    - 세대수 확보 가능성: 8점
    - 주차 충족률: 6점
    - 구조·법규 리스크: 6점
    
    즉시 탈락:
    - 주차 법정 기준 미달
    - 구조적 불가 (일조/도로)
    
    Returns:
        (total_score, item_scores, fatal_reject, reject_reasons)
    """
    items = {}
    fatal_reject = False
    reject_reasons = []
    
    # Extract capacity data
    if hasattr(capacity_ctx, 'incentive_capacity'):  # V2
        total_units = capacity_ctx.incentive_capacity.total_units
        required_parking = capacity_ctx.incentive_capacity.required_parking_spaces
        gfa = capacity_ctx.incentive_capacity.target_gfa_sqm
    else:  # V1
        total_units = capacity_ctx.unit_plan.recommended_units
        required_parking = 0  # V1 doesn't have this
        gfa = 0
    
    # 1. 세대수 확보 가능성 (8점)
    if total_units >= 50:
        unit_score = 8.0  # 적정 규모
    elif total_units >= 30:
        unit_score = 6.0  # 소규모
    elif total_units >= 20:
        unit_score = 4.0  # 매우 소규모
    else:
        unit_score = 2.0  # 사업성 의문
    items["세대수 확보"] = unit_score
    
    # 2. 주차 충족률 (6점)
    # 법정 기준: 세대당 1대 (일반적)
    if required_parking >= total_units:
        parking_score = 6.0  # 충족
    elif required_parking >= total_units * 0.8:
        parking_score = 4.5  # 80% 이상
    elif required_parking >= total_units * 0.6:
        parking_score = 3.0  # 60% 이상
    else:
        parking_score = 0.0  # 미달
        fatal_reject = True
        reject_reasons.append("주차 법정 기준 미달")
    items["주차 충족률"] = parking_score
    
    # 3. 구조·법규 리스크 (6점)
    structure_score = 6.0  # 기본 만점
    
    # FAR/BCR 체크
    if land_ctx.far <= 0 or land_ctx.bcr <= 0:
        structure_score -= 2.0  # 정보 불완전
    
    # 도로 체크
    if land_ctx.road_width < 4.0:
        structure_score -= 2.0  # 도로 협소
        if land_ctx.road_width < 3.0:
            fatal_reject = True
            reject_reasons.append("도로 기준 미달 (구조적 불가)")
    
    items["구조·법규 리스크"] = max(structure_score, 0.0)
    
    total = unit_score + parking_score + max(structure_score, 0.0)
    
    logger.debug(f"[C] 건축: {total:.1f}/20 (세대 {unit_score:.1f}, 주차 {parking_score:.1f}, 구조 {structure_score:.1f})")
    
    return total, items, fatal_reject, reject_reasons


def calculate_section_d_price(
    appraisal_ctx,
    land_ctx
) -> Tuple[float, Dict[str, float], List[str]]:
    """
    [D] 가격·매입 적정성 (15점)
    
    항목:
    - LH 기준 매입가 부합: 10점
    - 인근 거래 대비 안정성: 5점
    
    감점:
    - 매입가 상한 초과 가능성: -5 ~ -15
    
    Returns:
        (total_score, item_scores, deduction_reasons)
    """
    items = {}
    deductions = []
    
    # 1. LH 기준 매입가 부합 (10점)
    # LH 기준: 평당 3,000만원 내외 (서울 기준)
    price_per_py = appraisal_ctx.unit_price_pyeong
    
    if price_per_py <= 30_000_000:
        purchase_score = 10.0  # 기준 내
    elif price_per_py <= 35_000_000:
        purchase_score = 8.0   # 약간 초과
        deductions.append("매입가 기준 약간 초과 (-2)")
    elif price_per_py <= 40_000_000:
        purchase_score = 5.0   # 상당 초과
        deductions.append("매입가 기준 상당 초과 (-5)")
    else:
        purchase_score = 0.0   # 크게 초과
        deductions.append("매입가 기준 크게 초과 (-10)")
    items["LH 기준 매입가"] = purchase_score
    
    # 2. 인근 거래 대비 안정성 (5점)
    confidence = appraisal_ctx.confidence_score
    if confidence >= 0.8:
        stability_score = 5.0  # 높은 신뢰도
    elif confidence >= 0.6:
        stability_score = 4.0  # 중간 신뢰도
    else:
        stability_score = 2.0  # 낮은 신뢰도
        deductions.append("거래 사례 부족 (-1)")
    items["거래 안정성"] = stability_score
    
    total = purchase_score + stability_score
    
    logger.debug(f"[D] 가격: {total:.1f}/15 (매입가 {purchase_score:.1f}, 안정성 {stability_score:.1f})")
    
    return total, items, deductions


def calculate_section_e_business(
    feasibility_ctx
) -> Tuple[float, Dict[str, float], bool, List[str]]:
    """
    [E] 사업성 (20점)
    
    항목:
    - 손익 구조: 10점
    - 사업 리스크: 5점
    - 실행 가능성: 5점
    
    즉시 탈락:
    - 구조적 적자 고정
    
    Returns:
        (total_score, item_scores, fatal_reject, reject_reasons)
    """
    items = {}
    fatal_reject = False
    reject_reasons = []
    
    # 1. 손익 구조 (10점)
    npv = feasibility_ctx.financial_metrics.npv_public
    irr = feasibility_ctx.financial_metrics.irr_public
    
    if npv > 0 and irr >= 12.0:
        profit_score = 10.0  # 우수
    elif npv > -500_000_000 and irr >= 8.0:
        profit_score = 7.0   # 양호
    elif npv > -1_000_000_000:
        profit_score = 4.0   # 보통
    else:
        profit_score = 0.0   # 불량
        fatal_reject = True
        reject_reasons.append("구조적 적자 고정")
    items["손익 구조"] = profit_score
    
    # 2. 사업 리스크 (5점)
    # IRR 기반 리스크 평가
    if irr >= 15.0:
        risk_score = 5.0  # 낮음
    elif irr >= 10.0:
        risk_score = 4.0  # 보통
    elif irr >= 5.0:
        risk_score = 2.0  # 높음
    else:
        risk_score = 0.0  # 매우 높음
    items["사업 리스크"] = risk_score
    
    # 3. 실행 가능성 (5점)
    # Profitability grade 기반
    grade = feasibility_ctx.profitability_grade
    if grade in ["S", "A"]:
        exec_score = 5.0
    elif grade in ["B", "C"]:
        exec_score = 3.0
    elif grade == "D":
        exec_score = 1.0
    else:  # F
        exec_score = 0.0
    items["실행 가능성"] = exec_score
    
    total = profit_score + risk_score + exec_score
    
    logger.debug(f"[E] 사업성: {total:.1f}/20 (손익 {profit_score:.1f}, 리스크 {risk_score:.1f}, 실행 {exec_score:.1f})")
    
    return total, items, fatal_reject, reject_reasons


__all__ = [
    "calculate_section_a_policy",
    "calculate_section_b_location",
    "calculate_section_c_construction",
    "calculate_section_d_price",
    "calculate_section_e_business"
]
