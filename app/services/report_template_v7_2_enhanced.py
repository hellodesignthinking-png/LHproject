"""
ZeroSite Report Engine v7.2 Enhanced Template Generator
Implements all 8 fix requirements for complete data integrity
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class ReportTemplateV72Enhanced:
    """
    Enhanced template generator with all v7.2 fixes:
    1. Uses ONLY v7.2 field names
    2. Adds missing 14 zoning fields with fallback
    3. Implements NoticeRuleEvaluator v7.2
    4. Full multi_parcel support with shape metrics
    5. GeoOptimizer Alternative 1-3 comparison + ASCII charts
    6. v7.2 Type Demand grading scale
    7. API reliability/log section
    8. Full Risk Table quantitative scoring (0-20) LH_2025
    """
    
    def __init__(self):
        self.version = "7.2-enhanced"
        self.generated_at = datetime.now().isoformat()
    
    def generate_comprehensive_markdown(self, data: Dict[str, Any]) -> str:
        """Generate comprehensive markdown with ALL v7.2 fields"""
        
        # Extract v7.2 sections
        metadata = data.get('metadata', {})
        basic = data.get('basic_info', {})
        coords = data.get('coordinates', {})
        zone = data.get('zone_info', {})
        poi_v3_1 = data.get('poi_analysis_v3_1', {})
        type_demand_v3_1 = data.get('type_demand_v3_1', {})
        multi_parcel_v3_0 = data.get('multi_parcel_v3_0', {})
        geo_v3_1 = data.get('geo_optimizer_v3_1', {})
        api_perf = data.get('api_performance', {})
        lh_notice_v2_1 = data.get('lh_notice_v2_1', {})
        risk_2025 = data.get('risk_analysis_2025', {})
        lh_assess = data.get('lh_assessment', {})
        dev_info = data.get('development_info', {})
        demand = data.get('demand_analysis', {})
        financial = data.get('financial_data', {})
        nego = data.get('negotiation_strategy', {})
        summary = data.get('summary', {})
        
        report = self._generate_header(basic, metadata)
        report += self._generate_executive_summary_v7_2(poi_v3_1, type_demand_v3_1, geo_v3_1, risk_2025, lh_assess)
        report += self._generate_location_info_v7_2(basic, coords, zone)
        report += self._generate_poi_analysis_v3_1(poi_v3_1)
        report += self._generate_type_demand_v3_1(type_demand_v3_1)
        report += self._generate_multi_parcel_v3_0(multi_parcel_v3_0, coords)
        report += self._generate_geo_optimizer_v3_1(geo_v3_1)
        report += self._generate_lh_notice_v2_1(lh_notice_v2_1, lh_assess)
        report += self._generate_risk_analysis_2025(risk_2025)
        report += self._generate_api_reliability_section(api_perf)
        report += self._generate_development_info(dev_info)
        report += self._generate_financial_projections(financial)
        report += self._generate_negotiation_strategy(nego)
        report += self._generate_final_recommendation(summary, lh_assess)
        
        return report
    
    def _generate_header(self, basic: Dict, metadata: Dict) -> str:
        """Generate report header with v7.2 branding"""
        return f"""# LH 신축매입임대 대상지 종합 분석보고서 v7.2
## 📍 {basic.get('address', '대상지')}

**Report Version**: {metadata.get('report_version', '7.2.0-complete')}  
**Engine Version**: {metadata.get('engine_version', 'v7.2')}  
**Generated**: {self.generated_at}  
**Patches Applied**: {len(metadata.get('patches_applied', []))} / 11  

---

"""
    
    def _generate_executive_summary_v7_2(self, poi: Dict, td: Dict, geo: Dict, risk: Dict, lh: Dict) -> str:
        """Executive Summary using v7.2 fields"""
        return f"""## 📊 Executive Summary (v7.2)

### 핵심 평가 지표

| 구분 | 값 | 등급 |
|------|-----|------|
| **POI v3.1 총점** | {poi.get('total_score_v3_1', 0):.2f}점 | {poi.get('lh_grade', 'N/A')} |
| **Type Demand v3.1** | {td.get('main_score', 0):.2f}점 | {self._get_demand_grade(td.get('demand_level', 'N/A'))} |
| **GeoOptimizer v3.1** | {geo.get('final_score', 0):.2f}점 | {self._get_score_grade(geo.get('final_score', 0))} |
| **Risk Score (LH 2025)** | {risk.get('risk_score', 0):.1f}점 / 20점 | {risk.get('risk_level', 'N/A')} |
| **LH 종합 등급** | {lh.get('total_score', 0):.2f}점 | {lh.get('grade', 'N/A')} |

