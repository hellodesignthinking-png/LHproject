"""
ZeroSite v1.1 - Playwright 기반 PDF 생성 엔진

목표: 기존 HTML 보고서를 Chromium 기반으로 PDF 변환
"""

from playwright.async_api import async_playwright
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def generate_pdf_from_url(
    url: str,
    run_id: str,
    report_type: str,
    timeout_ms: int = 60000  # 기본 60초로 증가
) -> bytes:
    """
    HTML 보고서 URL을 PDF로 변환한다.
    
    Args:
        url: 내부 HTML 보고서 엔드포인트 (예: http://localhost:8091/api/v4/reports/...)
        run_id: RUN_ID (Site Identity)
        report_type: A~F (보고서 유형)
        timeout_ms: 페이지 로드 타임아웃 (밀리초)
    
    Returns:
        PDF bytes
    
    Raises:
        Exception: PDF 생성 실패 시
    """
    logger.info(f"📄 Starting PDF generation: RUN_ID={run_id}, Type={report_type}")
    
    try:
        async with async_playwright() as p:
            # Chromium 브라우저 시작
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",  # Docker 환경에서 메모리 이슈 방지
                ]
            )
            
            # 새 페이지 생성
            page = await browser.new_page()
            
            # HTML 로드 (load = DOM 로드 완료만 대기, networkidle은 너무 느림)
            logger.info(f"⏳ Loading HTML from: {url}")
            await page.goto(url, wait_until="load", timeout=timeout_ms)
            
            # 추가 대기: JavaScript 렌더링 완료
            await page.wait_for_timeout(2000)  # 2초 대기
            
            # PDF 생성 옵션
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,  # 배경색/이미지 포함
                display_header_footer=True,
                header_template=f"""
                  <div style="font-size:9px; text-align:center; width:100%; padding: 5px 0;">
                    <span style="color: #666;">ZeroSite Report | RUN_ID: {run_id} | TYPE: {report_type}</span>
                  </div>
                """,
                footer_template="""
                  <div style="font-size:9px; text-align:center; width:100%; padding: 5px 0;">
                    <span style="color: #666;">Page <span class="pageNumber"></span> / <span class="totalPages"></span></span>
                  </div>
                """,
                margin={
                    "top": "20mm",
                    "bottom": "20mm",
                    "left": "15mm",
                    "right": "15mm"
                },
                prefer_css_page_size=False,  # A4 강제 적용
            )
            
            await browser.close()
            
            logger.info(f"✅ PDF generated successfully: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
    except Exception as e:
        logger.error(f"❌ PDF generation failed: {e}", exc_info=True)
        raise Exception(f"PDF generation failed for RUN_ID={run_id}, Type={report_type}: {str(e)}")


async def generate_pdf_with_custom_options(
    url: str,
    run_id: str,
    report_type: str,
    **pdf_options
) -> bytes:
    """
    커스텀 PDF 옵션을 사용하여 PDF 생성
    
    Args:
        url: HTML 보고서 URL
        run_id: RUN_ID
        report_type: A~F
        **pdf_options: page.pdf()에 전달할 추가 옵션
    
    Returns:
        PDF bytes
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        
        # 기본 옵션 + 커스텀 옵션 병합
        default_options = {
            "format": "A4",
            "print_background": True,
        }
        merged_options = {**default_options, **pdf_options}
        
        pdf_bytes = await page.pdf(**merged_options)
        await browser.close()
        
        return pdf_bytes
