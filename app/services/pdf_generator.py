"""
ZeroSite PDF Generator
Version: 1.0
Purpose: HTML → PDF 변환 (LH 제출용)
Methods: WeasyPrint (우선), Playwright (폴백)
"""

import os
import logging
from typing import Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    LH 제출용 PDF 생성 엔진
    
    Features:
    - HTML → PDF 변환
    - 표지/목차/페이지 번호 자동 생성
    - 한글 폰트 지원
    - 워터마크 추가
    """
    
    def __init__(self):
        self.output_dir = Path("/tmp/zerosite_pdfs")
        self.output_dir.mkdir(exist_ok=True)
        
        # 한글 폰트 경로
        self.font_paths = [
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf",
            "/System/Library/Fonts/AppleGothic.ttf",  # macOS
        ]
        
        self.use_weasyprint = self._check_weasyprint()
        self.use_playwright = self._check_playwright()
        
        if not self.use_weasyprint and not self.use_playwright:
            logger.warning("No PDF generation method available. PDF generation will fail.")
    
    def _check_weasyprint(self) -> bool:
        """WeasyPrint 사용 가능 여부 확인"""
        try:
            import weasyprint
            logger.info("✅ WeasyPrint available")
            return True
        except ImportError:
            logger.warning("⚠️ WeasyPrint not available")
            return False
    
    def _check_playwright(self) -> bool:
        """Playwright 사용 가능 여부 확인"""
        try:
            from playwright.sync_api import sync_playwright
            logger.info("✅ Playwright available")
            return True
        except ImportError:
            logger.warning("⚠️ Playwright not available")
            return False
    
    def generate_pdf_from_html(
        self,
        html_content: str,
        output_filename: str,
        add_cover: bool = True,
        add_toc: bool = True,
        add_watermark: bool = True,
        metadata: Optional[dict] = None
    ) -> str:
        """
        HTML을 PDF로 변환
        
        Args:
            html_content: HTML 문자열
            output_filename: 출력 파일명
            add_cover: 표지 추가 여부
            add_toc: 목차 추가 여부
            add_watermark: 워터마크 추가 여부
            metadata: PDF 메타데이터
        
        Returns:
            생성된 PDF 파일 경로
        """
        # 전처리: 표지/목차/워터마크 추가
        processed_html = self._preprocess_html(
            html_content,
            add_cover=add_cover,
            add_toc=add_toc,
            add_watermark=add_watermark,
            metadata=metadata or {}
        )
        
        # PDF 생성 (WeasyPrint 우선)
        if self.use_weasyprint:
            return self._generate_with_weasyprint(processed_html, output_filename, metadata)
        elif self.use_playwright:
            return self._generate_with_playwright(processed_html, output_filename, metadata)
        else:
            raise RuntimeError("No PDF generation method available")
    
    def _preprocess_html(
        self,
        html_content: str,
        add_cover: bool,
        add_toc: bool,
        add_watermark: bool,
        metadata: dict
    ) -> str:
        """HTML 전처리: 표지/목차/워터마크 추가"""
        
        # CSS 스타일 추가
        pdf_styles = """
        <style>
            @page {
                size: A4;
                margin: 2.5cm 2cm;
                
                @top-right {
                    content: "ZeroSite Decision OS";
                    font-size: 10pt;
                    color: #666;
                }
                
                @bottom-center {
                    content: counter(page) " / " counter(pages);
                    font-size: 10pt;
                    color: #666;
                }
            }
            
            @page :first {
                @top-right { content: none; }
                @bottom-center { content: none; }
            }
            
            body {
                font-family: 'Nanum Gothic', 'Malgun Gothic', sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
            }
            
            h1 {
                font-size: 24pt;
                font-weight: bold;
                margin-top: 1cm;
                margin-bottom: 0.5cm;
                page-break-after: avoid;
            }
            
            h2 {
                font-size: 18pt;
                font-weight: bold;
                margin-top: 0.8cm;
                margin-bottom: 0.4cm;
                page-break-after: avoid;
            }
            
            h3 {
                font-size: 14pt;
                font-weight: bold;
                margin-top: 0.6cm;
                margin-bottom: 0.3cm;
            }
            
            .module-section {
                page-break-before: always;
            }
            
            .no-break {
                page-break-inside: avoid;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1cm 0;
                page-break-inside: avoid;
            }
            
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            
            th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
            
            .watermark {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotate(-45deg);
                font-size: 72pt;
                color: rgba(200, 200, 200, 0.1);
                z-index: -1;
                font-weight: bold;
            }
        </style>
        """
        
        # 표지 HTML
        cover_html = ""
        if add_cover:
            cover_html = f"""
            <div class="cover-page" style="text-align: center; padding-top: 6cm;">
                <h1 style="font-size: 36pt; margin-bottom: 1cm;">
                    LH 신축매입임대<br>사업 타당성 분석
                </h1>
                <p style="font-size: 18pt; color: #666; margin-bottom: 3cm;">
                    ZeroSite Decision OS
                </p>
                <table style="width: 60%; margin: 0 auto; border: none;">
                    <tr style="border: none;">
                        <th style="text-align: right; border: none; padding: 10px;">프로젝트명:</th>
                        <td style="border: none; padding: 10px;">{metadata.get('project_name', 'N/A')}</td>
                    </tr>
                    <tr style="border: none;">
                        <th style="text-align: right; border: none; padding: 10px;">지번:</th>
                        <td style="border: none; padding: 10px;">{metadata.get('land_address', 'N/A')}</td>
                    </tr>
                    <tr style="border: none;">
                        <th style="text-align: right; border: none; padding: 10px;">분석일:</th>
                        <td style="border: none; padding: 10px;">{datetime.now().strftime('%Y-%m-%d')}</td>
                    </tr>
                </table>
            </div>
            <div style="page-break-after: always;"></div>
            """
        
        # 목차 HTML
        toc_html = ""
        if add_toc:
            toc_html = """
            <div class="toc" style="padding: 1cm 0;">
                <h1>목차</h1>
                <ul style="list-style: none; padding-left: 0;">
                    <li style="margin: 10px 0;"><a href="#executive-summary">Executive Summary (M6)</a></li>
                    <li style="margin: 10px 0;"><a href="#m1">M1. 토지·입지 사실 확정</a></li>
                    <li style="margin: 10px 0;"><a href="#m2">M2. 토지 매입 적정성</a></li>
                    <li style="margin: 10px 0;"><a href="#m3">M3. 공급유형 적합성</a></li>
                    <li style="margin: 10px 0;"><a href="#m4">M4. 건축 규모 검토</a></li>
                    <li style="margin: 10px 0;"><a href="#m5">M5. 사업성·리스크 검증</a></li>
                    <li style="margin: 10px 0;"><a href="#m7">M7. 커뮤니티 계획</a></li>
                    <li style="margin: 10px 0;"><a href="#appendix">부록</a></li>
                </ul>
            </div>
            <div style="page-break-after: always;"></div>
            """
        
        # 워터마크 HTML
        watermark_html = ""
        if add_watermark:
            watermark_html = '<div class="watermark">ZeroSite</div>'
        
        # 최종 HTML 조립
        final_html = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>ZeroSite Report - {metadata.get('project_name', 'Analysis')}</title>
            {pdf_styles}
        </head>
        <body>
            {watermark_html}
            {cover_html}
            {toc_html}
            {html_content}
        </body>
        </html>
        """
        
        return final_html
    
    def _generate_with_weasyprint(
        self,
        html_content: str,
        output_filename: str,
        metadata: Optional[dict]
    ) -> str:
        """WeasyPrint로 PDF 생성"""
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            output_path = self.output_dir / output_filename
            
            # 폰트 설정
            font_config = FontConfiguration()
            
            # CSS 추가 (한글 폰트)
            css = CSS(string="""
                @font-face {
                    font-family: 'Nanum Gothic';
                    src: local('NanumGothic');
                }
            """, font_config=font_config)
            
            # PDF 생성
            doc = HTML(string=html_content)
            doc.write_pdf(
                str(output_path),
                stylesheets=[css],
                font_config=font_config
            )
            
            logger.info(f"✅ PDF generated with WeasyPrint: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ WeasyPrint PDF generation failed: {e}")
            raise
    
    def _generate_with_playwright(
        self,
        html_content: str,
        output_filename: str,
        metadata: Optional[dict]
    ) -> str:
        """Playwright로 PDF 생성 (폴백)"""
        try:
            from playwright.sync_api import sync_playwright
            
            output_path = self.output_dir / output_filename
            
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                
                # HTML 로드
                page.set_content(html_content)
                
                # PDF 생성
                page.pdf(
                    path=str(output_path),
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '2.5cm',
                        'right': '2cm',
                        'bottom': '2.5cm',
                        'left': '2cm'
                    }
                )
                
                browser.close()
            
            logger.info(f"✅ PDF generated with Playwright: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Playwright PDF generation failed: {e}")
            raise
    
    def generate_from_url(
        self,
        url: str,
        output_filename: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        URL에서 HTML을 가져와 PDF 생성
        
        Args:
            url: HTML 페이지 URL
            output_filename: 출력 파일명
            metadata: PDF 메타데이터
        
        Returns:
            생성된 PDF 파일 경로
        """
        try:
            import requests
            response = requests.get(url)
            response.raise_for_status()
            
            html_content = response.text
            return self.generate_pdf_from_html(
                html_content,
                output_filename,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to generate PDF from URL: {e}")
            raise


# Singleton instance
_pdf_generator = None


def get_pdf_generator() -> PDFGenerator:
    """PDF Generator 싱글톤 인스턴스 반환"""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = PDFGenerator()
    return _pdf_generator


# 편의 함수
def generate_pdf(html_content: str, output_filename: str, **kwargs) -> str:
    """편의 함수: PDF 생성"""
    generator = get_pdf_generator()
    return generator.generate_pdf_from_html(html_content, output_filename, **kwargs)
