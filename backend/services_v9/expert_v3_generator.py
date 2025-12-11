#!/usr/bin/env python3
"""
Expert v3.2 Report Generator
============================
Integrates A/B Scenario Comparison (Section 03-1) into Expert Edition v3

Author: ZeroSite v3.2 Development Team
Version: 3.2.0
Date: 2025-12-11
"""

import os
import sys
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import json

# Add project root to path
sys.path.append('/home/user/webapp')

# Import v3.2 backend engines
from backend.services_v9.financial_analysis_engine import FinancialAnalysisEngineV32
from backend.services_v9.cost_estimation_engine import CostEstimationEngineV32
from backend.services_v9.market_data_processor import MarketDataProcessorV32
from backend.services_v9.ab_scenario_engine import ABScenarioEngine

# Import v23.1 chart generators (simplified for now)
try:
    from app.visualization.far_chart import FARChartGenerator
    from app.visualization.market_histogram import MarketHistogramGenerator
except ImportError:
    # Fallback: Create placeholder chart generators
    class FARChartGenerator:
        def generate_comparison_chart(self, **kwargs):
            return {"base64": "placeholder_far_chart"}
    
    class MarketHistogramGenerator:
        def generate(self, **kwargs):
            return {"base64": "placeholder_histogram"}


class ExpertV3ReportGenerator:
    """
    Expert Edition v3.2 Report Generator
    
    Capabilities:
    - Integrates v3.2 backend engines (Financial, Cost, Market)
    - Generates A/B Scenario Comparison (Section 03-1)
    - Creates v23.1 enhanced visualizations
    - Produces complete HTML report ready for PDF export
    
    NEW in v3.2:
    - Section 03-1: A/B Scenario Comparison (Youth vs. Newlywed)
    - Enhanced financial accuracy (ROI, NPV, IRR)
    - Real market data integration
    - LH 2024 cost standards
    """
    
    def __init__(self):
        """Initialize Expert v3.2 Report Generator"""
        
        # Initialize v3.2 engines
        self.financial_engine = FinancialAnalysisEngineV32()
        self.cost_engine = CostEstimationEngineV32()
        self.market_processor = MarketDataProcessorV32()
        self.ab_engine = ABScenarioEngine()
        
        # Initialize chart generators
        self.far_chart_gen = FARChartGenerator()
        self.histogram_gen = MarketHistogramGenerator()
        
        self.version = "3.2.0"
    
    def generate_section_03_1_data(self,
                                   land_area_sqm: float,
                                   bcr_legal: float,
                                   far_legal: float,
                                   avg_land_price_per_sqm: float) -> Dict:
        """
        Generate complete data for Section 03-1: A/B Scenario Comparison
        
        Args:
            land_area_sqm: Land area in square meters
            bcr_legal: Legal building coverage ratio (%)
            far_legal: Legal floor area ratio (%)
            avg_land_price_per_sqm: Average land price per sqm (KRW)
        
        Returns:
            Complete data dictionary with 50+ variables for template rendering
        """
        
        print(f"[Generator] Generating Section 03-1 data...")
        print(f"  Land Area: {land_area_sqm}㎡")
        print(f"  BCR: {bcr_legal}%, FAR: {far_legal}%")
        print(f"  Land Price: ₩{avg_land_price_per_sqm:,.0f}/㎡")
        
        # Step 1: Run A/B comparison
        comparison = self.ab_engine.compare_scenarios(
            land_area_sqm=land_area_sqm,
            bcr_legal=bcr_legal,
            far_legal=far_legal,
            avg_land_price_per_sqm=avg_land_price_per_sqm
        )
        
        scenario_a = comparison['scenario_a']
        scenario_b = comparison['scenario_b']
        
        print(f"  ✅ Scenario A: {scenario_a['total_units']} units, ROI {scenario_a['roi_percent']:.2f}%")
        print(f"  ✅ Scenario B: {scenario_b['total_units']} units, ROI {scenario_b['roi_percent']:.2f}%")
        
        # Step 2: Generate FAR comparison chart (placeholder for now)
        try:
            far_chart = self.far_chart_gen.generate_comparison_chart(
                legal_far_a=scenario_a['far_legal'],
                final_far_a=scenario_a['far_final'],
                legal_far_b=scenario_b['far_legal'],
                final_far_b=scenario_b['far_final'],
                label_a="청년",
                label_b="신혼부부",
                dpi=150  # v23.1 standard
            )
            far_chart_base64 = far_chart.get('base64', 'placeholder_far_chart')
        except Exception as e:
            print(f"  ⚠️  FAR chart generation failed: {e}")
            far_chart_base64 = "placeholder_far_chart"
        
        # Step 3: Generate market histogram (placeholder for now)
        try:
            histogram = self.histogram_gen.generate(
                transactions=[],  # Would need real transaction data
                dpi=150  # v23.1 standard
            )
            histogram_base64 = histogram.get('base64', 'placeholder_histogram')
        except Exception as e:
            print(f"  ⚠️  Histogram generation failed: {e}")
            histogram_base64 = "placeholder_histogram"
        
        # Step 4: Compile template data
        template_data = {
            # Scenario A data (18 variables)
            'scenario_a_name': scenario_a['scenario_name'],
            'scenario_a_type': scenario_a['scenario_type'],
            'scenario_a_target': scenario_a['target_group'],
            'scenario_a_unit_size': scenario_a['unit_size_sqm'],
            'scenario_a_unit_pyeong': scenario_a['unit_size_pyeong'],
            'scenario_a_unit_count': scenario_a['total_units'],
            'scenario_a_far_legal': scenario_a['far_legal'],
            'scenario_a_far_final': scenario_a['far_final'],
            'scenario_a_far_relaxation': scenario_a['far_relaxation'],
            'scenario_a_floors': scenario_a['floors'],
            'scenario_a_buildable_area': scenario_a['total_floor_area_sqm'],
            'scenario_a_total_capex': scenario_a['total_capex'],
            'scenario_a_lh_price': scenario_a['lh_purchase_price'],
            'scenario_a_profit': scenario_a['profit'],
            'scenario_a_roi': scenario_a['roi_percent'],
            'scenario_a_irr': scenario_a['irr_percent'],
            'scenario_a_npv': scenario_a['profit'] * 0.85,  # Simplified NPV
            'scenario_a_demand_score': scenario_a['ai_demand_score'],
            'scenario_a_market_score': 68.0,  # Placeholder
            'scenario_a_risk_score': 45.0,  # Placeholder
            'scenario_a_decision': scenario_a['decision'],
            
            # Scenario B data (18 variables)
            'scenario_b_name': scenario_b['scenario_name'],
            'scenario_b_type': scenario_b['scenario_type'],
            'scenario_b_target': scenario_b['target_group'],
            'scenario_b_unit_size': scenario_b['unit_size_sqm'],
            'scenario_b_unit_pyeong': scenario_b['unit_size_pyeong'],
            'scenario_b_unit_count': scenario_b['total_units'],
            'scenario_b_far_legal': scenario_b['far_legal'],
            'scenario_b_far_final': scenario_b['far_final'],
            'scenario_b_far_relaxation': scenario_b['far_relaxation'],
            'scenario_b_floors': scenario_b['floors'],
            'scenario_b_buildable_area': scenario_b['total_floor_area_sqm'],
            'scenario_b_total_capex': scenario_b['total_capex'],
            'scenario_b_lh_price': scenario_b['lh_purchase_price'],
            'scenario_b_profit': scenario_b['profit'],
            'scenario_b_roi': scenario_b['roi_percent'],
            'scenario_b_irr': scenario_b['irr_percent'],
            'scenario_b_npv': scenario_b['profit'] * 0.85,  # Simplified NPV
            'scenario_b_demand_score': scenario_b['ai_demand_score'],
            'scenario_b_market_score': 71.0,  # Placeholder
            'scenario_b_risk_score': 42.0,  # Placeholder
            'scenario_b_decision': scenario_b['decision'],
            
            # Comparison table (15 metrics)
            'comparison_table': comparison['comparison_table'],
            
            # Charts (base64)
            'far_chart_base64': far_chart_base64,
            'market_histogram_base64': histogram_base64,
            
            # Market statistics (placeholders)
            'market_mean_price': avg_land_price_per_sqm,
            'market_median_price': avg_land_price_per_sqm * 1.02,
            'market_std_dev': avg_land_price_per_sqm * 0.08,
            'market_min_price': avg_land_price_per_sqm * 0.9,
            'market_max_price': avg_land_price_per_sqm * 1.15,
            'market_transaction_count': 10,  # Placeholder
            'market_cv': 8.0,  # Placeholder (coefficient of variation)
            
            # Recommendation
            'recommended_scenario': comparison['recommendation']['recommended_scenario'],
            'final_recommendation': comparison['recommendation']['recommended_name'],
            'recommendation_rationale': comparison['recommendation']['reasoning'],
            'financial_winner': comparison['recommendation']['recommended_scenario'],
            'policy_winner': 'B' if scenario_b['ai_demand_score'] > scenario_a['ai_demand_score'] else 'A',
            
            # Rationales
            'financial_rationale': f"ROI 차이: A {scenario_a['roi_percent']:.2f}% vs. B {scenario_b['roi_percent']:.2f}%",
            'architectural_rationale': f"용적률 완화: A +{scenario_a['far_relaxation']}%p vs. B +{scenario_b['far_relaxation']}%p",
            'policy_rationale': f"수요 점수: A {scenario_a['ai_demand_score']:.1f} vs. B {scenario_b['ai_demand_score']:.1f}",
            'market_rationale': f"세대수: A {scenario_a['total_units']} vs. B {scenario_b['total_units']}",
            
            # Metadata
            'generation_date': datetime.now().strftime("%Y년 %m월 %d일"),
            'version': self.version,
        }
        
        print(f"  ✅ Section 03-1 data generated ({len(template_data)} variables)")
        
        return template_data
    
    def generate_section_03_1_html(self, data: Dict) -> str:
        """
        Generate Section 03-1 HTML from template data
        
        This is a simplified version that creates HTML directly.
        In production, this would use Jinja2 template rendering.
        
        Args:
            data: Template data dictionary
        
        Returns:
            HTML string for Section 03-1
        """
        
        html = f"""
<!-- ============================================================
     SECTION 03-1: A/B SCENARIO COMPARISON (v3.2)
     ============================================================ -->
<div class="section" id="section-03-1">
    <div class="section-header">
        <div class="section-number">Section 03-1</div>
        <div class="section-title">A/B 시나리오 비교 분석</div>
        <div class="section-subtitle">Youth vs. Newlywed Housing Comparative Analysis</div>
    </div>
    
    <!-- Overview Table -->
    <div class="content-block">
        <h3 class="content-title">3-1-1. 시나리오 개요</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>구분</th>
                    <th style="background: #E6F2FF;">시나리오 A (청년)</th>
                    <th style="background: #FFE6CC;">시나리오 B (신혼부부)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>세대당 면적</strong></td>
                    <td class="text-center">{data['scenario_a_unit_size']:.1f}㎡ ({data['scenario_a_unit_pyeong']:.1f}평)</td>
                    <td class="text-center">{data['scenario_b_unit_size']:.1f}㎡ ({data['scenario_b_unit_pyeong']:.1f}평)</td>
                </tr>
                <tr>
                    <td><strong>세대수</strong></td>
                    <td class="text-center"><strong>{data['scenario_a_unit_count']}</strong> 세대</td>
                    <td class="text-center"><strong>{data['scenario_b_unit_count']}</strong> 세대</td>
                </tr>
                <tr>
                    <td><strong>법정 용적률</strong></td>
                    <td class="text-center">{data['scenario_a_far_legal']:.1f}%</td>
                    <td class="text-center">{data['scenario_b_far_legal']:.1f}%</td>
                </tr>
                <tr>
                    <td><strong>완화 용적률</strong></td>
                    <td class="text-center"><strong>{data['scenario_a_far_final']:.1f}%</strong> (+{data['scenario_a_far_relaxation']:.0f}%p)</td>
                    <td class="text-center"><strong>{data['scenario_b_far_final']:.1f}%</strong> (+{data['scenario_b_far_relaxation']:.0f}%p)</td>
                </tr>
                <tr>
                    <td><strong>지상층수</strong></td>
                    <td class="text-center">{data['scenario_a_floors']}층</td>
                    <td class="text-center">{data['scenario_b_floors']}층</td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <!-- Financial Summary -->
    <div class="content-block">
        <h3 class="content-title">3-1-2. 재무 비교</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>재무 지표</th>
                    <th style="background: #E6F2FF;">시나리오 A</th>
                    <th style="background: #FFE6CC;">시나리오 B</th>
                    <th>차이</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>총 사업비 (CAPEX)</strong></td>
                    <td class="text-right">{data['scenario_a_total_capex']/100000000:.1f} 억원</td>
                    <td class="text-right">{data['scenario_b_total_capex']/100000000:.1f} 억원</td>
                    <td class="text-right">{(data['scenario_a_total_capex'] - data['scenario_b_total_capex'])/100000000:.1f} 억원</td>
                </tr>
                <tr>
                    <td><strong>LH 매입가</strong></td>
                    <td class="text-right">{data['scenario_a_lh_price']/100000000:.1f} 억원</td>
                    <td class="text-right">{data['scenario_b_lh_price']/100000000:.1f} 억원</td>
                    <td class="text-right">{(data['scenario_a_lh_price'] - data['scenario_b_lh_price'])/100000000:.1f} 억원</td>
                </tr>
                <tr>
                    <td><strong>사업 수익</strong></td>
                    <td class="text-right">{data['scenario_a_profit']/100000000:.1f} 억원</td>
                    <td class="text-right">{data['scenario_b_profit']/100000000:.1f} 억원</td>
                    <td class="text-right">{(data['scenario_a_profit'] - data['scenario_b_profit'])/100000000:.1f} 억원</td>
                </tr>
                <tr>
                    <td><strong>ROI</strong></td>
                    <td class="text-right">{data['scenario_a_roi']:.2f}%</td>
                    <td class="text-right">{data['scenario_b_roi']:.2f}%</td>
                    <td class="text-right">{(data['scenario_a_roi'] - data['scenario_b_roi']):.2f}%p</td>
                </tr>
                <tr>
                    <td><strong>재무 판정</strong></td>
                    <td class="text-center"><span class="decision-badge decision-{data['scenario_a_decision'].lower()}">{data['scenario_a_decision']}</span></td>
                    <td class="text-center"><span class="decision-badge decision-{data['scenario_b_decision'].lower()}">{data['scenario_b_decision']}</span></td>
                    <td class="text-center">-</td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <!-- Final Recommendation -->
    <div class="content-block">
        <h3 class="content-title">3-1-3. 종합 의견</h3>
        <div class="highlight-box" style="background: linear-gradient(135deg, #005BAC 0%, #0075C9 100%); color: white; padding: 20px; border-radius: 8px;">
            <h4 style="color: white; margin-top: 0;">✅ 최종 권고</h4>
            <p style="font-size: 13pt; font-weight: bold;">
                {data['final_recommendation']}
            </p>
            <p style="font-size: 10pt;">
                {data['recommendation_rationale']}
            </p>
        </div>
        
        <div style="margin-top: 20px;">
            <h4>주요 판단 근거:</h4>
            <ul style="line-height: 1.8;">
                <li><strong>재무적 관점</strong>: {data['financial_rationale']}</li>
                <li><strong>건축적 관점</strong>: {data['architectural_rationale']}</li>
                <li><strong>정책적 관점</strong>: {data['policy_rationale']}</li>
                <li><strong>시장 관점</strong>: {data['market_rationale']}</li>
            </ul>
        </div>
    </div>
</div>
<!-- End of Section 03-1 -->
"""
        
        return html
    
    def generate_complete_report(self,
                                address: str,
                                land_area_sqm: float,
                                bcr_legal: float = 50.0,
                                far_legal: float = 300.0) -> Dict:
        """
        Generate complete Expert v3.2 HTML report
        
        Args:
            address: Property address
            land_area_sqm: Land area in square meters
            bcr_legal: Legal building coverage ratio (default: 50%)
            far_legal: Legal floor area ratio (default: 300%)
        
        Returns:
            Dictionary with report HTML and metadata
        """
        
        print("=" * 80)
        print(f"EXPERT V3.2 REPORT GENERATOR")
        print("=" * 80)
        print(f"Address: {address}")
        print(f"Land Area: {land_area_sqm}㎡ ({land_area_sqm/3.3:.1f}평)")
        print(f"BCR: {bcr_legal}%, FAR: {far_legal}%")
        print()
        
        # Step 1: Get market data
        print("[Step 1/5] Fetching market data...")
        try:
            market_data = self.market_processor.get_market_data_with_fallback(
                address=address,
                land_area_sqm=land_area_sqm
            )
            avg_land_price = market_data['avg_price_per_sqm']
            print(f"  ✅ Market price: ₩{avg_land_price:,.0f}/㎡ ({market_data['confidence']} confidence)")
        except Exception as e:
            print(f"  ⚠️  Market data fetch failed: {e}")
            print(f"  Using fallback: ₩9,500,000/㎡")
            avg_land_price = 9_500_000
            market_data = {'avg_price_per_sqm': avg_land_price, 'confidence': 'LOW'}
        
        # Step 2: Generate Section 03-1 data
        print("\n[Step 2/5] Generating Section 03-1 (A/B Comparison)...")
        section_03_1_data = self.generate_section_03_1_data(
            land_area_sqm=land_area_sqm,
            bcr_legal=bcr_legal,
            far_legal=far_legal,
            avg_land_price_per_sqm=avg_land_price
        )
        
        # Step 3: Generate Section 03-1 HTML
        print("\n[Step 3/5] Rendering Section 03-1 HTML...")
        section_03_1_html = self.generate_section_03_1_html(section_03_1_data)
        print(f"  ✅ HTML generated ({len(section_03_1_html)} bytes)")
        
        # Step 4: Assemble complete report (simplified - just Section 03-1 for now)
        print("\n[Step 4/5] Assembling complete report...")
        
        # Basic HTML structure with CSS
        complete_html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expert v3.2 Report - {address}</title>
    <style>
        /* LH Color System */
        :root {{
            --lh-primary-blue: #005BAC;
            --lh-secondary-blue: #0075C9;
            --lh-orange: #FF7A00;
            --lh-gray-light: #F8F9FA;
        }}
        
        /* Base Styles */
        body {{
            font-family: 'Nanum Gothic', 'Malgun Gothic', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            background: white;
            margin: 20px;
        }}
        
        /* Section Styles */
        .section {{
            margin: 40px 0;
            padding: 20px;
            border-top: 3px solid var(--lh-primary-blue);
        }}
        
        .section-header {{
            margin-bottom: 30px;
        }}
        
        .section-number {{
            display: inline-block;
            background: linear-gradient(135deg, var(--lh-primary-blue) 0%, var(--lh-secondary-blue) 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .section-title {{
            font-size: 18pt;
            font-weight: bold;
            color: #2C3E50;
            margin: 10px 0;
        }}
        
        .section-subtitle {{
            font-size: 10pt;
            color: #7F8C8D;
            font-style: italic;
        }}
        
        /* Content Blocks */
        .content-block {{
            margin: 30px 0;
        }}
        
        .content-title {{
            font-size: 13pt;
            font-weight: bold;
            color: var(--lh-primary-blue);
            margin: 20px 0 15px 0;
            padding-left: 12px;
            border-left: 4px solid var(--lh-primary-blue);
        }}
        
        /* Tables */
        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        table.data-table thead {{
            background: linear-gradient(135deg, var(--lh-primary-blue) 0%, var(--lh-secondary-blue) 100%);
            color: white;
        }}
        
        table.data-table th {{
            padding: 12px;
            text-align: center;
            font-weight: bold;
            border: 1px solid #003D73;
        }}
        
        table.data-table td {{
            padding: 10px;
            border: 1px solid #E5E7EB;
        }}
        
        table.data-table td.text-center {{
            text-align: center;
        }}
        
        table.data-table td.text-right {{
            text-align: right;
            font-family: 'Courier New', monospace;
        }}
        
        /* Decision Badges */
        .decision-badge {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 10pt;
        }}
        
        .decision-go {{
            background: linear-gradient(135deg, #27AE60 0%, #2ECC71 100%);
            color: white;
        }}
        
        .decision-no-go {{
            background: linear-gradient(135deg, #C0392B 0%, #E74C3C 100%);
            color: white;
        }}
        
        /* Highlight Box */
        .highlight-box {{
            background: #E3F2FD;
            border-left: 4px solid var(--lh-primary-blue);
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .highlight-box h4 {{
            margin-top: 0;
            color: var(--lh-primary-blue);
        }}
    </style>
</head>
<body>
    <div style="text-align: center; margin: 40px 0;">
        <h1 style="color: var(--lh-primary-blue);">ZeroSite Expert Edition v3.2</h1>
        <h2>{address}</h2>
        <p>토지면적: {land_area_sqm:.1f}㎡ ({land_area_sqm/3.3:.1f}평)</p>
        <p>생성일: {datetime.now().strftime('%Y년 %m월 %d일')}</p>
    </div>
    
    {section_03_1_html}
    
    <div style="margin-top: 60px; padding: 20px; background: var(--lh-gray-light); border-radius: 8px; text-align: center;">
        <p style="color: #7F8C8D; font-size: 9pt;">
            본 보고서는 ZeroSite Expert Edition v3.2로 생성되었습니다.<br>
            A/B Scenario Comparison Engine | LH 2024 Standards | v23.1 Enhanced Visualizations
        </p>
    </div>
</body>
</html>
"""
        
        print(f"  ✅ Complete HTML assembled ({len(complete_html):,} bytes)")
        
        # Step 5: Compile metadata
        print("\n[Step 5/5] Compiling metadata...")
        metadata = {
            'address': address,
            'land_area_sqm': land_area_sqm,
            'land_area_pyeong': round(land_area_sqm / 3.3, 1),
            'bcr_legal': bcr_legal,
            'far_legal': far_legal,
            'market_price_per_sqm': avg_land_price,
            'market_confidence': market_data.get('confidence', 'UNKNOWN'),
            'scenario_a_decision': section_03_1_data['scenario_a_decision'],
            'scenario_b_decision': section_03_1_data['scenario_b_decision'],
            'recommended_scenario': section_03_1_data['recommended_scenario'],
            'generation_date': datetime.now().isoformat(),
            'version': self.version,
            'sections_included': ['Cover', 'Section 03-1 A/B Comparison'],
            'html_size_bytes': len(complete_html),
        }
        
        print(f"  ✅ Metadata compiled")
        print()
        print("=" * 80)
        print("REPORT GENERATION COMPLETE")
        print("=" * 80)
        print(f"Recommended Scenario: {section_03_1_data['final_recommendation']}")
        print(f"HTML Size: {len(complete_html):,} bytes")
        print()
        
        return {
            'html': complete_html,
            'metadata': metadata,
            'section_03_1_data': section_03_1_data,
        }


# Test function
if __name__ == "__main__":
    generator = ExpertV3ReportGenerator()
    
    # Test case: Mapo-gu
    result = generator.generate_complete_report(
        address="서울특별시 마포구 월드컵북로 120",
        land_area_sqm=660.0,
        bcr_legal=50.0,
        far_legal=300.0
    )
    
    # Save to file
    output_file = "/home/user/webapp/test_expert_v3_2_output.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result['html'])
    
    print(f"✅ Report saved: {output_file}")
    print(f"✅ File size: {len(result['html']):,} bytes")
    print(f"✅ Recommended: {result['metadata']['recommended_scenario']}")
