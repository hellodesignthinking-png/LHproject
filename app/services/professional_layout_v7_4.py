"""
ZeroSite v7.4 Professional Layout System

Professional A4 layout with:
- Print-optimized CSS with page breaks
- Headers and footers
- Page numbering
- LH brand colors
- Government document styling
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ProfessionalLayoutV74:
    """
    Professional A4 Layout System for v7.4
    
    Provides:
    - Print-ready CSS with proper page breaks
    - Professional headers and footers
    - Page numbers (via CSS counters)
    - LH corporate brand styling
    - Government document formatting
    """
    
    # LH Brand Colors
    LH_PRIMARY = "#0047AB"  # LH Blue
    LH_SECONDARY = "#00A651"  # LH Green
    LH_ACCENT = "#FF6B35"  # Accent Orange
    LH_DARK = "#1A1A1A"  # Text Dark
    LH_GRAY = "#666666"  # Text Gray
    LH_LIGHT_BG = "#F8F9FA"  # Light Background
    
    def __init__(self):
        """Initialize professional layout system"""
        logger.info("📄 Professional Layout v7.4 initialized")
    
    def get_professional_css(self) -> str:
        """
        Get comprehensive professional CSS for A4 print-ready reports
        
        Returns:
            Complete CSS string with print media queries and page breaks
        """
        return f"""
/* ═══════════════════════════════════════════════════════════════
   ZeroSite v7.4 Professional Report CSS
   A4 Print-Optimized | Government Document Standard
   ═══════════════════════════════════════════════════════════════ */

/* ─────────────────────────────────────────────────────────────── */
/* 1. CSS RESET & BASE STYLES                                      */
/* ─────────────────────────────────────────────────────────────── */

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html {{
    font-size: 12pt;  /* Base font size for print */
}}

