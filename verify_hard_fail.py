#!/usr/bin/env python3
"""
Verify Phase 3.10 Hard-Fail is Working
======================================

This script tests if the hard-fail enforcement blocks
report generation when mandatory KPIs are missing.
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.final_report_assembly.assemblers.landowner_summary import LandownerSummaryAssembler

# Test with EMPTY context (should FAIL)
print("=" * 80)
print("🧪 TESTING HARD-FAIL ENFORCEMENT")
print("=" * 80)
print()

test_context_id = "31e4e31c-a054-470f-814f-bae43fd857d0"
print(f"Testing with context: {test_context_id}")
print("Expected: FAIL with clear error message")
print()

try:
    assembler = LandownerSummaryAssembler(test_context_id)
    result = assembler.assemble()
    
    print("Result:")
    print(f"  Status: {result['qa_result']['status']}")
    
    if result['qa_result']['status'] == 'FAIL':
        print("  ✅ HARD-FAIL WORKING!")
        print(f"  Errors: {result['qa_result']['errors']}")
    else:
        print("  ❌ HARD-FAIL NOT WORKING - Report generated despite missing data")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print()
print("=" * 80)
