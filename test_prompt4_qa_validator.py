"""
Test Final Report QA Validator (PROMPT 4)
==========================================

Tests for Extended QA Validator that validates "decision-readiness"
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.final_report_assembly.qa_validator import (
    FinalReportQAValidator,
    should_block_pdf_generation,
    log_qa_result
)


# ========== TEST SCENARIOS ==========

def test_scenario_1_pass():
    """
    SCENARIO 1: PASS
    - Executive summary exists
    - Sufficient narrative
    - Judgment statement present
    - Decision ready
    """
    print("\n" + "=" * 70)
    print("TEST SCENARIO 1: PASS (All checks pass)")
    print("=" * 70)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <section class="executive-summary">
            <h2>Executive Summary</h2>
            <p class="narrative">이 토지는 LH 공공기여형 민간임대 사업에 적합합니다.</p>
            <p class="narrative">재무 분석 결과 수익성이 확인되었습니다.</p>
            <p class="narrative">LH 심사 결과도 긍정적입니다.</p>
        </section>
        
        <section class="module-section" data-module="M2">
            <h3>M2: 토지평가</h3>
            <p>토지 감정가: 6,081,933,538원</p>
        </section>
        
        <section class="module-section" data-module="M5">
            <h3>M5: 사업성 분석</h3>
            <p>NPV: 792,999,999원</p>
        </section>
        
        <section class="module-section" data-module="M6">
            <h3>M6: LH 심사</h3>
            <p>결과: 조건부 승인</p>
        </section>
        
        <section class="recommendation">
            <h2>최종 의견</h2>
            <p class="judgment">본 사업을 <strong>추천합니다</strong>.</p>
        </section>
    </body>
    </html>
    """
    
    modules_data = {
        "M2": {"land_value": 6081933538},
        "M5": {"is_profitable": True, "npv": 792999999},
        "M6": {"decision": "조건부 승인"}
    }
    
    result = FinalReportQAValidator.validate(
        report_type="landowner_summary",
        html_content=html_content,
        modules_data=modules_data
    )
    
    log_qa_result(result)
    
    # Assertions
    assert result["status"] == "PASS", f"Expected PASS, got {result['status']}"
    assert not should_block_pdf_generation(result), "PDF should NOT be blocked"
    assert len(result["blocking_issues"]) == 0, "No blocking issues expected"
    
    print("\n✅ TEST PASSED: Scenario 1 (PASS)")


def test_scenario_2_fail_missing_executive_summary():
    """
    SCENARIO 2: FAIL - Missing Executive Summary
    """
    print("\n" + "=" * 70)
    print("TEST SCENARIO 2: FAIL (Missing Executive Summary)")
    print("=" * 70)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <section class="module-section" data-module="M2">
            <h3>M2: 토지평가</h3>
        </section>
        
        <section class="recommendation">
            <p>사업을 추천합니다.</p>
        </section>
    </body>
    </html>
    """
    
    modules_data = {
        "M5": {"is_profitable": True, "npv": 100000000},
        "M6": {"decision": "승인"}
    }
    
    result = FinalReportQAValidator.validate(
        report_type="landowner_summary",
        html_content=html_content,
        modules_data=modules_data
    )
    
    log_qa_result(result)
    
    # Assertions
    assert result["status"] == "FAIL", f"Expected FAIL, got {result['status']}"
    assert should_block_pdf_generation(result), "PDF SHOULD be blocked"
    assert "missing_executive_summary" in result["blocking_issues"]
    
    print("\n✅ TEST PASSED: Scenario 2 (FAIL - Missing Exec Summary)")


def test_scenario_3_fail_no_judgment():
    """
    SCENARIO 3: FAIL - No Judgment Statement
    """
    print("\n" + "=" * 70)
    print("TEST SCENARIO 3: FAIL (No Judgment Statement)")
    print("=" * 70)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <section class="executive-summary">
            <h2>요약</h2>
            <p class="narrative">분석 결과입니다.</p>
            <p class="narrative">데이터는 다음과 같습니다.</p>
            <p class="narrative">추가 검토가 필요합니다.</p>
        </section>
        
        <section class="module-section">
            <h3>M5</h3>
            <p>NPV: 100,000원</p>
        </section>
    </body>
    </html>
    """
    
    modules_data = {
        "M5": {"is_profitable": True, "npv": 100000},
        "M6": {"decision": "승인"}
    }
    
    result = FinalReportQAValidator.validate(
        report_type="landowner_summary",
        html_content=html_content,
        modules_data=modules_data
    )
    
    log_qa_result(result)
    
    # Assertions
    assert result["status"] == "FAIL", f"Expected FAIL, got {result['status']}"
    assert should_block_pdf_generation(result), "PDF SHOULD be blocked"
    assert "missing_judgment_statement" in result["blocking_issues"]
    
    print("\n✅ TEST PASSED: Scenario 3 (FAIL - No Judgment)")


