#!/usr/bin/env python3
"""Test Quick Check assembler directly"""
import sys
sys.path.insert(0, '.')

from app.services.final_report_assembly.assemblers.quick_check import QuickCheckAssembler

try:
    assembler = QuickCheckAssembler("test-debug-001")
    
    # Mock load_module_html
    def mock_load(module_id):
        if module_id == "M5":
            return '<section data-module="M5" data-npv="3250000000" data-irr="15.8"><p>M5 content</p></section>'
        elif module_id == "M6":
            return '<section data-module="M6" data-decision="적합"><p>M6 content</p></section>'
        else:
            raise ValueError(f"Unexpected module: {module_id}")
    
    assembler.load_module_html = mock_load
    
    print("Testing Quick Check Assembler...")
    result = assembler.assemble()
    
    print(f"Status: {result.get('qa_result', {}).get('status', 'UNKNOWN')}")
    print(f"HTML Length: {len(result.get('html', ''))} bytes")
    print(f"Blocking: {result.get('qa_result', {}).get('blocking', False)}")
    
    if result.get('qa_result', {}).get('status') == 'FAIL':
        print(f"Errors: {result.get('qa_result', {}).get('errors', [])}")
        print(f"Reason: {result.get('qa_result', {}).get('reason', 'Unknown')}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
