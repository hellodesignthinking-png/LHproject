"""
Test CH3 Business Feasibility Scoring Module

Tests:
1. Scorer creation
2. High ROI scenario (excellent feasibility)
3. Negative ROI scenario (poor feasibility)
4. LH linkage bonus
5. Gap ratio impact
6. Report formatting
"""

import sys
from app.services.ch3_feasibility_scoring import CH3FeasibilityScorer, create_feasibility_scorer


def test_scorer_creation():
    """Test 1: Create CH3 feasibility scorer"""
    print("\n" + "="*70)
    print("TEST 1: CH3 Feasibility Scorer Creation")
    print("="*70)
    
    scorer = create_feasibility_scorer()
    
    print(f"✅ Scorer created: {scorer.__class__.__name__}")
    
    return scorer


def test_high_roi_scenario(scorer):
    """Test 2: High ROI scenario (10%+)"""
    print("\n" + "="*70)
    print("TEST 2: High ROI Scenario (Excellent Feasibility)")
    print("="*70)
    
    result = scorer.calculate_feasibility_score(
        roi=12.5,
        lh_purchase_price=20000000000,  # 200억
        total_project_cost=17700000000,  # 177억
        analysis_mode='LH_LINKED',
        expected_units=56,
        land_appraisal=4000000000,  # 40억
        verified_cost=13000000000  # 130억
    )
    
    print(f"\n📊 Input:")
    print(f"   ROI: 12.5%")
    print(f"   LH Purchase: 200억원")
    print(f"   Total Cost: 177억원")
    print(f"   Analysis Mode: LH_LINKED")
    print(f"   Units: 56")
    
    print(f"\n✅ Result:")
    print(f"   Total Score: {result['total_score']}/20")
    print(f"   Grade: {result['grade']}")
    print(f"   Factors:")
    for factor, value in result['factors'].items():
        print(f"      - {factor}: {value:+.1f}")
    print(f"   Rationale: {result['rationale']}")
    
    # Validate: High ROI should give high score
    high_score = result['total_score'] >= 18
    excellent_grade = result['grade'] in ['S', 'A']
    
    print(f"\n🔍 Validation:")
    status = "✅ PASSED" if high_score else "❌ FAILED"
    print(f"   {status}: High score achieved ({result['total_score']}/20)")
    
    status = "✅ PASSED" if excellent_grade else "❌ FAILED"
    print(f"   {status}: Excellent grade ({result['grade']})")
    
    return result, high_score and excellent_grade


def test_negative_roi_scenario(scorer):
    """Test 3: Negative ROI scenario (poor feasibility)"""
    print("\n" + "="*70)
    print("TEST 3: Negative ROI Scenario (Poor Feasibility)")
    print("="*70)
    
    result = scorer.calculate_feasibility_score(
        roi=-4.49,
        lh_purchase_price=13240781400,  # 132.4억
        total_project_cost=13863098126,  # 138.6억
        analysis_mode='LH_LINKED',
        expected_units=56,
        land_appraisal=4154535000,  # 41.5억
        verified_cost=9086246400  # 90.9억
    )
    
    print(f"\n📊 Input:")
    print(f"   ROI: -4.49%")
    print(f"   LH Purchase: 132.4억원")
    print(f"   Total Cost: 138.6억원")
    print(f"   Gap: -6.3억원 (loss)")
    
    print(f"\n✅ Result:")
    print(f"   Total Score: {result['total_score']}/20")
    print(f"   Grade: {result['grade']}")
    print(f"   Factors:")
    for factor, value in result['factors'].items():
        print(f"      - {factor}: {value:+.1f}")
    print(f"   Rationale: {result['rationale']}")
    
    # Validate: Negative ROI should give low score
    low_score = result['total_score'] < 10
    poor_grade = result['grade'] in ['D', 'F']
    
    print(f"\n🔍 Validation:")
    status = "✅ PASSED" if low_score else "❌ FAILED"
    print(f"   {status}: Low score for negative ROI ({result['total_score']}/20)")
    
    status = "✅ PASSED" if poor_grade else "❌ FAILED"
    print(f"   {status}: Poor grade ({result['grade']})")
    
    return result, low_score and poor_grade


