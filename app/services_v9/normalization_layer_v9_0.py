"""
ZeroSite v9.0 Normalization Layer
- Engine 출력을 표준 스키마로 변환
- KeyError 방지 및 기본값 처리
- 데이터 품질 보장
"""

from typing import Dict, Any, List, Optional
from app.models_v9.standard_schema_v9_0 import (
    StandardAnalysisOutput,
    SiteInfo,
    GISResult,
    POIDistance,
    FinancialResult,
    LHScores,
    RiskAssessment,
    RiskItem,
    DemandResult,
    FinalRecommendation,
    AnalysisMode,
    ProjectGrade,
    DecisionType,
    RiskSeverity,
    RiskStatus,
    RiskCategory
)
import logging
import math

logger = logging.getLogger(__name__)


class NormalizationLayerV90:
    """
    v9.0 정규화 레이어
    - 각 Engine의 원시 출력을 표준 스키마로 변환
    - KeyError 방지 및 기본값 처리
    - 데이터 무결성 보장
    """
    
    def __init__(self):
        self.version = "v9.0"
    
    # ===== Site Info Normalization =====
    
    def normalize_site_info(self, raw_input: Dict[str, Any]) -> SiteInfo:
        """입력 데이터 → SiteInfo 변환"""
        try:
            land_area = float(raw_input.get("land_area", 0))
            
            # land_appraisal_price 기본값 처리 (지역별 평균 평당가 기준)
            land_appraisal_price_raw = raw_input.get("land_appraisal_price")
            if land_appraisal_price_raw is None or float(land_appraisal_price_raw) == 0:
                # 서울 평균 평당가 기준 (약 3,000만원/평 → 9,090,909원/m²)
                land_appraisal_price = 9_000_000.0
                logger.info(f"⚠️  감정평가액 미입력 → 기본값 적용: {land_appraisal_price:,.0f}원/m²")
            else:
                land_appraisal_price = float(land_appraisal_price_raw)
            
            return SiteInfo(
                address=raw_input.get("address", "주소 없음"),
                land_area=land_area,
                zone_type=raw_input.get("zone_type", "미지정"),
                land_appraisal_price=land_appraisal_price,
                total_land_price=land_area * land_appraisal_price,
                latitude=raw_input.get("latitude"),
                longitude=raw_input.get("longitude"),
                building_coverage_ratio=float(raw_input.get("building_coverage_ratio", 50.0)),
                floor_area_ratio=float(raw_input.get("floor_area_ratio", 200.0)),
                height_limit=raw_input.get("height_limit")
            )
        except Exception as e:
            logger.error(f"Site info normalization error: {e}")
            # 기본값 반환
            return SiteInfo(
                address="주소 오류",
                land_area=100.0,
                zone_type="미지정",
                land_appraisal_price=1000000,
                total_land_price=100000000,
                building_coverage_ratio=50.0,
                floor_area_ratio=200.0
            )
    
    # ===== GIS Normalization =====
    
    def normalize_gis_output(self, gis_raw: Dict[str, Any]) -> GISResult:
        """GIS Engine 출력 정규화"""
        try:
            pois_by_category = {}
            
            # 각 POI 카테고리 처리
            for category in ["elementary_schools", "middle_schools", "high_schools",
                            "subway_stations", "bus_stops", "hospitals", 
                            "supermarkets", "parks"]:
                items = gis_raw.get(category, [])
                normalized_pois = []
                
                for item in items:
                    try:
                        distance_m = self._safe_float(item.get("distance", 9999.0))
                        accessibility_score = self._safe_float(item.get("accessibility_score", 0.0))
                        
                        poi = POIDistance(
                            category=category,
                            name=item.get("name", "Unknown"),
                            distance_m=distance_m,
                            distance_display=self._format_distance(distance_m),
                            walk_time_min=self._calculate_walk_time(distance_m),
                            drive_time_min=self._calculate_drive_time(distance_m),
                            accessibility_score=accessibility_score,
                            interpretation=self._interpret_accessibility(accessibility_score)
                        )
                        normalized_pois.append(poi)
                    except Exception as e:
                        logger.warning(f"POI normalization error for {category}: {e}")
                        continue
                
                pois_by_category[category] = normalized_pois
            
            overall_score = self._safe_float(gis_raw.get("overall_accessibility_score", 50.0))
            
            return GISResult(
                elementary_schools=pois_by_category.get("elementary_schools", []),
                middle_schools=pois_by_category.get("middle_schools", []),
                high_schools=pois_by_category.get("high_schools", []),
                subway_stations=pois_by_category.get("subway_stations", []),
                bus_stops=pois_by_category.get("bus_stops", []),
                hospitals=pois_by_category.get("hospitals", []),
                supermarkets=pois_by_category.get("supermarkets", []),
                parks=pois_by_category.get("parks", []),
                overall_accessibility_score=min(max(overall_score, 0.0), 100.0),
                accessibility_grade=self._score_to_grade(overall_score)
            )
        except Exception as e:
            logger.error(f"GIS normalization error: {e}")
            return self._get_default_gis_result()
    
    # ===== Financial Normalization =====
    
    def normalize_financial_output(self, 
                                   financial_raw: Dict[str, Any],
                                   unit_count: int) -> FinancialResult:
        """Financial Engine 출력 정규화"""
        try:
            # 분석 모드 결정
            mode = AnalysisMode.LH_LINKED if unit_count >= 50 else AnalysisMode.STANDARD
            
            total_land_price = self._safe_float(financial_raw.get("total_land_price", 0.0))
            construction_cost_per_sqm = self._safe_float(financial_raw.get("construction_cost_per_sqm", 2500000.0))
            total_construction_cost = self._safe_float(financial_raw.get("total_construction_cost", 0.0))
            total_capex = self._safe_float(financial_raw.get("total_capex", 0.0))
            
            # LH 관련 데이터 (50세대 이상인 경우만)
            lh_purchase_price = None
            lh_purchase_price_per_sqm = None
            verified_cost = None
            
            if mode == AnalysisMode.LH_LINKED:
                lh_purchase_price = self._safe_float(financial_raw.get("lh_purchase_price"))
                lh_purchase_price_per_sqm = self._safe_float(financial_raw.get("lh_purchase_price_per_sqm"))
                verified_cost = self._safe_float(financial_raw.get("verified_cost"))
            
            # 수익성 지표
            annual_noi = self._safe_float(financial_raw.get("annual_noi", 0.0))
            cap_rate = self._safe_float(financial_raw.get("cap_rate", 0.0))
            roi_10yr = self._safe_float(financial_raw.get("roi_10yr", 0.0))
            irr_10yr = self._safe_float(financial_raw.get("irr_10yr", 0.0))
            
            # 사업성 점수 기반 등급
            business_score = self._safe_float(financial_raw.get("business_score", 50.0))
            overall_grade = self._score_to_grade(business_score * 2.5)  # 40점 만점 → 100점 환산
            
            return FinancialResult(
                total_land_price=total_land_price,
                construction_cost_per_sqm=construction_cost_per_sqm,
                total_construction_cost=total_construction_cost,
                total_capex=total_capex,
                analysis_mode=mode,
                lh_purchase_price=lh_purchase_price,
                lh_purchase_price_per_sqm=lh_purchase_price_per_sqm,
                verified_cost=verified_cost,
                annual_noi=annual_noi,
                cap_rate=cap_rate,
                roi_10yr=roi_10yr,
                irr_10yr=irr_10yr,
                unit_count=unit_count,
                unit_type_distribution=financial_raw.get("unit_type_distribution", {}),
                overall_grade=overall_grade,
                breakeven_year=financial_raw.get("breakeven_year")
            )
        except Exception as e:
            logger.error(f"Financial normalization error: {e}")
            return self._get_default_financial_result()
    
    # ===== LH Scores Normalization =====
    
    def normalize_lh_scores(self, lh_raw: Dict[str, Any]) -> LHScores:
        """LH Evaluation Engine 출력 정규화"""
        try:
            location_score = min(max(self._safe_float(lh_raw.get("location_score", 0.0)), 0.0), 35.0)
            scale_score = min(max(self._safe_float(lh_raw.get("scale_score", 0.0)), 0.0), 20.0)
            business_score = min(max(self._safe_float(lh_raw.get("business_score", 0.0)), 0.0), 40.0)
            regulation_score = min(max(self._safe_float(lh_raw.get("regulation_score", 0.0)), 0.0), 15.0)
            
            total = location_score + scale_score + business_score + regulation_score
            
            return LHScores(
                location_score=location_score,
                scale_score=scale_score,
                business_score=business_score,
                regulation_score=regulation_score,
                total_score=total,
                grade=self._total_score_to_grade(total)
            )
        except Exception as e:
            logger.error(f"LH scores normalization error: {e}")
            return LHScores(
                location_score=0.0,
                scale_score=0.0,
                business_score=0.0,
                regulation_score=0.0,
                total_score=0.0,
                grade=ProjectGrade.F
            )
    
    # ===== Risk Assessment Normalization =====
    
    def normalize_risk_assessment(self, risk_raw: Dict[str, Any]) -> RiskAssessment:
        """Risk Engine 출력 정규화"""
        try:
            all_risks_raw = risk_raw.get("all_risks", [])
            all_risks = []
            critical_risks = []
            
            pass_count = 0
            warning_count = 0
            fail_count = 0
            
            for risk_item in all_risks_raw:
                try:
                    risk = RiskItem(
                        id=risk_item.get("id", "UNKNOWN"),
                        category=RiskCategory(risk_item.get("category", "LEGAL")),
                        name=risk_item.get("name", "Unknown Risk"),
                        severity=RiskSeverity(risk_item.get("severity", "MEDIUM")),
                        status=RiskStatus(risk_item.get("status", "WARNING")),
                        description=risk_item.get("description", ""),
                        mitigation=risk_item.get("mitigation")
                    )
                    
                    all_risks.append(risk)
                    
                    # 카운트 집계
                    if risk.status == RiskStatus.PASS:
                        pass_count += 1
                    elif risk.status == RiskStatus.WARNING:
                        warning_count += 1
                    elif risk.status == RiskStatus.FAIL:
                        fail_count += 1
                    
                    # Critical 리스크 (HIGH severity + FAIL status)
                    if risk.severity == RiskSeverity.HIGH and risk.status == RiskStatus.FAIL:
                        critical_risks.append(risk)
                        
                except Exception as e:
                    logger.warning(f"Risk item normalization error: {e}")
                    continue
            
            # 전체 위험도 계산
            if fail_count >= 5:
                overall_level = "CRITICAL"
            elif fail_count >= 3:
                overall_level = "HIGH"
            elif fail_count >= 1 or warning_count >= 5:
                overall_level = "MEDIUM"
            else:
                overall_level = "LOW"
            
            return RiskAssessment(
                total_items=25,
                pass_count=pass_count,
                warning_count=warning_count,
                fail_count=fail_count,
                critical_risks=critical_risks,
                all_risks=all_risks,
                overall_risk_level=overall_level
            )
        except Exception as e:
            logger.error(f"Risk assessment normalization error: {e}")
            return RiskAssessment(
                total_items=25,
                pass_count=0,
                warning_count=0,
                fail_count=0,
                critical_risks=[],
                all_risks=[],
                overall_risk_level="UNKNOWN"
            )
    
    # ===== Demand Normalization =====
    
    def normalize_demand(self, demand_raw: Dict[str, Any]) -> DemandResult:
        """Demand Engine 출력 정규화"""
        try:
            return DemandResult(
                population_total=int(demand_raw.get("population_total", 0)),
                household_count=int(demand_raw.get("household_count", 0)),
                target_households=int(demand_raw.get("target_households", 0)),
                demand_score=min(max(self._safe_float(demand_raw.get("demand_score", 50.0)), 0.0), 100.0),
                demand_grade=self._score_to_grade(demand_raw.get("demand_score", 50.0)),
                recommended_unit_type=demand_raw.get("recommended_unit_type", "든든전세")
            )
        except Exception as e:
            logger.error(f"Demand normalization error: {e}")
            return DemandResult(
                population_total=0,
                household_count=0,
                target_households=0,
                demand_score=50.0,
                demand_grade="C",
                recommended_unit_type="든든전세"
            )
    
    # ===== Final Recommendation Normalization =====
    
    def generate_recommendation(self,
                               lh_scores: LHScores,
                               financial_result: FinancialResult,
                               risk_assessment: RiskAssessment) -> FinalRecommendation:
        """최종 의사결정 생성"""
        try:
            # 의사결정 로직
            total_score = lh_scores.total_score
            roi = financial_result.roi_10yr
            fail_count = risk_assessment.fail_count
            
            # 결정 알고리즘
            if total_score >= 80 and roi >= 10 and fail_count == 0:
                decision = DecisionType.PROCEED
                confidence = 90.0
            elif total_score >= 70 and roi >= 5 and fail_count <= 2:
                decision = DecisionType.PROCEED_WITH_CONDITIONS
                confidence = 75.0
            elif total_score >= 60 and roi >= 0 and fail_count <= 5:
                decision = DecisionType.REVISE
                confidence = 65.0
            else:
                decision = DecisionType.NOGO
                confidence = 50.0
            
            # 강점/약점 분석
            strengths = []
            weaknesses = []
            
            if lh_scores.location_score >= 28:
                strengths.append(f"우수한 입지 점수 ({lh_scores.location_score:.1f}/35점)")
            else:
                weaknesses.append(f"입지 점수 개선 필요 ({lh_scores.location_score:.1f}/35점)")
            
            if financial_result.roi_10yr >= 10:
                strengths.append(f"높은 수익성 (ROI {financial_result.roi_10yr:.1f}%)")
            elif financial_result.roi_10yr < 0:
                weaknesses.append(f"낮은 수익성 (ROI {financial_result.roi_10yr:.1f}%)")
            
            if fail_count == 0:
                strengths.append("리스크 항목 모두 통과")
            elif fail_count >= 3:
                weaknesses.append(f"중요 리스크 {fail_count}개 발생")
            
            # 실행 항목
            action_items = []
            if financial_result.roi_10yr < 5:
                action_items.append("공사비 절감 방안 검토")
                action_items.append("임대료 인상 가능성 분석")
            if fail_count > 0:
                action_items.append("리스크 완화 계획 수립")
            if lh_scores.total_score < 70:
                action_items.append("LH 평가 점수 개선 방안 마련")
            
            # 임원 요약
            executive_summary = (
                f"본 사업은 LH 평가 {lh_scores.total_score:.1f}점(등급 {lh_scores.grade.value}), "
                f"10년 ROI {financial_result.roi_10yr:.1f}%로 평가되며, "
                f"{decision.value} 의사결정을 권고합니다."
            )
            
            return FinalRecommendation(
                decision=decision,
                confidence_level=confidence,
                key_strengths=strengths,
                key_weaknesses=weaknesses,
                action_items=action_items if action_items else ["현재 상태 유지"],
                executive_summary=executive_summary
            )
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            return FinalRecommendation(
                decision=DecisionType.REVISE,
                confidence_level=50.0,
                key_strengths=[],
                key_weaknesses=["분석 오류 발생"],
                action_items=["상세 재검토 필요"],
                executive_summary="분석 중 오류가 발생하여 재검토가 필요합니다."
            )
    
    # ===== Helper Methods =====
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """안전한 float 변환 (infinity/NaN 방지)"""
        try:
            f = float(value) if value is not None else default
            if math.isinf(f) or math.isnan(f):
                return default
            return f
        except (ValueError, TypeError):
            return default
    
    def _format_distance(self, distance_m: float) -> str:
        """거리를 사람이 읽기 좋은 형식으로 변환"""
        if distance_m >= 10000:
            return "10km 이상"
        elif distance_m >= 2000:
            return f"{distance_m/1000:.1f}km"
        elif distance_m >= 1000:
            return f"{distance_m/1000:.2f}km"
        else:
            return f"{int(distance_m)}m"
    
    def _calculate_walk_time(self, distance_m: float) -> Optional[int]:
        """도보 시간 계산 (평균 속도 4km/h = 66.67m/min)"""
        if distance_m > 5000:  # 5km 이상은 도보 불가
            return None
        return int(distance_m / 66.67)
    
    def _calculate_drive_time(self, distance_m: float) -> Optional[int]:
        """차량 시간 계산 (평균 속도 30km/h = 500m/min, 도심 기준)"""
        return int(distance_m / 500)
    
    def _interpret_accessibility(self, score: float) -> str:
        """접근성 점수 해석"""
        if score >= 9.0:
            return "매우 우수"
        elif score >= 7.0:
            return "우수"
        elif score >= 5.0:
            return "보통"
        elif score >= 3.0:
            return "미흡"
        else:
            return "불량"
    
    def _score_to_grade(self, score: float) -> str:
        """점수를 등급으로 변환 (100점 만점 기준)"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _total_score_to_grade(self, total_score: float) -> ProjectGrade:
        """110점 만점 기준 등급 변환"""
        percentage = (total_score / 110.0) * 100
        grade_str = self._score_to_grade(percentage)
        return ProjectGrade(grade_str)
    
    def _get_default_gis_result(self) -> GISResult:
        """기본 GIS 결과 (오류 시)"""
        return GISResult(
            overall_accessibility_score=50.0,
            accessibility_grade="C"
        )
    
    def _get_default_financial_result(self) -> FinancialResult:
        """기본 Financial 결과 (오류 시)"""
        return FinancialResult(
            total_land_price=0.0,
            construction_cost_per_sqm=2500000.0,
            total_construction_cost=0.0,
            total_capex=0.0,
            analysis_mode=AnalysisMode.STANDARD,
            annual_noi=0.0,
            cap_rate=0.0,
            roi_10yr=0.0,
            irr_10yr=0.0,
            unit_count=0,
            overall_grade="F"
        )
