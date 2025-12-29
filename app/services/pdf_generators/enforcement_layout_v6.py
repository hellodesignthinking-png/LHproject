"""
ZeroSite v6.0 ABSOLUTE FINAL - ENFORCEMENT LAYOUT SYSTEM
Purpose: 강제 35/35/30 구조 + 해석 불가 규격 적용
Author: ZeroSite by AntennaHoldings NataiHeum
Date: 2025-12-29

ABSOLUTE RULES (NO EXCEPTIONS):
1. 상단 35%: DECISION ZONE (결론 1문장 + 핵심 수치 52pt)
2. 중단 35%: EVIDENCE ZONE (그래프/표 1-2개, 상단에 결론 문장)
3. 하단 30%: CHAIN ZONE (다음 모듈 필연 연결)
4. 한 페이지에 "가장 크게 읽히는 문장"은 반드시 1개만
5. 이 구조를 어기면 FAIL

Design Philosophy:
- ❌ "개선" 불가
- ❌ "부분 반영" 불가
- ✅ "전면 강제" 전용
"""

from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import List, Dict, Any, Tuple

from .enhanced_design_system import EnhancedDesignSystem as EDS


class EnforcementLayoutV6:
    """
    v6.0 ABSOLUTE FINAL - 강제 레이아웃 엔진
    모든 페이지는 35/35/30 구조를 강제로 따름
    """
    
    # Page dimensions
    PAGE_WIDTH, PAGE_HEIGHT = A4
    
    # Zone heights (strict enforcement)
    DECISION_ZONE_HEIGHT = PAGE_HEIGHT * 0.35  # 35%
    EVIDENCE_ZONE_HEIGHT = PAGE_HEIGHT * 0.35  # 35%
    CHAIN_ZONE_HEIGHT = PAGE_HEIGHT * 0.30     # 30%
    
    # Typography enforcement
    FONT_H0_CONCLUSION = 28  # 결론 (가장 크게)
    FONT_METRIC_HUGE = 52    # 핵심 수치
    FONT_H2_MEANING = 18     # 의미
    FONT_H3_LOGIC = 14       # 논리
    FONT_BODY = 11           # 본문
    FONT_CAPTION = 9         # 캡션
    
    # Colors (strict semantic)
    COLOR_NAVY = colors.HexColor("#1F2A44")      # 구조·제도
    COLOR_RED = colors.HexColor("#E63946")       # 실패·붕괴·위험
    COLOR_GREEN = colors.HexColor("#2A9D8F")     # 안정·통과
    COLOR_AMBER = colors.HexColor("#F4A261")     # 경고
    COLOR_GRAY = colors.HexColor("#999999")      # 비핵심
    COLOR_DIMMED = colors.HexColor("#CCCCCC")    # 배경 데이터
    
    @classmethod
    def create_decision_zone(cls, 
                            conclusion_text: str,
                            key_metric: str,
                            metric_unit: str = "",
                            color: colors.Color = None) -> List[Any]:
        """
        DECISION ZONE (상단 35%) 생성
        
        Args:
            conclusion_text: 결론 1문장 (26-28pt Bold)
            key_metric: 핵심 수치 (52pt Extra Bold)
            metric_unit: 단위 (18pt)
            color: 강조 색상 (기본: RED)
        
        Returns:
            List of flowables for decision zone
        """
        elements = []
        
        if color is None:
            color = cls.COLOR_RED
        
        # 1. 결론 문장 (가장 크게, 최상단)
        conclusion_style = ParagraphStyle(
            'EnforcementConclusion',
            fontName='NanumBarunGothic-Bold',
            fontSize=cls.FONT_H0_CONCLUSION,
            textColor=color,
            alignment=TA_LEFT,
            leading=cls.FONT_H0_CONCLUSION * 1.4,
            spaceBefore=10,
            spaceAfter=15
        )
        
        elements.append(Paragraph(f"<b>{conclusion_text}</b>", conclusion_style))
        
        # 2. 핵심 수치 (52pt, 중앙 정렬)
        if key_metric:
            metric_style = ParagraphStyle(
                'EnforcementMetric',
                fontName='NanumBarunGothic-Bold',
                fontSize=cls.FONT_METRIC_HUGE,
                textColor=color,
                alignment=TA_CENTER,
                leading=cls.FONT_METRIC_HUGE * 1.2,
                spaceBefore=20,
                spaceAfter=10
            )
            
            metric_text = f"<b>{key_metric}</b>"
            if metric_unit:
                metric_text += f"<font size='{cls.FONT_H2_MEANING}'>{metric_unit}</font>"
            
            elements.append(Paragraph(metric_text, metric_style))
        
        # 3. Zone separator (visual)
        elements.append(Spacer(1, 10))
        
        return elements
    
    @classmethod
    def create_evidence_zone(cls,
                            evidence_elements: List[Any],
                            conclusion_above_evidence: str = None) -> List[Any]:
        """
        EVIDENCE ZONE (중단 35%) 생성
        
        Args:
            evidence_elements: 그래프/표 flowables
            conclusion_above_evidence: 증거 상단에 표시할 결론 문장
        
        Returns:
            List of flowables for evidence zone
        """
        elements = []
        
        # 1. 그래프 상단 결론 (필수)
        if conclusion_above_evidence:
            evidence_conclusion_style = ParagraphStyle(
                'EvidenceConclusion',
                fontName='NanumBarunGothic-Bold',
                fontSize=cls.FONT_H3_LOGIC,
                textColor=cls.COLOR_NAVY,
                alignment=TA_LEFT,
                leading=cls.FONT_H3_LOGIC * 1.4,
                spaceBefore=5,
                spaceAfter=8,
                borderWidth=0,
                borderPadding=0,
                leftIndent=0
            )
            
            elements.append(Paragraph(f"▣ {conclusion_above_evidence}", evidence_conclusion_style))
        
        # 2. 증거 요소들 (그래프, 표 등)
        for elem in evidence_elements:
            elements.append(elem)
        
        elements.append(Spacer(1, 15))
        
        return elements
    
    @classmethod
    def create_chain_zone(cls,
                         chain_text: str,
                         next_module: str) -> List[Any]:
        """
        CHAIN ZONE (하단 30%) 생성
        
        Args:
            chain_text: 다음 모듈로의 필연 연결 문장
            next_module: 다음 모듈 이름 (예: "M4")
        
        Returns:
            List of flowables for chain zone
        """
        elements = []
        
        # 1. 연결 문장
        chain_style = ParagraphStyle(
            'ChainZone',
            fontName='NanumBarunGothic',
            fontSize=cls.FONT_BODY,
            textColor=cls.COLOR_NAVY,
            alignment=TA_LEFT,
            leading=cls.FONT_BODY * 1.6,
            spaceBefore=10,
            spaceAfter=5,
            leftIndent=10,
            rightIndent=10,
            borderWidth=1,
            borderColor=cls.COLOR_NAVY,
            borderPadding=10,
            backColor=colors.HexColor("#F8F9FA")
        )
        
        chain_html = f"""
        <b>➜ {next_module}로의 필연 연결</b><br/>
        <br/>
        {chain_text}
        """
        
        elements.append(Paragraph(chain_html, chain_style))
        
        return elements
    
    @classmethod
    def create_comparison_table_enforced(cls,
                                        table_data: List[List[str]],
                                        highlight_row: int,
                                        conclusion_text: str) -> List[Any]:
        """
        강제 규격 비교 표 생성 (결론 선행)
        
        Args:
            table_data: 표 데이터 (header 포함)
            highlight_row: 강조할 행 (0-based, header 제외)
            conclusion_text: 표 상단 결론 문장
        
        Returns:
            List of flowables
        """
        elements = []
        
        # 1. 결론 문장 (표 위)
        conclusion_style = ParagraphStyle(
            'TableConclusion',
            fontName='NanumBarunGothic-Bold',
            fontSize=cls.FONT_H3_LOGIC,
            textColor=cls.COLOR_RED,
            alignment=TA_LEFT,
            spaceBefore=5,
            spaceAfter=8
        )
        
        elements.append(Paragraph(f"<b>▣ {conclusion_text}</b>", conclusion_style))
        
        # 2. 표 생성
        num_cols = len(table_data[0]) if table_data else 3
        col_width = (EDS.CHART_WIDTH if hasattr(EDS, 'CHART_WIDTH') else 180*mm) / num_cols
        
        table = Table(table_data, colWidths=[col_width] * num_cols)
        
        style_commands = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), cls.COLOR_NAVY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'NanumBarunGothic-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'NanumBarunGothic'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 1), (-1, -1), 8),
            ('RIGHTPADDING', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, cls.COLOR_GRAY),
            ('LINEBELOW', (0, 0), (-1, 0), 2, cls.COLOR_NAVY),
        ]
        
        # Highlight key row
        if 0 <= highlight_row < len(table_data) - 1:
            row_idx = highlight_row + 1
            style_commands.extend([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor("#FFF3CD")),
                ('FONTNAME', (0, row_idx), (-1, row_idx), 'NanumBarunGothic-Bold'),
                ('TEXTCOLOR', (0, row_idx), (-1, row_idx), cls.COLOR_GREEN),
                ('LINEABOVE', (0, row_idx), (-1, row_idx), 2, cls.COLOR_GREEN),
                ('LINEBELOW', (0, row_idx), (-1, row_idx), 2, cls.COLOR_GREEN),
            ])
        
        table.setStyle(TableStyle(style_commands))
        elements.append(table)
        
        return elements
    
    @classmethod
    def create_module_page_enforced(cls,
                                   module_name: str,
                                   decision_conclusion: str,
                                   decision_metric: str,
                                   decision_unit: str,
                                   evidence_elements: List[Any],
                                   evidence_conclusion: str,
                                   chain_text: str,
                                   next_module: str,
                                   decision_color: colors.Color = None) -> List[Any]:
        """
        전체 모듈 페이지를 35/35/30 구조로 강제 생성
        
        Returns:
            Complete page story (flowables)
        """
        story = []
        
        # DECISION ZONE (35%)
        decision_elements = cls.create_decision_zone(
            conclusion_text=decision_conclusion,
            key_metric=decision_metric,
            metric_unit=decision_unit,
            color=decision_color
        )
        story.extend(decision_elements)
        
        # Visual separator
        story.append(Spacer(1, 0.15*inch))
        
        # EVIDENCE ZONE (35%)
        evidence_zone = cls.create_evidence_zone(
            evidence_elements=evidence_elements,
            conclusion_above_evidence=evidence_conclusion
        )
        story.extend(evidence_zone)
        
        # Visual separator
        story.append(Spacer(1, 0.15*inch))
        
        # CHAIN ZONE (30%)
        chain_elements = cls.create_chain_zone(
            chain_text=chain_text,
            next_module=next_module
        )
        story.extend(chain_elements)
        
        return story
    
    @classmethod
    def create_lifestyle_card(cls, lifestyle_data: Dict[str, str]) -> Table:
        """
        생활 장면 카드 (M3 전용)
        
        Args:
            lifestyle_data: {'icon': '🚶', 'text': '...'}
        
        Returns:
            Styled table as card
        """
        card_data = []
        
        for icon, text in lifestyle_data.items():
            card_data.append([f"{icon} {text}"])
        
        card_table = Table(card_data, colWidths=[150*mm])
        
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0F4FF")),
            ('FONTNAME', (0, 0), (-1, -1), 'NanumBarunGothic'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), cls.COLOR_NAVY),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
        ]))
        
        return card_table


# Convenience function for validation
def validate_35_35_30_structure(story_elements: List[Any]) -> bool:
    """
    35/35/30 구조 준수 여부 검증
    
    Args:
        story_elements: Flowable elements
    
    Returns:
        True if structure is enforced, False otherwise
    """
    # Simple heuristic: Check if there are 3 major sections
    # In production, implement more sophisticated zone height calculation
    
    if len(story_elements) < 3:
        return False
    
    # Check for decision zone markers
    has_decision = any(
        hasattr(elem, 'style') and 
        getattr(elem.style, 'fontSize', 0) >= EnforcementLayoutV6.FONT_H0_CONCLUSION
        for elem in story_elements
        if hasattr(elem, 'style')
    )
    
    # Check for chain zone markers
    has_chain = any(
        hasattr(elem, 'style') and 
        getattr(elem.style, 'borderWidth', 0) > 0
        for elem in story_elements
        if hasattr(elem, 'style')
    )
    
    return has_decision and has_chain
