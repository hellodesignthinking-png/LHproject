"""
Advanced Chart Builder for ZeroSite v5.0 ENHANCED
Purpose: Create decision-ready charts/graphs with built-in conclusion highlighting
Author: ZeroSite by AntennaHoldings NataiHeum
Date: 2025-12-29

Design Philosophy:
- Every chart must have a ONE-SENTENCE CONCLUSION at the top
- Highlight the key data point that drives the decision
- Dim/gray out secondary data for focus
- No decorative charts - every visual element serves decision-making
"""

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from typing import List, Dict, Any, Tuple
import math

from .enhanced_design_system import EnhancedDesignSystem as EDS


class AdvancedChartBuilder:
    """Build decision-focused charts with automatic highlighting"""
    
    # Chart dimensions
    CHART_WIDTH = 180 * mm
    CHART_HEIGHT = 100 * mm
    CHART_SMALL_HEIGHT = 60 * mm
    
    # Visual hierarchy colors
    COLOR_PRIMARY = colors.HexColor("#1F2A44")  # Deep Navy
    COLOR_HIGHLIGHT = colors.HexColor("#E63946")  # Danger Red
    COLOR_SUCCESS = colors.HexColor("#2A9D8F")  # Success Green
    COLOR_WARNING = colors.HexColor("#F4A261")  # Warning Amber
    COLOR_DIMMED = colors.HexColor("#CCCCCC")  # Gray for non-key data
    COLOR_GRID = colors.HexColor("#E8E8E8")
    
    @classmethod
    def create_decision_bar_chart(cls, 
                                  data: List[Dict[str, Any]], 
                                  conclusion: str,
                                  highlight_index: int = 0,
                                  y_label: str = "점수",
                                  show_values: bool = True) -> List[Any]:
        """
        Create a bar chart that highlights the key decision point
        
        Args:
            data: List of {'label': str, 'value': float, 'color': str (optional)}
            conclusion: ONE-SENTENCE conclusion to display above chart
            highlight_index: Index of the bar to highlight (default: 0)
            y_label: Y-axis label
            show_values: Whether to show values on top of bars
        
        Returns:
            List of ReportLab flowables [Conclusion, Chart]
        """
        elements = []
        
        # 1. Conclusion at top (35% zone)
        conclusion_style = EDS.get_text_style('decision', size=14, color=cls.COLOR_HIGHLIGHT)
        elements.append(Paragraph(f"<b>{conclusion}</b>", conclusion_style))
        elements.append(Spacer(1, 10))
        
        # 2. Build the chart
        drawing = Drawing(cls.CHART_WIDTH, cls.CHART_HEIGHT)
        
        chart = VerticalBarChart()
        chart.x = 40
        chart.y = 30
        chart.width = cls.CHART_WIDTH - 60
        chart.height = cls.CHART_HEIGHT - 50
        
        # Extract labels and values
        labels = [item['label'] for item in data]
        values = [item['value'] for item in data]
        
        chart.data = [values]
        chart.categoryAxis.categoryNames = labels
        chart.categoryAxis.labels.fontSize = 10
        chart.categoryAxis.labels.angle = 0
        
        # Y-axis
        chart.valueAxis.labels.fontSize = 9
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(values) * 1.2 if values else 100
        chart.valueAxis.valueStep = max(values) / 5 if values else 20
        chart.valueAxis.gridLineColor = cls.COLOR_GRID
        
        # Bar colors: highlight one, dim others
        bar_colors = []
        for i in range(len(data)):
            if i == highlight_index:
                # Use custom color if provided, otherwise highlight color
                bar_colors.append(
                    colors.HexColor(data[i].get('color', cls.COLOR_HIGHLIGHT.hexval()))
                )
            else:
                bar_colors.append(cls.COLOR_DIMMED)
        
        chart.bars[0].fillColor = bar_colors[0]  # First bar
        # Apply color to all bars
        for i, bar_color in enumerate(bar_colors):
            if hasattr(chart.bars, '__getitem__'):
                chart.bars[0].fillColor = bar_color if i == 0 else chart.bars[0].fillColor
        
        # Simplify: Apply highlight to all bars via stroke
        chart.bars.strokeColor = None
        chart.bars.strokeWidth = 0
        
        # Add value labels on top if requested
        if show_values:
            for i, (label, value) in enumerate(zip(labels, values)):
                x_pos = chart.x + (i + 0.5) * (chart.width / len(labels))
                y_pos = chart.y + (value / chart.valueAxis.valueMax) * chart.height + 5
                
                label_color = cls.COLOR_PRIMARY if i == highlight_index else cls.COLOR_DIMMED
                
                drawing.add(String(
                    x_pos, y_pos,
                    f"{value:.1f}",
                    fontSize=11 if i == highlight_index else 9,
                    fillColor=label_color,
                    textAnchor='middle',
                    fontName='NanumBarunGothic-Bold' if i == highlight_index else 'NanumBarunGothic'
                ))
        
        drawing.add(chart)
        elements.append(drawing)
        
        return elements
    
    @classmethod
    def create_comparison_table(cls,
                                rows: List[Dict[str, Any]],
                                conclusion: str,
                                highlight_row: int = 0,
                                col_widths: List[float] = None) -> List[Any]:
        """
        Create a comparison table with one row highlighted
        
        Args:
            rows: List of {'label': str, 'values': List[str or float]}
            conclusion: ONE-SENTENCE conclusion
            highlight_row: Row index to highlight (0 = header excluded)
            col_widths: Optional column widths in mm
        
        Returns:
            List of flowables
        """
        elements = []
        
        # 1. Conclusion
        conclusion_style = EDS.get_text_style('decision', size=14, color=cls.COLOR_HIGHLIGHT)
        elements.append(Paragraph(f"<b>{conclusion}</b>", conclusion_style))
        elements.append(Spacer(1, 10))
        
        # 2. Build table data
        table_data = []
        
        # Header row
        if rows:
            header = ['항목'] + list(rows[0]['values'].keys() if isinstance(rows[0]['values'], dict) else [f"항목{i+1}" for i in range(len(rows[0]['values']))])
            table_data.append(header)
            
            # Data rows
            for row in rows:
                values = row['values']
                if isinstance(values, dict):
                    row_data = [row['label']] + list(values.values())
                else:
                    row_data = [row['label']] + values
                table_data.append(row_data)
        
        # Column widths
        if col_widths is None:
            num_cols = len(table_data[0]) if table_data else 3
            col_widths = [cls.CHART_WIDTH / num_cols] * num_cols
        
        # 3. Create table
        table = Table(table_data, colWidths=col_widths)
        
        # Base style
        style_commands = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), cls.COLOR_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'NanumBarunGothic-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'NanumBarunGothic'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('LEFTPADDING', (0, 1), (-1, -1), 8),
            ('RIGHTPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, cls.COLOR_GRID),
            ('LINEBELOW', (0, 0), (-1, 0), 2, cls.COLOR_PRIMARY),
        ]
        
        # Highlight the key row
        if highlight_row >= 0 and highlight_row < len(table_data) - 1:
            row_idx = highlight_row + 1  # +1 for header
            style_commands.extend([
                ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor("#FFF3CD")),
                ('FONTNAME', (0, row_idx), (-1, row_idx), 'NanumBarunGothic-Bold'),
                ('TEXTCOLOR', (0, row_idx), (-1, row_idx), cls.COLOR_HIGHLIGHT),
                ('LINEABOVE', (0, row_idx), (-1, row_idx), 1.5, cls.COLOR_HIGHLIGHT),
                ('LINEBELOW', (0, row_idx), (-1, row_idx), 1.5, cls.COLOR_HIGHLIGHT),
            ])
        
        table.setStyle(TableStyle(style_commands))
        elements.append(table)
        
        return elements
    
    @classmethod
    def create_risk_elimination_chart(cls,
                                      risks: List[Dict[str, Any]],
                                      conclusion: str = "LH 방식은 총 리스크를 68%p 감소") -> List[Any]:
        """
        Create a before/after risk comparison chart
        
        Args:
            risks: List of {'name': str, 'before': float, 'after': float}
            conclusion: ONE-SENTENCE conclusion
        
        Returns:
            List of flowables
        """
        elements = []
        
        # 1. Conclusion
        conclusion_style = EDS.get_text_style('decision', size=14, color=cls.COLOR_SUCCESS)
        elements.append(Paragraph(f"<b>✓ {conclusion}</b>", conclusion_style))
        elements.append(Spacer(1, 10))
        
        # 2. Table showing before/after
        table_data = [
            ['리스크 항목', '일반 분양 (%)', 'LH 방식 (%)', '감소폭']
        ]
        
        total_before = 0
        total_after = 0
        
        for risk in risks:
            before = risk['before']
            after = risk['after']
            reduction = before - after
            
            total_before += before
            total_after += after
            
            table_data.append([
                risk['name'],
                f"{before:.0f}%",
                f"{after:.0f}%" if after > 0 else "0% (제거)",
                f"▼ {reduction:.0f}%p"
            ])
        
        # Total row
        table_data.append([
            Paragraph("<b>총 리스크</b>", EDS.get_text_style('default')),
            Paragraph(f"<b>{total_before:.0f}%</b>", EDS.get_text_style('default')),
            Paragraph(f"<b>{total_after:.0f}%</b>", EDS.get_text_style('default', color=cls.COLOR_SUCCESS)),
            Paragraph(f"<b>▼ {total_before - total_after:.0f}%p</b>", 
                     EDS.get_text_style('default', color=cls.COLOR_SUCCESS))
        ])
        
        col_widths = [70*mm, 35*mm, 35*mm, 35*mm]
        table = Table(table_data, colWidths=col_widths)
        
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), cls.COLOR_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'NanumBarunGothic-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Body
            ('FONTNAME', (0, 1), (-1, -2), 'NanumBarunGothic'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            
            # Total row highlight
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#D4EDDA")),
            ('FONTNAME', (0, -1), (-1, -1), 'NanumBarunGothic-Bold'),
            ('LINEABOVE', (0, -1), (-1, -1), 2, cls.COLOR_SUCCESS),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, cls.COLOR_GRID),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        
        return elements
    
    @classmethod
    def create_module_compression_diagram(cls,
                                         modules: Dict[str, str],
                                         conclusion: str) -> List[Any]:
        """
        Create M2→M3→M4→M5→M6 compression diagram
        
        Args:
            modules: {'M2': 'one-line summary', 'M3': '...', ...}
            conclusion: Final ONE-SENTENCE from M6
        
        Returns:
            List of flowables
        """
        elements = []
        
        # 1. M6 Conclusion at top (largest font)
        conclusion_style = EDS.get_text_style('decision', size=16, color=cls.COLOR_HIGHLIGHT)
        elements.append(Paragraph(f"<b>⚡ {conclusion}</b>", conclusion_style))
        elements.append(Spacer(1, 15))
        
        # 2. Build compression table
        table_data = []
        
        module_order = ['M2', 'M3', 'M4', 'M5']
        for i, module in enumerate(module_order):
            if module in modules:
                arrow = "↓" if i < len(module_order) - 1 else ""
                table_data.append([
                    f"{module}",
                    modules[module],
                    arrow
                ])
        
        col_widths = [20*mm, 140*mm, 15*mm]
        table = Table(table_data, colWidths=col_widths)
        
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'NanumBarunGothic-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'NanumBarunGothic'),
            ('FONTNAME', (2, 0), (2, -1), 'NanumBarunGothic-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (2, 0), (2, -1), 14),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F0F0F0")),
            ('TEXTCOLOR', (0, 0), (0, -1), cls.COLOR_PRIMARY),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (1, -1), 0.5, cls.COLOR_GRID),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 10))
        
        # 3. Linkage explanation
        linkage_text = """
        <para alignment="left" fontSize="9" textColor="#666666">
        ※ 각 모듈은 독립적이지 않으며, M2→M3→M4→M5 순서대로 필연적으로 연결됩니다.<br/>
        하나의 모듈이 빠지면 최종 결론(M6)이 성립하지 않습니다.
        </para>
        """
        elements.append(Paragraph(linkage_text, EDS.get_text_style('caption')))
        
        return elements
