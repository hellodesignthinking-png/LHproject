"""
ZeroSite v24.1 - Unit Type Engine
청년/신혼/고령 등 5종 유닛타입 평가 엔진

Author: ZeroSite Development Team
Version: 24.1.0
Created: 2025-12-12
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class UnitType(Enum):
    """LH 공식 유닛타입 5종"""
    YOUTH = "청년"  # 30㎡ (9평)
    NEWLYWED_I = "신혼·신생아 I"  # 45㎡ (14평)
    NEWLYWED_II = "신혼·신생아 II"  # 55㎡ (17평)
    MULTI_CHILD = "다자녀"  # 65㎡ (20평)
    ELDERLY = "고령자"  # 40㎡ (12평)


@dataclass
class UnitTypeSpec:
    """유닛타입 사양"""
    type_name: str
    area_sqm: float
    area_pyeong: float
    target_household: str
    monthly_rent_range: tuple  # (min, max) KRW
    lh_priority_score: float  # 0-100
    market_demand_score: float  # 0-100
    construction_efficiency: float  # 0-100


@dataclass
class UnitTypeEvaluation:
    """유닛타입 평가 결과"""
    unit_type: str
    
    # 평가 점수 (0-100)
    location_suitability: float  # 입지 적합성
    target_demand: float  # 수요층 존재
    policy_alignment: float  # 정책 부합도
    financial_viability: float  # 재무 타당성
    construction_feasibility: float  # 시공 용이성
    
    # 종합 점수
    total_score: float
    rank: str  # S, A, B, C, D
    
    # 예상 수요
    estimated_applications: int  # 예상 신청자 수
    competition_ratio: float  # 예상 경쟁률
    
    # 재무 지표
    estimated_monthly_rent: int  # 예상 월세 (원)
    estimated_deposit: int  # 예상 보증금 (원)
    lh_purchase_price_per_unit: int  # LH 매입가/세대 (원)
    
    # 추천 사항
    recommended: bool
    recommendation_notes: List[str]
    risk_factors: List[str]


@dataclass
class UnitMixResult:
    """유닛믹스 최적화 결과"""
    total_units: int
    
    # 유닛타입별 배분
    youth_units: int
    youth_percentage: float
    
    newlywed_i_units: int
    newlywed_i_percentage: float
    
    newlywed_ii_units: int
    newlywed_ii_percentage: float
    
    multi_child_units: int
    multi_child_percentage: float
    
    elderly_units: int
    elderly_percentage: float
    
    # 종합 평가
    policy_score: float  # 정책 부합도 (0-100)
    market_score: float  # 시장 수요 부합도 (0-100)
    financial_score: float  # 재무 안정성 (0-100)
    overall_score: float  # 종합 점수
    
    # 예상 수익
    total_revenue: int  # 총 예상 수익 (원)
    average_rent_per_unit: int  # 평균 월세/세대
    
    # 추천 여부
    recommended_mix: bool
    optimization_notes: List[str]


class UnitTypeEngineV241:
    """
    유닛타입 평가 및 최적 믹스 도출 엔진
    
    기능:
    1. 5가지 유닛타입별 평가 (청년/신혼I/신혼II/다자녀/고령)
    2. 입지 특성에 따른 적합도 분석
    3. 최적 유닛믹스 도출
    4. LH 정책 부합도 평가
    """
    
    def __init__(self):
        """엔진 초기화"""
        # LH 공식 유닛타입 사양
        self.unit_specs = {
            UnitType.YOUTH: UnitTypeSpec(
                type_name="청년",
                area_sqm=30.0,
                area_pyeong=9.0,
                target_household="만 19-39세 무주택 청년",
                monthly_rent_range=(200000, 350000),
                lh_priority_score=90.0,
                market_demand_score=95.0,
                construction_efficiency=95.0
            ),
            UnitType.NEWLYWED_I: UnitTypeSpec(
                type_name="신혼·신생아 I",
                area_sqm=45.0,
                area_pyeong=14.0,
                target_household="신혼부부, 예비 신혼부부",
                monthly_rent_range=(300000, 500000),
                lh_priority_score=95.0,
                market_demand_score=90.0,
                construction_efficiency=90.0
            ),
            UnitType.NEWLYWED_II: UnitTypeSpec(
                type_name="신혼·신생아 II",
                area_sqm=55.0,
                area_pyeong=17.0,
                target_household="신혼부부 (자녀 1-2명)",
                monthly_rent_range=(400000, 650000),
                lh_priority_score=85.0,
                market_demand_score=85.0,
                construction_efficiency=85.0
            ),
            UnitType.MULTI_CHILD: UnitTypeSpec(
                type_name="다자녀",
                area_sqm=65.0,
                area_pyeong=20.0,
                target_household="자녀 3명 이상 가구",
                monthly_rent_range=(450000, 750000),
                lh_priority_score=80.0,
                market_demand_score=60.0,
                construction_efficiency=75.0
            ),
            UnitType.ELDERLY: UnitTypeSpec(
                type_name="고령자",
                area_sqm=40.0,
                area_pyeong=12.0,
                target_household="만 65세 이상 고령자",
                monthly_rent_range=(250000, 400000),
                lh_priority_score=75.0,
                market_demand_score=70.0,
                construction_efficiency=80.0
            )
        }
    
    def evaluate_unit_type(
        self,
        unit_type: UnitType,
        location_type: str,  # "도심", "부도심", "외곽"
        nearby_facilities: Dict[str, int],  # {"학교": 3, "병원": 2, "지하철": 1}
        land_price_per_sqm: float,
        total_units: int
    ) -> UnitTypeEvaluation:
        """
        특정 유닛타입 평가
        
        Args:
            unit_type: 평가할 유닛타입
            location_type: 입지 유형
            nearby_facilities: 인근 편의시설 수
            land_price_per_sqm: 토지 단가 (원/㎡)
            total_units: 총 세대수
        
        Returns:
            UnitTypeEvaluation: 평가 결과
        """
        spec = self.unit_specs[unit_type]
        
        # 1. 입지 적합성 평가 (0-100)
        location_suitability = self._evaluate_location_suitability(
            unit_type, location_type, nearby_facilities
        )
        
        # 2. 수요층 존재도 평가
        target_demand = self._evaluate_target_demand(
            unit_type, location_type
        )
        
        # 3. 정책 부합도 (LH 우선순위)
        policy_alignment = spec.lh_priority_score
        
        # 4. 재무 타당성
        financial_viability = self._evaluate_financial_viability(
            spec, land_price_per_sqm, total_units
        )
        
        # 5. 시공 용이성
        construction_feasibility = spec.construction_efficiency
        
        # 종합 점수 계산 (가중평균)
        total_score = (
            location_suitability * 0.25 +
            target_demand * 0.20 +
            policy_alignment * 0.25 +
            financial_viability * 0.20 +
            construction_feasibility * 0.10
        )
        
        # 등급 부여
        if total_score >= 90:
            rank = "S"
        elif total_score >= 80:
            rank = "A"
        elif total_score >= 70:
            rank = "B"
        elif total_score >= 60:
            rank = "C"
        else:
            rank = "D"
        
        # 예상 수요 계산
        estimated_applications = int(total_units * (target_demand / 100) * 5)
        competition_ratio = estimated_applications / max(1, total_units)
        
        # 예상 임대료
        avg_rent = sum(spec.monthly_rent_range) // 2
        estimated_monthly_rent = avg_rent
        estimated_deposit = avg_rent * 10
        
        # LH 매입가 추정 (건축비 + 토지비)
        construction_cost_per_sqm = 2500000  # 평균 건축비 250만원/㎡
        lh_purchase_price = int(
            (spec.area_sqm * construction_cost_per_sqm) +
            (land_price_per_sqm * spec.area_sqm * 0.3)
        )
        
        # 추천 여부 및 노트
        recommended = total_score >= 70
        recommendation_notes = []
        risk_factors = []
        
        if total_score >= 80:
            recommendation_notes.append("적극 추천: 입지 및 수요 조건이 우수함")
        elif total_score >= 70:
            recommendation_notes.append("추천: 전반적으로 양호한 조건")
        elif total_score >= 60:
            recommendation_notes.append("조건부 추천: 일부 개선 필요")
        else:
            recommendation_notes.append("비추천: 조건 미흡")
            risk_factors.append("입지 또는 수요 조건 부족")
        
        if location_suitability < 60:
            risk_factors.append("입지 적합성 낮음")
        
        if target_demand < 60:
            risk_factors.append("수요층 부족 우려")
        
        return UnitTypeEvaluation(
            unit_type=spec.type_name,
            location_suitability=location_suitability,
            target_demand=target_demand,
            policy_alignment=policy_alignment,
            financial_viability=financial_viability,
            construction_feasibility=construction_feasibility,
            total_score=total_score,
            rank=rank,
            estimated_applications=estimated_applications,
            competition_ratio=competition_ratio,
            estimated_monthly_rent=estimated_monthly_rent,
            estimated_deposit=estimated_deposit,
            lh_purchase_price_per_unit=lh_purchase_price,
            recommended=recommended,
            recommendation_notes=recommendation_notes,
            risk_factors=risk_factors
        )
    
    def optimize_unit_mix(
        self,
        total_units: int,
        location_type: str,
        nearby_facilities: Dict[str, int],
        land_price_per_sqm: float,
        policy_priority: str = "balanced"  # "youth", "newlywed", "elderly", "balanced"
    ) -> UnitMixResult:
        """
        최적 유닛믹스 도출
        
        Args:
            total_units: 총 세대수
            location_type: 입지 유형
            nearby_facilities: 인근 편의시설
            land_price_per_sqm: 토지 단가
            policy_priority: 정책 우선순위
        
        Returns:
            UnitMixResult: 최적 믹스 결과
        """
        
        # 각 유닛타입 평가
        evaluations = {}
        for unit_type in UnitType:
            evaluations[unit_type] = self.evaluate_unit_type(
                unit_type, location_type, nearby_facilities, 
                land_price_per_sqm, total_units
            )
        
        # 정책 우선순위에 따른 배분
        if policy_priority == "youth":
            mix = {"youth": 0.50, "newlywed_i": 0.30, "newlywed_ii": 0.10, "multi_child": 0.05, "elderly": 0.05}
        elif policy_priority == "newlywed":
            mix = {"youth": 0.25, "newlywed_i": 0.40, "newlywed_ii": 0.25, "multi_child": 0.05, "elderly": 0.05}
        elif policy_priority == "elderly":
            mix = {"youth": 0.20, "newlywed_i": 0.25, "newlywed_ii": 0.20, "multi_child": 0.05, "elderly": 0.30}
        else:  # balanced
            mix = {"youth": 0.35, "newlywed_i": 0.30, "newlywed_ii": 0.20, "multi_child": 0.08, "elderly": 0.07}
        
        # 세대수 계산
        youth_units = int(total_units * mix["youth"])
        newlywed_i_units = int(total_units * mix["newlywed_i"])
        newlywed_ii_units = int(total_units * mix["newlywed_ii"])
        multi_child_units = int(total_units * mix["multi_child"])
        elderly_units = total_units - (youth_units + newlywed_i_units + newlywed_ii_units + multi_child_units)
        
        # 종합 점수 계산
        policy_score = (
            evaluations[UnitType.YOUTH].policy_alignment * mix["youth"] +
            evaluations[UnitType.NEWLYWED_I].policy_alignment * mix["newlywed_i"] +
            evaluations[UnitType.NEWLYWED_II].policy_alignment * mix["newlywed_ii"] +
            evaluations[UnitType.MULTI_CHILD].policy_alignment * mix["multi_child"] +
            evaluations[UnitType.ELDERLY].policy_alignment * mix["elderly"]
        )
        
        market_score = (
            evaluations[UnitType.YOUTH].target_demand * mix["youth"] +
            evaluations[UnitType.NEWLYWED_I].target_demand * mix["newlywed_i"] +
            evaluations[UnitType.NEWLYWED_II].target_demand * mix["newlywed_ii"] +
            evaluations[UnitType.MULTI_CHILD].target_demand * mix["multi_child"] +
            evaluations[UnitType.ELDERLY].target_demand * mix["elderly"]
        )
        
        financial_score = (
            evaluations[UnitType.YOUTH].financial_viability * mix["youth"] +
            evaluations[UnitType.NEWLYWED_I].financial_viability * mix["newlywed_i"] +
            evaluations[UnitType.NEWLYWED_II].financial_viability * mix["newlywed_ii"] +
            evaluations[UnitType.MULTI_CHILD].financial_viability * mix["multi_child"] +
            evaluations[UnitType.ELDERLY].financial_viability * mix["elderly"]
        )
        
        overall_score = (policy_score + market_score + financial_score) / 3
        
        # 총 수익 추정
        total_revenue = (
            evaluations[UnitType.YOUTH].estimated_monthly_rent * youth_units +
            evaluations[UnitType.NEWLYWED_I].estimated_monthly_rent * newlywed_i_units +
            evaluations[UnitType.NEWLYWED_II].estimated_monthly_rent * newlywed_ii_units +
            evaluations[UnitType.MULTI_CHILD].estimated_monthly_rent * multi_child_units +
            evaluations[UnitType.ELDERLY].estimated_monthly_rent * elderly_units
        ) * 12 * 20  # 20년
        
        average_rent_per_unit = total_revenue // (total_units * 12 * 20)
        
        recommended_mix = overall_score >= 70
        
        optimization_notes = []
        if overall_score >= 80:
            optimization_notes.append("우수한 유닛믹스 구성")
        elif overall_score >= 70:
            optimization_notes.append("양호한 유닛믹스 구성")
        else:
            optimization_notes.append("유닛믹스 재검토 권장")
        
        optimization_notes.append(f"정책 우선순위: {policy_priority}")
        optimization_notes.append(f"청년형 비중: {mix['youth']*100:.0f}%")
        
        return UnitMixResult(
            total_units=total_units,
            youth_units=youth_units,
            youth_percentage=mix["youth"] * 100,
            newlywed_i_units=newlywed_i_units,
            newlywed_i_percentage=mix["newlywed_i"] * 100,
            newlywed_ii_units=newlywed_ii_units,
            newlywed_ii_percentage=mix["newlywed_ii"] * 100,
            multi_child_units=multi_child_units,
            multi_child_percentage=mix["multi_child"] * 100,
            elderly_units=elderly_units,
            elderly_percentage=(elderly_units / total_units) * 100,
            policy_score=policy_score,
            market_score=market_score,
            financial_score=financial_score,
            overall_score=overall_score,
            total_revenue=total_revenue,
            average_rent_per_unit=average_rent_per_unit,
            recommended_mix=recommended_mix,
            optimization_notes=optimization_notes
        )
    
    def _evaluate_location_suitability(
        self, 
        unit_type: UnitType, 
        location_type: str, 
        nearby_facilities: Dict[str, int]
    ) -> float:
        """입지 적합성 평가"""
        base_score = {
            "도심": 90,
            "부도심": 80,
            "외곽": 60
        }.get(location_type, 70)
        
        # 편의시설 가점
        facility_bonus = sum(nearby_facilities.values()) * 2
        
        return min(100, base_score + facility_bonus)
    
    def _evaluate_target_demand(self, unit_type: UnitType, location_type: str) -> float:
        """수요층 존재도 평가"""
        # 입지별 유닛타입 수요 매트릭스
        demand_matrix = {
            UnitType.YOUTH: {"도심": 95, "부도심": 85, "외곽": 60},
            UnitType.NEWLYWED_I: {"도심": 90, "부도심": 90, "외곽": 70},
            UnitType.NEWLYWED_II: {"도심": 80, "부도심": 85, "외곽": 75},
            UnitType.MULTI_CHILD: {"도심": 60, "부도심": 70, "외곽": 80},
            UnitType.ELDERLY: {"도심": 70, "부도심": 75, "외곽": 65}
        }
        
        return demand_matrix[unit_type].get(location_type, 70)
    
    def _evaluate_financial_viability(
        self, 
        spec: UnitTypeSpec, 
        land_price_per_sqm: float, 
        total_units: int
    ) -> float:
        """재무 타당성 평가"""
        construction_cost = spec.area_sqm * 2500000
        land_cost = spec.area_sqm * land_price_per_sqm * 0.3
        total_cost = construction_cost + land_cost
        
        monthly_rent = sum(spec.monthly_rent_range) // 2
        annual_revenue = monthly_rent * 12
        
        # ROI 계산
        roi = (annual_revenue * 20) / total_cost
        
        if roi > 1.5:
            return 95
        elif roi > 1.2:
            return 85
        elif roi > 1.0:
            return 75
        elif roi > 0.8:
            return 65
        else:
            return 50


# 테스트 코드
if __name__ == "__main__":
    engine = UnitTypeEngineV241()
    
    # 유닛믹스 최적화 테스트
    result = engine.optimize_unit_mix(
        total_units=100,
        location_type="부도심",
        nearby_facilities={"학교": 3, "병원": 2, "지하철": 1, "마트": 2},
        land_price_per_sqm=3000000,
        policy_priority="balanced"
    )
    
    print("=" * 60)
    print("유닛믹스 최적화 결과")
    print("=" * 60)
    print(f"총 세대수: {result.total_units}")
    print(f"\n유닛타입별 배분:")
    print(f"  청년형: {result.youth_units}세대 ({result.youth_percentage:.1f}%)")
    print(f"  신혼I: {result.newlywed_i_units}세대 ({result.newlywed_i_percentage:.1f}%)")
    print(f"  신혼II: {result.newlywed_ii_units}세대 ({result.newlywed_ii_percentage:.1f}%)")
    print(f"  다자녀: {result.multi_child_units}세대 ({result.multi_child_percentage:.1f}%)")
    print(f"  고령자: {result.elderly_units}세대 ({result.elderly_percentage:.1f}%)")
    print(f"\n종합 평가:")
    print(f"  정책 점수: {result.policy_score:.1f}")
    print(f"  시장 점수: {result.market_score:.1f}")
    print(f"  재무 점수: {result.financial_score:.1f}")
    print(f"  종합 점수: {result.overall_score:.1f}")
    print(f"\n예상 수익:")
    print(f"  총 수익 (20년): {result.total_revenue:,}원")
    print(f"  평균 월세/세대: {result.average_rent_per_unit:,}원")
    print(f"\n추천 여부: {'✅ 추천' if result.recommended_mix else '❌ 비추천'}")
    print(f"\n최적화 노트:")
    for note in result.optimization_notes:
        print(f"  - {note}")