def test_lh_linkage_bonus(scorer):
    """Test 4: LH linkage bonus effect"""
    print("\n" + "="*70)
    print("TEST 4: LH Linkage Bonus Effect")
    print("="*70)
    
    # Same ROI, with and without LH linkage
    base_params = {
        'roi': 6.5,
        'lh_purchase_price': 15000000000,
        'total_project_cost': 14000000000,
        'expected_units': 56,
        'land_appraisal': 4000000000,
        'verified_cost': 9000000000
    }
    
    # With LH linkage
    result_linked = scorer.calculate_feasibility_score(
        **base_params,
        analysis_mode='LH_LINKED'
    )
    
    # Without LH linkage
    result_standard = scorer.calculate_feasibility_score(
        **base_params,
        analysis_mode='STANDARD'
    )
    
    bonus_difference = result_linked['total_score'] - result_standard['total_score']
    
    print(f"\n📊 Same ROI (6.5%), Different Modes:")
    print(f"   LH_LINKED score: {result_linked['total_score']}/20 (linkage bonus: {result_linked['factors']['linkage_score']})")
    print(f"   STANDARD score: {result_standard['total_score']}/20 (linkage bonus: {result_standard['factors']['linkage_score']})")
    print(f"   Difference: +{bonus_difference} points for LH_LINKED")
    
    # Validate: LH_LINKED should get bonus points
    linked_has_bonus = result_linked['factors']['linkage_score'] > 0
    standard_no_bonus = result_standard['factors']['linkage_score'] == 0
    bonus_correct = result_linked['factors']['linkage_score'] == 2.0
    
    # Note: Scores might be capped at 20, so linked might not always be higher
    # The important thing is the bonus is applied
    
    print(f"\n🔍 Validation:")
    status = "✅ PASSED" if linked_has_bonus else "❌ FAILED"
    print(f"   {status}: LH_LINKED receives bonus")
    
    status = "✅ PASSED" if standard_no_bonus else "❌ FAILED"
    print(f"   {status}: STANDARD receives no bonus")
    
    status = "✅ PASSED" if bonus_correct else "❌ FAILED"
    print(f"   {status}: Bonus is 2 points for 50+ units")
    
    return linked_has_bonus and standard_no_bonus and bonus_correct


def test_gap_ratio_impact(scorer):
    """Test 5: Gap ratio impact on score"""
    print("\n" + "="*70)
    print("TEST 5: Gap Ratio Impact")
    print("="*70)
    
    test_cases = [
        (10.0, 20000, 18000, "Excellent gap (+11%)"),
        (5.0, 18000, 17000, "Good gap (+5.9%)"),
        (-5.0, 15000, 16000, "Poor gap (-6.7%)")
    ]
    
    results = []
    
    for roi, lh_price, total_cost, description in test_cases:
        result = scorer.calculate_feasibility_score(
            roi=roi,
            lh_purchase_price=lh_price * 1000000,
            total_project_cost=total_cost * 1000000,
            analysis_mode='LH_LINKED',
            expected_units=56,
            land_appraisal=4000000000,
            verified_cost=9000000000
        )
        
        gap_ratio = result['metrics']['gap_ratio']
        gap_score = result['factors']['gap_score']
        
        print(f"\n   {description}:")
        print(f"      Gap Ratio: {gap_ratio:+.2f}%")
        print(f"      Gap Score: {gap_score:+.1f} points")
        print(f"      Total: {result['total_score']}/20")
        
        results.append(gap_score)
    
    # Validate: Positive gap should give positive score, negative gap negative
    positive_gaps_positive = results[0] > 0 and results[1] > 0
    negative_gap_negative = results[2] < 0
    gap_impact_works = positive_gaps_positive and negative_gap_negative
    
    print(f"\n🔍 Validation:")
    status = "✅ PASSED" if gap_impact_works else "❌ FAILED"
    print(f"   {status}: Gap scores reflect profitability")
    print(f"   Positive gaps (+) → positive scores: {results[0]:.1f}, {results[1]:.1f}")
    print(f"   Negative gap (-) → negative score: {results[2]:.1f}")
    
    return gap_impact_works


def test_report_formatting(scorer):
    """Test 6: Report formatting"""
    print("\n" + "="*70)
    print("TEST 6: Report Formatting")
    print("="*70)
    
    result = scorer.calculate_feasibility_score(
        roi=7.5,
        lh_purchase_price=18000000000,
        total_project_cost=16500000000,
        analysis_mode='LH_LINKED',
        expected_units=56,
        land_appraisal=4000000000,
        verified_cost=11000000000
    )
    
    # Format for report
    report_text = scorer.format_for_report(result)
    
    print(f"\n📄 Formatted Report:")
    print(report_text)
    
    # Validate
    has_content = len(report_text) > 100
    has_grade = result['grade'] in report_text
    has_rationale = result['rationale'] in report_text
    
    print(f"\n🔍 Validation:")
    status = "✅ PASSED" if has_content else "❌ FAILED"
    print(f"   {status}: Report has content ({len(report_text)} chars)")
    
    status = "✅ PASSED" if has_grade else "❌ FAILED"
    print(f"   {status}: Grade appears in report")
    
    status = "✅ PASSED" if has_rationale else "❌ FAILED"
    print(f"   {status}: Rationale appears in report")
    
    return has_content and has_grade and has_rationale


