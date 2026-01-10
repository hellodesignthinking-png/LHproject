"""
Playwright 기반 PDF 생성 서비스
================================

HTML을 고품질 PDF로 변환합니다.

Version: 1.0
Date: 2026-01-10
"""

import asyncio
import logging
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger(__name__)


class PlaywrightPDFGenerator:
    """
    Playwright를 사용한 PDF 생성 엔진
    
    **특징**:
    - Chromium 헤드리스 브라우저 사용
    - CSS 미디어 쿼리 지원 (@media print)
    - 배경 그래픽 포함
    - 한글 폰트 렌더링
    
    **사용 예시**:
    ```python
    generator = PlaywrightPDFGenerator()
    pdf_bytes = await generator.generate_pdf_from_html(
        html_content="<html>...</html>",
        filename="report.pdf"
    )
    ```
    """
    
    def __init__(self):
        self._browser: Optional[Browser] = None
    
    async def _get_browser(self) -> Browser:
        """브라우저 인스턴스 가져오기 (재사용)"""
        if self._browser is None or not self._browser.is_connected():
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            logger.info("✅ Playwright Chromium 브라우저 시작")
        
        return self._browser
    
    async def generate_pdf_from_html(
        self,
        html_content: str,
        filename: str = "document.pdf",
        page_format: str = "A4",
        print_background: bool = True,
        margin: Optional[dict] = None
    ) -> bytes:
        """
        HTML 문자열을 PDF로 변환
        
        Args:
            html_content: HTML 문자열
            filename: 파일명 (메타데이터용)
            page_format: 페이지 크기 (A4, A3, Letter 등)
            print_background: 배경 그래픽 포함 여부
            margin: 여백 설정 (예: {"top": "2cm", "bottom": "2cm"})
        
        Returns:
            PDF 바이트 데이터
        """
        browser = await self._get_browser()
        page: Page = await browser.new_page()
        
        try:
            # HTML 로드
            await page.set_content(html_content, wait_until="networkidle")
            logger.info(f"📄 HTML 로드 완료: {len(html_content)} bytes")
            
            # PDF 생성 옵션
            pdf_options = {
                "format": page_format,
                "print_background": print_background,
                "prefer_css_page_size": False,  # format 우선 사용
            }
            
            # 여백 설정
            if margin is None:
                margin = {
                    "top": "2cm",
                    "right": "2cm",
                    "bottom": "2cm",
                    "left": "2cm"
                }
            pdf_options["margin"] = margin
            
            # PDF 생성
            pdf_bytes = await page.pdf(**pdf_options)
            logger.info(f"✅ PDF 생성 완료: {filename} ({len(pdf_bytes)} bytes)")
            
            return pdf_bytes
        
        except Exception as e:
            logger.error(f"❌ PDF 생성 실패: {e}", exc_info=True)
            raise
        
        finally:
            await page.close()
    
    async def generate_pdf_from_url(
        self,
        url: str,
        filename: str = "document.pdf",
        page_format: str = "A4",
        print_background: bool = True,
        margin: Optional[dict] = None,
        wait_for_selector: Optional[str] = None
    ) -> bytes:
        """
        URL에서 페이지를 로드하고 PDF로 변환
        
        Args:
            url: 대상 URL
            filename: 파일명
            page_format: 페이지 크기
            print_background: 배경 그래픽 포함
            margin: 여백 설정
            wait_for_selector: 대기할 CSS 셀렉터 (예: "#report-content")
        
        Returns:
            PDF 바이트 데이터
        """
        browser = await self._get_browser()
        page: Page = await browser.new_page()
        
        try:
            # URL 로드
            await page.goto(url, wait_until="networkidle", timeout=30000)
            logger.info(f"🌐 URL 로드 완료: {url}")
            
            # 특정 요소 대기 (옵션)
            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector, timeout=10000)
                logger.info(f"⏳ 셀렉터 대기 완료: {wait_for_selector}")
            
            # 추가 대기 (자바스크립트 렌더링)
            await asyncio.sleep(1)
            
            # PDF 생성 옵션
            pdf_options = {
                "format": page_format,
                "print_background": print_background,
                "prefer_css_page_size": False,
            }
            
            if margin is None:
                margin = {
                    "top": "2cm",
                    "right": "2cm",
                    "bottom": "2cm",
                    "left": "2cm"
                }
            pdf_options["margin"] = margin
            
            # PDF 생성
            pdf_bytes = await page.pdf(**pdf_options)
            logger.info(f"✅ PDF 생성 완료: {filename} ({len(pdf_bytes)} bytes)")
            
            return pdf_bytes
        
        except Exception as e:
            logger.error(f"❌ PDF 생성 실패 (URL: {url}): {e}", exc_info=True)
            raise
        
        finally:
            await page.close()
    
    async def close(self):
        """브라우저 종료"""
        if self._browser:
            await self._browser.close()
            self._browser = None
            logger.info("🔒 Playwright 브라우저 종료")


# 싱글톤 인스턴스
_pdf_generator: Optional[PlaywrightPDFGenerator] = None


async def get_pdf_generator() -> PlaywrightPDFGenerator:
    """PDF 생성기 싱글톤 인스턴스 가져오기"""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = PlaywrightPDFGenerator()
    return _pdf_generator


async def generate_pdf_from_html(
    html_content: str,
    filename: str = "document.pdf",
    **kwargs
) -> bytes:
    """
    편의 함수: HTML을 PDF로 변환
    
    Args:
        html_content: HTML 문자열
        filename: 파일명
        **kwargs: PDF 생성 옵션
    
    Returns:
        PDF 바이트 데이터
    """
    generator = await get_pdf_generator()
    return await generator.generate_pdf_from_html(html_content, filename, **kwargs)


async def generate_pdf_from_url(
    url: str,
    filename: str = "document.pdf",
    **kwargs
) -> bytes:
    """
    편의 함수: URL을 PDF로 변환
    
    Args:
        url: 대상 URL
        filename: 파일명
        **kwargs: PDF 생성 옵션
    
    Returns:
        PDF 바이트 데이터
    """
    generator = await get_pdf_generator()
    return await generator.generate_pdf_from_url(url, filename, **kwargs)
