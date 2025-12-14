"""
ZeroSite v38 - Chart Generator
Generate matplotlib charts for PDF reports
"""
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rc
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import io
import os


class ChartGenerator:
    """Generate professional charts for appraisal reports"""
    
    def __init__(self):
        self._setup_korean_fonts()
        self._setup_style()
    
    def _setup_korean_fonts(self):
        """Setup Korean fonts for matplotlib"""
        font_paths = [
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                fm.fontManager.addfont(font_path)
                font_name = fm.FontProperties(fname=font_path).get_name()
                rc('font', family=font_name)
                plt.rcParams['axes.unicode_minus'] = False
                print(f"✅ Matplotlib Korean font: {font_name}")
                return
        
        print("⚠️ Korean font not found for matplotlib")
    
    def _setup_style(self):
        """Setup professional chart style"""
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': '#F8F9FA',
            'axes.edgecolor': '#1A237E',
            'axes.linewidth': 1.5,
            'grid.color': '#E0E0E0',
            'grid.linestyle': '--',
            'grid.linewidth': 0.5,
        })
    
    def generate_price_trend_chart(
        self,
        months: List[str],
        prices: List[float],
        width: float = 8,
        height: float = 4
    ) -> bytes:
        """
        Generate 3-year price trend line chart
        
        Args:
            months: List of month strings (e.g., ['2022-01', '2022-02', ...])
            prices: List of average prices (원/㎡)
            width: Chart width in inches
            height: Chart height in inches
        
        Returns:
            PNG image as bytes
        """
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        # Plot line
        ax.plot(months, prices, 
                color='#03A9F4', 
                linewidth=2.5, 
                marker='o', 
                markersize=4,
                label='평균 거래가')
        
        # Fill area under line
        ax.fill_between(range(len(months)), prices, alpha=0.2, color='#03A9F4')
        
        # Styling
        ax.set_title('지역 시세 추세 (최근 3년)', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('기간', fontsize=11)
        ax.set_ylabel('평균 거래가 (만원/㎡)', fontsize=11)
        ax.legend(loc='upper left', frameon=True, shadow=True)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        
        # Rotate x-axis labels
        ax.tick_params(axis='x', rotation=45)
        plt.xticks(range(0, len(months), 6), [months[i] for i in range(0, len(months), 6)])
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        # Tight layout
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        plt.close(fig)
        
        return buffer.getvalue()
    
    def generate_transaction_volume_chart(
        self,
        months: List[str],
        volumes: List[int],
        width: float = 8,
        height: float = 4
    ) -> bytes:
        """
        Generate monthly transaction volume bar chart
        
        Args:
            months: List of month strings (e.g., ['2024-01', '2024-02', ...])
            volumes: List of transaction counts
            width: Chart width in inches
            height: Chart height in inches
        
        Returns:
            PNG image as bytes
        """
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        # Create bar chart
        bars = ax.bar(months, volumes, 
                      color='#1A237E', 
                      alpha=0.8,
                      edgecolor='#0D47A1',
                      linewidth=1.5)
        
        # Highlight highest volume
        max_idx = volumes.index(max(volumes))
        bars[max_idx].set_color('#03A9F4')
        
        # Styling
        ax.set_title('월별 거래량 추이 (최근 12개월)', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('기간', fontsize=11)
        ax.set_ylabel('거래 건수', fontsize=11)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=9)
        
        # Rotate x-axis labels
        ax.tick_params(axis='x', rotation=45)
        
        # Grid
        ax.grid(True, axis='y', alpha=0.3)
        
        # Tight layout
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        plt.close(fig)
        
        return buffer.getvalue()
    
    def generate_supply_demand_chart(
        self,
        months: List[str],
        supply: List[float],
        demand: List[float],
        width: float = 8,
        height: float = 4
    ) -> bytes:
        """
        Generate supply vs demand dual-axis chart
        
        Args:
            months: List of month strings
            supply: Supply index values
            demand: Demand index values
            width: Chart width in inches
            height: Chart height in inches
        
        Returns:
            PNG image as bytes
        """
        fig, ax1 = plt.subplots(figsize=(width, height), dpi=100)
        
        # Left y-axis (Supply)
        color1 = '#E91E63'
        ax1.set_xlabel('기간', fontsize=11)
        ax1.set_ylabel('공급량 (분양물량)', color=color1, fontsize=11)
        ax1.plot(months, supply, color=color1, linewidth=2.5, marker='s', 
                label='공급량', markersize=5)
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.fill_between(range(len(months)), supply, alpha=0.2, color=color1)
        
        # Right y-axis (Demand)
        ax2 = ax1.twinx()
        color2 = '#4CAF50'
        ax2.set_ylabel('수요지수', color=color2, fontsize=11)
        ax2.plot(months, demand, color=color2, linewidth=2.5, marker='o',
                label='수요지수', markersize=5)
        ax2.tick_params(axis='y', labelcolor=color2)
        
        # Title
        ax1.set_title('공급·수요 분석', fontsize=14, fontweight='bold', pad=20)
        
        # Legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', 
                  frameon=True, shadow=True)
        
        # Rotate x-axis labels
        ax1.tick_params(axis='x', rotation=45)
        plt.xticks(range(0, len(months), 3), [months[i] for i in range(0, len(months), 3)])
        
        # Grid
        ax1.grid(True, alpha=0.3)
        
        # Tight layout
        fig.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        plt.close(fig)
        
        return buffer.getvalue()
    
    @staticmethod
    def generate_sample_data_3years() -> Tuple[List[str], List[float]]:
        """Generate sample 3-year monthly price data"""
        months = []
        prices = []
        
        base_date = datetime(2022, 1, 1)
        base_price = 800.0  # 800만원/㎡
        
        for i in range(36):  # 36 months = 3 years
            current_date = base_date + timedelta(days=30*i)
            month_str = current_date.strftime('%Y-%m')
            months.append(month_str)
            
            # Simulate price trend (gradual increase with some fluctuation)
            trend = base_price * (1 + 0.015 * i)  # 1.5% monthly increase
            noise = np.random.normal(0, 20)  # Random fluctuation
            price = trend + noise
            prices.append(round(price, 1))
        
        return months, prices
    
    @staticmethod
    def generate_sample_transaction_volume() -> Tuple[List[str], List[int]]:
        """Generate sample 12-month transaction volume data"""
        months = []
        volumes = []
        
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(12):
            current_date = base_date + timedelta(days=30*i)
            month_str = current_date.strftime('%Y-%m')
            months.append(month_str)
            
            # Simulate transaction volume (seasonal pattern)
            base_volume = 50
            seasonal = 20 * np.sin(i * np.pi / 6)  # Seasonal variation
            noise = np.random.randint(-10, 10)
            volume = int(base_volume + seasonal + noise)
            volumes.append(max(volume, 10))  # At least 10 transactions
        
        return months, volumes
    
    @staticmethod
    def generate_sample_supply_demand() -> Tuple[List[str], List[float], List[float]]:
        """Generate sample supply and demand data"""
        months = []
        supply = []
        demand = []
        
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(12):
            current_date = base_date + timedelta(days=30*i)
            month_str = current_date.strftime('%Y-%m')
            months.append(month_str)
            
            # Supply (decreasing trend)
            supply_val = 100 - i * 3 + np.random.normal(0, 5)
            supply.append(max(supply_val, 50))
            
            # Demand (increasing trend)
            demand_val = 80 + i * 4 + np.random.normal(0, 5)
            demand.append(min(demand_val, 150))
        
        return months, supply, demand