body {{
    font-family: 'Noto Sans KR', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: {self.LH_DARK};
    background-color: #ffffff;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* ─────────────────────────────────────────────────────────────── */
/* 2. PAGE STRUCTURE (A4 210mm × 297mm)                            */
/* ─────────────────────────────────────────────────────────────── */

.report-container {{
    max-width: 210mm;
    margin: 0 auto;
    background: white;
}}

.page {{
    width: 210mm;
    min-height: 297mm;
    padding: 25mm 20mm 30mm 20mm;  /* Top, Right, Bottom, Left */
    margin: 0 auto;
    background: white;
    position: relative;
    page-break-after: always;
}}

.page:last-child {{
    page-break-after: auto;
}}

/* ─────────────────────────────────────────────────────────────── */
/* 3. COVER PAGE                                                    */
/* ─────────────────────────────────────────────────────────────── */

.cover-page {{
    height: 297mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 50mm 25mm;
    background: linear-gradient(135deg, {self.LH_PRIMARY} 0%, {self.LH_SECONDARY} 100%);
    color: white;
    page-break-after: always;
}}

.cover-header {{
    text-align: center;
}}

.cover-logo {{
    font-size: 18pt;
    font-weight: 300;
    letter-spacing: 8px;
    margin-bottom: 15mm;
    opacity: 0.9;
    text-transform: uppercase;
}}

.project-title {{
    font-size: 36pt;
    font-weight: 700;
    margin-bottom: 10mm;
    line-height: 1.3;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}}

.subtitle {{
    font-size: 20pt;
    font-weight: 300;
    opacity: 0.95;
    margin-bottom: 5mm;
}}

.report-type {{
    font-size: 14pt;
    font-weight: 400;
    opacity: 0.85;
    border-top: 1px solid rgba(255,255,255,0.3);
    border-bottom: 1px solid rgba(255,255,255,0.3);
    padding: 8px 0;
    margin-top: 8mm;
}}

.cover-middle {{
    background: rgba(255, 255, 255, 0.12);
    padding: 25px 30px;
    border-radius: 8px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
}}

.info-row {{
    display: flex;
    justify-content: space-between;
    margin: 12px 0;
    font-size: 13pt;
    padding: 8px 0;
    border-bottom: 1px dotted rgba(255,255,255,0.3);
}}

.info-row:last-child {{
    border-bottom: none;
}}

.info-row .label {{
    font-weight: 500;
    opacity: 0.9;
}}

.info-row .value {{
    font-weight: 600;
    text-align: right;
}}

.cover-footer {{
    text-align: center;
}}

.organization {{
    font-size: 28pt;
    font-weight: 700;
    margin-bottom: 8px;
}}

.department {{
    font-size: 16pt;
    font-weight: 400;
    opacity: 0.9;
    margin-bottom: 15px;
}}

.report-date {{
    font-size: 14pt;
    font-weight: 300;
    opacity: 0.85;
    margin-bottom: 20px;
}}

.confidential {{
    font-size: 10pt;
    opacity: 0.7;
    font-weight: 300;
    border-top: 1px solid rgba(255,255,255,0.3);
    padding-top: 15px;
}}

/* ─────────────────────────────────────────────────────────────── */
/* 4. TABLE OF CONTENTS                                             */
/* ─────────────────────────────────────────────────────────────── */

.toc-page {{
    page-break-after: always;
}}

.section-header {{
    font-size: 28pt;
    font-weight: 700;
    color: {self.LH_PRIMARY};
    margin-bottom: 30px;
    padding-bottom: 15px;
    border-bottom: 3px solid {self.LH_PRIMARY};
}}

.toc-list {{
    margin-top: 25px;
}}

.toc-item {{
    display: flex;
    align-items: baseline;
    padding: 12px 5px;
    border-bottom: 1px dotted #ddd;
    transition: background-color 0.2s;
}}

.toc-item:hover {{
    background-color: {self.LH_LIGHT_BG};
}}

.toc-num {{
    font-weight: 600;
    color: {self.LH_PRIMARY};
    min-width: 50px;
    font-size: 11pt;
}}

.toc-title {{
    flex: 1;
    font-size: 11pt;
    padding-left: 10px;
}}

.toc-subtitle {{
    font-size: 10pt;
    color: {self.LH_GRAY};
    padding-left: 60px;
    margin-top: 3px;
}}

.toc-page-num {{
    min-width: 40px;
    text-align: right;
    color: {self.LH_GRAY};
    font-size: 11pt;
}}

/* ─────────────────────────────────────────────────────────────── */
/* 5. SECTION STYLES                                                */
/* ─────────────────────────────────────────────────────────────── */

.section {{
    margin-bottom: 35mm;
    page-break-inside: avoid;
}}

.section-title {{
    font-size: 22pt;
    font-weight: 700;
    color: {self.LH_PRIMARY};
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 3px solid {self.LH_PRIMARY};
    page-break-after: avoid;
}}

.subsection {{
    margin-bottom: 25px;
}}

.subsection-title {{
    font-size: 16pt;
    font-weight: 600;
    color: {self.LH_DARK};
    margin: 20px 0 12px 0;
    padding-left: 12px;
    border-left: 4px solid {self.LH_SECONDARY};
    page-break-after: avoid;
}}

.sub-subsection-title {{
    font-size: 13pt;
    font-weight: 600;
    color: {self.LH_GRAY};
    margin: 15px 0 10px 0;
    page-break-after: avoid;
}}

/* ─────────────────────────────────────────────────────────────── */
/* 6. NARRATIVE CONTENT                                             */
/* ─────────────────────────────────────────────────────────────── */

.narrative-block {{
    margin-bottom: 25px;
}}

.paragraph {{
    text-align: justify;
    text-justify: inter-word;
    margin-bottom: 12px;
    line-height: 1.8;
    font-size: 11pt;
    color: {self.LH_DARK};
}}

.paragraph strong {{
    color: {self.LH_PRIMARY};
    font-weight: 600;
}}

.paragraph em {{
    color: {self.LH_ACCENT};
    font-style: normal;
    font-weight: 500;
}}

.highlight-box {{
    background-color: {self.LH_LIGHT_BG};
    border-left: 4px solid {self.LH_PRIMARY};
    padding: 15px 20px;
    margin: 20px 0;
    border-radius: 4px;
}}

.key-finding {{
    background-color: #FFF9E6;
    border-left: 4px solid {self.LH_ACCENT};
    padding: 15px 20px;
    margin: 20px 0;
    border-radius: 4px;
}}

.recommendation {{
    background-color: #E8F5E9;
    border-left: 4px solid {self.LH_SECONDARY};
    padding: 15px 20px;
    margin: 20px 0;
    border-radius: 4px;
}}

/* ─────────────────────────────────────────────────────────────── */
/* 7. DATA TABLES                                                   */
/* ─────────────────────────────────────────────────────────────── */

.data-table {{
    margin: 20px 0;
    overflow-x: auto;
    page-break-inside: avoid;
}}

.data-table table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 10pt;
}}

.data-table thead {{
    background-color: {self.LH_PRIMARY};
    color: white;
}}

.data-table th {{
    padding: 12px 10px;
    text-align: center;
    font-weight: 600;
    border: 1px solid #dee2e6;
}}

.data-table td {{
    padding: 10px;
    border: 1px solid #dee2e6;
    text-align: center;
}}

.data-table tbody tr:nth-child(even) {{
    background-color: {self.LH_LIGHT_BG};
}}

