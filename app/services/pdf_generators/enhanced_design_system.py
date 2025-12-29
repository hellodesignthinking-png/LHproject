"""
ZeroSite Enhanced Design System for PDF Reports
================================================

Enhanced visual design system with improved readability,
modern layout, and professional typography.

Version: v5.0 ENHANCED
Date: 2025-12-29
"""

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import Table, TableStyle
from typing import Dict, List, Tuple, Any


class EnhancedDesignSystem:
    """Enhanced design system for ZeroSite PDF reports"""
    
    # ==================== COLOR PALETTE ====================
    # Primary colors
    COLOR_PRIMARY = HexColor('#1E40AF')  # Deep blue (강조)
    COLOR_PRIMARY_LIGHT = HexColor('#3B82F6')  # Light blue
    COLOR_PRIMARY_DARK = HexColor('#1E3A8A')  # Dark blue
    
    # Semantic colors
    COLOR_SUCCESS = HexColor('#10B981')  # Green (성공/긍정)
    COLOR_WARNING = HexColor('#F59E0B')  # Amber (경고/주의)
    COLOR_DANGER = HexColor('#EF4444')  # Red (위험/부정)
    COLOR_INFO = HexColor('#06B6D4')  # Cyan (정보)
    
    # Neutral colors
    COLOR_TEXT_PRIMARY = HexColor('#111827')  # Almost black
    COLOR_TEXT_SECONDARY = HexColor('#6B7280')  # Gray
    COLOR_TEXT_TERTIARY = HexColor('#9CA3AF')  # Light gray
    
    # Background colors
    COLOR_BG_WHITE = colors.white
    COLOR_BG_LIGHT = HexColor('#F9FAFB')  # Very light gray
    COLOR_BG_GRAY = HexColor('#F3F4F6')  # Light gray
    COLOR_BG_PRIMARY = HexColor('#EFF6FF')  # Light blue
    COLOR_BG_SUCCESS = HexColor('#D1FAE5')  # Light green
    COLOR_BG_WARNING = HexColor('#FEF3C7')  # Light yellow
    COLOR_BG_DANGER = HexColor('#FEE2E2')  # Light red
    
    # Border colors
    COLOR_BORDER_LIGHT = HexColor('#E5E7EB')
    COLOR_BORDER_MEDIUM = HexColor('#D1D5DB')
    COLOR_BORDER_DARK = HexColor('#9CA3AF')
    
    # ==================== TYPOGRAPHY ====================
    # Font families (Korean + Latin)
    FONT_FAMILY_SANS = 'NanumGothic'  # Main font
    FONT_FAMILY_SANS_BOLD = 'NanumGothicBold'
    
    # Font sizes (in points)
    FONT_SIZE_H1 = 24  # Main title
    FONT_SIZE_H2 = 18  # Section title
    FONT_SIZE_H3 = 14  # Subsection title
    FONT_SIZE_H4 = 12  # Small heading
    FONT_SIZE_BODY = 10  # Normal text
    FONT_SIZE_SMALL = 9  # Small text
    FONT_SIZE_TINY = 8  # Caption/footnote
    
    # Font sizes for emphasis
    FONT_SIZE_DISPLAY = 32  # Very large numbers/titles
    FONT_SIZE_EMPHASIS = 16  # Emphasized text
    
    # Line heights (leading)
    LEADING_TIGHT = 1.2
    LEADING_NORMAL = 1.5
    LEADING_RELAXED = 1.8
    
    # ==================== SPACING ====================
    SPACE_XXXS = 2 * mm
    SPACE_XXS = 4 * mm
    SPACE_XS = 6 * mm
    SPACE_SM = 8 * mm
    SPACE_MD = 12 * mm
    SPACE_LG = 16 * mm
    SPACE_XL = 24 * mm
    SPACE_XXL = 32 * mm
    
    # ==================== LAYOUT ====================
    PAGE_WIDTH = 210 * mm  # A4
    PAGE_HEIGHT = 297 * mm
    
    MARGIN_TOP = 20 * mm
    MARGIN_BOTTOM = 20 * mm
    MARGIN_LEFT = 20 * mm
    MARGIN_RIGHT = 20 * mm
    
    CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    
    # Grid system (12 columns)
    COLUMN_GAP = 5 * mm
    COLUMN_WIDTH = (CONTENT_WIDTH - 11 * COLUMN_GAP) / 12
    
    # ==================== STYLE HELPERS ====================
    
    @classmethod
    def get_heading_style(cls, level: int = 1, **kwargs) -> ParagraphStyle:
        """Get heading style by level (1-4)"""
        
        if level == 1:
            return ParagraphStyle(
                'Heading1Enhanced',
                fontName=cls.FONT_FAMILY_SANS_BOLD,
                fontSize=cls.FONT_SIZE_H1,
                textColor=cls.COLOR_PRIMARY_DARK,
                spaceAfter=cls.SPACE_LG,
                spaceBefore=cls.SPACE_MD,
                leading=cls.FONT_SIZE_H1 * cls.LEADING_TIGHT,
                alignment=TA_LEFT,
                **kwargs
            )
        elif level == 2:
            return ParagraphStyle(
                'Heading2Enhanced',
                fontName=cls.FONT_FAMILY_SANS_BOLD,
                fontSize=cls.FONT_SIZE_H2,
                textColor=cls.COLOR_PRIMARY,
                spaceAfter=cls.SPACE_MD,
                spaceBefore=cls.SPACE_LG,
                leading=cls.FONT_SIZE_H2 * cls.LEADING_TIGHT,
                alignment=TA_LEFT,
                borderPadding=(cls.SPACE_XS, 0, cls.SPACE_XS, 0),
                leftIndent=cls.SPACE_SM,
                **kwargs
            )
        elif level == 3:
            return ParagraphStyle(
                'Heading3Enhanced',
                fontName=cls.FONT_FAMILY_SANS_BOLD,
                fontSize=cls.FONT_SIZE_H3,
                textColor=cls.COLOR_TEXT_PRIMARY,
                spaceAfter=cls.SPACE_SM,
                spaceBefore=cls.SPACE_MD,
                leading=cls.FONT_SIZE_H3 * cls.LEADING_NORMAL,
                alignment=TA_LEFT,
                **kwargs
            )
        else:  # level 4
            return ParagraphStyle(
                'Heading4Enhanced',
                fontName=cls.FONT_FAMILY_SANS_BOLD,
                fontSize=cls.FONT_SIZE_H4,
                textColor=cls.COLOR_TEXT_SECONDARY,
                spaceAfter=cls.SPACE_XS,
                spaceBefore=cls.SPACE_SM,
                leading=cls.FONT_SIZE_H4 * cls.LEADING_NORMAL,
                alignment=TA_LEFT,
                **kwargs
            )
    
    @classmethod
    def get_body_style(cls, **kwargs) -> ParagraphStyle:
        """Get body text style"""
        return ParagraphStyle(
            'BodyEnhanced',
            fontName=cls.FONT_FAMILY_SANS,
            fontSize=cls.FONT_SIZE_BODY,
            textColor=cls.COLOR_TEXT_PRIMARY,
            leading=cls.FONT_SIZE_BODY * cls.LEADING_NORMAL,
            alignment=TA_LEFT,
            spaceAfter=cls.SPACE_SM,
            **kwargs
        )
    
    @classmethod
    def get_emphasis_style(cls, size: str = 'large', color: str = 'primary', **kwargs) -> ParagraphStyle:
        """Get emphasized text style"""
        
        font_size = {
            'display': cls.FONT_SIZE_DISPLAY,
            'large': cls.FONT_SIZE_EMPHASIS,
            'medium': cls.FONT_SIZE_H3,
            'small': cls.FONT_SIZE_H4
        }.get(size, cls.FONT_SIZE_EMPHASIS)
        
        text_color = {
            'primary': cls.COLOR_PRIMARY,
            'success': cls.COLOR_SUCCESS,
            'warning': cls.COLOR_WARNING,
            'danger': cls.COLOR_DANGER,
            'info': cls.COLOR_INFO
        }.get(color, cls.COLOR_PRIMARY)
        
        return ParagraphStyle(
            f'Emphasis{size.capitalize()}{color.capitalize()}',
            fontName=cls.FONT_FAMILY_SANS_BOLD,
            fontSize=font_size,
            textColor=text_color,
            leading=font_size * cls.LEADING_TIGHT,
            alignment=TA_CENTER,
            spaceAfter=cls.SPACE_MD,
            spaceBefore=cls.SPACE_SM,
            **kwargs
        )
    
    @classmethod
    def get_card_style(cls, card_type: str = 'default') -> Dict[str, Any]:
        """Get card/box styling"""
        
        styles = {
            'default': {
                'background': cls.COLOR_BG_LIGHT,
                'border_color': cls.COLOR_BORDER_LIGHT,
                'border_width': 1,
                'padding': cls.SPACE_MD
            },
            'primary': {
                'background': cls.COLOR_BG_PRIMARY,
                'border_color': cls.COLOR_PRIMARY_LIGHT,
                'border_width': 2,
                'padding': cls.SPACE_MD
            },
            'success': {
                'background': cls.COLOR_BG_SUCCESS,
                'border_color': cls.COLOR_SUCCESS,
                'border_width': 2,
                'padding': cls.SPACE_MD
            },
            'warning': {
                'background': cls.COLOR_BG_WARNING,
                'border_color': cls.COLOR_WARNING,
                'border_width': 2,
                'padding': cls.SPACE_MD
            },
            'danger': {
                'background': cls.COLOR_BG_DANGER,
                'border_color': cls.COLOR_DANGER,
                'border_width': 2,
                'padding': cls.SPACE_MD
            }
        }
        
        return styles.get(card_type, styles['default'])
    
    @classmethod
    def create_enhanced_table_style(cls, header_color: HexColor = None) -> TableStyle:
        """Create enhanced table style with better readability"""
        
        if header_color is None:
            header_color = cls.COLOR_PRIMARY
        
        return TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), header_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), cls.FONT_FAMILY_SANS_BOLD),
            ('FONTSIZE', (0, 0), (-1, 0), cls.FONT_SIZE_H4),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), cls.SPACE_SM),
            ('BOTTOMPADDING', (0, 0), (-1, 0), cls.SPACE_SM),
            
            # Body styling
            ('FONTNAME', (0, 1), (-1, -1), cls.FONT_FAMILY_SANS),
            ('FONTSIZE', (0, 1), (-1, -1), cls.FONT_SIZE_BODY),
            ('TEXTCOLOR', (0, 1), (-1, -1), cls.COLOR_TEXT_PRIMARY),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), cls.SPACE_XS),
            ('BOTTOMPADDING', (0, 1), (-1, -1), cls.SPACE_XS),
            ('LEFTPADDING', (0, 1), (-1, -1), cls.SPACE_SM),
            ('RIGHTPADDING', (0, 1), (-1, -1), cls.SPACE_SM),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, cls.COLOR_BG_LIGHT]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, cls.COLOR_BORDER_LIGHT),
            ('LINEBELOW', (0, 0), (-1, 0), 2, header_color),
        ])
    
    @classmethod
    def create_metric_card(cls, label: str, value: str, unit: str = '', 
                          status: str = 'default') -> str:
        """Create a metric card HTML"""
        
        status_colors = {
            'success': cls.COLOR_SUCCESS,
            'warning': cls.COLOR_WARNING,
            'danger': cls.COLOR_DANGER,
            'default': cls.COLOR_PRIMARY
        }
        
        color = status_colors.get(status, status_colors['default'])
        
        return f"""
        <para alignment="center" spaceAfter="12">
            <font size="10" color="#{cls.COLOR_TEXT_SECONDARY.hexval()[2:]}">{label}</font><br/>
            <font size="24" color="#{color.hexval()[2:]}"><b>{value}</b></font>
            <font size="12" color="#{cls.COLOR_TEXT_SECONDARY.hexval()[2:]}">{unit}</font>
        </para>
        """


