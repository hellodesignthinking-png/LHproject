"""
ZeroSite Phase 11: Integration Engine

Connects Architecture Module with:
- Phase 2: Financial Engine (CAPEX/OPEX/ROI)
- Phase 3: LH Score Engine (100-point evaluation)

This enables:
- Design → Business Viability (자동 사업성 계산)
- Design → LH Evaluation (자동 LH 평가)

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.1
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .models import BuildingDesign, DesignStrategy, SupplyType
from ..services.financial_engine_v7_4 import run_full_financial_analysis
from ..lh_score_mapper_v11 import LHScoreMapper, LHScoreBreakdown

logger = logging.getLogger(__name__)


@dataclass
class IntegratedDesignAnalysis:
    """통합 설계 분석 결과"""
    
    # 설계 정보
    design: BuildingDesign
    strategy: DesignStrategy
    
    # 재무 분석 (Phase 2)
    financial_result: Dict[str, Any]
    capex: float
    opex: float
    noi: float
    roi: float
    irr: float
    cap_rate: float
    project_rating: str  # A/B/C/D
    
    # LH 평가 (Phase 3)
    lh_score_breakdown: LHScoreBreakdown
    lh_total_score: float
    lh_grade: str  # A/B/C/D/F
    
    # 종합 판정
    overall_decision: str  # GO/CONDITIONAL/REVISE
    recommendation: str
    confidence: float


class IntegrationEngine:
    """
    Phase 2 & 3 통합 엔진
    
    Architecture Module의 설계안을 받아서:
    1. Financial Engine으로 CAPEX/OPEX/ROI 자동 계산
    2. LH Score Engine으로 100점 평가 자동 수행
    3. 종합 판정 및 추천
    """
    
    def __init__(self):
        """Initialize integration engine"""
        self.lh_score_mapper = LHScoreMapper()
        logger.info("🔗 Integration Engine initialized (Phase 2 + Phase 3)")
    
    def analyze_design(
        self,
        design: BuildingDesign,
        land_area: float,
        land_appraisal_price: float,
        bcr: float,
        far: float,
        zone_type: str = "제2종일반주거지역",
        housing_type: str = "Newlyweds_TypeII",
        address: str = "",
        pseudo_data: Optional[Dict] = None
    ) -> IntegratedDesignAnalysis:
        """
        설계안에 대한 통합 분석 수행
        
        Args:
            design: BuildingDesign 객체
            land_area: 대지면적 (㎡)
            land_appraisal_price: 토지 감정평가액 (원)
            bcr: 건폐율 (%)
            far: 용적률 (%)
            zone_type: 용도지역
            housing_type: LH 주택 유형 (기본: 신혼부부형II)
            address: 대지 주소
            pseudo_data: Pseudo-Data 엔진 결과 (선택)
        
        Returns:
            IntegratedDesignAnalysis: 통합 분석 결과
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🔍 Integrated Analysis: {design.strategy.value} design")
        logger.info(f"{'='*80}")
        
        # ========================================
        # Step 1: Financial Analysis (Phase 2)
        # ========================================
        logger.info("💰 Step 1: Financial Engine (Phase 2)")
        
        financial_result = self._run_financial_analysis(
            design=design,
            land_area=land_area,
            land_appraisal_price=land_appraisal_price,
            housing_type=housing_type,
            address=address
        )
        
        # Extract key metrics
        capex = financial_result.get("total_capex", 0)
        opex = financial_result.get("annual_opex", 0)
        noi = financial_result.get("annual_noi", 0)
        roi = financial_result.get("roi", 0)
        irr = financial_result.get("irr_10yr", 0)
        cap_rate = financial_result.get("cap_rate", 0)
        project_rating = financial_result.get("project_rating", "C")
        
        logger.info(f"  ✅ Total CapEx: ₩{capex:,.0f}")
        logger.info(f"  ✅ Annual OpEx: ₩{opex:,.0f}")
        logger.info(f"  ✅ Annual NOI: ₩{noi:,.0f}")
        logger.info(f"  ✅ ROI: {roi:.2f}%")
        logger.info(f"  ✅ IRR (10yr): {irr:.2f}%")
        logger.info(f"  ✅ Cap Rate: {cap_rate:.2f}%")
        logger.info(f"  ✅ Project Rating: {project_rating}")
        
        # ========================================
        # Step 2: LH Score Evaluation (Phase 3)
        # ========================================
        logger.info("\n🏆 Step 2: LH Score Engine (Phase 3)")
        
        # Prepare analysis_result for LH Score
        analysis_result = self._prepare_analysis_result(
            design=design,
            land_area=land_area,
            bcr=bcr,
            far=far,
            zone_type=zone_type,
            financial_result=financial_result,
            land_appraisal_price=land_appraisal_price
        )
        
        # Prepare unit_analysis
        unit_analysis = self._prepare_unit_analysis(design)
        
        # Use provided pseudo_data or generate default
        if pseudo_data is None:
            pseudo_data = self._generate_default_pseudo_data(address)
        
        # Calculate LH Score
        lh_score_breakdown = self.lh_score_mapper.calculate_lh_score(
            analysis_result=analysis_result,
            unit_analysis=unit_analysis,
            pseudo_data=pseudo_data
        )
        
        logger.info(f"  ✅ LH Total Score: {lh_score_breakdown.total_score:.1f}/100")
        logger.info(f"  ✅ LH Grade: {lh_score_breakdown.grade.value}")
        logger.info(f"  📊 Breakdown:")
        logger.info(f"     - Location: {lh_score_breakdown.location_total:.1f}/25")
        logger.info(f"     - Feasibility: {lh_score_breakdown.feasibility_total:.1f}/30")
        logger.info(f"     - Policy: {lh_score_breakdown.policy_total:.1f}/20")
        logger.info(f"     - Financial: {lh_score_breakdown.financial_total:.1f}/15")
        logger.info(f"     - Risk: {lh_score_breakdown.risk_total:.1f}/10")
        
        # ========================================
        # Step 3: Overall Decision
        # ========================================
        logger.info("\n🎯 Step 3: Overall Decision")
        
        decision, recommendation, confidence = self._make_overall_decision(
            lh_score=lh_score_breakdown.total_score,
            lh_grade=lh_score_breakdown.grade.value,
            roi=roi,
            irr=irr,
            project_rating=project_rating
        )
        
        logger.info(f"  ✅ Decision: {decision}")
        logger.info(f"  ✅ Recommendation: {recommendation}")
        logger.info(f"  ✅ Confidence: {confidence:.1f}%")
        
        # ========================================
        # Return Integrated Result
        # ========================================
        return IntegratedDesignAnalysis(
            design=design,
            strategy=design.strategy,
            # Financial
            financial_result=financial_result,
            capex=capex,
            opex=opex,
            noi=noi,
            roi=roi,
            irr=irr,
            cap_rate=cap_rate,
            project_rating=project_rating,
            # LH Score
            lh_score_breakdown=lh_score_breakdown,
            lh_total_score=lh_score_breakdown.total_score,
            lh_grade=lh_score_breakdown.grade.value,
            # Overall
            overall_decision=decision,
            recommendation=recommendation,
            confidence=confidence
        )
    
    def _run_financial_analysis(
        self,
        design: BuildingDesign,
        land_area: float,
        land_appraisal_price: float,
        housing_type: str,
        address: str
    ) -> Dict[str, Any]:
        """Run Phase 2 Financial Engine"""
        
        # Map supply type to unit_type for financial engine
        unit_type_map = {
            SupplyType.YOUTH: "청년",
            SupplyType.NEWLYWED: "신혼부부",
            SupplyType.SENIOR: "고령자",
            SupplyType.GENERAL: "일반",
            SupplyType.MIXED: "혼합"
        }
        
        unit_type = unit_type_map.get(design.supply_type, "일반")
        
        # Prepare params for financial engine
        params = {
            # Required params
            "land_area": land_area,
            "address": address or "서울특별시 강남구",
            "unit_type": unit_type,
            
            # Optional params
            "construction_type": "standard",
            "land_appraisal_price": land_appraisal_price,
            "housing_type": housing_type,
        }
        
        try:
            result = run_full_financial_analysis(**params)
            
            # Extract metrics from result
            capex_data = result.get("capex", {})
            opex_data = result.get("opex", {})
            noi_data = result.get("noi", {})
            returns_data = result.get("returns", {})
            
            # Get values (with fallback to simplified calculation if needed)
            total_capex = capex_data.get("total_capex", 0)
            annual_opex = opex_data.get("year1_total_opex", 0)
            annual_noi = noi_data.get("noi", 0)
            roi = returns_data.get("roi", 0)
            irr = returns_data.get("irr", 0)
            cap_rate = returns_data.get("cap_rate", 0)
            
            # 🔧 TEMPORARY FIX: If financial engine returns invalid values, use simplified estimation
            # TODO: Fix financial engine integration to work properly with design parameters
            if total_capex == 0 or total_capex > land_appraisal_price * 100:  # Unrealistic values
                logger.warning("⚠️ Using simplified financial estimation (temporary)")
                
                # Simplified CAPEX estimation
                # Land: appraisal price
                # Construction: ~3.5M KRW/㎡ * GFA
                # Indirect costs: ~20%
                construction_cost = design.volume.total_gfa * 3_500_000
                total_capex = land_appraisal_price + construction_cost * 1.2
                
                # Simplified OPEX (3% of CAPEX annually)
                annual_opex = total_capex * 0.03
                
                # Simplified NOI (rental income - opex)
                # Assume 50,000 KRW/㎡/month rent
                annual_rental_income = design.volume.total_gfa * 50_000 * 12 * 0.8  # 80% occupancy
                annual_noi = annual_rental_income - annual_opex
                
                # Calculate returns
                roi = (annual_noi / total_capex) * 100 if total_capex > 0 else 0
                cap_rate = roi
                irr = roi * 0.15  # Rough estimate
            
            return {
                "total_capex": total_capex,
                "annual_opex": annual_opex,
                "annual_noi": annual_noi,
                "roi": roi,
                "irr_10yr": irr,
                "cap_rate": cap_rate,
                "project_rating": result.get("project_rating", "C")
            }
        except Exception as e:
            logger.error(f"❌ Financial analysis failed: {e}")
            
            # Fallback to simplified estimation
            logger.warning("⚠️ Using fallback simplified financial estimation")
            
            construction_cost = design.volume.total_gfa * 3_500_000
            total_capex = land_appraisal_price + construction_cost * 1.2
            annual_opex = total_capex * 0.03
            annual_rental_income = design.volume.total_gfa * 50_000 * 12 * 0.8
            annual_noi = annual_rental_income - annual_opex
            roi = (annual_noi / total_capex) * 100 if total_capex > 0 else 0
            
            return {
                "total_capex": total_capex,
                "annual_opex": annual_opex,
                "annual_noi": annual_noi,
                "roi": roi,
                "irr_10yr": roi * 0.15,
                "cap_rate": roi,
                "project_rating": "C"
            }
    
    def _prepare_analysis_result(
        self,
        design: BuildingDesign,
        land_area: float,
        bcr: float,
        far: float,
        zone_type: str,
        financial_result: Dict,
        land_appraisal_price: float
    ) -> Dict[str, Any]:
        """Prepare analysis_result for LH Score Mapper"""
        
        return {
            "land_info": {
                "land_area": land_area,
                "land_appraisal_price": land_appraisal_price,
                "zone_type": zone_type,
                "building_coverage_ratio": bcr,
                "floor_area_ratio": far
            },
            "development_plan": {
                "unit_count": design.total_units,
                "max_floors": design.volume.floor_count,
                "total_gfa": design.volume.total_gfa,
                "parking_spaces": design.parking.provided_spots
            },
            "financial_result": {
                "irr_10yr": financial_result.get("irr_10yr", 0),
                "roi": financial_result.get("roi", 0),
                "cap_rate": financial_result.get("cap_rate", 0),
                "total_capex": financial_result.get("total_capex", 0),
                "annual_noi": financial_result.get("annual_noi", 0)
            },
            "risk_assessment": {
                "overall_risk": self._assess_risk_level(design, financial_result)
            }
        }
    
    def _prepare_unit_analysis(self, design: BuildingDesign) -> Dict[str, Any]:
        """Prepare unit_analysis for LH Score Mapper"""
        
        # Map SupplyType to recommended_type
        supply_type_map = {
            SupplyType.YOUTH: "youth",
            SupplyType.NEWLYWED: "newlywed",
            SupplyType.SENIOR: "senior",
            SupplyType.GENERAL: "general",
            SupplyType.MIXED: "mixed"
        }
        
        recommended_type = supply_type_map.get(
            design.supply_type,
            "general"
        )
        
        # Calculate confidence based on strategy
        confidence_map = {
            DesignStrategy.STABLE: 95,   # High confidence
            DesignStrategy.STANDARD: 90,  # High confidence
            DesignStrategy.PROFIT: 85     # Good confidence
        }
        
        confidence = confidence_map.get(design.strategy, 85)
        
        return {
            "recommended_type": recommended_type,
            "confidence": confidence,
            "unit_mix": [
                {
                    "type_name": unit.name,
                    "area_sqm": unit.size_sqm,
                    "count": unit.count
                }
                for unit in design.unit_mix
            ]
        }
    
    def _generate_default_pseudo_data(self, address: str) -> Dict[str, Any]:
        """Generate default pseudo data if not provided"""
        
        # Extract region from address for basic categorization
        is_seoul = "서울" in address
        is_gangnam = any(x in address for x in ["강남", "서초", "송파", "분당"])
        
        # Default values based on region
        if is_gangnam:
            # Premium location
            return {
                "education": {
                    "elementary": {"count": 5},
                    "middle": {"count": 3},
                    "high": {"count": 2},
                    "university": {"count": 2}
                },
                "transportation": {
                    "subway": {"lines": ["2호선", "신분당선"]},
                    "bus": {"total_routes": 30}
                },
                "convenience": {
                    "shopping": {
                        "large_marts": {"count": 3},
                        "convenience_stores": {"count": 40}
                    },
                    "dining": {
                        "restaurants": {"count": 150}
                    }
                }
            }
        elif is_seoul:
            # Seoul (non-Gangnam)
            return {
                "education": {
                    "elementary": {"count": 3},
                    "middle": {"count": 2},
                    "high": {"count": 1},
                    "university": {"count": 1}
                },
                "transportation": {
                    "subway": {"lines": ["6호선"]},
                    "bus": {"total_routes": 20}
                },
                "convenience": {
                    "shopping": {
                        "large_marts": {"count": 2},
                        "convenience_stores": {"count": 25}
                    },
                    "dining": {
                        "restaurants": {"count": 80}
                    }
                }
            }
        else:
            # Other regions
            return {
                "education": {
                    "elementary": {"count": 2},
                    "middle": {"count": 1},
                    "high": {"count": 1},
                    "university": {"count": 0}
                },
                "transportation": {
                    "subway": {"lines": []},
                    "bus": {"total_routes": 15}
                },
                "convenience": {
                    "shopping": {
                        "large_marts": {"count": 1},
                        "convenience_stores": {"count": 15}
                    },
                    "dining": {
                        "restaurants": {"count": 50}
                    }
                }
            }
    
    def _assess_risk_level(self, design: BuildingDesign, financial_result: Dict) -> str:
        """Assess overall risk level"""
        
        roi = financial_result.get("roi", 0)
        irr = financial_result.get("irr_10yr", 0)
        
        # High performance = Low risk
        if roi >= 35 and irr >= 4:
            return "LOW"
        elif roi >= 25 and irr >= 3:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _make_overall_decision(
        self,
        lh_score: float,
        lh_grade: str,
        roi: float,
        irr: float,
        project_rating: str
    ) -> tuple:
        """Make overall investment decision"""
        
        # Decision logic
        if lh_score >= 80 and roi >= 30 and irr >= 3.5:
            decision = "GO"
            recommendation = "✅ 우수한 LH 점수와 재무 지표로 사업 추진 강력 권장"
            confidence = 95
        
        elif lh_score >= 70 and roi >= 25 and irr >= 3.0:
            decision = "GO"
            recommendation = "✅ 양호한 평가 결과로 사업 추진 권장"
            confidence = 85
        
        elif lh_score >= 60 and roi >= 20:
            decision = "CONDITIONAL"
            recommendation = "🟡 조건부 추진 권장 - 일부 지표 개선 후 진행"
            confidence = 70
        
        elif lh_score >= 50 and roi >= 15:
            decision = "REVISE"
            recommendation = "🟠 재검토 권장 - 설계 수정 또는 조건 변경 필요"
            confidence = 55
        
        else:
            decision = "STOP"
            recommendation = "🔴 사업 중단 권장 - 현재 조건으로는 수익성/평가 부족"
            confidence = 40
        
        return decision, recommendation, confidence