# Test function
if __name__ == "__main__":
    print("=" * 80)
    print("ZeroSite v38 - Chart Generator Test")
    print("=" * 80)
    
    generator = ChartGenerator()
    
    # Test 1: Price trend chart
    print("\n[Test 1] Generating 3-year price trend chart...")
    months, prices = ChartGenerator.generate_sample_data_3years()
    chart1 = generator.generate_price_trend_chart(months, prices)
    with open('/tmp/test_price_trend.png', 'wb') as f:
        f.write(chart1)
    print(f"✅ Saved: /tmp/test_price_trend.png ({len(chart1):,} bytes)")
    
    # Test 2: Transaction volume chart
    print("\n[Test 2] Generating transaction volume chart...")
    months2, volumes = ChartGenerator.generate_sample_transaction_volume()
    chart2 = generator.generate_transaction_volume_chart(months2, volumes)
    with open('/tmp/test_transaction_volume.png', 'wb') as f:
        f.write(chart2)
    print(f"✅ Saved: /tmp/test_transaction_volume.png ({len(chart2):,} bytes)")
    
    # Test 3: Supply/Demand chart
    print("\n[Test 3] Generating supply/demand chart...")
    months3, supply, demand = ChartGenerator.generate_sample_supply_demand()
    chart3 = generator.generate_supply_demand_chart(months3, supply, demand)
    with open('/tmp/test_supply_demand.png', 'wb') as f:
        f.write(chart3)
    print(f"✅ Saved: /tmp/test_supply_demand.png ({len(chart3):,} bytes)")
    
    print("\n" + "=" * 80)
    print("All charts generated successfully!")
    print("=" * 80)
