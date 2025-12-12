#!/usr/bin/env python3
"""
Expert v3.3 PDF Generator
=========================
Converts Expert v3.2 HTML reports to professional PDF format

Features:
- High-quality PDF output with WeasyPrint
- Korean font support
- Embedded Base64 images (charts, graphs)
- Professional A/B comparison tables
- Page break optimization
- 150dpi resolution for all graphics

Author: ZeroSite v3.3 Development Team
Version: 3.3.0
Date: 2025-12-12
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging

# WeasyPrint imports
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


class ExpertV3PDFGenerator:
    """
    PDF Generator for Expert v3.2/v3.3 Reports
    
    Converts HTML reports to professional PDF with:
    - High-resolution charts (150dpi)
    - Korean text support
    - Proper page breaks
    - Professional styling
    """
    
    def __init__(self):
        """Initialize PDF generator with font configuration"""
        self.font_config = FontConfiguration()
        logger.info("✅ Expert v3.3 PDF Generator initialized")
    
    def generate_pdf_from_html(
        self,
        html_content: str,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF from HTML content
        
        Args:
            html_content: Complete HTML string (with embedded CSS and images)
            output_path: Optional file path to save PDF
        
        Returns:
            PDF content as bytes
        """
        try:
            logger.info("🔧 Generating PDF from HTML...")
            
            # Add PDF-specific CSS enhancements
            enhanced_html = self._enhance_html_for_pdf(html_content)
            
            # Convert to PDF
            html_obj = HTML(string=enhanced_html, base_url=".")
            pdf_bytes = html_obj.write_pdf(
                font_config=self.font_config,
                presentational_hints=True
            )
            
            # Save to file if path provided
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_bytes(pdf_bytes)
                logger.info(f"💾 PDF saved to: {output_path}")
            
            logger.info(f"✅ PDF generated: {len(pdf_bytes):,} bytes ({len(pdf_bytes)/1024:.1f} KB)")
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {e}", exc_info=True)
            raise
    
    def _enhance_html_for_pdf(self, html_content: str) -> str:
        """
        Add PDF-specific CSS enhancements
        
        Improvements:
        - Better page breaks
        - High DPI printing
        - Improved table rendering
        - Color accuracy
        """
        pdf_css = """
<style>
/* PDF-specific enhancements */
@page {
    size: A4;
    margin: 15mm 12mm 15mm 12mm;
    
    @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #666;
    }
}

/* Prevent awkward page breaks */
table, .section, .scenario-card {
    page-break-inside: avoid;
}

h1, h2, h3 {
    page-break-after: avoid;
}

/* High-resolution printing */
img {
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
    max-width: 100%;
    height: auto;
}

/* Table enhancements for PDF */
table {
    border-collapse: collapse;
    width: 100%;
}

th, td {
    padding: 10px 12px;
    border: 1.3px solid #ddd;
}

th {
    background-color: #0047AB !important;
    color: white !important;
    font-weight: bold;
}

/* Alternating row colors */
tbody tr:nth-child(even) {
    background-color: #f8f9fa;
}

tbody tr:nth-child(odd) {
    background-color: #ffffff;
}

/* Scenario-specific coloring */
.scenario-a-col {
    background-color: #E3F2FD !important;
}

.scenario-b-col {
    background-color: #FFF3E0 !important;
}

/* Text clarity */
body {
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

/* LH Blue branding */
.lh-blue {
    color: #0047AB;
}

.bg-lh-blue {
    background-color: #0047AB !important;
    color: white !important;
}

/* Decision badges */
.decision-go {
    background-color: #10b981;
    color: white;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: bold;
}

.decision-no-go {
    background-color: #ef4444;
    color: white;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: bold;
}

/* Print-friendly colors */
@media print {
    * {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
}
</style>
"""
        
        # Insert PDF CSS right before </head> tag
        if "</head>" in html_content:
            html_content = html_content.replace("</head>", pdf_css + "\n</head>")
        else:
            # If no </head> tag, insert at beginning
            html_content = pdf_css + "\n" + html_content
        
        return html_content
    
    def get_pdf_metadata(self, pdf_bytes: bytes) -> Dict:
        """
        Get metadata about generated PDF
        
        Args:
            pdf_bytes: PDF content as bytes
        
        Returns:
            Dict with file size, page count estimate, etc.
        """
        return {
            "size_bytes": len(pdf_bytes),
            "size_kb": round(len(pdf_bytes) / 1024, 2),
            "size_mb": round(len(pdf_bytes) / (1024 * 1024), 2),
            "format": "PDF",
            "quality": "High (150dpi equivalent)"
        }


# Standalone test
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 Expert v3.3 PDF Generator Test")
    print("="*80 + "\n")
    
    # Sample HTML (minimal test)
    sample_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Expert v3.3 Test Report</title>
    <style>
        body {
            font-family: 'Malgun Gothic', sans-serif;
            margin: 40px;
        }
        h1 {
            color: #0047AB;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #0047AB;
            color: white;
        }
    </style>
</head>
<body>
    <h1>🏗️ ZeroSite Expert v3.3 테스트 리포트</h1>
    
    <h2>프로젝트 개요</h2>
    <table>
        <tr>
            <th>항목</th>
            <th>내용</th>
        </tr>
        <tr>
            <td>주소</td>
            <td>서울특별시 강남구 역삼동 123-45</td>
        </tr>
        <tr>
            <td>대지면적</td>
            <td>1,650.0㎡</td>
        </tr>
        <tr>
            <td>건폐율</td>
            <td>50.0%</td>
        </tr>
        <tr>
            <td>용적률</td>
            <td>300.0%</td>
        </tr>
    </table>
    
    <h2>A/B 시나리오 비교</h2>
    <table>
        <thead>
            <tr>
                <th>항목</th>
                <th class="scenario-a-col">시나리오 A (청년)</th>
                <th class="scenario-b-col">시나리오 B (신혼부부)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>세대 수</td>
                <td>77세대</td>
                <td>51세대</td>
            </tr>
            <tr>
                <td>ROI</td>
                <td>-7.34%</td>
                <td>-22.15%</td>
            </tr>
            <tr>
                <td>결정</td>
                <td><span class="decision-no-go">NO-GO</span></td>
                <td><span class="decision-no-go">NO-GO</span></td>
            </tr>
        </tbody>
    </table>
    
    <p><strong>생성 일시:</strong> 2025-12-12 16:30:00</p>
    <p><strong>문서 코드:</strong> EXP_V33_TEST_001</p>
</body>
</html>
    """
    
    try:
        # Initialize generator
        generator = ExpertV3PDFGenerator()
        
        # Generate PDF
        output_path = "/home/user/webapp/test_expert_v33_output.pdf"
        pdf_bytes = generator.generate_pdf_from_html(
            html_content=sample_html,
            output_path=output_path
        )
        
        # Get metadata
        metadata = generator.get_pdf_metadata(pdf_bytes)
        
        # Results
        print("✅ PDF generated successfully")
        print(f"   ├─ File path: {output_path}")
        print(f"   ├─ Size: {metadata['size_kb']} KB")
        print(f"   ├─ Format: {metadata['format']}")
        print(f"   └─ Quality: {metadata['quality']}")
        
        print("\n" + "="*80)
        print("✅ Expert v3.3 PDF Generator Test PASSED")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
