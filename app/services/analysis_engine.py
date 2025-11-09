"""
토지 분석 엔진 - 모든 서비스를 통합하여 종합 분석 수행
"""

import asyncio
from typing import Dict, Any, List
from app.schemas import (
    LandAnalysisRequest,
    Coordinates,
    BuildingCapacity,
    RiskFactor,
    DemandAnalysis,
    AnalysisSummary,
    NearbyFacility
)
from app.services.kakao_service import KakaoService
from app.services.land_regulation_service import LandRegulationService
from app.services.mois_service import MOISService
from app.utils.calculations import BuildingCalculator


class AnalysisEngine:
    """토지 분석 통합 엔진"""
    
    def __init__(self):
        self.kakao = KakaoService()
        self.land_regulation = LandRegulationService()
        self.mois = MOISService()
        self.calculator = BuildingCalculator()
    
    async def analyze_land(self, request: LandAnalysisRequest) -> Dict[str, Any]:
        """
        토지 종합 분석 실행
        
        Args:
            request: 토지 분석 요청
            
        Returns:
            분석 결과 딕셔너리
        """
        print(f"📍 토지 분석 시작: {request.address}")
        
        # 1. 좌표 변환
        print("  ↳ 1단계: 주소 → 좌표 변환")
        coordinates = await self.kakao.address_to_coordinates(request.address)
        
        if not coordinates:
            raise ValueError("주소를 좌표로 변환할 수 없습니다.")
        
        print(f"    ✓ 좌표: ({coordinates.latitude}, {coordinates.longitude})")
        
        # 2. 병렬로 데이터 수집
        print("  ↳ 2단계: 외부 API 데이터 수집 (병렬)")
        
        zone_task = self.land_regulation.get_zone_info(coordinates)
        restrictions_task = self.land_regulation.check_development_restrictions(coordinates)
        hazardous_task = self.kakao.search_hazardous_facilities(coordinates)
        accessibility_task = self.kakao.analyze_location_accessibility(coordinates)
        demographic_task = self.mois.analyze_demographics(request.address, coordinates)
        
        zone_info, restrictions, hazardous_facilities, accessibility, demographic_info = \
            await asyncio.gather(
                zone_task,
                restrictions_task,
                hazardous_task,
                accessibility_task,
                demographic_task
            )
        
        print(f"    ✓ 용도지역: {zone_info.zone_type}")
        print(f"    ✓ 청년인구 비율: {demographic_info.youth_ratio}%")
        print(f"    ✓ 접근성 점수: {accessibility['accessibility_score']}")
        
        # 3. 리스크 요인 분석
        print("  ↳ 3단계: 리스크 요인 분석")
        risk_factors = self._analyze_risk_factors(
            restrictions,
            hazardous_facilities,
            accessibility
        )
        print(f"    ✓ 리스크 요인: {len(risk_factors)}개")
        
        # 4. 건축 규모 계산
        print("  ↳ 4단계: 건축 규모 산정")
        building_capacity = self.calculator.calculate_capacity(
            land_area=request.land_area,
            zone_info=zone_info,
            unit_type=request.unit_type
        )
        print(f"    ✓ 예상 세대수: {building_capacity.units}세대")
        print(f"    ✓ 층수: {building_capacity.floors}층")
        
        # 5. 수요 분석
        print("  ↳ 5단계: 입지 및 수요 분석")
        demand_analysis = await self._analyze_demand(
            demographic_info=demographic_info,
            accessibility=accessibility,
            unit_type=request.unit_type,
            coordinates=coordinates
        )
        print(f"    ✓ 수요 점수: {demand_analysis.demand_score}/100")
        
        # 6. 종합 판단
        print("  ↳ 6단계: 종합 적합성 판단")
        summary = self._create_summary(
            risk_factors=risk_factors,
            building_capacity=building_capacity,
            demand_analysis=demand_analysis,
            restrictions=restrictions
        )
        print(f"    ✓ 최종 판단: {summary.recommendation}")
        
        print("✅ 토지 분석 완료\n")
        
        return {
            "coordinates": coordinates,
            "zone_info": zone_info,
            "building_capacity": building_capacity,
            "risk_factors": risk_factors,
            "demographic_info": demographic_info,
            "demand_analysis": demand_analysis,
            "summary": summary
        }
    
    def _analyze_risk_factors(
        self,
        restrictions: List[str],
        hazardous_facilities: List[Dict],
        accessibility: Dict
    ) -> List[RiskFactor]:
        """리스크 요인 분석"""
        risks = []
        
        # 개발 제한 리스크
        for restriction in restrictions:
            risks.append(RiskFactor(
                category="법적제한",
                description=f"{restriction} 해당",
                severity="high"
            ))
        
        # 유해시설 리스크
        if hazardous_facilities:
            for facility in hazardous_facilities[:3]:  # 최대 3개
                risks.append(RiskFactor(
                    category="유해시설",
                    description=f"{facility['category']} {int(facility['distance'])}m 이내 위치 ({facility['name']})",
                    severity="medium" if facility['distance'] > 300 else "high"
                ))
        
        # 접근성 리스크
        if accessibility['nearest_subway_distance'] > 2000:
            risks.append(RiskFactor(
                category="접근성",
                description=f"지하철역 {int(accessibility['nearest_subway_distance'])}m (도보 20분 이상)",
                severity="medium"
            ))
        
        if accessibility['accessibility_score'] < 40:
            risks.append(RiskFactor(
                category="입지",
                description="전반적인 대중교통 접근성 부족",
                severity="medium"
            ))
        
        return risks
    
    async def _analyze_demand(
        self,
        demographic_info,
        accessibility: Dict,
        unit_type: str,
        coordinates: Coordinates
    ) -> DemandAnalysis:
        """수요 분석"""
        
        # 수요 지표 계산
        demand_indicators = await self.mois.calculate_demand_indicators(
            demographic_info,
            unit_type
        )
        
        # 종합 수요 점수 계산 (100점 만점)
        demand_score = 0
        
        # 1. 인구통계 점수 (40점)
        demand_score += min(demand_indicators['demographic_fit_score'] * 0.4, 40)
        
        # 2. 접근성 점수 (30점)
        demand_score += accessibility['accessibility_score'] * 0.3
        
        # 3. 시장 규모 점수 (30점)
        demand_score += demand_indicators['market_size_score'] * 0.3
        
        demand_score = round(demand_score, 1)
        
        # 핵심 수요 요인 추출
        key_factors = []
        
        if demographic_info.youth_ratio > 30:
            key_factors.append(f"청년 인구 비중 {demographic_info.youth_ratio}% (높음)")
        
        if demographic_info.single_household_ratio > 30:
            key_factors.append(f"1인 가구 비율 {demographic_info.single_household_ratio}%")
        
        if accessibility['nearest_subway_distance'] < 1000:
            key_factors.append(f"지하철역 {int(accessibility['nearest_subway_distance'])}m (도보 10분 이내)")
        
        if accessibility['nearest_university_distance'] < 3000:
            key_factors.append(f"대학교 {int(accessibility['nearest_university_distance'])}m 거리")
        
        # 적합성 판단
        if demand_score >= 70:
            recommendation = "적합"
        elif demand_score >= 50:
            recommendation = "검토 필요"
        else:
            recommendation = "부적합"
        
        return DemandAnalysis(
            demand_score=demand_score,
            key_factors=key_factors if key_factors else ["수요 분석 데이터 부족"],
            recommendation=recommendation,
            nearby_facilities=accessibility.get('subway_stations', [])[:3]
        )
    
    def _create_summary(
        self,
        risk_factors: List[RiskFactor],
        building_capacity: BuildingCapacity,
        demand_analysis: DemandAnalysis,
        restrictions: List[str]
    ) -> AnalysisSummary:
        """종합 판단 생성"""
        
        # 치명적 리스크 확인
        has_critical_risk = any(
            r.severity == "high" for r in risk_factors
        ) or len(restrictions) > 0
        
        # 적격성 판단
        is_eligible = (
            not has_critical_risk and
            demand_analysis.demand_score >= 50 and
            building_capacity.units >= 10
        )
        
        # 종합 추천
        if is_eligible and demand_analysis.demand_score >= 70:
            recommendation = "적합 - LH 매입 가능성 높음"
        elif is_eligible:
            recommendation = "검토 필요 - 조건부 적합"
        else:
            recommendation = "부적합 - 매입 제외 대상"
        
        return AnalysisSummary(
            is_eligible=is_eligible,
            estimated_units=building_capacity.units,
            demand_score=demand_analysis.demand_score,
            recommendation=recommendation,
            risk_count=len(risk_factors)
        )
