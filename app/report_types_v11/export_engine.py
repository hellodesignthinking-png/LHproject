"""
ZeroSite Phase 10: Export Engine

Handles PDF, HTML, and JSON exports for all report types.

Key Features:
    - HTML to PDF conversion using WeasyPrint
    - Direct HTML export
    - JSON structured data export
    - File management and naming
    - Export result tracking
"""

from typing import Dict, List, Optional, Literal
from pathlib import Path
from datetime import datetime
import json
import time

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("Warning: WeasyPrint not available. PDF export will be disabled.")

from app.report_types_v11.base_report_engine import (
    ZeroSiteDecision,
    ReportMetadata,
    ReportExportResult
)
from app.report_types_v11.template_renderer import TemplateRenderer, get_template_name


class ExportEngine:
    """
    Unified export engine for PDF, HTML, and JSON
    
    Handles all export operations with consistent interface.
    """
    
    def __init__(
        self,
        output_dir: Path = None,
        template_dir: Path = None
    ):
        """
        Initialize export engine
        
        Args:
            output_dir: Directory for output files
            template_dir: Directory for templates
        """
        self.output_dir = output_dir or Path("./reports")
        self.template_dir = template_dir or Path("./app/report_templates_v11")
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize template renderer
        self.renderer = TemplateRenderer(self.template_dir)
        
        # Export tracking
        self.export_log: List[ReportExportResult] = []
    
    def _generate_filename(
        self,
        decision: ZeroSiteDecision,
        report_type: str,
        extension: str
    ) -> str:
        """
        Generate unique filename for export
        
        Format: {report_type}_{timestamp}_{analysis_id}.{extension}
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean analysis_id for filename
        clean_id = decision.analysis_id.replace("_", "")
        return f"{report_type}_{timestamp}_{clean_id}.{extension}"
    
    def render_html(
        self,
        decision: ZeroSiteDecision,
        report_type: str
    ) -> str:
        """
        Render HTML from template
        
        Args:
            decision: Decision object with all data
            report_type: Type of report to render
        
        Returns:
            Rendered HTML string
        """
        template_name = get_template_name(report_type)
        
        # Build context with decision and utilities
        context = {
            "decision": decision,
            "report_type": report_type,
            "generated_at": datetime.now().isoformat()
        }
        
        return self.renderer.render(template_name, context)
    
    def export_html(
        self,
        decision: ZeroSiteDecision,
        report_type: str
    ) -> ReportExportResult:
        """
        Export report as HTML file
        
        Args:
            decision: Decision object
            report_type: Type of report to export
        
        Returns:
            Export result with file path
        """
        start_time = time.time()
        
        try:
            # Render HTML
            html_content = self.render_html(decision, report_type)
            
            # Generate filename
            filename = self._generate_filename(decision, report_type, "html")
            file_path = self.output_dir / filename
            
            # Write HTML file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create metadata
            metadata = ReportMetadata(
                report_type=report_type,
                report_id=decision.analysis_id,
                file_name=filename,
                pages=1,  # HTML doesn't have page count
                format="html"
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            result = ReportExportResult(
                success=True,
                report_type=report_type,
                html_path=str(file_path),
                metadata=metadata,
                generation_time_seconds=generation_time
            )
            
            self.export_log.append(result)
            return result
            
        except Exception as e:
            end_time = time.time()
            generation_time = end_time - start_time
            
            result = ReportExportResult(
                success=False,
                report_type=report_type,
                error_message=f"HTML export failed: {str(e)}",
                generation_time_seconds=generation_time
            )
            
            self.export_log.append(result)
            return result
    
    def export_pdf(
        self,
        decision: ZeroSiteDecision,
        report_type: str
    ) -> ReportExportResult:
        """
        Export report as PDF file
        
        Uses WeasyPrint for HTML to PDF conversion.
        
        Args:
            decision: Decision object
            report_type: Type of report to export
        
        Returns:
            Export result with file path
        """
        start_time = time.time()
        
        if not WEASYPRINT_AVAILABLE:
            result = ReportExportResult(
                success=False,
                report_type=report_type,
                error_message="WeasyPrint not available. Install with: pip install weasyprint",
                generation_time_seconds=0
            )
            self.export_log.append(result)
            return result
        
        try:
            # Render HTML first
            html_content = self.render_html(decision, report_type)
            
            # Generate filename
            filename = self._generate_filename(decision, report_type, "pdf")
            file_path = self.output_dir / filename
            
            # Convert HTML to PDF using WeasyPrint
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(str(file_path))
            
            # Create metadata
            metadata = ReportMetadata(
                report_type=report_type,
                report_id=decision.analysis_id,
                file_name=filename,
                pages=self._estimate_page_count(report_type),
                format="pdf"
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            result = ReportExportResult(
                success=True,
                report_type=report_type,
                file_path=str(file_path),
                metadata=metadata,
                generation_time_seconds=generation_time
            )
            
            self.export_log.append(result)
            return result
            
        except Exception as e:
            end_time = time.time()
            generation_time = end_time - start_time
            
            result = ReportExportResult(
                success=False,
                report_type=report_type,
                error_message=f"PDF export failed: {str(e)}",
                generation_time_seconds=generation_time
            )
            
            self.export_log.append(result)
            return result
    
    def export_json(
        self,
        decision: ZeroSiteDecision,
        report_type: str
    ) -> ReportExportResult:
        """
        Export report data as JSON file
        
        Args:
            decision: Decision object
            report_type: Type of report to export
        
        Returns:
            Export result with file path
        """
        start_time = time.time()
        
        try:
            # Generate filename
            filename = self._generate_filename(decision, report_type, "json")
            file_path = self.output_dir / filename
            
            # Create export data
            export_data = {
                "metadata": {
                    "report_type": report_type,
                    "generated_at": datetime.now().isoformat(),
                    "version": "11.0",
                    "analysis_id": decision.analysis_id
                },
                "decision": decision.dict(),
                "report_type": report_type
            }
            
            # Write JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            # Create metadata
            metadata = ReportMetadata(
                report_type=report_type,
                report_id=decision.analysis_id,
                file_name=filename,
                pages=0,  # JSON doesn't have pages
                format="json"
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            result = ReportExportResult(
                success=True,
                report_type=report_type,
                json_path=str(file_path),
                metadata=metadata,
                generation_time_seconds=generation_time
            )
            
            self.export_log.append(result)
            return result
            
        except Exception as e:
            end_time = time.time()
            generation_time = end_time - start_time
            
            result = ReportExportResult(
                success=False,
                report_type=report_type,
                error_message=f"JSON export failed: {str(e)}",
                generation_time_seconds=generation_time
            )
            
            self.export_log.append(result)
            return result
    
    def export_all_formats(
        self,
        decision: ZeroSiteDecision,
        report_type: str,
        formats: List[Literal["pdf", "html", "json"]] = ["pdf", "html", "json"]
    ) -> Dict[str, ReportExportResult]:
        """
        Export report in multiple formats
        
        Args:
            decision: Decision object
            report_type: Type of report to export
            formats: List of formats to export
        
        Returns:
            Dictionary of results by format
        """
        results = {}
        
        if "pdf" in formats:
            results["pdf"] = self.export_pdf(decision, report_type)
        
        if "html" in formats:
            results["html"] = self.export_html(decision, report_type)
        
        if "json" in formats:
            results["json"] = self.export_json(decision, report_type)
        
        return results
    
    def export_all_report_types(
        self,
        decision: ZeroSiteDecision,
        formats: List[Literal["pdf", "html", "json"]] = ["pdf", "html"]
    ) -> Dict[str, Dict[str, ReportExportResult]]:
        """
        Export all 5 report types in specified formats
        
        This is the main function for bulk export.
        
        Args:
            decision: Decision object
            formats: List of formats to export
        
        Returns:
            Nested dictionary: {report_type: {format: result}}
        """
        report_types = [
            "lh_submission",
            "investor",
            "construction",
            "executive",
            "comparative"
        ]
        
        results = {}
        
        for report_type in report_types:
            results[report_type] = self.export_all_formats(
                decision,
                report_type,
                formats
            )
        
        return results
    
    def _estimate_page_count(self, report_type: str) -> int:
        """Estimate page count for each report type"""
        page_estimates = {
            "lh_submission": 10,
            "investor": 6,
            "construction": 8,
            "executive": 2,
            "comparative": 6
        }
        return page_estimates.get(report_type, 5)
    
    def get_export_summary(self) -> Dict[str, any]:
        """Get summary of all exports"""
        total_time = sum(r.generation_time_seconds for r in self.export_log)
        success_count = sum(1 for r in self.export_log if r.success)
        
        return {
            "total_exports": len(self.export_log),
            "successful": success_count,
            "failed": len(self.export_log) - success_count,
            "total_time_seconds": total_time,
            "average_time_seconds": total_time / len(self.export_log) if self.export_log else 0,
            "exports": [r.dict() for r in self.export_log]
        }
    
    def clear_log(self):
        """Clear export log"""
        self.export_log = []


# Convenience functions
def export_single_report(
    decision: ZeroSiteDecision,
    report_type: str,
    format: Literal["pdf", "html", "json"] = "pdf",
    output_dir: Path = None
) -> ReportExportResult:
    """
    Export a single report in one format
    
    Usage:
        result = export_single_report(decision, "executive", "pdf")
        print(f"PDF generated: {result.file_path}")
    """
    engine = ExportEngine(output_dir=output_dir)
    
    if format == "pdf":
        return engine.export_pdf(decision, report_type)
    elif format == "html":
        return engine.export_html(decision, report_type)
    elif format == "json":
        return engine.export_json(decision, report_type)
    else:
        raise ValueError(f"Unknown format: {format}")


def export_all_reports(
    decision: ZeroSiteDecision,
    formats: List[Literal["pdf", "html", "json"]] = ["pdf", "html"],
    output_dir: Path = None
) -> Dict[str, Dict[str, ReportExportResult]]:
    """
    Export all 5 report types in specified formats
    
    This is the main convenience function for Phase 10.
    
    Usage:
        results = export_all_reports(decision, ["pdf", "html"])
        
        for report_type, format_results in results.items():
            for format_type, result in format_results.items():
                if result.success:
                    print(f"✓ {report_type}.{format_type}: {result.file_path}")
    """
    engine = ExportEngine(output_dir=output_dir)
    return engine.export_all_report_types(decision, formats)
