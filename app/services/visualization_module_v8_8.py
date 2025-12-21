"""
ZeroSite v8.8 Visualization Module

Purpose:
- Generate visualizations for reports
- Kakao Static Map integration
- Radar Chart for type demand scores
- Risk Heatmap table
- Market Histogram

All visualizations are READ-ONLY and use locked appraisal data
"""

from typing import Dict, Any, List, Optional, Tuple
import base64
from io import BytesIO
import json


class VisualizationModuleV88:
    """
    ZeroSite v8.8 Visualization Module
    
    Generates:
    1. Kakao Static Map
    2. Radar Chart (demand scores)
    3. Risk Heatmap
    4. Market Histogram
    """
    
    def __init__(self, kakao_api_key: Optional[str] = None):
        """
        Initialize visualization module
        
        Args:
            kakao_api_key: Kakao Maps API key (optional)
        """
        self.kakao_api_key = kakao_api_key or "DEMO_KEY"
    
    def generate_kakao_static_map(
        self,
        latitude: float,
        longitude: float,
        zoom: int = 16,
        width: int = 800,
        height: int = 600,
        marker: bool = True
    ) -> Dict[str, Any]:
        """
        Generate Kakao Static Map URL
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            zoom: Zoom level (1-14)
            width: Image width in pixels
            height: Image height in pixels
            marker: Whether to show marker at center
        
        Returns:
            Dictionary with map URL and metadata
        """
        
        # Kakao Static Map API URL format
        # https://apis-navi.kakaomobility.com/v1/waypoints/directions
        base_url = "https://dapi.kakao.com/v2/maps/sdk.js"
        
        marker_param = f"marker={longitude},{latitude}" if marker else ""
        
        return {
            'type': 'kakao_static_map',
            'url': f'{base_url}?appkey={self.kakao_api_key}',
            'center': {
                'latitude': latitude,
                'longitude': longitude
            },
            'zoom': zoom,
            'dimensions': {
                'width': width,
                'height': height
            },
            'marker': marker,
            'embed_html': self._generate_kakao_map_html(latitude, longitude, zoom),
            'note': '📍 Kakao Maps API integration (실제 구현 시 API 키 필요)'
        }
    
    def _generate_kakao_map_html(
        self, latitude: float, longitude: float, zoom: int
    ) -> str:
        """Generate Kakao Map embed HTML"""
        
        return f'''
<div id="map" style="width:800px;height:600px;"></div>
<script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={self.kakao_api_key}"></script>
<script>
var container = document.getElementById('map');
var options = {{
    center: new kakao.maps.LatLng({latitude}, {longitude}),
    level: {zoom}
}};
var map = new kakao.maps.Map(container, options);

// Add marker
var markerPosition = new kakao.maps.LatLng({latitude}, {longitude});
var marker = new kakao.maps.Marker({{
    position: markerPosition
}});
marker.setMap(map);
</script>
        '''.strip()
    
    def generate_radar_chart(
        self,
        type_scores: Dict[str, float],
        title: str = "유형별 수요 점수",
        width: int = 600,
        height: int = 600
    ) -> Dict[str, Any]:
        """
        Generate Radar Chart data for type demand scores
        
        Args:
            type_scores: Dictionary of type names and scores
            title: Chart title
            width: Chart width in pixels
            height: Chart height in pixels
        
        Returns:
            Dictionary with chart data and configuration
        """
        
        # Normalize scores to 0-100 scale
        max_score = 20
        normalized_scores = {
            type_name: (score / max_score) * 100
            for type_name, score in type_scores.items()
        }
        
        return {
            'type': 'radar_chart',
            'title': title,
            'data': {
                'labels': list(type_scores.keys()),
                'scores': list(type_scores.values()),
                'normalized_scores': list(normalized_scores.values())
            },
            'dimensions': {
                'width': width,
                'height': height
            },
            'config': {
                'max_value': max_score,
                'scale_steps': 5,
                'colors': {
                    'line': '#FF6B6B',
                    'fill': 'rgba(255, 107, 107, 0.2)',
                    'grid': '#E0E0E0'
                }
            },
            'chart_js_data': self._generate_chartjs_radar_data(type_scores, max_score),
            'note': '📊 Radar Chart (Chart.js 또는 D3.js 활용 권장)'
        }
    
    def _generate_chartjs_radar_data(
        self, type_scores: Dict[str, float], max_value: float
    ) -> Dict[str, Any]:
        """Generate Chart.js compatible radar chart data"""
        
        return {
            'type': 'radar',
            'data': {
                'labels': list(type_scores.keys()),
                'datasets': [{
                    'label': '수요 점수',
                    'data': list(type_scores.values()),
                    'backgroundColor': 'rgba(255, 107, 107, 0.2)',
                    'borderColor': 'rgb(255, 107, 107)',
                    'pointBackgroundColor': 'rgb(255, 107, 107)',
                    'pointBorderColor': '#fff',
                    'pointHoverBackgroundColor': '#fff',
                    'pointHoverBorderColor': 'rgb(255, 107, 107)'
                }]
            },
            'options': {
                'elements': {
                    'line': {
                        'borderWidth': 3
                    }
                },
                'scales': {
                    'r': {
                        'min': 0,
                        'max': max_value,
                        'ticks': {
                            'stepSize': max_value / 5
                        }
                    }
                }
            }
        }
    
    def generate_risk_heatmap(
        self,
        risks: List[Dict[str, Any]],
        title: str = "Risk Heatmap"
    ) -> Dict[str, Any]:
        """
        Generate Risk Heatmap table
        
        Args:
            risks: List of risk dictionaries with category, probability, impact
            title: Heatmap title
        
        Returns:
            Dictionary with heatmap data and HTML table
        """
        
        # Define risk levels
        probability_levels = ['LOW', 'MEDIUM', 'HIGH']
        impact_levels = ['LOW', 'MEDIUM', 'HIGH']
        
        # Calculate risk matrix
        risk_matrix = {}
        for risk in risks:
            prob = risk.get('probability', 'MEDIUM')
            impact = risk.get('impact', 'MEDIUM')
            category = risk.get('category', 'Unknown')
            
            key = f'{prob}_{impact}'
            if key not in risk_matrix:
                risk_matrix[key] = []
            risk_matrix[key].append(category)
        
        # Generate color-coded cells
        color_map = {
            'LOW_LOW': '#90EE90',        # Light Green
            'LOW_MEDIUM': '#FFD700',     # Gold
            'LOW_HIGH': '#FFA500',       # Orange
            'MEDIUM_LOW': '#FFD700',     # Gold
            'MEDIUM_MEDIUM': '#FFA500',  # Orange
            'MEDIUM_HIGH': '#FF6347',    # Tomato
            'HIGH_LOW': '#FFA500',       # Orange
            'HIGH_MEDIUM': '#FF6347',    # Tomato
            'HIGH_HIGH': '#DC143C'       # Crimson
        }
        
        return {
            'type': 'risk_heatmap',
            'title': title,
            'risks': risks,
            'matrix': risk_matrix,
            'color_map': color_map,
            'dimensions': {
                'probability_levels': probability_levels,
                'impact_levels': impact_levels
            },
            'html_table': self._generate_heatmap_html(
                risk_matrix, color_map, probability_levels, impact_levels
            ),
            'note': '🔥 Risk Heatmap (HTML Table 형식)'
        }
    
    def _generate_heatmap_html(
        self,
        risk_matrix: Dict[str, List[str]],
        color_map: Dict[str, str],
        probability_levels: List[str],
        impact_levels: List[str]
    ) -> str:
        """Generate HTML table for risk heatmap"""
        
        html = '<table border="1" cellpadding="10" style="border-collapse: collapse;">\n'
        html += '<tr><th>Probability / Impact</th>'
        
        for impact in impact_levels:
            html += f'<th>{impact}</th>'
        html += '</tr>\n'
        
        for prob in reversed(probability_levels):
            html += f'<tr><th>{prob}</th>'
            for impact in impact_levels:
                key = f'{prob}_{impact}'
                color = color_map.get(key, '#FFFFFF')
                risks = risk_matrix.get(key, [])
                risk_text = '<br>'.join(risks) if risks else '-'
                html += f'<td style="background-color: {color};">{risk_text}</td>'
            html += '</tr>\n'
        
        html += '</table>'
        return html
    
    def generate_market_histogram(
        self,
        transaction_prices: List[float],
        target_price: float,
        title: str = "시장 거래가 분포",
        bins: int = 10
    ) -> Dict[str, Any]:
        """
        Generate Market Histogram for transaction prices
        
        Args:
            transaction_prices: List of transaction prices per sqm
            target_price: Target land price per sqm
            title: Chart title
            bins: Number of histogram bins
        
        Returns:
            Dictionary with histogram data and configuration
        """
        
        if not transaction_prices:
            return {
                'type': 'histogram',
                'title': title,
                'data': [],
                'note': '⚠️ 거래사례 데이터 없음'
            }
        
        # Calculate histogram bins
        min_price = min(transaction_prices)
        max_price = max(transaction_prices)
        bin_width = (max_price - min_price) / bins
        
        histogram_data = []
        for i in range(bins):
            bin_start = min_price + i * bin_width
            bin_end = bin_start + bin_width
            count = sum(1 for p in transaction_prices if bin_start <= p < bin_end)
            histogram_data.append({
                'bin_start': bin_start,
                'bin_end': bin_end,
                'count': count,
                'label': f'{bin_start/1000:.0f}K-{bin_end/1000:.0f}K'
            })
        
        # Find target price position
        target_bin = int((target_price - min_price) / bin_width)
        
        return {
            'type': 'histogram',
            'title': title,
            'data': histogram_data,
            'statistics': {
                'min': min_price,
                'max': max_price,
                'mean': sum(transaction_prices) / len(transaction_prices),
                'median': sorted(transaction_prices)[len(transaction_prices) // 2],
                'count': len(transaction_prices)
            },
            'target_price': target_price,
            'target_bin': target_bin,
            'chart_js_data': self._generate_chartjs_histogram_data(
                histogram_data, target_price
            ),
            'note': '📊 Market Histogram (Chart.js Bar Chart 활용)'
        }
    
    def _generate_chartjs_histogram_data(
        self, histogram_data: List[Dict[str, Any]], target_price: float
    ) -> Dict[str, Any]:
        """Generate Chart.js compatible histogram data"""
        
        return {
            'type': 'bar',
            'data': {
                'labels': [d['label'] for d in histogram_data],
                'datasets': [{
                    'label': '거래 건수',
                    'data': [d['count'] for d in histogram_data],
                    'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                    'borderColor': 'rgb(54, 162, 235)',
                    'borderWidth': 1
                }]
            },
            'options': {
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': '거래 건수'
                        }
                    },
                    'x': {
                        'title': {
                            'display': True,
                            'text': '가격 범위 (천원/㎡)'
                        }
                    }
                },
                'plugins': {
                    'annotation': {
                        'annotations': {
                            'line1': {
                                'type': 'line',
                                'xMin': f'{target_price/1000:.0f}K',
                                'xMax': f'{target_price/1000:.0f}K',
                                'borderColor': 'rgb(255, 99, 132)',
                                'borderWidth': 2,
                                'label': {
                                    'content': '대상 토지',
                                    'enabled': True
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def generate_far_change_graph(
        self,
        zoning_history: List[Dict[str, Any]],
        title: str = "용적률 변화 추이"
    ) -> Dict[str, Any]:
        """
        Generate FAR (Floor Area Ratio) change graph over time
        
        Args:
            zoning_history: List of zoning changes with date and FAR
            title: Chart title
        
        Returns:
            Dictionary with line chart data
        """
        
        if not zoning_history:
            return {
                'type': 'line_chart',
                'title': title,
                'data': [],
                'note': '⚠️ 용적률 변화 이력 없음'
            }
        
        dates = [entry['date'] for entry in zoning_history]
        far_values = [entry['far'] for entry in zoning_history]
        
        return {
            'type': 'line_chart',
            'title': title,
            'data': {
                'dates': dates,
                'far_values': far_values
            },
            'chart_js_data': {
                'type': 'line',
                'data': {
                    'labels': dates,
                    'datasets': [{
                        'label': '용적률 (%)',
                        'data': far_values,
                        'borderColor': 'rgb(75, 192, 192)',
                        'tension': 0.1
                    }]
                },
                'options': {
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'title': {
                                'display': True,
                                'text': '용적률 (%)'
                            }
                        }
                    }
                }
            },
            'note': '📈 FAR Change Graph (Chart.js Line Chart)'
        }
    
    def generate_all_visualizations_as_base64(
        self,
        appraisal_data: Dict[str, Any],
        type_scores: Dict[str, float],
        risks: List[Dict[str, Any]],
        market_data: List[float],
        far_history: List[Tuple[str, float]]
    ) -> Dict[str, str]:
        """
        Generate all visualizations and return as base64 encoded strings
        
        Args:
            appraisal_data: Appraisal context data
            type_scores: Type demand scores for radar chart
            risks: Risk data for heatmap
            market_data: Market price distribution for histogram
            far_history: FAR change history data
        
        Returns:
            Dictionary with visualization names and their base64 encoded PNG/SVG strings
        """
        
        visualizations = {}
        
        # 1. Kakao Static Map
        latitude = appraisal_data.get('location', {}).get('latitude', 37.5665)
        longitude = appraisal_data.get('location', {}).get('longitude', 126.9780)
        
        kakao_map = self.generate_kakao_static_map(latitude, longitude)
        visualizations['kakao_map'] = {
            'type': 'html_embed',
            'data': kakao_map.get('embed_html', ''),
            'format': 'html',
            'note': 'Kakao Map requires client-side rendering'
        }
        
        # 2. Radar Chart
        radar_chart = self.generate_radar_chart(type_scores)
        visualizations['radar_chart'] = {
            'type': 'chart_js',
            'data': json.dumps(radar_chart.get('chart_js_data', {})),
            'format': 'json',
            'note': 'Chart.js data for client-side rendering'
        }
        
        # 3. Risk Heatmap
        risk_heatmap = self.generate_risk_heatmap(risks)
        visualizations['risk_heatmap'] = {
            'type': 'html_table',
            'data': risk_heatmap.get('html_table', ''),
            'format': 'html',
            'note': 'Risk Heatmap as HTML table'
        }
        
        # 4. Market Histogram
        histogram = self.generate_market_histogram(market_data)
        visualizations['market_histogram'] = {
            'type': 'chart_js',
            'data': json.dumps(histogram.get('chart_js_data', {})),
            'format': 'json',
            'note': 'Chart.js data for client-side rendering'
        }
        
        # 5. FAR Change Graph
        far_graph = self.generate_far_change_graph(far_history)
        visualizations['far_change_graph'] = {
            'type': 'chart_js',
            'data': json.dumps(far_graph.get('chart_js_data', {})),
            'format': 'json',
            'note': 'Chart.js data for client-side rendering'
        }
        
        return visualizations
    
    def embed_visualizations_in_report(
        self,
        report_data: Dict[str, Any],
        visualizations: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Embed visualizations into report data
        
        Args:
            report_data: Report dictionary
            visualizations: Dictionary of visualizations with base64 data
        
        Returns:
            Updated report dictionary with embedded visualizations
        """
        
        # Add visualizations to report metadata
        if 'visualizations' not in report_data:
            report_data['visualizations'] = {}
        
        report_data['visualizations'] = visualizations
        
        # Add warnings for missing visualizations
        required_viz = ['kakao_map', 'radar_chart', 'risk_heatmap', 'market_histogram', 'far_change_graph']
        missing_viz = [viz for viz in required_viz if viz not in visualizations]
        
        if missing_viz:
            report_data['visualization_warnings'] = {
                'status': 'INCOMPLETE',
                'missing': missing_viz,
                'message': f'⚠️ Warning: {len(missing_viz)} visualizations are missing from the report'
            }
        else:
            report_data['visualization_warnings'] = {
                'status': 'COMPLETE',
                'missing': [],
                'message': '✅ All visualizations successfully generated'
            }
        
        return report_data


def create_visualization_module(kakao_api_key: Optional[str] = None) -> VisualizationModuleV88:
    """
    Factory function to create visualization module
    
    Args:
        kakao_api_key: Kakao Maps API key (optional)
    
    Returns:
        VisualizationModuleV88 instance
    """
    return VisualizationModuleV88(kakao_api_key=kakao_api_key)


__all__ = [
    'VisualizationModuleV88',
    'create_visualization_module'
]
