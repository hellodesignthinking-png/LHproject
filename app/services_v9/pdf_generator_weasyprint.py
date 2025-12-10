"""
ZeroSite Expert Edition v3 - WeasyPrint PDF Generator

Generates simple 2-3 page land appraisal PDF reports
Uses Jinja2 templates and WeasyPrint for professional PDF output

Features:
- ZeroSite v3 black-minimal design
- 3-page professional report layout
- Automatic styling and formatting
- Support for Korean text

Author: ZeroSite Development Team + GenSpark AI
Date: 2025-12-10
Version: v3.0
"""

from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import logging
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import io

logger = logging.getLogger(__name__)


class WeasyPrintPDFGenerator:
    """
    WeasyPrint-based PDF Generator for Land Reports
    
    Generates professional 2-3 page PDF reports using HTML templates
    """
    
    def __init__(self):
        """Initialize PDF generator with template environment"""
        # Get template directory
        template_dir = Path(__file__).parent / "templates" / "weasyprint"
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
        
        # Font configuration for WeasyPrint
        self.font_config = FontConfiguration()
        
        logger.info("✅ WeasyPrint PDF Generator initialized")
        logger.info(f"   Template directory: {template_dir}")
    
    def generate_pdf(
        self,
        report_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF from report data
        
        Args:
            report_data: Complete report data dict (same as API response)
            output_path: Optional file path to save PDF
        
        Returns:
            PDF content as bytes
        """
        try:
            logger.info(f"🔧 Generating PDF for report: {report_data.get('report_id', 'N/A')}")
            
            # Load template
            template = self.env.get_template("land_report_simple.html")
            
            # Render HTML
            html_content = template.render(data=report_data)
            
            # Generate PDF
            pdf_bytes = self._html_to_pdf(html_content)
            
            # Save to file if path provided
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_bytes(pdf_bytes)
                logger.info(f"💾 PDF saved to: {output_path}")
            
            logger.info(f"✅ PDF generated successfully ({len(pdf_bytes):,} bytes)")
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {e}", exc_info=True)
            raise
    
    def _html_to_pdf(self, html_content: str) -> bytes:
        """
        Convert HTML to PDF using WeasyPrint
        
        Args:
            html_content: Rendered HTML string
        
        Returns:
            PDF content as bytes
        """
        try:
            # Create HTML object
            html = HTML(string=html_content, base_url=".")
            
            # Generate PDF
            pdf_bytes = html.write_pdf(font_config=self.font_config)
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"❌ HTML to PDF conversion failed: {e}", exc_info=True)
            raise
    
    def generate_pdf_stream(
        self,
        report_data: Dict[str, Any]
    ) -> io.BytesIO:
        """
        Generate PDF and return as BytesIO stream
        
        Args:
            report_data: Complete report data dict
        
        Returns:
            BytesIO stream containing PDF
        """
        pdf_bytes = self.generate_pdf(report_data)
        stream = io.BytesIO(pdf_bytes)
        stream.seek(0)
        return stream
    
    def get_pdf_size(self, report_data: Dict[str, Any]) -> int:
        """
        Get PDF file size without saving
        
        Args:
            report_data: Complete report data dict
        
        Returns:
            PDF size in bytes
        """
        pdf_bytes = self.generate_pdf(report_data)
        return len(pdf_bytes)


# Standalone test
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 WeasyPrint PDF Generator Test")
    print("="*60 + "\n")
    
    # Sample test data
    test_data = {
        "report_id": "rpt_20251210_test123",
        "timestamp": "2025-12-10T09:00:00",
        "input": {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_size_sqm": 1000.0,
            "zone_type": "제2종일반주거지역",
            "asking_price": 10000000000
        },
        "valuation": {
            "estimated_price_krw": 12546748607,
            "price_range": {
                "low": 11000000000,
                "avg": 12546748607,
                "high": 14000000000
            },
            "price_per_sqm_krw": 12546749,
            "confidence_score": 0.83,
            "confidence_level": "HIGH",
            "transaction_count": 10,
            "coordinate": {
                "lat": 37.515224,
                "lng": 127.051055,
                "region": "서울특별시",
                "district": "강남구"
            },
            "enhanced_features": {
                "dynamic_transactions": True,
                "weighted_adjustments": True,
                "advanced_confidence": True,
                "adjustment_weights": {
                    "distance": "35%",
                    "time": "25%",
                    "size": "25%",
                    "zone": "15%"
                },
                "confidence_weights": {
                    "sample_size": "30%",
                    "price_variance": "30%",
                    "distance": "25%",
                    "recency": "15%"
                }
            }
        },
        "recommendation": {
            "status": "저가 (매수 추천)",
            "difference_krw": -2053251393,
            "difference_pct": -16.36,
            "emoji": "🔵"
        },
        "comparables": [
            {
                "address": "서울특별시 강남구 대치동 62-33",
                "distance_km": 0.5,
                "size_sqm": 548.3,
                "price_per_sqm": 14225425,
                "total_price": 7800334497,
                "transaction_date": "2025-05-17",
                "adjustments": {
                    "distance": "-3.0%",
                    "time": "-3.0%",
                    "size": "-4.0%",
                    "zone": "+0.0%",
                    "total": "-2.8%"
                }
            },
            {
                "address": "서울특별시 강남구 대치동 65-63",
                "distance_km": 0.52,
                "size_sqm": 1007.0,
                "price_per_sqm": 12613173,
                "total_price": 12701448597,
                "transaction_date": "2024-03-26",
                "adjustments": {
                    "distance": "-3.0%",
                    "time": "-6.0%",
                    "size": "+0.0%",
                    "zone": "-3.0%",
                    "total": "-3.0%"
                }
            }
        ],
        "negotiation": {
            "market_price": 12546748607,
            "recommended_price": 13200000000,
            "conservative_price": 11919411177
        }
    }
    
    try:
        # Initialize generator
        generator = WeasyPrintPDFGenerator()
        
        # Generate PDF
        output_path = "/tmp/test_land_report.pdf"
        pdf_bytes = generator.generate_pdf(test_data, output_path=output_path)
        
        # Results
        print(f"✅ PDF generated successfully")
        print(f"   ├─ File path: {output_path}")
        print(f"   ├─ File size: {len(pdf_bytes):,} bytes ({len(pdf_bytes)/1024:.1f} KB)")
        print(f"   ├─ Report ID: {test_data['report_id']}")
        print(f"   └─ Address: {test_data['input']['address']}")
        
        print("\n" + "="*60)
        print("✅ WeasyPrint PDF Generator Test PASSED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
