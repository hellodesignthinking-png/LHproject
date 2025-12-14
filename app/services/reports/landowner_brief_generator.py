"""
ZeroSite v40.4 - Landowner Brief Report Generator
토지주용 간략 보고서 (3 페이지)

목적: 토지 소유주가 빠르게 이해할 수 있는 핵심 요약
대상: 일반 토지 소유주 (비전문가)
페이지: 3 pages
포함 내용:
- Page 1: 표지 + 핵심 요약
- Page 2: 감정가 및 개발 가능성
- Page 3: LH 심사예측 + Next Steps

Created: 2025-12-14
"""

from typing import Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime
import os


class LandownerBriefGenerator:
    """토지주용 3페이지 간략 보고서 생성기"""
    
    # Color Palette (Simple & Clear)
    COLOR_PRIMARY = (0.102, 0.357, 0.714)  # #1A5CB6 Blue
    COLOR_SUCCESS = (0.298, 0.686, 0.314)  # #4CAF50 Green
    COLOR_WARNING = (1.0, 0.596, 0.0)      # #FF9800 Orange
    COLOR_DANGER = (0.957, 0.263, 0.212)   # #F44336 Red
    COLOR_GREY = (0.5, 0.5, 0.5)           # Grey
    COLOR_BG_LIGHT = (0.96, 0.96, 0.96)    # Light Grey Background
    
    def __init__(self):
        self.width, self.height = A4
        self.margin = 20*mm
        self.y_position = 0
        
        # Register Korean fonts
        self._register_korean_fonts()
        
    def _register_korean_fonts(self):
        """Register Korean fonts"""
        try:
            font_paths = [
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Korean', font_path))
                    pdfmetrics.registerFont(TTFont('Korean-Bold', font_path))
                    self.korean_font = 'Korean'
                    self.korean_font_bold = 'Korean-Bold'
                    return
            
            self.korean_font = 'Helvetica'
            self.korean_font_bold = 'Helvetica-Bold'
            
        except Exception as e:
            self.korean_font = 'Helvetica'
            self.korean_font_bold = 'Helvetica-Bold'
    
    def generate(self, context: Dict) -> bytes:
        """
        토지주용 간략 보고서 생성
        
        Args:
            context: v40.3 full context (appraisal, diagnosis, capacity, scenario, lh_review)
            
        Returns:
            bytes: PDF file bytes
        """
        buffer = io.BytesIO()
        self.pdf = canvas.Canvas(buffer, pagesize=A4)
        
        # Page 1: Cover + Executive Summary
        self._page_1_cover_and_summary(context)
        
        # Page 2: Appraisal & Development Potential
        self._page_2_appraisal_and_development(context)
        
        # Page 3: LH Review + Next Steps
        self._page_3_lh_review_and_next_steps(context)
        
        # Finalize
        self.pdf.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    # ============================================
    # Page 1: Cover + Executive Summary
    # ============================================
    
    def _page_1_cover_and_summary(self, context: Dict):
        """Page 1: 표지 및 핵심 요약"""
        self.y_position = self.height - self.margin
        
        # Header Box
        self.pdf.setFillColorRGB(*self.COLOR_PRIMARY)
        self.pdf.rect(0, self.height - 80*mm, self.width, 80*mm, fill=True, stroke=False)
        
        # Title
        self.pdf.setFillColorRGB(1, 1, 1)  # White
        self.pdf.setFont(self.korean_font_bold, 24)
        title_text = "토지 분석 요약 보고서"
        self.pdf.drawCentredString(self.width/2, self.height - 40*mm, title_text)
        
        # Subtitle
        self.pdf.setFont(self.korean_font, 14)
        subtitle = "Landowner Brief Report"
        self.pdf.drawCentredString(self.width/2, self.height - 50*mm, subtitle)
        
        # Address
        address = context.get("input", {}).get("address", "주소 정보 없음")
        self.pdf.setFont(self.korean_font, 12)
        self.pdf.drawCentredString(self.width/2, self.height - 65*mm, address)
        
        # Date
        date_str = datetime.now().strftime("%Y년 %m월 %d일")
        self.pdf.setFont(self.korean_font, 10)
        self.pdf.drawCentredString(self.width/2, self.height - 75*mm, date_str)
        
        # Executive Summary Section
        self.y_position = self.height - 90*mm
        self._draw_section_header("핵심 요약 (Executive Summary)")
        
        appraisal = context.get("appraisal", {})
        lh_review = context.get("lh_review", {})
        scenario = context.get("scenario", {})
        
        # Key Metrics in Boxes
        self.y_position -= 10*mm
        
        # Row 1: Appraisal Value & Price per sqm
        metrics_y = self.y_position
        
        # Metric 1: 감정가
        self._draw_metric_box(
            self.margin, 
            metrics_y,
            70*mm,
            f"{appraisal.get('final_value', 0):,.0f} 원",
            "감정가"
        )
        
        # Metric 2: 평당 가격
        value_per_sqm = appraisal.get('value_per_sqm', 0)
        value_per_pyeong = value_per_sqm * 3.3058
        self._draw_metric_box(
            self.margin + 75*mm,
            metrics_y,
            70*mm,
            f"{value_per_pyeong:,.0f} 원/평",
            "평당 가격"
        )
        
        self.y_position -= 25*mm
        
        # Row 2: LH Pass Probability & Risk
        if lh_review:
            metrics_y = self.y_position
            
            # Metric 3: LH 통과 확률
            pass_prob = lh_review.get('pass_probability', 0)
            color = self._get_probability_color(pass_prob)
            self._draw_metric_box(
                self.margin,
                metrics_y,
                70*mm,
                f"{pass_prob:.1f}%",
                "LH 통과 확률",
                color=color
            )
            
            # Metric 4: 리스크 레벨
            risk_level = lh_review.get('risk_level', 'MEDIUM')
            risk_color = self._get_risk_color(risk_level)
            risk_kr = {"LOW": "낮음", "MEDIUM": "보통", "HIGH": "높음"}.get(risk_level, risk_level)
            self._draw_metric_box(
                self.margin + 75*mm,
                metrics_y,
                70*mm,
                risk_kr,
                "리스크 레벨",
                color=risk_color
            )
            
            self.y_position -= 25*mm
        
        # Recommended Scenario
        recommended = scenario.get("recommended", "정보 없음")
        self.pdf.setFont(self.korean_font_bold, 11)
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.drawString(self.margin, self.y_position, f"✓ 추천 시나리오: {recommended}")
        
        # Footer
        self.pdf.setFont(self.korean_font, 8)
        self.pdf.setFillColorRGB(*self.COLOR_GREY)
        footer_text = "ZeroSite v40.4 | AI 기반 토지 분석 시스템"
        self.pdf.drawCentredString(self.width/2, self.margin, footer_text)
        
        self.pdf.showPage()
    
    # ============================================
    # Page 2: Appraisal & Development
    # ============================================
    
    def _page_2_appraisal_and_development(self, context: Dict):
        """Page 2: 감정가 및 개발 가능성"""
        self.y_position = self.height - self.margin
        
        # Page Header
        self._draw_page_header("감정가 및 개발 가능성", "Page 2/3")
        
        appraisal = context.get("appraisal", {})
        diagnosis = context.get("diagnosis", {})
        capacity = context.get("capacity", {})
        
        # Section 1: 감정평가 결과
        self._draw_section_header("1. 감정평가 결과")
        self.y_position -= 5*mm
        
        # Appraisal Table
        final_value = appraisal.get('final_value', 0)
        value_per_sqm = appraisal.get('value_per_sqm', 0)
        land_area = context.get("input", {}).get("land_area_sqm", 0)
        
        appraisal_data = [
            ["항목", "금액"],
            ["총 감정가", f"{final_value:,.0f} 원"],
            ["평당 가격", f"{value_per_sqm * 3.3058:,.0f} 원/평"],
            ["제곱미터당", f"{value_per_sqm:,.0f} 원/㎡"],
            ["대지면적", f"{land_area:.2f} ㎡"],
        ]
        
        self._draw_simple_table(appraisal_data, 80*mm)
        self.y_position -= 35*mm
        
        # Section 2: 용도지역 및 규제
        self._draw_section_header("2. 용도지역 및 개발 규제")
        self.y_position -= 5*mm
        
        zone_type = appraisal.get("zoning", {}).get("zone_type", "정보 없음")
        far = appraisal.get("zoning", {}).get("far", 0)
        bcr = appraisal.get("zoning", {}).get("bcr", 0)
        
        zoning_data = [
            ["항목", "내용"],
            ["용도지역", zone_type],
            ["용적률", f"{far}%"],
            ["건폐율", f"{bcr}%"],
            ["적합성", diagnosis.get("suitability", "검토 필요")],
        ]
        
        self._draw_simple_table(zoning_data, 80*mm)
        self.y_position -= 35*mm
        
        # Section 3: 개발 규모
        self._draw_section_header("3. 예상 개발 규모")
        self.y_position -= 5*mm
        
        max_floor_area = capacity.get("max_floor_area", 0)
        max_units = capacity.get("max_units", 0)
        
        capacity_data = [
            ["항목", "수치"],
            ["최대 연면적", f"{max_floor_area:,.0f} ㎡"],
            ["예상 세대수", f"{max_units} 세대"],
            ["건축 면적", f"{capacity.get('max_building_area', 0):,.0f} ㎡"],
        ]
        
        self._draw_simple_table(capacity_data, 80*mm)
        
        # Footer
        self._draw_page_footer("2")
        self.pdf.showPage()
    
    # ============================================
    # Page 3: LH Review + Next Steps
    # ============================================
    
    def _page_3_lh_review_and_next_steps(self, context: Dict):
        """Page 3: LH 심사예측 및 다음 단계"""
        self.y_position = self.height - self.margin
        
        # Page Header
        self._draw_page_header("LH 심사예측 및 다음 단계", "Page 3/3")
        
        lh_review = context.get("lh_review", {})
        
        # Section 1: LH 심사예측 결과
        self._draw_section_header("1. LH 공공주택 사전심사 예측")
        self.y_position -= 5*mm
        
        if lh_review:
            # Overall Score
            score = lh_review.get('predicted_score', 0)
            probability = lh_review.get('pass_probability', 0)
            risk_level = lh_review.get('risk_level', 'MEDIUM')
            
            lh_summary_data = [
                ["평가 항목", "결과"],
                ["종합 점수", f"{score:.1f} / 100점"],
                ["통과 확률", f"{probability:.1f}%"],
                ["리스크 레벨", self._translate_risk(risk_level)],
            ]
            
            self._draw_simple_table(lh_summary_data, 80*mm)
            self.y_position -= 30*mm
            
            # Top 3 Factors
            self._draw_subsection("주요 평가 요소 (상위 3개)")
            self.y_position -= 3*mm
            
            factors = lh_review.get('factors', [])[:3]
            for i, factor in enumerate(factors, 1):
                factor_name = factor.get('factor_name', '평가요소')
                factor_score = factor.get('score', 0)
                
                self.pdf.setFont(self.korean_font, 9)
                self.pdf.drawString(self.margin + 5*mm, self.y_position, 
                                  f"{i}. {factor_name}: {factor_score:.0f}점")
                self.y_position -= 5*mm
            
            self.y_position -= 5*mm
            
            # Improvement Suggestions
            suggestions = lh_review.get('suggestions', [])
            if suggestions:
                self._draw_subsection("개선 제안")
                self.y_position -= 3*mm
                
                for i, suggestion in enumerate(suggestions[:3], 1):
                    self.pdf.setFont(self.korean_font, 9)
                    # Wrap text if too long
                    if len(suggestion) > 50:
                        suggestion = suggestion[:47] + "..."
                    self.pdf.drawString(self.margin + 5*mm, self.y_position,
                                      f"• {suggestion}")
                    self.y_position -= 5*mm
        else:
            self.pdf.setFont(self.korean_font, 10)
            self.pdf.drawString(self.margin, self.y_position,
                              "LH 심사예측 데이터가 없습니다. 먼저 예측을 실행하세요.")
            self.y_position -= 15*mm
        
        # Section 2: Next Steps
        self.y_position -= 10*mm
        self._draw_section_header("2. 다음 단계 (Next Steps)")
        self.y_position -= 5*mm
        
        next_steps = [
            "1. 전문가 상담: 감정평가사 또는 LH 전문 컨설턴트와 상담",
            "2. 상세 보고서: 필요시 전문가용 상세 보고서 (25~40p) 요청",
            "3. LH 제출: LH 제출용 보고서 작성 및 사전심사 신청",
            "4. 사업 추진: 통과 확률이 높을 경우 본격적인 사업 추진"
        ]
        
        for step in next_steps:
            self.pdf.setFont(self.korean_font, 9)
            self.pdf.drawString(self.margin + 5*mm, self.y_position, step)
            self.y_position -= 6*mm
        
        # Contact Box
        self.y_position -= 10*mm
        self._draw_contact_box()
        
        # Footer
        self._draw_page_footer("3")
        self.pdf.showPage()
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def _draw_metric_box(self, x, y, width, value, label, color=None):
        """Draw a metric box with value and label"""
        height = 18*mm
        
        # Box background
        if color is None:
            color = self.COLOR_PRIMARY
        self.pdf.setFillColorRGB(*color)
        self.pdf.setStrokeColorRGB(*color)
        self.pdf.rect(x, y - height, width, height, fill=False, stroke=True)
        
        # Value
        self.pdf.setFont(self.korean_font_bold, 16)
        self.pdf.setFillColorRGB(*color)
        self.pdf.drawCentredString(x + width/2, y - 8*mm, value)
        
        # Label
        self.pdf.setFont(self.korean_font, 9)
        self.pdf.setFillColorRGB(0.3, 0.3, 0.3)
        self.pdf.drawCentredString(x + width/2, y - 15*mm, label)
    
    def _draw_section_header(self, title):
        """Draw section header"""
        self.pdf.setFillColorRGB(*self.COLOR_PRIMARY)
        self.pdf.rect(self.margin, self.y_position - 7*mm, self.width - 2*self.margin, 7*mm, fill=True, stroke=False)
        
        self.pdf.setFillColorRGB(1, 1, 1)
        self.pdf.setFont(self.korean_font_bold, 12)
        self.pdf.drawString(self.margin + 3*mm, self.y_position - 5*mm, title)
        
        self.y_position -= 10*mm
    
    def _draw_subsection(self, title):
        """Draw subsection title"""
        self.pdf.setFont(self.korean_font_bold, 10)
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.drawString(self.margin, self.y_position, title)
        self.y_position -= 6*mm
    
    def _draw_page_header(self, title, page_info):
        """Draw page header"""
        self.pdf.setFont(self.korean_font_bold, 14)
        self.pdf.setFillColorRGB(*self.COLOR_PRIMARY)
        self.pdf.drawString(self.margin, self.y_position, title)
        
        self.pdf.setFont(self.korean_font, 10)
        self.pdf.setFillColorRGB(*self.COLOR_GREY)
        self.pdf.drawRightString(self.width - self.margin, self.y_position, page_info)
        
        # Line
        self.y_position -= 3*mm
        self.pdf.setStrokeColorRGB(*self.COLOR_PRIMARY)
        self.pdf.setLineWidth(1)
        self.pdf.line(self.margin, self.y_position, self.width - self.margin, self.y_position)
        
        self.y_position -= 8*mm
    
    def _draw_simple_table(self, data, width):
        """Draw simple table"""
        table = Table(data, colWidths=[width*0.4, width*0.6])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*self.COLOR_PRIMARY)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.korean_font_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.Color(*self.COLOR_BG_LIGHT)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        table_width, table_height = table.wrapOn(self.pdf, width, 300*mm)
        table.drawOn(self.pdf, self.margin, self.y_position - table_height)
    
    def _draw_contact_box(self):
        """Draw contact information box"""
        box_height = 20*mm
        self.pdf.setFillColorRGB(*self.COLOR_BG_LIGHT)
        self.pdf.rect(self.margin, self.y_position - box_height, 
                     self.width - 2*self.margin, box_height, fill=True, stroke=False)
        
        self.pdf.setFillColorRGB(*self.COLOR_PRIMARY)
        self.pdf.setFont(self.korean_font_bold, 10)
        self.pdf.drawString(self.margin + 5*mm, self.y_position - 7*mm, "📞 문의 및 상담")
        
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.setFont(self.korean_font, 9)
        self.pdf.drawString(self.margin + 5*mm, self.y_position - 13*mm, 
                          "ZeroSite AI 기반 토지 분석 시스템")
        self.pdf.drawString(self.margin + 5*mm, self.y_position - 18*mm,
                          "Email: support@zerosite.ai | Web: www.zerosite.ai")
    
    def _draw_page_footer(self, page_num):
        """Draw page footer"""
        self.pdf.setFont(self.korean_font, 8)
        self.pdf.setFillColorRGB(*self.COLOR_GREY)
        footer_text = f"ZeroSite v40.4 Landowner Brief | Page {page_num}/3"
        self.pdf.drawCentredString(self.width/2, self.margin, footer_text)
    
    def _get_probability_color(self, probability):
        """Get color based on probability"""
        if probability >= 70:
            return self.COLOR_SUCCESS
        elif probability >= 50:
            return self.COLOR_WARNING
        else:
            return self.COLOR_DANGER
    
    def _get_risk_color(self, risk_level):
        """Get color based on risk level"""
        risk_colors = {
            "LOW": self.COLOR_SUCCESS,
            "MEDIUM": self.COLOR_WARNING,
            "HIGH": self.COLOR_DANGER
        }
        return risk_colors.get(risk_level, self.COLOR_GREY)
    
    def _translate_risk(self, risk_level):
        """Translate risk level to Korean"""
        translations = {
            "LOW": "낮음 (안전)",
            "MEDIUM": "보통 (주의)",
            "HIGH": "높음 (위험)"
        }
        return translations.get(risk_level, risk_level)
