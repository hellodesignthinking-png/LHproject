"""
ZeroSite v23 - Tornado Chart Generator
=======================================

Generates visual tornado diagrams for sensitivity analysis results.

Author: ZeroSite Development Team
Date: 2025-12-10
Version: 1.0
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environment

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Korean font configuration
def setup_korean_font():
    """
    Configure matplotlib to support Korean characters
    """
    try:
        # Try to find Korean fonts
        korean_fonts = [
            'NanumGothic',
            'NanumBarunGothic', 
            'Malgun Gothic',
            'AppleGothic',
            'UnDotum'
        ]
        
        for font_name in korean_fonts:
            try:
                fm.FontProperties(family=font_name)
                plt.rcParams['font.family'] = font_name
                logger.info(f"✅ Korean font set: {font_name}")
                break
            except:
                continue
        else:
            logger.warning("⚠️ No Korean font found, using default")
            plt.rcParams['font.family'] = 'sans-serif'
        
        # Ensure minus sign displays correctly
        plt.rcParams['axes.unicode_minus'] = False
        
    except Exception as e:
        logger.error(f"❌ Font setup error: {str(e)}")
        plt.rcParams['font.family'] = 'sans-serif'


class TornadoChartGenerator:
    """
    Generates tornado diagrams for sensitivity analysis
    """
    
    def __init__(self):
        setup_korean_font()
        self.colors = {
            'negative': '#d32f2f',  # Red for negative impact
            'positive': '#2e7d32',  # Green for positive impact
            'neutral': '#7f8c8d'    # Gray for neutral
        }
    
    def generate_tornado_chart(
        self, 
        tornado_data: list, 
        output_path: str,
        title: str = "민감도 분석 - Tornado Diagram",
        base_profit: float = 0.0
    ) -> bool:
        """
        Generate tornado diagram from sensitivity data
        
        Args:
            tornado_data: List of dicts with 'variable', 'downside_eok', 'upside_eok', 'variability_eok'
            output_path: Path to save PNG file
            title: Chart title
            base_profit: Base scenario profit for reference line
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"📊 Generating tornado chart: {output_path}")
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Extract data
            variables = [item['variable'] for item in tornado_data]
            downside = [item['downside_eok'] for item in tornado_data]
            upside = [item['upside_eok'] for item in tornado_data]
            
            # Calculate positions
            y_pos = np.arange(len(variables))
            
            # Plot horizontal bars
            bars_down = ax.barh(
                y_pos, 
                downside, 
                align='center', 
                color=self.colors['negative'], 
                alpha=0.8, 
                label='음(−) 영향'
            )
            
            bars_up = ax.barh(
                y_pos, 
                upside, 
                align='center', 
                color=self.colors['positive'], 
                alpha=0.8, 
                label='양(+) 영향'
            )
            
            # Add value labels on bars
            for i, (bar_down, bar_up, down_val, up_val) in enumerate(zip(bars_down, bars_up, downside, upside)):
                # Downside label
                if abs(down_val) > 1:
                    ax.text(
                        down_val / 2, 
                        i, 
                        f'{down_val:.1f}억', 
                        ha='center', 
                        va='center', 
                        fontsize=9,
                        fontweight='bold',
                        color='white'
                    )
                
                # Upside label
                if abs(up_val) > 1:
                    ax.text(
                        up_val / 2, 
                        i, 
                        f'{up_val:+.1f}억', 
                        ha='center', 
                        va='center', 
                        fontsize=9,
                        fontweight='bold',
                        color='white'
                    )
            
            # Formatting
            ax.set_yticks(y_pos)
            ax.set_yticklabels(variables, fontsize=11, fontweight='600')
            ax.set_xlabel('수익 영향 (억원)', fontsize=12, fontweight='bold')
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Add vertical line at zero
            ax.axvline(x=0, color='black', linewidth=1.5, linestyle='-', alpha=0.8)
            
            # Add vertical line at base profit (if provided)
            if base_profit != 0:
                ax.axvline(
                    x=base_profit, 
                    color='#ff9800', 
                    linewidth=1.5, 
                    linestyle='--', 
                    alpha=0.6,
                    label=f'기준 시나리오 ({base_profit:.1f}억)'
                )
            
            # Legend
            ax.legend(loc='best', fontsize=10, framealpha=0.9)
            
            # Grid
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            
            # Set x-axis limits with padding
            all_values = downside + upside
            x_min = min(all_values) * 1.2
            x_max = max(all_values) * 1.2
            ax.set_xlim(x_min, x_max)
            
            # Tight layout
            plt.tight_layout()
            
            # Save figure
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"✅ Tornado chart saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate tornado chart: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_profit_distribution_chart(
        self,
        scenarios: list,
        output_path: str,
        title: str = "시나리오별 수익 분포"
    ) -> bool:
        """
        Generate bar chart showing profit distribution across scenarios
        
        Args:
            scenarios: List of scenario dicts with 'scenario_name', 'profit_eok', 'is_base'
            output_path: Path to save PNG file
            title: Chart title
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"📊 Generating profit distribution chart: {output_path}")
            
            # Create figure
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Extract data
            scenario_names = [s['scenario_name'] for s in scenarios]
            profits = [s['profit_eok'] for s in scenarios]
            
            # Color based on profit (green for positive, red for negative)
            colors = [self.colors['positive'] if p >= 0 else self.colors['negative'] for p in profits]
            
            # Create bars
            bars = ax.bar(range(len(scenario_names)), profits, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
            
            # Highlight base scenario with thick border
            base_idx = next((i for i, s in enumerate(scenarios) if s.get('is_base', False)), None)
            if base_idx is not None:
                bars[base_idx].set_edgecolor('black')
                bars[base_idx].set_linewidth(3)
                bars[base_idx].set_alpha(1.0)
            
            # Add value labels on bars
            for i, (bar, profit) in enumerate(zip(bars, profits)):
                height = bar.get_height()
                label_y = height + (2 if height >= 0 else -5)
                va = 'bottom' if height >= 0 else 'top'
                
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    label_y,
                    f'{profit:.1f}억',
                    ha='center',
                    va=va,
                    fontsize=9,
                    fontweight='bold'
                )
            
            # Formatting
            ax.set_xticks(range(len(scenario_names)))
            ax.set_xticklabels(scenario_names, rotation=45, ha='right', fontsize=9)
            ax.set_ylabel('수익 (억원)', fontsize=12, fontweight='bold')
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Add horizontal line at zero
            ax.axhline(y=0, color='black', linewidth=1.5, linestyle='-', alpha=0.8)
            
            # Grid
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Add legend for base scenario
            if base_idx is not None:
                from matplotlib.patches import Rectangle
                base_patch = Rectangle((0, 0), 1, 1, fc='white', ec='black', linewidth=3, label='기준 시나리오')
                ax.legend(handles=[base_patch], loc='best', fontsize=10)
            
            # Tight layout
            plt.tight_layout()
            
            # Save figure
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"✅ Profit distribution chart saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate profit distribution chart: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


# Convenience functions
def generate_tornado_chart(tornado_data, output_path, title=None, base_profit=0.0):
    """Generate tornado chart (convenience function)"""
    generator = TornadoChartGenerator()
    return generator.generate_tornado_chart(tornado_data, output_path, title or "민감도 분석 - Tornado Diagram", base_profit)


def generate_profit_distribution_chart(scenarios, output_path, title=None):
    """Generate profit distribution chart (convenience function)"""
    generator = TornadoChartGenerator()
    return generator.generate_profit_distribution_chart(scenarios, output_path, title or "시나리오별 수익 분포")


# Test function
if __name__ == "__main__":
    # Test data
    test_tornado_data = [
        {
            'variable': 'CAPEX (±10%)',
            'downside_eok': 30.00,
            'upside_eok': -30.00,
            'variability_eok': 60.00
        },
        {
            'variable': '감정평가율 (±5%)',
            'downside_eok': -11.13,
            'upside_eok': 11.13,
            'variability_eok': 22.26
        }
    ]
    
    test_scenarios = [
        {'scenario_name': 'CAPEX -10%, 평가율 -5%', 'profit_eok': 18.51, 'is_base': False},
        {'scenario_name': 'CAPEX -10%, 평가율 +0%', 'profit_eok': 29.64, 'is_base': False},
        {'scenario_name': 'CAPEX -10%, 평가율 +5%', 'profit_eok': 40.77, 'is_base': False},
        {'scenario_name': 'CAPEX +0%, 평가율 -5%', 'profit_eok': -11.49, 'is_base': False},
        {'scenario_name': 'Base (기준)', 'profit_eok': -0.36, 'is_base': True},
        {'scenario_name': 'CAPEX +0%, 평가율 +5%', 'profit_eok': 10.77, 'is_base': False},
        {'scenario_name': 'CAPEX +10%, 평가율 -5%', 'profit_eok': -41.49, 'is_base': False},
        {'scenario_name': 'CAPEX +10%, 평가율 +0%', 'profit_eok': -30.36, 'is_base': False},
        {'scenario_name': 'CAPEX +10%, 평가율 +5%', 'profit_eok': -19.23, 'is_base': False}
    ]
    
    print("Testing Tornado Chart Generator...")
    
    # Test tornado chart
    success1 = generate_tornado_chart(
        test_tornado_data,
        '/home/user/webapp/test_tornado.png',
        base_profit=-0.36
    )
    print(f"Tornado chart: {'✅ SUCCESS' if success1 else '❌ FAILED'}")
    
    # Test profit distribution
    success2 = generate_profit_distribution_chart(
        test_scenarios,
        '/home/user/webapp/test_profit_distribution.png'
    )
    print(f"Profit distribution: {'✅ SUCCESS' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n✅ All tests passed!")
        print("Generated files:")
        print("  - /home/user/webapp/test_tornado.png")
        print("  - /home/user/webapp/test_profit_distribution.png")