def test_scenario_4_warning_insufficient_narrative():
    """
    SCENARIO 4: WARNING - Insufficient Narrative
    """
    print("\n" + "=" * 70)
    print("TEST SCENARIO 4: WARNING (Insufficient Narrative)")
    print("=" * 70)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <section class="executive-summary">
            <h2>Executive Summary</h2>
            <p class="narrative">This is a brief summary.</p>
        </section>
        
        <section class="module-section">
            <h3>M5</h3>
        </section>
        
        <section class="recommendation">
            <p>사업을 추천합니다.</p>
        </section>
    </body>
    </html>
    """
    
    modules_data = {
        "M5": {"is_profitable": True, "npv": 100000000},
        "M6": {"decision": "승인"}
    }
    
    result = FinalReportQAValidator.validate(
        report_type="landowner_summary",  # Requires ≥3 narrative paragraphs
        html_content=html_content,
        modules_data=modules_data
    )
    
    log_qa_result(result)
    
    # Assertions
    assert result["status"] == "WARNING", f"Expected WARNING, got {result['status']}"
    assert not should_block_pdf_generation(result), "PDF should NOT be blocked for WARNING"
    assert len(result["warnings"]) > 0
    
    print("\n✅ TEST PASSED: Scenario 4 (WARNING - Insufficient Narrative)")


def test_scenario_5_warning_not_decision_ready():
    """
    SCENARIO 5: WARNING - Not Decision Ready (M5 not profitable)
    """
    print("\n" + "=" * 70)
    print("TEST SCENARIO 5: WARNING (Not Decision Ready)")
    print("=" * 70)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <section class="executive-summary">
            <h2>요약</h2>
            <p class="narrative">분석 결과를 보고드립니다.</p>
            <p class="narrative">재무 분석이 완료되었습니다.</p>
            <p class="narrative">추가 검토가 필요한 상황입니다.</p>
        </section>
        
        <section class="module-section" data-module="M5">
            <h3>M5</h3>
            <p>NPV: -50,000,000원</p>
        </section>
        
        <section class="recommendation">
            <p class="judgment">현 조건에서는 사업 추진이 <strong>부적합</strong>합니다.</p>
        </section>
    </body>
    </html>
    """
    
    modules_data = {
        "M5": {"is_profitable": False, "npv": -50000000},
        "M6": {"decision": "조건부 승인"}
    }
    
    result = FinalReportQAValidator.validate(
        report_type="landowner_summary",
        html_content=html_content,
        modules_data=modules_data
    )
    
    log_qa_result(result)
    
    # Assertions
    assert result["status"] == "WARNING", f"Expected WARNING, got {result['status']}"
    assert not should_block_pdf_generation(result), "PDF should NOT be blocked"
    assert len(result["warnings"]) > 0
    
    print("\n✅ TEST PASSED: Scenario 5 (WARNING - Not Decision Ready)")