### 종합 판단

- **적격 여부**: {lh.get('is_eligible', False) and '✅ 적격' or '⚠️ 검토 필요'}
- **추천**: {lh.get('recommendation', 'N/A')}
- **수요 수준**: {td.get('demand_level', 'N/A')}

---

"""
    
    def _generate_location_info_v7_2(self, basic: Dict, coords: Dict, zone: Dict) -> str:
        """
        FIX 1 & 2: Location info using ONLY v7.2 fields + 14 zoning fields with fallback
        """
        return f"""## I. 대상지 기본 정보 (v7.2)

### 1. 위치 정보

- **주소**: {basic.get('address', 'N/A')}
- **면적**: {basic.get('land_area', 0):.2f}㎡ (약 {int(basic.get('land_area', 0) / 3.3)}평)
- **GPS 좌표**: ({coords.get('latitude', 0):.6f}, {coords.get('longitude', 0):.6f})
- **분석 대상**: {basic.get('unit_type', 'N/A')} 유형
- **LH 기준 버전**: {basic.get('lh_version', '2024')}

### 2. 용도지역 및 법규 정보 (Zoning v7.2 - 23 fields)

#### 기본 용도지역
- **용도지역**: {zone.get('land_use_zone', 'N/A')}
- **건폐율**: {zone.get('building_coverage_ratio', 0):.1f}%
- **용적률**: {zone.get('floor_area_ratio', 0):.1f}%
- **높이 제한**: {zone.get('height_limit', 0):.1f}m {self._render_fallback(zone.get('height_limit', 0))}

#### 중첩 지역 지정 (Overlay Zones)
- **중첩 용도지역**: {', '.join(zone.get('overlay_zones', [])) or '없음'} {self._render_fallback(zone.get('overlay_zones', []))}
- **지구단위계획구역**: {self._yes_no(zone.get('district_unit_plan', False))} {self._render_fallback(zone.get('district_unit_plan'))}
- **경관지구**: {self._yes_no(zone.get('landscape_district', False))} {self._render_fallback(zone.get('landscape_district'))}

#### 개발 제한 사항 (Restrictions)
- **개발제한사항**: {', '.join(zone.get('development_restrictions', [])) or '없음'} {self._render_fallback(zone.get('development_restrictions', []))}
- **환경규제**: {', '.join(zone.get('environmental_restrictions', [])) or '없음'} {self._render_fallback(zone.get('environmental_restrictions', []))}
- **문화재보호구역**: {self._yes_no(zone.get('cultural_heritage_zone', False))} {self._render_fallback(zone.get('cultural_heritage_zone'))}
- **군사시설보호구역**: {self._yes_no(zone.get('military_restriction_zone', False))} {self._render_fallback(zone.get('military_restriction_zone'))}

#### 기반 시설 (Infrastructure)
- **도로 너비**: {zone.get('road_width', 0):.1f}m {self._render_fallback(zone.get('road_width', 0))}
- **도로 상태**: {zone.get('road_condition', 'N/A')} {self._render_fallback(zone.get('road_condition', 'N/A'))}
- **상수도**: {self._yes_no(zone.get('water_supply', True))}
- **하수도**: {self._yes_no(zone.get('sewage_system', True))}
- **전기**: {self._yes_no(zone.get('electricity', True))}
- **가스**: {self._yes_no(zone.get('gas_supply', True))}

#### 도시계획 (Planning)
- **도시계획구역**: {self._yes_no(zone.get('urban_planning_area', False))} {self._render_fallback(zone.get('urban_planning_area'))}
- **재개발구역**: {self._yes_no(zone.get('redevelopment_zone', False))} {self._render_fallback(zone.get('redevelopment_zone'))}
- **특별계획구역**: {self._yes_no(zone.get('special_planning_area', False))} {self._render_fallback(zone.get('special_planning_area'))}

