"""
Phase 10.5: PDF Exporter for LH Full Report
Exports complete HTML report to professional PDF with LH branding

Features:
- LH official branding (colors, fonts, logo)
- Professional page layout
- Header/Footer with page numbers
- Table of contents with hyperlinks
- High-quality chart embedding
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("Warning: WeasyPrint not available. PDF export will be limited.")

logger = logging.getLogger(__name__)

# LH Brand Guidelines
LH_BRAND = {
    'primary_color': '#2165D1',  # LH Blue
    'secondary_color': '#5B9BD5',  # Light Blue
    'accent_color': '#ED7D31',  # Orange
    'text_color': '#333333',  # Dark Gray
    'light_bg': '#F8F9FA',  # Light Background
    'font_family': 'Noto Sans KR, sans-serif'
}


class PDFExporterFull:
    """Export LH Full Report to professional PDF"""
    
    def __init__(self):
        """Initialize PDF exporter"""
        self.font_config = FontConfiguration() if WEASYPRINT_AVAILABLE else None
    
    def export_to_pdf(
        self,
        html_content: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Export HTML report to PDF with LH branding
        
        Args:
            html_content: Complete HTML content
            output_path: Output PDF file path
            metadata: Report metadata (title, author, etc.)
            
        Returns:
            Path to generated PDF file
        """
        if not WEASYPRINT_AVAILABLE:
            raise ImportError("WeasyPrint is required for PDF export. Install with: pip install weasyprint")
        
        logger.info(f"Exporting PDF to: {output_path}")
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add LH CSS styling
        styled_html = self._add_lh_styling(html_content)
        
        # Create HTML document
        html_doc = HTML(string=styled_html)
        
        # Generate PDF
        html_doc.write_pdf(
            output_path,
            stylesheets=[CSS(string=self._get_pdf_css())],
            font_config=self.font_config
        )
        
        logger.info(f"PDF exported successfully: {output_path}")
        return output_path
    
    def _add_lh_styling(self, html_content: str) -> str:
        """Add LH branding and styling to HTML"""
        # Wrap content in LH-branded HTML structure
        styled_html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>LH 신축매입임대 사업 타당성 분석 보고서</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {LH_BRAND['font_family']};
            color: {LH_BRAND['text_color']};
            line-height: 1.6;
            font-size: 11pt;
        }}
        
        /* Page layout */
        @page {{
            size: A4;
            margin: 2.5cm 2cm;
            
            @top-center {{
                content: "LH 신축매입임대 사업 타당성 분석 보고서";
                font-size: 9pt;
                color: {LH_BRAND['primary_color']};
                border-bottom: 1px solid {LH_BRAND['primary_color']};
                padding-bottom: 0.5cm;
            }}
            
            @bottom-center {{
                content: counter(page) " / " counter(pages);
                font-size: 9pt;
                color: {LH_BRAND['text_color']};
            }}
        }}
        
        /* Cover page - no header/footer */
        @page :first {{
            @top-center {{ content: none; }}
            @bottom-center {{ content: none; }}
        }}
        
        /* Headings */
        h1 {{
            color: {LH_BRAND['primary_color']};
            font-size: 24pt;
            font-weight: 700;
            margin-bottom: 1cm;
            page-break-after: avoid;
        }}
        
        h2 {{
            color: {LH_BRAND['primary_color']};
            font-size: 18pt;
            font-weight: 700;
            margin-top: 1.5cm;
            margin-bottom: 0.8cm;
            border-bottom: 2px solid {LH_BRAND['primary_color']};
            padding-bottom: 0.3cm;
            page-break-after: avoid;
        }}
        
        h3 {{
            color: {LH_BRAND['secondary_color']};
            font-size: 14pt;
            font-weight: 600;
            margin-top: 1cm;
            margin-bottom: 0.5cm;
            page-break-after: avoid;
        }}
        
        h4 {{
            color: {LH_BRAND['text_color']};
            font-size: 12pt;
            font-weight: 600;
            margin-top: 0.8cm;
            margin-bottom: 0.4cm;
        }}
        
        /* Paragraphs */
        p {{
            margin-bottom: 0.5cm;
            text-align: justify;
        }}
        
        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0.8cm 0;
            page-break-inside: avoid;
        }}
        
        th {{
            background-color: {LH_BRAND['primary_color']};
            color: white;
            padding: 0.4cm;
            text-align: left;
            font-weight: 600;
            border: 1px solid {LH_BRAND['primary_color']};
        }}
        
        td {{
            padding: 0.3cm;
            border: 1px solid #DDDDDD;
        }}
        
        tr:nth-child(even) {{
            background-color: {LH_BRAND['light_bg']};
        }}
        
        /* Lists */
        ul, ol {{
            margin-left: 1cm;
            margin-bottom: 0.5cm;
        }}
        
        li {{
            margin-bottom: 0.3cm;
        }}
        
        /* Info boxes */
        .info-box {{
            background-color: {LH_BRAND['light_bg']};
            border-left: 4px solid {LH_BRAND['primary_color']};
            padding: 0.5cm;
            margin: 0.8cm 0;
            page-break-inside: avoid;
        }}
        
        .warning-box {{
            background-color: #FFF3CD;
            border-left: 4px solid {LH_BRAND['accent_color']};
            padding: 0.5cm;
            margin: 0.8cm 0;
            page-break-inside: avoid;
        }}
        
        .success-box {{
            background-color: #D4EDDA;
            border-left: 4px solid #28A745;
            padding: 0.5cm;
            margin: 0.8cm 0;
            page-break-inside: avoid;
        }}
        
        /* Images and Charts */
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0.5cm auto;
            page-break-inside: avoid;
        }}
        
        .chart-container {{
            text-align: center;
            margin: 1cm 0;
            page-break-inside: avoid;
        }}
        
        .chart-title {{
            font-weight: 600;
            color: {LH_BRAND['primary_color']};
            margin-bottom: 0.3cm;
        }}
        
        /* Cover page */
        .cover-page {{
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            page-break-after: always;
        }}
        
        .cover-title {{
            font-size: 32pt;
            color: {LH_BRAND['primary_color']};
            font-weight: 700;
            margin-bottom: 1cm;
        }}
        
        .cover-subtitle {{
            font-size: 18pt;
            color: {LH_BRAND['secondary_color']};
            margin-bottom: 2cm;
        }}
        
        .cover-info {{
            font-size: 12pt;
            color: {LH_BRAND['text_color']};
            line-height: 2;
        }}
        
        /* Table of Contents */
        .toc {{
            page-break-after: always;
        }}
        
        .toc-item {{
            margin-bottom: 0.3cm;
            display: flex;
            justify-content: space-between;
        }}
        
        .toc-title {{
            flex-grow: 1;
        }}
        
        .toc-page {{
            min-width: 2cm;
            text-align: right;
        }}
        
        /* Page breaks */
        .page-break {{
            page-break-after: always;
        }}
        
        .avoid-break {{
            page-break-inside: avoid;
        }}
        
        /* Footer */
        .report-footer {{
            margin-top: 2cm;
            padding-top: 0.5cm;
            border-top: 1px solid #DDDDDD;
            font-size: 9pt;
            color: #666666;
            text-align: center;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
        return styled_html
    
    def _get_pdf_css(self) -> str:
        """Get additional CSS for PDF rendering"""
        return """
        /* Additional PDF-specific styling */
        @page {
            margin: 2.5cm 2cm;
        }
        
        /* Ensure proper page breaks */
        h1, h2, h3 {
            page-break-after: avoid;
        }
        
        table, figure, .chart-container {
            page-break-inside: avoid;
        }
        """


def export_report_to_pdf(
    html_content: str,
    output_filename: str,
    output_dir: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Convenience function to export report to PDF
    
    Args:
        html_content: HTML report content
        output_filename: Output PDF filename
        output_dir: Output directory (default: ./output/reports/)
        metadata: Report metadata
        
    Returns:
        Path to generated PDF
    """
    if output_dir is None:
        output_dir = Path('output/reports')
    
    output_path = output_dir / output_filename
    
    exporter = PDFExporterFull()
    return exporter.export_to_pdf(html_content, output_path, metadata)
