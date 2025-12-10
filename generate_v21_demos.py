"""
Generate v21 Demo Reports for Testing & Validation
- Mapo Newlywed Housing
- Mixed Housing (Youth + Newlywed)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from generate_v21_report import V21ReportGenerator
import time


def generate_mapo_newlywed():
    """Generate Mapo Newlywed Housing demo"""
    print("\n" + "="*80)
    print("📝 Generating Mapo Newlywed Housing Demo")
    print("="*80 + "\n")
    
    generator = V21ReportGenerator()
    
    context = generator.generate_full_context(
        address="서울특별시 마포구 공덕동 456-78",
        land_area_pyeong=650,
        supply_type="신혼부부",
        land_price_per_pyeong=7_800_000,
        far_legal=200,
        far_relaxation=35,
        bcr_legal=60,
        lh_appraisal_rate=97,
        near_subway=True,
        subway_distance_m=320,
        school_zone=True,
        demand_score=85,
    )
    
    # Generate HTML
    html_path = "generated_reports/v21_mapo_newlywed.html"
    html_content = generator.generate_html_report(context, html_path)
    
    # Generate PDF
    pdf_path = "generated_reports/v21_mapo_newlywed.pdf"
    generator.generate_pdf_report(html_content, pdf_path)
    
    print("\n✅ Mapo Newlywed Demo Generated")
    print(f"   HTML: {html_path}")
    print(f"   PDF: {pdf_path}")
    print(f"   IRR: {context['irr']:.1f}%")
    print(f"   Decision: {context['financial_decision']}/{context['policy_decision']}")
    
    return context


def generate_mixed_housing():
    """Generate Mixed Housing (Youth + Newlywed) demo"""
    print("\n" + "="*80)
    print("📝 Generating Mixed Housing Demo")
    print("="*80 + "\n")
    
    generator = V21ReportGenerator()
    
    context = generator.generate_full_context(
        address="서울특별시 송파구 잠실동 789-12",
        land_area_pyeong=800,
        supply_type="혼합",
        land_price_per_pyeong=9_200_000,
        far_legal=250,
        far_relaxation=45,
        bcr_legal=60,
        lh_appraisal_rate=96,
        near_subway=True,
        subway_distance_m=280,
        school_zone=True,
        demand_score=88,
    )
    
    # Generate HTML
    html_path = "generated_reports/v21_mixed_housing.html"
    html_content = generator.generate_html_report(context, html_path)
    
    # Generate PDF
    pdf_path = "generated_reports/v21_mixed_housing.pdf"
    generator.generate_pdf_report(html_content, pdf_path)
    
    print("\n✅ Mixed Housing Demo Generated")
    print(f"   HTML: {html_path}")
    print(f"   PDF: {pdf_path}")
    print(f"   IRR: {context['irr']:.1f}%")
    print(f"   Decision: {context['financial_decision']}/{context['policy_decision']}")
    
    return context


def main():
    """Generate all v21 demo reports"""
    print("\n🚀 ZeroSite v21 Demo Report Generator")
    print("="*80)
    
    start_time = time.time()
    
    # Generate demos
    demos = []
    demos.append(("Mapo Newlywed", generate_mapo_newlywed()))
    demos.append(("Mixed Housing", generate_mixed_housing()))
    
    total_time = time.time() - start_time
    
    # Summary
    print("\n" + "="*80)
    print("🎉 All v21 Demo Reports Generated!")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   Total Demos: {len(demos)}")
    print(f"   Total Time: {total_time:.1f}s")
    print(f"   Avg Time: {total_time/len(demos):.1f}s per report")
    
    print(f"\n📋 Demo Reports:")
    for name, context in demos:
        print(f"\n   {name}:")
        print(f"      Address: {context['address']}")
        print(f"      Units: {context['total_units']}세대")
        print(f"      CAPEX: {context['total_capex']/1e8:.1f}억원")
        print(f"      IRR: {context['irr']:.1f}%")
        print(f"      NPV: {context['npv']/1e8:.1f}억원")
        print(f"      Decision: {context['financial_decision']}/{context['policy_decision']}")
        print(f"      Narrative Lines: {context['narrative_stats']['total_lines_generated']}")


if __name__ == "__main__":
    main()
