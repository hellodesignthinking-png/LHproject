"""
ZeroSite Phase 10: Base Report Engine

Single Engine Architecture:
- One decision object input
- Multiple template outputs
- Unified rendering pipeline
- Community injection support
- Phase 8 verified cost placeholder

Architecture:
    Input (Decision) → Community Injector → Template Renderer → Export (PDF/HTML/JSON)
"""

from typing import Dict, List, Optional, Literal, Any
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field
import json


class ParcelData(BaseModel):
    """Individual parcel data"""
    address: str
    land_area: float
    building_coverage_ratio: float
    floor_area_ratio: float
    land_use_zone: str
    current_land_price: Optional[float] = None


class CapexData(BaseModel):
    """Capital expenditure breakdown"""
    land_acquisition: float
    construction_cost: float
    design_supervision: float
    financing_cost: float
    contingency: float
    total_capex: float


class ROIData(BaseModel):
    """Return on Investment metrics"""
    roi_percent: float
    irr_percent: float
    npv: float
    payback_period_months: int
    annual_rental_income: float
    total_rental_income: float


class LHScoreData(BaseModel):
    """LH evaluation scores"""
    location_score: float
    transportation_score: float
    education_score: float
    amenities_score: float
    demand_score: float
    total_score: float
    grade: str  # A, B, C, D, E, F


class ComparableValuation(BaseModel):
    """Phase 7: Comparable valuation data"""
    estimated_price_per_m2: float
    estimated_total_price: float
    confidence_level: float
    comparable_transactions: int
    valuation_method: str
    price_range_min: float
    price_range_max: float


class VerifiedCostData(BaseModel):
    """Phase 8: Verified cost placeholder"""
    cost_per_m2: Optional[float] = None
    year: int = 2025
    region: Optional[str] = None
    unit_type: Optional[str] = None
    status: str = "pending_phase8"
    note: str = "Verified cost will be populated after Phase 8 implementation"


class CommunityModule(BaseModel):
    """Community facility module"""
    module_id: str
    module_name: str
    target_type: str  # Youth, Newlyweds, Senior, etc.
    facilities: List[str]
    estimated_cost: float
    space_requirement_m2: float
    narrative: str
    benefits: List[str]


class BuildingScaleData(BaseModel):
    """Building scale calculations"""
    max_building_area: float
    max_floor_area: float
    estimated_units: int
    avg_unit_size: float
    total_floors: int


