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
    NearbyFacility,
    GradeInfo,
    CheckItemSchema
)
from app.services.kakao_service import KakaoService
from app.services.land_regulation_service import LandRegulationService
from app.services.mois_service import MOISService
from app.utils.calculations import BuildingCalculator
from app.services.lh_criteria_checker import LHCriteriaChecker
from app.services.demand_prediction import MunicipalDemandPredictor
from app.services.negotiation_strategy import NegotiationStrategyGenerator
from app.services.ai_auto_corrector import get_auto_corrector
from app.services.geo_optimizer import get_geo_optimizer
from app.services.parcel_cluster import get_parcel_analyzer


class AnalysisEngine:
    """토지 분석 통합 엔진"""
    
    def __init__(self):
        self.kakao = KakaoService()
        self.land_regulation = LandRegulationService()
        self.mois = MOISService()
        self.calculator = BuildingCalculator()
        self.demand_predictor = MunicipalDemandPredictor()  # 수요예측 엔진
        self.strategy_generator = NegotiationStrategyGenerator()  # 협상전략 생성기
        # ✨ v5.0: 신규 서비스
        self.auto_corrector = get_auto_corrector()  # AI 자동 교정
        self.geo_optimizer = get_geo_optimizer()  # 지리 최적화
        self.parcel_analyzer = get_parcel_analyzer()  # 다필지 분석
    
    def _format_distance(self, distance: float) -> str:
        """
        Format distance for display, handling edge cases like 9999 (no data)
        """
        if distance >= 9999 or distance == float('inf'):
            return "2km 이상 (데이터 없음)"
        elif distance > 2000:
            return f"{distance/1000:.1f}km"
        else:
            return f"{int(distance)}m"
    
    def _format_walk_time(self, distance: float) -> str:
        """
        Calculate and format walking time (~80m/min)
        """
        if distance >= 9999 or distance == float('inf'):
            return "도보 시간 미확인"
        minutes = int(distance / 80)
        return f"도보 {minutes}분"
    
    def _get_zone_defaults(self, zone_type: str) -> Dict[str, float]:
        """용도지역별 기본 건폐율/용적률 반환"""
        zone_map = {
            "제1종전용주거지역": {"bcr": 50, "far": 100},
            "제2종전용주거지역": {"bcr": 50, "far": 150},
            "제1종일반주거지역": {"bcr": 60, "far": 200},
            "제2종일반주거지역": {"bcr": 60, "far": 200},
            "제3종일반주거지역": {"bcr": 50, "far": 300},
            "준주거지역": {"bcr": 70, "far": 500},
            "중심상업지역": {"bcr": 90, "far": 1500},
            "일반상업지역": {"bcr": 80, "far": 1300},
            "근린상업지역": {"bcr": 70, "far": 900},
            "유통상업지역": {"bcr": 80, "far": 1100},
            "전용공업지역": {"bcr": 70, "far": 300},
            "일반공업지역": {"bcr": 70, "far": 350},
            "준공업지역": {"bcr": 70, "far": 400},
            "보전녹지지역": {"bcr": 20, "far": 80},
            "생산녹지지역": {"bcr": 20, "far": 100},
            "자연녹지지역": {"bcr": 20, "far": 100},
            "보전관리지역": {"bcr": 20, "far": 80},
            "생산관리지역": {"bcr": 20, "far": 80},
            "계획관리지역": {"bcr": 40, "far": 100},
            "자연환경보전지역": {"bcr": 20, "far": 80},
        }
        return zone_map.get(zone_type, {"bcr": 60, "far": 200})
    
    async def analyze_land(self, request: LandAnalysisRequest) -> Dict[str, Any]:
        """
        토지 종합 분석 실행
        
        Args:
            request: 토지 분석 요청
            
        Returns:
            분석 결과 딕셔너리
        """
        print(f"📍 토지 분석 시작: {request.address}")
        
        # 0. ✨ v5.0: AI 자동 교정 (입력 검증 및 교정)
        print("  ↳ 0단계: AI 자동 입력 교정")
        corrected_input = self.auto_corrector.correct_input(
            address=request.address,
            land_area=request.land_area,
            zone_type=request.zone_type
        )
        print(f"    ✓ 교정 완료: {len(corrected_input.corrections_made)}건 교정, {len(corrected_input.warnings)}건 경고")
        
        # 교정된 주소 사용 (교정이 있으면)
        working_address = corrected_input.corrected_address or request.address
        working_area = corrected_input.corrected_land_area or request.land_area
        
        # 1. 좌표 변환
        print("  ↳ 1단계: 주소 → 좌표 변환")
        coordinates = await self.kakao.address_to_coordinates(working_address)
        
        if not coordinates:
            raise ValueError("주소를 좌표로 변환할 수 없습니다.")
        
        print(f"    ✓ 좌표: ({coordinates.latitude}, {coordinates.longitude})")
        
        # 2. 병렬로 데이터 수집
        print("  ↳ 2단계: 외부 API 데이터 수집 (병렬)")
        
        zone_task = self.land_regulation.get_zone_info(coordinates)
        restrictions_task = self.land_regulation.check_development_restrictions(coordinates)
        # unit_type 전달 (다자녀형일 때 2순위 유해시설도 체크)
        unit_type_value = request.unit_type.value if request.unit_type else None
        hazardous_task = self.kakao.search_hazardous_facilities(coordinates, unit_type=unit_type_value)
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
        
        # 사용자가 용도지역을 선택한 경우 우선 사용
        if request.zone_type:
            from app.schemas import ZoneInfo
            # 용도지역별 기본 건폐율/용적률 설정
            zone_defaults = self._get_zone_defaults(request.zone_type)
            zone_info = ZoneInfo(
                zone_type=request.zone_type,
                building_coverage_ratio=zone_defaults['bcr'],
                floor_area_ratio=zone_defaults['far'],
                height_limit=zone_info.height_limit if zone_info else None
            )
            print(f"    ✓ 용도지역: {zone_info.zone_type} (사용자 선택)")
        else:
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
        
        # 7. 등급 평가 및 체크리스트 생성 (신규)
        print("  ↳ 7단계: LH 기준 등급 평가 (A/B/C)")
        
        # 사업성 계산
        land_price = request.land_appraisal_price * request.land_area if request.land_appraisal_price else 0
        financial_data = self.calculator.calculate_lh_purchase_feasibility(
            land_price=land_price,
            building_capacity=building_capacity,
            unit_type=request.unit_type.value if request.unit_type else "청년형",
            land_area=request.land_area
        )
        
        # 가중치 설정 (사용자 정의 또는 기본값)
        custom_weights = None
        if request.weights:
            custom_weights = {
                "location": request.weights.location,
                "scale": request.weights.scale,
                "business": request.weights.business,
                "regulation": request.weights.regulation
            }
            print(f"    ✓ 사용자 정의 가중치: 입지 {request.weights.location}%, 규모 {request.weights.scale}%, 사업성 {request.weights.business}%, 법규 {request.weights.regulation}%")
        
        # 등급 평가기 생성 (가중치 적용, LH 버전 적용)
        lh_version = request.lh_version if hasattr(request, 'lh_version') else "2024"
        print(f"    ✓ LH 기준 버전: {lh_version}")
        criteria_checker = LHCriteriaChecker(
            custom_weights=custom_weights,
            lh_version=lh_version
        )
        
        # 등급 평가 수행
        grade_result = criteria_checker.check_all(
            location_data={
                'nearest_subway_distance': accessibility.get('nearest_subway_distance', 9999),
                'accessibility_score': accessibility.get('accessibility_score', 0),
                'harmful_facilities': hazardous_facilities,
                'nearest_school_distance': accessibility.get('nearest_school_distance', 9999)
            },
            building_data={
                'units': building_capacity.units,
                'parking_spaces': building_capacity.parking_spaces,
                'floors': building_capacity.floors,
                'building_area': building_capacity.building_area,
                'total_floor_area': building_capacity.total_floor_area,
                'land_area': request.land_area,
                'average_unit_area': financial_data.get('average_unit_area', 30)
            },
            financial_data=financial_data,
            zone_data={
                'zone_type': zone_info.zone_type,
                'building_coverage_ratio': zone_info.building_coverage_ratio,
                'floor_area_ratio': zone_info.floor_area_ratio,
                'height_limit': zone_info.height_limit
            }
        )
        
        # GradeInfo 스키마로 변환
        grade_info = GradeInfo(
            grade=grade_result.grade.value,
            total_score=grade_result.total_score,
            category_scores=grade_result.category_scores,
            summary=grade_result.summary,
            recommendations=grade_result.recommendations
        )
        
        # CheckItem -> CheckItemSchema 변환
        checklist = [
            CheckItemSchema(
                category=item.category,
                item=item.item,
                status=item.status.value,
                value=item.value,
                standard=item.standard,
                description=item.description,
                score=item.score
            )
            for item in grade_result.checklist
        ]
        
        # Summary에 등급 정보 추가
        summary.grade = grade_result.grade.value
        summary.total_score = grade_result.total_score
        
        print(f"    ✓ 등급: {grade_result.grade.value} ({grade_result.total_score:.1f}점)")
        
        # 8. 지자체 수요예측 (LITE 1.0)
        print("  ↳ 8단계: 지자체 수요예측 엔진 (LITE 1.0)")
        
        # 수요예측 입력 데이터 준비
        subway_dist = accessibility.get('nearest_subway_distance', 9999)
        # 🔥 Sanitize infinity values to prevent OverflowError
        if not isinstance(subway_dist, (int, float)) or subway_dist == float('inf') or subway_dist > 10000:
            subway_dist = 9999
        univ_dist = accessibility.get('nearest_university_distance', 5000)  # 기본값
        youth_ratio_val = demographic_info.youth_ratio if demographic_info else 25.0
        avg_rent = 45.0  # 기본값 (만원) - 실제로는 지역별 시세 API 필요
        existing_supply = 200  # 기본값 - 실제로는 주변 임대주택 조사 필요
        
        # unit_type 문자열 추출
        unit_type_str = request.unit_type.value if request.unit_type else "청년"
        
        demand_prediction = self.demand_predictor.predict(
            subway_distance=subway_dist,
            university_distance=univ_dist,
            youth_ratio=youth_ratio_val,
            avg_rent_price=avg_rent,
            existing_rental_units=existing_supply,
            target_units=building_capacity.units,
            unit_type=unit_type_str,
            lh_version=lh_version
        )
        
        print(f"    ✓ 수요 예측: {demand_prediction.demand_level} ({demand_prediction.demand_score:.1f}점)")
        
        # 9. 사업성 협상전략 생성
        print("  ↳ 9단계: 사업성 협상전략 자동 생성")
        
        # 체크리스트 통과율 계산
        total_checks = len(checklist)
        passed_checks = sum(1 for item in checklist if item.status in ["통과", "참고"])
        checklist_pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # 입지 점수 계산 (카테고리 점수에서 가져오기)
        location_score = grade_result.category_scores.get("입지", 0)
        
        negotiation_strategy = self.strategy_generator.generate(
            units=building_capacity.units,
            construction_cost=financial_data.get('construction_cost', 0),
            land_cost=financial_data.get('land_cost', 0),
            business_score=grade_result.category_scores.get("사업성", 0),
            roi=financial_data.get('roi', 0),
            lh_purchase_price=financial_data.get('lh_purchase_price_per_unit', 150000000),
            actual_cost_per_unit=financial_data.get('cost_per_unit', 0),
            parking_ratio=building_capacity.parking_spaces / building_capacity.units if building_capacity.units > 0 else 0,
            location_score=location_score,
            demand_score=demand_analysis.demand_score,
            zone_type=zone_info.zone_type,
            checklist_pass_rate=checklist_pass_rate
        )
        
        print(f"    ✓ 협상전략: {len(negotiation_strategy.strategies)}개 전략 생성")
        
        # 등급 점수에 수요예측 점수 반영 (+10% 가중)
        adjusted_total_score = grade_result.total_score * 0.9 + demand_prediction.demand_score * 0.1
        print(f"    ✓ 수요예측 반영 후 최종 점수: {adjusted_total_score:.1f}점")
        
        # GradeInfo에 조정된 점수 반영
        grade_info.total_score = round(adjusted_total_score, 2)
        
        # 체크리스트 상세 정보 추출 (PDF 생성용)
        checklist_details = criteria_checker.get_checklist_details(grade_result)
        
        # 10. 유형별 수요점수 완전 분리 계산 (v5.0 핵심 기능)
        print("  ↳ 10단계: 유형별 수요점수 완전 분리 계산")
        type_demand_scores = self._calculate_type_demand_scores(
            demographic_info=demographic_info,
            accessibility=accessibility,
            coordinates=coordinates,
            building_capacity=building_capacity,
            zone_info=zone_info
        )
        print(f"    ✓ 유형별 점수 계산 완료:")
        for unit_type, score in type_demand_scores.items():
            print(f"      - {unit_type}: {score:.1f}점")
        
        # 11. ✨ v5.0: 지리적 최적화 분석
        print("  ↳ 11단계: 지리적 최적화 분석")
        geo_optimization_result = self.geo_optimizer.optimize(
            latitude=coordinates.latitude,
            longitude=coordinates.longitude,
            address=working_address,
            accessibility=accessibility,
            demographic_info=demographic_info,
            zone_info=zone_info
        )
        print(f"    ✓ 최적화 점수: {geo_optimization_result.optimization_score:.1f}점")
        print(f"    ✓ 추천 대안 위치: {len(geo_optimization_result.recommended_sites)}개")
        
        print("✅ 토지 분석 완료\n")
        
        return {
            "coordinates": coordinates,
            "zone_info": zone_info,
            "building_capacity": building_capacity,
            "risk_factors": risk_factors,
            "demographic_info": demographic_info,
            "demand_analysis": demand_analysis,
            "summary": summary,
            "financial_data": financial_data,  # 사업성 상세 정보
            "grade_info": grade_info,  # 등급 평가 결과
            "checklist": checklist,  # 체크리스트
            "checklist_details": checklist_details,  # 체크리스트 상세 정보 (PDF용)
            "lh_version": lh_version,  # 사용된 LH 기준 버전
            "demand_prediction": {  # 지자체 수요예측 (신규)
                "demand_score": demand_prediction.demand_score,
                "demand_level": demand_prediction.demand_level,
                "comment": demand_prediction.comment,
                "factor_scores": demand_prediction.factor_scores,
                "recommendations": demand_prediction.recommendations
            },
            "negotiation_strategy": {  # 협상전략 (신규)
                "strategies": negotiation_strategy.strategies,
                "strengths": negotiation_strategy.strengths,
                "weaknesses": negotiation_strategy.weaknesses,
                "priority_actions": negotiation_strategy.priority_actions
            },
            "type_demand_scores": type_demand_scores,  # ✨ v5.0: 유형별 수요점수 완전 분리
            "corrected_input": {  # ✨ v5.0: AI 자동 교정 결과
                "original_address": corrected_input.original_address,
                "corrected_address": corrected_input.corrected_address,
                "address_confidence": corrected_input.address_confidence,
                "original_land_area": corrected_input.original_land_area,
                "corrected_land_area": corrected_input.corrected_land_area,
                "area_confidence": corrected_input.area_confidence,
                "corrections_made": corrected_input.corrections_made,
                "warnings": corrected_input.warnings,
                "suggestions": corrected_input.suggestions
            },
            "geo_optimization": {  # ✨ v5.0: 지리적 최적화
                "analyzed_location": geo_optimization_result.analyzed_location,
                "optimization_score": geo_optimization_result.optimization_score,
                "recommended_sites": [site.dict() for site in geo_optimization_result.recommended_sites],
                "current_site_strengths": geo_optimization_result.current_site_strengths,
                "current_site_weaknesses": geo_optimization_result.current_site_weaknesses,
                "optimization_suggestions": geo_optimization_result.optimization_suggestions
            }
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
        
        # 유해시설 리스크 - LH 기준 적용
        if hazardous_facilities:
            for facility in hazardous_facilities:
                distance = facility['distance']
                category = facility['category']
                name = facility['name']
                
                # 주유소 25m 이내: 절대 탈락 사유 (LH 매입 제외 대상)
                if category == "주유소" and distance <= 25:
                    risks.append(RiskFactor(
                        category="LH매입제외",
                        description=f"주유소 {int(distance)}m 이내 위치 - 절대 탈락 사유 ({name})",
                        severity="critical"
                    ))
                # 주유소 25~50m: 고위험
                elif category == "주유소" and distance <= 50:
                    risks.append(RiskFactor(
                        category="유해시설",
                        description=f"주유소 {int(distance)}m 이내 위치 - 고위험 ({name})",
                        severity="high"
                    ))
                # 기타 유해시설 50m 이내
                elif distance <= 50:
                    risks.append(RiskFactor(
                        category="유해시설",
                        description=f"{category} {int(distance)}m 이내 위치 ({name})",
                        severity="high"
                    ))
                # 유해시설 50~500m
                elif distance <= 500:
                    risks.append(RiskFactor(
                        category="유해시설",
                        description=f"{category} {int(distance)}m 이내 위치 ({name})",
                        severity="medium"
                    ))
        
        # 접근성 리스크
        nearest_subway = accessibility.get('nearest_subway_distance', 9999)
        if nearest_subway == float('inf') or nearest_subway > 10000:
            nearest_subway = 9999
        if nearest_subway > 2000:
            # Format distance display properly
            if nearest_subway >= 9999:
                distance_text = "2km 이상 (데이터 없음)"
            else:
                distance_text = f"{int(nearest_subway)}m (도보 {int(nearest_subway/80)}분 이상)"
            
            risks.append(RiskFactor(
                category="접근성",
                description=f"지하철역 {distance_text}",
                severity="medium"
            ))
        
        if accessibility['accessibility_score'] < 40:
            risks.append(RiskFactor(
                category="입지",
                description="전반적인 대중교통 접근성 부족",
                severity="medium"
            ))
        
        return risks
    
    async def _calculate_kakao_demand_bonus(
        self,
        coordinates: Coordinates,
        unit_type: str
    ) -> Dict[str, float]:
        """
        카카오 주변 시설 데이터 기반 수요 보정
        정부 API 실패 시 대체 점수 계산
        """
        try:
            # 주변 시설 밀집도 조사 (2km 반경)
            facility_categories = {
                "학교": {"radius": 2000, "weight": 0.15},
                "대학교": {"radius": 3000, "weight": 0.2},
                "지하철역": {"radius": 1500, "weight": 0.25},
                "편의점": {"radius": 500, "weight": 0.1},
                "대형마트": {"radius": 2000, "weight": 0.1},
                "병원": {"radius": 1500, "weight": 0.1},
                "카페": {"radius": 1000, "weight": 0.05},
                "음식점": {"radius": 1000, "weight": 0.05}
            }
            
            total_score = 0
            facility_count = 0
            
            for category, config in facility_categories.items():
                facilities = await self.kakao.search_nearby_facilities(
                    coordinates,
                    category,
                    radius=config["radius"]
                )
                count = len(facilities)
                facility_count += count
                
                # 시설 수에 따른 점수 (최대 100점)
                category_score = min(count * 10, 100) * config["weight"]
                total_score += category_score
            
            # 인구통계 보정 점수 (40점 만점)
            # 주변 시설이 많으면 = 인구 밀집 지역
            demographic_boost = min(total_score * 0.4, 35)
            
            # 시장 규모 보정 점수 (30점 만점)
            # 주변 시설이 많으면 = 시장 규모 큼
            market_boost = min(total_score * 0.3, 25)
            
            print(f"    💡 카카오 기반 수요 보정: 주변 시설 {facility_count}개 (인구+{demographic_boost:.1f}점, 시장+{market_boost:.1f}점)")
            
            return {
                "demographic_boost": demographic_boost,
                "market_boost": market_boost,
                "facility_count": facility_count
            }
        except Exception as e:
            print(f"    ⚠️ 카카오 보정 계산 실패: {e}")
            return {
                "demographic_boost": 20,  # 기본 최소값
                "market_boost": 15,
                "facility_count": 0
            }
    
    async def _analyze_demand(
        self,
        demographic_info,
        accessibility: Dict,
        unit_type: str,
        coordinates: Coordinates
    ) -> DemandAnalysis:
        """수요 분석 (정부 API 실패 시 카카오 데이터로 보정)"""
        
        # 수요 지표 계산
        demand_indicators = await self.mois.calculate_demand_indicators(
            demographic_info,
            unit_type
        )
        
        # 카카오 주변 시설 기반 수요 보정 (정부 API 실패 시)
        kakao_bonus = await self._calculate_kakao_demand_bonus(coordinates, unit_type)
        
        # 종합 수요 점수 계산 (100점 만점)
        demand_score = 0
        
        # 1. 인구통계 점수 (40점) - 정부 API 실패 시 카카오 보정 적용
        demographic_score = demand_indicators['demographic_fit_score'] * 0.4
        if demographic_score < 20:  # API 실패로 낮은 점수인 경우
            demographic_score = max(demographic_score, kakao_bonus['demographic_boost'])
        demand_score += min(demographic_score, 40)
        
        # 2. 접근성 점수 (30점) - 카카오 데이터는 항상 정확
        demand_score += accessibility['accessibility_score'] * 0.3
        
        # 3. 시장 규모 점수 (30점) - 정부 API 실패 시 카카오 보정 적용
        market_score = demand_indicators['market_size_score'] * 0.3
        if market_score < 10:  # API 실패로 낮은 점수인 경우
            market_score = max(market_score, kakao_bonus['market_boost'])
        demand_score += market_score
        
        demand_score = round(demand_score, 1)
        
        # 핵심 수요 요인 추출
        key_factors = []
        
        if demographic_info.youth_ratio > 30:
            key_factors.append(f"청년 인구 비중 {demographic_info.youth_ratio}% (높음)")
        
        if demographic_info.single_household_ratio > 30:
            key_factors.append(f"1인 가구 비율 {demographic_info.single_household_ratio}%")
        
        nearest_subway_for_demand = accessibility.get('nearest_subway_distance', 9999)
        if nearest_subway_for_demand == float('inf') or nearest_subway_for_demand > 10000:
            nearest_subway_for_demand = 9999
        if nearest_subway_for_demand < 1000 and nearest_subway_for_demand < 9999:
            key_factors.append(f"지하철역 {self._format_distance(nearest_subway_for_demand)} ({self._format_walk_time(nearest_subway_for_demand)} 이내)")
        
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
        
        # 절대 탈락 사유 확인 (주유소 25m 이내 등)
        has_absolute_disqualification = any(
            r.severity == "critical" for r in risk_factors
        )
        
        # 치명적 리스크 확인
        has_critical_risk = any(
            r.severity == "high" for r in risk_factors
        ) or len(restrictions) > 0
        
        # 적격성 판단
        if has_absolute_disqualification:
            is_eligible = False
            recommendation = "절대 탈락 - LH 매입 제외 대상 (주유소 25m 이내 또는 기타 절대 제한 사유)"
        elif has_critical_risk:
            is_eligible = False
            recommendation = "부적합 - 고위험 요인 존재"
        elif demand_analysis.demand_score >= 70 and building_capacity.units >= 10:
            is_eligible = True
            recommendation = "적합 - LH 매입 가능성 높음"
        elif demand_analysis.demand_score >= 50 and building_capacity.units >= 10:
            is_eligible = True
            recommendation = "검토 필요 - 조건부 적합"
        else:
            is_eligible = False
            recommendation = "부적합 - 수요 또는 규모 미달"
        
        return AnalysisSummary(
            is_eligible=is_eligible,
            estimated_units=building_capacity.units,
            demand_score=demand_analysis.demand_score,
            recommendation=recommendation,
            risk_count=len(risk_factors)
        )
    
    def _calculate_type_demand_scores(
        self,
        demographic_info: Any,
        accessibility: Dict,
        coordinates: Coordinates,
        building_capacity: BuildingCapacity,
        zone_info: Any
    ) -> Dict[str, float]:
        """
        유형별 수요점수 완전 분리 계산 (v5.0 핵심 기능)
        
        각 주거 유형별로 독립적인 수요 점수 계산
        - 청년: 지하철/대학 접근성 중심
        - 신혼·신생아 I/II: 학교/보육시설 중심
        - 다자녀: 학교/공원 중심
        - 고령자: 병원/복지시설 중심
        
        Returns:
            유형별 점수 딕셔너리 {"청년": 88.5, "신혼·신생아 I": 85.2, ...}
        """
        scores = {}
        
        # 기본 입지 점수 (모든 유형 공통)
        base_score = min(accessibility.get('accessibility_score', 50) * 0.6, 60)
        
        # 인구 데이터
        youth_ratio = demographic_info.youth_ratio if demographic_info else 25.0
        elderly_ratio = demographic_info.elderly_ratio if demographic_info else 15.0
        
        # POI 거리 데이터
        subway_dist = accessibility.get('nearest_subway_distance', 9999)
        # 🔥 Sanitize infinity values for type demand scores
        if subway_dist == float('inf') or subway_dist > 10000:
            subway_dist = 9999
        school_dist = accessibility.get('nearest_school_distance', 9999)
        if school_dist == float('inf') or school_dist > 10000:
            school_dist = 9999
        hospital_dist = accessibility.get('nearest_hospital_distance', 9999)
        if hospital_dist == float('inf') or hospital_dist > 10000:
            hospital_dist = 9999
        
        # 1. 청년형 - 지하철/대학/편의시설 중심
        youth_score = base_score
        if subway_dist < 500:
            youth_score += 25
        elif subway_dist < 1000:
            youth_score += 15
        elif subway_dist < 1500:
            youth_score += 5
        
        youth_score += min(youth_ratio * 0.8, 20)  # 청년인구 비율
        youth_score = min(youth_score, 100)
        scores["청년"] = round(youth_score, 1)
        
        # 2. 신혼·신생아 I (60㎡ 미만) - 학교/보육시설 중심
        newlywed_i_score = base_score
        if school_dist < 500:
            newlywed_i_score += 20
        elif school_dist < 1000:
            newlywed_i_score += 12
        
        if subway_dist < 800:
            newlywed_i_score += 10
        
        newlywed_i_score += min(youth_ratio * 0.5, 15)  # 신혼부부는 청년층 포함
        newlywed_i_score = min(newlywed_i_score, 100)
        scores["신혼·신생아 I"] = round(newlywed_i_score, 1)
        
        # 3. 신혼·신생아 II (60~85㎡) - 학교/공원/편의시설
        newlywed_ii_score = base_score
        if school_dist < 600:
            newlywed_ii_score += 18
        elif school_dist < 1200:
            newlywed_ii_score += 10
        
        if subway_dist < 1000:
            newlywed_ii_score += 8
        
        # 용도지역 가산점
        if zone_info.zone_type in ["제2종일반주거지역", "제3종일반주거지역"]:
            newlywed_ii_score += 5
        
        newlywed_ii_score = min(newlywed_ii_score, 100)
        scores["신혼·신생아 II"] = round(newlywed_ii_score, 1)
        
        # 4. 다자녀형 - 학교/공원/커뮤니티
        multichl_score = base_score
        if school_dist < 400:
            multichl_score += 22
        elif school_dist < 800:
            multichl_score += 14
        
        # 넓은 면적 선호 (건축 규모 반영)
        if building_capacity.units >= 30:
            multichl_score += 8
        
        # 안전한 주거 환경 (주거지역 가산)
        if "주거지역" in zone_info.zone_type:
            multichl_score += 7
        
        multichl_score = min(multichl_score, 100)
        scores["다자녀"] = round(multichl_score, 1)
        
        # 5. 고령자형 - 병원/복지시설/대중교통
        elderly_score = base_score
        if hospital_dist < 500:
            elderly_score += 25
        elif hospital_dist < 1000:
            elderly_score += 15
        elif hospital_dist < 1500:
            elderly_score += 8
        
        if subway_dist < 600:
            elderly_score += 12
        elif subway_dist < 1200:
            elderly_score += 6
        
        elderly_score += min(elderly_ratio * 1.2, 18)  # 고령인구 비율
        elderly_score = min(elderly_score, 100)
        scores["고령자"] = round(elderly_score, 1)
        
        # 6. 일반형 - 균형잡힌 입지 조건
        general_score = base_score
        if subway_dist < 800:
            general_score += 15
        elif subway_dist < 1500:
            general_score += 8
        
        if school_dist < 800:
            general_score += 10
        elif school_dist < 1500:
            general_score += 5
        
        # 적정 규모 (15~40세대)
        if 15 <= building_capacity.units <= 40:
            general_score += 10
        
        # 주거지역 가산
        if "주거지역" in zone_info.zone_type:
            general_score += 5
        
        general_score = min(general_score, 100)
        scores["일반"] = round(general_score, 1)
        
        # 7. 든든전세형 - 안정적 전세 수요 중심
        lease_score = base_score
        # 신혼부부와 청년층 모두 타겟
        lease_score += min((youth_ratio + elderly_ratio) * 0.3, 15)
        
        if subway_dist < 1000:
            lease_score += 12
        elif subway_dist < 1500:
            lease_score += 6
        
        # 학교/병원 균형
        if school_dist < 1000 or hospital_dist < 1000:
            lease_score += 8
        
        # 안정적인 주거환경
        if zone_info.zone_type in ["제2종일반주거지역", "제3종일반주거지역"]:
            lease_score += 7
        
        lease_score = min(lease_score, 100)
        scores["든든전세"] = round(lease_score, 1)
        
        return scores
