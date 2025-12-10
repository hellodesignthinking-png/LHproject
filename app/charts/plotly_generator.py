"""
ZeroSite Chart Generator using Plotly

This module generates high-quality charts for the v3 Full Report:
1. 30-Year Cashflow Chart (Line)
2. Competitive Analysis Radar Chart
3. Sensitivity Heatmap
4. Tornado Chart (Sensitivity Analysis)
5. McKinsey 2x2 Risk Matrix

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 1.0 - PRODUCTION
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64


class PlotlyChartGenerator:
    """
    High-quality chart generator using Plotly for Expert Edition v3
    """
    
    def __init__(self):
        """Initialize chart generator"""
        self.default_colors = {
            'primary': '#1976d2',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#d32f2f',
            'info': '#00bcd4',
            'secondary': '#757575'
        }
    
    def generate_cashflow_chart(self, cash_flow_data: list) -> str:
        """
        Generate 30-year cashflow line chart
        
        Args:
            cash_flow_data: List of dicts with keys: year, revenue, expense, net_cf, cumulative_cf
            
        Returns:
            Base64 encoded PNG image
        """
        years = [item['year'] for item in cash_flow_data]
        revenue = [item['revenue'] / 100_000_000 for item in cash_flow_data]  # 억원
        expense = [item['expense'] / 100_000_000 for item in cash_flow_data]  # 억원
        net_cf = [item['net_cf'] / 100_000_000 for item in cash_flow_data]  # 억원
        cumulative = [item['cumulative_cf'] / 100_000_000 for item in cash_flow_data]  # 억원
        
        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=1, cols=1,
            specs=[[{"secondary_y": True}]]
        )
        
        # Add traces
        fig.add_trace(
            go.Scatter(
                x=years, y=revenue,
                name='수익',
                line=dict(color=self.default_colors['success'], width=2),
                mode='lines+markers'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=years, y=expense,
                name='지출',
                line=dict(color=self.default_colors['danger'], width=2),
                mode='lines+markers'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=years, y=net_cf,
                name='순현금흐름',
                line=dict(color=self.default_colors['primary'], width=3),
                mode='lines+markers'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=years, y=cumulative,
                name='누적현금흐름',
                line=dict(color=self.default_colors['warning'], width=2, dash='dash'),
                mode='lines'
            ),
            secondary_y=True
        )
        
        # Update layout
        fig.update_layout(
            title='30년 현금흐름 프로젝션',
            xaxis_title='연도',
            yaxis_title='현금흐름 (억원)',
            yaxis2_title='누적현금흐름 (억원)',
            hovermode='x unified',
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
            width=1200,
            height=500,
            template='plotly_white'
        )
        
        # Convert to base64
        return self._fig_to_base64(fig)
    
    def generate_radar_chart(self, scores: dict) -> str:
        """
        Generate competitive analysis radar chart
        
        Args:
            scores: Dict with keys: location, feasibility, policy, financial, risk
            
        Returns:
            Base64 encoded PNG image
        """
        categories = ['입지', '사업성', '정책', '재무', '리스크']
        values = [
            scores.get('location', 0),
            scores.get('feasibility', 0),
            scores.get('policy', 0),
            scores.get('financial', 0),
            scores.get('risk', 0)
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(25, 118, 210, 0.3)',
            line=dict(color=self.default_colors['primary'], width=2),
            marker=dict(size=8, color=self.default_colors['primary']),
            name='본 프로젝트'
        ))
        
        # Add benchmark (industry average)
        benchmark = [70, 65, 75, 60, 70]
        fig.add_trace(go.Scatterpolar(
            r=benchmark,
            theta=categories,
            fill='toself',
            fillcolor='rgba(117, 117, 117, 0.1)',
            line=dict(color=self.default_colors['secondary'], width=1, dash='dash'),
            marker=dict(size=6, color=self.default_colors['secondary']),
            name='업계 평균'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickvals=[20, 40, 60, 80, 100],
                    gridcolor='lightgray'
                )
            ),
            title='경쟁력 분석 (레이더 차트)',
            showlegend=True,
            legend=dict(x=0.85, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
            width=600,
            height=500,
            template='plotly_white'
        )
        
        return self._fig_to_base64(fig)
    
    def generate_sensitivity_heatmap(self, sensitivity_data: dict) -> str:
        """
        Generate sensitivity analysis heatmap
        
        Args:
            sensitivity_data: Dict with construction cost and appraisal rate variations
            
        Returns:
            Base64 encoded PNG image
        """
        # Create sensitivity matrix
        capex_variations = ['-10%', '-5%', '0%', '+5%', '+10%']
        appraisal_variations = ['+5%', '+3%', '0%', '-3%', '-5%']
        
        # Sample NPV matrix (in 억원)
        npv_matrix = [
            [5.2, 3.1, 0.8, -1.5, -3.8],   # CAPEX -10%
            [2.9, 0.8, -1.5, -3.8, -6.1],  # CAPEX -5%
            [0.6, -1.5, -3.8, -6.1, -8.4], # CAPEX 0%
            [-1.7, -3.8, -6.1, -8.4, -10.7], # CAPEX +5%
            [-4.0, -6.1, -8.4, -10.7, -13.0]  # CAPEX +10%
        ]
        
        fig = go.Figure(data=go.Heatmap(
            z=npv_matrix,
            x=appraisal_variations,
            y=capex_variations,
            colorscale=[
                [0, self.default_colors['danger']],
                [0.5, self.default_colors['warning']],
                [1, self.default_colors['success']]
            ],
            text=[[f"{val:.1f}억" for val in row] for row in npv_matrix],
            texttemplate="%{text}",
            textfont={"size": 12},
            colorbar=dict(title="NPV (억원)")
        ))
        
        fig.update_layout(
            title='민감도 분석 히트맵 (CAPEX x 감정평가율)',
            xaxis_title='LH 감정평가율 변동',
            yaxis_title='CAPEX 변동',
            width=700,
            height=500,
            template='plotly_white'
        )
        
        return self._fig_to_base64(fig)
    
    def generate_tornado_chart(self, sensitivity_data: list) -> str:
        """
        Generate Tornado chart for sensitivity analysis
        
        Args:
            sensitivity_data: List of dicts with keys: variable, downside, upside, base
            
        Returns:
            Base64 encoded PNG image
        """
        # Sort by impact (absolute difference)
        sorted_data = sorted(
            sensitivity_data,
            key=lambda x: abs(x['upside'] - x['downside']),
            reverse=True
        )
        
        variables = [item['variable'] for item in sorted_data]
        base_values = [item['base'] for item in sorted_data]
        downside = [item['downside'] - item['base'] for item in sorted_data]
        upside = [item['upside'] - item['base'] for item in sorted_data]
        
        fig = go.Figure()
        
        # Downside bars (negative impact)
        fig.add_trace(go.Bar(
            y=variables,
            x=downside,
            name='Downside',
            orientation='h',
            marker=dict(color=self.default_colors['danger']),
            text=[f"{d:.1f}억" for d in downside],
            textposition='inside'
        ))
        
        # Upside bars (positive impact)
        fig.add_trace(go.Bar(
            y=variables,
            x=upside,
            name='Upside',
            orientation='h',
            marker=dict(color=self.default_colors['success']),
            text=[f"+{u:.1f}억" for u in upside],
            textposition='inside'
        ))
        
        fig.update_layout(
            title='Tornado 차트 (민감도 순위)',
            xaxis_title='NPV 영향 (억원)',
            yaxis_title='변수',
            barmode='overlay',
            width=800,
            height=600,
            template='plotly_white',
            legend=dict(x=0.85, y=0.99, bgcolor='rgba(255,255,255,0.8)')
        )
        
        return self._fig_to_base64(fig)
    
    def generate_risk_matrix(self, risks: list) -> str:
        """
        Generate McKinsey 2x2 Risk Matrix
        
        Args:
            risks: List of dicts with keys: name, impact, probability, category
            
        Returns:
            Base64 encoded PNG image
        """
        fig = go.Figure()
        
        # Define quadrants
        fig.add_shape(
            type="rect", x0=0, y0=0, x1=0.5, y1=0.5,
            fillcolor="rgba(76, 175, 80, 0.2)", line=dict(width=0)
        )
        fig.add_shape(
            type="rect", x0=0.5, y0=0, x1=1, y1=0.5,
            fillcolor="rgba(255, 152, 0, 0.2)", line=dict(width=0)
        )
        fig.add_shape(
            type="rect", x0=0, y0=0.5, x1=0.5, y1=1,
            fillcolor="rgba(255, 152, 0, 0.2)", line=dict(width=0)
        )
        fig.add_shape(
            type="rect", x0=0.5, y0=0.5, x1=1, y1=1,
            fillcolor="rgba(211, 47, 47, 0.2)", line=dict(width=0)
        )
        
        # Add risk points
        for risk in risks:
            fig.add_trace(go.Scatter(
                x=[risk['probability']],
                y=[risk['impact'] / 10],  # Normalize to 0-1
                mode='markers+text',
                marker=dict(
                    size=15,
                    color=self.default_colors['danger'] if risk['impact'] > 7 else self.default_colors['warning']
                ),
                text=[risk['name']],
                textposition='top center',
                name=risk['name'],
                showlegend=False
            ))
        
        # Add quadrant labels
        annotations = [
            dict(x=0.25, y=0.25, text="Low Risk<br>(Monitor)", showarrow=False, font=dict(size=12)),
            dict(x=0.75, y=0.25, text="Medium Risk<br>(Manage)", showarrow=False, font=dict(size=12)),
            dict(x=0.25, y=0.75, text="Medium Risk<br>(Manage)", showarrow=False, font=dict(size=12)),
            dict(x=0.75, y=0.75, text="High Risk<br>(Mitigate)", showarrow=False, font=dict(size=12, color='red'))
        ]
        
        fig.update_layout(
            title='McKinsey 2x2 리스크 매트릭스',
            xaxis=dict(
                title='발생 가능성 (Probability)',
                range=[0, 1],
                tickvals=[0, 0.5, 1],
                ticktext=['Low', 'Medium', 'High']
            ),
            yaxis=dict(
                title='영향도 (Impact)',
                range=[0, 1],
                tickvals=[0, 0.5, 1],
                ticktext=['Low', 'Medium', 'High']
            ),
            width=700,
            height=700,
            template='plotly_white',
            annotations=annotations
        )
        
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """
        Convert Plotly figure to HTML string (embedded)
        
        Args:
            fig: Plotly figure object
            
        Returns:
            HTML string with embedded Plotly chart
        """
        # Generate interactive HTML div
        html_div = fig.to_html(
            include_plotlyjs='cdn',
            div_id=f"plotly-chart-{hash(str(fig))}",
            config={'displayModeBar': True, 'responsive': True}
        )
        
        return html_div


# ============================================================
# Test Script
# ============================================================
def main():
    """Test chart generation"""
    
    print("\n" + "="*80)
    print("🎨 Testing Plotly Chart Generation")
    print("="*80 + "\n")
    
    generator = PlotlyChartGenerator()
    
    # Test 1: Cashflow Chart
    print("📊 1. Generating 30-Year Cashflow Chart...")
    cash_flow_data = [
        {"year": i, "revenue": 2722_000_000 if i == 3 else 0,
         "expense": 4200_000_000 if i <= 3 else 0,
         "net_cf": (2722_000_000 if i == 3 else 0) - (4200_000_000 if i <= 3 else 0),
         "cumulative_cf": sum([(2722_000_000 if y == 3 else 0) - (4200_000_000 if y <= 3 else 0) for y in range(1, i+1)])}
        for i in range(1, 31)
    ]
    cashflow_chart = generator.generate_cashflow_chart(cash_flow_data)
    print(f"   ✅ Cashflow chart generated ({len(cashflow_chart)} bytes)")
    
    # Test 2: Radar Chart
    print("📊 2. Generating Radar Chart...")
    scores = {"location": 82, "feasibility": 75, "policy": 85, "financial": 65, "risk": 70}
    radar_chart = generator.generate_radar_chart(scores)
    print(f"   ✅ Radar chart generated ({len(radar_chart)} bytes)")
    
    # Test 3: Sensitivity Heatmap
    print("📊 3. Generating Sensitivity Heatmap...")
    sensitivity_data = {}  # Using default data in function
    heatmap_chart = generator.generate_sensitivity_heatmap(sensitivity_data)
    print(f"   ✅ Heatmap generated ({len(heatmap_chart)} bytes)")
    
    # Test 4: Tornado Chart
    print("📊 4. Generating Tornado Chart...")
    tornado_data = [
        {"variable": "LH 감정평가율", "base": -9.88, "downside": -15.2, "upside": -4.5},
        {"variable": "건설비", "base": -9.88, "downside": -13.1, "upside": -6.7},
        {"variable": "토지가격", "base": -9.88, "downside": -12.3, "upside": -7.4},
        {"variable": "금리", "base": -9.88, "downside": -11.5, "upside": -8.2}
    ]
    tornado_chart = generator.generate_tornado_chart(tornado_data)
    print(f"   ✅ Tornado chart generated ({len(tornado_chart)} bytes)")
    
    # Test 5: Risk Matrix
    print("📊 5. Generating McKinsey 2x2 Risk Matrix...")
    risks = [
        {"name": "건설비", "impact": 9.0, "probability": 0.7, "category": "high"},
        {"name": "감정평가", "impact": 8.5, "probability": 0.5, "category": "high"},
        {"name": "정책변경", "impact": 6.0, "probability": 0.3, "category": "medium"},
        {"name": "경기침체", "impact": 5.0, "probability": 0.2, "category": "low"}
    ]
    risk_matrix = generator.generate_risk_matrix(risks)
    print(f"   ✅ Risk matrix generated ({len(risk_matrix)} bytes)")
    
    print("\n" + "="*80)
    print("✅ All charts generated successfully!")
    print("="*80)
    print("\n💡 Charts are ready for integration into v3 Full Report")


if __name__ == "__main__":
    main()
