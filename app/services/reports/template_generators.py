"""
ZeroSite v40.5 - Template-Based Report Generators
간략 보고서 생성기 (템플릿 기반)

목적: 빠른 구현을 위한 템플릿 기반 생성기
보고서:
- Policy Impact (15p)
- Developer Feasibility (15~20p)
- Extended Professional (25~40p)

Created: 2025-12-14
"""

from typing import Dict
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from .base_report_generator import BaseReportGenerator


# ============================================
# Policy Impact Report (15p)
# ============================================

class PolicyImpactGenerator(BaseReportGenerator):
    """정책 영향 분석 보고서 (15p) - 템플릿 기반"""
    
    def generate(self, context: Dict) -> bytes:
        """정책 영향 분석 보고서 생성"""
        buffer = io.BytesIO()
        self.pdf = canvas.Canvas(buffer, pagesize=A4)
        
        # Cover
        self.draw_cover_page(
            "정책 영향 분석 보고서",
            "Policy Impact Analysis Report",
            context
        )
        
        # Content pages (simplified)
        for page_num in range(2, 16):
            self._draw_content_page(context, page_num, 15)
        
        self.pdf.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _draw_content_page(self, context: Dict, page_num: int, total: int):
        """내용 페이지 그리기"""
        self.y_position = self.height - self.margin
        
        self.draw_page_header(
            f"정책 영향 분석 - Section {page_num-1}",
            f"Page {page_num}/{total}"
        )
        
        # Sample content based on page
        if page_num == 2:
            self.draw_subsection("1. Executive Summary")
            lh_review = context.get("lh_review", {})
            if lh_review:
                text = f"LH 통과 확률: {lh_review.get('pass_probability', 0):.1f}%"
                self.draw_text_block(text)
        
        elif page_num == 3:
            self.draw_subsection("2. 정책 환경 분석")
            self.draw_text_block(
                "현재 정부의 공공주택 정책은 청년, 신혼부부, 고령자를 대상으로 "
                "다양한 지원 프로그램을 운영하고 있습니다."
            )
        
        elif page_num >= 4 and page_num <= 6:
            self.draw_subsection(f"{page_num-1}. 시나리오별 정책 기여도")
            scenario = context.get("scenario", {})
            scenarios = scenario.get("scenarios", [])
            if scenarios:
                for scen in scenarios[:3]:
                    text = f"• {scen.get('name', 'N/A')}: 정책점수 {scen.get('policy_score', 0)}점"
                    self.pdf.setFont(self.korean_font, 9)
                    self.pdf.drawString(self.margin, self.y_position, text)
                    self.y_position -= 7*mm
        
        else:
            self.draw_subsection(f"{page_num-1}. 추가 분석")
            self.draw_text_block(
                "상세 분석 내용은 v40.6에서 제공될 예정입니다. "
                "현재는 템플릿 기반 간략 보고서입니다."
            )
        
        self.draw_page_footer(str(page_num), str(total))
        self.pdf.showPage()


# ============================================
# Developer Feasibility Report (15~20p)
# ============================================

class DeveloperFeasibilityGenerator(BaseReportGenerator):
    """개발사업자용 타당성 보고서 (15~20p) - 템플릿 기반"""
    
    def generate(self, context: Dict) -> bytes:
        """사업타당성 보고서 생성"""
        buffer = io.BytesIO()
        self.pdf = canvas.Canvas(buffer, pagesize=A4)
        
        # Cover
        self.draw_cover_page(
            "개발사업자용 사업타당성 보고서",
            "Developer Feasibility Study",
            context
        )
        
        # Content pages
        for page_num in range(2, 19):
            self._draw_content_page(context, page_num, 18)
        
        self.pdf.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _draw_content_page(self, context: Dict, page_num: int, total: int):
        """내용 페이지 그리기"""
        self.y_position = self.height - self.margin
        
        self.draw_page_header(
            f"사업타당성 분석 - Section {page_num-1}",
            f"Page {page_num}/{total}"
        )
        
        if page_num == 2:
            self.draw_subsection("1. Executive Summary")
            appraisal = context.get("appraisal", {})
            text = f"토지 감정가: {self.format_currency(appraisal.get('final_value', 0))}"
            self.draw_text_block(text)
        
        elif page_num == 3:
            self.draw_subsection("2. 사업 개요")
            input_data = context.get("input", {})
            text = f"소재지: {input_data.get('address', 'N/A')}\n"
            text += f"면적: {input_data.get('land_area_sqm', 0):,.2f}㎡"
            self.draw_text_block(text)
        
        elif page_num >= 4 and page_num <= 7:
            self.draw_subsection(f"{page_num-1}. 재무 분석")
            scenario = context.get("scenario", {})
            scenarios = scenario.get("scenarios", [])
            if scenarios:
                for scen in scenarios[:3]:
                    text = f"• {scen.get('name', 'N/A')}: IRR {scen.get('irr', 0):.1f}%"
                    self.pdf.setFont(self.korean_font, 9)
                    self.pdf.drawString(self.margin, self.y_position, text)
                    self.y_position -= 7*mm
        
        elif page_num >= 8 and page_num <= 10:
            self.draw_subsection(f"{page_num-4}. 리스크 분석")
            lh_review = context.get("lh_review", {})
            if lh_review:
                text = f"LH 심사 리스크: {lh_review.get('risk_level', 'MEDIUM')}"
                self.draw_text_block(text)
        
        else:
            self.draw_subsection(f"{page_num-1}. 상세 분석")
            self.draw_text_block(
                "상세 재무 분석 및 민감도 분석은 v40.6에서 제공될 예정입니다."
            )
        
        self.draw_page_footer(str(page_num), str(total))
        self.pdf.showPage()


