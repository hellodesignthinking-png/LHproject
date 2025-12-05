"""
ZeroSite v7.4 PDF Export Utility

Converts professional HTML reports to high-quality PDF documents
using WeasyPrint for government-standard print output.
"""

from typing import Optional
import logging
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


class PDFExportV74:
    """
    PDF Export Utility for v7.4 Professional Reports
    
    Converts HTML reports to PDF with:
    - Professional A4 layout (210mm × 297mm)
    - Proper page breaks and margins
    - LH corporate styling
    - Font embedding for consistent rendering
    """
    
    def __init__(self):
        """Initialize PDF export utility"""
        self.font_config = FontConfiguration()
        logger.info("📄 PDF Export v7.4 initialized")
    
    def html_to_pdf(
        self,
        html_content: str,
        output_path: str,
        base_url: Optional[str] = None
    ) -> bool:
        """
        Convert HTML content to PDF file
        
        Args:
            html_content: HTML string to convert
            output_path: Path where PDF will be saved
            base_url: Base URL for resolving relative paths (optional)
        
        Returns:
            True if conversion successful, False otherwise
        """
        try:
            logger.info(f"🔄 Converting HTML to PDF: {output_path}")
            
            # Create HTML object
            html_doc = HTML(string=html_content, base_url=base_url)
            
            # Additional CSS for PDF optimization
            pdf_css = CSS(string=self._get_pdf_optimization_css())
            
            # Generate PDF
            html_doc.write_pdf(
                output_path,
                stylesheets=[pdf_css],
                font_config=self.font_config
            )
            
            # Verify file was created
            pdf_path = Path(output_path)
            if pdf_path.exists():
                file_size = pdf_path.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
                logger.info(f"✅ PDF generated successfully: {file_size_mb:.2f} MB")
                return True
            else:
                logger.error("❌ PDF file not created")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error converting HTML to PDF: {str(e)}")
            return False
    
    def html_file_to_pdf(
        self,
        html_file_path: str,
        output_path: Optional[str] = None
    ) -> bool:
        """
        Convert HTML file to PDF
        
        Args:
            html_file_path: Path to HTML file
            output_path: Path where PDF will be saved (optional, defaults to same name with .pdf)
        
        Returns:
            True if conversion successful, False otherwise
        """
        try:
            # Read HTML file
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Determine output path
            if output_path is None:
                html_path = Path(html_file_path)
                output_path = str(html_path.with_suffix('.pdf'))
            
            # Get base URL for relative path resolution
            base_url = Path(html_file_path).parent.as_uri()
            
            # Convert to PDF
            return self.html_to_pdf(html_content, output_path, base_url)
            
        except Exception as e:
            logger.error(f"❌ Error reading HTML file: {str(e)}")
            return False
    
    def _get_pdf_optimization_css(self) -> str:
        """
        Additional CSS for PDF optimization
        
        Returns:
            CSS string for better PDF rendering
        """
        return """
        /* PDF Optimization CSS */
        
        @page {
            size: A4 portrait;
            margin: 25mm 20mm 30mm 20mm;
            
            @top-center {
                content: element(header);
            }
            
            @bottom-center {
                content: counter(page);
                font-family: 'Noto Sans KR', sans-serif;
                font-size: 9pt;
                color: #666;
            }
        }
        
        @page :first {
            margin: 0;
        }
        
        /* Ensure page breaks work correctly */
        .page-break {
            page-break-after: always;
            break-after: page;
        }
        
        .page-break-before {
            page-break-before: always;
            break-before: page;
        }
        
        .avoid-break {
            page-break-inside: avoid;
            break-inside: avoid;
        }
        
        /* Better table handling in PDF */
        table {
            page-break-inside: avoid;
        }
        
        thead {
            display: table-header-group;
        }
        
        tfoot {
            display: table-footer-group;
        }
        
        /* Optimize images for print */
        img {
            max-width: 100%;
            height: auto;
            page-break-inside: avoid;
        }
        
        /* Better text rendering */
        body {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        /* Ensure links are visible in print */
        a {
            text-decoration: underline;
            color: #0047AB;
        }
        
        /* Hide screen-only elements */
        .no-print {
            display: none !important;
        }
        """


def convert_v7_4_report_to_pdf(
    html_content: str,
    output_pdf_path: str
) -> bool:
    """
    Convenience function to convert v7.4 report HTML to PDF
    
    Args:
        html_content: HTML report content
        output_pdf_path: Path where PDF will be saved
    
    Returns:
        True if successful, False otherwise
    """
    exporter = PDFExportV74()
    return exporter.html_to_pdf(html_content, output_pdf_path)


def convert_html_file_to_pdf(
    html_file_path: str,
    output_pdf_path: Optional[str] = None
) -> bool:
    """
    Convenience function to convert HTML file to PDF
    
    Args:
        html_file_path: Path to HTML file
        output_pdf_path: Path where PDF will be saved (optional)
    
    Returns:
        True if successful, False otherwise
    """
    exporter = PDFExportV74()
    return exporter.html_file_to_pdf(html_file_path, output_pdf_path)
