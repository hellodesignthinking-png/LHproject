"""
Phase 10.5 + Phase B: Advanced Chart Generator for Full LH Report
Generates professional charts for financial analysis visualization

Existing Charts (Phase 10.5):
- CAPEX Breakdown (Pie Chart)
- NPV Discount Curve (Line Chart)
- IRR Sensitivity Table
- OpEx vs Revenue Timeline (Bar Chart)
- Market Signal Comparison (Gauge Chart)
- Demand Score Bar Chart

New Charts (Phase B):
- Gantt Chart (36-Month Project Roadmap)
- NPV Tornado Chart (Sensitivity Analysis)
- Financial Scorecard (Visual KPI Dashboard)
- Competitive Analysis Table (Market Comparison)
- 30-Year Cashflow Chart (Long-term Projection)
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import io
import base64

# LH Brand Colors
LH_BLUE = '#2165D1'
LH_LIGHT_BLUE = '#5B9BD5'
LH_GRAY = '#7F7F7F'
LH_GREEN = '#70AD47'
LH_ORANGE = '#ED7D31'
LH_RED = '#E74C3C'

class ChartGenerator:
    """Generate professional charts for LH Full Report"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize chart generator
        
        Args:
            output_dir: Directory to save chart images. If None, returns base64 strings.
        """
        self.output_dir = output_dir
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set Korean font
        plt.rcParams['font.family'] = 'NanumGothic'
        plt.rcParams['axes.unicode_minus'] = False
    
    def generate_capex_breakdown_pie(
        self,
        capex_data: Dict[str, float],
        filename: str = "capex_breakdown.png"
    ) -> str:
        """
        Generate CAPEX breakdown pie chart
        
        Args:
            capex_data: Dictionary of CAPEX components (e.g., {'토지비': 1000, '건축비': 1500, ...})
            filename: Output filename
            
        Returns:
            File path or base64 string
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        labels = list(capex_data.keys())
        sizes = list(capex_data.values())
        colors = [LH_BLUE, LH_LIGHT_BLUE, LH_GREEN, LH_ORANGE, LH_GRAY]
        
        # Create pie chart with percentages
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors[:len(labels)],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10}
        )
        
        # Make percentage text bold and white
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('총 공사비 구성', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        return self._save_or_encode(fig, filename)
    
    def generate_npv_discount_curve(
        self,
        years: List[int],
        cashflows: List[float],
        discount_rate: float = 0.02,
        filename: str = "npv_curve.png"
    ) -> str:
        """
        Generate NPV discount curve showing present value over time
        
        Args:
            years: List of years
            cashflows: Annual cashflows
            discount_rate: Discount rate (default: 2% for public projects)
            filename: Output filename
            
        Returns:
            File path or base64 string
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Calculate present values
        pv_values = [cf / ((1 + discount_rate) ** year) for year, cf in zip(years, cashflows)]
        cumulative_pv = np.cumsum(pv_values)
        
        # Plot bars for annual PV
        ax.bar(years, pv_values, color=LH_BLUE, alpha=0.6, label='연간 현재가치')
        
        # Plot line for cumulative NPV
        ax.plot(years, cumulative_pv, color=LH_ORANGE, linewidth=2.5, 
                marker='o', markersize=5, label='누적 NPV')
        
        # Add zero line
        ax.axhline(y=0, color=LH_GRAY, linestyle='--', linewidth=1)
        
        ax.set_xlabel('연도 (Year)', fontsize=11, fontweight='bold')
        ax.set_ylabel('현재가치 (억원)', fontsize=11, fontweight='bold')
        ax.set_title(f'NPV 할인곡선 (할인율 {discount_rate*100:.1f}%)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        return self._save_or_encode(fig, filename)
    
    def generate_irr_sensitivity_table(
        self,
        base_irr: float,
        optimistic_irr: float,
        pessimistic_irr: float,
        filename: str = "irr_sensitivity.png"
    ) -> str:
        """
        Generate IRR sensitivity analysis table visualization
        
        Args:
            base_irr: Base case IRR
            optimistic_irr: Optimistic scenario IRR
            pessimistic_irr: Pessimistic scenario IRR
            filename: Output filename
            
        Returns:
            File path or base64 string
        """
        fig, ax = plt.subplots(figsize=(10, 5))
        
        scenarios = ['비관적\n(Pessimistic)', '기본\n(Base)', '낙관적\n(Optimistic)']
        irr_values = [pessimistic_irr, base_irr, optimistic_irr]
        colors = [LH_RED, LH_BLUE, LH_GREEN]
        
        bars = ax.barh(scenarios, irr_values, color=colors, alpha=0.8, edgecolor='black')
        
        # Add percentage labels on bars
        for i, (bar, irr) in enumerate(zip(bars, irr_values)):
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{irr:.2f}%',
                   ha='left', va='center', fontsize=12, fontweight='bold')
        
        ax.set_xlabel('IRR (%)', fontsize=11, fontweight='bold')
        ax.set_title('내부수익률(IRR) 민감도 분석', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        return self._save_or_encode(fig, filename)
    
    def generate_opex_revenue_timeline(
        self,
        years: List[int],
        revenues: List[float],
        opex: List[float],
        filename: str = "opex_revenue_timeline.png"
    ) -> str:
        """
        Generate OpEx vs Revenue timeline bar chart
        
        Args:
            years: List of years
            revenues: Annual revenues
            opex: Annual operating expenses
            filename: Output filename
            
        Returns:
            File path or base64 string
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(years))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, revenues, width, label='수익 (Revenue)', 
                       color=LH_GREEN, alpha=0.8)
        bars2 = ax.bar(x + width/2, opex, width, label='운영비 (OpEx)', 
                       color=LH_ORANGE, alpha=0.8)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('연도 (Year)', fontsize=11, fontweight='bold')
        ax.set_ylabel('금액 (억원)', fontsize=11, fontweight='bold')
        ax.set_title('연간 수익 vs 운영비 추이', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels([f'Y{y}' for y in years])
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        plt.tight_layout()
        return self._save_or_encode(fig, filename)
    
    def generate_market_signal_gauge(
        self,
        zerosite_value: float,
        market_avg: float,
        filename: str = "market_signal.png"
    ) -> str:
        """
        Generate market signal comparison gauge chart
        
        Args:
            zerosite_value: ZeroSite calculated value (억원)
            market_avg: Market average value (억원)
            filename: Output filename
            
        Returns:
            File path or base64 string
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = ['ZeroSite\n계산가', '시장\n평균가']
        values = [zerosite_value, market_avg]
        
        delta_pct = ((zerosite_value - market_avg) / market_avg) * 100
        
        # Determine color based on signal
        if delta_pct < -15:
            signal_color = LH_GREEN
            signal_text = "저평가 (UNDERVALUED)"
        elif delta_pct > 15:
            signal_color = LH_RED
            signal_text = "고평가 (OVERVALUED)"
        else:
            signal_color = LH_BLUE
            signal_text = "적정가 (FAIR)"
        
        bars = ax.bar(categories, values, color=[LH_BLUE, LH_GRAY], alpha=0.7, 
                      edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1f}억원',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_ylabel('가격 (억원)', fontsize=11, fontweight='bold')
        ax.set_title(f'시장 대비 가격 분석: {signal_text}\n(델타: {delta_pct:+.1f}%)',
                     fontsize=14, fontweight='bold', pad=20, color=signal_color)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        plt.tight_layout()
        return self._save_or_encode(fig, filename)
    
    def generate_demand_score_bar(
        self,
        demand_scores: Dict[str, float],
        filename: str = "demand_scores.png"
    ) -> str:
        """
        Generate demand score comparison bar chart
        
        Args:
            demand_scores: Dictionary of housing types and their demand scores
                          (e.g., {'청년': 65, '신혼부부': 72, ...})
            filename: Output filename
            
        Returns:
            File path or base64 string
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        housing_types = list(demand_scores.keys())
        scores = list(demand_scores.values())
        
        # Color bars based on score
        colors = []
        for score in scores:
            if score >= 70:
                colors.append(LH_GREEN)
            elif score >= 50:
                colors.append(LH_BLUE)
            else:
                colors.append(LH_ORANGE)
        
        bars = ax.bar(housing_types, scores, color=colors, alpha=0.8, edgecolor='black')
        
        # Add score labels
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{score:.1f}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Add threshold lines
        ax.axhline(y=70, color=LH_GREEN, linestyle='--', linewidth=1, alpha=0.5, label='고수요 (≥70)')
        ax.axhline(y=50, color=LH_BLUE, linestyle='--', linewidth=1, alpha=0.5, label='중수요 (≥50)')
        
        ax.set_ylabel('수요 점수', fontsize=11, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.set_title('주거유형별 지역 수요 분석', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        plt.tight_layout()
        return self._save_or_encode(fig, filename)
    
    # ============================================================
    # Phase B: New Visualization Methods
    # ============================================================
    
    def generate_gantt_chart(
        self,
        milestones: List[Dict[str, Any]],
        filename: str = "gantt_chart.png"
    ) -> str:
        """
        Generate 36-month project roadmap Gantt chart
        
        Args:
            milestones: List of milestone dictionaries with keys:
                       - 'name': Milestone name (str)
                       - 'start_month': Start month (int, 0-35)
                       - 'duration': Duration in months (int)
                       - 'phase': Phase name (str)
            filename: Output filename
            
        Returns:
            File path or base64 string
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Phase colors
        phase_colors = {
            '준비단계': LH_BLUE,
            '착공단계': LH_GREEN,
            '시공단계': LH_ORANGE,
            '준공단계': LH_GRAY
        }
        
        # Sort milestones by start month
        sorted_milestones = sorted(milestones, key=lambda x: x['start_month'])
        
        # Plot each milestone as a horizontal bar
        for i, milestone in enumerate(sorted_milestones):
            start = milestone['start_month']
            duration = milestone['duration']
            phase = milestone.get('phase', '기타')
            color = phase_colors.get(phase, LH_GRAY)
            
            ax.barh(i, duration, left=start, height=0.6, 
                   color=color, alpha=0.7, edgecolor='black', linewidth=1)
            
            # Add milestone name
            ax.text(start + duration/2, i, milestone['name'],
                   ha='center', va='center', fontsize=9, fontweight='bold',
                   color='white' if duration > 3 else 'black')
        
        # Formatting
        ax.set_yticks(range(len(sorted_milestones)))
        ax.set_yticklabels([m['name'] for m in sorted_milestones], fontsize=9)
        ax.set_xlabel('개월 (Month)', fontsize=11, fontweight='bold')
        ax.set_title('36개월 프로젝트 로드맵 (Project Roadmap)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, 36)
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        
        # Add phase markers every 12 months
        for month in [0, 12, 24, 36]:
            ax.axvline(x=month, color=LH_RED, linestyle='--', linewidth=1.5, alpha=0.5)
            if month < 36:
                ax.text(month + 6, len(sorted_milestones) - 0.5, f'Year {month//12 + 1}',
                       ha='center', va='top', fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
        
        # Legend
        legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, alpha=0.7, edgecolor='black')
                          for phase, color in phase_colors.items()]
        ax.legend(legend_elements, phase_colors.keys(), 
                 loc='upper right', fontsize=9, title='단계 (Phase)')
        
        plt.tight_layout()
        return self._save_or_encode(fig, filename)
    
    def generate_npv_tornado_chart(
        self,
        sensitivity_data: Dict[str, Dict[str, float]],
        base_npv: float,
        filename: str = "npv_tornado.png"
    ) -> str:
        """
        Generate NPV Tornado chart for sensitivity analysis
        
        Args:
            sensitivity_data: Dictionary with format:
                {
                    'variable_name': {
                        'low': npv_value_at_-10%,
                        'high': npv_value_at_+10%
                    },
                    ...
                }
            base_npv: Base case NPV value
            filename: Output filename
            
        Returns:
            File path or base64 string
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Calculate impacts
        impacts = []
        for var_name, values in sensitivity_data.items():
            low_impact = values['low'] - base_npv
            high_impact = values['high'] - base_npv
            total_range = abs(high_impact - low_impact)
            impacts.append({
                'name': var_name,
                'low': low_impact,
                'high': high_impact,
                'range': total_range
            })
        
        # Sort by total range (most sensitive first)
        impacts = sorted(impacts, key=lambda x: x['range'], reverse=True)
        
        # Plot tornado bars
        y_pos = np.arange(len(impacts))
        for i, impact in enumerate(impacts):
            # Low side (left, red)
            ax.barh(i, abs(impact['low']), left=min(0, impact['low']), 
                   height=0.8, color=LH_RED, alpha=0.7, label='하향 (-10%)' if i == 0 else '')
            # High side (right, green)
            ax.barh(i, abs(impact['high']), left=max(0, impact['high'] - abs(impact['high'])), 
                   height=0.8, color=LH_GREEN, alpha=0.7, label='상향 (+10%)' if i == 0 else '')
            
            # Add range labels
            ax.text(impact['low'] - 5, i, f'{impact["low"]:.1f}억',
                   ha='right', va='center', fontsize=9, fontweight='bold')
            ax.text(impact['high'] + 5, i, f'{impact["high"]:.1f}억',
                   ha='left', va='center', fontsize=9, fontweight='bold')
        
        # Add base NPV line
        ax.axvline(x=0, color=LH_BLUE, linestyle='-', linewidth=2.5, 
                  label=f'기준 NPV ({base_npv:.1f}억)')
        
        # Formatting
        ax.set_yticks(y_pos)
        ax.set_yticklabels([imp['name'] for imp in impacts], fontsize=10)
        ax.set_xlabel('NPV 변동 (억원)', fontsize=11, fontweight='bold')
        ax.set_title('NPV 민감도 분석 (Tornado Chart)\n변수별 ±10% 변동 시 NPV 영향', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='lower right', fontsize=9)
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        return self._save_or_encode(fig, filename)
    
    def generate_financial_scorecard(
        self,
        kpis: Dict[str, Any],
        filename: str = "financial_scorecard.png"
    ) -> str:
        """
        Generate visual Financial Scorecard with key KPIs
        
        Args:
            kpis: Dictionary with KPI values:
                {
                    'capex': float,  # 총 투자비 (억원)
                    'npv': float,    # 순현재가치 (억원)
                    'irr': float,    # 내부수익률 (%)
                    'payback': float, # 회수기간 (년)
                    'roi': float,    # 투자수익률 (%)
                    'grade': str     # 종합등급 (A+, A, B+, etc.)
                }
            filename: Output filename
            
        Returns:
            File path or base64 string
        """
        fig = plt.figure(figsize=(14, 8))
        gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
        
        # Title
        fig.suptitle('재무 성과 지표 (Financial Scorecard)', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        # KPI Cards
        kpi_configs = [
            {'key': 'capex', 'label': '총 투자비\n(CAPEX)', 'unit': '억원', 'color': LH_BLUE},
            {'key': 'npv', 'label': '순현재가치\n(NPV)', 'unit': '억원', 'color': LH_GREEN},
            {'key': 'irr', 'label': '내부수익률\n(IRR)', 'unit': '%', 'color': LH_ORANGE},
            {'key': 'payback', 'label': '투자회수기간\n(Payback)', 'unit': '년', 'color': LH_GRAY},
            {'key': 'roi', 'label': '투자수익률\n(ROI)', 'unit': '%', 'color': LH_LIGHT_BLUE},
        ]
        
        for i, config in enumerate(kpi_configs):
            row = i // 3
            col = i % 3
            ax = fig.add_subplot(gs[row, col])
            
            value = kpis.get(config['key'], 0)
            
            # Draw KPI card
            ax.text(0.5, 0.7, config['label'], 
                   ha='center', va='center', fontsize=12, fontweight='bold',
                   transform=ax.transAxes)
            ax.text(0.5, 0.3, f"{value:.1f}{config['unit']}", 
                   ha='center', va='center', fontsize=20, fontweight='bold',
                   color=config['color'], transform=ax.transAxes)
            
            # Add background color
            ax.add_patch(plt.Rectangle((0, 0), 1, 1, 
                                      facecolor=config['color'], alpha=0.1,
                                      transform=ax.transAxes))
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        # Overall Grade (bottom center, larger)
        ax_grade = fig.add_subplot(gs[2, :])
        grade = kpis.get('grade', 'B+')
        
        # Grade color
        grade_colors = {
            'A+': LH_GREEN, 'A': LH_GREEN, 'A-': LH_LIGHT_BLUE,
            'B+': LH_BLUE, 'B': LH_BLUE, 'B-': LH_ORANGE,
            'C+': LH_ORANGE, 'C': LH_RED
        }
        grade_color = grade_colors.get(grade, LH_GRAY)
        
        ax_grade.text(0.5, 0.5, f'종합 등급: {grade}', 
                     ha='center', va='center', fontsize=28, fontweight='bold',
                     color=grade_color, transform=ax_grade.transAxes,
                     bbox=dict(boxstyle='round,pad=0.5', facecolor=grade_color, 
                              alpha=0.2, edgecolor=grade_color, linewidth=3))
        
        ax_grade.set_xlim(0, 1)
        ax_grade.set_ylim(0, 1)
        ax_grade.axis('off')
        
        return self._save_or_encode(fig, filename)
    
    def generate_competitive_analysis_table(
        self,
        competitors: List[Dict[str, Any]],
        current_project: Dict[str, Any],
        filename: str = "competitive_analysis.png"
    ) -> str:
        """
        Generate Competitive Analysis comparison table
        
        Args:
            competitors: List of competitor project dictionaries:
                [{
                    'name': str,
                    'price': float,  # 분양가/임대료 (만원)
                    'distance': float,  # 거리 (km)
                    'units': int,  # 세대수
                    'completion': str  # 준공년도
                }, ...]
            current_project: Current project data (same format as competitors)
            filename: Output filename
            
        Returns:
            File path or base64 string
        """
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Prepare table data
        columns = ['프로젝트', '가격\n(만원)', '거리\n(km)', '세대수', '준공년도']
        
        # Add current project at top
        all_projects = [current_project] + competitors
        table_data = []
        for proj in all_projects:
            table_data.append([
                proj['name'],
                f"{proj['price']:.0f}",
                f"{proj['distance']:.1f}",
                f"{proj['units']:,}",
                proj['completion']
            ])
        
        # Create table
        table = ax.table(cellText=table_data, colLabels=columns,
                        cellLoc='center', loc='center',
                        colColours=[LH_BLUE]*len(columns))
        
        # Style table
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        # Highlight current project (first row)
        for i in range(len(columns)):
            cell = table[(1, i)]  # Row 1 (after header)
            cell.set_facecolor(LH_LIGHT_BLUE)
            cell.set_alpha(0.3)
            cell.set_text_props(weight='bold')
        
        # Header styling
        for i in range(len(columns)):
            cell = table[(0, i)]
            cell.set_facecolor(LH_BLUE)
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('경쟁 프로젝트 비교 분석 (Competitive Analysis)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')
        
        plt.tight_layout()
        return self._save_or_encode(fig, filename)
    
    def generate_30year_cashflow_chart(
        self,
        years: List[int],
        revenues: List[float],
        expenses: List[float],
        net_cashflows: List[float],
        filename: str = "30year_cashflow.png"
    ) -> str:
        """
        Generate 30-year cashflow projection chart
        
        Args:
            years: List of years (0-29 for 30 years)
            revenues: Annual revenues (억원)
            expenses: Annual expenses (억원)
            net_cashflows: Annual net cashflows (억원)
            filename: Output filename
            
        Returns:
            File path or base64 string
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                       gridspec_kw={'height_ratios': [2, 1]})
        
        # Top chart: Stacked area for revenues and expenses
        ax1.fill_between(years, 0, revenues, color=LH_GREEN, alpha=0.3, label='수익 (Revenue)')
        ax1.fill_between(years, 0, [-e for e in expenses], color=LH_RED, alpha=0.3, label='지출 (Expense)')
        ax1.plot(years, revenues, color=LH_GREEN, linewidth=2, marker='o', markersize=3)
        ax1.plot(years, [-e for e in expenses], color=LH_RED, linewidth=2, marker='o', markersize=3)
        
        ax1.axhline(y=0, color=LH_GRAY, linestyle='-', linewidth=1)
        ax1.set_ylabel('연간 금액 (억원)', fontsize=11, fontweight='bold')
        ax1.set_title('30년 현금흐름 분석 (30-Year Cashflow Projection)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Bottom chart: Net cashflow bars
        colors = [LH_GREEN if cf > 0 else LH_RED for cf in net_cashflows]
        ax2.bar(years, net_cashflows, color=colors, alpha=0.6, edgecolor='black', linewidth=0.5)
        ax2.axhline(y=0, color=LH_GRAY, linestyle='-', linewidth=1.5)
        
        # Add cumulative line
        cumulative_cf = np.cumsum(net_cashflows)
        ax2.plot(years, cumulative_cf, color=LH_BLUE, linewidth=2.5, 
                marker='o', markersize=4, label='누적 현금흐름')
        
        ax2.set_xlabel('연도 (Year)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('순현금흐름 (억원)', fontsize=11, fontweight='bold')
        ax2.legend(loc='upper left', fontsize=10)
        ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # Add decade markers
        for decade in [0, 10, 20, 30]:
            if decade < 30:
                ax1.axvline(x=decade, color=LH_ORANGE, linestyle='--', linewidth=1, alpha=0.5)
                ax2.axvline(x=decade, color=LH_ORANGE, linestyle='--', linewidth=1, alpha=0.5)
        
        plt.tight_layout()
        return self._save_or_encode(fig, filename)
    
    def _save_or_encode(self, fig, filename: str) -> str:
        """
        Save figure to file or encode as base64
        
        Args:
            fig: Matplotlib figure
            filename: Output filename
            
        Returns:
            File path (if output_dir set) or base64 data URI
        """
        if self.output_dir:
            # Save to file
            output_path = self.output_dir / filename
            fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            return str(output_path)
        else:
            # Return base64 string
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"


# Convenience functions for quick chart generation
def generate_all_financial_charts(
    financial_data: Dict[str, Any],
    output_dir: Optional[Path] = None
) -> Dict[str, str]:
    """
    Generate all financial charts at once (Phase 10.5 + Phase B)
    
    Args:
        financial_data: Complete financial analysis data
        output_dir: Output directory (optional)
        
    Returns:
        Dictionary mapping chart names to paths/base64 strings
    """
    generator = ChartGenerator(output_dir)
    charts = {}
    
    # ===== Phase 10.5 Charts =====
    
    # CAPEX Breakdown
    if 'capex_breakdown' in financial_data:
        charts['capex_breakdown'] = generator.generate_capex_breakdown_pie(
            financial_data['capex_breakdown']
        )
    
    # NPV Curve
    if 'cashflows' in financial_data and 'years' in financial_data:
        charts['npv_curve'] = generator.generate_npv_discount_curve(
            financial_data['years'],
            financial_data['cashflows']
        )
    
    # IRR Sensitivity
    if all(k in financial_data for k in ['base_irr', 'optimistic_irr', 'pessimistic_irr']):
        charts['irr_sensitivity'] = generator.generate_irr_sensitivity_table(
            financial_data['base_irr'],
            financial_data['optimistic_irr'],
            financial_data['pessimistic_irr']
        )
    
    # OpEx vs Revenue
    if all(k in financial_data for k in ['years', 'revenues', 'opex']):
        charts['opex_revenue'] = generator.generate_opex_revenue_timeline(
            financial_data['years'],
            financial_data['revenues'],
            financial_data['opex']
        )
    
    # Market Signal
    if all(k in financial_data for k in ['zerosite_value', 'market_avg']):
        charts['market_signal'] = generator.generate_market_signal_gauge(
            financial_data['zerosite_value'],
            financial_data['market_avg']
        )
    
    # Demand Scores
    if 'demand_scores' in financial_data:
        charts['demand_scores'] = generator.generate_demand_score_bar(
            financial_data['demand_scores']
        )
    
    # ===== Phase B Charts =====
    
    # Gantt Chart (36-month roadmap)
    if 'milestones' in financial_data:
        charts['gantt_chart'] = generator.generate_gantt_chart(
            financial_data['milestones']
        )
    
    # NPV Tornado Chart (sensitivity analysis)
    if 'sensitivity_data' in financial_data and 'base_npv' in financial_data:
        charts['npv_tornado'] = generator.generate_npv_tornado_chart(
            financial_data['sensitivity_data'],
            financial_data['base_npv']
        )
    
    # Financial Scorecard (visual KPI dashboard)
    if 'kpis' in financial_data:
        charts['financial_scorecard'] = generator.generate_financial_scorecard(
            financial_data['kpis']
        )
    
    # Competitive Analysis Table
    if 'competitors' in financial_data and 'current_project' in financial_data:
        charts['competitive_analysis'] = generator.generate_competitive_analysis_table(
            financial_data['competitors'],
            financial_data['current_project']
        )
    
    # 30-Year Cashflow Chart
    if all(k in financial_data for k in ['years_30', 'revenues_30', 'expenses_30', 'net_cashflows_30']):
        charts['cashflow_30year'] = generator.generate_30year_cashflow_chart(
            financial_data['years_30'],
            financial_data['revenues_30'],
            financial_data['expenses_30'],
            financial_data['net_cashflows_30']
        )
    
    return charts


def generate_all_financial_charts_parallel(
    financial_data: Dict[str, Any],
    output_dir: Optional[Path] = None,
    max_workers: int = 4
) -> Dict[str, str]:
    """
    Generate all financial charts in parallel using ThreadPoolExecutor
    
    Args:
        financial_data: Complete financial analysis data
        output_dir: Output directory (optional)
        max_workers: Maximum number of parallel workers (default: 4)
        
    Returns:
        Dictionary mapping chart names to paths/base64 strings
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time
    
    generator = ChartGenerator(output_dir)
    charts = {}
    
    # Define chart generation tasks
    tasks = []
    
    # Phase 10.5 Charts
    if 'capex_breakdown' in financial_data:
        tasks.append(('capex_breakdown', lambda: generator.generate_capex_breakdown_pie(
            financial_data['capex_breakdown']
        )))
    
    if 'cashflows' in financial_data and 'years' in financial_data:
        tasks.append(('npv_curve', lambda: generator.generate_npv_discount_curve(
            financial_data['years'], financial_data['cashflows']
        )))
    
    if all(k in financial_data for k in ['base_irr', 'optimistic_irr', 'pessimistic_irr']):
        tasks.append(('irr_sensitivity', lambda: generator.generate_irr_sensitivity_table(
            financial_data['base_irr'],
            financial_data['optimistic_irr'],
            financial_data['pessimistic_irr']
        )))
    
    if all(k in financial_data for k in ['years', 'revenues', 'opex']):
        tasks.append(('opex_revenue', lambda: generator.generate_opex_revenue_timeline(
            financial_data['years'],
            financial_data['revenues'],
            financial_data['opex']
        )))
    
    if all(k in financial_data for k in ['zerosite_value', 'market_avg']):
        tasks.append(('market_signal', lambda: generator.generate_market_signal_gauge(
            financial_data['zerosite_value'],
            financial_data['market_avg']
        )))
    
    if 'demand_scores' in financial_data:
        tasks.append(('demand_score', lambda: generator.generate_demand_score_bar(
            financial_data['demand_scores']
        )))
    
    # Phase B Charts
    if 'milestones' in financial_data:
        tasks.append(('gantt_chart', lambda: generator.generate_gantt_chart(
            financial_data['milestones']
        )))
    
    if 'sensitivity_data' in financial_data and 'base_npv' in financial_data:
        tasks.append(('npv_tornado', lambda: generator.generate_npv_tornado_chart(
            financial_data['sensitivity_data'],
            financial_data['base_npv']
        )))
    
    if 'kpis' in financial_data:
        tasks.append(('financial_scorecard', lambda: generator.generate_financial_scorecard(
            financial_data['kpis']
        )))
    
    if 'competitors' in financial_data and 'current_project' in financial_data:
        tasks.append(('competitive_analysis', lambda: generator.generate_competitive_analysis_table(
            financial_data['competitors'],
            financial_data['current_project']
        )))
    
    if all(k in financial_data for k in ['years_30', 'revenues_30', 'expenses_30', 'net_cashflows_30']):
        tasks.append(('cashflow_30year', lambda: generator.generate_30year_cashflow_chart(
            financial_data['years_30'],
            financial_data['revenues_30'],
            financial_data['expenses_30'],
            financial_data['net_cashflows_30']
        )))
    
    # Execute tasks in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_name = {
            executor.submit(task_func): task_name 
            for task_name, task_func in tasks
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_name):
            chart_name = future_to_name[future]
            try:
                charts[chart_name] = future.result()
            except Exception as e:
                print(f"Warning: Failed to generate {chart_name}: {e}")
                charts[chart_name] = None
    
    return charts