.data-table tbody tr:hover {{
    background-color: #e7f3ff;
}}

.data-table .label-column {{
    text-align: left;
    font-weight: 500;
    color: {self.LH_DARK};
}}

.data-table .number-column {{
    text-align: right;
    font-family: 'Roboto Mono', monospace;
}}

.data-table .highlight-row {{
    background-color: #FFF9E6 !important;
    font-weight: 600;
}}

.table-caption {{
    font-size: 10pt;
    color: {self.LH_GRAY};
    text-align: center;
    margin-top: 8px;
    font-style: italic;
}}

/* ─────────────────────────────────────────────────────────────── */
/* 8. LISTS (BULLETS & NUMBERED)                                    */
/* ─────────────────────────────────────────────────────────────── */

.bullet-list {{
    margin: 15px 0;
    padding-left: 25px;
}}

.bullet-list li {{
    margin-bottom: 8px;
    line-height: 1.6;
    color: {self.LH_DARK};
}}

.bullet-list li::marker {{
    color: {self.LH_PRIMARY};
    font-weight: 600;
}}

.numbered-list {{
    margin: 15px 0;
    padding-left: 25px;
    counter-reset: item;
}}

.numbered-list li {{
    margin-bottom: 8px;
    line-height: 1.6;
    color: {self.LH_DARK};
    counter-increment: item;
}}

.numbered-list li::marker {{
    color: {self.LH_PRIMARY};
    font-weight: 600;
}}

/* ─────────────────────────────────────────────────────────────── */
/* 9. SPECIAL CONTENT BOXES                                         */
/* ─────────────────────────────────────────────────────────────── */

.executive-summary {{
    background: linear-gradient(135deg, {self.LH_PRIMARY}15 0%, {self.LH_SECONDARY}15 100%);
    border: 2px solid {self.LH_PRIMARY};
    padding: 20px;
    margin: 25px 0;
    border-radius: 6px;
    page-break-inside: avoid;
}}

.executive-summary-title {{
    font-size: 16pt;
    font-weight: 700;
    color: {self.LH_PRIMARY};
    margin-bottom: 15px;
}}

.decision-box {{
    background-color: white;
    border: 3px solid {self.LH_SECONDARY};
    padding: 20px;
    margin: 25px 0;
    border-radius: 6px;
    text-align: center;
    page-break-inside: avoid;
}}

.decision-label {{
    font-size: 18pt;
    font-weight: 700;
    color: {self.LH_PRIMARY};
    margin-bottom: 10px;
}}

.decision-value {{
    font-size: 24pt;
    font-weight: 700;
    color: {self.LH_SECONDARY};
}}

.risk-critical {{
    color: #D32F2F;
    font-weight: 700;
}}

.risk-high {{
    color: {self.LH_ACCENT};
    font-weight: 600;
}}

.risk-medium {{
    color: #F57C00;
    font-weight: 500;
}}

.risk-low {{
    color: {self.LH_SECONDARY};
    font-weight: 400;
}}

/* ─────────────────────────────────────────────────────────────── */
/* 10. HEADERS & FOOTERS                                            */
/* ─────────────────────────────────────────────────────────────── */

.page-header {{
    position: absolute;
    top: 15mm;
    left: 20mm;
    right: 20mm;
    padding-bottom: 5mm;
    border-bottom: 1px solid #e0e0e0;
    font-size: 9pt;
    color: {self.LH_GRAY};
}}

.page-header-left {{
    float: left;
    font-weight: 500;
}}

.page-header-right {{
    float: right;
    font-weight: 400;
}}

