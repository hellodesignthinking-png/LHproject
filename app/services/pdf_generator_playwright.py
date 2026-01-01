"""
ZeroSite v1.5.1 - Playwright 기반 PDF 생성 엔진 (워터마크 지원)

목표: 기존 HTML 보고서를 Chromium 기반으로 PDF 변환
핵심: 모든 PDF에 출처 추적 가능한 워터마크 삽입

v1.5.1 변경사항:
- Internal vs Shared PDF 시각적 구분
- RUN_ID, Report Type, Timestamp 워터마크
- 제거 불가능한 footer 워터마크
"""

from playwright.async_api import async_playwright
from typing import Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


async def generate_pdf_from_url(
    url: str,
    run_id: str,
    report_type: str,
    timeout_ms: int = 60000,  # 기본 60초로 증가
    is_shared: Optional[bool] = None  # v1.5.1: deprecated, kept for backward compatibility
) -> bytes:
    """
    HTML 보고서 URL을 PDF로 변환한다.
    
    🔏 v1.5.1: 워터마크 지원 추가
    - RUN_ID 기반 워터마크 (접근 방식 무관)
    - "ZeroSite Confidential Document"
    - RUN_ID, Report Type, Generated Timestamp 포함
    
    Args:
        url: 내부 HTML 보고서 엔드포인트 (예: http://localhost:8091/api/v4/reports/...)
        run_id: RUN_ID (Site Identity)
        report_type: A~F (보고서 유형)
        timeout_ms: 페이지 로드 타임아웃 (밀리초)
        is_shared: Deprecated (워터마크는 RUN_ID 기반으로 통일)
    
    Returns:
        PDF bytes
    
    Raises:
        Exception: PDF 생성 실패 시
    """
    logger.info(f"📄 Starting PDF generation: RUN_ID={run_id}, Type={report_type} (with watermark)")
    
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
            
            # 🔏 v1.5.1: 워터마크 생성 (RUN_ID 기반, 접근 방식 무관)
            generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            
            # RUN_ID 기반 워터마크 (Internal/Shared 구분 없음 - 캐시 공유)
            watermark_text = f"🔒 ZeroSite Confidential Document"
            watermark_details = f"RUN_ID: {run_id} | Report: {report_type} | {generated_at}"
            watermark_color = "rgba(120, 120, 120, 0.65)"
            
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
                footer_template=f"""
                  <div style="
                    font-size: 9px;
                    text-align: center;
                    width: 100%;
                    padding: 10px 0;
                    border-top: 2px solid {watermark_color};
                    background: linear-gradient(to bottom, rgba(250,250,250,0.9), rgba(240,240,240,0.95));
                  ">
                    <div style="
                      font-weight: 700;
                      color: {watermark_color};
                      margin-bottom: 5px;
                      letter-spacing: 1px;
                      font-size: 10px;
                    ">
                      {watermark_text}
                    </div>
                    <div style="
                      font-size: 8px;
                      color: rgba(80, 80, 80, 0.8);
                      font-family: 'Courier New', monospace;
                      margin-bottom: 4px;
                    ">
                      {watermark_details}
                    </div>
                    <div style="
                      font-size: 7px;
                      color: #999;
                      margin-top: 3px;
                    ">
                      Page <span class="pageNumber"></span> of <span class="totalPages"></span> | This document is traceable and confidential
                    </div>
                  </div>
                """,
                margin={
                    "top": "20mm",
                    "bottom": "28mm",  # v1.5.1: 워터마크 공간 확보
                    "left": "15mm",
                    "right": "15mm"
                },
                prefer_css_page_size=False,  # A4 강제 적용
            )
            
            await browser.close()
            
            logger.info(f"✅ PDF generated with watermark: {len(pdf_bytes)} bytes, RUN_ID={run_id}")
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
