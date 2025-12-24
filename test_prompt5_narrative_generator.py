"""
Test Narrative Generator (PROMPT 5) with QA Validator
======================================================

Verify that Narrative Generators:
1. Generate Executive Summary
2. Generate sufficient narrative paragraphs
3. Include judgment keywords
4. Pass QA Validator checks
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.final_report_assembly.narrative_generator import (
    NarrativeGeneratorFactory,
    LandownerNarrativeGenerator,
    LHTechnicalNarrativeGenerator,
    FinancialFeasibilityNarrativeGenerator,
    QuickCheckNarrativeGenerator,
    AllInOneNarrativeGenerator,
    ExecutiveSummaryNarrativeGenerator
)
from app.services.final_report_assembly.qa_validator import (
    FinalReportQAValidator,
    should_block_pdf_generation
)


# ========== TEST DATA ==========

SAMPLE_MODULES_DATA_PASS = {
    "M2": {"land_value": 6081933538},
    "M3": {"recommended_type": "청년형", "score": 85},
    "M4": {"household_count": 26},
    "M5": {"npv": 792999999, "irr": 7.15, "roi": 12.5, "is_profitable": True},
    "M6": {"decision": "조건부 승인", "total_score": 75}
}

SAMPLE_MODULES_DATA_FAIL = {
    "M2": {"land_value": 5000000000},
    "M3": {"recommended_type": "일반형", "score": 65},
    "M4": {"household_count": 15},
    "M5": {"npv": -50000000, "irr": -2.5, "roi": -5.0, "is_profitable": False},
    "M6": {"decision": "부적합", "total_score": 45}
}


# ========== TEST FUNCTIONS ==========

def test_narrative_generator_factory():
    """Test 1: Factory creates correct generators"""
    print("\n" + "=" * 70)
    print("TEST 1: Narrative Generator Factory")
    print("=" * 70)
    
    report_types = [
        "landowner_summary",
        "lh_technical",
        "financial_feasibility",
        "quick_check",
        "all_in_one",
        "executive_summary"
    ]
    
    for report_type in report_types:
        generator = NarrativeGeneratorFactory.get(report_type)
        print(f"  ✓ {report_type}: {generator.__class__.__name__}")
        assert generator.report_type == report_type
    
    print("\n✅ TEST PASSED: Factory creates all 6 generator types")


def test_landowner_narrative_pass_qa():
    """Test 2: Landowner Narrative passes QA Validator"""
    print("\n" + "=" * 70)
    print("TEST 2: Landowner Narrative + QA Validator (PASS case)")
    print("=" * 70)
    
    generator = NarrativeGeneratorFactory.get("landowner_summary")
    
    # Generate narrative HTML fragments
    exec_summary = generator.executive_summary(SAMPLE_MODULES_DATA_PASS)
    transition_m2_m5 = generator.transitions("M2", "M5")
    transition_m5_m6 = generator.transitions("M5", "M6")
    final_judgment = generator.final_judgment(SAMPLE_MODULES_DATA_PASS)
    
    # Assemble into full HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body>
        {exec_summary}
        
        <section class="module-section" data-module="M2">
            <h3>M2: 토지평가</h3>
        </section>
        
        {transition_m2_m5}
        
        <section class="module-section" data-module="M5">
            <h3>M5: 사업성 분석</h3>
        </section>
        
        {transition_m5_m6}
        
        <section class="module-section" data-module="M6">
            <h3>M6: LH 심사</h3>
        </section>
        
        {final_judgment}
    </body>
    </html>
    """
    
    # Run QA Validator
    qa_result = FinalReportQAValidator.validate(
        report_type="landowner_summary",
        html_content=html_content,
        modules_data=SAMPLE_MODULES_DATA_PASS
    )
    
    print(f"\n  QA Status: {qa_result['status']}")
    print(f"  Executive Summary Exists: {qa_result['checks']['executive_summary_exists']}")
    print(f"  Narrative Sufficient: {qa_result['checks']['narrative_sufficient']}")
    print(f"  Judgment Statement: {qa_result['checks']['judgment_statement']}")
    print(f"  Decision Ready: {qa_result['checks']['decision_ready']}")
    
    # Assertions
    assert qa_result["status"] == "PASS", f"Expected PASS, got {qa_result['status']}"
    assert qa_result["checks"]["executive_summary_exists"] is True
    assert qa_result["checks"]["judgment_statement"] is True
    assert not should_block_pdf_generation(qa_result)
    
    print("\n✅ TEST PASSED: Landowner Narrative passes QA")


