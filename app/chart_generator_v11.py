"""
ZeroSite v11.0 - Chart Generator
=================================
데이터 시각화 차트 생성 엔진 (Pure HTML/CSS/SVG)

목적: 보고서에 포함될 시각화 차트 생성
- Radar Chart (5 unit types comparison)
- Bar Chart (LH Score breakdown)
- Heatmap Matrix (Unit-type suitability)

No external dependencies - Pure HTML/CSS/SVG

Author: ZeroSite Team
Date: 2025-12-05
"""

from typing import Dict, Any, List, Tuple
import math


class ChartGenerator:
    """
    순수 HTML/CSS/SVG 기반 차트 생성기
    
    지원 차트:
    1. Radar Chart - 5개 세대유형 비교
    2. Bar Chart - LH 점수 breakdown
    3. Heatmap - 세대유형 적합성 매트릭스
    """
    
    def __init__(self):
        self.colors = {
            'youth': '#3498db',      # 청년형 - Blue
            'newlywed': '#e74c3c',   # 신혼형 - Red
            'senior': '#9b59b6',     # 고령자형 - Purple
            'general': '#2ecc71',    # 일반형 - Green
            'vulnerable': '#f39c12'  # 취약계층형 - Orange
        }
    
    # ========================================================================
    # 1. Radar Chart for Unit Types
    # ========================================================================
    
    def generate_unit_type_radar_chart(
        self,
        unit_analysis: Dict[str, Any]
    ) -> str:
        """
        5개 세대유형 비교 Radar Chart 생성 (SVG)
        
        Args:
            unit_analysis: Unit-Type Analyzer 결과
            
        Returns:
            Radar Chart HTML/SVG
        """
        # 6개 평가 기준
        criteria = [
            'demographic',
            'transportation',
            'infrastructure',
            'policy',
            'economic',
            'social'
        ]
        
        criteria_labels = {
            'demographic': '인구 구성',
            'transportation': '교통',
            'infrastructure': '생활 인프라',
            'policy': '정책',
            'economic': '경제',
            'social': '사회 수요'
        }
        
        # 5개 세대유형 데이터
        unit_types = {
            'youth': '청년형',
            'newlywed': '신혼형',
            'senior': '고령자형',
            'general': '일반형',
            'vulnerable': '취약계층형'
        }
        
        # SVG 설정
        width = 600
        height = 600
        center_x = width // 2
        center_y = height // 2
        max_radius = 200
        num_criteria = len(criteria)
        
        svg = f'''
        <div class="radar-chart-container">
            <h4>📊 세대유형 비교 Radar Chart</h4>
            <p class="chart-description">6개 평가 기준에 대한 5개 세대유형의 적합도 비교</p>
            
            <svg width="{width}" height="{height}" class="radar-chart-svg">
                <!-- Background circles -->
                <g class="radar-grid">
        '''
        
        # 동심원 (20, 40, 60, 80, 100)
        for i in range(1, 6):
            radius = (max_radius / 5) * i
            svg += f'''
                    <circle cx="{center_x}" cy="{center_y}" r="{radius}" 
                            fill="none" stroke="#e0e0e0" stroke-width="1"/>
                    <text x="{center_x + radius + 5}" y="{center_y}" 
                          font-size="10" fill="#999">{i*20}</text>
            '''
        
        # 축 (6개 criteria)
        svg += '<g class="radar-axes">'
        
        for i, criterion in enumerate(criteria):
            angle = (math.pi * 2 / num_criteria) * i - math.pi / 2
            x_end = center_x + max_radius * math.cos(angle)
            y_end = center_y + max_radius * math.sin(angle)
            
            # 축 라인
            svg += f'''
                <line x1="{center_x}" y1="{center_y}" 
                      x2="{x_end}" y2="{y_end}" 
                      stroke="#ccc" stroke-width="2"/>
            '''
            
            # 라벨
            label_distance = max_radius + 30
            x_label = center_x + label_distance * math.cos(angle)
            y_label = center_y + label_distance * math.sin(angle)
            
            svg += f'''
                <text x="{x_label}" y="{y_label}" 
                      text-anchor="middle" dominant-baseline="middle"
                      font-size="13" font-weight="600" fill="#333">
                    {criteria_labels[criterion]}
                </text>
            '''
        
        svg += '</g>'
        
        # 각 세대유형의 다각형
        svg += '<g class="radar-polygons">'
        
        for unit_key, unit_label in unit_types.items():
            scores = unit_analysis.get('by_type', {}).get(unit_key, {})
            
            # 각 criteria 점수 추출
            points = []
            for i, criterion in enumerate(criteria):
                score = scores.get(f'{criterion}_score', 50) / 100  # 0-1로 정규화
                angle = (math.pi * 2 / num_criteria) * i - math.pi / 2
                x = center_x + max_radius * score * math.cos(angle)
                y = center_y + max_radius * score * math.sin(angle)
                points.append(f"{x},{y}")
            
            points_str = " ".join(points)
            color = self.colors.get(unit_key, '#999')
            
            # 다각형 (반투명)
            svg += f'''
                <polygon points="{points_str}" 
                         fill="{color}" fill-opacity="0.2" 
                         stroke="{color}" stroke-width="2"
                         class="radar-polygon radar-{unit_key}"/>
            '''
            
            # 각 포인트에 점 표시
            for point in points:
                x, y = point.split(',')
                svg += f'''
                    <circle cx="{x}" cy="{y}" r="4" 
                            fill="{color}" stroke="white" stroke-width="2"
                            class="radar-point"/>
                '''
        
        svg += '</g>'
        
        svg += '''
            </svg>
            
            <!-- Legend -->
            <div class="radar-legend">
        '''
        
        for unit_key, unit_label in unit_types.items():
            color = self.colors.get(unit_key, '#999')
            svg += f'''
                <div class="legend-item">
                    <span class="legend-color" style="background-color: {color};"></span>
                    <span class="legend-label">{unit_label}</span>
                </div>
            '''
        
        svg += '''
            </div>
        </div>
        
        <style>
        .radar-chart-container {
            margin: 30px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .radar-chart-container h4 {
            margin-bottom: 10px;
            color: #2c3e50;
        }
        
        .chart-description {
            font-size: 13px;
            color: #666;
            margin-bottom: 20px;
        }
        
        .radar-chart-svg {
            display: block;
            margin: 0 auto;
        }
        
        .radar-polygon {
            transition: fill-opacity 0.3s;
        }
        
        .radar-polygon:hover {
            fill-opacity: 0.5 !important;
        }
        
        .radar-point {
            transition: r 0.2s;
        }
        
        .radar-point:hover {
            r: 6;
        }
        
        .radar-legend {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 20px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 3px;
            border: 2px solid #ddd;
        }
        
        .legend-label {
            font-size: 13px;
            font-weight: 500;
            color: #333;
        }
        </style>
        '''
        
        return svg
    
    # ========================================================================
    # 2. Bar Chart for LH Score Breakdown
    # ========================================================================
    
    def generate_lh_score_bar_chart(
        self,
        lh_result: Dict[str, Any]
    ) -> str:
        """
        LH 점수 breakdown Bar Chart 생성
        
        Args:
            lh_result: LH Score Mapper 결과
            
        Returns:
            Bar Chart HTML
        """
        categories = {
            'location_suitability': {'label': '입지 적합성', 'max': 25, 'color': '#3498db'},
            'business_feasibility': {'label': '사업 타당성', 'max': 30, 'color': '#e74c3c'},
            'policy_alignment': {'label': '정책 부합성', 'max': 20, 'color': '#2ecc71'},
            'financial_soundness': {'label': '재무 건전성', 'max': 15, 'color': '#f39c12'},
            'risk_level': {'label': '리스크 수준', 'max': 10, 'color': '#9b59b6'}
        }
        
        scores = lh_result.get('category_scores', {})
        
        html = '''
        <div class="bar-chart-container">
            <h4>📊 LH 점수 Breakdown</h4>
            <p class="chart-description">5개 평가 영역별 점수 분포 (총 100점)</p>
            
            <div class="bar-chart">
        '''
        
        for cat_key, cat_info in categories.items():
            score = scores.get(cat_key, 0)
            max_score = cat_info['max']
            percentage = (score / max_score) * 100
            color = cat_info['color']
            label = cat_info['label']
            
            # 색상 강도 결정
            if percentage >= 80:
                bar_class = 'bar-excellent'
            elif percentage >= 60:
                bar_class = 'bar-good'
            elif percentage >= 40:
                bar_class = 'bar-fair'
            else:
                bar_class = 'bar-poor'
            
            html += f'''
                <div class="bar-row">
                    <div class="bar-label">
                        <span class="label-text">{label}</span>
                        <span class="label-score">{score:.1f}/{max_score}</span>
                    </div>
                    <div class="bar-container">
                        <div class="bar-fill {bar_class}" 
                             style="width: {percentage}%; background-color: {color};">
                            <span class="bar-percentage">{percentage:.0f}%</span>
                        </div>
                    </div>
                </div>
            '''
        
        html += '''
            </div>
        </div>
        
        <style>
        .bar-chart-container {
            margin: 30px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .bar-chart-container h4 {
            margin-bottom: 10px;
            color: #2c3e50;
        }
        
        .bar-chart {
            margin-top: 20px;
        }
        
        .bar-row {
            margin-bottom: 20px;
        }
        
        .bar-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .label-text {
            font-weight: 600;
            color: #333;
        }
        
        .label-score {
            font-weight: bold;
            color: #666;
        }
        
        .bar-container {
            width: 100%;
            height: 40px;
            background: #f0f0f0;
            border-radius: 6px;
            overflow: hidden;
            position: relative;
        }
        
        .bar-fill {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            transition: width 0.6s ease, background-color 0.3s;
            position: relative;
        }
        
        .bar-fill:hover {
            opacity: 0.8;
        }
        
        .bar-percentage {
            color: white;
            font-weight: bold;
            font-size: 13px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        .bar-excellent {
            box-shadow: inset 0 0 10px rgba(255,255,255,0.3);
        }
        
        .bar-good {
            opacity: 0.9;
        }
        
        .bar-fair {
            opacity: 0.75;
        }
        
        .bar-poor {
            opacity: 0.6;
        }
        </style>
        '''
        
        return html
    
    # ========================================================================
    # 3. Heatmap for Unit-Type Suitability Matrix
    # ========================================================================
    
    def generate_heatmap_matrix(
        self,
        unit_analysis: Dict[str, Any]
    ) -> str:
        """
        세대유형 적합성 Heatmap 매트릭스 생성
        
        Args:
            unit_analysis: Unit-Type Analyzer 결과
            
        Returns:
            Heatmap HTML
        """
        unit_types = {
            'youth': '청년형',
            'newlywed': '신혼형',
            'senior': '고령자형',
            'general': '일반형',
            'vulnerable': '취약계층형'
        }
        
        criteria = {
            'demographic': '인구',
            'transportation': '교통',
            'infrastructure': '생활',
            'policy': '정책',
            'economic': '경제',
            'social': '사회'
        }
        
        html = '''
        <div class="heatmap-container">
            <h4>🌡️ 세대유형 적합성 Heatmap</h4>
            <p class="chart-description">세대유형별 평가 기준 적합도 (색상: 빨강=높음, 노랑=보통, 초록=낮음)</p>
            
            <table class="heatmap-table">
                <thead>
                    <tr>
                        <th>세대유형</th>
        '''
        
        # Column headers
        for criterion_label in criteria.values():
            html += f'<th>{criterion_label}</th>'
        
        html += '<th>평균</th></tr></thead><tbody>'
        
        # Rows
        for unit_key, unit_label in unit_types.items():
            scores_data = unit_analysis.get('by_type', {}).get(unit_key, {})
            
            html += f'<tr><td class="row-header">{unit_label}</td>'
            
            total_score = 0
            count = 0
            
            for criterion_key in criteria.keys():
                score = scores_data.get(f'{criterion_key}_score', 50)
                total_score += score
                count += 1
                
                # Heatmap color
                if score >= 85:
                    cell_class = 'heat-excellent'
                elif score >= 70:
                    cell_class = 'heat-good'
                elif score >= 50:
                    cell_class = 'heat-fair'
                else:
                    cell_class = 'heat-poor'
                
                html += f'''
                    <td class="heat-cell {cell_class}" data-score="{score}">
                        {score:.0f}
                    </td>
                '''
            
            # Average
            avg_score = total_score / count if count > 0 else 0
            
            if avg_score >= 85:
                avg_class = 'heat-excellent'
            elif avg_score >= 70:
                avg_class = 'heat-good'
            elif avg_score >= 50:
                avg_class = 'heat-fair'
            else:
                avg_class = 'heat-poor'
            
            html += f'''
                <td class="heat-cell heat-avg {avg_class}">
                    <strong>{avg_score:.1f}</strong>
                </td>
            '''
            
            html += '</tr>'
        
        html += '''
                </tbody>
            </table>
            
            <!-- Heatmap Legend -->
            <div class="heatmap-legend">
                <div class="legend-item">
                    <span class="legend-color heat-excellent"></span>
                    <span class="legend-label">우수 (85+)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color heat-good"></span>
                    <span class="legend-label">양호 (70-84)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color heat-fair"></span>
                    <span class="legend-label">보통 (50-69)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color heat-poor"></span>
                    <span class="legend-label">미흡 (<50)</span>
                </div>
            </div>
        </div>
        
        <style>
        .heatmap-container {
            margin: 30px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .heatmap-container h4 {
            margin-bottom: 10px;
            color: #2c3e50;
        }
        
        .heatmap-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .heatmap-table th,
        .heatmap-table td {
            padding: 12px;
            text-align: center;
            border: 2px solid white;
        }
        
        .heatmap-table th {
            background: #34495e;
            color: white;
            font-weight: 600;
            font-size: 13px;
        }
        
        .row-header {
            background: #ecf0f1;
            font-weight: 600;
            text-align: left !important;
        }
        
        .heat-cell {
            font-weight: 500;
            font-size: 14px;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: help;
        }
        
        .heat-cell:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            z-index: 10;
        }
        
        /* Heatmap colors */
        .heat-excellent {
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            color: white;
        }
        
        .heat-good {
            background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%);
            color: white;
        }
        
        .heat-fair {
            background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
            color: white;
        }
        
        .heat-poor {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
        }
        
        .heat-avg {
            font-weight: bold !important;
            border-left: 3px solid #2c3e50;
        }
        
        .heatmap-legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .heatmap-legend .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .heatmap-legend .legend-color {
            width: 30px;
            height: 20px;
            border-radius: 3px;
            border: 1px solid #ddd;
        }
        
        .heatmap-legend .legend-label {
            font-size: 13px;
            color: #555;
        }
        </style>
        '''
        
        return html


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    print("✅ Chart Generator v11.0 Module Loaded")
    print("="*60)
    
    # Test
    generator = ChartGenerator()
    
    # Test data
    test_unit_analysis = {
        'by_type': {
            'youth': {
                'demographic_score': 75,
                'transportation_score': 85,
                'infrastructure_score': 70,
                'policy_score': 80,
                'economic_score': 65,
                'social_score': 75
            },
            'newlywed': {
                'demographic_score': 80,
                'transportation_score': 85,
                'infrastructure_score': 85,
                'policy_score': 90,
                'economic_score': 80,
                'social_score': 85
            },
            'senior': {
                'demographic_score': 65,
                'transportation_score': 70,
                'infrastructure_score': 60,
                'policy_score': 75,
                'economic_score': 55,
                'social_score': 70
            },
            'general': {
                'demographic_score': 70,
                'transportation_score': 75,
                'infrastructure_score': 70,
                'policy_score': 70,
                'economic_score': 70,
                'social_score': 70
            },
            'vulnerable': {
                'demographic_score': 60,
                'transportation_score': 65,
                'infrastructure_score': 55,
                'policy_score': 85,
                'economic_score': 50,
                'social_score': 80
            }
        }
    }
    
    test_lh = {
        'category_scores': {
            'location_suitability': 18.0,
            'business_feasibility': 23.0,
            'policy_alignment': 16.0,
            'financial_soundness': 12.0,
            'risk_level': 7.0
        }
    }
    
    # Test charts
    radar = generator.generate_unit_type_radar_chart(test_unit_analysis)
    print(f"✅ Radar Chart Generated: {len(radar):,} characters")
    
    bar = generator.generate_lh_score_bar_chart(test_lh)
    print(f"✅ Bar Chart Generated: {len(bar):,} characters")
    
    heatmap = generator.generate_heatmap_matrix(test_unit_analysis)
    print(f"✅ Heatmap Generated: {len(heatmap):,} characters")
    
    print("\n" + "="*60)
    print("✅ Chart Generator Test Complete")
