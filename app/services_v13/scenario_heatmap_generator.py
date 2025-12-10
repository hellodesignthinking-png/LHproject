"""
ZeroSite v23 - Scenario Heatmap Generator
=========================================

Generates 3×3 heatmap visualizations for sensitivity analysis scenarios.

Author: ZeroSite Development Team
Date: 2025-12-10
Version: 1.0
"""

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Korean font setup (same as tornado chart)
def setup_korean_font():
    """Configure matplotlib to support Korean characters"""
    try:
        korean_fonts = ['NanumGothic', 'NanumBarunGothic', 'Malgun Gothic', 'AppleGothic', 'UnDotum']
        for font_name in korean_fonts:
            try:
                fm.FontProperties(family=font_name)
                plt.rcParams['font.family'] = font_name
                logger.info(f"✅ Korean font set: {font_name}")
                break
            except:
                continue
        else:
            plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False
    except Exception as e:
        logger.error(f"❌ Font setup error: {str(e)}")
        plt.rcParams['font.family'] = 'sans-serif'


class ScenarioHeatmapGenerator:
    """
    Generates heatmap visualizations for sensitivity analysis
    """
    
    def __init__(self):
        setup_korean_font()
    
    def generate_profit_heatmap(
        self,
        scenarios: list,
        output_path: str,
        title: str = "수익 Heatmap - 9 Scenarios"
    ) -> bool:
        """
        Generate 3×3 heatmap of profit scenarios
        
        Args:
            scenarios: List of scenario dicts with 'capex_eok', 'appraisal_rate', 'profit_eok'
            output_path: Path to save PNG file
            title: Chart title
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"📊 Generating profit heatmap: {output_path}")
            
            # Extract unique CAPEX and appraisal rate levels
            capex_levels = sorted(set(s['capex_eok'] for s in scenarios))
            appraisal_levels = sorted(set(s['appraisal_rate'] for s in scenarios))
            
            # Create 3×3 matrix
            profit_matrix = np.zeros((len(capex_levels), len(appraisal_levels)))
            
            for s in scenarios:
                i = capex_levels.index(s['capex_eok'])
                j = appraisal_levels.index(s['appraisal_rate'])
                profit_matrix[i, j] = s['profit_eok']
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create heatmap
            sns.heatmap(
                profit_matrix,
                annot=True,
                fmt='.1f',
                cmap='RdYlGn',
                center=0,
                cbar_kws={'label': '수익 (억원)', 'shrink': 0.8},
                xticklabels=[f"{int(r*100)}%" for r in appraisal_levels],
                yticklabels=[f"{int(c)}억" for c in capex_levels],
                linewidths=1,
                linecolor='white',
                annot_kws={'fontsize': 12, 'fontweight': 'bold'},
                ax=ax
            )
            
            # Formatting
            ax.set_xlabel('감정평가율 (%)', fontsize=12, fontweight='bold')
            ax.set_ylabel('CAPEX (억원)', fontsize=12, fontweight='bold')
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Rotate labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
            plt.setp(ax.get_yticklabels(), rotation=0)
            
            # Tight layout
            plt.tight_layout()
            
            # Save
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"✅ Profit heatmap saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate profit heatmap: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_roi_heatmap(
        self,
        scenarios: list,
        output_path: str,
        title: str = "ROI Heatmap - 9 Scenarios"
    ) -> bool:
        """
        Generate 3×3 heatmap of ROI scenarios
        
        Args:
            scenarios: List of scenario dicts with 'capex_eok', 'appraisal_rate', 'roi_pct'
            output_path: Path to save PNG file
            title: Chart title
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"📊 Generating ROI heatmap: {output_path}")
            
            # Extract unique levels
            capex_levels = sorted(set(s['capex_eok'] for s in scenarios))
            appraisal_levels = sorted(set(s['appraisal_rate'] for s in scenarios))
            
            # Create matrix
            roi_matrix = np.zeros((len(capex_levels), len(appraisal_levels)))
            
            for s in scenarios:
                i = capex_levels.index(s['capex_eok'])
                j = appraisal_levels.index(s['appraisal_rate'])
                roi_matrix[i, j] = s['roi_pct']
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create heatmap
            sns.heatmap(
                roi_matrix,
                annot=True,
                fmt='.2f',
                cmap='RdYlGn',
                center=0,
                cbar_kws={'label': 'ROI (%)', 'shrink': 0.8},
                xticklabels=[f"{int(r*100)}%" for r in appraisal_levels],
                yticklabels=[f"{int(c)}억" for c in capex_levels],
                linewidths=1,
                linecolor='white',
                annot_kws={'fontsize': 12, 'fontweight': 'bold'},
                ax=ax
            )
            
            # Formatting
            ax.set_xlabel('감정평가율 (%)', fontsize=12, fontweight='bold')
            ax.set_ylabel('CAPEX (억원)', fontsize=12, fontweight='bold')
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
            plt.setp(ax.get_yticklabels(), rotation=0)
            
            plt.tight_layout()
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"✅ ROI heatmap saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate ROI heatmap: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_decision_heatmap(
        self,
        scenarios: list,
        output_path: str,
        title: str = "의사결정 Heatmap - 9 Scenarios"
    ) -> bool:
        """
        Generate 3×3 heatmap showing GO/NO-GO decisions
        
        Args:
            scenarios: List of scenario dicts with 'capex_eok', 'appraisal_rate', 'decision'
            output_path: Path to save PNG file
            title: Chart title
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"📊 Generating decision heatmap: {output_path}")
            
            # Extract unique levels
            capex_levels = sorted(set(s['capex_eok'] for s in scenarios))
            appraisal_levels = sorted(set(s['appraisal_rate'] for s in scenarios))
            
            # Create matrix (1 for GO, 0 for NO-GO)
            decision_matrix = np.zeros((len(capex_levels), len(appraisal_levels)))
            decision_labels = [['' for _ in range(len(appraisal_levels))] for _ in range(len(capex_levels))]
            
            for s in scenarios:
                i = capex_levels.index(s['capex_eok'])
                j = appraisal_levels.index(s['appraisal_rate'])
                
                # Set value: 2 for GO (Private), 1 for GO (Policy), 0 for NO-GO
                if 'GO (Private)' in s['decision']:
                    decision_matrix[i, j] = 2
                    decision_labels[i][j] = 'GO\n(Private)'
                elif 'GO (Policy)' in s['decision'] or 'GO' in s['decision']:
                    decision_matrix[i, j] = 1
                    decision_labels[i][j] = 'GO\n(Policy)'
                else:
                    decision_matrix[i, j] = 0
                    decision_labels[i][j] = 'NO-GO'
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Custom colormap: Red (NO-GO) -> Yellow (Policy) -> Green (Private)
            from matplotlib.colors import LinearSegmentedColormap
            colors = ['#d32f2f', '#ffd54f', '#2e7d32']
            n_bins = 3
            cmap = LinearSegmentedColormap.from_list('decision_cmap', colors, N=n_bins)
            
            # Create heatmap
            sns.heatmap(
                decision_matrix,
                annot=np.array(decision_labels),
                fmt='',
                cmap=cmap,
                cbar_kws={'label': '의사결정', 'ticks': [0.33, 1, 1.67], 'shrink': 0.8},
                xticklabels=[f"{int(r*100)}%" for r in appraisal_levels],
                yticklabels=[f"{int(c)}억" for c in capex_levels],
                linewidths=2,
                linecolor='white',
                annot_kws={'fontsize': 11, 'fontweight': 'bold'},
                vmin=0,
                vmax=2,
                ax=ax
            )
            
            # Update colorbar labels
            colorbar = ax.collections[0].colorbar
            colorbar.set_ticks([0.33, 1, 1.67])
            colorbar.set_ticklabels(['NO-GO', 'GO (Policy)', 'GO (Private)'])
            
            # Formatting
            ax.set_xlabel('감정평가율 (%)', fontsize=12, fontweight='bold')
            ax.set_ylabel('CAPEX (억원)', fontsize=12, fontweight='bold')
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
            plt.setp(ax.get_yticklabels(), rotation=0)
            
            plt.tight_layout()
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"✅ Decision heatmap saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate decision heatmap: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


# Convenience functions
def generate_profit_heatmap(scenarios, output_path, title=None):
    """Generate profit heatmap (convenience function)"""
    generator = ScenarioHeatmapGenerator()
    return generator.generate_profit_heatmap(scenarios, output_path, title or "수익 Heatmap - 9 Scenarios")


def generate_roi_heatmap(scenarios, output_path, title=None):
    """Generate ROI heatmap (convenience function)"""
    generator = ScenarioHeatmapGenerator()
    return generator.generate_roi_heatmap(scenarios, output_path, title or "ROI Heatmap - 9 Scenarios")


def generate_decision_heatmap(scenarios, output_path, title=None):
    """Generate decision heatmap (convenience function)"""
    generator = ScenarioHeatmapGenerator()
    return generator.generate_decision_heatmap(scenarios, output_path, title or "의사결정 Heatmap - 9 Scenarios")


# Test function
if __name__ == "__main__":
    # Test data
    test_scenarios = [
        {'capex_eok': 270.0, 'appraisal_rate': 0.87, 'profit_eok': 18.51, 'roi_pct': 6.85, 'decision': 'GO (Policy)'},
        {'capex_eok': 270.0, 'appraisal_rate': 0.92, 'profit_eok': 29.64, 'roi_pct': 10.98, 'decision': 'GO (Policy)'},
        {'capex_eok': 270.0, 'appraisal_rate': 0.97, 'profit_eok': 40.77, 'roi_pct': 15.10, 'decision': 'GO (Policy)'},
        {'capex_eok': 300.0, 'appraisal_rate': 0.87, 'profit_eok': -11.49, 'roi_pct': -3.83, 'decision': 'NO-GO'},
        {'capex_eok': 300.0, 'appraisal_rate': 0.92, 'profit_eok': -0.36, 'roi_pct': -0.12, 'decision': 'NO-GO'},
        {'capex_eok': 300.0, 'appraisal_rate': 0.97, 'profit_eok': 10.77, 'roi_pct': 3.59, 'decision': 'NO-GO'},
        {'capex_eok': 330.0, 'appraisal_rate': 0.87, 'profit_eok': -41.49, 'roi_pct': -12.57, 'decision': 'NO-GO'},
        {'capex_eok': 330.0, 'appraisal_rate': 0.92, 'profit_eok': -30.36, 'roi_pct': -9.20, 'decision': 'NO-GO'},
        {'capex_eok': 330.0, 'appraisal_rate': 0.97, 'profit_eok': -19.23, 'roi_pct': -5.83, 'decision': 'NO-GO'}
    ]
    
    print("Testing Scenario Heatmap Generator...")
    
    # Test profit heatmap
    success1 = generate_profit_heatmap(
        test_scenarios,
        '/home/user/webapp/test_profit_heatmap.png'
    )
    print(f"Profit heatmap: {'✅ SUCCESS' if success1 else '❌ FAILED'}")
    
    # Test ROI heatmap
    success2 = generate_roi_heatmap(
        test_scenarios,
        '/home/user/webapp/test_roi_heatmap.png'
    )
    print(f"ROI heatmap: {'✅ SUCCESS' if success2 else '❌ FAILED'}")
    
    # Test decision heatmap
    success3 = generate_decision_heatmap(
        test_scenarios,
        '/home/user/webapp/test_decision_heatmap.png'
    )
    print(f"Decision heatmap: {'✅ SUCCESS' if success3 else '❌ FAILED'}")
    
    if success1 and success2 and success3:
        print("\n✅ All tests passed!")
        print("Generated files:")
        print("  - /home/user/webapp/test_profit_heatmap.png")
        print("  - /home/user/webapp/test_roi_heatmap.png")
        print("  - /home/user/webapp/test_decision_heatmap.png")
