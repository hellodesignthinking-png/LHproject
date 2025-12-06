"""
Phase 10.5: Advanced Chart Generator for Full LH Report
Generates professional charts for financial analysis visualization

Charts:
- CAPEX Breakdown (Pie Chart)
- NPV Discount Curve (Line Chart)
- IRR Sensitivity Table
- OpEx vs Revenue Timeline (Bar Chart)
- Market Signal Comparison (Radar Chart)
- Demand Score Heatmap
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
    Generate all financial charts at once
    
    Args:
        financial_data: Complete financial analysis data
        output_dir: Output directory (optional)
        
    Returns:
        Dictionary mapping chart names to paths/base64 strings
    """
    generator = ChartGenerator(output_dir)
    charts = {}
    
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
    
    return charts
