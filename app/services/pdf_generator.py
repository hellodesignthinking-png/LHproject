"""
ZeroSite v3.3 PDF Generator
==========================

Composer 결과물을 PDF로 변환하는 서비스

Features:
- HTML 템플릿 기반 PDF 생성
- Master Plan v3.3 스타일 가이드 적용
- 7개 보고서 타입 지원
- WeasyPrint 기반 고품질 PDF

Author: ZeroSite Development Team
Date: 2025-12-15
Version: v3.3
"""

from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import tempfile
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Report Composer 결과물을 PDF로 변환
    
    Usage:
        generator = PDFGenerator()
        pdf_bytes = generator.generate("pre_report", composer_result, metadata)
    """
    
    # 템플릿 디렉토리
    TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "reports"
    
    # 스타일 가이드 (Master Plan v3.3 Section 6)
    STYLE_GUIDE = """
    @page {
        size: A4;
        margin: 2cm 1.5cm;
        
        @top-right {
            content: "ZeroSite Report";
            font-size: 8pt;
            color: #666;
        }
        
        @bottom-center {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 8pt;
            color: #666;
        }
    }
    
    body {
        font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
        font-size: 10pt;
        line-height: 1.6;
        color: #333;
    }
    
    h1 {
        font-size: 18pt;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 0;
        margin-bottom: 10pt;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5pt;
    }
    
    h2 {
        font-size: 14pt;
        font-weight: 600;
        color: #34495e;
        margin-top: 15pt;
        margin-bottom: 8pt;
    }
    
    h3 {
        font-size: 12pt;
        font-weight: 600;
        color: #555;
        margin-top: 10pt;
        margin-bottom: 5pt;
    }
    
    /* Status colors (Master Plan v3.3) */
    .status-pass, .status-high { 
        color: #2ECC71; 
        font-weight: 600;
    }
    
    .status-warning, .status-medium { 
        color: #F1C40F; 
        font-weight: 600;
    }
    
    .status-fail, .status-low { 
        color: #E74C3C; 
        font-weight: 600;
    }
    
    /* Header */
    .header {
        border-bottom: 2px solid #333;
        padding-bottom: 10pt;
        margin-bottom: 20pt;
    }
    
    .header h1 {
        border: none;
        margin-bottom: 5pt;
    }
    
    .header .metadata {
        font-size: 8pt;
        color: #666;
    }
    
    /* Footer */
    .footer {
        margin-top: 30pt;
        padding-top: 10pt;
        border-top: 1px solid #ddd;
        font-size: 8pt;
        color: #666;
        text-align: center;
    }
    
    /* Tables */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 10pt 0;
    }
    
    th {
        background-color: #f5f5f5;
        text-align: left;
        padding: 8pt;
        border: 1px solid #ddd;
        font-weight: 600;
    }
    
    td {
        padding: 8pt;
        border: 1px solid #ddd;
    }
    
    tr:nth-child(even) {
        background-color: #fafafa;
    }
    
    /* Lists */
    ul {
        margin: 10pt 0;
        padding-left: 20pt;
    }
    
    li {
        margin: 5pt 0;
    }
    
    /* Boxes */
    .info-box {
        background-color: #e8f4f8;
        border-left: 4px solid #3498db;
        padding: 10pt;
        margin: 10pt 0;
    }
    
    .warning-box {
        background-color: #fef5e7;
        border-left: 4px solid #f39c12;
        padding: 10pt;
        margin: 10pt 0;
    }
    
    .success-box {
        background-color: #e8f8f5;
        border-left: 4px solid #27ae60;
        padding: 10pt;
        margin: 10pt 0;
    }
    
    .danger-box {
        background-color: #fadbd8;
        border-left: 4px solid #e74c3c;
        padding: 10pt;
        margin: 10pt 0;
    }
    
    /* Metrics dashboard */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10pt;
        margin: 15pt 0;
    }
    
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 4pt;
        padding: 10pt;
        text-align: center;
    }
    
    .metric-label {
        font-size: 8pt;
        color: #666;
        text-transform: uppercase;
    }
    
    .metric-value {
        font-size: 16pt;
        font-weight: 700;
        color: #2c3e50;
        margin: 5pt 0;
    }
    
    .metric-unit {
        font-size: 9pt;
        color: #888;
    }
    
    /* Page breaks */
    .page-break {
        page-break-after: always;
    }
    
    .avoid-break {
        page-break-inside: avoid;
    }
    
    /* Charts (simplified for PDF) */
    .chart-bar {
        background: #ecf0f1;
        border-radius: 2pt;
        padding: 5pt;
        margin: 5pt 0;
    }
    
    .chart-bar-fill {
        background: linear-gradient(to right, #3498db, #2980b9);
        height: 20pt;
        border-radius: 2pt;
        display: flex;
        align-items: center;
        padding: 0 5pt;
        color: white;
        font-weight: 600;
    }
    """
    
    # 보고서 타입별 템플릿 매핑
    REPORT_TEMPLATES = {
        "pre_report": "pre_report.html",
        "comprehensive": "comprehensive.html",
        "lh_decision": "lh_decision.html",
        "investor": "investor.html",
        "land_price": "land_price.html",
        "internal": "internal.html",
        "full_report": "full_report.html"
    }
    
    def __init__(self):
        """Initialize PDF Generator"""
        # 템플릿 디렉토리 생성
        self.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Jinja2 환경 설정
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.TEMPLATE_DIR)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Custom filters 등록
        self.jinja_env.filters['format_number'] = self._format_number
        self.jinja_env.filters['format_currency'] = self._format_currency
        self.jinja_env.filters['format_percent'] = self._format_percent
        
        logger.info(f"PDFGenerator initialized. Template dir: {self.TEMPLATE_DIR}")
    
    def generate(
        self, 
        report_type: str, 
        composer_result: Dict[str, Any], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Composer 결과물을 PDF로 변환
        
        Args:
            report_type: "pre_report", "comprehensive", "investor" 등
            composer_result: Composer.compose() 반환값
            metadata: 추가 메타데이터 (report_id, created_at 등)
            
        Returns:
            PDF 바이트 데이터
            
        Raises:
            ValueError: Unknown report type
            FileNotFoundError: Template not found
        """
        # 1. 템플릿 이름 확인
        template_name = self.REPORT_TEMPLATES.get(report_type)
        if not template_name:
            raise ValueError(f"Unknown report type: {report_type}")
        
        # 2. HTML 렌더링
        html_content = self._render_template(template_name, composer_result, metadata or {})
        
        # 3. PDF 변환
        try:
            pdf_bytes = self._convert_to_pdf(html_content)
            logger.info(f"PDF generated successfully for {report_type}")
            return pdf_bytes
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def _render_template(
        self, 
        template_name: str, 
        data: Dict[str, Any], 
        metadata: Dict[str, Any]
    ) -> str:
        """HTML 템플릿에 데이터 바인딩"""
        try:
            template = self.jinja_env.get_template(template_name)
        except Exception as e:
            logger.error(f"Template {template_name} not found: {e}")
            # Fallback to simple template
            return self._create_simple_html(data, metadata)
        
        context = {
            "data": data,
            "metadata": metadata,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_id": metadata.get("report_id", "N/A")
        }
        
        return template.render(**context)
    
    def _convert_to_pdf(self, html_content: str) -> bytes:
        """HTML을 PDF로 변환"""
        try:
            html = HTML(string=html_content)
            css = CSS(string=self.STYLE_GUIDE)
            
            # Write PDF with stylesheets
            pdf_bytes = html.write_pdf(stylesheets=[css])
            return pdf_bytes
        except TypeError as e:
            # Fallback for version compatibility issues
            logger.warning(f"PDF generation with CSS failed ({e}), trying without CSS")
            html = HTML(string=html_content)
            return html.write_pdf()
    
    def _create_simple_html(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """템플릿이 없을 때 간단한 HTML 생성"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>ZeroSite Report</title>
        </head>
        <body>
            <div class="header">
                <h1>ZeroSite Report</h1>
                <p>Report ID: {metadata.get('report_id', 'N/A')}</p>
                <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            <div>
                <h2>Report Data</h2>
                <pre>{str(data)}</pre>
            </div>
        </body>
        </html>
        """
    
    def generate_to_file(
        self, 
        report_type: str, 
        composer_result: Dict[str, Any], 
        output_path: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        PDF를 파일로 저장
        
        Returns:
            저장된 파일 경로
        """
        pdf_bytes = self.generate(report_type, composer_result, metadata)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'wb') as f:
            f.write(pdf_bytes)
        
        logger.info(f"PDF saved to {output_path}")
        return str(output_file)
    
    # ========================================
    # Jinja2 Custom Filters
    # ========================================
    
    @staticmethod
    def _format_number(value: float, decimal_places: int = 2) -> str:
        """숫자 포맷팅"""
        if value is None:
            return "N/A"
        return f"{value:,.{decimal_places}f}"
    
    @staticmethod
    def _format_currency(value: float, unit: str = "원") -> str:
        """통화 포맷팅"""
        if value is None:
            return "N/A"
        if value >= 100_000_000:  # 1억 이상
            return f"{value / 100_000_000:,.1f}억{unit}"
        elif value >= 10_000:  # 1만 이상
            return f"{value / 10_000:,.0f}만{unit}"
        else:
            return f"{value:,.0f}{unit}"
    
    @staticmethod
    def _format_percent(value: float, decimal_places: int = 1) -> str:
        """퍼센트 포맷팅"""
        if value is None:
            return "N/A"
        return f"{value:.{decimal_places}f}%"