#### 추가 규제 사항 (Additional Regulations)
- **주차 요구사항**: {zone.get('parking_requirements', 'N/A')} {self._render_fallback(zone.get('parking_requirements', 'N/A'))}
- **녹지비율**: {zone.get('green_space_ratio', 0):.1f}% {self._render_fallback(zone.get('green_space_ratio', 0))}
- **건축선 후퇴**: {self._format_setback(zone.get('setback_requirements', {}))} {self._render_fallback(zone.get('setback_requirements', {}))}

---

"""
    
    def _generate_poi_analysis_v3_1(self, poi: Dict) -> str:
        """
        FIX 1: POI Analysis using ONLY v3.1 fields
        """
        pois = poi.get('pois', {})
        
        poi_table = "| POI 유형 | 거리 (m) | 가중치 | 가중 거리 |\n"
        poi_table += "|----------|----------|--------|----------|\n"
        
        for poi_type, poi_data in pois.items():
            distance = poi_data.get('distance_m', 0)
            weight = poi_data.get('weight', 0)
            weighted = distance * weight
            poi_table += f"| {self._translate_poi_type(poi_type)} | {distance:.0f} | {weight:.2f} | {weighted:.0f} |\n"
        
        return f"""## II. POI 접근성 분석 v3.1

### POI v3.1 종합 평가

- **LH Grade**: {poi.get('lh_grade', 'N/A')}
- **Total Score v3.1**: {poi.get('total_score_v3_1', 0):.2f}점
- **Final Distance**: {poi.get('final_distance_m', 0):.2f}m
- **Weight Applied Distance**: {poi.get('weight_applied_distance', 0):.2f}m
- **Engine Version**: {poi.get('version', 'N/A')}

### POI 거리 상세 (v3.1 Standard)

{poi_table}

**가중 평균 거리**: {poi.get('weight_applied_distance', 0):.2f}m  
**최종 거리**: {poi.get('final_distance_m', 0):.2f}m  

---

"""
    
    def _generate_type_demand_v3_1(self, td: Dict) -> str:
        """
        FIX 6: Type Demand with v7.2 grading scale
        """
        type_scores = td.get('type_scores', {})
        
        table = "| 주거 유형 | Raw Score | POI Bonus | User Weight | **Final Score** | 등급 |\n"
        table += "|-----------|-----------|-----------|-------------|-----------------|------|\n"
        
        for type_name, scores in type_scores.items():
            raw = scores.get('raw_score', 0)
            bonus = scores.get('poi_bonus', 0)
            weight = scores.get('user_type_weight', 1.0)
            final = scores.get('final_score', 0)
            grade = self._get_v7_2_type_grade(final)
            
            table += f"| {type_name} | {raw:.1f} | {bonus:.1f} | {weight:.2f} | **{final:.1f}** | {grade} |\n"
        
        return f"""## III. 유형별 수요 분석 (Type Demand v3.1)

### Type Demand v3.1 평가 결과

- **Main Score**: {td.get('main_score', 0):.2f}점
- **Demand Level**: {td.get('demand_level', 'N/A')}
- **Engine Version**: {td.get('version', 'N/A')}

### 유형별 상세 점수 (v7.2 Grading Scale)

{table}

#### v7.2 등급 기준
- **S등급**: 90점 이상 (매우 높음)
- **A등급**: 80~89점 (높음)
- **B등급**: 70~79점 (보통)
- **C등급**: 60~69점 (낮음)
- **D등급**: 60점 미만 (매우 낮음)

---

"""
    
    def _generate_multi_parcel_v3_0(self, mp: Dict, coords: Dict) -> str:
        """
        FIX 4: Full multi_parcel support with combined_center and shape metrics
        """
        is_multi = mp.get('is_multi_parcel', False)
        
        if not is_multi:
            return f"""## IV. Multi-Parcel 분석 (v3.0)

### 단일 필지 모드

- **Is Multi-Parcel**: {is_multi}
- **Parcel Count**: 1
- **Combined Center**: ({coords.get('latitude', 0):.6f}, {coords.get('longitude', 0):.6f})
- **Compactness Ratio**: N/A (단일 필지)
- **Shape Penalty**: N/A (단일 필지)
- **Recommendation**: 단일 필지 분석
- **Version**: {mp.get('version', 'N/A')}

---

