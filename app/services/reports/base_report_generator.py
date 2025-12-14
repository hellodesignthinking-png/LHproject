"""
ZeroSite v40.5 - Base Report Generator
공통 PDF 생성 기능 제공

Purpose: DRY 원칙 적용, 코드 재사용
Features:
- 한글 폰트 등록
- 공통 디자인 요소 (헤더, 푸터, 테이블)
- 색상 팔레트
- 페이지 레이아웃

Created: 2025-12-14
"""

from typing import Dict, List, Optional, Tuple
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


class BaseReportGenerator:
    """PDF 보고서 생성을 위한 베이스 클래스"""
    
    # ZeroSite Color Palette
    COLOR_PRIMARY = (0.102, 0.357, 0.714)      # #1A5CB6 Blue
    COLOR_SECONDARY = (0.224, 0.286, 0.671)    # #3949AB Indigo
    COLOR_ACCENT = (0.012, 0.663, 0.957)       # #03A9F4 Sky Blue
    COLOR_SUCCESS = (0.298, 0.686, 0.314)      # #4CAF50 Green
    COLOR_WARNING = (1.0, 0.596, 0.0)          # #FF9800 Orange
    COLOR_DANGER = (0.957, 0.263, 0.212)       # #F44336 Red
    COLOR_GREY = (0.5, 0.5, 0.5)               # Grey
    COLOR_LIGHT_GREY = (0.7, 0.7, 0.7)         # Light Grey
    COLOR_BG_LIGHT = (0.96, 0.96, 0.96)        # Light Background
    COLOR_TABLE_HEADER = (0.910, 0.918, 0.965) # Light Blue Grey
    
    def __init__(self):
        self.width, self.height = A4
        self.margin = 20*mm
        self.y_position = 0
        self.pdf = None
        
        # Register Korean fonts
        self._register_korean_fonts()
        
    def _register_korean_fonts(self):
        """Register Korean fonts"""
        try:
            font_paths = [
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
                '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf',
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
    
    # ============================================
    # Common Drawing Methods
    # ============================================
    
    def draw_cover_page(self, title: str, subtitle: str, context: Dict):
        """Draw professional cover page"""
        self.y_position = self.height - self.margin
        
        # Header Box
        self.pdf.setFillColorRGB(*self.COLOR_PRIMARY)
        self.pdf.rect(0, self.height - 100*mm, self.width, 100*mm, fill=True, stroke=False)
        
        # Title
        self.pdf.setFillColorRGB(1, 1, 1)
        self.pdf.setFont(self.korean_font_bold, 28)
        self.pdf.drawCentredString(self.width/2, self.height - 50*mm, title)
        
        # Subtitle
        self.pdf.setFont(self.korean_font, 16)
        self.pdf.drawCentredString(self.width/2, self.height - 65*mm, subtitle)
        
        # Address
        address = context.get("input", {}).get("address", "주소 정보 없음")
        self.pdf.setFont(self.korean_font, 14)
        self.pdf.drawCentredString(self.width/2, self.height - 80*mm, address)
        
        # Date
        date_str = datetime.now().strftime("%Y년 %m월 %d일")
        self.pdf.setFont(self.korean_font, 12)
        self.pdf.drawCentredString(self.width/2, self.height - 95*mm, date_str)
        
        # Middle section - Key Info
        self.y_position = self.height - 120*mm
        
        # Context ID
        context_id = context.get("context_id", "N/A")
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.setFont(self.korean_font, 10)
        self.pdf.drawString(self.margin, self.y_position, f"Report ID: {context_id[:16]}...")
        
        # Footer - ZeroSite branding
        self.pdf.setFont(self.korean_font, 10)
        self.pdf.setFillColorRGB(*self.COLOR_GREY)
        self.pdf.drawCentredString(self.width/2, 30*mm, "ZeroSite v40.5 | AI 기반 토지 분석 시스템")
        self.pdf.drawCentredString(self.width/2, 25*mm, "LH 공공주택 사전심사 예측 전문")
        
        self.pdf.showPage()
    
    def draw_page_header(self, title: str, page_info: str):
        """Draw page header with title and page number"""
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
    
    def draw_section_header(self, title: str):
        """Draw section header"""
        self.pdf.setFillColorRGB(*self.COLOR_PRIMARY)
        self.pdf.rect(self.margin, self.y_position - 7*mm, 
                     self.width - 2*self.margin, 7*mm, fill=True, stroke=False)
        
        self.pdf.setFillColorRGB(1, 1, 1)
        self.pdf.setFont(self.korean_font_bold, 12)
        self.pdf.drawString(self.margin + 3*mm, self.y_position - 5*mm, title)
        
        self.y_position -= 10*mm
    
    def draw_subsection(self, title: str):
        """Draw subsection title"""
        self.pdf.setFont(self.korean_font_bold, 11)
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.drawString(self.margin, self.y_position, title)
        self.y_position -= 6*mm
    
    def draw_simple_table(self, data: List[List[str]], width: float):
        """Draw simple 2-column table"""
        table = Table(data, colWidths=[width*0.4, width*0.6])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*self.COLOR_TABLE_HEADER)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.Color(*self.COLOR_PRIMARY)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
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
    
    def draw_metric_box(self, x: float, y: float, width: float, 
                       value: str, label: str, color=None):
        """Draw metric box with value and label"""
        height = 18*mm
        
        if color is None:
            color = self.COLOR_PRIMARY
            
        # Box border
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
    
    def draw_page_footer(self, page_num: str, total_pages: str = ""):
        """Draw page footer"""
        self.pdf.setFont(self.korean_font, 8)
        self.pdf.setFillColorRGB(*self.COLOR_GREY)
        
        if total_pages:
            footer_text = f"ZeroSite v40.5 | Page {page_num}/{total_pages}"
        else:
            footer_text = f"ZeroSite v40.5 | Page {page_num}"
            
        self.pdf.drawCentredString(self.width/2, self.margin, footer_text)
    
    def draw_text_block(self, text: str, max_width: float = None):
        """Draw multi-line text block"""
        if max_width is None:
            max_width = self.width - 2*self.margin
        
        self.pdf.setFont(self.korean_font, 9)
        self.pdf.setFillColorRGB(0, 0, 0)
        
        # Simple word wrapping
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.pdf.stringWidth(test_line, self.korean_font, 9) < max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        for line in lines:
            self.pdf.drawString(self.margin + 5*mm, self.y_position, line)
            self.y_position -= 5*mm
    
    def check_page_break(self, required_space: float = 50*mm):
        """Check if page break is needed"""
        if self.y_position < self.margin + required_space:
            self.pdf.showPage()
            self.y_position = self.height - self.margin
            return True
        return False
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def get_probability_color(self, probability: float):
        """Get color based on probability"""
        if probability >= 70:
            return self.COLOR_SUCCESS
        elif probability >= 50:
            return self.COLOR_WARNING
        else:
            return self.COLOR_DANGER
    
    def get_risk_color(self, risk_level: str):
        """Get color based on risk level"""
        risk_colors = {
            "LOW": self.COLOR_SUCCESS,
            "MEDIUM": self.COLOR_WARNING,
            "HIGH": self.COLOR_DANGER
        }
        return risk_colors.get(risk_level, self.COLOR_GREY)
    
    def translate_risk(self, risk_level: str):
        """Translate risk level to Korean"""
        translations = {
            "LOW": "낮음 (안전)",
            "MEDIUM": "보통 (주의)",
            "HIGH": "높음 (위험)"
        }
        return translations.get(risk_level, risk_level)
    
    def format_currency(self, value: float):
        """Format currency with Korean units"""
        if value >= 100000000:  # 억
            return f"{value/100000000:,.1f}억 원"
        elif value >= 10000:  # 만
            return f"{value/10000:,.0f}만 원"
        else:
            return f"{value:,.0f} 원"
