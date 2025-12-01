"""
ZeroSite v7.2 Extended - Full Data Exporter
모든 엔진 필드를 100% 출력하는 시스템

Purpose: 
- 누락 없이 모든 분석 데이터를 표 형태로 출력
- 부록에 Raw JSON 데이터 전체 출력
- 필드별 설명 및 해석 자동 생성
"""

from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)


class FullDataExporter:
    """모든 엔진 필드 100% 출력 시스템"""
    
    def __init__(self):
        self.version = "1.0.0"
        logger.info(f"📊 Full Data Exporter initialized (v{self.version})")
    
    def export_to_dict(self, analysis_data: Dict) -> Dict:
        """분석 데이터를 Dictionary 형태로 반환 (Extended Report용)"""
        # 이미 Dictionary 형태이므로 그대로 반환
        return analysis_data
    
    # ============================================================================
    # 모든 필드를 표 형태로 출력
    # ============================================================================
    
    def export_poi_all_fields(self, poi_data: Dict) -> str:
        """POI 분석 모든 필드 출력"""
        html = """
        <div class="full-data-section">
            <h4>📊 POI v3.1 전체 데이터</h4>
            <table class="full-data-table">
                <thead>
                    <tr>
                        <th style="width: 30%">필드명</th>
                        <th style="width: 20%">값</th>
                        <th style="width: 50%">설명</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # 전체 필드 출력
        fields = [
            ('total_score_v3_1', poi_data.get('total_score_v3_1', 'N/A'), 'POI 종합 점수 (100점 만점)'),
            ('lh_grade', poi_data.get('lh_grade', 'N/A'), 'LH 평가 등급 (S/A/B/C/D)'),
            ('final_distance_m', f"{poi_data.get('final_distance_m', 0):.0f}m", '가중치 적용 최종 거리'),
            ('weight_applied_distance', f"{poi_data.get('weight_applied_distance', 0):.2f}", '가중 거리 합계'),
            ('version', poi_data.get('version', 'N/A'), '분석 엔진 버전'),
        ]
        
        for field_name, value, description in fields:
            html += f"""
                <tr>
                    <td><code>{field_name}</code></td>
                    <td><strong>{value}</strong></td>
                    <td>{description}</td>
                </tr>
            """
        
        # POI 개별 시설 전체 출력
        pois = poi_data.get('pois', {})
        html += """
                <tr class="section-header">
                    <td colspan="3"><strong>개별 POI 시설 상세 (전체)</strong></td>
                </tr>
        """
        
        for poi_type, poi_info in pois.items():
            poi_name = self._translate_poi_type(poi_type)
            distance = poi_info.get('distance_m', 0)
            weight = poi_info.get('weight', 0)
            lh_grade = poi_info.get('lh_distance_grade', 'N/A')
            
            html += f"""
                <tr>
                    <td>└─ <strong>{poi_name}</strong> ({poi_type})</td>
                    <td>{distance:.0f}m</td>
                    <td>가중치: {weight:.2f}, LH등급: {lh_grade}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
    
    def export_type_demand_all_fields(self, td_data: Dict) -> str:
        """Type Demand 분석 모든 필드 출력"""
        html = """
        <div class="full-data-section">
            <h4>📊 Type Demand v3.1 전체 데이터</h4>
            <table class="full-data-table">
                <thead>
                    <tr>
                        <th style="width: 30%">필드명</th>
                        <th style="width: 20%">값</th>
                        <th style="width: 50%">설명</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # 종합 필드
        fields = [
            ('main_score', f"{td_data.get('main_score', 0):.2f}점", '사용자 선택 유형의 최종 점수'),
            ('grade', td_data.get('grade', 'N/A'), '사용자 선택 유형의 등급 (S/A/B/C/D)'),
            ('demand_level', td_data.get('demand_level', 'N/A'), '수요 수준 (매우 높음/높음/보통/낮음/매우 낮음)'),
            ('selected_unit_type', td_data.get('selected_unit_type', 'N/A'), '사용자가 선택한 주거 유형'),
            ('version', td_data.get('version', 'N/A'), '분석 엔진 버전'),
        ]
        
        for field_name, value, description in fields:
            html += f"""
                <tr>
                    <td><code>{field_name}</code></td>
                    <td><strong>{value}</strong></td>
                    <td>{description}</td>
                </tr>
            """
        
        # 유형별 상세 점수 전체 출력
        type_scores = td_data.get('type_scores', {})
        html += """
                <tr class="section-header">
                    <td colspan="3"><strong>유형별 상세 점수 (5개 유형 전체)</strong></td>
                </tr>
        """
        
        for type_name, scores in type_scores.items():
            html += f"""
                <tr>
                    <td colspan="3"><strong>🏠 {type_name}</strong></td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ raw_score</td>
                    <td>{scores.get('raw_score', 0):.2f}</td>
                    <td>지역 인구통계 기반 순수 수요 점수</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ poi_bonus</td>
                    <td>{scores.get('poi_bonus', 0):.2f}</td>
                    <td>POI 접근성 가점</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ user_type_weight</td>
                    <td>{scores.get('user_type_weight', 1.0):.2f}</td>
                    <td>시장 선호도 가중치</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ final_score</td>
                    <td><strong>{scores.get('final_score', 0):.2f}점</strong></td>
                    <td>최종 점수 (raw + bonus) × weight</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ grade</td>
                    <td><strong>{scores.get('grade', 'N/A')}</strong></td>
                    <td>v7.2 등급 (S/A/B/C/D)</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ grade_text</td>
                    <td>{scores.get('grade_text', 'N/A')}</td>
                    <td>등급 한글 해석</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
    
    def export_zoning_all_fields(self, zone_data: Dict) -> str:
        """Zoning 정보 23개 필드 전체 출력"""
        html = """
        <div class="full-data-section">
            <h4>📊 Zoning v7.2 전체 데이터 (23개 필드)</h4>
            <table class="full-data-table">
                <thead>
                    <tr>
                        <th style="width: 30%">필드명</th>
                        <th style="width: 20%">값</th>
                        <th style="width: 50%">설명</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # 23개 필드 전체 정의
        fields = [
            # 기본 정보 (5개)
            ('zone_type', zone_data.get('zone_type', 'N/A'), '용도지역 (예: 제3종일반주거지역)'),
            ('district', zone_data.get('district', 'N/A'), '용도지구 (예: 방화지구)'),
            ('zone', zone_data.get('zone', 'N/A'), '용도구역 (예: 개발제한구역)'),
            ('altitude_district', zone_data.get('altitude_district', 'N/A'), '고도지구 (예: 최고고도지구)'),
            ('fire_district', zone_data.get('fire_district', False), '방화지구 지정 여부'),
            
            # 건축 규제 (6개)
            ('building_coverage_ratio', f"{zone_data.get('building_coverage_ratio', 0)}%", '건폐율 상한'),
            ('floor_area_ratio', f"{zone_data.get('floor_area_ratio', 0)}%", '용적률 상한'),
            ('height_limit', f"{zone_data.get('height_limit', 'N/A')}", '높이 제한'),
            ('min_green_ratio', f"{zone_data.get('min_green_ratio', 0)}%", '최소 녹지율'),
            ('parking_requirement', zone_data.get('parking_requirement', 'N/A'), '주차장 설치 기준'),
            ('setback_requirement', zone_data.get('setback_requirement', 'N/A'), '건축선 후퇴 거리'),
            
            # 지구단위계획 (3개)
            ('district_unit_plan', zone_data.get('district_unit_plan', False), '지구단위계획구역 지정 여부'),
            ('landscape_district', zone_data.get('landscape_district', False), '경관지구 지정 여부'),
            ('historic_cultural', zone_data.get('historic_cultural', False), '문화재 보호구역 포함 여부'),
            
            # Overlay zones (3개)
            ('overlay_zones', ', '.join(zone_data.get('overlay_zones', [])) or '없음', '중첩 용도지역'),
            ('development_restrictions', ', '.join(zone_data.get('development_restrictions', [])) or '없음', '개발 제한 사항'),
            ('environmental_restrictions', ', '.join(zone_data.get('environmental_restrictions', [])) or '없음', '환경 제약 사항'),
            
            # 기반시설 (3개)
            ('road_width', f"{zone_data.get('road_width', 'N/A')}", '접한 도로 폭'),
            ('water_supply', zone_data.get('water_supply', 'N/A'), '상수도 공급 현황'),
            ('sewerage', zone_data.get('sewerage', 'N/A'), '하수도 처리 현황'),
            
            # 기타 (3개)
            ('land_use_plan', zone_data.get('land_use_plan', 'N/A'), '도시관리계획 상 용도'),
            ('zoning_compliance', zone_data.get('zoning_compliance', 'N/A'), '법규 적합성 판정'),
            ('remarks', zone_data.get('remarks', '없음'), '특이사항 및 비고'),
        ]
        
        for field_name, value, description in fields:
            html += f"""
                <tr>
                    <td><code>{field_name}</code></td>
                    <td><strong>{value}</strong></td>
                    <td>{description}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
            <div class="info-box" style="margin-top: 20px;">
                <strong>📌 23개 필드 카테고리</strong><br>
                • 기본 정보 (5개): 용도지역, 지구, 구역, 고도, 방화<br>
                • 건축 규제 (6개): 건폐율, 용적률, 높이, 녹지율, 주차, 건축선<br>
                • 지구단위계획 (3개): 지구단위계획, 경관지구, 문화재<br>
                • 중첩 규제 (3개): 중첩 용도, 개발 제한, 환경 제약<br>
                • 기반시설 (3개): 도로, 상수도, 하수도<br>
                • 기타 (3개): 도시계획, 적합성, 비고
            </div>
        </div>
        """
        
        return html
    
    def export_geo_optimizer_all_fields(self, geo_data: Dict) -> str:
        """GeoOptimizer 모든 필드 출력"""
        html = """
        <div class="full-data-section">
            <h4>📊 GeoOptimizer v3.1 전체 데이터</h4>
            <table class="full-data-table">
                <thead>
                    <tr>
                        <th style="width: 30%">필드명</th>
                        <th style="width: 20%">값</th>
                        <th style="width: 50%">설명</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # 전체 필드
        fields = [
            ('final_score', f"{geo_data.get('final_score', 0):.2f}점", '최종 종합 점수'),
            ('final_score_formatted', geo_data.get('final_score_formatted', 'N/A'), '포맷된 점수 문자열'),
            ('weighted_total', f"{geo_data.get('weighted_total', 0):.2f}점", '가중 합계 점수'),
            ('slope_score', f"{geo_data.get('slope_score', 0):.2f}점", '경사도 점수'),
            ('noise_score', f"{geo_data.get('noise_score', 0):.2f}점", '소음 점수'),
            ('sunlight_score', f"{geo_data.get('sunlight_score', 0):.2f}점", '일조량 점수'),
            ('version', geo_data.get('version', 'N/A'), '분석 엔진 버전'),
        ]
        
        for field_name, value, description in fields:
            html += f"""
                <tr>
                    <td><code>{field_name}</code></td>
                    <td><strong>{value}</strong></td>
                    <td>{description}</td>
                </tr>
            """
        
        # 현재 부지 강점/약점
        strengths = geo_data.get('current_strengths', [])
        weaknesses = geo_data.get('current_weaknesses', [])
        
        html += f"""
                <tr class="section-header">
                    <td colspan="3"><strong>현재 부지 평가</strong></td>
                </tr>
                <tr>
                    <td>current_strengths</td>
                    <td>{len(strengths)}개</td>
                    <td>{', '.join(strengths) if strengths else '없음'}</td>
                </tr>
                <tr>
                    <td>current_weaknesses</td>
                    <td>{len(weaknesses)}개</td>
                    <td>{', '.join(weaknesses) if weaknesses else '없음'}</td>
                </tr>
        """
        
        # 대안 부지 전체
        alternatives = geo_data.get('alternatives', [])
        html += f"""
                <tr class="section-header">
                    <td colspan="3"><strong>대안 후보지 ({len(alternatives)}개)</strong></td>
                </tr>
        """
        
        for i, alt in enumerate(alternatives, 1):
            html += f"""
                <tr>
                    <td colspan="3"><strong>대안 {i}: {alt.get('location', 'N/A')}</strong></td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ distance_m</td>
                    <td>{alt.get('distance_m', 0)}m</td>
                    <td>현재 부지로부터의 거리</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ distance_km</td>
                    <td>{alt.get('distance_km', 'N/A')}</td>
                    <td>거리 (킬로미터)</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ score</td>
                    <td><strong>{alt.get('score', 0):.2f}점</strong></td>
                    <td>대안 부지 점수</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ score_formatted</td>
                    <td>{alt.get('score_formatted', 'N/A')}</td>
                    <td>포맷된 점수</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ reason</td>
                    <td colspan="2">{alt.get('reason', 'N/A')}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
    
    def export_risk_all_fields(self, risk_data: Dict) -> str:
        """Risk Assessment 모든 필드 출력"""
        html = """
        <div class="full-data-section">
            <h4>📊 Risk Assessment 2025 전체 데이터</h4>
            <table class="full-data-table">
                <thead>
                    <tr>
                        <th style="width: 30%">필드명</th>
                        <th style="width: 20%">값</th>
                        <th style="width: 50%">설명</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # 종합 리스크 필드
        fields = [
            ('risk_score', f"{risk_data.get('risk_score', 0):.1f}점", '종합 리스크 점수 (100점 만점)'),
            ('risk_score_formatted', risk_data.get('risk_score_formatted', 'N/A'), '포맷된 점수 (예: 80점/100점)'),
            ('risk_score_percentage', risk_data.get('risk_score_percentage', 'N/A'), '백분율 표기 (예: 80%)'),
            ('risk_level', risk_data.get('risk_level', 'N/A'), '리스크 등급 (저위험/중위험/고위험)'),
            ('total_risk_count', risk_data.get('total_risk_count', 0), '확인된 총 리스크 개수'),
            ('deduction_per_risk', f"{risk_data.get('deduction_per_risk', 10)}점", '리스크 1건당 감점'),
            ('total_deduction', f"{risk_data.get('total_deduction', 0)}점", '총 감점액'),
            ('criteria_version', risk_data.get('criteria_version', 'N/A'), '평가 기준 버전'),
        ]
        
        for field_name, value, description in fields:
            html += f"""
                <tr>
                    <td><code>{field_name}</code></td>
                    <td><strong>{value}</strong></td>
                    <td>{description}</td>
                </tr>
            """
        
        # 카테고리별 리스크 상세
        risk_categories = risk_data.get('risk_categories', {})
        risk_factors = risk_data.get('risk_factors', [])
        
        html += f"""
                <tr class="section-header">
                    <td colspan="3"><strong>카테고리별 리스크 ({len(risk_categories)}개 카테고리)</strong></td>
                </tr>
        """
        
        for category, risks in risk_categories.items():
            html += f"""
                <tr>
                    <td><strong>{category}</strong></td>
                    <td>{len(risks)}건</td>
                    <td>{', '.join([r.get('description', 'N/A') for r in risks[:3]]) if risks else '없음'}</td>
                </tr>
            """
        
        # 개별 리스크 전체 목록
        html += f"""
                <tr class="section-header">
                    <td colspan="3"><strong>개별 리스크 상세 ({len(risk_factors)}건)</strong></td>
                </tr>
        """
        
        for i, risk in enumerate(risk_factors, 1):
            html += f"""
                <tr>
                    <td colspan="3"><strong>리스크 {i}</strong></td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ category</td>
                    <td>{risk.get('category', 'N/A')}</td>
                    <td>리스크 카테고리</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ description</td>
                    <td colspan="2">{risk.get('description', 'N/A')}</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;└─ severity</td>
                    <td>{risk.get('severity', 'N/A')}</td>
                    <td>심각도 (high/medium/low)</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
    
    # ============================================================================
    # JSON 형태로 전체 데이터 출력 (부록용)
    # ============================================================================
    
    def export_as_json_appendix(self, analysis_data: Dict) -> str:
        """부록: 전체 분석 데이터를 JSON 형태로 출력"""
        html = """
        <div class="appendix-section">
            <h3>부록 A: 엔진 Raw Data 전체</h3>
            <p>
                본 부록은 ZeroSite v7.2 분석 엔진이 생성한 모든 데이터를 JSON 형식으로 제공합니다.
                개발자 및 데이터 분석가가 활용할 수 있도록 원본 데이터를 보존하였습니다.
            </p>
            <div class="json-container">
                <h4>📦 Full Analysis Data (JSON)</h4>
                <pre><code class="json">
        """
        
        # JSON 포맷팅
        json_str = json.dumps(analysis_data, indent=2, ensure_ascii=False)
        # HTML 이스케이프
        json_str = json_str.replace('<', '&lt;').replace('>', '&gt;')
        
        html += json_str
        html += """
                </code></pre>
            </div>
            <div class="info-box" style="margin-top: 20px;">
                <strong>💡 활용 방법</strong><br>
                • Python: <code>import json; data = json.loads(json_string)</code><br>
                • JavaScript: <code>const data = JSON.parse(jsonString)</code><br>
                • 데이터 검증: 각 필드의 타입과 범위를 확인하여 정합성 검증 가능<br>
                • API 연동: RESTful API 응답 형식과 동일하여 시스템 연동 용이
            </div>
        </div>
        """
        
        return html
    
    # ============================================================================
    # Helper Methods
    # ============================================================================
    
    def _translate_poi_type(self, poi_type: str) -> str:
        """POI 타입 한글 번역"""
        translations = {
            'elementary_school': '초등학교',
            'hospital': '종합병원',
            'subway_station': '지하철역',
            'bus_stop': '버스정류장',
            'convenience_store': '편의점',
            'university': '대학교',
            'library': '도서관',
            'park': '공원',
            'supermarket': '대형마트'
        }
        return translations.get(poi_type, poi_type)


# Singleton instance
_full_data_exporter = None

def get_full_data_exporter() -> FullDataExporter:
    """Get or create full data exporter instance"""
    global _full_data_exporter
    if _full_data_exporter is None:
        _full_data_exporter = FullDataExporter()
    return _full_data_exporter
