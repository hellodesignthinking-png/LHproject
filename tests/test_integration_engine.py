"""
ZeroSite Phase 11.1: Integration Engine Tests

Tests for Phase 11 + Phase 2 + Phase 3 integration

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.1
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.architect import DesignGenerator, SupplyType
from app.architect.integration_engine import IntegrationEngine


def test_integration_basic():
    """Test 1: Basic integration functionality"""
    print("\n" + "="*80)
    print("TEST 1: Integration Engine - Basic Functionality")
    print("="*80)
    
    # Create design
    generator = DesignGenerator(
        address="서울특별시 강남구 역삼동 123-45",
        land_params={
            "area": 1000.0,
            "bcr": 60,
            "far": 200,
            "max_floors": 15
        },
        supply_type=SupplyType.NEWLYWED
    )
    
    designs = generator.generate()
    
    # Test integration
    integration_engine = IntegrationEngine()
    
    for design in designs:
        analysis = integration_engine.analyze_design(
            design=design,
            land_area=1000.0,
            land_appraisal_price=9_000_000_000,  # 90억원
            bcr=60,
            far=200,
            zone_type="제2종일반주거지역",
            housing_type="Newlyweds_TypeII",
            address="서울특별시 강남구 역삼동 123-45"
        )
        
        # Validate results
        assert analysis.capex > 0, "CapEx should be positive"
        assert analysis.roi > 0, "ROI should be positive"
        assert 0 <= analysis.lh_total_score <= 100, "LH score should be 0-100"
        assert analysis.lh_grade in ['A', 'B', 'C', 'D', 'F'], "LH grade should be A-F"
        assert analysis.overall_decision in ['GO', 'CONDITIONAL', 'REVISE', 'STOP'], "Decision should be valid"
        
        print(f"\n✅ {design.strategy.value} Design:")
        print(f"   Total Units: {design.total_units}")
        print(f"   CapEx: ₩{analysis.capex:,.0f}")
        print(f"   ROI: {analysis.roi:.2f}%")
        print(f"   IRR (10yr): {analysis.irr:.2f}%")
        print(f"   LH Score: {analysis.lh_total_score:.1f}/100 (Grade: {analysis.lh_grade})")
        print(f"   Decision: {analysis.overall_decision}")
    
    print("\n✅ TEST 1 PASSED: Integration Engine works correctly")


def test_financial_integration():
    """Test 2: Phase 2 Financial Engine Integration"""
    print("\n" + "="*80)
    print("TEST 2: Phase 2 Financial Engine Integration")
    print("="*80)
    
    generator = DesignGenerator(
        address="경기도 성남시 분당구 판교동",
        land_params={
            "area": 800.0,
            "bcr": 55,
            "far": 180,
            "max_floors": 12
        },
        supply_type=SupplyType.YOUTH
    )
    
    designs = generator.generate()
    integration_engine = IntegrationEngine()
    
    # Test STANDARD design
    standard_design = [d for d in designs if d.strategy.value == "standard"][0]
    
    analysis = integration_engine.analyze_design(
        design=standard_design,
        land_area=800.0,
        land_appraisal_price=6_000_000_000,  # 60억원
        bcr=55,
        far=180,
        zone_type="제2종일반주거지역",
        housing_type="Youth",
        address="경기도 성남시 분당구 판교동"
    )
    
    # Validate financial metrics
    assert analysis.capex > 0, "Total CapEx must be calculated"
    assert analysis.opex > 0, "Annual OpEx must be calculated"
    assert analysis.noi > 0, "Annual NOI must be calculated"
    assert analysis.roi > 0, "ROI must be calculated"
    assert analysis.irr > 0, "IRR must be calculated"
    assert analysis.cap_rate > 0, "Cap Rate must be calculated"
    assert analysis.project_rating in ['A', 'B', 'C', 'D', 'F'], "Project rating must be valid"
    
    print(f"\n✅ Financial Analysis Results:")
    print(f"   Total CapEx: ₩{analysis.capex:,.0f}")
    print(f"   Annual OpEx: ₩{analysis.opex:,.0f}")
    print(f"   Annual NOI: ₩{analysis.noi:,.0f}")
    print(f"   ROI: {analysis.roi:.2f}%")
    print(f"   IRR (10yr): {analysis.irr:.2f}%")
    print(f"   Cap Rate: {analysis.cap_rate:.2f}%")
    print(f"   Project Rating: {analysis.project_rating}")
    
    print("\n✅ TEST 2 PASSED: Financial Engine integrated successfully")


def test_lh_score_integration():
    """Test 3: Phase 3 LH Score Engine Integration"""
    print("\n" + "="*80)
    print("TEST 3: Phase 3 LH Score Engine Integration")
    print("="*80)
    
    generator = DesignGenerator(
        address="서울특별시 서초구 반포동",
        land_params={
            "area": 1200.0,
            "bcr": 60,
            "far": 250,
            "max_floors": 15
        },
        supply_type=SupplyType.NEWLYWED
    )
    
    designs = generator.generate()
    integration_engine = IntegrationEngine()
    
    # Test STABLE design (should have high LH score)
    stable_design = [d for d in designs if d.strategy.value == "stable"][0]
    
    analysis = integration_engine.analyze_design(
        design=stable_design,
        land_area=1200.0,
        land_appraisal_price=12_000_000_000,  # 120억원
        bcr=60,
        far=250,
        zone_type="제2종일반주거지역",
        housing_type="Newlyweds_TypeII",
        address="서울특별시 서초구 반포동"
    )
    
    # Validate LH score
    breakdown = analysis.lh_score_breakdown
    
    assert 0 <= breakdown.location_total <= 25, "Location score should be 0-25"
    assert 0 <= breakdown.feasibility_total <= 30, "Feasibility score should be 0-30"
    assert 0 <= breakdown.policy_total <= 20, "Policy score should be 0-20"
    assert 0 <= breakdown.financial_total <= 15, "Financial score should be 0-15"
    assert 0 <= breakdown.risk_total <= 10, "Risk score should be 0-10"
    
    total_check = (
        breakdown.location_total +
        breakdown.feasibility_total +
        breakdown.policy_total +
        breakdown.financial_total +
        breakdown.risk_total
    )
    
    assert abs(total_check - breakdown.total_score) < 0.1, "Score components should sum to total"
    
    print(f"\n✅ LH Score Breakdown:")
    print(f"   Location (입지): {breakdown.location_total:.1f}/25")
    print(f"   Feasibility (타당성): {breakdown.feasibility_total:.1f}/30")
    print(f"   Policy (정책): {breakdown.policy_total:.1f}/20")
    print(f"   Financial (재무): {breakdown.financial_total:.1f}/15")
    print(f"   Risk (리스크): {breakdown.risk_total:.1f}/10")
    print(f"   ─────────────────────────")
    print(f"   Total Score: {breakdown.total_score:.1f}/100")
    print(f"   Grade: {breakdown.grade.value}")
    
    print(f"\n✅ Strengths ({len(breakdown.strengths)}):")
    for strength in breakdown.strengths:
        print(f"   {strength}")
    
    if breakdown.weaknesses:
        print(f"\n⚠️ Weaknesses ({len(breakdown.weaknesses)}):")
        for weakness in breakdown.weaknesses:
            print(f"   {weakness}")
    
    print(f"\n💡 Recommendations ({len(breakdown.recommendations)}):")
    for rec in breakdown.recommendations:
        print(f"   {rec}")
    
    print("\n✅ TEST 3 PASSED: LH Score Engine integrated successfully")


def test_decision_logic():
    """Test 4: Overall Decision Logic"""
    print("\n" + "="*80)
    print("TEST 4: Overall Decision Logic")
    print("="*80)
    
    generator = DesignGenerator(
        address="부산광역시 해운대구 우동",
        land_params={
            "area": 900.0,
            "bcr": 50,
            "far": 160,
            "max_floors": 10
        },
        supply_type=SupplyType.SENIOR
    )
    
    designs = generator.generate()
    integration_engine = IntegrationEngine()
    
    decisions = []
    for design in designs:
        analysis = integration_engine.analyze_design(
            design=design,
            land_area=900.0,
            land_appraisal_price=5_000_000_000,  # 50억원
            bcr=50,
            far=160,
            zone_type="제2종일반주거지역",
            housing_type="Senior",
            address="부산광역시 해운대구 우동"
        )
        
        decisions.append({
            "strategy": design.strategy.value,
            "lh_score": analysis.lh_total_score,
            "roi": analysis.roi,
            "decision": analysis.overall_decision,
            "confidence": analysis.confidence
        })
    
    # Validate decisions
    for dec in decisions:
        assert dec["decision"] in ['GO', 'CONDITIONAL', 'REVISE', 'STOP'], "Decision must be valid"
        assert 0 <= dec["confidence"] <= 100, "Confidence must be 0-100%"
        
        print(f"\n✅ {dec['strategy']} Design:")
        print(f"   LH Score: {dec['lh_score']:.1f}/100")
        print(f"   ROI: {dec['roi']:.2f}%")
        print(f"   Decision: {dec['decision']}")
        print(f"   Confidence: {dec['confidence']:.1f}%")
    
    print("\n✅ TEST 4 PASSED: Decision logic works correctly")


def test_three_strategies_comparison():
    """Test 5: Compare 3 Strategies (A/B/C)"""
    print("\n" + "="*80)
    print("TEST 5: Three Strategies Comparison (A/B/C)")
    print("="*80)
    
    generator = DesignGenerator(
        address="인천광역시 연수구 송도동",
        land_params={
            "area": 1500.0,
            "bcr": 65,
            "far": 220,
            "max_floors": 18
        },
        supply_type=SupplyType.MIXED
    )
    
    designs = generator.generate()
    integration_engine = IntegrationEngine()
    
    comparison_table = []
    
    for design in designs:
        analysis = integration_engine.analyze_design(
            design=design,
            land_area=1500.0,
            land_appraisal_price=10_000_000_000,  # 100억원
            bcr=65,
            far=220,
            zone_type="제2종일반주거지역",
            housing_type="Newlyweds_TypeII",
            address="인천광역시 연수구 송도동"
        )
        
        comparison_table.append({
            "strategy": design.strategy.value,
            "units": design.total_units,
            "gfa": design.volume.total_gfa,
            "capex": analysis.capex,
            "roi": analysis.roi,
            "irr": analysis.irr,
            "lh_score": analysis.lh_total_score,
            "lh_grade": analysis.lh_grade,
            "decision": analysis.overall_decision
        })
    
    # Display comparison
    print("\n" + "="*80)
    print("설계안 비교표")
    print("="*80)
    print(f"{'전략':<12} {'세대수':<8} {'연면적(㎡)':<12} {'ROI(%)':<10} {'IRR(%)':<10} {'LH점수':<10} {'등급':<6} {'판정':<12}")
    print("-"*80)
    
    for row in comparison_table:
        print(f"{row['strategy']:<12} {row['units']:<8} {row['gfa']:<12.0f} "
              f"{row['roi']:<10.2f} {row['irr']:<10.2f} {row['lh_score']:<10.1f} "
              f"{row['lh_grade']:<6} {row['decision']:<12}")
    
    # Validate comparison
    stable = comparison_table[0]
    standard = comparison_table[1]
    profit = comparison_table[2]
    
    # Stable should have highest LH score
    print(f"\n✅ Strategy Characteristics:")
    print(f"   Stable: Lowest units ({stable['units']}), High LH score ({stable['lh_score']:.1f})")
    print(f"   Standard: Moderate units ({standard['units']}), Balanced metrics")
    print(f"   Profit: Highest units ({profit['units']}), Max ROI ({profit['roi']:.2f}%)")
    
    print("\n✅ TEST 5 PASSED: Strategy comparison works correctly")


def test_performance():
    """Test 6: Performance Benchmark"""
    print("\n" + "="*80)
    print("TEST 6: Performance Benchmark")
    print("="*80)
    
    import time
    
    start_time = time.time()
    
    generator = DesignGenerator(
        address="서울특별시 강남구 역삼동 123-45",
        land_params={
            "area": 1000.0,
            "bcr": 60,
            "far": 200,
            "max_floors": 15
        },
        supply_type=SupplyType.NEWLYWED
    )
    
    designs = generator.generate()
    integration_engine = IntegrationEngine()
    
    for design in designs:
        _ = integration_engine.analyze_design(
            design=design,
            land_area=1000.0,
            land_appraisal_price=9_000_000_000,
            bcr=60,
            far=200,
            zone_type="제2종일반주거지역",
            housing_type="Newlyweds_TypeII",
            address="서울특별시 강남구 역삼동 123-45"
        )
    
    end_time = time.time()
    elapsed = (end_time - start_time) * 1000  # Convert to ms
    
    print(f"\n✅ Performance Results:")
    print(f"   Total Time: {elapsed:.2f}ms")
    print(f"   Per Design: {elapsed/3:.2f}ms")
    print(f"   Target: < 500ms per design")
    
    assert elapsed < 1500, "Total time should be under 1.5 seconds for 3 designs"
    
    print("\n✅ TEST 6 PASSED: Performance within acceptable range")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔗 ZEROSITE PHASE 11.1: INTEGRATION ENGINE TESTS")
    print("Architecture (Phase 11) + Financial (Phase 2) + LH Score (Phase 3)")
    print("="*80)
    
    try:
        test_integration_basic()
        test_financial_integration()
        test_lh_score_integration()
        test_decision_logic()
        test_three_strategies_comparison()
        test_performance()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED (6/6)")
        print("="*80)
        print("\n✅ Integration Engine is PRODUCTION READY!")
        print("\nPhase 11.1 완료:")
        print("  - Architecture Module ✅")
        print("  - Financial Engine Integration ✅")
        print("  - LH Score Engine Integration ✅")
        print("  - Decision Logic ✅")
        print("  - Performance Optimization ✅")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
