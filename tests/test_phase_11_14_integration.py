"""
ZeroSite Phase 11~14 Integration Tests

Comprehensive tests for Phase 11-14 full integration

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 1.0
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.architect.lh_policy_rules import LHPolicyRules, LHSupplyType
from app.report.narrative_engine import AcademicNarrativeEngine
from app.timeline.critical_path import CriticalPathAnalyzer
from datetime import datetime


def test_lh_policy_rules():
    """Test 1: LH Policy Rules Database"""
    print("\n" + "="*80)
    print("TEST 1: LH Policy Rules Database")
    print("="*80)
    
    rules = LHPolicyRules()
    
    # Test unit rules
    youth_rules = rules.get_unit_rules(LHSupplyType.YOUTH)
    assert len(youth_rules) > 0, "Should have youth unit rules"
    assert youth_rules[0].size_avg == 14.0, "Youth unit should be 14㎡"
    
    # Test common area ratio
    common_ratio = rules.get_common_area_ratio()
    assert common_ratio == 0.15, "Common area ratio should be 15%"
    
    # Test parking ratio
    parking_seoul = rules.get_parking_ratio("seoul")
    parking_general = rules.get_parking_ratio("general")
    assert parking_seoul == 0.3, "Seoul parking should be 0.3/unit"
    assert parking_general == 0.2, "General parking should be 0.2/unit"
    
    # Test unit calculation
    distribution = rules.calculate_total_units(1000.0, LHSupplyType.YOUTH)
    assert "youth_14" in distribution, "Should have youth_14 units"
    assert distribution["youth_14"]["count"] > 0, "Should have positive unit count"
    
    print(f"✅ Youth 14㎡ rules: {youth_rules[0].unit_type}")
    print(f"✅ Common area ratio: {common_ratio*100}%")
    print(f"✅ Parking (Seoul): {parking_seoul}/unit")
    print(f"✅ Unit calculation: {distribution['youth_14']['count']} units")
    
    print("\n✅ TEST 1 PASSED: LH Policy Rules working correctly")


def test_academic_narrative():
    """Test 2: Academic Narrative Engine"""
    print("\n" + "="*80)
    print("TEST 2: Academic Narrative Engine")
    print("="*80)
    
    engine = AcademicNarrativeEngine()
    
    # Test data
    design_result = {
        "total_units": 50,
        "total_gfa": 1800,
        "supply_type": "청년"
    }
    
    financial_result = {
        "roi": 2.8,
        "capex": 18_000_000_000
    }
    
    lh_score = {
        "total_score": 87.5,
        "grade": "B"
    }
    
    # Generate narrative
    sections = engine.generate_full_narrative(design_result, financial_result, lh_score)
    
    assert len(sections) == 5, "Should have 5 narrative sections"
    
    section_types = [s.type.value for s in sections]
    assert "what" in section_types, "Should have WHAT section"
    assert "so_what" in section_types, "Should have SO WHAT section"
    assert "why" in section_types, "Should have WHY section"
    assert "insight" in section_types, "Should have INSIGHT section"
    assert "conclusion" in section_types, "Should have CONCLUSION section"
    
    # Check content length
    for section in sections:
        assert len(section.content) > 100, f"{section.title} should have substantial content"
        assert len(section.key_points) > 0, f"{section.title} should have key points"
    
    print(f"✅ Generated {len(sections)} narrative sections")
    print(f"✅ Section types: {', '.join(section_types)}")
    print(f"✅ All sections have content and key points")
    
    # Print first section as example
    print(f"\n📝 Example (WHAT section):")
    print(f"   Title: {sections[0].title}")
    print(f"   Content length: {len(sections[0].content)} chars")
    print(f"   Key points: {len(sections[0].key_points)}")
    
    print("\n✅ TEST 2 PASSED: Academic Narrative Engine working correctly")


def test_critical_path():
    """Test 3: Critical Path Analyzer"""
    print("\n" + "="*80)
    print("TEST 3: Critical Path Analyzer")
    print("="*80)
    
    analyzer = CriticalPathAnalyzer()
    
    # Generate timeline
    timeline = analyzer.generate_timeline(
        start_date=datetime(2025, 1, 1),
        project_scale="standard"
    )
    
    assert timeline.total_duration_months > 0, "Should have positive duration"
    assert len(timeline.phases) > 0, "Should have phases"
    assert len(timeline.critical_path) > 0, "Should have critical path"
    assert len(timeline.key_risks) > 0, "Should have key risks"
    assert len(timeline.recommendations) > 0, "Should have recommendations"
    
    # Check critical path
    critical_phases = [p for p in timeline.phases if p.is_critical]
    assert len(critical_phases) == len(timeline.critical_path), "Critical path count should match"
    
    # Check phase structure
    for phase in timeline.phases:
        assert phase.phase_name, "Phase should have name"
        assert phase.duration_months > 0, "Phase should have positive duration"
        assert phase.description, "Phase should have description"
    
    print(f"✅ Total duration: {timeline.total_duration_months} months")
    print(f"✅ Total phases: {len(timeline.phases)}")
    print(f"✅ Critical phases: {len(critical_phases)}")
    print(f"✅ Key risks identified: {len(timeline.key_risks)}")
    print(f"✅ Recommendations: {len(timeline.recommendations)}")
    
    # Generate narratives
    narratives = analyzer.get_narrative(timeline)
    
    assert "overview" in narratives, "Should have overview narrative"
    assert "critical_path" in narratives, "Should have critical path narrative"
    assert "risk_analysis" in narratives, "Should have risk analysis"
    
    print(f"\n📊 Narrative sections generated: {len(narratives)}")
    
    print("\n✅ TEST 3 PASSED: Critical Path Analyzer working correctly")


def test_full_integration():
    """Test 4: Full Phase 11-14 Integration"""
    print("\n" + "="*80)
    print("TEST 4: Full Phase 11-14 Integration")
    print("="*80)
    
    # Step 1: LH Policy Rules
    print("\n📋 Step 1: Load LH Policy Rules")
    rules = LHPolicyRules()
    distribution = rules.calculate_total_units(2000.0, LHSupplyType.NEWLYWED)
    philosophy = rules.get_design_philosophy(LHSupplyType.NEWLYWED)
    
    total_units = sum(info["count"] for info in distribution.values())
    print(f"   Total units: {total_units}")
    print(f"   Philosophy length: {len(philosophy)} chars")
    
    # Step 2: Generate Narrative
    print("\n📝 Step 2: Generate Academic Narrative")
    engine = AcademicNarrativeEngine()
    
    design_data = {
        "total_units": total_units,
        "total_gfa": 2000,
        "supply_type": "신혼부부"
    }
    
    financial_data = {
        "roi": 2.3,
        "capex": 20_000_000_000
    }
    
    lh_score_data = {
        "total_score": 82.0,
        "grade": "B"
    }
    
    narratives = engine.generate_full_narrative(design_data, financial_data, lh_score_data)
    print(f"   Generated {len(narratives)} narrative sections")
    
    # Step 3: Generate Timeline
    print("\n📅 Step 3: Generate Critical Timeline")
    analyzer = CriticalPathAnalyzer()
    timeline = analyzer.generate_timeline(project_scale="standard")
    timeline_narratives = analyzer.get_narrative(timeline)
    
    print(f"   Timeline: {timeline.total_duration_months} months")
    print(f"   Timeline narratives: {len(timeline_narratives)} sections")
    
    # Step 4: Integration check
    print("\n🔗 Step 4: Integration Check")
    
    # All components should work together
    assert total_units > 0, "Should calculate units from policy rules"
    assert len(narratives) == 5, "Should generate all narrative sections"
    assert timeline.total_duration_months > 0, "Should generate timeline"
    
    # Create comprehensive output
    comprehensive_output = {
        "design": {
            "units": total_units,
            "distribution": distribution,
            "philosophy": philosophy[:200] + "..."
        },
        "narrative": {
            "sections": [s.title for s in narratives],
            "total_length": sum(len(s.content) for s in narratives)
        },
        "timeline": {
            "duration": timeline.total_duration_months,
            "phases": len(timeline.phases),
            "critical_path": len(timeline.critical_path),
            "narratives": list(timeline_narratives.keys())
        }
    }
    
    print(f"\n📦 Comprehensive Output:")
    print(f"   Design units: {comprehensive_output['design']['units']}")
    print(f"   Narrative sections: {len(comprehensive_output['narrative']['sections'])}")
    print(f"   Narrative total length: {comprehensive_output['narrative']['total_length']} chars")
    print(f"   Timeline duration: {comprehensive_output['timeline']['duration']} months")
    print(f"   Timeline phases: {comprehensive_output['timeline']['phases']}")
    
    print("\n✅ TEST 4 PASSED: Full Phase 11-14 Integration working correctly")
    
    return comprehensive_output


def test_performance():
    """Test 5: Performance Benchmark"""
    print("\n" + "="*80)
    print("TEST 5: Performance Benchmark")
    print("="*80)
    
    import time
    
    # Test 1: LH Policy Rules
    start = time.time()
    for _ in range(100):
        rules = LHPolicyRules()
        _ = rules.calculate_total_units(1000.0, LHSupplyType.YOUTH)
    elapsed_policy = (time.time() - start) * 1000 / 100
    
    # Test 2: Narrative Generation
    start = time.time()
    for _ in range(10):
        engine = AcademicNarrativeEngine()
        _ = engine.generate_full_narrative(
            {"total_units": 50, "total_gfa": 1500, "supply_type": "청년"},
            {"roi": 2.5, "capex": 15_000_000_000},
            {"total_score": 85.0, "grade": "B"}
        )
    elapsed_narrative = (time.time() - start) * 1000 / 10
    
    # Test 3: Timeline Generation
    start = time.time()
    for _ in range(100):
        analyzer = CriticalPathAnalyzer()
        _ = analyzer.generate_timeline()
    elapsed_timeline = (time.time() - start) * 1000 / 100
    
    print(f"\n⏱️ Performance Results:")
    print(f"   LH Policy Rules: {elapsed_policy:.2f}ms")
    print(f"   Narrative Generation: {elapsed_narrative:.2f}ms")
    print(f"   Timeline Generation: {elapsed_timeline:.2f}ms")
    print(f"   Total (sequential): {elapsed_policy + elapsed_narrative + elapsed_timeline:.2f}ms")
    
    # All should be fast
    assert elapsed_policy < 10, "Policy rules should be < 10ms"
    assert elapsed_narrative < 500, "Narrative should be < 500ms"
    assert elapsed_timeline < 10, "Timeline should be < 10ms"
    
    print("\n✅ TEST 5 PASSED: All performance benchmarks met")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 ZEROSITE PHASE 11~14 INTEGRATION TESTS")
    print("="*80)
    
    try:
        test_lh_policy_rules()
        test_academic_narrative()
        test_critical_path()
        comprehensive_output = test_full_integration()
        test_performance()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED (5/5)")
        print("="*80)
        
        print("\n🎉 Phase 11~14 통합 완료!")
        print("\n주요 기능:")
        print("  ✅ Phase 11: LH 정책 규칙 DB")
        print("  ✅ Phase 12: (기존 완성)")
        print("  ✅ Phase 13: Academic Narrative Engine")
        print("  ✅ Phase 14: Critical Path & Timeline")
        print("\n통합 결과:")
        print(f"  • 설계 세대수: {comprehensive_output['design']['units']}세대")
        print(f"  • 서술 섹션: {len(comprehensive_output['narrative']['sections'])}개")
        print(f"  • 프로젝트 기간: {comprehensive_output['timeline']['duration']}개월")
        print("\n✅ 모든 Phase가 정상적으로 통합되어 작동합니다!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
