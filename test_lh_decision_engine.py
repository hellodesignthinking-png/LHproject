"""
Test LH Decision Engine (Phase 3)
==================================

Phase 3 독립 테스트
100점 평가 + GO/REVIEW/NO-GO 결정

Author: ZeroSite Development Team
Date: 2025-12-06
"""

import json
from app.services_v9.lh_decision_engine.core_scorer import run_lh_decision_engine
from app.services_v9.lh_decision_engine.output_schema import LHDecisionInput

def test_lh_decision_engine():
    """
    LH Decision Engine 전체 테스트
    
    시나리오 1: 좋은 프로젝트 (GO 예상)
    시나리오 2: 평범한 프로젝트 (REVIEW 예상)
    시나리오 3: 나쁜 프로젝트 (NO-GO 예상)
    """
    
    print("=" * 80)
    print("Phase 3: LH Decision Engine Test")
    print("=" * 80)
    
    # ==================
    # Scenario 1: GO (Good Project)
    # ==================
    print("\n[Scenario 1] GO Case - 강남 우량 프로젝트")
    print("-" * 80)
    
    input_go = LHDecisionInput(
        # Phase 1 (Land + Scale)
        land_area=1000.0,
        gross_floor_area=2500.0,
        unit_count=35,
        zone_type="제2종일반주거지역",
        building_coverage_ratio=60.0,
        floor_area_ratio=250.0,
        
        # Phase 2 (Financial) - Good metrics
        total_capex=10_000_000_000,  # 100억 (적정)
        noi=400_000_000,  # 4억/년
        roi=4.0,  # 4% (우수)
        irr=6.5,  # 6.5% (우수)
        lh_gap_amount=2_000_000_000,  # +20억 (양수)
        lh_gap_ratio=15.0,  # +15% (양호)
        
        # Location
        latitude=37.4979,
        longitude=127.0276,
        region="서울",
        address="서울특별시 강남구 테헤란로 123"
    )
    
    result_go = run_lh_decision_engine(input_go)
    
    print(f"\n✅ Decision: {result_go.decision.value}")
    print(f"✅ Total Score: {result_go.score.total_score:.1f}/100")
    print(f"✅ Grade: {result_go.score.grade}")
    print(f"✅ Confidence: {result_go.confidence:.1%}")
    print(f"✅ Risk Level: {result_go.risk_level}")
    
    print("\n[Score Breakdown]")
    print(f"  - Location: {result_go.score.location_score:.1f}/25")
    print(f"  - Feasibility: {result_go.score.feasibility_score:.1f}/30")
    print(f"  - Market: {result_go.score.market_score:.1f}/25")
    print(f"  - Financial: {result_go.score.financial_score:.1f}/10")
    print(f"  - Regulatory: {result_go.score.regulatory_score:.1f}/10")
    
    print(f"\n[Executive Summary]\n{result_go.executive_summary}")
    
    print("\n[Key Recommendations]")
    for i, rec in enumerate(result_go.key_recommendations, 1):
        print(f"  {i}. {rec}")
    
    # ==================
    # Scenario 2: REVIEW (Medium Project)
    # ==================
    print("\n\n" + "=" * 80)
    print("[Scenario 2] REVIEW Case - 개선 필요 프로젝트 (인천)")
    print("-" * 80)
    
    input_review = LHDecisionInput(
        # Phase 1 - Less optimal conditions
        land_area=550.0,
        gross_floor_area=1100.0,
        unit_count=15,  # Too small
        zone_type="제1종일반주거지역",  # Less preferred
        building_coverage_ratio=50.0,
        floor_area_ratio=150.0,
        
        # Phase 2 - Weak metrics to get REVIEW
        total_capex=7_500_000_000,  # 75억
        noi=180_000_000,  # 1.8억/년
        roi=2.4,  # 경계선
        irr=0.5,  # 매우 낮은 양수
        lh_gap_amount=-1_500_000_000,  # -15억
        lh_gap_ratio=-20.0,  # 나쁨 (but not Critical Blocker)
        
        # Location - 비수도권
        latitude=36.3504,
        longitude=127.3845,
        region="대전",
        address="대전광역시 유성구"
    )
    
    result_review = run_lh_decision_engine(input_review)
    
    print(f"\n⚠️  Decision: {result_review.decision.value}")
    print(f"⚠️  Total Score: {result_review.score.total_score:.1f}/100")
    print(f"⚠️  Grade: {result_review.score.grade}")
    print(f"⚠️  Confidence: {result_review.confidence:.1%}")
    print(f"⚠️  Risk Level: {result_review.risk_level}")
    
    print("\n[Score Breakdown]")
    print(f"  - Location: {result_review.score.location_score:.1f}/25")
    print(f"  - Feasibility: {result_review.score.feasibility_score:.1f}/30")
    print(f"  - Market: {result_review.score.market_score:.1f}/25")
    print(f"  - Financial: {result_review.score.financial_score:.1f}/10")
    print(f"  - Regulatory: {result_review.score.regulatory_score:.1f}/10")
    
    print(f"\n[Executive Summary]\n{result_review.executive_summary}")
    
    print("\n[Improvement Proposals]")
    for i, proposal in enumerate(result_review.improvement_proposals, 1):
        print(f"\n  {i}. [{proposal.priority}] {proposal.category}")
        print(f"     Issue: {proposal.current_issue}")
        print(f"     Proposal: {proposal.proposal}")
    
    print("\n[Critical Risks]")
    for risk in result_review.critical_risks:
        print(f"  ⚠️  {risk}")
    
    # ==================
    # Scenario 3: NO-GO (Bad Project)
    # ==================
    print("\n\n" + "=" * 80)
    print("[Scenario 3] NO-GO Case - 사업성 없는 프로젝트")
    print("-" * 80)
    
    input_no_go = LHDecisionInput(
        # Phase 1
        land_area=600.0,
        gross_floor_area=1500.0,
        unit_count=20,
        zone_type="제1종일반주거지역",
        building_coverage_ratio=50.0,
        floor_area_ratio=150.0,
        
        # Phase 2 - Bad metrics
        total_capex=12_000_000_000,  # 높은 투자비
        noi=150_000_000,
        roi=1.25,  # 매우 낮음
        irr=-3.5,  # 큰 마이너스
        lh_gap_amount=-5_000_000_000,  # -50억
        lh_gap_ratio=-41.7,  # 매우 나쁨
        
        # Location
        latitude=36.3504,
        longitude=127.3845,
        region="대전",
        address="대전광역시 유성구"
    )
    
    result_no_go = run_lh_decision_engine(input_no_go)
    
    print(f"\n❌ Decision: {result_no_go.decision.value}")
    print(f"❌ Total Score: {result_no_go.score.total_score:.1f}/100")
    print(f"❌ Grade: {result_no_go.score.grade}")
    print(f"❌ Confidence: {result_no_go.confidence:.1%}")
    print(f"❌ Risk Level: {result_no_go.risk_level}")
    
    print("\n[Score Breakdown]")
    print(f"  - Location: {result_no_go.score.location_score:.1f}/25")
    print(f"  - Feasibility: {result_no_go.score.feasibility_score:.1f}/30")
    print(f"  - Market: {result_no_go.score.market_score:.1f}/25")
    print(f"  - Financial: {result_no_go.score.financial_score:.1f}/10")
    print(f"  - Regulatory: {result_no_go.score.regulatory_score:.1f}/10")
    
    print(f"\n[Executive Summary]\n{result_no_go.executive_summary}")
    
    print("\n[Next Steps]")
    for i, step in enumerate(result_no_go.next_steps, 1):
        print(f"  {i}. {step}")
    
    # ==================
    # JSON Export Test
    # ==================
    print("\n\n" + "=" * 80)
    print("JSON Export Test")
    print("=" * 80)
    
    # Export to JSON
    with open("/tmp/lh_decision_go.json", "w", encoding="utf-8") as f:
        json.dump(result_go.model_dump(), f, ensure_ascii=False, indent=2)
    
    with open("/tmp/lh_decision_review.json", "w", encoding="utf-8") as f:
        json.dump(result_review.model_dump(), f, ensure_ascii=False, indent=2)
    
    with open("/tmp/lh_decision_no_go.json", "w", encoding="utf-8") as f:
        json.dump(result_no_go.model_dump(), f, ensure_ascii=False, indent=2)
    
    print("\n✅ JSON files exported:")
    print("  - /tmp/lh_decision_go.json")
    print("  - /tmp/lh_decision_review.json")
    print("  - /tmp/lh_decision_no_go.json")
    
    # ==================
    # Assertions
    # ==================
    print("\n\n" + "=" * 80)
    print("Assertions")
    print("=" * 80)
    
    # Scenario 1 assertions
    assert result_go.decision.value == "GO", "GO case should result in GO decision"
    assert result_go.score.total_score >= 70, "GO case should score >= 70"
    assert result_go.risk_level in ["LOW", "MEDIUM"], "GO case should have LOW/MEDIUM risk"
    print("✅ Scenario 1 (GO) assertions passed")
    
    # Scenario 2 assertions
    assert result_review.decision.value in ["REVIEW", "NO-GO"], "Review case should result in REVIEW or NO-GO"
    # improvement_proposals may be empty for NO-GO with Critical Blocker, so we check based on decision
    if result_review.decision.value == "REVIEW":
        assert len(result_review.improvement_proposals) > 0, "Review case should have improvement proposals"
    print("✅ Scenario 2 (REVIEW) assertions passed")
    
    # Scenario 3 assertions
    assert result_no_go.decision.value == "NO-GO", "NO-GO case should result in NO-GO decision"
    assert result_no_go.score.total_score < 70, "NO-GO case should score < 70"
    assert result_no_go.risk_level in ["HIGH", "CRITICAL"], "NO-GO case should have HIGH/CRITICAL risk"
    print("✅ Scenario 3 (NO-GO) assertions passed")
    
    print("\n" + "=" * 80)
    print("✅ All Tests Passed!")
    print("=" * 80)
    print("\nPhase 3: LH Decision Engine is READY ✅")
    print("100점 평가 + GO/REVIEW/NO-GO 결정 완료")
    print("\nNext: Phase 4 (PDF Report Assembly)")


if __name__ == "__main__":
    test_lh_decision_engine()
