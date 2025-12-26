"""
M7 PDF Renderer (ZeroSite v4.0)
================================

M7 보고서 데이터를 HTML → PDF로 변환

Author: ZeroSite M7 Team
Date: 2025-12-26
Version: 4.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


class PDFRenderer:
    """
    PDF 렌더링 엔진
    
    M7 보고서 데이터 → HTML → PDF
    """
    
    def __init__(self):
        """PDF 렌더러 초기화"""
        # Template directory
        template_dir = Path(__file__).parent / "templates"
        
        # Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
        
        # Font configuration for WeasyPrint
        self.font_config = FontConfiguration()
        
        logger.info("="*80)
        logger.info("📄 PDF Renderer Initialized")
        logger.info(f"   Template Directory: {template_dir}")
        logger.info("="*80)
    
    def render_to_html(self, report_data: Dict[str, Any]) -> str:
        """
        보고서 데이터를 HTML로 렌더링
        
        Args:
            report_data: M7 보고서 데이터
        
        Returns:
            HTML 문자열
        """
        template = self.env.get_template("full_report.html")
        html_content = template.render(**report_data)
        return html_content
    
    def render_to_pdf(
        self,
        report_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        보고서 데이터를 PDF로 렌더링
        
        Args:
            report_data: M7 보고서 데이터
            output_path: PDF 저장 경로 (선택)
        
        Returns:
            PDF 바이트 데이터
        """
        logger.info("\n" + "="*80)
        logger.info("📄 PDF RENDERING START")
        logger.info("="*80)
        
        # Step 1: HTML 렌더링
        logger.info("[1/3] Rendering HTML from template...")
        html_content = self.render_to_html(report_data)
        logger.info(f"✓ HTML rendered ({len(html_content)} characters)")
        
        # Step 2: PDF 생성
        logger.info("[2/3] Converting HTML to PDF...")
        
        # WeasyPrint HTML 객체 생성
        html_obj = HTML(string=html_content)
        
        # PDF 생성 (target 없이 바이트 반환)
        pdf_bytes = html_obj.write_pdf(font_config=self.font_config)
        logger.info(f"✓ PDF generated ({len(pdf_bytes)} bytes)")
        
        # Step 3: 파일 저장 (선택)
        if output_path:
            logger.info(f"[3/3] Saving PDF to {output_path}...")
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            
            logger.info(f"✓ PDF saved to {output_path}")
        else:
            logger.info("[3/3] Skipping file save (output_path not provided)")
        
        logger.info("="*80)
        logger.info("✅ PDF RENDERING COMPLETE")
        logger.info("="*80 + "\n")
        
        return pdf_bytes
    
    def render_executive_summary_only(
        self,
        report_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        경영진 요약만 PDF로 렌더링 (간략 버전)
        
        Args:
            report_data: M7 보고서 데이터
            output_path: PDF 저장 경로 (선택)
        
        Returns:
            PDF 바이트 데이터
        """
        # Executive summary template 사용
        template = self.env.get_template("executive_summary.html")
        html_content = template.render(**report_data)
        
        html_obj = HTML(string=html_content)
        pdf_bytes = html_obj.write_pdf(font_config=self.font_config)
        
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes


def generate_pdf_from_report(
    report_data: Dict[str, Any],
    output_path: str
) -> str:
    """
    편의 함수: 보고서 데이터로부터 PDF 생성
    
    Args:
        report_data: M7 보고서 데이터
        output_path: PDF 저장 경로
    
    Returns:
        생성된 PDF 파일 경로
    """
    renderer = PDFRenderer()
    renderer.render_to_pdf(report_data, output_path)
    return output_path


__all__ = ["PDFRenderer", "generate_pdf_from_report"]
