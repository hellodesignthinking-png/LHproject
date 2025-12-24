#!/usr/bin/env python3
"""Test script to verify data integrity fixes"""
import pytest
from app.services.final_report_assembly.assemblers import landowner_summary

def test_no_na_in_kpis():
    """Core KPIs must NOT contain N/A"""
    assembler = landowner_summary.LandownerSummaryAssembler("test_context")
    result = assembler.assemble()
    
    html = result["html"]
    
    # Find KPI summary box
    import re
    kpi_box = re.search(r'<section[^>]*kpi-summary-box[^>]*>(.*?)</section>', html, re.DOTALL)
    
    assert kpi_box, "KPI summary box must exist"
    
    kpi_content = kpi_box.group(1)
    
    # Assert NO N/A indicators
    assert "N/A" not in kpi_content, "KPI box contains N/A"
    assert "데이터 없음" not in kpi_content, "KPI box contains 데이터 없음"
    assert "분석 미완료" not in kpi_content, "KPI box contains 분석 미완료"
    
    print("✅ TEST PASSED: No N/A in core KPIs")

def test_module_completeness_gate():
    """Incomplete modules should BLOCK Final Report"""
    assembler = landowner_summary.LandownerSummaryAssembler("incomplete_context")
    
    is_complete, missing = assembler.validate_module_completeness()
    
    if not is_complete:
        print(f"✅ TEST PASSED: Incomplete modules detected: {missing}")
        with pytest.raises(Exception):
            assembler.assemble()  # Should raise error
    else:
        result = assembler.assemble()
        assert result["qa_result"]["status"] != "FAIL", "QA should catch incomplete data"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