class LayoutHelper:
    """Helper class for creating complex layouts"""
    
    @staticmethod
    def create_two_column_layout(left_content: List, right_content: List, 
                                 left_width: float = 0.5) -> Table:
        """Create a two-column layout"""
        
        total_width = EnhancedDesignSystem.CONTENT_WIDTH
        left_col_width = total_width * left_width
        right_col_width = total_width * (1 - left_width) - EnhancedDesignSystem.COLUMN_GAP
        
        data = [[left_content, right_content]]
        
        table = Table(data, colWidths=[left_col_width, right_col_width])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return table
    
    @staticmethod
    def create_metric_grid(metrics: List[Dict[str, str]], columns: int = 3) -> Table:
        """Create a grid of metrics"""
        
        ds = EnhancedDesignSystem
        col_width = (ds.CONTENT_WIDTH - (columns - 1) * ds.COLUMN_GAP) / columns
        
        # Organize metrics into rows
        rows = []
        for i in range(0, len(metrics), columns):
            row = metrics[i:i + columns]
            # Pad with empty cells if needed
            while len(row) < columns:
                row.append({'label': '', 'value': '', 'unit': ''})
            rows.append(row)
        
        # Create table data
        table_data = []
        for row in rows:
            row_cells = []
            for metric in row:
                cell_html = ds.create_metric_card(
                    metric.get('label', ''),
                    metric.get('value', ''),
                    metric.get('unit', ''),
                    metric.get('status', 'default')
                )
                row_cells.append(cell_html)
            table_data.append(row_cells)
        
        table = Table(table_data, colWidths=[col_width] * columns)
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        
        return table
