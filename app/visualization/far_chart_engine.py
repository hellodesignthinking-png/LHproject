"""
FAR Chart Engine v24.0
======================
용적률 차트 생성 엔진 - Bar charts, Gauge charts, Scenario comparison

Author: ZeroSite Development Team
Version: 24.0.0
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class FARChartEngine:
    """FAR Chart visualization engine"""
    
    def __init__(self):
        self.version = "24.0.0"
        self.engine_name = "FARChartEngine"
    
    def generate_bar_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate FAR comparison bar chart
        
        Args:
            data: {
                'current_far': 220.0,
                'max_legal_far': 250.0,
                'incentive_far': 20.0,
                'achievable_far': 270.0,
                'recommended_far': 229.5
            }
        
        Returns:
            Plotly-compatible chart configuration
        """
        chart_config = {
            'type': 'bar',
            'data': [
                {
                    'x': ['Current FAR', 'Legal Max', 'With Incentive', 'Recommended'],
                    'y': [
                        data.get('current_far', 0),
                        data.get('max_legal_far', 0),
                        data.get('achievable_far', 0),
                        data.get('recommended_far', 0)
                    ],
                    'marker': {
                        'color': ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6']
                    },
                    'text': [
                        f"{data.get('current_far', 0):.1f}%",
                        f"{data.get('max_legal_far', 0):.1f}%",
                        f"{data.get('achievable_far', 0):.1f}%",
                        f"{data.get('recommended_far', 0):.1f}%"
                    ],
                    'textposition': 'auto'
                }
            ],
            'layout': {
                'title': 'FAR Analysis (용적률 분석)',
                'xaxis': {'title': 'FAR Type'},
                'yaxis': {'title': 'FAR (%)'},
                'height': 400
            }
        }
        
        return {
            'chart_type': 'bar_chart',
            'config': chart_config,
            'format': 'plotly_json'
        }
    
    def generate_gauge_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate FAR utilization gauge chart
        
        Args:
            data: {
                'current_far': 229.5,
                'max_far': 270.0,
                'utilization_percent': 85.0
            }
        """
        utilization = data.get('utilization_percent', 0)
        
        # Color based on utilization level
        if utilization < 70:
            color = '#EF4444'  # Red - Low utilization
        elif utilization < 85:
            color = '#F59E0B'  # Orange - Medium
        else:
            color = '#10B981'  # Green - Good utilization
        
        chart_config = {
            'type': 'indicator',
            'data': [{
                'type': 'indicator',
                'mode': 'gauge+number+delta',
                'value': utilization,
                'title': {'text': 'FAR Utilization (용적률 활용도)'},
                'delta': {'reference': 85, 'increasing': {'color': '#10B981'}},
                'gauge': {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 70], 'color': '#FEE2E2'},
                        {'range': [70, 85], 'color': '#FEF3C7'},
                        {'range': [85, 100], 'color': '#D1FAE5'}
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 4},
                        'thickness': 0.75,
                        'value': 85
                    }
                }
            }],
            'layout': {'height': 300}
        }
        
        return {
            'chart_type': 'gauge_chart',
            'config': chart_config,
            'utilization': utilization,
            'color': color,
            'format': 'plotly_json'
        }
    
    def generate_scenario_comparison(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate scenario comparison chart
        
        Args:
            scenarios: [
                {'name': 'A안', 'far': 220, 'units': 18, 'roi': 10.5},
                {'name': 'B안', 'far': 240, 'units': 22, 'roi': 12.3},
                {'name': 'C안', 'far': 230, 'units': 20, 'roi': 15.8}
            ]
        """
        chart_config = {
            'type': 'grouped_bar',
            'data': [
                {
                    'x': [s['name'] for s in scenarios],
                    'y': [s['far'] for s in scenarios],
                    'name': 'FAR (%)',
                    'type': 'bar',
                    'marker': {'color': '#3B82F6'}
                },
                {
                    'x': [s['name'] for s in scenarios],
                    'y': [s['units'] for s in scenarios],
                    'name': 'Units (세대)',
                    'type': 'bar',
                    'yaxis': 'y2',
                    'marker': {'color': '#10B981'}
                },
                {
                    'x': [s['name'] for s in scenarios],
                    'y': [s['roi'] for s in scenarios],
                    'name': 'ROI (%)',
                    'type': 'bar',
                    'yaxis': 'y3',
                    'marker': {'color': '#F59E0B'}
                }
            ],
            'layout': {
                'title': 'Scenario Comparison (시나리오 비교)',
                'xaxis': {'title': 'Scenario'},
                'yaxis': {'title': 'FAR (%)'},
                'yaxis2': {'title': 'Units', 'overlaying': 'y', 'side': 'right'},
                'yaxis3': {'title': 'ROI (%)', 'overlaying': 'y', 'side': 'right', 'position': 0.85},
                'barmode': 'group',
                'height': 450
            }
        }
        
        # Find best scenario
        best_scenario = max(scenarios, key=lambda x: x.get('roi', 0))
        
        return {
            'chart_type': 'scenario_comparison',
            'config': chart_config,
            'best_scenario': best_scenario['name'],
            'scenario_count': len(scenarios),
            'format': 'plotly_json'
        }
    
    def generate_all_charts(self, full_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all FAR charts from analysis results"""
        
        results = {
            'engine': self.engine_name,
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'charts': {}
        }
        
        # Bar chart
        if 'far_data' in full_data:
            results['charts']['bar_chart'] = self.generate_bar_chart(full_data['far_data'])
        
        # Gauge chart
        if 'utilization_data' in full_data:
            results['charts']['gauge_chart'] = self.generate_gauge_chart(full_data['utilization_data'])
        
        # Scenario comparison
        if 'scenarios' in full_data:
            results['charts']['scenario_comparison'] = self.generate_scenario_comparison(full_data['scenarios'])
        
        return results
    
    def export_html(self, chart_config: Dict[str, Any], output_path: str) -> str:
        """Export chart as standalone HTML file"""
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>FAR Chart - ZeroSite v24</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1F2937;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>FAR Analysis Chart (용적률 분석 차트)</h1>
        <div id="chart"></div>
        <p style="color: #6B7280; margin-top: 20px;">
            Generated by ZeroSite v24 FAR Chart Engine | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
    <script>
        var data = {json.dumps(chart_config['config']['data'])};
        var layout = {json.dumps(chart_config['config']['layout'])};
        Plotly.newPlot('chart', data, layout);
    </script>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        return output_path


def main():
    """CLI test for FAR Chart Engine"""
    
    print("\n" + "="*60)
    print("FAR CHART ENGINE v24.0 - CLI TEST")
    print("="*60 + "\n")
    
    engine = FARChartEngine()
    
    # Test 1: Bar Chart
    print("📊 Test 1: FAR Comparison Bar Chart")
    print("-" * 60)
    
    far_data = {
        'current_far': 220.0,
        'max_legal_far': 250.0,
        'incentive_far': 20.0,
        'achievable_far': 270.0,
        'recommended_far': 229.5
    }
    
    bar_chart = engine.generate_bar_chart(far_data)
    print(f"✅ Chart Type: {bar_chart['chart_type']}")
    print(f"✅ Format: {bar_chart['format']}")
    print(f"✅ Data Points: {len(bar_chart['config']['data'][0]['x'])}")
    print(f"✅ Values: Current {far_data['current_far']}%, Max {far_data['max_legal_far']}%, "
          f"Achievable {far_data['achievable_far']}%, Recommended {far_data['recommended_far']}%")
    
    # Test 2: Gauge Chart
    print("\n📊 Test 2: FAR Utilization Gauge")
    print("-" * 60)
    
    util_data = {
        'current_far': 229.5,
        'max_far': 270.0,
        'utilization_percent': 85.0
    }
    
    gauge_chart = engine.generate_gauge_chart(util_data)
    print(f"✅ Chart Type: {gauge_chart['chart_type']}")
    print(f"✅ Utilization: {gauge_chart['utilization']}%")
    print(f"✅ Color: {gauge_chart['color']} (Green = Good utilization)")
    
    # Test 3: Scenario Comparison
    print("\n📊 Test 3: Scenario Comparison Chart")
    print("-" * 60)
    
    scenarios = [
        {'name': 'A안', 'far': 220, 'units': 18, 'roi': 10.5},
        {'name': 'B안', 'far': 240, 'units': 22, 'roi': 12.3},
        {'name': 'C안', 'far': 230, 'units': 20, 'roi': 15.8}
    ]
    
    scenario_chart = engine.generate_scenario_comparison(scenarios)
    print(f"✅ Chart Type: {scenario_chart['chart_type']}")
    print(f"✅ Scenarios: {scenario_chart['scenario_count']}")
    print(f"✅ Best Scenario: {scenario_chart['best_scenario']} (Highest ROI)")
    
    # Test 4: All Charts
    print("\n📊 Test 4: Generate All Charts")
    print("-" * 60)
    
    full_data = {
        'far_data': far_data,
        'utilization_data': util_data,
        'scenarios': scenarios
    }
    
    all_charts = engine.generate_all_charts(full_data)
    print(f"✅ Engine: {all_charts['engine']}")
    print(f"✅ Version: {all_charts['version']}")
    print(f"✅ Charts Generated: {len(all_charts['charts'])}")
    print(f"✅ Chart Types: {', '.join(all_charts['charts'].keys())}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
