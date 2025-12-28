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
    
    def create_4step_diagram(self, steps: List[Dict[str, str]], title: str = "4-Step Process") -> Table:
        """
        4-Step Diagram (프로세스 단계 시각화)
        
        M4 건축규모 축소 논리 등에 사용
        
        Args:
            steps: 각 단계 정보 [{"number": "1", "title": "...", "desc": "..."}, ...]
            title: 다이어그램 제목
        
        Returns:
            Table: 4단계 다이어그램 테이블
        """
        from reportlab.platypus import Spacer
        
        # 스타일 정의
        step_title_style = ParagraphStyle(
            'StepTitle',
            fontName=self.theme.typography.font_bold,
            fontSize=11,
            textColor=self.theme.colors.primary,
            alignment=TA_CENTER,
            spaceAfter=3,
        )
        
        step_desc_style = ParagraphStyle(
            'StepDesc',
            fontName=self.theme.typography.font_regular,
            fontSize=9,
            textColor=self.theme.colors.text_body,
            alignment=TA_CENTER,
            leading=12,
        )
        
        step_number_style = ParagraphStyle(
            'StepNumber',
            fontName=self.theme.typography.font_bold,
            fontSize=16,
            textColor=colors.white,
            alignment=TA_CENTER,
        )
        
        # 각 단계 셀 생성
        step_cells = []
        for step in steps:
            number = step.get('number', '?')
            step_title = step.get('title', '')
            desc = step.get('desc', '')
            
            # 숫자 배지
            number_para = Paragraph(f"<b>{number}</b>", step_number_style)
            number_cell = Table([[number_para]], colWidths=[1*cm])
            number_cell.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), self.theme.colors.accent),
                ('ROUNDEDCORNERS', [0.3*cm, 0.3*cm, 0.3*cm, 0.3*cm]),
            ]))
            
            title_para = Paragraph(step_title, step_title_style)
            desc_para = Paragraph(desc, step_desc_style)
            
            # 단계 컨테이너
            step_container = Table(
                [[number_cell], [title_para], [desc_para]],
                colWidths=[3.5*cm]
            )
            step_container.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            step_cells.append(step_container)
        
        # 4개 단계를 가로로 배치
        main_table = Table([step_cells], colWidths=[3.5*cm] * len(steps))
        main_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 1, self.theme.colors.border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, self.theme.colors.border),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        return main_table
    
    def create_radar_chart_placeholder(self, categories: List[str], values: List[float], title: str = "Stability Analysis") -> Table:
        """
        레이더 차트 플레이스홀더 (간단한 테이블 형식)
        
        실제 matplotlib 레이더 차트는 복잡하므로, 간단한 바 형식으로 대체
        
        Args:
            categories: 평가 항목 리스트
            values: 각 항목의 값 (0-100)
            title: 차트 제목
        
        Returns:
            Table: 레이더 차트 대체 테이블
        """
        # 간단한 바 차트 스타일 테이블
        data = [['항목', '점수', '평가']]
        
        for cat, val in zip(categories, values):
            # 점수에 따른 평가
            if val >= 80:
                evaluation = "우수"
                color_bg = colors.HexColor('#D4EDDA')
            elif val >= 60:
                evaluation = "양호"
                color_bg = colors.HexColor('#FFF3CD')
            else:
                evaluation = "개선필요"
                color_bg = colors.HexColor('#F8D7DA')
            
            data.append([cat, f"{val:.0f}점", evaluation])
        
        table = Table(data, colWidths=[6*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), self.theme.colors.primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), self.theme.typography.font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.theme.colors.border),
        ]))
        
        return table
    
    def create_module_linkage_diagram(self, modules: List[Dict[str, str]], final_decision: str) -> Table:
        """
        모듈 연계 다이어그램 (M6용)
        
        M1-M5가 M6로 수렴하는 구조 시각화
        
        Args:
            modules: 모듈 정보 [{"name": "M2", "label": "토지가치", "status": "✅"}, ...]
            final_decision: 최종 결정 텍스트
        
        Returns:
            Table: 모듈 연계 다이어그램
        """
        module_style = ParagraphStyle(
            'ModuleLabel',
            fontName=self.theme.typography.font_regular,
            fontSize=9,
            textColor=self.theme.colors.text_body,
            alignment=TA_CENTER,
        )
        
        decision_style = ParagraphStyle(
            'FinalDecision',
            fontName=self.theme.typography.font_bold,
            fontSize=12,
            textColor=self.theme.colors.primary,
            alignment=TA_CENTER,
        )
        
        # 모듈 셀들
        module_cells = []
        for mod in modules:
            name = mod.get('name', '')
            label = mod.get('label', '')
            status = mod.get('status', '')
            
            cell_text = f"{status}<br/><b>{name}</b><br/>{label}"
            para = Paragraph(cell_text, module_style)
            
            module_cells.append([para])
        
        # 모듈 테이블
        module_table = Table(module_cells, colWidths=[2.5*cm], rowHeights=[1.5*cm] * len(modules))
        module_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FF')),
            ('BOX', (0, 0), (-1, -1), 1, self.theme.colors.accent),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, self.theme.colors.border),
        ]))
        
        # 화살표
        arrow_para = Paragraph("→", decision_style)
        
        # 최종 결정 박스
        decision_para = Paragraph(f"<b>M6 최종 판단</b><br/>{final_decision}", decision_style)
        decision_box = Table([[decision_para]], colWidths=[5*cm], rowHeights=[3*cm])
        decision_box.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#DBEAFE')),
            ('BOX', (0, 0), (-1, -1), 2, self.theme.colors.primary),
        ]))
        
        # 전체 레이아웃
        layout_table = Table([[module_table, arrow_para, decision_box]], colWidths=[3*cm, 2*cm, 5.5*cm])
        layout_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return layout_table
    
    def create_3stage_arrow_flow_v42(self, stages: List[Dict[str, str]], title: str = "가치 형성 구조") -> Table:
        """
        3단 화살표 Flow Diagram (v4.2 강화판)
        
        프롬프트: [희소성] → [실수요 거래 구조] → [LH 정책 활용 가치]
        각 단계에 아이콘 사용 (Map / People / Policy)
        
        Args:
            stages: [{"icon": "🗺️", "title": "도심 필지 희소성", "desc": "개발가능 15-20%"}, ...]
            title: 다이어그램 제목
        
        Returns:
            Table: 3단 화살표 Flow
        """
        from reportlab.platypus import Spacer
        
        # 스타일 정의
        icon_style = ParagraphStyle(
            'IconStyle',
            fontName=self.theme.typography.font_regular,
            fontSize=32,  # 아이콘 크기 증가
            textColor=self.theme.colors.primary,
            alignment=TA_CENTER,
        )
        
        title_style = ParagraphStyle(
            'StageTitle',
            fontName=self.theme.typography.font_bold,
            fontSize=13,  # 제목 크기 증가
            textColor=colors.white,
            alignment=TA_CENTER,
            leading=16,
        )
        
        desc_style = ParagraphStyle(
            'StageDesc',
            fontName=self.theme.typography.font_regular,
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER,
            leading=13,
        )
        
        arrow_style = ParagraphStyle(
            'ArrowStyle',
            fontName=self.theme.typography.font_bold,
            fontSize=28,  # 화살표 크기 증가
            textColor=self.theme.colors.accent,
            alignment=TA_CENTER,
        )
        
        # 단계 셀들 생성
        stage_cells = []
        for i, stage in enumerate(stages):
            icon = stage.get('icon', '●')
            stage_title = stage.get('title', '')
            desc = stage.get('desc', '')
            
            # 아이콘
            icon_para = Paragraph(icon, icon_style)
            # 제목
            title_para = Paragraph(f"<b>{stage_title}</b>", title_style)
            # 설명
            desc_para = Paragraph(desc, desc_style)
            
            # 단계 박스
            stage_box = Table(
                [[icon_para], [title_para], [desc_para]],
                colWidths=[4.2*cm],
                rowHeights=[1.2*cm, 0.8*cm, 0.7*cm]
            )
            stage_box.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), self.theme.colors.primary),
                ('ROUNDEDCORNERS', [8, 8, 8, 8]),  # 둥근 모서리
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            stage_cells.append(stage_box)
            
            # 마지막 단계가 아니면 화살표 추가
            if i < len(stages) - 1:
                arrow_para = Paragraph("→", arrow_style)
                stage_cells.append(arrow_para)
        
        # 가로 배치
        flow_table = Table([stage_cells], colWidths=[4.2*cm, 0.8*cm] * (len(stages) - 1) + [4.2*cm])
        flow_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return flow_table
    
    def create_stacked_premium_bar_v42(self, premiums: Dict[str, float], unit: str = "억원") -> Table:
        """
        프리미엄 분해 Stacked Bar (v4.2 신규)
        
        프롬프트: 입지 / 희소성 / 정책 프리미엄을 색상 분리
        
        Args:
            premiums: {"입지": 5.0, "희소성": 3.0, "정책": 2.0} (억원 단위)
            unit: 단위 표시
        
        Returns:
            Table: Stacked Bar 차트
        """
        # 총합 계산
        total = sum(premiums.values())
        
        # 색상 매핑
        color_map = {
            "입지": self.theme.colors.accent,  # Blue
            "희소성": self.theme.colors.warning,  # Amber
            "정책": self.theme.colors.success,  # Green
        }
        
        # Bar 셀 생성
        bar_cells = []
        label_cells = []
        
        for key, value in premiums.items():
            pct = (value / total * 100) if total > 0 else 0
            width = pct / 100 * 12  # 12cm 기준
            
            # Bar 조각
            bar_cell = Table([['']], colWidths=[width*cm], rowHeights=[1*cm])
            bar_cell.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), color_map.get(key, self.theme.colors.background_medium)),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            bar_cells.append(bar_cell)
            
            # 레이블
            label_style = ParagraphStyle(
                'LabelStyle',
                fontName=self.theme.typography.font_regular,
                fontSize=9,
                textColor=self.theme.colors.text_secondary,
                alignment=TA_CENTER,
            )
            label_para = Paragraph(f"{key}<br/>{value:.1f}{unit}", label_style)
            label_cells.append([label_para])
        
        # Bar 배치
        bar_row = Table([bar_cells], colWidths=[None] * len(bar_cells))
        bar_row.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # 레이블 배치
        label_table = Table(label_cells, colWidths=[4*cm] * len(label_cells))
        label_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        # 전체 조합
        full_table = Table([[bar_row], [label_table]], colWidths=[14*cm])
        
        return full_table
    
    def create_lifestyle_cards_v42(self, cards: List[Dict[str, str]]) -> Table:
        """
        Lifestyle Cards (v4.2 비주얼 강화)
        
        프롬프트: 아이콘 크기 증가, 카드 배경색 차별화
        
        Args:
            cards: [{"icon": "🏃", "title": "이동 중심", "desc": "대중교통 선호"}, ...]
        
        Returns:
            Table: Lifestyle Cards (강화판)
        """
        icon_style = ParagraphStyle(
            'IconBig',
            fontName=self.theme.typography.font_regular,
            fontSize=42,  # 아이콘 크기 대폭 증가 (32 → 42)
            textColor=self.theme.colors.accent,
            alignment=TA_CENTER,
        )
        
        title_style = ParagraphStyle(
            'CardTitle',
            fontName=self.theme.typography.font_bold,
            fontSize=11,  # 제목 크기 증가
            textColor=self.theme.colors.primary,
            alignment=TA_CENTER,
            leading=14,
        )
        
        desc_style = ParagraphStyle(
            'CardDesc',
            fontName=self.theme.typography.font_regular,
            fontSize=9,
            textColor=self.theme.colors.text_secondary,
            alignment=TA_CENTER,
            leading=12,
        )
        
        # 카드 셀 생성
        card_cells = []
        
        # 배경색 순환 (Blue 계열 그라데이션)
        bg_colors = [
            colors.HexColor('#EFF6FF'),  # 아주 연한 파랑
            colors.HexColor('#DBEAFE'),  # 연한 파랑
            colors.HexColor('#BFDBFE'),  # 파랑
            colors.HexColor('#93C5FD'),  # 진한 파랑
        ]
        
        for i, card in enumerate(cards):
            icon = card.get('icon', '●')
            card_title = card.get('title', '')
            desc = card.get('desc', '')
            
            icon_para = Paragraph(icon, icon_style)
            title_para = Paragraph(f"<b>{card_title}</b>", title_style)
            desc_para = Paragraph(desc, desc_style)
            
            # 카드 박스
            card_box = Table(
                [[icon_para], [title_para], [desc_para]],
                colWidths=[3.2*cm],
                rowHeights=[1.5*cm, 0.7*cm, 0.8*cm]
            )
            
            bg_color = bg_colors[i % len(bg_colors)]
            
            card_box.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), bg_color),  # 차별화된 배경색
                ('BOX', (0, 0), (-1, -1), 2, self.theme.colors.accent),
                ('ROUNDEDCORNERS', [6, 6, 6, 6]),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            card_cells.append([card_box])
        
        # 4개 가로 배치
        cards_table = Table([card_cells], colWidths=[3.5*cm] * len(cards))
        cards_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return cards_table
    
    def create_housing_type_matrix_v42(self, types: List[Dict[str, Any]]) -> Table:
        """
        유형 비교 Matrix (v4.2 신규)
        
        프롬프트: X축: 거주 기간, Y축: LH 운영 안정성
        청년형 Blue, 기타 Gray 처리
        
        Args:
            types: [{"name": "청년형", "duration": 2, "stability": 85, "highlight": True}, ...]
        
        Returns:
            Table: Matrix 차트
        """
        # 간단한 테이블 매트릭스 (실제 차트는 matplotlib 필요)
        header_style = ParagraphStyle(
            'MatrixHeader',
            fontName=self.theme.typography.font_bold,
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER,
        )
        
        cell_style = ParagraphStyle(
            'MatrixCell',
            fontName=self.theme.typography.font_regular,
            fontSize=9,
            textColor=self.theme.colors.text_primary,
            alignment=TA_CENTER,
        )
        
        # 데이터 준비
        matrix_data = [
            ['유형', '거주기간(년)', 'LH 운영안정성(%)', '권장도']
        ]
        
        for type_info in types:
            name = type_info.get('name', '')
            duration = type_info.get('duration', 0)
            stability = type_info.get('stability', 0)
            highlight = type_info.get('highlight', False)
            
            recommend = "✅ 권장" if highlight else "ℹ️ 가능"
            
            matrix_data.append([
                name,
                f"{duration}년",
                f"{stability}%",
                recommend
            ])
        
        matrix_table = Table(matrix_data, colWidths=[3*cm, 3*cm, 3.5*cm, 3*cm])
        
        # 스타일 적용
        matrix_table.setStyle(TableStyle([
            # 헤더
            ('BACKGROUND', (0, 0), (-1, 0), self.theme.colors.primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), self.theme.typography.font_bold),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # 전체 테두리
            ('GRID', (0, 0), (-1, -1), 1, self.theme.colors.border),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        # 청년형 행 강조 (Blue 배경)
        for i, type_info in enumerate(types):
            if type_info.get('highlight', False):
                matrix_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i+1), (-1, i+1), colors.HexColor('#DBEAFE')),
                    ('TEXTCOLOR', (0, i+1), (-1, i+1), self.theme.colors.primary),
                    ('FONTNAME', (0, i+1), (-1, i+1), self.theme.typography.font_bold),
                ]))
        
        return matrix_table
    
    def create_final_decision_badge_v42(self, decision: str, score: float, subtitle: str = "") -> Table:
        """
        Final Decision Badge (v4.2 대형화)
        
        프롬프트: 현재보다 2배 크기, 색상 강화
        
        Args:
            decision: "go" | "conditional" | "no-go"
            score: 점수 (0-110)
            subtitle: 부제목
        
        Returns:
            Table: 대형 Decision Badge
        """
        # Decision 매핑
        decision_info = {
            "go": {"text": "GO", "icon": "✅", "color": self.theme.colors.success, "bg": colors.HexColor('#D4EDDA')},
            "conditional": {"text": "CONDITIONAL", "icon": "⚠️", "color": self.theme.colors.warning, "bg": colors.HexColor('#FFF3CD')},
            "no-go": {"text": "NO-GO", "icon": "❌", "color": self.theme.colors.danger, "bg": colors.HexColor('#F8D7DA')},
        }
        
        info = decision_info.get(decision.lower(), decision_info["conditional"])
        
        # 스타일 (크기 2배)
        icon_style = ParagraphStyle(
            'BadgeIcon',
            fontName=self.theme.typography.font_regular,
            fontSize=80,  # 40 → 80
            textColor=info['color'],
            alignment=TA_CENTER,
        )
        
        title_style = ParagraphStyle(
            'BadgeTitle',
            fontName=self.theme.typography.font_bold,
            fontSize=32,  # 18 → 32
            textColor=info['color'],
            alignment=TA_CENTER,
            spaceAfter=4,
        )
        
        score_style = ParagraphStyle(
            'BadgeScore',
            fontName=self.theme.typography.font_bold,
            fontSize=48,  # 24 → 48
            textColor=self.theme.colors.primary,
            alignment=TA_CENTER,
            spaceAfter=4,
        )
        
        subtitle_style = ParagraphStyle(
            'BadgeSubtitle',
            fontName=self.theme.typography.font_regular,
            fontSize=14,  # 11 → 14
            textColor=self.theme.colors.text_secondary,
            alignment=TA_CENTER,
        )
        
        # 배지 컨텐츠
        icon_para = Paragraph(info['icon'], icon_style)
        title_para = Paragraph(info['text'], title_style)
        score_para = Paragraph(f"{score:.1f}/110", score_style)
        subtitle_para = Paragraph(subtitle, subtitle_style) if subtitle else Paragraph("", subtitle_style)
        
        # 배지 테이블
        badge_table = Table(
            [[icon_para], [title_para], [score_para], [subtitle_para]],
            colWidths=[15*cm],
            rowHeights=[3*cm, 1.2*cm, 1.5*cm, 0.8*cm]  # 전체 크기 증가
        )
        
        badge_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), info['bg']),
            ('BOX', (0, 0), (-1, -1), 4, info['color']),  # 테두리 두께 증가
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        return badge_table


# Singleton instance for easy import
consulting_helpers = ConsultingDesignHelpers()


# Wrapper functions for backward compatibility
def create_executive_insight_box(title: str = "Executive Insight", 
                                  main_text: str = "", 
                                  detail_text: str = "", 
                                  box_type: str = "info"):
    """
    Wrapper for consulting_helpers.create_executive_insight_box
    
    Args:
        title: Box title
        main_text: Main message
        detail_text: Additional details
        box_type: Box type (info/success/warning/danger) - currently not used
    """
    # Combine main_text and detail_text
    combined_text = main_text
    if detail_text:
        combined_text += f"<br/><br/>{detail_text}"
    
    return consulting_helpers.create_executive_insight_box(combined_text, title)


# Export all
__all__ = [
    'ConsultingDesignHelpers',
    'consulting_helpers',
    'create_executive_insight_box',
    'create_flow_diagram',
    'create_horizontal_range_bar',
    'create_lifestyle_cards',
    'create_comparison_cards',
    'create_final_decision_badge',
]
