"""
ZeroSite Report Theme - Unified Design System
==============================================

Purpose: Provide consistent typography, colors, and layout
for all M2-M6 PDF reports.

Design Philosophy:
- Public Institution × Professional Consulting
- Clean, modern, data-driven aesthetics
- Emphasis on key decision points (cards, badges, gauges)

Author: ZeroSite AI Development Team
Date: 2025-12-19
"""

from reportlab.lib import colors
from reportlab.lib.units import mm
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ZeroSiteColors:
    """ZeroSite Brand Color Palette (v4.5 FINAL - Consulting-Grade with NO compromise)"""
    # Primary Colors - 요구사항: Primary #1F3A5F
    primary = colors.HexColor('#1F3A5F')  # Primary Navy (consulting standard)
    primary_light = colors.HexColor('#3B82F6')  # Secondary (consulting standard)
    primary_dark = colors.HexColor('#071526')
    
    # Accent Colors (핵심 수치/결론) - 요구사항: Secondary #3B82F6
    accent = colors.HexColor('#3B82F6')  # Secondary Blue
    accent_light = colors.HexColor('#5B8FFF')
    
    # Status Colors (판단 상태) - 요구사항: Positive #16A34A, Warning #F59E0B, Risk #DC2626
    success = colors.HexColor('#16A34A')  # Positive Green
    warning = colors.HexColor('#F59E0B')  # Warning Amber
    danger = colors.HexColor('#DC2626')  # Risk Red
    positive_green = success  # Alias
    risk_red = danger  # Alias
    
    # Neutral Colors (그레이스케일) - 요구사항: 회색 텍스트 #6B7280 이하
    neutral_gray = colors.HexColor('#6B7280')  # Neutral Gray
    background = colors.HexColor('#F8FAFC')  # Light background (consulting standard)
    background_medium = colors.HexColor('#D0D4DA')  # Medium gray
    text_secondary = neutral_gray  # Body gray
    
    # Text Colors
    text_primary = colors.HexColor('#1F3A5F')  # Primary Navy (제목용)
    text_light = colors.HexColor('#9CA3AF')  # Light gray
    
    border = colors.HexColor('#E2E8F0')  # Light border
    
    # Legacy (for backward compatibility)
    color_primary = primary
    color_secondary_gray = text_secondary
    color_accent = background


@dataclass
class ZeroSiteTypography:
    """ZeroSite Typography System (v4.5 FINAL - Consulting-Grade NO COMPROMISE)
    
    요구사항: H1 24pt Bold, H2 17pt SemiBold, H3 14pt SemiBold, Body 11pt Regular, 
    Caption 9pt, Score/Decision Badge 40pt 이상
    """
    # Font Family (consulting-grade, 한글 호환)
    font_regular = 'Helvetica'  # Body 11pt Regular
    font_bold = 'Helvetica-Bold'  # H1 24pt Bold
    font_semibold = 'Helvetica-Bold'  # H2/H3 SemiBold (ReportLab에서는 Bold로 대체)
    font_light = 'Helvetica'  # Subtle text
    
    # Numeric Font (숫자 가독성 최적화)
    font_numeric = 'Helvetica-Bold'  # 숫자 전용 (Bold로 강조)
    
    # Font Sizes (pt) - 요구사항 정확히 반영
    size_h1 = 24  # Main title (요구사항: 24pt Bold)
    size_h2 = 17  # Section heading (요구사항: 17pt SemiBold)
    size_h3 = 14  # Sub-section (요구사항: 14pt SemiBold)
    size_body = 11  # Body text (요구사항: 11pt Regular)
    size_caption = 9  # Footer, notes (요구사항: 9pt)
    size_small = 8.5  # Fine print
    size_score = 40  # Large score display (요구사항: 40pt 이상 - Decision Badge용)
    
    # Line Heights (multiplier) - 컨설팅급 가독성
    leading_h1 = 1.4  # H1 행간
    leading_h2 = 1.5  # H2 행간
    leading_body = 1.7  # Body 행간 (최상급 가독성)
    leading_caption = 1.5


@dataclass
class ZeroSiteLayout:
    """ZeroSite Page Layout System (v4.5 FINAL - Consulting-Grade 12-Column Grid)
    
    요구사항:
    - A4, 12컬럼 그리드
    - 좌측 8컬럼 핵심 내용, 우측 4컬럼 시각요소/요약 박스
    - Executive Insight Zone 상단 고정
    """
    # Page Margins (A4 기준)
    margin_top = 25 * mm  # Executive Insight Zone 포함
    margin_bottom = 25 * mm
    margin_left = 25 * mm
    margin_right = 20 * mm
    
    # 12-Column Grid System (A4 기준: 210mm)
    # 요구사항: 좌측 8컬럼(핵심 내용), 우측 4컬럼(시각요소/요약)
    grid_columns = 12
    grid_gutter = 3 * mm  # Column 간 간격
    
    # Total content width = 210mm - margin_left - margin_right = 165mm
    content_width = 210 * mm - margin_left - margin_right  # ~165mm
    
    # Column width calculation: (content_width - (11 * gutter)) / 12
    column_width = (content_width - (grid_gutter * 11)) / 12  # ~11.4mm per column
    
    # 8-4 Split (요구사항)
    main_content_width = column_width * 8 + grid_gutter * 7  # 좌측 8컬럼
    sidebar_width = column_width * 4 + grid_gutter * 3  # 우측 4컬럼
    
    # Executive Insight Zone (상단 고정)
    executive_zone_height = 40 * mm  # Executive Insight Box 전용 공간
    
    # Spacing (프롬프트 기준 조정)
    space_section = 0.4  # inches between sections
    space_paragraph = 0.3  # inches between paragraphs
    space_item = 0.2  # inches between items
    space_tight = 0.1  # inches for tight spacing
    
    # Card/Component Padding
    card_padding = 15  # points (Executive Insight Box용 증가)
    card_radius = 5  # points (for visual reference)
    
    # Page Header Height
    header_height = 15 * mm  # Report Title + Module Code + Context ID