.page-footer {{
    position: absolute;
    bottom: 15mm;
    left: 20mm;
    right: 20mm;
    padding-top: 5mm;
    border-top: 1px solid #e0e0e0;
    font-size: 9pt;
    color: {self.LH_GRAY};
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.footer-left {{
    font-weight: 400;
}}

.footer-center {{
    font-weight: 500;
}}

.footer-right {{
    font-weight: 600;
    color: {self.LH_PRIMARY};
}}

/* ─────────────────────────────────────────────────────────────── */
/* 11. PAGE BREAKS & PRINT CONTROL                                  */
/* ─────────────────────────────────────────────────────────────── */

.page-break {{
    page-break-after: always;
}}

.page-break-before {{
    page-break-before: always;
}}

.avoid-break {{
    page-break-inside: avoid;
}}

/* ─────────────────────────────────────────────────────────────── */
/* 12. PRINT MEDIA QUERIES                                          */
/* ─────────────────────────────────────────────────────────────── */

@media print {{
    body {{
        margin: 0;
        padding: 0;
    }}
    
    .page {{
        margin: 0;
        page-break-after: always;
    }}
    
    .page:last-child {{
        page-break-after: auto;
    }}
    
    .section-title,
    .subsection-title,
    .table-caption {{
        page-break-after: avoid;
    }}
    
    .data-table,
    .highlight-box,
    .executive-summary,
    .decision-box {{
        page-break-inside: avoid;
    }}
    
    /* Hide screen-only elements */
    .no-print {{
        display: none !important;
    }}
    
    /* Page counter for print */
    @page {{
        size: A4 portrait;
        margin: 25mm 20mm 30mm 20mm;
    }}
    
    @page :first {{
        margin: 0;
    }}
}}

/* ─────────────────────────────────────────────────────────────── */
/* 13. RESPONSIVE (Screen View)                                     */
/* ─────────────────────────────────────────────────────────────── */

@media screen and (max-width: 1024px) {{
    .report-container {{
        max-width: 100%;
        padding: 0 15px;
    }}
    
    .page {{
        width: 100%;
        min-height: auto;
        padding: 20px;
        page-break-after: auto;
    }}
    
    .cover-page {{
        height: auto;
        min-height: 100vh;
        padding: 40px 20px;
    }}
}}

/* ─────────────────────────────────────────────────────────────── */
/* 14. UTILITY CLASSES                                              */
/* ─────────────────────────────────────────────────────────────── */

.text-center {{
    text-align: center;
}}

.text-right {{
    text-align: right;
}}

.text-left {{
    text-align: left;
}}

.font-bold {{
    font-weight: 700;
}}

.font-semibold {{
    font-weight: 600;
}}

.text-primary {{
    color: {self.LH_PRIMARY};
}}

.text-secondary {{
    color: {self.LH_SECONDARY};
}}

.text-accent {{
    color: {self.LH_ACCENT};
}}

.text-gray {{
    color: {self.LH_GRAY};
}}

.mb-small {{
    margin-bottom: 10px;
}}

.mb-medium {{
    margin-bottom: 20px;
}}

.mb-large {{
    margin-bottom: 30px;
}}

.mt-small {{
    margin-top: 10px;
}}

.mt-medium {{
    margin-top: 20px;
}}

.mt-large {{
    margin-top: 30px;
}}

/* ═══════════════════════════════════════════════════════════════
   END OF STYLESHEET
   ═══════════════════════════════════════════════════════════════ */
"""
    
    def generate_page_header(self, project_title: str, section_name: str = "") -> str:
        """
        Generate HTML for page header
        
        Args:
            project_title: Project title for header
            section_name: Current section name (optional)
        
        Returns:
            HTML string for page header
        """
        return f"""
        <div class="page-header">
            <span class="page-header-left">{project_title}</span>
            <span class="page-header-right">{section_name}</span>
            <div style="clear: both;"></div>
        </div>
        """
    
    def generate_page_footer(
        self,
        organization: str = "한국토지주택공사 (LH)",
        page_number: str = "",
        confidential: bool = True
    ) -> str:
        """
        Generate HTML for page footer
        
        Args:
            organization: Organization name
            page_number: Page number (if applicable)
            confidential: Whether to show confidential notice
        
        Returns:
            HTML string for page footer
        """
        confidential_text = "🔒 대외비" if confidential else ""
        
        return f"""
        <div class="page-footer">
            <span class="footer-left">{organization}</span>
            <span class="footer-center">{confidential_text}</span>
            <span class="footer-right">{page_number}</span>
        </div>
        """
    
    def wrap_page_with_headers_footers(
        self,
        content: str,
        project_title: str,
        section_name: str = "",
        page_number: str = "",
        include_header: bool = True,
        include_footer: bool = True
    ) -> str:
        """
        Wrap content in a page with headers and footers
        
        Args:
            content: Page content HTML
            project_title: Project title
            section_name: Section name
            page_number: Page number
            include_header: Whether to include header
            include_footer: Whether to include footer
        
        Returns:
            Complete page HTML
        """
        header_html = self.generate_page_header(project_title, section_name) if include_header else ""
        footer_html = self.generate_page_footer(page_number=page_number) if include_footer else ""
        
        return f"""
        <div class="page">
            {header_html}
            <div class="page-content">
                {content}
            </div>
            {footer_html}
        </div>
        """
    
    def generate_section_divider(self, section_number: int, section_title: str) -> str:
        """
        Generate a visual section divider
        
        Args:
            section_number: Section number
            section_title: Section title
        
        Returns:
            HTML for section divider
        """
        return f"""
        <div class="page-break"></div>
        <div class="section">
            <h1 class="section-title">{section_number}. {section_title}</h1>
        </div>
        """