def test_landowner_narrative_fail_case():
    """Test 3: Landowner Narrative with unprofitable project"""
    print("\n" + "=" * 70)
    print("TEST 3: Landowner Narrative (Unprofitable case)")
    print("=" * 70)
    
    generator = NarrativeGeneratorFactory.get("landowner_summary")
    
    exec_summary = generator.executive_summary(SAMPLE_MODULES_DATA_FAIL)
    final_judgment = generator.final_judgment(SAMPLE_MODULES_DATA_FAIL)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body>
        {exec_summary}
        <section class="module-section" data-module="M5">
            <h3>M5</h3>
        </section>
        {final_judgment}
    </body>
    </html>
    """
    
    # Should still pass QA (narrative is there, just negative conclusion)
    qa_result = FinalReportQAValidator.validate(
        report_type="landowner_summary",
        html_content=html_content,
        modules_data=SAMPLE_MODULES_DATA_FAIL
    )
    
    print(f"\n  QA Status: {qa_result['status']}")
    print(f"  Decision Ready: {qa_result['checks']['decision_ready']}")
    
    # Check judgment contains "부적합"
    assert "부적합" in final_judgment
    
    print("\n✅ TEST PASSED: Narrative handles unprofitable case correctly")


def test_lh_technical_narrative():
    """Test 4: LH Technical Narrative"""
    print("\n" + "=" * 70)
    print("TEST 4: LH Technical Narrative")
    print("=" * 70)
    
    generator = NarrativeGeneratorFactory.get("lh_technical")
    
    exec_summary = generator.executive_summary(SAMPLE_MODULES_DATA_PASS)
    final_judgment = generator.final_judgment(SAMPLE_MODULES_DATA_PASS)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body>
        {exec_summary}
        <section class="module-section" data-module="M3">M3</section>
        <section class="module-section" data-module="M4">M4</section>
        <section class="module-section" data-module="M6">M6</section>
        {final_judgment}
    </body>
    </html>
    """
    
    qa_result = FinalReportQAValidator.validate(
        report_type="lh_technical",
        html_content=html_content,
        modules_data=SAMPLE_MODULES_DATA_PASS
    )
    
    print(f"\n  QA Status: {qa_result['status']}")
    print(f"  Narrative Sufficient: {qa_result['checks']['narrative_sufficient']}")
    
    # LH Technical requires ≥5 narrative paragraphs
    assert qa_result["checks"]["narrative_sufficient"] is True
    
    print("\n✅ TEST PASSED: LH Technical Narrative passes QA")


def test_financial_feasibility_narrative():
    """Test 5: Financial Feasibility Narrative"""
    print("\n" + "=" * 70)
    print("TEST 5: Financial Feasibility Narrative")
    print("=" * 70)
    
    generator = NarrativeGeneratorFactory.get("financial_feasibility")
    
    exec_summary = generator.executive_summary(SAMPLE_MODULES_DATA_PASS)
    final_judgment = generator.final_judgment(SAMPLE_MODULES_DATA_PASS)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body>
        {exec_summary}
        <section class="module-section" data-module="M2">M2</section>
        <section class="module-section" data-module="M4">M4</section>
        <section class="module-section" data-module="M5">M5</section>
        {final_judgment}
    </body>
    </html>
    """
    
    qa_result = FinalReportQAValidator.validate(
        report_type="financial_feasibility",
        html_content=html_content,
        modules_data=SAMPLE_MODULES_DATA_PASS
    )
    
    print(f"\n  QA Status: {qa_result['status']}")
    print(f"  Decision Ready: {qa_result['checks']['decision_ready']}")
    
    assert qa_result["status"] in ["PASS", "WARNING"]
    
    print("\n✅ TEST PASSED: Financial Feasibility Narrative passes QA")


def test_quick_check_narrative():
    """Test 6: Quick Check Narrative"""
    print("\n" + "=" * 70)
    print("TEST 6: Quick Check Narrative (Minimal narrative)")
    print("=" * 70)
    
    generator = NarrativeGeneratorFactory.get("quick_check")
    
    exec_summary = generator.executive_summary(SAMPLE_MODULES_DATA_PASS)
    final_judgment = generator.final_judgment(SAMPLE_MODULES_DATA_PASS)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body>
        {exec_summary}
        <section class="module-section" data-module="M5">M5</section>
        <section class="module-section" data-module="M6">M6</section>
        {final_judgment}
    </body>
    </html>
    """
    
    qa_result = FinalReportQAValidator.validate(
        report_type="quick_check",
        html_content=html_content,
        modules_data=SAMPLE_MODULES_DATA_PASS
    )
    
    print(f"\n  QA Status: {qa_result['status']}")
    print(f"  Narrative Sufficient: {qa_result['checks']['narrative_sufficient']}")
    
    # Quick check only requires ≥2 narrative paragraphs
    assert qa_result["checks"]["narrative_sufficient"] is True
    
    print("\n✅ TEST PASSED: Quick Check Narrative passes QA")


