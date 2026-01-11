"""
ZeroSite Report Generator Service
==================================

Aggregates M1-M6 analysis data into comprehensive reports.

Author: ZeroSite Phase 3 Team
Date: 2026-01-11
Version: 1.0
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generate comprehensive analysis reports from M1-M6 data
    """
    
    def __init__(self):
        self.report_version = "3.0"
        logger.info("📊 Report Generator initialized")
    
    def generate_final_report(
        self,
        project_id: str,
        project_name: str,
        address: str,
        m1_data: Dict[str, Any],
        m2_data: Dict[str, Any],
        m3_data: Dict[str, Any],
        m4_data: Dict[str, Any],
        m5_data: Dict[str, Any],
        m6_data: Dict[str, Any],
        context_id: str,
        verification_log: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate final comprehensive report
        
        Args:
            project_id: Project identifier
            project_name: Project name
            address: Property address
            m1_data: M1 land information
            m2_data: M2 valuation data
            m3_data: M3 housing type data
            m4_data: M4 building scale data
            m5_data: M5 feasibility data
            m6_data: M6 LH review data
            context_id: Context identifier
            verification_log: Verification history
            
        Returns:
            Complete report dictionary
        """
        
        logger.info(f"📊 Generating final report for project {project_id}")
        
        # Generate report timestamp
        generated_at = datetime.now().isoformat()
        
        # Create executive summary
        executive_summary = self._generate_executive_summary(
            address=address,
            m2_data=m2_data,
            m3_data=m3_data,
            m4_data=m4_data,
            m5_data=m5_data,
            m6_data=m6_data
        )
        
        # Compile report sections
        report = {
            "report_metadata": {
                "report_version": self.report_version,
                "project_id": project_id,
                "project_name": project_name,
                "context_id": context_id,
                "generated_at": generated_at,
                "generated_by": "ZeroSite Decision OS v3.0"
            },
            
            "executive_summary": executive_summary,
            
            "section_1_land_information": self._format_m1_section(m1_data),
            "section_2_valuation": self._format_m2_section(m2_data),
            "section_3_housing_type": self._format_m3_section(m3_data),
            "section_4_building_scale": self._format_m4_section(m4_data),
            "section_5_feasibility": self._format_m5_section(m5_data),
            "section_6_lh_review": self._format_m6_section(m6_data),
            
            "appendix": {
                "verification_log": verification_log or [],
                "data_sources": self._collect_data_sources(m1_data, m2_data),
                "methodology": self._get_methodology_notes()
            }
        }
        
        logger.info(f"✅ Report generated successfully")
        
        return report
    
    def _generate_executive_summary(
        self,
        address: str,
        m2_data: Dict,
        m3_data: Dict,
        m4_data: Dict,
        m5_data: Dict,
        m6_data: Dict
    ) -> Dict[str, Any]:
        """Generate executive summary section"""
        
        # Extract key metrics
        land_value = m2_data.get('land_value', 0)
        unit_price = m2_data.get('unit_price_sqm', 0)
        confidence = m2_data.get('confidence', 0)
        
        housing_type = m3_data.get('selected_type', 'N/A')
        type_confidence = m3_data.get('confidence', 0)
        
        total_units = m4_data.get('legal_capacity', {}).get('total_units', 0)
        total_gfa = m4_data.get('legal_capacity', {}).get('total_gfa_sqm', 0)
        
        npv_public = m5_data.get('financial_metrics', {}).get('npv_public', 0)
        irr = m5_data.get('financial_metrics', {}).get('irr_public', 0)
        profitable = m5_data.get('profitability', {}).get('profitable', False)
        
        lh_decision = m6_data.get('decision', 'PENDING')
        lh_score = m6_data.get('total_score', 0)
        lh_grade = m6_data.get('grade', 'N/A')
        
        # Generate summary text
        summary_text = f"""
        ZeroSite has completed a comprehensive analysis of the property located at {address}.
        
        The land is valued at ₩{land_value:,.0f} (₩{unit_price:,.0f}/m²) with {confidence}% confidence.
        The recommended housing type is {housing_type} with {type_confidence}% suitability.
        
        The project proposes {total_units} units with {total_gfa:,.0f}m² total floor area.
        Financial analysis shows NPV of ₩{npv_public:,.0f} and IRR of {irr:.2f}%.
        
        LH Review: {lh_decision} (Score: {lh_score}/110, Grade: {lh_grade})
        """
        
        return {
            "summary_text": summary_text.strip(),
            "key_metrics": {
                "land_value": land_value,
                "unit_price_sqm": unit_price,
                "valuation_confidence": confidence,
                "housing_type": housing_type,
                "type_confidence": type_confidence,
                "total_units": total_units,
                "total_gfa_sqm": total_gfa,
                "npv_public": npv_public,
                "irr_public": irr,
                "profitable": profitable,
                "lh_decision": lh_decision,
                "lh_score": lh_score,
                "lh_grade": lh_grade
            },
            "recommendation": self._generate_recommendation(lh_decision, profitable)
        }
    
    def _generate_recommendation(self, lh_decision: str, profitable: bool) -> str:
        """Generate final recommendation text"""
        
        if lh_decision == "GO" and profitable:
            return "Strong recommendation to proceed. All criteria met."
        elif lh_decision == "CONDITIONAL":
            return "Conditional approval. Address specified conditions before proceeding."
        elif lh_decision == "REVIEW":
            return "Further review required. Consider alternative approaches."
        else:
            return "Not recommended at this time. Significant concerns identified."
    
    def _format_m1_section(self, m1_data: Dict) -> Dict[str, Any]:
        """Format M1 land information section"""
        return {
            "title": "M1: Land Information",
            "data": m1_data,
            "summary": f"Land area: {m1_data.get('area_sqm', 0):.2f}m² ({m1_data.get('area_pyeong', 0):.2f}평)"
        }
    
    def _format_m2_section(self, m2_data: Dict) -> Dict[str, Any]:
        """Format M2 valuation section"""
        return {
            "title": "M2: Land Valuation",
            "data": m2_data,
            "summary": f"Land value: ₩{m2_data.get('land_value', 0):,.0f}"
        }
    
    def _format_m3_section(self, m3_data: Dict) -> Dict[str, Any]:
        """Format M3 housing type section"""
        return {
            "title": "M3: Housing Type Selection",
            "data": m3_data,
            "summary": f"Selected type: {m3_data.get('selected_type', 'N/A')}"
        }
    
    def _format_m4_section(self, m4_data: Dict) -> Dict[str, Any]:
        """Format M4 building scale section"""
        legal = m4_data.get('legal_capacity', {})
        return {
            "title": "M4: Building Scale Analysis",
            "data": m4_data,
            "summary": f"Capacity: {legal.get('total_units', 0)} units, {legal.get('total_gfa_sqm', 0):.0f}m² GFA"
        }
    
    def _format_m5_section(self, m5_data: Dict) -> Dict[str, Any]:
        """Format M5 feasibility section"""
        financial = m5_data.get('financial_metrics', {})
        return {
            "title": "M5: Financial Feasibility",
            "data": m5_data,
            "summary": f"NPV: ₩{financial.get('npv_public', 0):,.0f}, IRR: {financial.get('irr_public', 0):.2f}%"
        }
    
    def _format_m6_section(self, m6_data: Dict) -> Dict[str, Any]:
        """Format M6 LH review section"""
        return {
            "title": "M6: LH Comprehensive Review",
            "data": m6_data,
            "summary": f"Decision: {m6_data.get('decision', 'PENDING')}, Score: {m6_data.get('total_score', 0)}/110"
        }
    
    def _collect_data_sources(self, m1_data: Dict, m2_data: Dict) -> List[Dict]:
        """Collect all data sources used"""
        
        sources = []
        
        # M1 data sources
        if m1_data.get('data_sources'):
            for source_type, source_name in m1_data['data_sources'].items():
                sources.append({
                    "module": "M1",
                    "type": source_type,
                    "source": source_name
                })
        
        # M2 data sources
        if m2_data.get('method'):
            sources.append({
                "module": "M2",
                "type": "valuation_method",
                "source": m2_data['method']
            })
        
        return sources
    
    def _get_methodology_notes(self) -> Dict[str, str]:
        """Get methodology documentation"""
        
        return {
            "M1": "Land information collected from government APIs (VWorld, MOLIT)",
            "M2": "4-Factor Enhanced Transaction Comparison Method",
            "M3": "Multi-criteria housing type selection algorithm",
            "M4": "LH standard capacity calculation with parking optimization",
            "M5": "Discounted cash flow analysis with risk adjustment",
            "M6": "110-point LH evaluation criteria (location, scale, feasibility, compliance)"
        }


# Singleton instance
report_generator = ReportGenerator()
