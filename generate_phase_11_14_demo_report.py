"""
ZeroSite Phase 11-14 Demo Report Generator

Standalone HTML report showcasing Phase 11-14 features:
- Phase 11: LH Policy Rules & Design Philosophy
- Phase 13: Academic Narrative (WHAT/SO WHAT/WHY/INSIGHT)
- Phase 14: Critical Timeline (36-month schedule)

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 1.0
"""

import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.architect.lh_policy_rules import LHPolicyRules, LHSupplyType
from app.report.narrative_engine import AcademicNarrativeEngine
from app.timeline.critical_path import CriticalPathAnalyzer


def generate_demo_html(
    address: str,
    land_area: float,
    unit_type: str = "청년",
    far: float = 200.0
) -> str:
    """Generate standalone demo HTML report"""
    
    print(f"\n{'='*80}")
    print("🎨 Phase 11-14 Demo Report Generator")
    print(f"{'='*80}\n")
    
    # Initialize engines
    lh_policy = LHPolicyRules()
    narrative_engine = AcademicNarrativeEngine()
    timeline_analyzer = CriticalPathAnalyzer()
    
    # Map unit type
    supply_type_map = {
        "청년": LHSupplyType.YOUTH,
        "신혼부부": LHSupplyType.NEWLYWED,
        "고령자": LHSupplyType.SENIOR,
        "일반": LHSupplyType.GENERAL,
        "혼합": LHSupplyType.MIXED
    }
    supply_type = supply_type_map.get(unit_type, LHSupplyType.YOUTH)
    
    # ============================================================
    # Phase 11: LH Policy Rules
    # ============================================================
    print("🏗️ Phase 11: LH Policy Rules...")
    
    buildable_area = land_area * (far / 100)
    unit_distribution = lh_policy.calculate_total_units(buildable_area, supply_type)
    design_philosophy = lh_policy.get_design_philosophy(supply_type)
    common_area_ratio = lh_policy.get_common_area_ratio()
    parking_ratio = lh_policy.get_parking_ratio("seoul")
    
    total_units = sum(u["count"] for u in unit_distribution.values())
    print(f"   ✅ Total Units: {total_units}세대")
    
    # ============================================================
    # Phase 13: Academic Narrative
    # ============================================================
    print("📝 Phase 13: Academic Narrative...")
    
    design_result = {
        "total_units": total_units,
        "total_gfa": buildable_area,
        "supply_type": unit_type
    }
    
    financial_result = {
        "roi": 2.5,
        "capex": buildable_area * 2_500_000
    }
    
    lh_score = {
        "total_score": 85.0,
        "grade": "B"
    }
    
    narratives = narrative_engine.generate_full_narrative(
        design_result, financial_result, lh_score
    )
    print(f"   ✅ Generated {len(narratives)} sections")
    
    # ============================================================
    # Phase 14: Critical Timeline
    # ============================================================
    print("📅 Phase 14: Critical Timeline...")
    
    timeline = timeline_analyzer.generate_timeline()
    print(f"   ✅ Timeline: {timeline.total_duration_months} months\n")
    
    # ============================================================
    # Generate HTML
    # ============================================================
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZeroSite Phase 11-14 Demo Report - {address}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #005BAC 0%, #003D73 100%);
            color: white;
            padding: 40px;
            margin: -40px -40px 40px -40px;
            border-radius: 8px 8px 0 0;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 30px 0;
            padding: 20px;
            background: #E6F2FF;
            border-radius: 8px;
        }}
        
        .meta-item {{
            text-align: center;
        }}
        
        .meta-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .meta-value {{
            font-size: 24px;
            font-weight: 700;
            color: #005BAC;
        }}
        
        .section {{
            margin: 40px 0;
            padding: 30px;
            background: #fafafa;
            border-left: 4px solid #005BAC;
        }}
        
        .section-title {{
            font-size: 24px;
            color: #005BAC;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #005BAC;
        }}
        
        .subsection {{
            margin: 20px 0;
        }}
        
        .subsection-title {{
            font-size: 18px;
            color: #333;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .unit-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .unit-table th,
        .unit-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        .unit-table th {{
            background: #005BAC;
            color: white;
            font-weight: 600;
        }}
        
        .unit-table tr:hover {{
            background: #f5f5f5;
        }}
        
        .narrative-box {{
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #D4AF37;
        }}
        
        .narrative-title {{
            font-size: 16px;
            font-weight: 700;
            color: #005BAC;
            margin-bottom: 10px;
        }}
        
        .narrative-content {{
            font-size: 14px;
            line-height: 1.8;
            color: #555;
        }}
        
        .key-points {{
            margin-top: 15px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        
        .key-points ul {{
            margin-left: 20px;
        }}
        
        .key-points li {{
            margin: 5px 0;
            color: #666;
        }}
        
        .timeline-phase {{
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #27AE60;
        }}
        
        .timeline-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .phase-name {{
            font-size: 16px;
            font-weight: 700;
            color: #333;
        }}
        
        .phase-duration {{
            font-size: 14px;
            color: white;
            background: #27AE60;
            padding: 5px 15px;
            border-radius: 20px;
        }}
        
        .critical-badge {{
            display: inline-block;
            background: #C0392B;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
        }}
        
        .phase-description {{
            font-size: 14px;
            color: #666;
            margin: 10px 0;
        }}
        
        .milestone-list {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        
        .milestone-list li {{
            margin: 5px 0;
            color: #555;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px 0 0 0;
            color: #999;
            font-size: 14px;
            border-top: 1px solid #ddd;
            margin-top: 40px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin: 5px;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-info {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 ZeroSite Phase 11-14 Demo Report</h1>
            <div class="subtitle">LH Policy-Driven Design | Academic Narrative | Critical Timeline</div>
        </div>
        
        <div class="meta-grid">
            <div class="meta-item">
                <div class="meta-label">📍 Address</div>
                <div class="meta-value" style="font-size: 16px;">{address}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">📏 Land Area</div>
                <div class="meta-value">{land_area:,.0f}㎡</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">🏠 Housing Type</div>
                <div class="meta-value" style="font-size: 18px;">{unit_type}형</div>
            </div>
        </div>
        
        <!-- Phase 11: LH Policy Rules -->
        <div class="section">
            <div class="section-title">🏗️ Phase 11: LH Policy-Driven Design</div>
            
            <div class="subsection">
                <div class="subsection-title">📊 Unit Distribution</div>
                <table class="unit-table">
                    <thead>
                        <tr>
                            <th>Unit Type</th>
                            <th>Area (㎡)</th>
                            <th>Count (세대)</th>
                            <th>Total Area (㎡)</th>
                        </tr>
                    </thead>
                    <tbody>"""
    
    # Add unit distribution rows
    for unit_type_key, unit_data in unit_distribution.items():
        html += f"""
                        <tr>
                            <td>{unit_type_key}</td>
                            <td>{unit_data.get('area', unit_data.get('area_sqm', 0)):.1f}㎡</td>
                            <td><strong>{unit_data['count']}세대</strong></td>
                            <td>{unit_data.get('total', unit_data.get('area', 0) * unit_data['count']):.1f}㎡</td>
                        </tr>"""
    
    html += f"""
                    </tbody>
                </table>
                
                <div style="margin: 20px 0; padding: 15px; background: white; border-radius: 8px;">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; text-align: center;">
                        <div>
                            <div style="font-size: 12px; color: #666;">총 세대수</div>
                            <div style="font-size: 24px; font-weight: 700; color: #005BAC;">{total_units}세대</div>
                        </div>
                        <div>
                            <div style="font-size: 12px; color: #666;">공용공간 비율</div>
                            <div style="font-size: 24px; font-weight: 700; color: #27AE60;">{common_area_ratio * 100:.0f}%</div>
                        </div>
                        <div>
                            <div style="font-size: 12px; color: #666;">주차 기준</div>
                            <div style="font-size: 24px; font-weight: 700; color: #D4AF37;">{parking_ratio}대/세대</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="subsection">
                <div class="subsection-title">💡 Design Philosophy</div>
                <div style="background: white; padding: 20px; border-radius: 8px; line-height: 1.8;">
                    {design_philosophy}
                </div>
            </div>
        </div>
        
        <!-- Phase 13: Academic Narrative -->
        <div class="section">
            <div class="section-title">📝 Phase 13: Academic Narrative</div>
            <div class="subsection-title" style="margin-bottom: 20px;">
                KDI Research Report Style | WHAT / SO WHAT / WHY / INSIGHT / CONCLUSION
            </div>
"""
    
    # Add narrative sections
    for narrative in narratives:
        html += f"""
            <div class="narrative-box">
                <div class="narrative-title">📌 {narrative.title}</div>
                <div class="narrative-content">{narrative.content}</div>
                <div class="key-points">
                    <strong>Key Points:</strong>
                    <ul>
"""
        for point in narrative.key_points:
            html += f"                        <li>{point}</li>\n"
        
        html += """
                    </ul>
                </div>
            </div>
"""
    
    html += f"""
        </div>
        
        <!-- Phase 14: Critical Timeline -->
        <div class="section">
            <div class="section-title">📅 Phase 14: Critical Timeline & Risk Analysis</div>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: center;">
                    <div>
                        <div style="font-size: 12px; color: #666;">Total Duration</div>
                        <div style="font-size: 28px; font-weight: 700; color: #005BAC;">{timeline.total_duration_months}</div>
                        <div style="font-size: 14px; color: #999;">months</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #666;">Critical Phases</div>
                        <div style="font-size: 28px; font-weight: 700; color: #C0392B;">{len([p for p in timeline.phases if p.is_critical])}</div>
                        <div style="font-size: 14px; color: #999;">phases</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #666;">Key Risks</div>
                        <div style="font-size: 28px; font-weight: 700; color: #E67E22;">{len(timeline.key_risks)}</div>
                        <div style="font-size: 14px; color: #999;">identified</div>
                    </div>
                </div>
            </div>
            
            <div class="subsection">
                <div class="subsection-title">🗓️ Project Phases</div>
"""
    
    # Add timeline phases
    for phase in timeline.phases:
        critical_badge = '<span class="critical-badge">CRITICAL PATH</span>' if phase.is_critical else ''
        html += f"""
                <div class="timeline-phase">
                    <div class="timeline-header">
                        <div class="phase-name">{phase.phase_name} {critical_badge}</div>
                        <div class="phase-duration">{phase.duration_months} months</div>
                    </div>
                    <div class="phase-description">{phase.description}</div>
                    <div style="margin-top: 10px;">
                        <strong>Key Milestones:</strong>
                        <ul class="milestone-list">
"""
        for milestone in phase.key_milestones:
            html += f"                            <li>{milestone}</li>\n"
        
        html += """
                        </ul>
                    </div>
"""
        
        if phase.risks:
            html += """
                    <div style="margin-top: 10px; padding: 10px; background: #fff3cd; border-radius: 4px;">
                        <strong style="color: #856404;">⚠️ Risks:</strong>
                        <ul style="margin-top: 5px; margin-left: 20px;">
"""
            for risk in phase.risks[:3]:  # Show top 3 risks
                html += f"                            <li style=\"color: #856404;\">{risk}</li>\n"
            
            html += """
                        </ul>
                    </div>
"""
        
        html += """
                </div>
"""
    
    html += f"""
            </div>
        </div>
        
        <div class="footer">
            <p><strong>ZeroSite Phase 11-14 Demo Report</strong></p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="margin-top: 10px;">
                <span class="badge badge-success">Phase 11: LH Policy Rules ✓</span>
                <span class="badge badge-info">Phase 13: Academic Narrative ✓</span>
                <span class="badge badge-warning">Phase 14: Critical Timeline ✓</span>
            </p>
            <p style="margin-top: 15px; font-size: 12px; color: #ccc;">
                © {datetime.now().year} ZeroSite Development Team + GenSpark AI
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Generate demo report"""
    
    # Test data
    test_cases = [
        {
            "address": "서울특별시 강남구 테헤란로 123",
            "land_area": 1000.0,
            "unit_type": "청년",
            "far": 200.0,
            "filename": "demo_gangnam_youth.html"
        },
        {
            "address": "서울특별시 마포구 월드컵북로 120",
            "land_area": 2000.0,
            "unit_type": "신혼부부",
            "far": 250.0,
            "filename": "demo_mapo_newlywed.html"
        }
    ]
    
    output_dir = Path("generated_reports")
    output_dir.mkdir(exist_ok=True)
    
    for test_case in test_cases:
        filename = test_case.pop("filename")
        
        print(f"\n📄 Generating: {filename}")
        html = generate_demo_html(**test_case)
        
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Saved to: {output_path}")
        print(f"📏 Size: {len(html):,} characters\n")
    
    print("="*80)
    print("✅ All demo reports generated successfully!")
    print("="*80)
    print(f"\n📂 Output directory: {output_dir.absolute()}")
    print(f"📄 Files generated: {len(test_cases)}")
    print("\n💡 Next: Start HTTP server to view reports")


if __name__ == "__main__":
    main()
