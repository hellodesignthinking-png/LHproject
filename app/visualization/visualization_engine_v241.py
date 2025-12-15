"""
ZeroSite v24.1 - Complete Visualization Engine
All 6 chart types for professional reports

Author: ZeroSite Development Team
Version: v24.1.1
Created: 2025-12-12
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np
import seaborn as sns
from typing import Dict, Any, List, Tuple
import io
import base64
from dataclasses import dataclass


# Korean font setup
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


@dataclass
class ChartConfig:
    """Chart configuration"""
    figsize: Tuple[int, int] = (10, 6)
    dpi: int = 100
    style: str = 'seaborn-v0_8-whitegrid'
    primary_color: str = '#005BAC'  # LH Blue
    secondary_color: str = '#FF7A00'  # ZeroSite Orange
    background_color: str = '#F7F9FB'  # ZeroSite White


class VisualizationEngineV241:
    """Complete visualization engine for all 6 chart types"""
    
    def __init__(self, config: ChartConfig = None):
        self.config = config or ChartConfig()
    
    def generate_all_charts(self, 
                           capacity_data: Dict[str, Any],
                           market_data: Dict[str, Any],
                           financial_data: Dict[str, Any],
                           risk_data: Dict[str, Any],
                           scenario_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all 6 chart types
        
        Returns:
            Dict of chart_name -> base64_image
        """
        charts = {}
        
        charts['capacity_chart'] = self.generate_capacity_chart(capacity_data)
        charts['market_histogram'] = self.generate_market_histogram(market_data)
        charts['financial_waterfall'] = self.generate_financial_waterfall(financial_data)
        charts['risk_heatmap'] = self.generate_risk_heatmap(risk_data)
        charts['far_comparison'] = self.generate_far_comparison(scenario_data)
        charts['type_distribution'] = self.generate_type_distribution(capacity_data)
        
        return charts
    
    def generate_capacity_chart(self, data: Dict[str, Any]) -> str:
        """
        Chart 1: Capacity Analysis Chart
        Shows: Total area, floors, units, parking
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Capacity Analysis', fontsize=16, fontweight='bold')
        
        # 1. Total Area Bar Chart
        areas = {
            'Total Area': data.get('total_area', 0),
            'Residential': data.get('residential_area', 0),
            'Commercial': data.get('commercial_area', 0),
            'Parking': data.get('parking_area', 0)
        }
        ax1.bar(areas.keys(), areas.values(), color=self.config.primary_color, alpha=0.7)
        ax1.set_ylabel('Area (sqm)')
        ax1.set_title('Area Distribution')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels
        for i, (key, val) in enumerate(areas.items()):
            ax1.text(i, val, f'{val:,.0f}', ha='center', va='bottom')
        
        # 2. Floors vs Units
        floors = data.get('floors', 0)
        units = data.get('total_units', 0)
        x = ['Floors', 'Units']
        y = [floors, units]
        bars = ax2.bar(x, y, color=[self.config.primary_color, self.config.secondary_color], alpha=0.7)
        ax2.set_title('Building Scale')
        ax2.set_ylabel('Count')
        ax2.grid(True, alpha=0.3)
        
        for bar, val in zip(bars, y):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val}', ha='center', va='bottom')
        
        # 3. Unit Type Distribution (Pie Chart)
        unit_types = {
            'Youth': data.get('youth_units', 0),
            'Newlywed': data.get('newlywed_units', 0),
            'General': data.get('general_units', 0)
        }
        colors = [self.config.primary_color, self.config.secondary_color, '#00C853']
        wedges, texts, autotexts = ax3.pie(unit_types.values(), labels=unit_types.keys(),
                                           autopct='%1.1f%%', colors=colors, startangle=90)
        ax3.set_title('Unit Type Distribution')
        
        # 4. FAR Utilization
        legal_far = data.get('legal_far', 200)
        relaxed_far = data.get('relaxed_far', 250)
        final_far = data.get('final_far', 240)
        
        x_pos = np.arange(3)
        fars = [legal_far, relaxed_far, final_far]
        labels = ['Legal FAR', 'Relaxed FAR', 'Final FAR']
        bars = ax4.bar(x_pos, fars, color=[self.config.primary_color, 
                                          self.config.secondary_color, '#00C853'], alpha=0.7)
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(labels)
        ax4.set_ylabel('FAR (%)')
        ax4.set_title('FAR Comparison')
        ax4.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, fars):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val}%', ha='center', va='bottom')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def generate_market_histogram(self, data: Dict[str, Any]) -> str:
        """
        Chart 2: Market Price Histogram
        Shows: Transaction price distribution
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Market Analysis', fontsize=16, fontweight='bold')
        
        # 1. Price Histogram
        transactions = data.get('transactions', [])
        if transactions:
            prices = [t.get('price_per_sqm', 0) for t in transactions]
        else:
            # Generate sample data for demonstration
            prices = np.random.normal(3000000, 500000, 100)
        
        ax1.hist(prices, bins=20, color=self.config.primary_color, alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Price per sqm (KRW)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Transaction Price Distribution')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add statistical lines
        mean_price = np.mean(prices)
        median_price = np.median(prices)
        ax1.axvline(mean_price, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_price:,.0f}')
        ax1.axvline(median_price, color='green', linestyle='--', linewidth=2, label=f'Median: {median_price:,.0f}')
        ax1.legend()
        
        # 2. Price Trend (Time Series)
        dates = data.get('dates', list(range(12)))
        avg_prices = data.get('avg_prices', np.linspace(2800000, 3200000, 12))
        
        ax2.plot(dates, avg_prices, marker='o', linewidth=2, 
                color=self.config.primary_color, markersize=6)
        ax2.fill_between(dates, avg_prices, alpha=0.3, color=self.config.primary_color)
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Avg Price per sqm (KRW)')
        ax2.set_title('Price Trend (Last 12 Months)')
        ax2.grid(True, alpha=0.3)
        
        # Format y-axis
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def generate_financial_waterfall(self, data: Dict[str, Any]) -> str:
        """
        Chart 3: Financial Waterfall Chart
        Shows: Revenue breakdown and cost structure
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Waterfall components
        categories = ['Revenue', 'Land Cost', 'Construction', 'Indirect', 'Financing', 'Net Profit']
        values = [
            data.get('total_revenue', 4500),
            -data.get('land_cost', 1500),
            -data.get('construction_cost', 1800),
            -data.get('indirect_cost', 400),
            -data.get('financing_cost', 300),
            data.get('net_profit', 500)
        ]
        
        # Calculate cumulative values
        cumulative = [0]
        for val in values[:-1]:
            cumulative.append(cumulative[-1] + val)
        
        # Colors: green for positive, red for negative, blue for final
        colors = []
        for i, val in enumerate(values):
            if i == 0:
                colors.append('#00C853')  # Revenue green
            elif i == len(values) - 1:
                colors.append(self.config.primary_color)  # Net profit blue
            else:
                colors.append('#FF5252')  # Costs red
        
        # Draw waterfall
        x_pos = np.arange(len(categories))
        for i, (cat, val) in enumerate(zip(categories, values)):
            if i == 0:
                # First bar starts from 0
                ax.bar(i, val, color=colors[i], alpha=0.7, edgecolor='black')
                ax.text(i, val/2, f'{val:,.0f}M', ha='center', va='center', fontweight='bold')
            elif i == len(categories) - 1:
                # Last bar (net profit)
                ax.bar(i, cumulative[i], bottom=0, color=colors[i], alpha=0.7, edgecolor='black')
                ax.text(i, cumulative[i]/2, f'{cumulative[i]:,.0f}M', 
                       ha='center', va='center', fontweight='bold', color='white')
            else:
                # Intermediate bars
                ax.bar(i, abs(val), bottom=cumulative[i], color=colors[i], 
                      alpha=0.7, edgecolor='black')
                ax.text(i, cumulative[i] + abs(val)/2, f'{abs(val):,.0f}M',
                       ha='center', va='center', fontweight='bold')
                
                # Connection line
                if i > 0:
                    ax.plot([i-0.5, i-0.5], [cumulative[i-1], cumulative[i]], 
                           'k--', alpha=0.5, linewidth=1)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories, rotation=15, ha='right')
        ax.set_ylabel('Amount (Million KRW)')
        ax.set_title('Financial Waterfall Analysis', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(0, color='black', linewidth=0.8)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def generate_risk_heatmap(self, data: Dict[str, Any]) -> str:
        """
        Chart 4: Risk Assessment Heatmap
        Shows: 5 risk categories with severity levels
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Risk categories and scores (0-1 scale)
        risk_categories = ['Financial', 'Market', 'Policy', 'Design', 'Legal']
        risk_scores = [
            data.get('financial_risk', 0.45),
            data.get('market_risk', 0.25),
            data.get('policy_risk', 0.20),
            data.get('design_risk', 0.35),
            data.get('legal_risk', 0.15)
        ]
        
        # Create matrix for heatmap (5 categories x 3 severity levels)
        risk_matrix = np.zeros((5, 3))
        for i, score in enumerate(risk_scores):
            if score < 0.33:
                risk_matrix[i, 0] = score * 3  # Low
            elif score < 0.67:
                risk_matrix[i, 1] = (score - 0.33) * 3  # Medium
            else:
                risk_matrix[i, 2] = (score - 0.67) * 3  # High
        
        # Plot heatmap
        im = ax.imshow(risk_matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=1)
        
        # Set ticks and labels
        ax.set_xticks(np.arange(3))
        ax.set_yticks(np.arange(5))
        ax.set_xticklabels(['Low', 'Medium', 'High'])
        ax.set_yticklabels(risk_categories)
        
        # Add risk scores as text
        for i in range(5):
            for j in range(3):
                text_color = 'white' if risk_matrix[i, j] > 0.5 else 'black'
                ax.text(j, i, f'{risk_matrix[i, j]:.2f}',
                       ha='center', va='center', color=text_color, fontweight='bold')
        
        # Add overall risk score
        overall_risk = np.mean(risk_scores)
        risk_level = 'Low' if overall_risk < 0.33 else ('Medium' if overall_risk < 0.67 else 'High')
        
        ax.set_title(f'Risk Assessment Heatmap\\nOverall Risk: {risk_level} ({overall_risk:.2%})',
                    fontsize=14, fontweight='bold')
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Risk Intensity', rotation=270, labelpad=20)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def generate_far_comparison(self, data: Dict[str, Any]) -> str:
        """
        Chart 5: FAR Comparison Chart (Scenario A/B/C)
        Shows: FAR comparison across different scenarios
        """
        fig, ax = plt.subplots(figsize=(12, 7))
        
        scenarios = data.get('scenarios', ['Scenario A', 'Scenario B', 'Scenario C'])
        far_values = data.get('far_values', [200, 240, 220])
        units = data.get('units', [45, 53, 48])
        roi = data.get('roi', [15.2, 18.5, 16.8])
        
        x = np.arange(len(scenarios))
        width = 0.25
        
        # Three bars per scenario
        bars1 = ax.bar(x - width, far_values, width, label='FAR (%)', 
                      color=self.config.primary_color, alpha=0.7)
        bars2 = ax.bar(x, units, width, label='Units',
                      color=self.config.secondary_color, alpha=0.7)
        bars3 = ax.bar(x + width, roi, width, label='ROI (%)',
                      color='#00C853', alpha=0.7)
        
        # Add value labels
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('Scenarios')
        ax.set_ylabel('Values')
        ax.set_title('Scenario Comparison: FAR, Units, ROI', 
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def generate_type_distribution(self, data: Dict[str, Any]) -> str:
        """
        Chart 6: Unit Type Distribution Chart
        Shows: Distribution of youth/newlywed/general units
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Unit Type Distribution', fontsize=16, fontweight='bold')
        
        # 1. Donut Chart
        unit_types = {
            'Youth': data.get('youth_units', 16),
            'Newlywed': data.get('newlywed_units', 27),
            'General': data.get('general_units', 10)
        }
        
        colors = [self.config.primary_color, self.config.secondary_color, '#00C853']
        wedges, texts, autotexts = ax1.pie(unit_types.values(), labels=unit_types.keys(),
                                           autopct='%1.1f%%', colors=colors, startangle=90,
                                           wedgeprops=dict(width=0.5))
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax1.set_title('Unit Type Proportion')
        
        # 2. Horizontal Bar Chart with Details
        types = list(unit_types.keys())
        counts = list(unit_types.values())
        areas = [data.get(f'{t.lower()}_avg_area', 60) for t in types]
        
        y_pos = np.arange(len(types))
        bars = ax2.barh(y_pos, counts, color=colors, alpha=0.7)
        
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(types)
        ax2.set_xlabel('Number of Units')
        ax2.set_title('Unit Count by Type')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add count and area labels
        for i, (bar, count, area) in enumerate(zip(bars, counts, areas)):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2.,
                    f' {count} units ({area}㎡)',
                    ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=self.config.dpi, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_base64


# Convenience function
def generate_all_visualizations(capacity_data, market_data, financial_data,
                               risk_data, scenario_data) -> Dict[str, str]:
    """
    Generate all 6 chart types in one call
    
    Returns:
        Dict of chart_name -> base64_image
    """
    engine = VisualizationEngineV241()
    return engine.generate_all_charts(
        capacity_data, market_data, financial_data, 
        risk_data, scenario_data
    )