"""
        
        # Multi-parcel mode
        center = mp.get('combined_center', {})
        
        return f"""## IV. Multi-Parcel 통합 분석 (v3.0)

### Multi-Parcel v3.0 평가 결과

- **Is Multi-Parcel**: ✅ {is_multi}
- **Parcel Count**: {mp.get('parcel_count', 0)}개
- **Total Area**: {mp.get('total_area', 0):.2f}㎡

### 형상 분석 (Shape Metrics)

- **Combined Center**: ({center.get('latitude', 0):.6f}, {center.get('longitude', 0):.6f})
- **Compactness Ratio**: {mp.get('compactness_ratio', 0):.3f}
- **Shape Penalty**: {mp.get('shape_penalty', 0):.3f}
- **Recommendation Level**: {mp.get('recommendation_level', 'N/A')}

#### Compactness Ratio 해석
- **0.80 이상**: 매우 양호 (정방형에 가까움)
- **0.60~0.79**: 양호 (약간의 불규칙)
- **0.40~0.59**: 보통 (불규칙한 형상)
- **0.40 미만**: 불량 (복잡한 형상, 개발 제약)

#### Shape Penalty 해석
- **0.00~0.05**: 패널티 없음
- **0.06~0.15**: 경미한 패널티
- **0.16~0.30**: 중간 패널티
- **0.31 이상**: 높은 패널티 (형상 개선 필요)

### 통합 개발 권장 사항

{self._get_multi_parcel_recommendation(mp.get('compactness_ratio', 0), mp.get('shape_penalty', 0))}

**Engine Version**: {mp.get('version', 'N/A')}

---

"""
    
    def _generate_geo_optimizer_v3_1(self, geo: Dict) -> str:
        """
        FIX 5: GeoOptimizer with Alternative 1-3 comparison + ASCII charts
        """
        alternatives = geo.get('alternatives', [])
        
        # ASCII chart for scores
        chart = self._generate_ascii_score_chart(geo.get('final_score', 0), alternatives)
        
        # Comparison table
        comparison = self._generate_alternative_comparison_table(geo, alternatives)
        
        return f"""## V. 지리적 최적화 분석 (GeoOptimizer v3.1)

### GeoOptimizer v3.1 종합 평가

- **Final Score**: {geo.get('final_score', 0):.2f}점
- **Weighted Total**: {geo.get('weighted_total', 0):.2f}점
- **Slope Score**: {geo.get('slope_score', 0):.2f}점
- **Noise Score**: {geo.get('noise_score', 0):.2f}점
- **Sunlight Score**: {geo.get('sunlight_score', 0):.2f}점
- **Engine Version**: {geo.get('version', 'N/A')}

### 점수 구성 분석

```
Slope Score    [{self._make_bar(geo.get('slope_score', 0), 100)}] {geo.get('slope_score', 0):.1f}
Noise Score    [{self._make_bar(geo.get('noise_score', 0), 100)}] {geo.get('noise_score', 0):.1f}
Sunlight Score [{self._make_bar(geo.get('sunlight_score', 0), 100)}] {geo.get('sunlight_score', 0):.1f}
─────────────────────────────────────────────────────
Weighted Total [{self._make_bar(geo.get('weighted_total', 0), 100)}] {geo.get('weighted_total', 0):.1f}
Final Score    [{self._make_bar(geo.get('final_score', 0), 100)}] {geo.get('final_score', 0):.1f}
```

### 대안 위치 비교 (Alternative 1~3)

{comparison}

### 대안 위치 점수 비교 차트

{chart}

### 현재 위치 장단점

**강점 (Strengths)**:
{self._format_list(geo.get('current_strengths', []))}

**약점 (Weaknesses)**:
{self._format_list(geo.get('current_weaknesses', []))}

---

"""
    
    def _generate_lh_notice_v2_1(self, notice: Dict, lh: Dict) -> str:
        """
        FIX 3: NoticeRuleEvaluator v7.2 for LH Notice scoring
        """
        # Evaluate notice rules
        notice_score = self._evaluate_notice_rules_v7_2(notice, lh)
        
        return f"""## VI. LH 공고 규칙 분석 (v2.1)

### LH Notice v2.1 평가

- **Version**: {notice.get('version', 'N/A')}
- **Has Recent Notice**: {notice.get('has_recent_notice', False)}
- **Notice Count**: {notice.get('notice_count', 0)}개

