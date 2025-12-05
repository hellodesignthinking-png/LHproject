"""
ZeroSite v11.0 Ultra Professional Report Generator
===================================================
Phase 2 Complete Integration:
- v9.1 Analysis Engine (automated 13-field calculation)
- v10.0 Professional Report Structure (8 Parts, 25+ sections)
- v11.0 Unit-Type Suitability Analysis (5 types x 6 criteria)
- Pseudo-Data Auto-Fill Engine (realistic facility/demographic data)
- Feasibility Check Layer (recommendation validation)

Report Structure (40-45 pages):
Part 1: Executive Summary
Part 2: Site & Location Analysis (EXPANDED with detailed infrastructure)
Part 3: Regulatory & Development Framework
Part 4: Demand + Unit-Type Suitability Analysis (EXPANDED to 8-10 pages)
Part 5: Financial Analysis (EXPANDED with 3 scenarios)
Part 6: LH Evaluation Criteria
Part 7: Risk Assessment & Mitigation (EXPANDED with 6x6 matrix)
Part 8: Final Recommendation & Appendix (EXPANDED with comprehensive data)
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Import v11.0 modules
from app.unit_type_analyzer_v11 import (
    DemographicIntelligence,
    InfrastructureScoring,
    UnitTypeSuitabilityAnalyzer
)
from app.pseudo_data_engine_v11 import PseudoDataEngine
from app.feasibility_checker_v11 import FeasibilityChecker


class ReportGeneratorV11:
    """v11.0 Ultra Professional Report Generator"""
    
    def __init__(self):
        self.version = "11.0"
        self.report_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    def generate_html_report(self, analysis_result: Dict[str, Any]) -> str:
        """
        Generate comprehensive 40-45 page HTML report
        
        Args:
            analysis_result: v9.1 REAL analysis result containing:
                - basic_info, land_info, development_plan
                - lh_evaluation_result, financial_result
                - risk_assessment, final_recommendation
        
        Returns:
            HTML string (40-45 pages, PDF-ready)
        """
        
        # Extract data from analysis result
        basic = analysis_result.get("basic_info", {})
        land = analysis_result.get("land_info", {})
        dev_plan = analysis_result.get("development_plan", {})
        lh_eval = analysis_result.get("lh_evaluation_result", {})
        financial = analysis_result.get("financial_result", {})
        risk_assess = analysis_result.get("risk_assessment", {})
        final_rec = analysis_result.get("final_recommendation", {})
        
        # Basic parameters
        address = basic.get("address", "")
        coord = basic.get("coordinates", {})
        latitude = coord.get("latitude", 37.5665)
        longitude = coord.get("longitude", 126.9780)
        legal_dong_code = basic.get("legal_dong_code", "")
        
        land_area = land.get("land_area", 0)
        land_price = land.get("land_appraisal_price", 0)
        zone_type = land.get("zone_type", "")
        bcr = land.get("building_coverage_ratio", 0)
        far = land.get("floor_area_ratio", 0)
        
        max_floors = dev_plan.get("max_floors", 0)
        unit_count = dev_plan.get("unit_count", 0)
        parking_spaces = dev_plan.get("parking_spaces", 0)
        total_gfa = dev_plan.get("total_gross_floor_area", 0)
        
        lh_score = lh_eval.get("total_score", 0.0)
        lh_grade = lh_eval.get("grade", "C")
        
        irr = financial.get("irr_10yr", 0.0)
        roi = financial.get("roi", 0.0)
        npv = financial.get("npv_10yr", 0)
        total_investment = financial.get("total_investment", 0)
        
        risk_level = risk_assess.get("overall_risk", "MEDIUM")
        confidence = final_rec.get("confidence", 0.0)
        decision = final_rec.get("decision", "REVIEW")
        
        # ============================================================
        # Initialize v11.0 Engines
        # ============================================================
        
        # Pseudo-Data Engine
        pseudo_engine = PseudoDataEngine(
            address=address,
            coord={"latitude": latitude, "longitude": longitude}
        )
        pseudo_data = pseudo_engine.generate_comprehensive_report()
        
        # Unit-Type Suitability Analyzer
        unit_analyzer = UnitTypeSuitabilityAnalyzer(
            address=address,
            coord={"latitude": latitude, "longitude": longitude}
        )
        unit_analysis = unit_analyzer.analyze_all_unit_types()
        recommended_type = unit_analysis["recommended_type"]
        
        # Feasibility Checker
        feasibility_checker = FeasibilityChecker(
            land_area=land_area,
            bcr=bcr,
            far=far,
            zone_type=zone_type,
            max_floors=max_floors,
            unit_count=unit_count,
            total_gfa=total_gfa
        )
        feasibility_result = feasibility_checker.check_unit_type_feasibility(recommended_type)
        
        # Generate specialized sections
        unit_type_matrix_html = self._generate_unit_type_matrix(unit_analysis)
        unit_type_detail_html = self._generate_unit_type_detail(
            unit_analysis, pseudo_data, recommended_type
        )
        infrastructure_by_type_html = self._generate_infrastructure_by_type(pseudo_data)
        feasibility_html = self._generate_feasibility_section(feasibility_result)
        financial_scenarios_html = self._generate_financial_scenarios(irr, roi, npv, total_investment)
        risk_matrix_html = self._generate_risk_matrix_6x6(risk_level, confidence)
        appendix_html = self._generate_comprehensive_appendix(analysis_result, pseudo_data)
        
        # Generate HTML
        html = self._build_html_structure(
            # Basic info
            address=address,
            latitude=latitude,
            longitude=longitude,
            legal_dong_code=legal_dong_code,
            land_area=land_area,
            land_price=land_price,
            zone_type=zone_type,
            bcr=bcr,
            far=far,
            max_floors=max_floors,
            unit_count=unit_count,
            parking_spaces=parking_spaces,
            total_gfa=total_gfa,
            
            # Evaluation & Financial
            lh_score=lh_score,
            lh_grade=lh_grade,
            irr=irr,
            roi=roi,
            npv=npv,
            total_investment=total_investment,
            
            # Risk & Decision
            risk_level=risk_level,
            confidence=confidence,
            decision=decision,
            
            # v11.0 Data
            pseudo_data=pseudo_data,
            unit_analysis=unit_analysis,
            recommended_type=recommended_type,
            feasibility_result=feasibility_result,
            
            # HTML Sections
            unit_type_matrix_html=unit_type_matrix_html,
            unit_type_detail_html=unit_type_detail_html,
            infrastructure_by_type_html=infrastructure_by_type_html,
            feasibility_html=feasibility_html,
            financial_scenarios_html=financial_scenarios_html,
            risk_matrix_html=risk_matrix_html,
            appendix_html=appendix_html
        )
        
        return html
