"""
PDF Generator for LH Expert Edition Reports
Converts HTML reports to high-quality PDF documents
"""

from pathlib import Path
from typing import Optional, Union
import logging

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate PDF reports from HTML"""
    
    def __init__(self):
        """Initialize PDF generator with Korean font support"""
        self.font_config = FontConfiguration()
        
        # CSS for PDF optimization
        self.pdf_css = CSS(string='''
            @page {
                size: A4;
                margin: 2cm 1.5cm;
                
                @top-center {
                    content: "LH Expert Edition Report";
                    font-size: 9pt;
                    color: #666;
                }
                
                @bottom-center {
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 9pt;
                    color: #666;
                }
            }
            
            /* Prevent page breaks inside important elements */
            .section, .card, .chart-container, table {
                page-break-inside: avoid;
            }
            
            /* Chart image optimization for PDF */
            img {
                max-width: 100%;
                height: auto;
                page-break-inside: avoid;
            }
            
            /* Table optimization */
            table {
                border-collapse: collapse;
                width: 100%;
                page-break-inside: avoid;
            }
            
            table th, table td {
                padding: 8px;
                border: 1px solid #ddd;
                font-size: 10pt;
            }
            
            /* Typography for PDF */
            body {
                font-family: "Noto Sans KR", "Malgun Gothic", "맑은 고딕", sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
            }
            
            h1 {
                font-size: 24pt;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                page-break-after: avoid;
            }
            
            h2 {
                font-size: 18pt;
                margin-top: 1.2em;
                margin-bottom: 0.4em;
                page-break-after: avoid;
            }
            
            h3 {
                font-size: 14pt;
                margin-top: 1em;
                margin-bottom: 0.3em;
                page-break-after: avoid;
            }
            
            /* Print optimization */
            @media print {
                body {
                    background: white;
                }
                
                .no-print {
                    display: none;
                }
            }
        ''', font_config=self.font_config)
    
    def generate_pdf(
        self,
        html_content: Union[str, Path],
        output_path: Union[str, Path],
        base_url: Optional[str] = None
    ) -> Path:
        """
        Generate PDF from HTML content
        
        Args:
            html_content: HTML string or path to HTML file
            output_path: Output PDF file path
            base_url: Base URL for resolving relative paths (optional)
            
        Returns:
            Path to generated PDF file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Load HTML
            if isinstance(html_content, Path) or (isinstance(html_content, str) and Path(html_content).exists()):
                # Load from file
                html_path = Path(html_content).resolve()  # Resolve to absolute path
                base_url = base_url or html_path.parent.as_uri()
                html = HTML(filename=str(html_path), base_url=base_url)
                logger.info(f"Loaded HTML from file: {html_path}")
            else:
                # Load from string
                html = HTML(string=html_content, base_url=base_url or '.')
                logger.info("Loaded HTML from string")
            
            # Generate PDF
            logger.info(f"Generating PDF: {output_path}")
            html.write_pdf(
                target=str(output_path),
                stylesheets=[self.pdf_css],
                font_config=self.font_config
            )
            
            # Check file size
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"PDF generated successfully: {file_size_mb:.2f}MB")
            
            if file_size_mb > 10:
                logger.warning(f"PDF file size ({file_size_mb:.2f}MB) exceeds 10MB target")
            
            return output_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def generate_pdf_optimized(
        self,
        html_content: Union[str, Path],
        output_path: Union[str, Path],
        base_url: Optional[str] = None,
        optimize_images: bool = True,
        jpeg_quality: int = 85
    ) -> Path:
        """
        Generate optimized PDF with image compression
        
        Args:
            html_content: HTML string or path to HTML file
            output_path: Output PDF file path
            base_url: Base URL for resolving relative paths
            optimize_images: Whether to optimize images (default: True)
            jpeg_quality: JPEG quality for compression (default: 85, range: 1-100)
            
        Returns:
            Path to generated PDF file
        """
        # First generate standard PDF
        pdf_path = self.generate_pdf(html_content, output_path, base_url)
        
        # Check if optimization is needed
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        
        if file_size_mb <= 10:
            logger.info(f"PDF size ({file_size_mb:.2f}MB) within 10MB limit, no optimization needed")
            return pdf_path
        
        # If PDF is too large and optimization is requested
        if optimize_images:
            logger.info(f"PDF size ({file_size_mb:.2f}MB) exceeds 10MB, optimization recommended")
            logger.info("Tip: Reduce chart image sizes or use lower resolution")
        
        return pdf_path


def generate_report_pdf(
    html_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    optimize: bool = True
) -> Path:
    """
    Convenience function to generate PDF report
    
    Args:
        html_path: Path to HTML report file
        output_path: Output PDF path (optional, defaults to same name as HTML)
        optimize: Whether to use optimization (default: True)
        
    Returns:
        Path to generated PDF file
    """
    html_path = Path(html_path)
    
    if output_path is None:
        output_path = html_path.with_suffix('.pdf')
    else:
        output_path = Path(output_path)
    
    generator = PDFGenerator()
    
    if optimize:
        return generator.generate_pdf_optimized(html_path, output_path)
    else:
        return generator.generate_pdf(html_path, output_path)


if __name__ == "__main__":
    # Test PDF generation
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_generator.py <html_file> [output_pdf]")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        pdf_path = generate_report_pdf(html_file, output_file)
        print(f"✅ PDF generated: {pdf_path}")
        print(f"   Size: {pdf_path.stat().st_size / (1024 * 1024):.2f}MB")
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        sys.exit(1)