### NoticeRuleEvaluator v7.2 평가 결과

**공고 준수 점수**: {notice_score.get('compliance_score', 0):.1f} / 100

| 평가 항목 | 결과 | 점수 |
|-----------|------|------|
| 최근 공고 존재 | {self._yes_no(notice.get('has_recent_notice', False))} | {notice_score.get('recent_notice_score', 0):.0f} |
| 관련 정책 수 | {len(notice.get('relevant_policies', []))}개 | {notice_score.get('policy_score', 0):.0f} |
| LH 등급 적합성 | {lh.get('grade', 'N/A')} | {notice_score.get('grade_score', 0):.0f} |

### 최근 공고 정보

{self._format_latest_notice(notice.get('latest_notice'))}

### 관련 정책

{self._format_list(notice.get('relevant_policies', []))}

---

"""
    
    def _generate_risk_analysis_2025(self, risk: Dict) -> str:
        """
        FIX 8: Full Risk Table quantitative scoring (0~20) using LH_2025 rules
        """
        risk_categories = risk.get('risk_categories', {})
        
        # Calculate detailed risk scores (0-20 scale)
        risk_breakdown = self._calculate_risk_scores_lh_2025(risk)
        
        return f"""## VII. 리스크 분석 (LH 2025 기준)

### Risk Table (LH_2025) 종합 평가

- **Criteria Version**: {risk.get('criteria_version', 'N/A')}
- **Risk Level**: {risk.get('risk_level', 'N/A')}
- **Risk Score**: {risk.get('risk_score', 0):.1f} / 20점
- **Total Risk Count**: {risk.get('total_risk_count', 0)}개

### 리스크 정량 평가 (0~20점 척도)

```
항목별 리스크 점수 (LH 2025 기준)

Legal Risk        [{self._make_bar(risk_breakdown['legal'], 20)}] {risk_breakdown['legal']:.1f}/20
Financial Risk    [{self._make_bar(risk_breakdown['financial'], 20)}] {risk_breakdown['financial']:.1f}/20
Technical Risk    [{self._make_bar(risk_breakdown['technical'], 20)}] {risk_breakdown['technical']:.1f}/20
Environmental     [{self._make_bar(risk_breakdown['environmental'], 20)}] {risk_breakdown['environmental']:.1f}/20
Market Risk       [{self._make_bar(risk_breakdown['market'], 20)}] {risk_breakdown['market']:.1f}/20
─────────────────────────────────────────────────────────
Total Score       [{self._make_bar(risk.get('risk_score', 0), 20)}] {risk.get('risk_score', 0):.1f}/20
```

### 카테고리별 리스크 상세

"""
        
        for category, risks in risk_categories.items():
            if risks:
                report_segment = f"#### {self._translate_risk_category(category)} ({len(risks)}개)\n\n"
                for idx, r in enumerate(risks, 1):
                    report_segment += f"{idx}. {r.get('description', 'N/A')}\n"
                report_segment += "\n"
            else:
                report_segment = f"#### {self._translate_risk_category(category)}\n✅ 해당 없음\n\n"
        
        return report_segment + f"""
### LH 2025 리스크 기준

| 점수 범위 | 등급 | 설명 |
|-----------|------|------|
| 18~20점 | 저위험 | 사업 진행 적극 권장 |
| 15~17점 | 중-저위험 | 일반적 주의사항만 적용 |
| 12~14점 | 중위험 | 특정 리스크 관리 필요 |
| 9~11점 | 중-고위험 | 적극적 대응 전략 수립 |
| 0~8점 | 고위험 | 사업성 재검토 필요 |

**현재 등급**: {risk.get('risk_level', 'N/A')} ({risk.get('risk_score', 0):.1f}점)

---

"""
    
    def _generate_api_reliability_section(self, api: Dict) -> str:
        """
        FIX 7: API reliability/log section
        """
        cache_stats = api.get('cache_stats', {})
        
        return f"""## VIII. API 신뢰성 및 성능 로그

### API Performance Metrics

- **Last Provider Used**: {api.get('last_provider_used', 'N/A')}
- **Retry Count**: {api.get('retry_count', 0)}회
- **API Errors**: {api.get('api_errors', 0)}건
- **Average Response Time**: {api.get('avg_response_time_ms', 0):.0f}ms