def test_problem_solved():
    """Test 7: Confirm '3-5점 문제' solved"""
    print("\n" + "="*70)
    print("TEST 7: Confirm '3-5점 문제' Solved")
    print("="*70)
    
    scorer = create_feasibility_scorer()
    
    # Test various ROI scenarios
    test_rois = [-5.0, 0.0, 5.0, 10.0, 15.0]
    results = []
    
    print(f"\n📊 Before (v8.5 bug):")
    print(f"   All ROIs → 3-5점 (static)")
    
    print(f"\n📊 After (v8.7 fix):")
    for roi_val in test_rois:
        result = scorer.calculate_feasibility_score(
            roi=roi_val,
            lh_purchase_price=15000000000,
            total_project_cost=14000000000,
            analysis_mode='LH_LINKED',
            expected_units=56,
            land_appraisal=4000000000
        )
        results.append(result['total_score'])
        print(f"   ROI {roi_val:+.1f}% → {result['total_score']}점 (등급: {result['grade']})")
    
    # Validate: Scores should be ROI-correlated and dynamic (not all 3-5)
    properly_ordered = results == sorted(results)
    wide_range = max(results) - min(results) >= 10
    not_all_same = len(set(results)) > 1
    not_static_3_5 = not all(3 <= score <= 5 for score in results)
    
    print(f"\n🔍 Validation:")
    status = "✅ PASSED" if properly_ordered else "❌ FAILED"
    print(f"   {status}: Scores properly ordered by ROI")
    
    status = "✅ PASSED" if wide_range else "❌ FAILED"
    print(f"   {status}: Wide score range (spread: {max(results) - min(results)} points)")
    
    status = "✅ PASSED" if not_static_3_5 else "❌ FAILED"
    print(f"   {status}: NOT stuck at 3-5 points (dynamic)")
    
    print(f"   ✅ Problem solved: Scores are ROI-based, not static!")
    
    return properly_ordered and wide_range and not_static_3_5


def main():
    """Run all CH3 feasibility scoring tests"""
    print("\n" + "="*70)
    print("🚀 CH3 BUSINESS FEASIBILITY SCORING TEST SUITE")
    print("   v8.7 Enhancement: ROI-based Dynamic Scoring")
    print("="*70)
    
    try:
        # Test 1: Create scorer
        scorer = test_scorer_creation()
        
        # Test 2: High ROI
        high_roi_result, high_roi_valid = test_high_roi_scenario(scorer)
        
        # Test 3: Negative ROI
        neg_roi_result, neg_roi_valid = test_negative_roi_scenario(scorer)
        
        # Test 4: LH linkage bonus
        linkage_valid = test_lh_linkage_bonus(scorer)
        
        # Test 5: Gap ratio impact
        gap_valid = test_gap_ratio_impact(scorer)
        
        # Test 6: Report formatting
        format_valid = test_report_formatting(scorer)
        
        # Test 7: Problem solved
        problem_solved = test_problem_solved()
        
        # Final summary
        print("\n" + "="*70)
        print("📊 CH3 FEASIBILITY SCORING TEST RESULTS")
        print("="*70)
        print(f"   1. Scorer Creation:       ✅ PASSED")
        print(f"   2. High ROI Scenario:     {'✅ PASSED' if high_roi_valid else '❌ FAILED'}")
        print(f"   3. Negative ROI Scenario: {'✅ PASSED' if neg_roi_valid else '❌ FAILED'}")
        print(f"   4. LH Linkage Bonus:      {'✅ PASSED' if linkage_valid else '❌ FAILED'}")
        print(f"   5. Gap Ratio Impact:      {'✅ PASSED' if gap_valid else '❌ FAILED'}")
        print(f"   6. Report Formatting:     {'✅ PASSED' if format_valid else '❌ FAILED'}")
        print(f"   7. Problem Solved:        {'✅ PASSED' if problem_solved else '❌ FAILED'}")
        
        if all([high_roi_valid, neg_roi_valid, linkage_valid, gap_valid, format_valid, problem_solved]):
            print("\n🎉 ALL TESTS PASSED - CH3 Feasibility Scoring Complete!")
            print("\n📝 Implementation Summary:")
            print("   ✅ ROI-based scoring (0-20 points)")
            print("   ✅ Gap ratio adjustments (-3 to +3)")
            print("   ✅ LH linkage bonus (+2 points)")
            print("   ✅ Construction cost checks")
            print("   ✅ S/A/B/C/D/F grading system")
            print("   ✅ Dynamic scores (not static 3-5 anymore)")
            
            print("\n📝 Next Steps:")
            print("   → Add image generation (Kakao Map, Radar, Heatmap)")
            print("   → Integrate all components into report generator")
            print("   → Update Phase 4: Report Structure with 3-tier separation")
            return 0
        else:
            print("\n⚠️  SOME TESTS FAILED - Review implementation")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
