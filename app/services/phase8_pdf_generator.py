"""
Phase 8: PDF Generator Service
================================

Playwright를 사용하여 HTML 보고서를 PDF로 변환하는 서비스

작성일: 2026-01-10
"""

import asyncio
import logging
from typing import Optional
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)

# Playwright는 선택적 의존성이므로 try-except로 감싸기
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. PDF generation will be disabled.")


class Phase8PDFGenerator:
    """HTML → PDF 변환 서비스"""
    
    def __init__(self):
        """초기화"""
        self.playwright_available = PLAYWRIGHT_AVAILABLE
        if not self.playwright_available:
            logger.warning("PDF Generator initialized without Playwright support")
        else:
            logger.info("PDF Generator initialized with Playwright support")
    
    async def html_to_pdf(
        self,
        html_content: str,
        output_path: Optional[str] = None,
        page_format: str = "A4",
        margin: dict = None,
        landscape: bool = False,
        print_background: bool = True,
        header_template: Optional[str] = None,
        footer_template: Optional[str] = None,
    ) -> bytes:
        """
        HTML을 PDF로 변환
        
        Args:
            html_content: HTML 문자열
            output_path: 출력 파일 경로 (None이면 바이트 반환)
            page_format: 페이지 포맷 (A4, Letter, Legal 등)
            margin: 여백 설정 {"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"}
            landscape: 가로 방향 여부
            print_background: 배경색 인쇄 여부
            header_template: 헤더 HTML 템플릿
            footer_template: 푸터 HTML 템플릿
        
        Returns:
            PDF 바이트 데이터
        """
        if not self.playwright_available:
            raise RuntimeError("Playwright is not installed. Please install: pip install playwright && playwright install chromium")
        
        # 기본 여백 설정
        if margin is None:
            margin = {
                "top": "20mm",
                "right": "15mm",
                "bottom": "20mm",
                "left": "15mm"
            }
        
        # 기본 푸터 (페이지 번호)
        if footer_template is None:
            footer_template = """
            <div style="font-size: 10px; text-align: center; width: 100%; padding: 10px 0;">
                <span class="pageNumber"></span> / <span class="totalPages"></span>
            </div>
            """
        
        try:
            async with async_playwright() as p:
                # 브라우저 실행
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # HTML 컨텐츠 로드
                await page.set_content(html_content, wait_until="networkidle")
                
                # PDF 생성 옵션
                pdf_options = {
                    "format": page_format,
                    "margin": margin,
                    "landscape": landscape,
                    "print_background": print_background,
                    "display_header_footer": bool(header_template or footer_template),
                }
                
                if header_template:
                    pdf_options["header_template"] = header_template
                if footer_template:
                    pdf_options["footer_template"] = footer_template
                
                if output_path:
                    pdf_options["path"] = output_path
                
                # PDF 생성
                pdf_bytes = await page.pdf(**pdf_options)
                
                # 브라우저 종료
                await browser.close()
                
                logger.info(f"PDF generated successfully. Size: {len(pdf_bytes)} bytes")
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Failed to generate PDF: {str(e)}", exc_info=True)
            raise
    
    async def url_to_pdf(
        self,
        url: str,
        output_path: Optional[str] = None,
        page_format: str = "A4",
        margin: dict = None,
        landscape: bool = False,
        wait_for_selector: Optional[str] = None,
        timeout: int = 30000,
    ) -> bytes:
        """
        URL을 PDF로 변환
        
        Args:
            url: 변환할 URL
            output_path: 출력 파일 경로
            page_format: 페이지 포맷
            margin: 여백 설정
            landscape: 가로 방향 여부
            wait_for_selector: 대기할 CSS 셀렉터
            timeout: 타임아웃 (밀리초)
        
        Returns:
            PDF 바이트 데이터
        """
        if not self.playwright_available:
            raise RuntimeError("Playwright is not installed")
        
        if margin is None:
            margin = {
                "top": "20mm",
                "right": "15mm",
                "bottom": "20mm",
                "left": "15mm"
            }
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # URL 로드
                await page.goto(url, wait_until="networkidle", timeout=timeout)
                
                # 특정 셀렉터 대기 (선택)
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=timeout)
                
                # PDF 생성
                pdf_options = {
                    "format": page_format,
                    "margin": margin,
                    "landscape": landscape,
                    "print_background": True,
                    "display_header_footer": True,
                    "footer_template": """
                    <div style="font-size: 10px; text-align: center; width: 100%; padding: 10px 0;">
                        <span class="pageNumber"></span> / <span class="totalPages"></span>
                    </div>
                    """
                }
                
                if output_path:
                    pdf_options["path"] = output_path
                
                pdf_bytes = await page.pdf(**pdf_options)
                
                await browser.close()
                
                logger.info(f"PDF generated from URL: {url}. Size: {len(pdf_bytes)} bytes")
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Failed to generate PDF from URL: {str(e)}", exc_info=True)
            raise


# 싱글톤 인스턴스
pdf_generator = Phase8PDFGenerator()
