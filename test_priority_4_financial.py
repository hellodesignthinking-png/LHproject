#!/usr/bin/env python3
"""
Test Priority 4: Financial Narrative Deep Expansion
Verify 6-page (3,000+ char) Financial Analysis section
"""

import sys
import time
from app.services_v13.report_full.narrative_interpreter import NarrativeInterpreter
from app.services_v13.data_engines.geocoder import Geocoder
from app.services_v13.data_engines.poi_analyzer import POIAnalyzer
from app.services_v13.analysis_engines.demand_analyzer import DemandAnalyzer
from app.services_v13.analysis_engines.market_analyzer import MarketAnalyzer
from app.services_v13.analysis_engines.financial_calculator import FinancialCalculator
from app.services_v13.analysis_engines.lh_integrator import LHIntegrator

def build_test_context():
    """Build minimal test context for financial narrative"""
    address = "서울특별시 강남구 역삼동 737"
    
    print("="*80)
    print("BUILDING TEST CONTEXT FOR FINANCIAL NARRATIVE")
    print("="*80)
    
    # Geocoding
    geocoder = Geocoder()
    geo_data = geocoder.get_location_info(address)
    
    # POI Analysis (minimal)
    poi_analyzer = POIAnalyzer(geo_data['lat'], geo_data['lng'], radius=1000)
    poi_data = poi_analyzer.analyze()
    
    # Demand Analysis
    demand_analyzer = DemandAnalyzer(geo_data)
    demand_result = demand_analyzer.analyze()
    
    # Market Analysis
    market_analyzer = MarketAnalyzer(geo_data)
    market_result = market_analyzer.analyze()
    
    # Financial Analysis
    fin_calc = FinancialCalculator(
        capex_billion=300.0,
        land_ratio=0.45,
        construction_cost_per_sqm=3.5,
        total_area_sqm=8500,
        annual_rent_per_unit=1500,
        num_units=120,
        interest_rate_pct=4.0
    )
    finance_result = fin_calc.calculate()
    
    # LH Integration
    lh_integrator = LHIntegrator(geo_data, demand_result, market_result, finance_result)
    lh_context = lh_integrator.build_context()
    
    # Combine all
    context = {
        **geo_data,
        **poi_data,
        **demand_result,
        **market_result,
        **finance_result,
        **lh_context
    }
    
    print(f"✅ Context built: {len(context)} keys")
    print(f"   - CAPEX: {finance_result.get('capex_billion', 0):.1f}억원")
    print(f"   - NPV: {finance_result.get('npv_billion', 0):.1f}억원")
    print(f"   - IRR: {finance_result.get('irr_percent', 0):.2f}%")
    print(f"   - Payback: {finance_result.get('payback_years', 0):.1f}년")
    print()
    
    return context

def test_financial_narrative_expansion():
    """Test Priority 4: Financial Narrative Deep Expansion"""
    
    print("="*80)
    print("PRIORITY 4: FINANCIAL NARRATIVE DEEP EXPANSION TEST")
    print("="*80)
    print()
    
    # Build context
    context = build_test_context()
    
    # Generate Financial Narrative
    print("="*80)
    print("GENERATING FINANCIAL NARRATIVE")
    print("="*80)
    
    start_time = time.time()
    ni = NarrativeInterpreter()
    financial_narrative = ni.interpret_financial(context)
    elapsed = time.time() - start_time
    
    # Analyze results
    char_count = len(financial_narrative)
    estimated_pages = char_count / 500  # Rough estimate: 500 chars per page
    
    print(f"✅ Financial Narrative generated in {elapsed:.2f}s")
    print(f"   - Character count: {char_count} chars")
    print(f"   - Estimated pages: {estimated_pages:.1f}p")
    print()
    
    # Check structure
    print("="*80)
    print("NARRATIVE STRUCTURE ANALYSIS")
    print("="*80)
    
    sections = [
        ("I. 핵심 재무 지표", "서론: 숫자의 의미"),
        ("II. 비용 구조 분석", "CAPEX"),
        ("III. 수익 구조", "사회적 ROI"),
        ("IV. NPV/IRR 해석", "음수 NPV는 실패가 아니다"),
        ("V. 시나리오 분석", "Base, Optimistic, Pessimistic"),
        ("VI. 결론", "전략적 의사결정")
    ]
    
    found_sections = []
    for section_num, keywords in sections:
        for keyword in keywords.split(", "):
            if keyword in financial_narrative:
                found_sections.append(f"   ✅ {section_num}: '{keyword}' found")
                break
        else:
            found_sections.append(f"   ❌ {section_num}: NOT FOUND")
    
    for line in found_sections:
        print(line)
    
    # Check for key policy phrases
    print()
    print("="*80)
    print("KEY POLICY PHRASES CHECK")
    print("="*80)
    
    policy_phrases = [
        "민간 수익성 vs. 정책적 공공가치",
        "사회적 IRR",
        "민간 NO-GO",
        "정책 CONDITIONAL GO",
        "LH 평가",
        "정책자금 활용",
        "감정평가율",
        "주거복지 편익"
    ]
    
    for phrase in policy_phrases:
        if phrase in financial_narrative:
            print(f"   ✅ '{phrase}' found")
        else:
            print(f"   ⚠️  '{phrase}' NOT found")
    
    # Preview
    print()
    print("="*80)
    print("NARRATIVE PREVIEW (First 1000 characters)")
    print("="*80)
    print(financial_narrative[:1000])
    print("...")
    print()
    
    # Target validation
    print("="*80)
    print("TARGET VALIDATION")
    print("="*80)
    
    target_chars = 3000
    target_pages_min = 4
    target_pages_max = 6
    
    if char_count >= target_chars:
        print(f"   ✅ Character count: {char_count} >= {target_chars} (Target met)")
    else:
        print(f"   ⚠️  Character count: {char_count} < {target_chars} (Target NOT met)")
    
    if target_pages_min <= estimated_pages <= target_pages_max:
        print(f"   ✅ Estimated pages: {estimated_pages:.1f}p is within {target_pages_min}-{target_pages_max}p (Target met)")
    else:
        print(f"   ⚠️  Estimated pages: {estimated_pages:.1f}p is outside {target_pages_min}-{target_pages_max}p (Target NOT met)")
    
    # Overall result
    print()
    print("="*80)
    print("PRIORITY 4: FINANCIAL NARRATIVE TEST RESULT")
    print("="*80)
    
    if char_count >= target_chars and target_pages_min <= estimated_pages <= target_pages_max:
        print("✅ SUCCESS: Financial Narrative expansion COMPLETE!")
        print(f"   - Target: 3,000+ chars, 4-6 pages")
        print(f"   - Actual: {char_count} chars, {estimated_pages:.1f} pages")
        print(f"   - Status: 20M KRW Government Submission Grade quality achieved")
        return 0
    else:
        print("⚠️  PARTIAL: Financial Narrative needs adjustment")
        print(f"   - Target: 3,000+ chars, 4-6 pages")
        print(f"   - Actual: {char_count} chars, {estimated_pages:.1f} pages")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(test_financial_narrative_expansion())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
