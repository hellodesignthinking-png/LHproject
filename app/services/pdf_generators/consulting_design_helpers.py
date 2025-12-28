"""
ZeroSite Consulting-Grade Design Helpers
=========================================

컨설팅급 보고서 디자인을 위한 시각적 요소 헬퍼 함수

목표: "한 페이지를 넘기자마자 '아, 이건 컨설팅 보고서다'라고 느끼게 만드는 구조"

Design Elements:
- Executive Insight Box: 핵심 메시지 시각적 강조
- Flow Diagram: 프로세스 흐름 시각화
- Comparison Cards: 비교 구조 시각화
- Decision Badge: 최종 판단 배지

Author: ZeroSite AI Development Team
Date: 2025-12-28
"""

from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import Table, Paragraph, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import List, Dict, Any
import logging

from .report_theme import ZeroSiteTheme

logger = logging.getLogger(__name__)


class ConsultingDesignHelpers:
    """컨설팅급 디자인 요소 생성기"""
    
    def __init__(self, theme: ZeroSiteTheme = None):
        """초기화
        
        Args:
            theme: ZeroSiteTheme 인스턴스 (선택)
        """
        self.theme = theme or ZeroSiteTheme()
    
    def create_executive_insight_box(self, insight_text: str, title: str = "Executive Insight") -> Table:
        """
        Executive Insight Box (컨설팅급 핵심 메시지 박스)
        
        목표: 한 페이지를 넘기자마자 핵심 판단이 보이는 구조
        
        Args:
            insight_text: 핵심 판단 문장 (2-3줄 권장)
            title: 박스 제목 (기본: Executive Insight)
        
        Returns:
            ReportLab Table object
        """
        # 제목 스타일
        title_style = ParagraphStyle(
            'InsightTitle',
            fontName=self.theme.typography.font_bold,
            fontSize=13,
            textColor=self.theme.colors.primary,
            alignment=TA_LEFT,
            leftIndent=15,
            spaceAfter=8,
        )
        
        # 본문 스타일
        insight_style = ParagraphStyle(
            'ExecutiveInsight',
            fontName=self.theme.typography.font_regular,
            fontSize=11.5,
            leading=18,
            textColor=self.theme.colors.text_primary,
            alignment=TA_LEFT,
            leftIndent=15,
            rightIndent=15,
        )
        
        # 텍스트 구성
        title_para = Paragraph(f"💡 {title}", title_style)
        insight_para = Paragraph(insight_text, insight_style)
        
        # 박스 테이블
        box_table = Table([[title_para], [insight_para]], colWidths=[16*cm])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.theme.colors.background),
            ('BOX', (0, 0), (-1, -1), 2, self.theme.colors.accent),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return box_table
    
    def create_flow_diagram(self, steps: List[str], title: str = "Process Flow") -> Table:
        """
        Flow Diagram (프로세스 흐름도)
        
        목표: 단순 텍스트 나열 → Flow Diagram 형태로 시각화
        
        Args:
            steps: 단계 리스트 ["입지 희소성", "거래 구조", "정책 활용 가치", "현재 토지가치 범위"]
            title: 다이어그램 제목
        
        Returns:
            ReportLab Table object
        """
        step_style = ParagraphStyle(
            'FlowStep',
            fontName=self.theme.typography.font_regular,
            fontSize=10,
            leading=14,
            textColor=colors.white,
            alignment=TA_CENTER,
        )
        
        arrow_style = ParagraphStyle(
            'FlowArrow',
            fontName=self.theme.typography.font_bold,
            fontSize=16,
            textColor=self.theme.colors.accent,
            alignment=TA_CENTER,
        )
        
        # 단계 박스 생성
        flow_data = []
        for i, step in enumerate(steps):
            step_para = Paragraph(step, step_style)
            flow_data.append([step_para])
            
            # 마지막 단계가 아니면 화살표 추가
            if i < len(steps) - 1:
                arrow_para = Paragraph("↓", arrow_style)
                flow_data.append([arrow_para])
        
        # 테이블 생성
        flow_table = Table(flow_data, colWidths=[12*cm])
        
        # 스타일 적용
        table_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        # 단계 박스에만 배경색 적용
        for i in range(0, len(flow_data), 2):  # 0, 2, 4, ... (단계 인덱스)
            table_style.add('BACKGROUND', (0, i), (-1, i), self.theme.colors.primary)
            table_style.add('TOPPADDING', (0, i), (-1, i), 10)
            table_style.add('BOTTOMPADDING', (0, i), (-1, i), 10)
        
        flow_table.setStyle(table_style)
        
        return flow_table
    
    def create_comparison_cards(self, left_title: str, left_items: List[str],
                               right_title: str, right_items: List[str]) -> Table:
        """
        Comparison Cards (비교 카드)
        
        목표: 일반 분양 vs LH 일괄 매입 등 비교 구조 시각화
        
        Args:
            left_title: 왼쪽 카드 제목 (예: "일반 분양")
            left_items: 왼쪽 항목 ["분양 리스크 ⛔", ...]
            right_title: 오른쪽 카드 제목 (예: "LH 일괄 매입")
            right_items: 오른쪽 항목 ["수익 확정 ✅", ...]
        
        Returns:
            ReportLab Table object
        """
        title_style = ParagraphStyle(
            'ComparisonTitle',
            fontName=self.theme.typography.font_bold,
            fontSize=12,
            textColor=self.theme.colors.primary,
            alignment=TA_LEFT,
            spaceAfter=6,
        )
        
        item_style = ParagraphStyle(
            'ComparisonItem',
            fontName=self.theme.typography.font_regular,
            fontSize=10,
            leading=16,
            textColor=self.theme.colors.text_primary,
            alignment=TA_LEFT,
        )
        
        # 왼쪽 카드
        left_content = []
        left_content.append(Paragraph(left_title, title_style))
        for item in left_items:
            left_content.append(Paragraph(f"• {item}", item_style))
        
        # 오른쪽 카드
        right_content = []
        right_content.append(Paragraph(right_title, title_style))
        for item in right_items:
            right_content.append(Paragraph(f"• {item}", item_style))
        
        # 테이블 구성
        comparison_table = Table([[left_content, right_content]], colWidths=[8*cm, 8*cm])
        
        comparison_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#FEF2F2')),  # 왼쪽 배경 (연한 빨간)
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#F0FDF4')),  # 오른쪽 배경 (연한 녹색)
            ('BOX', (0, 0), (-1, -1), 1.5, self.theme.colors.border),
            ('INNERGRID', (0, 0), (-1, -1), 1, self.theme.colors.border),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        return comparison_table
    
    def create_final_decision_badge(self, decision: str, score: float, subtitle: str = "") -> Table:
        """
        Final Decision Badge (M6 최종 판단 배지)
        
        목표: GO / CONDITIONAL / NO-GO 컬러 + 아이콘 + 한 문장
        
        Args:
            decision: 판단 (GO, CONDITIONAL, NOGO)
            score: LH 점수 (0-100)
            subtitle: 부가 설명 (선택)
        
        Returns:
            ReportLab Table object
        """
        # 판단별 컬러 및 아이콘
        decision_map = {
            'GO': {
                'color': self.theme.colors.positive_green,
                'icon': '✅',
                'text': '진행 가능',
                'bg': colors.HexColor('#F0FDF4')
            },
            'CONDITIONAL': {
                'color': self.theme.colors.warning,
                'icon': '⚠️',
                'text': '조건부 가능',
                'bg': colors.HexColor('#FFFBEB')
            },
            'NOGO': {
                'color': self.theme.colors.risk_red,
                'icon': '❌',
                'text': '검토 필요',
                'bg': colors.HexColor('#FEF2F2')
            }
        }
        
        decision_info = decision_map.get(decision, decision_map['CONDITIONAL'])
        
        # 스타일
        icon_style = ParagraphStyle(
            'DecisionIcon',
            fontName=self.theme.typography.font_regular,
            fontSize=48,
            alignment=TA_CENTER,
        )
        
        title_style = ParagraphStyle(
            'DecisionTitle',
            fontName=self.theme.typography.font_bold,
            fontSize=18,
            textColor=decision_info['color'],
            alignment=TA_CENTER,
            spaceAfter=4,
        )
        
        score_style = ParagraphStyle(
            'DecisionScore',
            fontName=self.theme.typography.font_bold,
            fontSize=24,
            textColor=self.theme.colors.primary,
            alignment=TA_CENTER,
            spaceAfter=4,
        )
        
        subtitle_style = ParagraphStyle(
            'DecisionSubtitle',
            fontName=self.theme.typography.font_regular,
            fontSize=11,
            textColor=self.theme.colors.text_secondary,
            alignment=TA_CENTER,
        )
        
        # 배지 컨텐츠
        icon_para = Paragraph(decision_info['icon'], icon_style)
        title_para = Paragraph(decision_info['text'], title_style)
        score_para = Paragraph(f"{score:.1f}/100", score_style)
        subtitle_para = Paragraph(subtitle, subtitle_style) if subtitle else Paragraph("", subtitle_style)
        
        # 배지 테이블
        badge_table = Table([[icon_para], [title_para], [score_para], [subtitle_para]], colWidths=[14*cm])
        
        badge_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), decision_info['bg']),
            ('BOX', (0, 0), (-1, -1), 3, decision_info['color']),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        return badge_table


# Singleton instance for easy import
consulting_helpers = ConsultingDesignHelpers()


# Export all
__all__ = [
    'ConsultingDesignHelpers',
    'consulting_helpers',
]