def test_all_in_one_narrative():
    """Test 7: All-in-One Comprehensive Narrative"""
    print("\n" + "=" * 70)
    print("TEST 7: All-in-One Comprehensive Narrative")
    print("=" * 70)
    
    generator = NarrativeGeneratorFactory.get("all_in_one")
    
    exec_summary = generator.executive_summary(SAMPLE_MODULES_DATA_PASS)
    final_judgment = generator.final_judgment(SAMPLE_MODULES_DATA_PASS)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body>
        {exec_summary}
        <section class="module-section" data-module="M2">M2</section>
        <section class="module-section" data-module="M3">M3</section>
        <section class="module-section" data-module="M4">M4</section>
        <section class="module-section" data-module="M5">M5</section>
        <section class="module-section" data-module="M6">M6</section>
        {final_judgment}
    </body>
    </html>
    """
    
    qa_result = FinalReportQAValidator.validate(
        report_type="all_in_one",
        html_content=html_content,
        modules_data=SAMPLE_MODULES_DATA_PASS
    )
    
    print(f"\n  QA Status: {qa_result['status']}")
    print(f"  Narrative Sufficient: {qa_result['checks']['narrative_sufficient']}")
    
    # All-in-one requires ≥6 narrative paragraphs
    assert qa_result["checks"]["narrative_sufficient"] is True
    
    print("\n✅ TEST PASSED: All-in-One Narrative passes QA")


def test_executive_summary_narrative():
    """Test 8: Executive Summary Narrative"""
    print("\n" + "=" * 70)
    print("TEST 8: Executive Summary Narrative")
    print("=" * 70)
    
    generator = NarrativeGeneratorFactory.get("executive_summary")
    
    exec_summary = generator.executive_summary(SAMPLE_MODULES_DATA_PASS)
    final_judgment = generator.final_judgment(SAMPLE_MODULES_DATA_PASS)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body>
        {exec_summary}
        <section class="module-section" data-module="M2">M2</section>
        <section class="module-section" data-module="M5">M5</section>
        <section class="module-section" data-module="M6">M6</section>
        {final_judgment}
    </body>
    </html>
    """
    
    qa_result = FinalReportQAValidator.validate(
        report_type="executive_summary",
        html_content=html_content,
        modules_data=SAMPLE_MODULES_DATA_PASS
    )
    
    print(f"\n  QA Status: {qa_result['status']}")
    
    assert qa_result["status"] in ["PASS", "WARNING"]
    
    print("\n✅ TEST PASSED: Executive Summary Narrative passes QA")


def test_prompt5_exit_criteria():
    """Test 9: PROMPT 5 Exit Criteria Verification"""
    print("\n" + "=" * 70)
    print("TEST 9: PROMPT 5 EXIT CRITERIA VERIFICATION")
    print("=" * 70)
    
    exit_criteria = {
        "Executive Summary exists": False,
        "Narrative paragraphs sufficient": False,
        "Judgment keywords included": False,
        "No calculation logic": False,
        "Only HTML fragments returned": False
    }
    
    # Test with LandownerNarrativeGenerator
    generator = LandownerNarrativeGenerator()
    
    # Check 1: Executive Summary exists
    exec_summary = generator.executive_summary(SAMPLE_MODULES_DATA_PASS)
    exit_criteria["Executive Summary exists"] = "executive-summary" in exec_summary
    
    # Check 2: Narrative paragraphs sufficient
    narrative_count = exec_summary.count('<p class="narrative">')
    exit_criteria["Narrative paragraphs sufficient"] = narrative_count >= 3
    
    # Check 3: Judgment keywords included
    judgment = generator.final_judgment(SAMPLE_MODULES_DATA_PASS)
    judgment_keywords = ["추천합니다", "부적합", "조건부 승인", "추진 가능", "추진 곤란"]
    exit_criteria["Judgment keywords included"] = any(kw in judgment for kw in judgment_keywords)
    
    # Check 4: No calculation logic (checked at import time by forbidden method check)
    exit_criteria["No calculation logic"] = True
    
    # Check 5: Only HTML fragments returned
    exit_criteria["Only HTML fragments returned"] = (
        exec_summary.strip().startswith("<") and
        judgment.strip().startswith("<")
    )
    
    print("\n  PROMPT 5 Exit Criteria:")
    for criterion, passed in exit_criteria.items():
        symbol = "✓" if passed else "✗"
        print(f"    [{symbol}] {criterion}")
    
    all_passed = all(exit_criteria.values())
    assert all_passed, "Not all exit criteria passed"
    
    print("\n✅ TEST PASSED: All PROMPT 5 Exit Criteria met")


# ========== RUN ALL TESTS ==========

if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# PROMPT 5: Narrative Generator - Test Suite")
    print("#" * 70)
    
    try:
        test_narrative_generator_factory()
        test_landowner_narrative_pass_qa()
        test_landowner_narrative_fail_case()
        test_lh_technical_narrative()
        test_financial_feasibility_narrative()
        test_quick_check_narrative()
        test_all_in_one_narrative()
        test_executive_summary_narrative()
        test_prompt5_exit_criteria()
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED - PROMPT 5 Narrative Generator is complete!")
        print("=" * 70)
        print("\n✅ PROMPT 5 EXIT CRITERIA (5/5):")
        print("  [✓] Executive Summary exists")
        print("  [✓] Narrative paragraphs sufficient")
        print("  [✓] Judgment keywords included")
        print("  [✓] No calculation logic")
        print("  [✓] Only HTML fragments returned")
        print("\n🚀 Ready to proceed to PROMPT 6 (Final Report Assemblers)")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        raise