# ============================================
# Extended Professional Report (25~40p)
# ============================================

class ExtendedProfessionalGenerator(BaseReportGenerator):
    """전문가용 상세 보고서 (25~40p) - 템플릿 기반"""
    
    def generate(self, context: Dict) -> bytes:
        """전문가용 상세 보고서 생성"""
        buffer = io.BytesIO()
        self.pdf = canvas.Canvas(buffer, pagesize=A4)
        
        # Cover
        self.draw_cover_page(
            "전문가용 상세 분석 보고서",
            "Extended Professional Report",
            context
        )
        
        # Table of Contents
        self._draw_toc()
        
        # Content pages
        for page_num in range(3, 31):
            self._draw_content_page(context, page_num, 30)
        
        self.pdf.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _draw_toc(self):
        """목차 페이지"""
        self.y_position = self.height - self.margin
        
        self.draw_page_header("목차 (Table of Contents)", "Page 2/30")
        
        sections = [
            "1. Executive Summary (LH 심사예측 포함)",
            "2. 토지 감정평가 (상세)",
            "3. 토지 진단 (상세)",
            "4. 규모 검토 (상세)",
            "5. 시나리오 분석 (A/B/C)",
            "6. LH 심사예측 (AI Judge)",
            "7. 종합 위험 평가",
            "8. 법률 및 세무 검토",
            "9. 부록 (거래사례, 법규)",
        ]
        
        self.y_position -= 10*mm
        
        for idx, section in enumerate(sections, 1):
            self.pdf.setFont(self.korean_font, 10)
            self.pdf.drawString(self.margin, self.y_position, section)
            self.y_position -= 8*mm
        
        self.draw_page_footer("2", "30")
        self.pdf.showPage()
    
    def _draw_content_page(self, context: Dict, page_num: int, total: int):
        """내용 페이지 그리기"""
        self.y_position = self.height - self.margin
        
        section_num = (page_num - 2) // 3 + 1
        
        self.draw_page_header(
            f"Section {section_num} - 상세 분석",
            f"Page {page_num}/{total}"
        )
        
        if page_num == 3:
            self.draw_subsection("1. Executive Summary")
            lh_review = context.get("lh_review", {})
            appraisal = context.get("appraisal", {})
            
            text = f"감정가: {self.format_currency(appraisal.get('final_value', 0))}\n"
            if lh_review:
                text += f"LH 통과 확률: {lh_review.get('pass_probability', 0):.1f}%"
            
            self.draw_text_block(text)
        
        elif page_num >= 4 and page_num <= 9:
            self.draw_subsection("2. 토지 감정평가 상세 분석")
            appraisal = context.get("appraisal", {})
            
            if page_num == 4:
                text = "거래사례비교법 기반 감정평가 결과"
                self.draw_text_block(text)
                
                transactions = appraisal.get("transactions", [])
                if transactions:
                    self.y_position -= 5*mm
                    self.pdf.setFont(self.korean_font_bold, 10)
                    self.pdf.drawString(self.margin, self.y_position, "거래사례:")
                    self.y_position -= 7*mm
                    
                    for trans in transactions[:5]:
                        text = f"• {trans.get('date', 'N/A')[:10]}, {trans.get('distance', 0):.0f}m"
                        self.pdf.setFont(self.korean_font, 8)
                        self.pdf.drawString(self.margin + 5*mm, self.y_position, text)
                        self.y_position -= 6*mm
            else:
                text = f"감정평가 상세 분석 (페이지 {page_num})"
                self.draw_text_block(text)
        
        elif page_num >= 10 and page_num <= 15:
            self.draw_subsection(f"{section_num}. 토지 진단 및 규모 검토")
            self.draw_text_block(
                "용도지역, 건폐율, 용적률 등 상세 분석 내용"
            )
        
        elif page_num >= 16 and page_num <= 20:
            self.draw_subsection(f"{section_num}. 시나리오 분석")
            scenario = context.get("scenario", {})
            scenarios = scenario.get("scenarios", [])
            
            if scenarios:
                for scen in scenarios[:3]:
                    text = f"• {scen.get('name', 'N/A')}: 정책 {scen.get('policy_score', 0)}점, IRR {scen.get('irr', 0):.1f}%"
                    self.pdf.setFont(self.korean_font, 9)
                    self.pdf.drawString(self.margin, self.y_position, text)
                    self.y_position -= 7*mm
        
        elif page_num >= 21 and page_num <= 25:
            self.draw_subsection(f"{section_num}. LH 심사예측 상세")
            lh_review = context.get("lh_review", {})
            
            if lh_review:
                factors = lh_review.get("factors", [])
                for factor in factors[:6]:
                    text = f"• {factor.get('factor_name', 'N/A')}: {factor.get('score', 0):.0f}점"
                    self.pdf.setFont(self.korean_font, 9)
                    self.pdf.drawString(self.margin, self.y_position, text)
                    self.y_position -= 7*mm
        
        else:
            self.draw_subsection(f"{section_num}. 부록 및 참고자료")
            self.draw_text_block(
                "상세 부록 내용은 v40.6에서 제공될 예정입니다."
            )
        
        self.draw_page_footer(str(page_num), str(total))
        self.pdf.showPage()
