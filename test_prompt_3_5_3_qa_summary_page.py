"""
Test Suite for PROMPT 3.5-3: QA Summary Page Auto-Insert
=========================================================

Tests:
1. QA Summary page generation from QA result
2. QA Summary HTML contains all required elements
3. QA Summary is inserted before </body> tag
4. Landowner assembler includes QA Summary in output

Expected Elements:
- QA Status (PASS/WARNING/FAIL with color coding)
- Validation checks table
- Warnings list
- Metadata (report type, verification time, QA version)
- Disclaimer text
"""

import sys
from unittest.mock import Mock, patch
from datetime import datetime

# Mock storage
mock_storage = Mock()
mock_context = {
    "canonical_summary": {
        "M2": {"land_value": 1000000},
        "M5": {"npv": 100000, "is_profitable": True},
        "M6": {"decision": "승인"}
    },
    "analyzed_at": datetime.now().isoformat()
}
mock_storage.get_frozen_context = Mock(return_value=mock_context)
sys.modules['app.services.context_storage'] = Mock(context_storage=mock_storage)

# Import after mocking
from app.services.final_report_assembly.qa_validator import (
    FinalReportQAValidator,
    generate_qa_summary_page
)
from app.services.final_report_assembly.assemblers import LandownerSummaryAssembler


def test_qa_summary_page():
    """Test PROMPT 3.5-3 implementation"""
    
    print("\n" + "="*80)
    print("TEST SUITE: PROMPT 3.5-3 - QA Summary Page Auto-Insert")
    print("="*80 + "\n")
    
    # Test 1: Generate QA summary page from QA result
    print("TEST 1: Generate QA Summary HTML from QA result")
    print("-" * 60)
    
    mock_qa_result = {
        "status": "PASS",
        "report_type": "landowner_summary",
        "checks": {
            "executive_summary_exists": True,
            "narrative_sufficient": True,
            "judgment_statement": True,
            "decision_ready": True
        },
        "warnings": [],
        "errors": [],
        "blocking_issues": []
    }
    
    qa_summary_html = generate_qa_summary_page(mock_qa_result)
    
    assert len(qa_summary_html) > 500, "QA summary HTML too short"
    assert "Quality Assurance Summary" in qa_summary_html, "Missing title"
    assert "PASS" in qa_summary_html, "Missing status"
    assert "landowner_summary" in qa_summary_html, "Missing report type"
    
    print(f"✅ QA Summary page generated ({len(qa_summary_html):,} chars)")
    print()
    
    # Test 2: Check required elements in QA summary
    print("TEST 2: Verify QA Summary contains all required elements")
    print("-" * 60)
    
    required_elements = [
        ("Status Section", "qa-status"),
        ("Validation Checks", "qa-details"),
        ("Warnings Section", "qa-warnings"),
        ("Metadata Section", "qa-metadata"),
        ("Disclaimer", "qa-disclaimer"),
        ("Report Type", "Report Type:"),
        ("Verification Time", "Verification Time:"),
        ("QA Version", "QA Version:")
    ]
    
    for name, element in required_elements:
        assert element in qa_summary_html, f"Missing element: {name} ({element})"
        print(f"✅ {name}: Found")
    
    print()
    
    # Test 3: Check color coding for different statuses
    print("TEST 3: Verify status-specific color coding")
    print("-" * 60)
    
    statuses = ["PASS", "WARNING", "FAIL"]
    expected_colors = {
        "PASS": "#28a745",
        "WARNING": "#ffc107",
        "FAIL": "#dc3545"
    }
    
    for status in statuses:
        test_qa_result = {
            "status": status,
            "report_type": "test",
            "checks": {},
            "warnings": [],
            "errors": [],
            "blocking_issues": []
        }
        
        summary = generate_qa_summary_page(test_qa_result)
        expected_color = expected_colors[status]
        
        assert expected_color in summary, f"Missing color for {status}: {expected_color}"
        print(f"✅ {status}: Color {expected_color} present")
    
    print()
    
    # Test 4: Test Landowner assembler includes QA summary
    print("TEST 4: Verify Landowner assembler includes QA Summary")
    print("-" * 60)
    
    context_id = "test_qa_summary_123"
    assembler = LandownerSummaryAssembler(context_id)
    
    result = assembler.assemble()
    html_output = result["html"]
    qa_result = result.get("qa_result")
    
    assert qa_result is not None, "QA result not returned"
    assert "qa-summary-page" in html_output, "QA Summary page not inserted in HTML"
    assert "Quality Assurance Summary" in html_output, "QA Summary title missing"
    assert qa_result["status"] in html_output, "QA status not in HTML"
    
    print(f"✅ Landowner assembler includes QA Summary")
    print(f"   HTML length: {len(html_output):,} chars")
    print(f"   QA Status: {qa_result['status']}")
    print(f"   QA Summary found: Yes")
    print()
    
    # Test 5: Check QA summary position (should be before </body>)
    print("TEST 5: Verify QA Summary position (before </body>)")
    print("-" * 60)
    
    qa_summary_pos = html_output.find("qa-summary-page")
    body_close_pos = html_output.find("</body>")
    
    assert qa_summary_pos > 0, "QA Summary not found in HTML"
    assert body_close_pos > 0, "</body> tag not found"
    assert qa_summary_pos < body_close_pos, "QA Summary not positioned before </body>"
    
    print(f"✅ QA Summary correctly positioned:")
    print(f"   QA Summary position: {qa_summary_pos}")
    print(f"   </body> position: {body_close_pos}")
    print(f"   QA Summary is before </body>: True")
    print()
    
    # Summary
    print("="*80)
    print("PROMPT 3.5-3 VALIDATION COMPLETE")
    print("="*80)
    print()
    print("✅ All 5 test scenarios passed:")
    print("   1. QA Summary page generates from QA result")
    print("   2. All required elements present (status, checks, warnings, metadata)")
    print("   3. Status-specific color coding works (PASS=green, WARNING=yellow, FAIL=red)")
    print("   4. Landowner assembler includes QA Summary")
    print("   5. QA Summary positioned correctly (before </body>)")
    print()
    print("📋 Exit Criteria Met:")
    print("   ✅ QA Summary auto-inserted at end of Final Reports")
    print("   ✅ Shows QA status (PASS/WARNING/FAIL)")
    print("   ✅ Lists all validation checks with results")
    print("   ✅ Includes warnings and metadata")
    print("   ✅ Provides transparency for automated QA")
    print()
    print("🎯 READY FOR PRODUCTION")
    print()


if __name__ == "__main__":
    test_qa_summary_page()
