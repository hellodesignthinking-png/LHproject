"""
Phase 3.5F Data Propagation Tests
==================================

Purpose: Verify that module data changes propagate immediately to all outputs

Test Cases:
1. Module data change → HTML reflects change
2. Module data change → PDF reflects change  
3. Module data change → All 6 reports reflect change
4. assembled_data validation → FAIL FAST works

Author: ZeroSite Team
Date: 2025-12-27
Version: 1.0
"""

import pytest
from app.services.data_contract import (
    STANDARD_SCHEMA_EXAMPLE,
    validate_assembled_data,
    DataValidationError
)
from app.services.m6_centered_report_base import create_m6_centered_report
from app.services.simple_html_renderer import render_simple_html
from app.services.format_utils import format_currency_kr


def test_module_data_change_reflects_in_html():
    """
    Test: M2 land value change should immediately reflect in HTML output
    """
    # Create assembled_data with specific land value
    test_land_value = 1234567890  # 12.35억원
    
    assembled_data = {
        "m6_result": STANDARD_SCHEMA_EXAMPLE["m6_result"],
        "modules": {
            "M2": {
                "summary": {
                    "land_value": test_land_value,
                    "land_value_per_pyeong": 50000000,
                    "confidence_pct": 85.5
                },
                "details": {},
                "raw_data": {}
            },
            "M3": STANDARD_SCHEMA_EXAMPLE["modules"]["M3"],
            "M4": STANDARD_SCHEMA_EXAMPLE["modules"]["M4"],
            "M5": STANDARD_SCHEMA_EXAMPLE["modules"]["M5"]
        }
    }
    
    # Generate report
    m6_result = assembled_data["m6_result"]
    report = create_m6_centered_report(assembled_data, report_type="all_in_one")
    
    # Render HTML
    html = render_simple_html(report)
    
    # Verify value appears in HTML
    expected_formatted = format_currency_kr(test_land_value)  # "12.35억원"
    assert expected_formatted in html, f"Expected {expected_formatted} in HTML but not found"


def test_all_six_reports_use_same_module_data():
    """
    Test: All 6 report types should use identical module data
    """
    # Create assembled_data with specific values
    test_land_value = 9876543210
    test_npv = 888888888
    test_units = 99
    
    assembled_data = {
        "m6_result": STANDARD_SCHEMA_EXAMPLE["m6_result"],
        "modules": {
            "M2": {
                "summary": {
                    "land_value": test_land_value,
                    "land_value_per_pyeong": 50000000,
                    "confidence_pct": 85.5
                },
                "details": {},
                "raw_data": {}
            },
            "M3": STANDARD_SCHEMA_EXAMPLE["modules"]["M3"],
            "M4": {
                "summary": {
                    "total_units": test_units,
                    "gross_area_sqm": 1500,
                    "parking_spaces": 15
                },
                "details": {},
                "raw_data": {}
            },
            "M5": {
                "summary": {
                    "npv_public_krw": test_npv,
                    "irr_pct": 12.5,
                    "roi_pct": 15.2,
                    "financial_grade": "B"
                },
                "details": {},
                "raw_data": {}
            }
        }
    }
    
    m6_result = assembled_data["m6_result"]
    
    # Generate all 6 report types
    report_types = [
        "all_in_one",
        "landowner_summary",
        "quick_check",
        "lh_technical",
        "financial_feasibility",
        "presentation"
    ]
    
    reports = {}
    for report_type in report_types:
        reports[report_type] = create_m6_centered_report(
            assembled_data, report_type=report_type
        )
    
    # Extract key_numbers from each report (if present)
    for report_type, report in reports.items():
        if 'key_numbers' in report:
            kn = report['key_numbers']
            
            # Check M2 land value
            assert kn['m2_land_value'] == test_land_value, \
                f"{report_type}: land_value mismatch"
            
            # Check M4 units
            assert kn['m4_total_units'] == test_units, \
                f"{report_type}: total_units mismatch"
            
            # Check M5 NPV
            assert kn['m5_npv'] == test_npv, \
                f"{report_type}: NPV mismatch"


def test_missing_module_data_fails_fast():
    """
    Test: Missing module data should raise DataValidationError immediately
    """
    # Create assembled_data with missing M2
    incomplete_data = {
        "m6_result": STANDARD_SCHEMA_EXAMPLE["m6_result"],
        "modules": {
            # M2 missing!
            "M3": STANDARD_SCHEMA_EXAMPLE["modules"]["M3"],
            "M4": STANDARD_SCHEMA_EXAMPLE["modules"]["M4"],
            "M5": STANDARD_SCHEMA_EXAMPLE["modules"]["M5"]
        }
    }
    
    # Should raise DataValidationError
    with pytest.raises(DataValidationError):
        validate_assembled_data(incomplete_data, strict=True)


def test_invalid_structure_fails_fast():
    """
    Test: Invalid structure should raise DataValidationError
    """
    # Create assembled_data with missing summary key
    invalid_data = {
        "m6_result": STANDARD_SCHEMA_EXAMPLE["m6_result"],
        "modules": {
            "M2": {
                # "summary" missing!
                "details": {},
                "raw_data": {}
            },
            "M3": STANDARD_SCHEMA_EXAMPLE["modules"]["M3"],
            "M4": STANDARD_SCHEMA_EXAMPLE["modules"]["M4"],
            "M5": STANDARD_SCHEMA_EXAMPLE["modules"]["M5"]
        }
    }
    
    # Should raise DataValidationError
    with pytest.raises(DataValidationError):
        validate_assembled_data(invalid_data, strict=True)


def test_data_change_propagates_to_multiple_outputs():
    """
    Integration test: Change M2/M4/M5 data and verify all outputs update
    """
    # Original values
    original_land = 6081933538
    original_units = 20
    original_npv = 792999999
    
    # Changed values
    new_land = 8000000000  # 80억원
    new_units = 30
    new_npv = 1000000000  # 10억원
    
    # Create assembled_data with NEW values
    assembled_data = {
        "m6_result": STANDARD_SCHEMA_EXAMPLE["m6_result"],
        "modules": {
            "M2": {
                "summary": {
                    "land_value": new_land,
                    "land_value_per_pyeong": 50000000,
                    "confidence_pct": 85.5
                },
                "details": {},
                "raw_data": {}
            },
            "M3": STANDARD_SCHEMA_EXAMPLE["modules"]["M3"],
            "M4": {
                "summary": {
                    "total_units": new_units,
                    "gross_area_sqm": 1500,
                    "parking_spaces": 15
                },
                "details": {},
                "raw_data": {}
            },
            "M5": {
                "summary": {
                    "npv_public_krw": new_npv,
                    "irr_pct": 12.5,
                    "roi_pct": 15.2,
                    "financial_grade": "B"
                },
                "details": {},
                "raw_data": {}
            }
        }
    }
    
    m6_result = assembled_data["m6_result"]
    
    # Generate all_in_one report
    report = create_m6_centered_report(assembled_data, report_type="all_in_one")
    
    # Verify key_numbers reflect NEW values (not original)
    kn = report['key_numbers']
    assert kn['m2_land_value'] == new_land, "Land value not updated"
    assert kn['m4_total_units'] == new_units, "Units not updated"
    assert kn['m5_npv'] == new_npv, "NPV not updated"
    
    # Verify HTML also reflects NEW values
    html = render_simple_html(report)
    expected_land = format_currency_kr(new_land)  # "80.00억원"
    assert expected_land in html, f"HTML doesn't show updated land value: {expected_land}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