class ZeroSiteDecision(BaseModel):
    """
    Unified decision object from Phase 0-7
    
    This is the SINGLE data model that Phase 10 consumes.
    Phase 10 does NOT modify this - only renders it.
    """
    # Basic info
    analysis_id: str = Field(default_factory=lambda: f"ZS_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Input data
    address: str
    parcels: List[ParcelData]
    
    # Strategy
    strategy: Literal["single", "merged"]
    recommended_type: str  # Youth, Newlyweds_TypeI, Newlyweds_TypeII, MultiChild, Senior
    
    # Phase 0-6 outputs
    scale: BuildingScaleData
    capex: CapexData
    roi: ROIData
    lh_score: LHScoreData
    
    # Phase 7 output
    comparable_valuation: ComparableValuation
    
    # Phase 8 placeholder
    verified_cost: VerifiedCostData = Field(default_factory=VerifiedCostData)
    
    # Phase 10 injection
    community: Optional[CommunityModule] = None
    
    # Final recommendation
    final_grade: str
    recommendation: Literal["GO", "IMPROVE", "NO_GO"]
    key_strengths: List[str] = []
    key_weaknesses: List[str] = []
    next_steps: List[str] = []


class ReportMetadata(BaseModel):
    """Report metadata"""
    report_type: Literal["lh_submission", "investor", "construction", "executive", "comparative"]
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = "11.0"
    report_id: str
    file_name: str
    pages: int
    format: Literal["pdf", "html", "json"]


class ReportExportResult(BaseModel):
    """Report export result"""
    success: bool
    report_type: str
    file_path: Optional[str] = None
    html_path: Optional[str] = None
    json_path: Optional[str] = None
    metadata: Optional[ReportMetadata] = None
    error_message: Optional[str] = None
    generation_time_seconds: float


class BaseReportEngine:
    """
    Base Report Engine for ZeroSite Phase 10
    
    Architecture:
        1. Load decision object (from Phase 0-7)
        2. Inject community module (from Phase 6.7)
        3. Render templates (5 types)
        4. Export to PDF/HTML/JSON
    
    Key Principles:
        - Single engine, multiple templates
        - No business logic in templates
        - Phase 0-7 outputs are read-only
        - Community injection is the only modification
        - All exports must be < 10 seconds total
    """
    
    def __init__(
        self,
        decision: ZeroSiteDecision,
        output_dir: Path = None,
        template_dir: Path = None
    ):
        """
        Initialize report engine
        
        Args:
            decision: Complete decision object from Phase 0-7
            output_dir: Directory for output files
            template_dir: Directory for templates
        """
        self.decision = decision
        self.output_dir = output_dir or Path("./reports")
        self.template_dir = template_dir or Path("./app/report_templates_v11")
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Report generation log
        self.generation_log: List[ReportExportResult] = []
    
    def inject_community(self, community_module: CommunityModule) -> None:
        """
        Inject community module into decision
        
        This is called BEFORE rendering templates.
        Community module is selected based on decision.recommended_type
        
        Args:
            community_module: Selected community facility module
        """
        self.decision.community = community_module
    
    def get_template_path(self, report_type: str) -> Path:
        """Get template file path for report type"""
        template_map = {
            "lh_submission": "lh_submission.html.jinja2",
            "investor": "investor_report.html.jinja2",
            "construction": "construction_report.html.jinja2",
            "executive": "executive_summary.html.jinja2",
            "comparative": "comparative_analysis.html.jinja2"
        }
        
        template_file = template_map.get(report_type)
        if not template_file:
            raise ValueError(f"Unknown report type: {report_type}")
        
        return self.template_dir / template_file
    
    def render_template(self, report_type: str, context: Dict[str, Any] = None) -> str:
        """
        Render template with decision data
        
        Args:
            report_type: Type of report to render
            context: Additional context data (optional)
        
        Returns:
            Rendered HTML string
        """
        # This will be implemented with Jinja2 in next phase
        # For now, return placeholder
        raise NotImplementedError("Template rendering will be implemented in Phase 10.3")
    
    def export_pdf(self, report_type: str) -> ReportExportResult:
        """
        Export report as PDF
        
        Args:
            report_type: Type of report to export
        
        Returns:
            Export result with file path
        """
        raise NotImplementedError("PDF export will be implemented in Phase 10.4")
    
    def export_html(self, report_type: str) -> ReportExportResult:
        """
        Export report as HTML
        
        Args:
            report_type: Type of report to export
        
        Returns:
            Export result with file path
        """
        raise NotImplementedError("HTML export will be implemented in Phase 10.5")
    
    def export_json(self, report_type: str) -> ReportExportResult:
        """
        Export report data as JSON
        
        Args:
            report_type: Type of report to export
        
        Returns:
            Export result with file path
        """
        try:
            start_time = datetime.now()
            
            # Generate file name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{report_type}_{timestamp}.json"
            file_path = self.output_dir / file_name
            
            # Create export data
            export_data = {
                "metadata": {
                    "report_type": report_type,
                    "generated_at": datetime.now().isoformat(),
                    "version": "11.0",
                    "analysis_id": self.decision.analysis_id
                },
                "decision": self.decision.dict(),
                "report_type": report_type
            }
            
            # Write JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            result = ReportExportResult(
                success=True,
                report_type=report_type,
                json_path=str(file_path),
                generation_time_seconds=generation_time
            )
            
            self.generation_log.append(result)
            return result
            
        except Exception as e:
            result = ReportExportResult(
                success=False,
                report_type=report_type,
                error_message=str(e),
                generation_time_seconds=0
            )
            self.generation_log.append(result)
            return result
    
    def export_all(
        self,
        formats: List[Literal["pdf", "html", "json"]] = ["pdf", "html", "json"]
    ) -> Dict[str, List[ReportExportResult]]:
        """
        Export all 5 report types in specified formats
        
        Args:
            formats: List of formats to export (pdf, html, json)
        
        Returns:
            Dictionary of results by format
        """
        report_types = [
            "lh_submission",
            "investor",
            "construction",
            "executive",
            "comparative"
        ]
        
        results = {
            "pdf": [],
            "html": [],
            "json": []
        }
        
        for report_type in report_types:
            if "pdf" in formats:
                try:
                    results["pdf"].append(self.export_pdf(report_type))
                except NotImplementedError:
                    # PDF export not yet implemented
                    pass
            
            if "html" in formats:
                try:
                    results["html"].append(self.export_html(report_type))
                except NotImplementedError:
                    # HTML export not yet implemented
                    pass
            
            if "json" in formats:
                results["json"].append(self.export_json(report_type))
        
        return results
    
    def get_generation_summary(self) -> Dict[str, Any]:
        """Get summary of all generated reports"""
        total_time = sum(r.generation_time_seconds for r in self.generation_log)
        success_count = sum(1 for r in self.generation_log if r.success)
        
        return {
            "total_reports": len(self.generation_log),
            "successful": success_count,
            "failed": len(self.generation_log) - success_count,
            "total_time_seconds": total_time,
            "average_time_seconds": total_time / len(self.generation_log) if self.generation_log else 0,
            "reports": [r.dict() for r in self.generation_log]
        }


# Factory function for easy usage
def create_report_engine(decision: ZeroSiteDecision) -> BaseReportEngine:
    """
    Factory function to create report engine
    
    Usage:
        decision = ZeroSiteDecision(...)
        engine = create_report_engine(decision)
        results = engine.export_all()
    """
    return BaseReportEngine(decision)
