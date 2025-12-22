"""
Phase 3.10 Final Lock: KPI Pipeline Test
Tests the new KPI extraction pipeline with hard-fail enforcement
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.final_report_assembly.kpi_extractor import KPIExtractor, validate_mandatory_kpi, FinalReportAssemblyError
from app.services.final_report_assembly.report_type_configs import MANDATORY_KPI

def test_module_root_enforcement():
    """Test 1: Module root must be section[data-module]"""
    print("\n" + "=" * 80)
    print("TEST 1: Module Root Enforcement")
    print("=" * 80)
    
    # Case 1: Valid module root
    valid_html = '''
    <section data-module="M2" data-land-value-total="5600000000">
        <h2>M2 Module</h2>
    </section>
    '''
    
    try:
        root = KPIExtractor.get_module_root(valid_html, "M2")
        print("✅ Valid module root found")
    except FinalReportAssemblyError as e:
        print(f"❌ Failed: {e}")
    
    # Case 2: No module root (should FAIL)
    invalid_html = '''
    <div class="module">
        <h2>M2 Module</h2>
    </div>
    '''
    
    try:
        root = KPIExtractor.get_module_root(invalid_html, "M2")
        print("❌ Should have failed but didn't")
    except FinalReportAssemblyError as e:
        print(f"✅ Correctly blocked: {e}")

def test_data_attribute_extraction():
    """Test 2: data-* attributes must exist"""
    print("\n" + "=" * 80)
    print("TEST 2: Data Attribute Extraction")
    print("=" * 80)
    
    html = '''
    <section data-module="M2" 
             data-land-value-total="5600000000"
             data-land-value-per-pyeong="5500000"
             data-land-area="0">
        <h2>M2 Module</h2>
    </section>
    '''
    
    try:
        root = KPIExtractor.get_module_root(html, "M2")
        raw = KPIExtractor.extract_raw_kpi_from_root(root)
        
        expected_keys = ['module', 'land_value_total', 'land_value_per_pyeong', 'land_area']
        actual_keys = list(raw.keys())
        
        print(f"Expected: {expected_keys}")
        print(f"Actual: {actual_keys}")
        
        if set(expected_keys) == set(actual_keys):
            print("✅ All data-* attributes extracted")
        else:
            print(f"❌ Missing or extra keys")
            
    except Exception as e:
        print(f"❌ Failed: {e}")

def test_m3_alias_rule():
    """Test 3: M3 alias (total_score ← type_score) ONLY"""
    print("\n" + "=" * 80)
    print("TEST 3: M3 Alias Rule")
    print("=" * 80)
    
    # Case 1: total_score exists
    raw1 = {"total_score": "85"}
    result1 = KPIExtractor.apply_alias_rules("M3", raw1)
    print(f"Case 1 (has total_score): {result1}")
    
    # Case 2: total_score missing, type_score exists
    raw2 = {"type_score": "82"}
    result2 = KPIExtractor.apply_alias_rules("M3", raw2)
    print(f"Case 2 (fallback to type_score): {result2}")
    
    if "total_score" in result2 and result2["total_score"] == "82":
        print("✅ M3 alias correctly applied")
    else:
        print("❌ M3 alias failed")

def test_m4_alias_rule():
    """Test 4: M4 alias (total_units ← unit_count) ONLY"""
    print("\n" + "=" * 80)
    print("TEST 4: M4 Alias Rule")
    print("=" * 80)
    
    # Case 1: total_units missing, unit_count exists
    raw = {"unit_count": "250"}
    result = KPIExtractor.apply_alias_rules("M4", raw)
    print(f"Result: {result}")
    
    if "total_units" in result and result["total_units"] == "250":
        print("✅ M4 alias correctly applied")
    else:
        print("❌ M4 alias failed")

def test_mandatory_kpi_validation():
    """Test 5: Mandatory KPI missing → FAIL"""
    print("\n" + "=" * 80)
    print("TEST 5: Mandatory KPI Validation")
    print("=" * 80)
    
    # Case 1: All mandatory KPI present
    modules_data_complete = {
        "M2": {"land_value_total": 5600000000},
        "M5": {"npv": 123456789},
        "M6": {"decision": "추진 가능"}
    }
    
    missing1 = validate_mandatory_kpi("landowner_summary", modules_data_complete, MANDATORY_KPI)
    if not missing1:
        print("✅ Case 1: All mandatory KPI present - PASS")
    else:
        print(f"❌ Case 1: Should PASS but found missing: {missing1}")
    
    # Case 2: Missing M2.land_value_total
    modules_data_incomplete = {
        "M2": {"land_value_total": None},  # Missing!
        "M5": {"npv": 123456789},
        "M6": {"decision": "추진 가능"}
    }
    
    missing2 = validate_mandatory_kpi("landowner_summary", modules_data_incomplete, MANDATORY_KPI)
    if "M2.land_value_total" in missing2:
        print(f"✅ Case 2: Correctly detected missing: {missing2}")
    else:
        print(f"❌ Case 2: Should detect M2.land_value_total missing")

def test_complete_pipeline():
    """Test 6: Complete KPI extraction pipeline"""
    print("\n" + "=" * 80)
    print("TEST 6: Complete KPI Extraction Pipeline")
    print("=" * 80)
    
    html = '''
    <section data-module="M5" 
             data-npv="123456789"
             data-irr="0.12"
             data-is-profitable="true">
        <h2>M5 Module</h2>
    </section>
    '''
    
    required_keys = ["npv", "irr"]
    
    try:
        result = KPIExtractor.extract_module_kpi(html, "M5", required_keys)
        
        print(f"Module ID: {result.get('_module_id')}")
        print(f"Required Keys: {result.get('_required_keys')}")
        print(f"Extracted Keys: {result.get('_extracted_keys')}")
        print(f"Normalized OK: {result.get('_normalized_ok')}")
        print(f"NPV: {result.get('npv')}")
        print(f"IRR: {result.get('irr')}")
        
        if result.get('_normalized_ok') and result.get('npv') == 123456789.0:
            print("✅ Complete pipeline working")
        else:
            print("❌ Pipeline failed")
            
    except Exception as e:
        print(f"❌ Failed: {e}")

def main():
    print("\n" + "=" * 80)
    print("🧪 Phase 3.10 Final Lock: KPI Pipeline Tests")
    print("=" * 80)
    
    test_module_root_enforcement()
    test_data_attribute_extraction()
    test_m3_alias_rule()
    test_m4_alias_rule()
    test_mandatory_kpi_validation()
    test_complete_pipeline()
    
    print("\n" + "=" * 80)
    print("✅ All Tests Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