# ============================================================
# Usage Example
# ============================================================

if __name__ == "__main__":
    from .design_generator import DesignGenerator
    
    # Example: Generate and analyze designs
    generator = DesignGenerator(
        address="서울특별시 강남구 역삼동 123-45",
        land_params={
            "area": 1000.0,
            "bcr": 60,
            "far": 200,
            "max_floors": 15
        },
        supply_type=SupplyType.NEWLYWED
    )
    
    designs = generator.generate()
    
    # Integrate with Phase 2 & 3
    integration_engine = IntegrationEngine()
    
    for design in designs:
        analysis = integration_engine.analyze_design(
            design=design,
            land_area=1000.0,
            land_appraisal_price=9_000_000_000,  # 90억원
            bcr=60,
            far=200,
            zone_type="제2종일반주거지역",
            housing_type="Newlyweds_TypeII",
            address="서울특별시 강남구 역삼동 123-45"
        )
        
        print(f"\n{'='*80}")
        print(f"Strategy: {analysis.strategy.value}")
        print(f"LH Score: {analysis.lh_total_score:.1f}/100 (Grade: {analysis.lh_grade})")
        print(f"ROI: {analysis.roi:.2f}% | IRR: {analysis.irr:.2f}%")
        print(f"Decision: {analysis.overall_decision}")
        print(f"Recommendation: {analysis.recommendation}")
        print(f"{'='*80}")
