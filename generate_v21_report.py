"""
ZeroSite Expert Edition v21 Professional - Report Generator

This script generates McKinsey-Grade professional reports with:
- v21 Professional Narrative Engine (270+ lines)
- LH Blue Design System
- Policy-Driven Insights (12+ citations)
- 2-Column Responsive Layout
- 6 Specialized Interpreters

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 21.0.0 - PROFESSIONAL EDITION
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add paths
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services_v13.report_full.v21_narrative_engine_pro import V21NarrativeEnginePro
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


class V21ReportGenerator:
    """
    Generates Expert Edition v21 Professional reports
    McKinsey-Grade + LH Blue Design
    """
    
    def __init__(self):
        """Initialize the v21 generator"""
        print("🚀 ZeroSite Expert Edition v21 Professional - Report Generator")
        print("="*80)
        
        # Initialize v21 Narrative Engine
        self.narrative_engine = V21NarrativeEnginePro()
        
        # Setup Jinja2
        template_dir = Path(__file__).parent / "app" / "services_v13" / "report_full"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        print("✅ v21 Narrative Engine loaded")
        print("✅ Jinja2 template system ready")
        print("="*80 + "\n")
    
    def generate_full_context(
        self,
        address: str,
        land_area_pyeong: float,
        supply_type: str = "청년",
        **kwargs
    ) -> dict:
        """
        Generate COMPLETE context for v21 report
        
        Args:
            address: Site address
            land_area_pyeong: Land area in pyeong
            supply_type: 청년, 신혼부부, 혼합 등
            **kwargs: Additional parameters
            
        Returns:
            dict: Complete context with all v21 variables
        """
        
        print(f"📊 Generating v21 Context for:")
        print(f"   Address: {address}")
        print(f"   Land Area: {land_area_pyeong:,.1f}평 ({land_area_pyeong * 3.3:,.1f}㎡)")
        print(f"   Supply Type: {supply_type}\n")
        
        # ============================================================
        # Basic Parameters
        # ============================================================
        land_area_sqm = land_area_pyeong * 3.3
        bcr = kwargs.get("bcr_legal", 60)
        far = kwargs.get("far_legal", 200)
        far_relaxation = kwargs.get("far_relaxation", 30)
        bcr_relaxation = kwargs.get("bcr_relaxation", 0)
        
        # Building calculations
        building_area = land_area_sqm * (bcr + bcr_relaxation) / 100
        buildable_area = land_area_sqm * (far + far_relaxation) / 100
        
        # Unit calculations (simplified)
        avg_unit_size = 50  # ㎡ per unit (approx)
        total_units = int(buildable_area / avg_unit_size * 0.7)  # 70% efficiency
        
        # ============================================================
        # Financial Calculations
        # ============================================================
        print("💰 Calculating Financial Metrics...")
        
        # CAPEX breakdown
        land_price_per_pyeong = kwargs.get("land_price_per_pyeong", 8_000_000)
        land_cost = land_area_pyeong * land_price_per_pyeong
        
        building_cost_per_sqm = 3_500_000  # ₩3.5M/㎡ (LH standard)
        building_cost = buildable_area * building_cost_per_sqm
        
        financial_cost = (land_cost + building_cost) * 0.08  # 8% interest
        admin_cost = (land_cost + building_cost) * 0.04  # 4% admin
        
        total_capex = land_cost + building_cost + financial_cost + admin_cost
        
        # LH appraisal value (revenue)
        lh_appraisal_rate = kwargs.get("lh_appraisal_rate", 95)  # 95% of market
        market_value = total_capex * 1.15  # Assume 15% markup
        lh_purchase_price = market_value * (lh_appraisal_rate / 100)
        
        # Profitability metrics
        npv = lh_purchase_price - total_capex
        roi = (npv / total_capex * 100) if total_capex > 0 else 0
        irr = roi * 0.8 if roi > 0 else 5.0  # Simplified IRR approximation
        payback_years = total_capex / (npv / 3) if npv > 0 else 5.0
        
        print(f"   ✅ Total CAPEX: {total_capex/1e8:.1f}억원")
        print(f"   ✅ LH Purchase Price: {lh_purchase_price/1e8:.1f}억원")
        print(f"   ✅ NPV: {npv/1e8:.1f}억원")
        print(f"   ✅ IRR: {irr:.1f}%")
        
        # ============================================================
        # Market & Demand Data (Simplified)
        # ============================================================
        comps = [
            {"address": f"{address} 인근 1", "price_per_sqm": 6_500_000, "transaction_date": "2024-11"},
            {"address": f"{address} 인근 2", "price_per_sqm": 6_800_000, "transaction_date": "2024-10"},
            {"address": f"{address} 인근 3", "price_per_sqm": 6_200_000, "transaction_date": "2024-09"},
        ]
        
        demand_data = {
            "demand_score": kwargs.get("demand_score", 78),
            "target_age_group": "20-35세" if supply_type == "청년" else "30-40세",
            "target_household": "1-2인 가구" if supply_type == "청년" else "2-4인 가구",
            "supply_ratio": 85,  # Undersupplied
        }
        
        # ============================================================
        # Generate v21 Professional Narratives
        # ============================================================
        print("\n📝 Generating v21 Professional Narratives...")
        
        # Create context dict for narrative engine
        narrative_context = {
            "address": address,
            "land_area_pyeong": land_area_pyeong,
            "land_area_sqm": land_area_sqm,
            "supply_type": supply_type,
            "total_units": total_units,
            "total_capex": total_capex,
            "land_cost": land_cost,
            "building_cost": building_cost,
            "financial_cost": financial_cost,
            "lh_purchase_price": lh_purchase_price,
            "lh_appraisal_rate": lh_appraisal_rate,
            "npv": npv,
            "irr": irr,
            "roi": roi,
            "payback_years": payback_years,
            "bcr_legal": bcr,
            "far_legal": far,
            "bcr_relaxation": bcr_relaxation,
            "far_relaxation": far_relaxation,
            "near_subway": kwargs.get("near_subway", True),
            "subway_distance_m": kwargs.get("subway_distance_m", 450),
            "school_zone": kwargs.get("school_zone", True),
            "zoning_type": kwargs.get("zoning_type", "제2종일반주거지역"),
        }
        
        # Generate narratives
        narrative_executive = self.narrative_engine.generate_executive_summary_v21(narrative_context)
        narrative_market = self.narrative_engine.generate_market_interpretation_v21(comps, narrative_context)
        narrative_demand = self.narrative_engine.generate_demand_interpretation_v21(demand_data, narrative_context)
        
        financial_dict = {
            "total_construction_cost_krw": total_capex,
            "capex_krw": total_capex,
            "land_cost_krw": land_cost,
            "building_cost_krw": building_cost,
            "design_cost_krw": admin_cost,  # Using admin cost as design cost approximation
            "lh_purchase_price": lh_purchase_price,
            "profit_krw": npv,
            "roi_pct": roi,
            "irr_public_pct": irr,
            "npv_public_krw": npv,
            "payback_period_years": payback_years,
        }
        narrative_financial = self.narrative_engine.generate_financial_interpretation_v21(financial_dict, narrative_context)
        narrative_zoning = self.narrative_engine.generate_zoning_planning_narrative(narrative_context)
        narrative_risk = self.narrative_engine.generate_risk_strategy_narrative(narrative_context)
        
        # Get stats
        stats = self.narrative_engine.get_narrative_stats()
        print(f"   ✅ Executive Summary: Generated")
        print(f"   ✅ Market Intelligence: Generated")
        print(f"   ✅ Demand Intelligence: Generated")
        print(f"   ✅ Financial Analysis: Generated")
        print(f"   ✅ Zoning & Planning: Generated")
        print(f"   ✅ Risk & Strategy: Generated")
        print(f"   📊 Total Narrative Lines: {stats['total_lines_generated']}/{stats['target_lines']}")
        print(f"   📚 Policy Citations: {stats['total_citations']}")
        
        # ============================================================
        # Decision Logic
        # ============================================================
        financial_decision = "PASS" if irr >= 10 else "CONDITIONAL" if irr >= 8 else "REJECT"
        policy_decision = "ADOPT" if far_relaxation >= 20 else "CONDITIONAL" if far_relaxation >= 10 else "REJECT"
        
        # Risk scoring (simplified)
        policy_risk_score = 75 if far_relaxation < 10 else 50 if far_relaxation < 30 else 25
        financial_risk_score = 75 if irr < 8 else 50 if irr < 12 else 25
        total_risk_score = policy_risk_score + financial_risk_score + 100  # +100 for other risks
        
        # ============================================================
        # Complete Context Assembly
        # ============================================================
        complete_context = {
            # Basic info
            "address": address,
            "land_area_pyeong": land_area_pyeong,
            "supply_type": supply_type,
            "total_units": total_units,
            "generation_date": datetime.now().strftime("%Y년 %m월 %d일 %H:%M"),
            "zoning_type": narrative_context["zoning_type"],
            "near_subway": narrative_context["near_subway"],
            
            # Financial metrics
            "irr": irr,
            "npv": npv,
            "roi": roi,
            "total_capex": total_capex,
            "land_cost": land_cost,
            "building_cost": building_cost,
            
            # Decisions
            "financial_decision": financial_decision,
            "policy_decision": policy_decision,
            "total_risk_score": total_risk_score,
            
            # v21 Professional Narratives
            "narrative_executive_summary": narrative_executive,
            "narrative_market_intelligence": narrative_market,
            "narrative_demand_intelligence": narrative_demand,
            "narrative_financial_analysis": narrative_financial,
            "narrative_zoning_planning": narrative_zoning,
            "narrative_risk_strategy": narrative_risk,
            
            # Stats
            "narrative_stats": stats,
        }
        
        return complete_context
    
    def generate_html_report(self, context: dict, output_path: str = None) -> str:
        """
        Generate v21 HTML report
        
        Args:
            context: Complete context dict
            output_path: Optional output file path
            
        Returns:
            str: HTML content
        """
        print("\n🎨 Rendering v21 Professional Template...")
        
        template = self.jinja_env.get_template("lh_expert_edition_v21.html.jinja2")
        html_content = template.render(**context)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"   ✅ HTML saved to: {output_path}")
        
        return html_content
    
    def generate_pdf_report(self, html_content: str, output_path: str):
        """
        Generate v21 PDF report from HTML
        
        Args:
            html_content: HTML string
            output_path: PDF output path
        """
        print("\n📄 Generating v21 Professional PDF...")
        
        HTML(string=html_content).write_pdf(output_path)
        
        print(f"   ✅ PDF saved to: {output_path}")
        
        # Get file size
        file_size_kb = os.path.getsize(output_path) / 1024
        print(f"   📊 File Size: {file_size_kb:.1f} KB")


def main():
    """Generate v21 demo report"""
    generator = V21ReportGenerator()
    
    # Example: Gangnam Youth Housing
    context = generator.generate_full_context(
        address="서울특별시 강남구 역삼동 123-45",
        land_area_pyeong=500,
        supply_type="청년",
        land_price_per_pyeong=8_500_000,
        far_legal=200,
        far_relaxation=40,
        bcr_legal=60,
        lh_appraisal_rate=96,
        near_subway=True,
        subway_distance_m=380,
        school_zone=True,
        demand_score=82,
    )
    
    # Generate HTML
    html_path = "generated_reports/v21_gangnam_youth.html"
    os.makedirs("generated_reports", exist_ok=True)
    html_content = generator.generate_html_report(context, html_path)
    
    # Generate PDF
    pdf_path = "generated_reports/v21_gangnam_youth.pdf"
    generator.generate_pdf_report(html_content, pdf_path)
    
    print("\n" + "="*80)
    print("🎉 v21 Professional Report Generation COMPLETE!")
    print("="*80)
    print(f"\n📊 Report Summary:")
    print(f"   Address: {context['address']}")
    print(f"   Total Units: {context['total_units']}세대")
    print(f"   IRR: {context['irr']:.1f}%")
    print(f"   NPV: {context['npv']/1e8:.1f}억원")
    print(f"   Financial Decision: {context['financial_decision']}")
    print(f"   Policy Decision: {context['policy_decision']}")
    print(f"   Narrative Lines: {context['narrative_stats']['total_lines_generated']}")
    print(f"   Policy Citations: {context['narrative_stats']['total_citations']}")
    print(f"\n📁 Output Files:")
    print(f"   HTML: {html_path}")
    print(f"   PDF: {pdf_path}")


if __name__ == "__main__":
    main()