### Failover Sequence

```
{' → '.join(api.get('failover_sequence', ['N/A']))}
```

### Cache Statistics

| 지표 | 값 |
|------|-----|
| **Cache Hit Rate** | {cache_stats.get('hit_rate', 0):.1f}% |
| **Total Requests** | {cache_stats.get('total_requests', 0):,}건 |
| **Cache Hits** | {cache_stats.get('cache_hits', 0):,}건 |
| **Cache Misses** | {cache_stats.get('cache_misses', 0):,}건 |

### API Reliability Chart

```
Success [{self._make_bar(100 - api.get('api_errors', 0) * 10, 100)}] {100 - api.get('api_errors', 0) * 10:.0f}%
Cache   [{self._make_bar(cache_stats.get('hit_rate', 0), 100)}] {cache_stats.get('hit_rate', 0):.1f}%
```

---

"""
    
    def _generate_development_info(self, dev: Dict) -> str:
        """Development information"""
        return f"""## IX. 개발 규모 산정

- **예상 세대수**: {dev.get('estimated_units', 0)}세대
- **예상 층수**: {dev.get('estimated_floors', 0)}층
- **건폐율**: {dev.get('building_coverage', 0):.1f}%
- **용적률**: {dev.get('floor_area_ratio', 0):.1f}%
- **주차대수**: {dev.get('parking_spaces', 0)}대

---

"""
    
    def _generate_financial_projections(self, financial: Dict) -> str:
        """Financial projections"""
        return f"""## X. 사업성 분석

- **총 사업비**: {financial.get('total_project_cost', 0):,.0f}원
- **예상 수익**: {financial.get('profit', 0):,.0f}원
- **수익률**: {financial.get('profit_rate', 0):.1f}%
- **ROI**: {financial.get('roi', 0):.1f}%

---

"""
    
    def _generate_negotiation_strategy(self, nego: Dict) -> str:
        """Negotiation strategy"""
        strategies = nego.get('strategies', [])
        
        return f"""## XI. 협상 전략

{self._format_list(strategies)}

---

"""
    
    def _generate_final_recommendation(self, summary: Dict, lh: Dict) -> str:
        """Final recommendation"""
        return f"""## XII. 종합 결론

### 최종 평가

- **적격 여부**: {summary.get('is_eligible', False) and '✅ 적격' or '⚠️ 검토 필요'}
- **LH 등급**: {lh.get('grade', 'N/A')} ({lh.get('total_score', 0):.1f}점)
- **추천**: {lh.get('recommendation', 'N/A')}

---

**보고서 종료**

