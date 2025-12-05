"""
ZeroSite v11.0 - LH Score Mapper Engine
========================================
LH 신축매입임대 평가 기준을 100점 만점으로 수치화하는 핵심 엔진

평가 항목 (100점 만점):
1. 입지 적합성 (Location) - 25점
   - 교통 접근성: 10점
   - 생활 편의성: 8점
   - 교육 환경: 7점

2. 사업 타당성 (Feasibility) - 30점
   - 용적률/건폐율 적정성: 10점
   - 세대수 적정성: 8점
   - 토지 가격 적정성: 12점

3. 정책 정합성 (Policy Alignment) - 20점
   - 용도지역 적합성: 8점
   - 주택 정책 부합도: 7점
   - 공급 유형 적합성: 5점

4. 재무 건전성 (Financial Health) - 15점
   - IRR/ROI 수준: 8점
   - 투자 회수 기간: 4점
   - 자금 조달 가능성: 3점

5. 리스크 수준 (Risk Level) - 10점
   - 법규 리스크: 4점
   - 시장 리스크: 3점
   - 시공 리스크: 3점
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum


class LHGrade(Enum):
    """LH 평가 등급"""
    A = "A"  # 90점 이상 - 최우수
    B = "B"  # 80-89점 - 우수
    C = "C"  # 70-79점 - 양호
    D = "D"  # 60-69점 - 보통
    F = "F"  # 60점 미만 - 부적합


@dataclass
class LHScoreBreakdown:
    """LH 점수 세부 항목"""
    # 입지 적합성 (25점)
    location_total: float
    transportation_access: float  # 10점
    living_convenience: float  # 8점
    education_environment: float  # 7점
    
    # 사업 타당성 (30점)
    feasibility_total: float
    far_bcr_adequacy: float  # 10점
    unit_count_adequacy: float  # 8점
    land_price_adequacy: float  # 12점
    
    # 정책 정합성 (20점)
    policy_total: float
    zone_suitability: float  # 8점
    housing_policy_alignment: float  # 7점
    unit_type_suitability: float  # 5점
    
    # 재무 건전성 (15점)
    financial_total: float
    irr_roi_level: float  # 8점
    payback_period: float  # 4점
    financing_feasibility: float  # 3점
    
    # 리스크 수준 (10점)
    risk_total: float
    legal_risk: float  # 4점
    market_risk: float  # 3점
    construction_risk: float  # 3점
    
    # 총점
    total_score: float
    grade: LHGrade
    
    # 세부 설명
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


class LHScoreMapper:
    """LH 평가 점수 계산 엔진"""
    
    def __init__(self):
        self.max_scores = {
            "location": 25,
            "feasibility": 30,
            "policy": 20,
            "financial": 15,
            "risk": 10
        }
    
    def calculate_lh_score(self, 
                          analysis_result: Dict[str, Any],
                          unit_analysis: Dict[str, Any],
                          pseudo_data: Dict[str, Any]) -> LHScoreBreakdown:
        """
        종합 LH 점수 계산
        
        Args:
            analysis_result: v9.1 분석 결과
            unit_analysis: v11.0 세대유형 분석 결과
            pseudo_data: v11.0 Pseudo-Data 엔진 결과
            
        Returns:
            LHScoreBreakdown: 세부 점수 및 등급
        """
        
        # 1. 입지 적합성 (25점)
        location_scores = self._calculate_location_score(analysis_result, pseudo_data)
        
        # 2. 사업 타당성 (30점)
        feasibility_scores = self._calculate_feasibility_score(analysis_result)
        
        # 3. 정책 정합성 (20점)
        policy_scores = self._calculate_policy_score(analysis_result, unit_analysis)
        
        # 4. 재무 건전성 (15점)
        financial_scores = self._calculate_financial_score(analysis_result)
        
        # 5. 리스크 수준 (10점)
        risk_scores = self._calculate_risk_score(analysis_result)
        
        # 총점 계산
        total_score = (
            location_scores["total"] +
            feasibility_scores["total"] +
            policy_scores["total"] +
            financial_scores["total"] +
            risk_scores["total"]
        )
        
        # 등급 계산
        grade = self._calculate_grade(total_score)
        
        # 강점/약점/개선사항 분석
        strengths = self._identify_strengths(location_scores, feasibility_scores, 
                                             policy_scores, financial_scores, risk_scores)
        weaknesses = self._identify_weaknesses(location_scores, feasibility_scores,
                                               policy_scores, financial_scores, risk_scores)
        recommendations = self._generate_recommendations(weaknesses, total_score)
        
        return LHScoreBreakdown(
            # Location (25점)
            location_total=location_scores["total"],
            transportation_access=location_scores["transportation"],
            living_convenience=location_scores["convenience"],
            education_environment=location_scores["education"],
            
            # Feasibility (30점)
            feasibility_total=feasibility_scores["total"],
            far_bcr_adequacy=feasibility_scores["far_bcr"],
            unit_count_adequacy=feasibility_scores["unit_count"],
            land_price_adequacy=feasibility_scores["land_price"],
            
            # Policy (20점)
            policy_total=policy_scores["total"],
            zone_suitability=policy_scores["zone"],
            housing_policy_alignment=policy_scores["housing_policy"],
            unit_type_suitability=policy_scores["unit_type"],
            
            # Financial (15점)
            financial_total=financial_scores["total"],
            irr_roi_level=financial_scores["irr_roi"],
            payback_period=financial_scores["payback"],
            financing_feasibility=financial_scores["financing"],
            
            # Risk (10점)
            risk_total=risk_scores["total"],
            legal_risk=risk_scores["legal"],
            market_risk=risk_scores["market"],
            construction_risk=risk_scores["construction"],
            
            # Total
            total_score=total_score,
            grade=grade,
            
            # Analysis
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )
    
    # ============================================================
    # 1. 입지 적합성 (25점)
    # ============================================================
    
    def _calculate_location_score(self, analysis_result: Dict, pseudo_data: Dict) -> Dict[str, float]:
        """입지 적합성 점수 계산"""
        
        # 1.1 교통 접근성 (10점)
        transport = pseudo_data.get("transportation", {})
        subway_lines = len(transport.get("subway", {}).get("lines", []))
        bus_routes = transport.get("bus", {}).get("total_routes", 0)
        
        # 지하철: 2개 이상 = 만점, 1개 = 7점, 0개 = 3점
        subway_score = min(subway_lines * 5, 6)
        if subway_lines == 0:
            subway_score = 3
        
        # 버스: 20개 이상 = 만점, 선형 계산
        bus_score = min(bus_routes / 20 * 4, 4)
        
        transportation_score = min(subway_score + bus_score, 10)
        
        # 1.2 생활 편의성 (8점)
        convenience = pseudo_data.get("convenience", {})
        
        # 대형마트
        marts = convenience.get("shopping", {}).get("large_marts", {}).get("count", 0)
        mart_score = min(marts * 2, 3)
        
        # 편의점
        stores = convenience.get("shopping", {}).get("convenience_stores", {}).get("count", 0)
        store_score = min(stores / 30 * 2, 2)
        
        # 음식점/카페
        restaurants = convenience.get("dining", {}).get("restaurants", {}).get("count", 0)
        dining_score = min(restaurants / 100 * 3, 3)
        
        convenience_score = min(mart_score + store_score + dining_score, 8)
        
        # 1.3 교육 환경 (7점)
        education = pseudo_data.get("education", {})
        
        elementary_count = education.get("elementary", {}).get("count", 0)
        middle_count = education.get("middle", {}).get("count", 0)
        high_count = education.get("high", {}).get("count", 0)
        university_count = education.get("university", {}).get("count", 0)
        
        # 초중고: 각 1점씩 (최대 5점)
        school_score = min(elementary_count * 1, 2) + min(middle_count * 1, 1.5) + min(high_count * 1, 1.5)
        
        # 대학: 있으면 +2점
        university_score = min(university_count * 1, 2)
        
        education_score = min(school_score + university_score, 7)
        
        return {
            "transportation": transportation_score,
            "convenience": convenience_score,
            "education": education_score,
            "total": transportation_score + convenience_score + education_score
        }
    
    # ============================================================
    # 2. 사업 타당성 (30점)
    # ============================================================
    
    def _calculate_feasibility_score(self, analysis_result: Dict) -> Dict[str, float]:
        """사업 타당성 점수 계산"""
        
        land_info = analysis_result.get("land_info", {})
        dev_plan = analysis_result.get("development_plan", {})
        
        # 2.1 용적률/건폐율 적정성 (10점)
        far = land_info.get("floor_area_ratio", 0)
        bcr = land_info.get("building_coverage_ratio", 0)
        
        # FAR: 200% 이상 = 만점, 150~199 = 6점, 100~149 = 3점
        if far >= 200:
            far_score = 6
        elif far >= 150:
            far_score = 4
        elif far >= 100:
            far_score = 2
        else:
            far_score = 1
        
        # BCR: 60% 이상 = 만점, 50~59 = 3점
        if bcr >= 60:
            bcr_score = 4
        elif bcr >= 50:
            bcr_score = 3
        elif bcr >= 40:
            bcr_score = 2
        else:
            bcr_score = 1
        
        far_bcr_score = min(far_score + bcr_score, 10)
        
        # 2.2 세대수 적정성 (8점)
        unit_count = dev_plan.get("unit_count", 0)
        
        # LH 매입은 보통 20세대 이상 선호
        if unit_count >= 30:
            unit_score = 8
        elif unit_count >= 20:
            unit_score = 6
        elif unit_count >= 10:
            unit_score = 4
        else:
            unit_score = 2
        
        # 2.3 토지 가격 적정성 (12점)
        land_area = land_info.get("land_area", 0)
        land_price = land_info.get("land_appraisal_price", 0)
        
        if land_area > 0:
            price_per_sqm = land_price / land_area
            
            # 평당 가격 (㎡ → 평 환산)
            price_per_pyeong = price_per_sqm * 3.3
            
            # 서울 기준: 3천만원/평 이하 = 만점
            if price_per_pyeong <= 30000000:
                land_price_score = 12
            elif price_per_pyeong <= 50000000:
                land_price_score = 9
            elif price_per_pyeong <= 80000000:
                land_price_score = 6
            else:
                land_price_score = 3
        else:
            land_price_score = 6  # 기본값
        
        return {
            "far_bcr": far_bcr_score,
            "unit_count": unit_score,
            "land_price": land_price_score,
            "total": far_bcr_score + unit_score + land_price_score
        }
    
    # ============================================================
    # 3. 정책 정합성 (20점)
    # ============================================================
    
    def _calculate_policy_score(self, analysis_result: Dict, unit_analysis: Dict) -> Dict[str, float]:
        """정책 정합성 점수 계산"""
        
        land_info = analysis_result.get("land_info", {})
        zone_type = land_info.get("zone_type", "")
        
        # 3.1 용도지역 적합성 (8점)
        zone_scores = {
            "제3종일반주거지역": 8,
            "제2종일반주거지역": 7,
            "제1종일반주거지역": 5,
            "준주거지역": 6,
            "제2종전용주거지역": 4,
            "제1종전용주거지역": 3
        }
        
        zone_score = 8  # 기본값
        for zone_name, score in zone_scores.items():
            if zone_name in zone_type:
                zone_score = score
                break
        
        # 3.2 주택 정책 부합도 (7점)
        # 신혼/청년/고령자형이면 정책 부합도 높음
        recommended_type = unit_analysis.get("recommended_type", "general")
        
        policy_priority_types = ["newlywed", "youth", "senior", "vulnerable"]
        if any(ptype in recommended_type.lower() for ptype in policy_priority_types):
            housing_policy_score = 7
        else:
            housing_policy_score = 5
        
        # 3.3 공급 유형 적합성 (5점)
        # 세대유형 분석의 confidence 기반
        confidence = unit_analysis.get("confidence", 0)
        
        if confidence >= 90:
            unit_type_score = 5
        elif confidence >= 80:
            unit_type_score = 4
        elif confidence >= 70:
            unit_type_score = 3
        else:
            unit_type_score = 2
        
        return {
            "zone": zone_score,
            "housing_policy": housing_policy_score,
            "unit_type": unit_type_score,
            "total": zone_score + housing_policy_score + unit_type_score
        }
    
    # ============================================================
    # 4. 재무 건전성 (15점)
    # ============================================================
    
    def _calculate_financial_score(self, analysis_result: Dict) -> Dict[str, float]:
        """재무 건전성 점수 계산"""
        
        financial = analysis_result.get("financial_result", {})
        
        # 4.1 IRR/ROI 수준 (8점)
        irr = financial.get("irr_10yr", 0)
        roi = financial.get("roi", 0)
        
        # IRR 기준 (5점)
        if irr >= 5:
            irr_score = 5
        elif irr >= 4:
            irr_score = 4
        elif irr >= 3:
            irr_score = 3
        elif irr >= 2:
            irr_score = 2
        else:
            irr_score = 1
        
        # ROI 기준 (3점)
        if roi >= 40:
            roi_score = 3
        elif roi >= 30:
            roi_score = 2.5
        elif roi >= 20:
            roi_score = 2
        else:
            roi_score = 1
        
        irr_roi_score = min(irr_score + roi_score, 8)
        
        # 4.2 투자 회수 기간 (4점)
        # IRR 기반 추정 (IRR 높을수록 회수 빠름)
        if irr >= 5:
            payback_score = 4
        elif irr >= 4:
            payback_score = 3.5
        elif irr >= 3:
            payback_score = 3
        else:
            payback_score = 2
        
        # 4.3 자금 조달 가능성 (3점)
        # LH 매입임대는 사업성 보장되면 대부분 가능
        financing_score = 3 if irr >= 3 else 2
        
        return {
            "irr_roi": irr_roi_score,
            "payback": payback_score,
            "financing": financing_score,
            "total": irr_roi_score + payback_score + financing_score
        }
    
    # ============================================================
    # 5. 리스크 수준 (10점)
    # ============================================================
    
    def _calculate_risk_score(self, analysis_result: Dict) -> Dict[str, float]:
        """리스크 수준 점수 계산 (리스크 낮을수록 점수 높음)"""
        
        risk_assessment = analysis_result.get("risk_assessment", {})
        overall_risk = risk_assessment.get("overall_risk", "MEDIUM")
        
        # 5.1 법규 리스크 (4점)
        # 용도지역, 건축 규제 등
        land_info = analysis_result.get("land_info", {})
        zone_type = land_info.get("zone_type", "")
        
        # 일반주거지역 = 법규 리스크 낮음
        if "일반주거" in zone_type:
            legal_risk_score = 4
        elif "준주거" in zone_type:
            legal_risk_score = 3.5
        elif "전용주거" in zone_type:
            legal_risk_score = 3
        else:
            legal_risk_score = 2
        
        # 5.2 시장 리스크 (3점)
        if overall_risk == "LOW":
            market_risk_score = 3
        elif overall_risk == "MEDIUM":
            market_risk_score = 2
        else:
            market_risk_score = 1
        
        # 5.3 시공 리스크 (3점)
        dev_plan = analysis_result.get("development_plan", {})
        max_floors = dev_plan.get("max_floors", 0)
        
        # 층수가 낮을수록 시공 리스크 낮음
        if max_floors <= 5:
            construction_risk_score = 3
        elif max_floors <= 10:
            construction_risk_score = 2.5
        elif max_floors <= 15:
            construction_risk_score = 2
        else:
            construction_risk_score = 1.5
        
        return {
            "legal": legal_risk_score,
            "market": market_risk_score,
            "construction": construction_risk_score,
            "total": legal_risk_score + market_risk_score + construction_risk_score
        }
    
    # ============================================================
    # 등급 및 분석
    # ============================================================
    
    def _calculate_grade(self, total_score: float) -> LHGrade:
        """총점 기반 등급 계산"""
        if total_score >= 90:
            return LHGrade.A
        elif total_score >= 80:
            return LHGrade.B
        elif total_score >= 70:
            return LHGrade.C
        elif total_score >= 60:
            return LHGrade.D
        else:
            return LHGrade.F
    
    def _identify_strengths(self, location: Dict, feasibility: Dict, 
                           policy: Dict, financial: Dict, risk: Dict) -> List[str]:
        """강점 식별"""
        strengths = []
        
        # 각 영역별 만점 대비 80% 이상이면 강점
        if location["total"] >= self.max_scores["location"] * 0.8:
            strengths.append(f"✅ 우수한 입지 조건 ({location['total']:.1f}/25점)")
        
        if feasibility["total"] >= self.max_scores["feasibility"] * 0.8:
            strengths.append(f"✅ 높은 사업 타당성 ({feasibility['total']:.1f}/30점)")
        
        if policy["total"] >= self.max_scores["policy"] * 0.8:
            strengths.append(f"✅ 정책과의 높은 정합성 ({policy['total']:.1f}/20점)")
        
        if financial["total"] >= self.max_scores["financial"] * 0.8:
            strengths.append(f"✅ 건전한 재무 구조 ({financial['total']:.1f}/15점)")
        
        if risk["total"] >= self.max_scores["risk"] * 0.8:
            strengths.append(f"✅ 낮은 리스크 수준 ({risk['total']:.1f}/10점)")
        
        return strengths
    
    def _identify_weaknesses(self, location: Dict, feasibility: Dict,
                            policy: Dict, financial: Dict, risk: Dict) -> List[str]:
        """약점 식별"""
        weaknesses = []
        
        # 각 영역별 만점 대비 60% 미만이면 약점
        if location["total"] < self.max_scores["location"] * 0.6:
            weaknesses.append(f"⚠️ 입지 조건 개선 필요 ({location['total']:.1f}/25점)")
        
        if feasibility["total"] < self.max_scores["feasibility"] * 0.6:
            weaknesses.append(f"⚠️ 사업 타당성 보완 필요 ({feasibility['total']:.1f}/30점)")
        
        if policy["total"] < self.max_scores["policy"] * 0.6:
            weaknesses.append(f"⚠️ 정책 정합성 미흡 ({policy['total']:.1f}/20점)")
        
        if financial["total"] < self.max_scores["financial"] * 0.6:
            weaknesses.append(f"⚠️ 재무 구조 개선 필요 ({financial['total']:.1f}/15점)")
        
        if risk["total"] < self.max_scores["risk"] * 0.6:
            weaknesses.append(f"⚠️ 높은 리스크 수준 ({risk['total']:.1f}/10점)")
        
        return weaknesses
    
    def _generate_recommendations(self, weaknesses: List[str], total_score: float) -> List[str]:
        """개선 권고사항 생성"""
        recommendations = []
        
        if total_score < 70:
            recommendations.append("🔴 전체 점수가 70점 미만으로, 사업 재검토가 필요합니다")
        elif total_score < 80:
            recommendations.append("🟡 전체 점수가 80점 미만으로, 일부 개선이 권장됩니다")
        
        for weakness in weaknesses:
            if "입지" in weakness:
                recommendations.append("💡 교통 접근성 및 생활 편의 시설 보완 검토")
            elif "타당성" in weakness:
                recommendations.append("💡 용적률 최적화 및 세대수 조정 검토")
            elif "정책" in weakness:
                recommendations.append("💡 정부 정책 우선 공급 유형 반영 검토")
            elif "재무" in weakness:
                recommendations.append("💡 건축 비용 절감 및 수익성 개선 방안 검토")
            elif "리스크" in weakness:
                recommendations.append("💡 법규 검토 및 리스크 완화 전략 수립")
        
        if not recommendations:
            recommendations.append("✅ 전반적으로 우수한 평가 결과, 사업 추진 권장")
        
        return recommendations


# ============================================================
# 사용 예시
# ============================================================

if __name__ == "__main__":
    # 테스트
    mapper = LHScoreMapper()
    
    test_analysis = {
        "land_info": {
            "land_area": 1000,
            "land_appraisal_price": 9000000000,
            "zone_type": "제3종일반주거지역",
            "building_coverage_ratio": 60,
            "floor_area_ratio": 250
        },
        "development_plan": {
            "unit_count": 42,
            "max_floors": 10
        },
        "financial_result": {
            "irr_10yr": 3.6,
            "roi": 37.11
        },
        "risk_assessment": {
            "overall_risk": "MEDIUM"
        }
    }
    
    test_unit_analysis = {
        "recommended_type": "youth",
        "confidence": 89.5
    }
    
    test_pseudo_data = {
        "education": {
            "elementary": {"count": 5},
            "middle": {"count": 3},
            "high": {"count": 2},
            "university": {"count": 3, "names": ["홍익대", "서강대", "연세대"]}
        },
        "transportation": {
            "subway": {"lines": ["2호선", "6호선"]},
            "bus": {"total_routes": 25}
        },
        "convenience": {
            "shopping": {
                "large_marts": {"count": 3},
                "convenience_stores": {"count": 35}
            },
            "dining": {
                "restaurants": {"count": 120}
            }
        }
    }
    
    result = mapper.calculate_lh_score(test_analysis, test_unit_analysis, test_pseudo_data)
    
    print("=" * 60)
    print("LH Score Mapper Test Result")
    print("=" * 60)
    print(f"총점: {result.total_score:.1f}/100")
    print(f"등급: {result.grade.value}")
    print(f"\n입지 적합성: {result.location_total:.1f}/25")
    print(f"사업 타당성: {result.feasibility_total:.1f}/30")
    print(f"정책 정합성: {result.policy_total:.1f}/20")
    print(f"재무 건전성: {result.financial_total:.1f}/15")
    print(f"리스크 수준: {result.risk_total:.1f}/10")
    
    print(f"\n강점:")
    for strength in result.strengths:
        print(f"  {strength}")
    
    print(f"\n약점:")
    for weakness in result.weaknesses:
        print(f"  {weakness}")
    
    print(f"\n권고사항:")
    for rec in result.recommendations:
        print(f"  {rec}")
