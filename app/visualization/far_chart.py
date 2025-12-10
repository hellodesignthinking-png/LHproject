"""
ZeroSite v23 - FAR Change Visualization
=======================================
Professional FAR (Floor Area Ratio) comparison chart for A/B scenarios

Generates dual-scenario FAR comparison charts showing:
- Legal FAR (base)
- Final FAR (after relaxation)
- Visual comparison between Scenario A and Scenario B
- LH official color scheme

Author: ZeroSite v23 Development Team
Version: 23.0.0
Date: 2025-12-10
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle
import numpy as np
from typing import Tuple, Optional
import base64
from io import BytesIO
import os


class FARChartGenerator:
    """
    FAR Change Chart Generator for ZeroSite v23
    
    Creates professional bar charts comparing FAR values across scenarios
    with LH official color scheme.
    """
    
    # LH Official Colors
    LH_BLUE = '#005BAC'
    LH_ORANGE = '#FF7A00'
    LH_GRAY = '#6C757D'
    LH_LIGHT_BLUE = '#4A90E2'
    LH_LIGHT_GRAY = '#E9ECEF'
    
    def __init__(self):
        """Initialize the FAR Chart Generator"""
        self._setup_korean_font()
    
    def _setup_korean_font(self):
        """Setup Korean font for matplotlib"""
        try:
            # Try to find available Korean fonts
            korean_fonts = [
                'NanumGothic',
                'NanumBarunGothic', 
                'Malgun Gothic',
                'AppleGothic',
                'DejaVu Sans'
            ]
            
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            
            for font in korean_fonts:
                if font in available_fonts:
                    plt.rcParams['font.family'] = font
                    plt.rcParams['axes.unicode_minus'] = False
                    return
            
            # Fallback
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['axes.unicode_minus'] = False
            
        except Exception as e:
            print(f"Warning: Could not setup Korean font: {e}")
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['axes.unicode_minus'] = False
    
    def generate_far_comparison_chart(
        self,
        scenario_a_legal: float,
        scenario_a_final: float,
        scenario_b_legal: float,
        scenario_b_final: float,
        scenario_a_label: str = "청년",
        scenario_b_label: str = "신혼부부",
        output_path: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate FAR comparison chart for two scenarios
        
        Args:
            scenario_a_legal: Scenario A legal FAR (%)
            scenario_a_final: Scenario A final FAR after relaxation (%)
            scenario_b_legal: Scenario B legal FAR (%)
            scenario_b_final: Scenario B final FAR after relaxation (%)
            scenario_a_label: Label for Scenario A (default: 청년)
            scenario_b_label: Label for Scenario B (default: 신혼부부)
            output_path: Optional file path to save PNG
        
        Returns:
            Tuple of (base64_string, file_path)
        """
        # Create figure and axis (v23.1: Enhanced DPI)
        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        
        # Data
        scenarios = [f'시나리오 A\n({scenario_a_label})', f'시나리오 B\n({scenario_b_label})']
        legal_fars = [scenario_a_legal, scenario_b_legal]
        final_fars = [scenario_a_final, scenario_b_final]
        
        # X positions
        x = np.arange(len(scenarios))
        width = 0.35
        
        # Create bars
        bars1 = ax.bar(
            x - width/2, 
            legal_fars, 
            width, 
            label='법정 용적률',
            color=self.LH_GRAY,
            alpha=0.8,
            edgecolor='white',
            linewidth=1.5
        )
        
        bars2 = ax.bar(
            x + width/2, 
            final_fars, 
            width,
            label='완화 후 용적률',
            color=[self.LH_BLUE, self.LH_ORANGE],
            alpha=0.9,
            edgecolor='white',
            linewidth=1.5
        )
        
        # Add value labels on bars
        for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
            height1 = bar1.get_height()
            height2 = bar2.get_height()
            
            # Legal FAR label
            ax.text(
                bar1.get_x() + bar1.get_width()/2., 
                height1,
                f'{height1:.0f}%',
                ha='center', 
                va='bottom',
                fontsize=11,
                fontweight='bold',
                color=self.LH_GRAY
            )
            
            # Final FAR label
            ax.text(
                bar2.get_x() + bar2.get_width()/2., 
                height2,
                f'{height2:.0f}%',
                ha='center', 
                va='bottom',
                fontsize=11,
                fontweight='bold',
                color=self.LH_BLUE if i == 0 else self.LH_ORANGE
            )
            
            # Relaxation amount (v23.1: Enhanced with box)
            relaxation = final_fars[i] - legal_fars[i]
            if relaxation > 0:
                ax.text(
                    bar2.get_x() + bar2.get_width()/2.,
                    height2 + 5,
                    f'(+{relaxation:.0f}%p)',
                    ha='center',
                    va='bottom',
                    fontsize=10,
                    fontweight='bold',
                    color=self.LH_BLUE if i == 0 else self.LH_ORANGE,
                    bbox=dict(
                        boxstyle='round,pad=0.5',
                        facecolor='#FFF3CD',
                        edgecolor=self.LH_BLUE if i == 0 else self.LH_ORANGE,
                        linewidth=2,
                        alpha=0.9
                    )
                )
        
        # Styling
        ax.set_xlabel('시나리오', fontsize=12, fontweight='bold', color='#333333')
        ax.set_ylabel('용적률 (%)', fontsize=12, fontweight='bold', color='#333333')
        ax.set_title(
            'A/B 시나리오 용적률 비교',
            fontsize=14,
            fontweight='bold',
            color='#333333',
            pad=20
        )
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios, fontsize=11)
        ax.legend(
            loc='upper left',
            fontsize=10,
            framealpha=0.95,
            edgecolor=self.LH_GRAY
        )
        
        # Grid
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.7)
        ax.set_axisbelow(True)
        
        # Y-axis limit (add 20% padding)
        max_far = max(final_fars)
        ax.set_ylim(0, max_far * 1.2)
        
        # Background color
        ax.set_facecolor('#FAFAFA')
        fig.patch.set_facecolor('white')
        
        # Tight layout
        plt.tight_layout()
        
        # Save to buffer for base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        base64_string = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            plt.savefig(output_path, format='png', dpi=150, bbox_inches='tight')
            file_path = output_path
        else:
            file_path = None
        
        plt.close(fig)
        
        return base64_string, file_path
    
    def generate_far_change_arrow_chart(
        self,
        scenario_a_legal: float,
        scenario_a_final: float,
        scenario_b_legal: float,
        scenario_b_final: float,
        scenario_a_label: str = "청년",
        scenario_b_label: str = "신혼부부",
        output_path: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate FAR change chart with arrows showing transformation
        
        Args:
            scenario_a_legal: Scenario A legal FAR (%)
            scenario_a_final: Scenario A final FAR after relaxation (%)
            scenario_b_legal: Scenario B legal FAR (%)
            scenario_b_final: Scenario B final FAR after relaxation (%)
            scenario_a_label: Label for Scenario A
            scenario_b_label: Label for Scenario B
            output_path: Optional file path to save PNG
        
        Returns:
            Tuple of (base64_string, file_path)
        """
        fig, ax = plt.subplots(figsize=(12, 5), dpi=100)
        
        # Data
        y_positions = [1, 0]
        labels = [f'시나리오 A ({scenario_a_label})', f'시나리오 B ({scenario_b_label})']
        legal_values = [scenario_a_legal, scenario_b_legal]
        final_values = [scenario_a_final, scenario_b_final]
        colors = [self.LH_BLUE, self.LH_ORANGE]
        
        # Draw arrows and values
        for i, (y_pos, label, legal, final, color) in enumerate(
            zip(y_positions, labels, legal_values, final_values, colors)
        ):
            # Legal FAR point
            ax.plot(legal, y_pos, 'o', color=self.LH_GRAY, markersize=15, zorder=3)
            ax.text(
                legal, y_pos + 0.15, 
                f'{legal:.0f}%',
                ha='center', va='bottom',
                fontsize=11, fontweight='bold',
                color=self.LH_GRAY
            )
            
            # Arrow
            ax.annotate(
                '',
                xy=(final, y_pos),
                xytext=(legal, y_pos),
                arrowprops=dict(
                    arrowstyle='->',
                    lw=3,
                    color=color,
                    alpha=0.7
                ),
                zorder=2
            )
            
            # Final FAR point
            ax.plot(final, y_pos, 'o', color=color, markersize=15, zorder=3)
            ax.text(
                final, y_pos + 0.15,
                f'{final:.0f}%',
                ha='center', va='bottom',
                fontsize=11, fontweight='bold',
                color=color
            )
            
            # Relaxation label
            relaxation = final - legal
            mid_x = (legal + final) / 2
            ax.text(
                mid_x, y_pos - 0.15,
                f'+{relaxation:.0f}%p',
                ha='center', va='top',
                fontsize=10,
                color=color,
                style='italic',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, alpha=0.8)
            )
            
            # Scenario label
            ax.text(
                legal - 10, y_pos,
                label,
                ha='right', va='center',
                fontsize=12, fontweight='bold',
                color='#333333'
            )
        
        # Styling
        ax.set_xlim(min(legal_values) - 30, max(final_values) + 30)
        ax.set_ylim(-0.5, 1.5)
        ax.set_xlabel('용적률 (%)', fontsize=12, fontweight='bold', color='#333333')
        ax.set_title(
            'A/B 시나리오 용적률 변화',
            fontsize=14,
            fontweight='bold',
            color='#333333',
            pad=20
        )
        
        # Remove y-axis
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
        # Grid
        ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.7)
        ax.set_axisbelow(True)
        
        # Background
        ax.set_facecolor('#FAFAFA')
        fig.patch.set_facecolor('white')
        
        plt.tight_layout()
        
        # Save to buffer for base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        base64_string = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            plt.savefig(output_path, format='png', dpi=150, bbox_inches='tight')
            file_path = output_path
        else:
            file_path = None
        
        plt.close(fig)
        
        return base64_string, file_path


def main():
    """Test the FAR Chart Generator"""
    generator = FARChartGenerator()
    
    print("=" * 80)
    print("ZeroSite v23 - FAR Chart Generator Test")
    print("=" * 80)
    
    # Test data
    scenario_a_legal = 200.0
    scenario_a_final = 240.0
    scenario_b_legal = 200.0
    scenario_b_final = 220.0
    
    print("\n📊 Generating FAR Comparison Chart...")
    base64_comparison, path_comparison = generator.generate_far_comparison_chart(
        scenario_a_legal=scenario_a_legal,
        scenario_a_final=scenario_a_final,
        scenario_b_legal=scenario_b_legal,
        scenario_b_final=scenario_b_final,
        output_path='far_comparison_chart.png'
    )
    print(f"✅ Comparison chart generated")
    print(f"   Base64 length: {len(base64_comparison)} characters")
    print(f"   File saved: far_comparison_chart.png")
    
    print("\n📊 Generating FAR Change Arrow Chart...")
    base64_arrow, path_arrow = generator.generate_far_change_arrow_chart(
        scenario_a_legal=scenario_a_legal,
        scenario_a_final=scenario_a_final,
        scenario_b_legal=scenario_b_legal,
        scenario_b_final=scenario_b_final,
        output_path='far_arrow_chart.png'
    )
    print(f"✅ Arrow chart generated")
    print(f"   Base64 length: {len(base64_arrow)} characters")
    print(f"   File saved: far_arrow_chart.png")
    
    print("\n" + "=" * 80)
    print("✅ All tests completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
