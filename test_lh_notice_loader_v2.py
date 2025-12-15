"""
Test file for LH Notice Loader v2.0
Tests Google Drive integration, PDF parsing, and auto-rule generation
"""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.lh_notice_loader_v2 import LHNoticeLoaderV2, PDF_AVAILABLE, GDRIVE_AVAILABLE


def print_separator(title=""):
    """Print a visual separator"""
    print("\n" + "="*70)
    if title:
        print(f" {title}")
        print("="*70)
    print()


async def test_filename_parsing():
    """Test 1: Filename Pattern Recognition"""
    print_separator("Test 1: Filename Pattern Recognition")
    
    loader = LHNoticeLoaderV2()
    
    test_cases = [
        "서울25-8차민간신축매입약정방식공고문.pdf",
        "경기24-3차_공고문_최종.pdf",
        "부산_2025_12차_공고.pdf",
        "LH_서울_2025년_3차_공고.pdf",
        "2025-서울-3차.pdf",
        "인천_25-5차_공고.pdf",
        "InvalidFilename.pdf"  # Should fail
    ]
    
    success_count = 0
    for filename in test_cases:
        result = loader.parse_filename(filename)
        if result:
            success_count += 1
            print(f"✅ {filename}")
            print(f"   Region: {result['region']}, Year: {result['year']}, Round: {result['round']}")
            print(f"   Version ID: {result['version_id']}")
        else:
            print(f"❌ {filename} - Could not parse")
        print()
    
    print(f"📊 Result: {success_count}/{len(test_cases)} filenames parsed successfully")
    return success_count > 0


async def test_pdf_availability():
    """Test 2: PDF Parsing Library Availability"""
    print_separator("Test 2: PDF Parsing Library Availability")
    
    if PDF_AVAILABLE:
        print("✅ PDF parsing libraries available (PyPDF2, pdfplumber)")
        
        try:
            import PyPDF2
            print(f"   PyPDF2 version: {PyPDF2.__version__}")
        except:
            pass
        
        try:
            import pdfplumber
            print(f"   pdfplumber available: Yes")
        except:
            pass
        
        return True
    else:
        print("❌ PDF parsing libraries NOT available")
        print("   Install with: pip install PyPDF2 pdfplumber")
        return False


async def test_gdrive_availability():
    """Test 3: Google Drive API Availability"""
    print_separator("Test 3: Google Drive API Availability")
    
    if GDRIVE_AVAILABLE:
        print("✅ Google Drive API libraries available")
        
        try:
            from google.oauth2 import service_account
            print("   google-auth: Available")
        except:
            pass
        
        try:
            from googleapiclient.discovery import build
            print("   google-api-python-client: Available")
        except:
            pass
        
        return True
    else:
        print("❌ Google Drive API libraries NOT available")
        print("   Install with: pip install google-api-python-client google-auth")
        return False


async def test_directory_structure():
    """Test 4: Directory Structure Creation"""
    print_separator("Test 4: Directory Structure Creation")
    
    loader = LHNoticeLoaderV2()
    
    directories = [
        loader.storage_dir,
        loader.auto_rules_dir
    ]
    
    all_exist = True
    for directory in directories:
        if directory.exists():
            print(f"✅ {directory} exists")
        else:
            print(f"❌ {directory} does NOT exist")
            all_exist = False
    
    return all_exist


