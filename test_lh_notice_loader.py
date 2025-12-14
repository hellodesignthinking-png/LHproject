"""LH Notice Loader Test Suite (v7.0)"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.lh_notice_loader import LHNoticeLoader

def test_filename_pattern():
    print("\n" + "="*80)
    print("테스트 1: 파일명 패턴 인식 (v2.0)")
    print("="*80)
    
    loader = LHNoticeLoader()
    
    test_cases = [
        ("서울25-8차민간신축매입약정방식공고문.pdf", True, 2025, 8),
        ("경기24-3차_공고문_최종.pdf", True, 2024, 3),
        ("invalid_filename.pdf", False, None, None),
    ]
    
    passed = 0
    for filename, should_match, exp_year, exp_round in test_cases:
        result = loader.parse_filename(filename)
        
        if should_match:
            if result and result["year"] == exp_year and result["round"] == exp_round:
                print(f"✅ PASS: {filename} → Year: {result['year']}, Round: {result['round']}")
                passed += 1
            else:
                print(f"❌ FAIL: {filename} → Got {result}")
        else:
            if result is None:
                print(f"✅ PASS: {filename} → Correctly rejected")
                passed += 1
            else:
                print(f"❌ FAIL: {filename} → Should be None")
    
    print(f"\n✅ Passed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)

def test_rule_extraction():
    print("\n" + "="*80)
    print("테스트 2: LH 규칙 추출")
    print("="*80)
    
    loader = LHNoticeLoader()
    
    sample_text = """
    청년형
    - 공급기간: 6년
    - 임대료율: 90%
    - 토지면적: 300㎡ ~ 600㎡
    
    고령자형
    - 공급기간: 20년
    - 임대료율: 80%
    - 토지면적: 400㎡ ~ 800㎡
    """
    
    rules = loader._extract_rules_from_text(sample_text)
    
    passed = 0
    if "청년" in rules:
        print(f"✅ 청년형 규칙 추출 성공: {rules['청년']}")
        passed += 1
    else:
        print(f"❌ 청년형 규칙 추출 실패")
    
    if "고령자" in rules:
        print(f"✅ 고령자형 규칙 추출 성공: {rules['고령자']}")
        passed += 1
    else:
        print(f"❌ 고령자형 규칙 추출 실패")
    
    print(f"\n✅ Passed: {passed}/2")
    return passed == 2

def test_json_storage():
    print("\n" + "="*80)
    print("테스트 3: JSON 저장 및 불러오기")
    print("="*80)
    
    loader = LHNoticeLoader()
    
    test_rules = {
        "청년": {"period": "6년", "rent_rate": "90%", "land_area": "300㎡ ~ 600㎡"},
        "고령자": {"period": "20년", "rent_rate": "80%", "land_area": "400㎡ ~ 800㎡"}
    }
    
    version_id = "test_2025_99"
    
    try:
        filepath = loader._save_rules_to_json(test_rules, version_id)
        print(f"✅ 저장 성공: {filepath}")
        
        loaded = loader.get_rules_by_version(version_id)
        if loaded and len(loaded) == 2:
            print(f"✅ 불러오기 성공: {len(loaded)} 규칙")
            return True
        else:
            print(f"❌ 불러오기 실패")
            return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    finally:
        test_dir = Path("data/lh_rules_auto")
        if test_dir.exists():
            for f in test_dir.glob("test_*.json"):
                f.unlink()

def test_processing_history():
    print("\n" + "="*80)
    print("테스트 4: 처리 이력 관리")
    print("="*80)
    
    loader = LHNoticeLoader()
    
    loader._add_processing_history("test_file_1.pdf", "2025_1", success=True)
    loader._add_processing_history("test_file_2.pdf", "2025_2", success=False, error="Parse error")
    
    history = loader._get_processing_history()
    
    if len(history) >= 2:
        print(f"✅ 처리 이력 개수: {len(history)}")
        return True
    else:
        print(f"❌ 처리 이력 부족")
        return False

def test_integration():
    print("\n" + "="*80)
    print("테스트 5: 통합 시나리오")
    print("="*80)
    
    loader = LHNoticeLoader()
    filename = "서울25-10차민간신축매입약정방식공고문.pdf"
    
    # 1. 파일명 파싱
    metadata = loader.parse_filename(filename)
    if not metadata:
        print(f"❌ 파일명 파싱 실패")
        return False
    print(f"✅ 파일명 파싱: Year={metadata['year']}, Round={metadata['round']}")
    
    # 2. 버전 ID 생성
    version_id = f"{metadata['year']}_{metadata['round']}"
    print(f"✅ 버전 ID 생성: {version_id}")
    
    # 3. 규칙 저장 시뮬레이션
    mock_rules = {
        "청년": {"period": "6년", "rent_rate": "90%", "land_area": "300㎡ ~ 600㎡"},
        "고령자": {"period": "20년", "rent_rate": "80%", "land_area": "400㎡ ~ 800㎡"}
    }
    
    try:
        filepath = loader._save_rules_to_json(mock_rules, version_id)
        print(f"✅ JSON 저장: {filepath}")
        
        loader._add_processing_history(filename, version_id, success=True)
        print(f"✅ 처리 이력 기록")
        
        loaded = loader.get_rules_by_version(version_id)
        if loaded and len(loaded) == 2:
            print(f"✅ 검증 성공")
            return True
        else:
            print(f"❌ 검증 실패")
            return False
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def main():
    print("\n" + "="*80)
    print("LH Notice Loader 시스템 테스트 (v7.0)")
    print("="*80)
    
    tests = [
        ("파일명 패턴 인식", test_filename_pattern),
        ("LH 규칙 추출", test_rule_extraction),
        ("JSON 저장/불러오기", test_json_storage),
        ("처리 이력 관리", test_processing_history),
        ("통합 시나리오", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 테스트 실행 중 오류: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*80)
    print("최종 결과")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*80}")
    print(f"✅ 성공: {passed}/{total}")
    print(f"❌ 실패: {total - passed}/{total}")
    print(f"성공률: {passed/total*100:.1f}%")
    print(f"{'='*80}")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