def test_scenario_6_lh_technical_pass():
    """
    SCENARIO 6: LH Technical Report - PASS
    """
    print("\n" + "=" * 70)
    print("TEST SCENARIO 6: LH Technical Report - PASS")
    print("=" * 70)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <section class="executive-summary">
            <h2>기술 검토 요약</h2>
            <p class="narrative">본 검토는 LH 기술 심사 기준에 따라 수행되었습니다.</p>
            <p class="narrative">건축 규모 및 주차 계획이 타당합니다.</p>
            <p class="narrative">인센티브 적용이 가능합니다.</p>
            <p class="narrative">법적 제약사항이 확인되었습니다.</p>
            <p class="narrative">LH 심사 결과가 반영되었습니다.</p>
            <p class="narrative">종합 의견을 제시합니다.</p>
        </section>
        
        <section class="module-section" data-module="M3">
            <h3>M3: LH 선호 주택유형</h3>
        </section>
        
        <section class="module-section" data-module="M4">
            <h3>M4: 건축 규모 결정</h3>
        </section>
        
        <section class="module-section" data-module="M6">
            <h3>M6: LH 심사</h3>
            <p>심사 결과: 조건부 승인</p>
        </section>
        
        <section class="recommendation">
            <p class="judgment">기술적으로 <strong>승인</strong> 가능합니다.</p>
        </section>
    </body>
    </html>
    """
    
    modules_data = {
        "M3": {"recommended_type": "청년형", "score": 85},
        "M4": {"household_count": 26},
        "M6": {"decision": "조건부 승인", "total_score": 75}
    }
    
    result = FinalReportQAValidator.validate(
        report_type="lh_technical",
        html_content=html_content,
        modules_data=modules_data
    )
    
    log_qa_result(result)
    
    # Assertions
    assert result["status"] == "PASS", f"Expected PASS, got {result['status']}"
    assert not should_block_pdf_generation(result)
    
    print("\n✅ TEST PASSED: Scenario 6 (LH Technical - PASS)")


def test_scenario_7_financial_feasibility_fail():
    """
    SCENARIO 7: Financial Feasibility Report - FAIL (Negative NPV)
    """
    print("\n" + "=" * 70)
    print("TEST SCENARIO 7: Financial Feasibility - WARNING (Negative NPV)")
    print("=" * 70)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <section class="executive-summary">
            <h2>재무 타당성 분석 요약</h2>
            <p class="narrative">재무 분석을 수행했습니다.</p>
            <p class="narrative">비용 구조를 검토했습니다.</p>
            <p class="narrative">수익성 지표를 산출했습니다.</p>
            <p class="narrative">리스크를 평가했습니다.</p>
        </section>
        
        <section class="module-section" data-module="M5">
            <h3>M5: 사업성 분석</h3>
            <p>NPV: -200,000,000원</p>
            <p>IRR: -2.5%</p>
        </section>
        
        <section class="recommendation">
            <p class="judgment">재무적으로 <strong>부적합</strong>합니다.</p>
        </section>
    </body>
    </html>
    """
    
    modules_data = {
        "M2": {"land_value": 5000000000},
        "M5": {"is_profitable": False, "npv": -200000000, "irr": -2.5}
    }
    
    result = FinalReportQAValidator.validate(
        report_type="financial_feasibility",
        html_content=html_content,
        modules_data=modules_data
    )
    
    log_qa_result(result)
    
    # Assertions
    assert result["status"] == "WARNING", f"Expected WARNING, got {result['status']}"
    assert not should_block_pdf_generation(result), "PDF should NOT be blocked for WARNING"
    
    print("\n✅ TEST PASSED: Scenario 7 (Financial Feasibility - WARNING)")


# ========== RUN ALL TESTS ==========

if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# PROMPT 4: Final Report QA Validator - Test Suite")
    print("#" * 70)
    
    try:
        test_scenario_1_pass()
        test_scenario_2_fail_missing_executive_summary()
        test_scenario_3_fail_no_judgment()
        test_scenario_4_warning_insufficient_narrative()
        test_scenario_5_warning_not_decision_ready()
        test_scenario_6_lh_technical_pass()
        test_scenario_7_financial_feasibility_fail()
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED - PROMPT 4 QA Validator is working correctly!")
        print("=" * 70)
        print("\n✅ PROMPT 4 EXIT CRITERIA:")
        print("  [✓] QA result has PASS / WARNING / FAIL status")
        print("  [✓] FAIL status blocks PDF generation")
        print("  [✓] Narrative insufficiency triggers WARNING or FAIL")
        print("  [✓] Can test independently without Assembler")
        print("\n🚀 Ready to proceed to PROMPT 5 (Narrative Generator)")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        raise
