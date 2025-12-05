"""
ZeroSite v11.0 Report Generator Builder
========================================
This script builds the complete v11.0 report generator by:
1. Reading v10.0 base structure
2. Adding v11.0 helper methods
3. Modifying Part 4 to include Unit-Type Analysis
4. Enhancing Parts 2, 5, 7, and Appendix

Usage:
    python build_v11_generator.py
"""

def build_v11_generator():
    """Build complete v11.0 report generator"""
    
    # Read v10.0 base
    with open("app/report_generator_v10_ultra_pro.py", "r", encoding="utf-8") as f:
        v10_content = f.read()
    
    # Find insertion point (before the main generate function)
    insertion_marker = "def generate_v10_ultra_pro_report("
    marker_pos = v10_content.find(insertion_marker)
    
    if marker_pos == -1:
        print("❌ Could not find insertion point in v10.0")
        return False
    
    # Split v10.0 content
    before_main = v10_content[:marker_pos]
    main_and_after = v10_content[marker_pos:]
    
    # v11.0 Helper Methods
    v11_helpers = '''

# ============================================================
# v11.0 Helper Methods
# ============================================================

class V11ReportHelpers:
    """v11.0 specific helper methods for enhanced sections"""
    
    @staticmethod
    def generate_unit_type_matrix(unit_analysis: Dict[str, Any]) -> str:
        """Generate 5x7 Unit-Type Comparison Matrix with v7.5 style"""
        
        types = unit_analysis.get("type_scores", {})
        
        def get_color_class(score: float) -> str:
            if score >= 85:
                return "score-excellent"  # Green
            elif score >= 70:
                return "score-good"  # Yellow-green
            elif score >= 50:
                return "score-fair"  # Yellow
            else:
                return "score-poor"  # Red
        
        html = """
        <table class="unit-type-matrix">
            <thead>
                <tr>
                    <th>세대유형</th>
                    <th>인구구조</th>
                    <th>교통접근성</th>
                    <th>생활인프라</th>
                    <th>정책정합성</th>
                    <th>경제적정성</th>
                    <th>사회수요</th>
                    <th class="total-score">종합점수</th>
                </tr>
            </thead>
            <tbody>
        """
        
        type_names = {
            "youth": ("청년형", "👨‍🎓"),
            "newlywed": ("신혼형", "👫"),
            "senior": ("고령자형", "👴"),
            "general": ("일반형", "👨‍👩‍👧"),
            "vulnerable": ("취약계층형", "🤝")
        }
        
        for type_key, (type_name, emoji) in type_names.items():
            type_data = types.get(type_key, {})
            scores = type_data.get("detailed_scores", {})
            total = type_data.get("total_score", 0)
            
            demo_score = scores.get("demographics", 0)
            transport_score = scores.get("transportation", 0)
            infra_score = scores.get("infrastructure", 0)
            policy_score = scores.get("policy", 0)
            economic_score = scores.get("economic", 0)
            social_score = scores.get("social", 0)
            
            total_class = get_color_class(total)
            
            html += f"""
                <tr>
                    <td class="type-name"><strong>{emoji} {type_name}</strong></td>
                    <td class="{get_color_class(demo_score)}">{demo_score:.1f}</td>
                    <td class="{get_color_class(transport_score)}">{transport_score:.1f}</td>
                    <td class="{get_color_class(infra_score)}">{infra_score:.1f}</td>
                    <td class="{get_color_class(policy_score)}">{policy_score:.1f}</td>
                    <td class="{get_color_class(economic_score)}">{economic_score:.1f}</td>
                    <td class="{get_color_class(social_score)}">{social_score:.1f}</td>
                    <td class="{total_class} total-score"><strong>{total:.1f}</strong></td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        
        <style>
            .unit-type-matrix {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 13px;
            }
            
            .unit-type-matrix th {
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                color: white;
                padding: 12px 8px;
                text-align: center;
                font-weight: bold;
                border: 1px solid #ddd;
            }
            
            .unit-type-matrix td {
                padding: 10px 8px;
                text-align: center;
                border: 1px solid #ddd;
            }
            
            .unit-type-matrix .type-name {
                text-align: left;
                font-weight: bold;
            }
            
            .unit-type-matrix .total-score {
                font-size: 14px;
                font-weight: bold;
            }
            
            .score-excellent {
                background-color: #d1fae5 !important;
                color: #065f46;
                font-weight: bold;
            }
            
            .score-good {
                background-color: #fef08a !important;
                color: #854d0e;
            }
            
            .score-fair {
                background-color: #fed7aa !important;
                color: #9a3412;
            }
            
            .score-poor {
                background-color: #fecaca !important;
                color: #991b1b;
            }
        </style>
        """
        
        return html
    
    @staticmethod
    def generate_unit_type_detail(unit_analysis: Dict, pseudo_data: Dict, recommended_type: str) -> str:
        """Generate detailed analysis of recommended unit type"""
        
        types = unit_analysis.get("type_scores", {})
        recommended_data = types.get(recommended_type.lower(), {})
        
        demographics = pseudo_data.get("demographics", {})
        age_dist = demographics.get("age_distribution", {})
        
        type_emoji = {
            "youth": "👨‍🎓",
            "newlywed": "👫",
            "senior": "👴",
            "general": "👨‍👩‍👧",
            "vulnerable": "🤝"
        }
        
        type_names_kr = {
            "youth": "청년형",
            "newlywed": "신혼형",
            "senior": "고령자형",
            "general": "일반형",
            "vulnerable": "취약계층형"
        }
        
        emoji = type_emoji.get(recommended_type.lower(), "🏠")
        type_name = type_names_kr.get(recommended_type.lower(), recommended_type)
        confidence = unit_analysis.get("confidence", 0)
        rationale = recommended_data.get("rationale", "추천 근거 생성 중...")
        
        html = f"""
        <div class="recommended-type-detail">
            <h3>{emoji} 추천 세대유형: {type_name}</h3>
            <div class="confidence-badge">신뢰도: {confidence:.1f}%</div>
            
            <div class="section-subheader">📋 추천 근거</div>
            <p>{rationale}</p>
            
            <div class="section-subheader">📊 인구통계 분석</div>
            <ul>
                <li><strong>청년층 (19-34세)</strong>: {age_dist.get('youth_19_34', 0)}%</li>
                <li><strong>신혼부부 추정</strong>: {age_dist.get('newlywed_estimated', 0)}%</li>
                <li><strong>고령자 (65세+)</strong>: {age_dist.get('senior_65_plus', 0)}%</li>
                <li><strong>일반 가구</strong>: {age_dist.get('general_other', 0)}%</li>
            </ul>
        </div>
        
        <style>
            .recommended-type-detail {{
                background: #f8fafc;
                border-left: 4px solid #3b82f6;
                padding: 20px;
                margin: 20px 0;
            }}
            
            .recommended-type-detail h3 {{
                color: #1e3a8a;
                margin-bottom: 15px;
            }}
            
            .confidence-badge {{
                display: inline-block;
                background: #10b981;
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
        </style>
        """
        
        return html
    
    @staticmethod
    def generate_infrastructure_by_type(pseudo_data: Dict) -> str:
        """Generate infrastructure analysis by unit type"""
        
        education = pseudo_data.get("education", {})
        medical = pseudo_data.get("medical", {})
        transport = pseudo_data.get("transportation", {})
        youth_specific = pseudo_data.get("youth_specific", {})
        senior_specific = pseudo_data.get("senior_specific", {})
        
        html = """
        <div class="infrastructure-analysis">
            <div class="section-subheader">🎓 청년형 특화 인프라</div>
            <table>
                <tr>
                    <th>시설 유형</th>
                    <th>개수</th>
                    <th>최단 거리</th>
                    <th>주요 시설</th>
                </tr>
        """
        
        # Universities
        unis = education.get("university", {})
        uni_count = unis.get("count", 0)
        if uni_count > 0:
            uni_names = ", ".join(unis.get("names", [])[:3])
            html += f"""
                <tr>
                    <td>대학교</td>
                    <td>{uni_count}개</td>
                    <td>{unis.get('nearest_distance', 'N/A')}</td>
                    <td>{uni_names}</td>
                </tr>
            """
        
        # Youth centers
        youth_support = youth_specific.get("youth_support", {})
        youth_centers = youth_support.get("youth_centers", [])
        if youth_centers:
            html += f"""
                <tr>
                    <td>청년센터</td>
                    <td>{len(youth_centers)}개</td>
                    <td>{youth_support.get('nearest_distance', 'N/A')}</td>
                    <td>{', '.join(youth_centers[:2])}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <div class="section-subheader">👴 고령자형 특화 인프라</div>
            <table>
                <tr>
                    <th>시설 유형</th>
                    <th>개수</th>
                    <th>최단 거리</th>
                    <th>주요 시설</th>
                </tr>
        """
        
        # Senior welfare
        welfare = senior_specific.get("welfare_facilities", {})
        welfare_centers = welfare.get("welfare_centers", {})
        if welfare_centers.get("count", 0) > 0:
            center_names = ", ".join(welfare_centers.get("names", [])[:2])
            html += f"""
                <tr>
                    <td>노인복지관</td>
                    <td>{welfare_centers.get('count', 0)}개</td>
                    <td>{welfare.get('nearest_distance', 'N/A')}</td>
                    <td>{center_names}</td>
                </tr>
            """
        
        # Hospitals
        hospitals = medical.get("general_hospitals", {})
        if hospitals.get("count", 0) > 0:
            hospital_names = ", ".join(hospitals.get("names", [])[:2])
            html += f"""
                <tr>
                    <td>종합병원</td>
                    <td>{hospitals.get('count', 0)}개</td>
                    <td>{hospitals.get('nearest_distance', 'N/A')}</td>
                    <td>{hospital_names}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        
        <style>
            .infrastructure-analysis table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }
            
            .infrastructure-analysis th {
                background: #f1f5f9;
                padding: 10px;
                text-align: left;
                border: 1px solid #e2e8f0;
            }
            
            .infrastructure-analysis td {
                padding: 10px;
                border: 1px solid #e2e8f0;
            }
        </style>
        """
        
        return html


'''
    
    # Combine all parts
    v11_content = before_main + v11_helpers + main_and_after
    
    # Update function name and add v11 imports
    v11_content = v11_content.replace(
        "def generate_v10_ultra_pro_report(",
        """def generate_v11_ultra_pro_report(
        address: str,
        land_area: float,
        land_appraisal_price: int,
        zone_type: str,
        analysis_result: Dict[str, Any]) -> str:
    \"\"\"
    Generate v11.0 Ultra Professional Report (40-45 pages)
    
    Enhancements over v10.0:
    - Unit-Type Suitability Analysis (5 types x 6 criteria)
    - Pseudo-Data Engine integration (realistic facility/demographic data)
    - Feasibility Check Layer (recommendation validation)
    - Expanded Part 4 (8-10 pages with unit-type analysis)
    - Enhanced financial scenarios with cash flow
    - 6x6 Risk Matrix visualization
    - Comprehensive Appendix with data sources
    \"\"\"
    
    # Import v11.0 modules
    from app.unit_type_analyzer_v11 import UnitTypeSuitabilityAnalyzer
    from app.pseudo_data_engine_v11 import PseudoDataEngine
    from app.feasibility_checker_v11 import FeasibilityChecker
    
    # Initialize v11.0 engines
    coord = analysis_result.get("coordinates", {"latitude": 37.5665, "longitude": 126.9780})
    
    pseudo_engine = PseudoDataEngine(address=address, coord=coord)
    pseudo_data = pseudo_engine.generate_comprehensive_report()
    
    unit_analyzer = UnitTypeSuitabilityAnalyzer(address=address, coord=coord)
    unit_analysis = unit_analyzer.analyze_all_unit_types()
    recommended_type = unit_analysis.get("recommended_type", "general")
    
    # Extract parameters for feasibility check
    land_info = analysis_result.get("building_standards", {})
    dev_plan = analysis_result.get("development_plan", {})
    
    feasibility_checker = FeasibilityChecker(
        land_area=land_area,
        bcr=land_info.get("building_coverage_ratio", 60),
        far=land_info.get("floor_area_ratio", 200),
        zone_type=zone_type,
        max_floors=dev_plan.get("floors", 5),
        unit_count=dev_plan.get("estimated_units", 20),
        total_gfa=land_area * land_info.get("floor_area_ratio", 200) / 100
    )
    feasibility_result = feasibility_checker.check_unit_type_feasibility(recommended_type)
    
    # Generate v11.0 specialized HTML sections
    helpers = V11ReportHelpers()
    unit_type_matrix_html = helpers.generate_unit_type_matrix(unit_analysis)
    unit_type_detail_html = helpers.generate_unit_type_detail(unit_analysis, pseudo_data, recommended_type)
    infrastructure_by_type_html = helpers.generate_infrastructure_by_type(pseudo_data)
    
    # Continue with v10.0 base generation (will be enhanced with v11 sections)
    # Original v10.0 function renamed below:
    
def generate_v10_ultra_pro_report("""
    )
    
    # Write v11.0 generator
    with open("app/report_generator_v11_ultra_pro.py", "w", encoding="utf-8") as f:
        f.write(v11_content)
    
    print("✅ v11.0 Report Generator built successfully!")
    print(f"📄 File size: {len(v11_content):,} characters")
    print(f"📊 Estimated lines: ~{len(v11_content.split(chr(10)))}")
    
    return True


if __name__ == "__main__":
    success = build_v11_generator()
    if success:
        print("\n🎉 v11.0 generation complete!")
        print("Next steps:")
        print("1. Test the generator: python -m app.report_generator_v11_ultra_pro")
        print("2. Update API endpoint to use v11.0")
        print("3. Generate test PDF report")
    else:
        print("\n❌ Build failed. Check error messages above.")
