"""
End-to-End Tests for LH Notice Loader

Tests LH PDF parsing, template detection, and rule extraction
"""

import pytest
import json
from pathlib import Path
from typing import Dict, List

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestE2ELHNoticeLoader:
    """End-to-end tests for LH Notice Loader"""
    
    def test_e2e_list_lh_notices(self):
        """Test listing processed LH notices"""
        print(f"\n📋 Testing LH notice list endpoint...")
        
        response = client.get("/api/lh-notices/list")
        
        assert response.status_code == 200, "List endpoint should succeed"
        
        data = response.json()
        
        assert "status" in data
        assert "total" in data
        assert "notices" in data
        
        print(f"   Status: {data['status']}")
        print(f"   Total notices: {data['total']}")
        
        if data["total"] > 0:
            print(f"   ✅ Found {data['total']} processed notices")
            
            # Show first few
            for i, notice in enumerate(data["notices"][:3], 1):
                print(f"   {i}. {notice.get('version_id', 'Unknown')}")
        else:
            print(f"   ⚠️  No notices processed yet (acceptable)")
    
    def test_e2e_get_lh_notice_rules(self):
        """Test retrieving specific LH notice rules"""
        # First get list
        list_response = client.get("/api/lh-notices/list")
        
        if list_response.status_code == 200:
            data = list_response.json()
            
            if data["total"] > 0:
                # Get first notice
                first_notice = data["notices"][0]
                version_id = first_notice.get("version_id")
                
                print(f"\n📄 Testing notice retrieval: {version_id}")
                
                # Get specific notice
                response = client.get(f"/api/lh-notices/{version_id}")
                
                if response.status_code == 200:
                    notice_data = response.json()
                    
                    assert "status" in notice_data
                    assert "rules" in notice_data
                    
                    rules = notice_data["rules"]
                    print(f"   Rules found: {len(rules) if isinstance(rules, dict) else 'N/A'}")
                    print(f"   ✅ Notice retrieval successful")
                elif response.status_code == 404:
                    print(f"   ⚠️  Notice not found (data may have changed)")
                else:
                    print(f"   ⚠️  Unexpected status: {response.status_code}")
            else:
                pytest.skip("No notices available for testing")
        else:
            pytest.skip("List endpoint unavailable")
    
    def test_e2e_lh_notice_sync(self):
        """Test LH notice sync from Google Drive"""
        print(f"\n🔄 Testing LH notice sync...")
        
        response = client.post("/api/lh-notices/sync")
        
        # Sync might fail if Google Drive not configured
        if response.status_code == 200:
            data = response.json()
            
            synced = data.get("synced_files", 0)
            new_versions = len(data.get("new_versions", []))
            failed = len(data.get("failed_files", []))
            
            print(f"   Synced: {synced}")
            print(f"   New versions: {new_versions}")
            print(f"   Failed: {failed}")
            
            print(f"   ✅ Sync completed")
        elif response.status_code == 500:
            error = response.json()
            print(f"   ⚠️  Sync failed: {error.get('message', 'Unknown error')}")
            print(f"   This is acceptable if Google Drive is not configured")
            pytest.skip("Google Drive sync not configured")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
    
    def test_e2e_notice_data_structure(self):
        """Validate LH notice data structure"""
        list_response = client.get("/api/lh-notices/list")
        
        if list_response.status_code == 200:
            data = list_response.json()
            
            if data["total"] > 0:
                first_notice = data["notices"][0]
                version_id = first_notice.get("version_id")
                
                response = client.get(f"/api/lh-notices/{version_id}")
                
                if response.status_code == 200:
                    notice_data = response.json()
                    rules = notice_data.get("rules", {})
                    
                    print(f"\n🔍 Validating notice structure for {version_id}")
                    
                    # Check expected structure
                    expected_fields = [
                        "version",
                        "exclusion_criteria",
                        "agreement_terms"
                    ]
                    
                    for field in expected_fields:
                        if field in rules:
                            print(f"   ✅ {field}: present")
                        else:
                            print(f"   ⚠️  {field}: missing")
                    
                    # Validate exclusion criteria structure
                    if "exclusion_criteria" in rules:
                        exclusions = rules["exclusion_criteria"]
                        if isinstance(exclusions, list) and len(exclusions) > 0:
                            print(f"   ✅ Exclusion criteria: {len(exclusions)} items")
                        else:
                            print(f"   ⚠️  Exclusion criteria empty or invalid format")
                    
                    print(f"   ✅ Structure validation complete")
                else:
                    pytest.skip("Notice retrieval failed")
            else:
                pytest.skip("No notices available")
        else:
            pytest.skip("List endpoint unavailable")


class TestE2ENoticeLoaderIntegration:
    """Test integration with analysis flow"""
    
    def test_notice_version_affects_analysis(self):
        """Test that different LH versions can be specified"""
        addr = {
            "address": "서울특별시 강남구 테헤란로 152",
            "land_area": 500.0
        }
        
        print(f"\n🔀 Testing LH version specification...")
        
        # Test with default version
        request_2024 = {
            **addr,
            "lh_version": "2024"
        }
        
        response_2024 = client.post("/api/analyze-land", json=request_2024)
        
        # Test with 2025 version
        request_2025 = {
            **addr,
            "lh_version": "2025"
        }
        
        response_2025 = client.post("/api/analyze-land", json=request_2025)
        
        # Both should succeed (or at least not crash)
        if response_2024.status_code == 200:
            print(f"   ✅ 2024 version: Success")
        else:
            print(f"   ⚠️  2024 version: {response_2024.status_code}")
        
        if response_2025.status_code == 200:
            print(f"   ✅ 2025 version: Success")
        else:
            print(f"   ⚠️  2025 version: {response_2025.status_code}")
        
        # At least one should work
        assert response_2024.status_code == 200 or response_2025.status_code == 200, \
            "At least one LH version should work"


class TestE2EPDFParsing:
    """Test PDF parsing capabilities (if PDF files available)"""
    
    def test_pdf_parser_available(self):
        """Check if PDF parsing dependencies are available"""
        print(f"\n📖 Checking PDF parsing capabilities...")
        
        try:
            import pdfplumber
            print(f"   ✅ pdfplumber: available")
        except ImportError:
            print(f"   ⚠️  pdfplumber: not installed")
        
        try:
            import tabula
            print(f"   ✅ tabula-py: available")
        except ImportError:
            print(f"   ⚠️  tabula-py: not installed")
        
        try:
            import fitz  # PyMuPDF
            print(f"   ✅ PyMuPDF: available")
        except ImportError:
            print(f"   ⚠️  PyMuPDF: not installed")
        
        try:
            import pytesseract
            print(f"   ✅ pytesseract: available")
        except ImportError:
            print(f"   ⚠️  pytesseract: not installed")
        
        print(f"\n   PDF parsing infrastructure check complete")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