class ZeroSiteTheme:
    """
    Complete ZeroSite theme for PDF generation
    
    Usage:
        theme = ZeroSiteTheme()
        title_style = theme.get_title_style()
        primary_color = theme.colors.primary
    """
    
    def __init__(self):
        self.colors = ZeroSiteColors()
        self.typography = ZeroSiteTypography()
        self.layout = ZeroSiteLayout()
    
    def get_title_style(self, styles_base):
        """Get H1 title style"""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        
        return ParagraphStyle(
            'ZeroSiteTitle',
            parent=styles_base['Heading1'],
            fontName=self.typography.font_bold,
            fontSize=self.typography.size_h1,
            leading=self.typography.size_h1 * self.typography.leading_h1,
            textColor=self.colors.primary,
            alignment=TA_CENTER,
            spaceAfter=20,
        )
    
    def get_heading_style(self, styles_base):
        """Get H2 section heading style"""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT
        
        return ParagraphStyle(
            'ZeroSiteHeading',
            parent=styles_base['Heading2'],
            fontName=self.typography.font_bold,
            fontSize=self.typography.size_h2,
            leading=self.typography.size_h2 * self.typography.leading_h2,
            textColor=self.colors.primary,
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=15,
        )
    
    def get_body_style(self, styles_base):
        """Get body text style"""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT
        
        return ParagraphStyle(
            'ZeroSiteBody',
            parent=styles_base['Normal'],
            fontName=self.typography.font_regular,
            fontSize=self.typography.size_body,
            leading=self.typography.size_body * self.typography.leading_body,
            textColor=self.colors.text_primary,
            alignment=TA_LEFT,
        )
    
    def get_caption_style(self, styles_base):
        """Get caption/footer style"""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        
        return ParagraphStyle(
            'ZeroSiteCaption',
            parent=styles_base['Normal'],
            fontName=self.typography.font_light,
            fontSize=self.typography.size_caption,
            leading=self.typography.size_caption * self.typography.leading_caption,
            textColor=self.colors.text_secondary,
            alignment=TA_CENTER,
        )
    
    def get_table_style(self, header_color=None):
        """
        Get standard table style
        
        Args:
            header_color: Optional color for header row (defaults to primary)
        """
        from reportlab.platypus import TableStyle
        
        if header_color is None:
            header_color = self.colors.primary
        
        return TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), header_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), self.typography.font_bold),
            ('FONTSIZE', (0, 0), (-1, 0), self.typography.size_body),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Body rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.colors.text_primary),
            ('FONTNAME', (0, 1), (-1, -1), self.typography.font_regular),
            ('FONTSIZE', (0, 1), (-1, -1), self.typography.size_body),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors.border),
            
            # Alternating rows
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors.background]),
        ])
    
    def create_kpi_card_html(self, title: str, value: str, subtitle: str = "", color: str = "primary") -> str:
        """
        Create HTML for KPI card (for use in Paragraph)
        
        Args:
            title: Card title (e.g., "M5 사업성 점수")
            value: Main value (e.g., "85점")
            subtitle: Optional subtitle (e.g., "/ 100점")
            color: Color scheme ("primary", "success", "warning", "danger")
        
        Returns:
            HTML string for ReportLab Paragraph
        """
        color_map = {
            "primary": str(self.colors.primary)[1:],  # Remove # from HexColor
            "success": str(self.colors.success)[1:],
            "warning": str(self.colors.warning)[1:],
            "danger": str(self.colors.danger)[1:],
        }
        
        hex_color = color_map.get(color, color_map["primary"])
        
        return f"""
<para alignment="center" spaceAfter="10">
    <font name="{self.typography.font_regular}" size="{self.typography.size_caption}" color="{self.colors.text_secondary}">
        {title}
    </font><br/>
    <font name="{self.typography.font_bold}" size="{self.typography.size_h1}" color="#{hex_color}">
        {value}
    </font>
    <font name="{self.typography.font_regular}" size="{self.typography.size_body}" color="{self.colors.text_light}">
        {subtitle}
    </font>
</para>
"""
    
    def create_badge_html(self, text: str, badge_type: str = "success") -> str:
        """
        Create HTML for status badge
        
        Args:
            text: Badge text (e.g., "GO", "CONDITIONAL", "HIGH RISK")
            badge_type: Badge type ("success", "warning", "danger", "info")
        
        Returns:
            HTML string for inline badge
        """
        badge_colors = {
            "success": (self.colors.success, colors.white),
            "warning": (self.colors.warning, colors.white),
            "danger": (self.colors.danger, colors.white),
            "info": (self.colors.primary, colors.white),
        }
        
        bg_color, text_color = badge_colors.get(badge_type, badge_colors["info"])
        
        return f"""<font name="{self.typography.font_bold}" size="{self.typography.size_body}" \
color="{text_color}" backColor="{bg_color}"> {text} </font>"""


# Singleton instance for easy import
theme = ZeroSiteTheme()


# Export all public classes and instances
__all__ = [
    'ZeroSiteColors',
    'ZeroSiteTypography',
    'ZeroSiteLayout',
    'ZeroSiteTheme',
    'theme',  # Singleton instance
]
