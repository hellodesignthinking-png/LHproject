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
    """ZeroSite Brand Color Palette (v4.1 FINAL - Consulting Grade)"""
    # Primary Colors (프롬프트 기준 정확히 반영)
    primary = colors.HexColor('#0A1F44')  # Primary Navy (프롬프트 스펙)
    primary_light = colors.HexColor('#2F5EFF')  # Sub Blue (프롬프트 스펙)
    primary_dark = colors.HexColor('#071526')
    
    # Accent Colors (핵심 수치/결론)
    accent = colors.HexColor('#2F5EFF')  # Sub Blue
    accent_light = colors.HexColor('#5B8FFF')
    
    # Status Colors (판단 상태 - 프롬프트 기준)
    success = colors.HexColor('#1DB954')  # Success Green (GO)
    warning = colors.HexColor('#F5A623')  # Warning Amber (조건부)
    danger = colors.HexColor('#D64545')  # Risk Red
    positive_green = success  # Alias
    risk_red = danger  # Alias
    
    # Neutral Colors (그레이스케일 - 프롬프트 기준)
    background = colors.HexColor('#F4F6F8')  # Light background
    background_medium = colors.HexColor('#D0D4DA')  # Medium gray
    text_secondary = colors.HexColor('#6B7280')  # Body gray
    
    # Text Colors
    text_primary = colors.HexColor('#0A1F44')  # Primary Navy (제목용)
    text_light = colors.HexColor('#9CA3AF')  # Light gray
    
    border = colors.HexColor('#E2E8F0')  # Light border
    
    # Legacy (for backward compatibility)
    color_primary = primary
    color_secondary_gray = text_secondary
    color_accent = background


@dataclass
class ZeroSiteTypography:
    """ZeroSite Typography System (v4.1 FINAL - Consulting Grade)"""
    # Font Family (프롬프트: Noto Sans KR 시스템, 실제: NanumBarunGothic으로 대체)
    # Note: Noto Sans KR은 ReportLab에서 직접 지원 안 됨, NanumBarunGothic 사용
    font_regular = 'NanumBarunGothic'  # Body text
    font_bold = 'NanumBarunGothicBold'  # Titles, emphasis
    font_light = 'NanumBarunGothicLight'  # Subtle text
    
    # Numeric Font (숫자 가독성 강화 - Inter/Roboto 대체)
    font_numeric = 'Helvetica'  # ReportLab 기본, 숫자 가독성 우수
    
    # Font Sizes (pt) - 프롬프트 기준 조정
    size_h1 = 22  # Main title (유지)
    size_h2 = 16  # Section heading (유지)
    size_h3 = 14  # Sub-section (유지)
    size_body = 10.5  # Body text (유지)
    size_caption = 9  # Footer, notes (유지)
    size_small = 8.5  # Fine print (유지)
    size_score = 28  # Large score display (추가)
    
    # Line Heights (multiplier)
    leading_h1 = 1.3
    leading_h2 = 1.4
    leading_body = 1.6
    leading_caption = 1.5


@dataclass
class ZeroSiteLayout:
    """ZeroSite Page Layout System (v4.1 FINAL - 12-Column Grid)"""
    # Page Margins (프롬프트: LH 내부 보고서 스타일, 좌측 여백 넓게)
    margin_top = 25 * mm
    margin_bottom = 25 * mm
    margin_left = 25 * mm  # 좌측 여백 증가 (22mm → 25mm)
    margin_right = 20 * mm  # 우측 여백 감소 (더 많은 콘텐츠 공간)
    
    # 12-Column Grid System (A4 기준: 210mm - 좌우마진 = 165mm)
    grid_columns = 12
    grid_gutter = 3 * mm  # Column 간 간격
    column_width = (210 * mm - margin_left - margin_right - (grid_gutter * 11)) / 12  # ~11.4mm
    
    # Spacing (프롬프트 기준 조정)
    space_section = 0.4  # inches between sections
    space_paragraph = 0.3  # inches between paragraphs
    space_item = 0.2  # inches between items
    space_tight = 0.1  # inches for tight spacing
    
    # Card/Component Padding
    card_padding = 12  # points (증가: 10 → 12)
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