async def test_rule_extraction():
    """Test 5: Rule Extraction Logic"""
    print_separator("Test 5: Rule Extraction Logic")
    
    loader = LHNoticeLoaderV2()
    
    # Mock PDF text content
    mock_text = """
    LH 신축매입임대 공고문
    
    1. 입지조건
    - 역세권 500m 이내 위치 필수
    - 초등학교 300m 이내 우선
    
    2. 건축기준
    - 층수 15층 이하
    - 세대수 100세대 이상
    
    3. 신청자격
    - 소득 70% 이하 가구
    - 자산기준 충족
    
    4. 보증금
    - 보증금 5,000만원 이하
    
    5. 배점기준
    - 입지 30점
    - 건축 20점
    - 가격 25점
    """
    
    file_info = {
        "region": "서울",
        "year": 2025,
        "round": "3차",
        "version_id": "서울_2025_3차",
        "filename": "test.pdf"
    }
    
    rules = loader._extract_rules_from_text(mock_text, file_info)
    
    print("Extracted Rules:")
    print(f"   Location rules: {rules.get('location', {})}")
    print(f"   Building rules: {rules.get('building', {})}")
    print(f"   Eligibility rules: {rules.get('eligibility', {})}")
    print(f"   Pricing rules: {rules.get('pricing', {})}")
    print(f"   Scoring rules: {rules.get('scoring', {})}")
    print(f"   Requirements: {len(rules.get('requirements', []))} items")
    
    # Validate extracted rules
    validation = {
        "subway_distance": rules.get('location', {}).get('subway_distance') == 500,
        "school_distance": rules.get('location', {}).get('school_distance') == 300,
        "max_floors": rules.get('building', {}).get('max_floors') == 15,
        "min_units": rules.get('building', {}).get('min_units') == 100,
        "income_limit": rules.get('eligibility', {}).get('income_limit') == 70
    }
    
    success_count = sum(validation.values())
    print(f"\n📊 Validation: {success_count}/{len(validation)} rules correctly extracted")
    
    for key, valid in validation.items():
        status = "✅" if valid else "❌"
        print(f"   {status} {key}")
    
    return success_count >= 3  # At least 3 out of 5 should be correct


async def test_gdrive_sync():
    """Test 6: Google Drive Sync (if credentials available)"""
    print_separator("Test 6: Google Drive Sync")
    
    loader = LHNoticeLoaderV2()
    
    print(f"Drive Folder ID: {loader.drive_folder_id}")
    print(f"Credentials Path: {loader.credentials_path}")
    
    import os
    if not os.path.exists(loader.credentials_path):
        print(f"\n⚠️  Credentials file not found at: {loader.credentials_path}")
        print("   Skipping Google Drive sync test")
        print("   To enable: Set GOOGLE_DRIVE_CREDENTIALS_PATH environment variable")
        return None
    
    print("\n🔄 Attempting to sync from Google Drive...")
    
    try:
        result = await loader.sync_from_drive(force_resync=False)
        
        print(f"\n📊 Sync Result:")
        print(f"   Status: {result['status']}")
        print(f"   Total files: {result.get('total_files', 0)}")
        print(f"   Synced files: {result['synced_files']}")
        print(f"   New versions: {result['new_versions']}")
        
        if result['failed_files']:
            print(f"   Failed files: {len(result['failed_files'])}")
            for failed in result['failed_files'][:3]:  # Show first 3 failures
                print(f"      - {failed['filename']}: {failed['reason']}")
        
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"\n❌ Sync failed with error: {e}")
        return False


async def test_version_management():
    """Test 7: Version Management"""
    print_separator("Test 7: Version Management")
    
    loader = LHNoticeLoaderV2()
    
    # List versions
    versions = await loader.list_versions()
    print(f"📋 Total versions in history: {len(versions)}")
    
    if versions:
        print("\nRecent versions:")
        for v in versions[-5:]:  # Last 5 versions
            print(f"   • {v['version_id']}")
            print(f"     Processed: {v['processed_at']}")
            print(f"     Rules: {v['rules_count']}")
    else:
        print("   No versions processed yet")
    
    # Get latest rules
    latest = await loader.get_latest_rules()
    if latest:
        print(f"\n✅ Latest rules available: {latest['version']}")
        print(f"   Updated: {latest['updated_at']}")
        print(f"   Auto-generated: {latest.get('auto_generated', False)}")
        
        rules = latest.get('rules', {})
        print(f"   Rule categories: {len(rules)}")
        for category in rules.keys():
            print(f"      - {category}")
        
        return True
    else:
        print("\n⚠️  No latest rules available yet")
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n" + "█"*70)
    print("   ZeroSite v7.0 - LH Notice Loader v2.0 Test Suite")
    print("█"*70)
    
    tests = [
        ("Filename Parsing", test_filename_parsing),
        ("PDF Library Availability", test_pdf_availability),
        ("Google Drive API Availability", test_gdrive_availability),
        ("Directory Structure", test_directory_structure),
        ("Rule Extraction Logic", test_rule_extraction),
        ("Google Drive Sync", test_gdrive_sync),
        ("Version Management", test_version_management)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print_separator("Test Summary")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"Total Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"   {status} - {test_name}")
    
    print("\n" + "█"*70)
    if failed == 0:
        print("   🎉 All tests passed!")
    else:
        print(f"   ⚠️  {failed} test(s) failed")
    print("█"*70 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
