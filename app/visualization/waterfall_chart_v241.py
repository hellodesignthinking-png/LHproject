"""
ZeroSite v24.1 - Financial Waterfall Chart Generator
Generates waterfall charts for financial analysis

Author: ZeroSite Development Team
Version: v24.1.0
Created: 2025-12-12
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
import base64
from io import BytesIO


@dataclass
class WaterfallComponent:
    """Single component in waterfall chart"""
    label: str
    value: float
    is_subtotal: bool = False
    color: Optional[str] = None


class WaterfallChartGenerator:
    """
    Financial Waterfall Chart Generator for ZeroSite v24.1
    
    Creates professional waterfall charts showing:
    - CAPEX breakdown
    - Operating cashflow
    - Net cashflow
    - Color-coded by positive/negative/subtotal
    """
    
    def __init__(self):
        """Initialize waterfall chart generator"""
        self.version = "24.1.0"
        
        # Color scheme
        self.colors = {
            "positive": "#2ecc71",  # Green
            "negative": "#e74c3c",  # Red
            "neutral": "#3498db",   # Blue
            "subtotal": "#34495e"   # Dark gray
        }
        
        # Chart styling
        self.figsize = (12, 6)
        self.dpi = 100
    
    def generate_chart(
        self,
        components: List[WaterfallComponent],
        title: str = "Financial Waterfall Analysis",
        y_label: str = "Amount (억원)"
    ) -> str:
        """
        Generate waterfall chart
        
        Args:
            components: List of waterfall components
            title: Chart title
            y_label: Y-axis label
            
        Returns:
            Base64-encoded PNG image
        """
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        # Prepare data
        labels = [comp.label for comp in components]
        values = [comp.value for comp in components]
        
        # Calculate bar positions and heights
        positions, heights, bottoms, colors = self._calculate_waterfall_positions(components)
        
        # Draw bars
        bars = ax.bar(
            positions,
            heights,
            bottom=bottoms,
            color=colors,
            edgecolor='black',
            linewidth=1.5,
            alpha=0.8
        )
        
        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, values)):
            if components[i].is_subtotal:
                # For subtotals, show cumulative value
                y_pos = bottoms[i] + heights[i]
            else:
                # For regular bars, show value in the middle
                y_pos = bottoms[i] + heights[i] / 2
            
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                y_pos,
                f'{value:,.0f}',
                ha='center',
                va='center',
                fontsize=9,
                fontweight='bold',
                color='white' if not components[i].is_subtotal else 'black'
            )
        
        # Draw connecting lines between bars
        for i in range(len(components) - 1):
            if not components[i+1].is_subtotal:
                # Connect current bar to next bar
                x1 = positions[i] + 0.4
                x2 = positions[i+1] - 0.4
                y = bottoms[i] + heights[i]
                ax.plot([x1, x2], [y, y], 'k--', linewidth=1, alpha=0.5)
        
        # Customize chart
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=10)
        ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Add grid
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: f'{x:,.0f}')
        )
        
        # Add zero line
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert to base64
        return self._fig_to_base64(fig)
    
    def generate_financial_waterfall(
        self,
        land_cost: float,
        construction_cost: float,
        other_capex: float,
        revenue: float,
        operating_cost: float,
        title: str = "프로젝트 재무 흐름"
    ) -> str:
        """
        Generate standard financial waterfall chart
        
        Args:
            land_cost: Land acquisition cost (negative)
            construction_cost: Construction cost (negative)
            other_capex: Other CAPEX (negative)
            revenue: Total revenue (positive)
            operating_cost: Operating cost (negative)
            title: Chart title
            
        Returns:
            Base64-encoded PNG image
        """
        # Create components
        components = [
            WaterfallComponent("시작", 0, is_subtotal=True),
            WaterfallComponent("토지비용", -abs(land_cost)),
            WaterfallComponent("건축비용", -abs(construction_cost)),
            WaterfallComponent("기타 CAPEX", -abs(other_capex)),
            WaterfallComponent("총 투자비", 
                             -(abs(land_cost) + abs(construction_cost) + abs(other_capex)),
                             is_subtotal=True),
            WaterfallComponent("매출", revenue),
            WaterfallComponent("운영비용", -abs(operating_cost)),
            WaterfallComponent("순이익",
                             revenue - abs(operating_cost) - abs(land_cost) - abs(construction_cost) - abs(other_capex),
                             is_subtotal=True)
        ]
        
        return self.generate_chart(components, title=title)
    
    def generate_roi_waterfall(
        self,
        initial_investment: float,
        annual_revenues: List[float],
        annual_costs: List[float],
        years: int = 5
    ) -> str:
        """
        Generate ROI waterfall over multiple years
        
        Args:
            initial_investment: Initial investment amount
            annual_revenues: List of annual revenues
            annual_costs: List of annual costs
            years: Number of years
            
        Returns:
            Base64-encoded PNG image
        """
        components = [
            WaterfallComponent("초기 투자", -abs(initial_investment), is_subtotal=True)
        ]
        
        cumulative = -abs(initial_investment)
        
        for year in range(min(years, len(annual_revenues), len(annual_costs))):
            net_income = annual_revenues[year] - annual_costs[year]
            cumulative += net_income
            
            components.append(
                WaterfallComponent(f"Year {year+1} 순익", net_income)
            )
        
        components.append(
            WaterfallComponent("최종 누적", cumulative, is_subtotal=True)
        )
        
        return self.generate_chart(
            components,
            title="투자수익률 분석 (연도별)",
            y_label="누적 금액 (억원)"
        )
    
    def _calculate_waterfall_positions(
        self,
        components: List[WaterfallComponent]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """
        Calculate positions, heights, bottoms for waterfall bars
        
        Returns:
            Tuple of (positions, heights, bottoms, colors)
        """
        n = len(components)
        positions = np.arange(n)
        heights = np.zeros(n)
        bottoms = np.zeros(n)
        colors = []
        
        cumulative = 0
        
        for i, comp in enumerate(components):
            if comp.is_subtotal:
                # Subtotal bar: show cumulative value from zero
                if i == 0:
                    # First bar (starting point)
                    heights[i] = 0
                    bottoms[i] = 0
                else:
                    heights[i] = cumulative
                    bottoms[i] = 0
                colors.append(comp.color or self.colors["subtotal"])
            else:
                # Regular bar: show change
                if comp.value >= 0:
                    heights[i] = comp.value
                    bottoms[i] = cumulative
                    colors.append(comp.color or self.colors["positive"])
                else:
                    heights[i] = abs(comp.value)
                    bottoms[i] = cumulative + comp.value
                    colors.append(comp.color or self.colors["negative"])
                
                cumulative += comp.value
        
        return positions, heights, bottoms, colors
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', dpi=self.dpi)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        return image_base64


# Module exports
__all__ = ["WaterfallChartGenerator", "WaterfallComponent"]