"""
    
    # Helper methods
    
    def _yes_no(self, value: bool) -> str:
        return "✅ 예" if value else "❌ 아니오"
    
    def _render_fallback(self, value: Any) -> str:
        """Show fallback indicator if value is default/empty"""
        if value in [None, 0, 0.0, "", [], {}, False]:
            return "*(fallback)*"
        return ""
    
    def _format_setback(self, setback: Dict) -> str:
        if not setback:
            return "N/A"
        parts = [f"{k}: {v}m" for k, v in setback.items()]
        return ", ".join(parts)
    
    def _translate_poi_type(self, poi_type: str) -> str:
        translations = {
            "elementary_school": "초등학교",
            "hospital": "병원",
            "subway_station": "지하철역",
            "university": "대학교",
        }
        return translations.get(poi_type, poi_type)
    
    def _get_v7_2_type_grade(self, score: float) -> str:
        """v7.2 Type Demand grading scale"""
        if score >= 90:
            return "S (매우 높음)"
        elif score >= 80:
            return "A (높음)"
        elif score >= 70:
            return "B (보통)"
        elif score >= 60:
            return "C (낮음)"
        else:
            return "D (매우 낮음)"
    
    def _get_multi_parcel_recommendation(self, compactness: float, penalty: float) -> str:
        if compactness >= 0.8 and penalty <= 0.05:
            return "**✅ 강력 추천**: 형상이 매우 양호하여 통합 개발 적극 권장"
        elif compactness >= 0.6 and penalty <= 0.15:
            return "**✅ 추천**: 형상이 양호하여 통합 개발 권장"
        elif compactness >= 0.4 and penalty <= 0.30:
            return "**⚠️ 조건부 추천**: 형상 개선 후 통합 개발 검토"
        else:
            return "**❌ 비추천**: 형상이 불량하여 통합 개발 곤란"
    
    def _make_bar(self, value: float, max_value: float, width: int = 30) -> str:
        """Create ASCII bar chart"""
        if max_value == 0:
            return "─" * width
        filled = int((value / max_value) * width)
        return "█" * filled + "─" * (width - filled)
    
    def _generate_alternative_comparison_table(self, geo: Dict, alternatives: List[Dict]) -> str:
        """Generate comparison table for alternatives"""
        if not alternatives:
            return "현재 위치가 최적 위치입니다."
        
        table = "| 구분 | 위치 | 거리 (m) | 점수 | 이유 |\n"
        table += "|------|------|----------|------|------|\n"
        table += f"| **현재** | 현재 위치 | 0 | {geo.get('final_score', 0):.1f} | - |\n"
        
        for idx, alt in enumerate(alternatives[:3], 1):
            table += f"| 대안{idx} | {alt.get('location', 'N/A')} | {alt.get('distance_m', 0):,.0f} | {alt.get('score', 0):.1f} | {alt.get('reason', 'N/A')} |\n"
        
        return table
    
    def _generate_ascii_score_chart(self, current_score: float, alternatives: List[Dict]) -> str:
        """Generate ASCII chart comparing current vs alternatives"""
        chart = "```\n"
        chart += f"현재 위치  [{self._make_bar(current_score, 100)}] {current_score:.1f}\n"
        
        for idx, alt in enumerate(alternatives[:3], 1):
            score = alt.get('score', 0)
            chart += f"대안 {idx}     [{self._make_bar(score, 100)}] {score:.1f}\n"
        
        chart += "```"
        return chart
    
    def _evaluate_notice_rules_v7_2(self, notice: Dict, lh: Dict) -> Dict[str, float]:
        """NoticeRuleEvaluator v7.2"""
        scores = {}
        
        # Recent notice (40 points)
        scores['recent_notice_score'] = 40 if notice.get('has_recent_notice', False) else 0
        
        # Policy count (30 points)
        policy_count = len(notice.get('relevant_policies', []))
        scores['policy_score'] = min(policy_count * 10, 30)
        
        # LH grade compliance (30 points)
        grade = lh.get('grade', 'C')
        grade_scores = {'A': 30, 'B': 20, 'C': 10, 'D': 0}
        scores['grade_score'] = grade_scores.get(grade, 0)
        
        scores['compliance_score'] = sum(scores.values())
        
        return scores
    
    def _calculate_risk_scores_lh_2025(self, risk: Dict) -> Dict[str, float]:
        """Calculate detailed risk scores using LH 2025 rules"""
        risk_categories = risk.get('risk_categories', {})
        
        # Base score is 20 (no risk), subtract for each risk found
        scores = {
            'legal': 20.0,
            'financial': 20.0,
            'technical': 20.0,
            'environmental': 20.0,
            'market': 20.0,
        }
        
        # Deduct points based on risk count (LH 2025 rules)
        for category, risks in risk_categories.items():
            if category in scores:
                # Each risk deducts 2-5 points depending on severity
                deduction = len(risks) * 3  # Average 3 points per risk
                scores[category] = max(0, scores[category] - deduction)
        
        return scores
    
    def _translate_risk_category(self, category: str) -> str:
        translations = {
            'legal': '법적 리스크',
            'financial': '재무 리스크',
            'technical': '기술적 리스크',
            'environmental': '환경 리스크',
            'market': '시장 리스크',
        }
        return translations.get(category, category)
    
    def _format_list(self, items: List[str]) -> str:
        if not items:
            return "- 없음"
        return "\n".join([f"- {item}" for item in items])
    
    def _format_latest_notice(self, notice: Optional[Dict]) -> str:
        if not notice:
            return "- 최근 공고 없음"
        return f"- {notice}"
    
    def _get_demand_grade(self, level: str) -> str:
        grades = {
            '높음': 'S',
            '보통': 'A',
            '낮음': 'B',
        }
        return grades.get(level, 'N/A')
    
    def _get_score_grade(self, score: float) -> str:
        if score >= 90:
            return 'S'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        else:
            return 'D'
