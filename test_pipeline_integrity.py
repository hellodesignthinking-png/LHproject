"""
ZeroSite Pipeline Integrity Validator 테스트
============================================

목적: M1~M6 정합성 체크 자동화 스크립트 검증

Author: ZeroSite Development Team
Date: 2026-01-11
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.utils.pipeline_integrity_validator import (
    PipelineIntegrityValidator,
    PipelineIntegrityExplainer
)

def test_case_1_missing_m4():
    """테스트 케이스 1: M4 데이터 누락"""
    print("=" * 80)
    print("TEST CASE 1: M4 데이터 누락")
    print("=" * 80)
    
    pipeline_results = {
        "land": {
            "details": {
                "address": "서울특별시 강남구 역삼동 123-45",
                "land_area_sqm": 500,
                "zoning": "제2종일반주거지역"
            }
        },
        "appraisal": {
            "summary": {"land_value_total_krw": 6081933539},
            "details": {"analysis": "토지 가치 분석 내용..." * 50}
        },
        "housing_type": {
            "details": {
                "selected": {"type": "청년형"},
                "insights": {"weaknesses": ["A", "B", "C"]}
            }
        },
        "building_capacity": {},  # M4 데이터 없음
        "feasibility": {},
        "comprehensive": {}
    }
    
    validator = PipelineIntegrityValidator(pipeline_results)
    result = validator.validate()
    
    print(f"\n✅ 검증 결과:")
    print(f"   STATUS: {result['status']}")
    print(f"   BLOCK_MODULE: {result.get('block_module', 'N/A')}")
    print(f"   MISSING_FIELDS: {result.get('missing_fields', [])}")
    print(f"   ERRORS: {len(result['errors'])}개")
    
    # UX 메시지 생성
    explainer = PipelineIntegrityExplainer()
    ux_message = explainer.generate_user_friendly_explanation(result)
    
    print(f"\n📢 사용자 메시지:")
    print(ux_message)

def test_case_2_all_pass():
    """테스트 케이스 2: 전체 PASS"""
    print("\n" + "=" * 80)
    print("TEST CASE 2: 전체 데이터 정상")
    print("=" * 80)
    
    pipeline_results = {
        "land": {
            "details": {
                "address": "서울특별시 강남구 역삼동 123-45",
                "land_area_sqm": 500,
                "zoning": "제2종일반주거지역"
            }
        },
        "appraisal": {
            "summary": {"land_value_total_krw": 6081933539},
            "details": {"analysis": "토지 가치 분석 내용..." * 50}
        },
        "housing_type": {
            "details": {
                "selected": {"type": "청년형"},
                "insights": {"weaknesses": ["A", "B", "C"]}
            }
        },
        "building_capacity": {
            "summary": {
                "recommended_units": 26,
                "total_floor_area_sqm": 1300,
                "recommended_scale": True
            }
        },
        "feasibility": {
            "summary": {
                "total_project_cost_krw": 11000000000,
                "lh_purchase_price_krw": 6690126893,
                "npv_public_krw": 792999999
            }
        },
        "comprehensive": {
            "details": {
                "decision_basis": ["A", "B", "C"],
                "risks": ["R1", "R2"]
            }
        }
    }
    
    validator = PipelineIntegrityValidator(pipeline_results)
    result = validator.validate()
    
    print(f"\n✅ 검증 결과:")
    print(f"   STATUS: {result['status']}")
    print(f"   ERRORS: {len(result['errors'])}개")
    
    if result['status'] == "PASS":
        print("\n🎉 모든 모듈이 정상입니다. 파이프라인 실행 가능!")

def test_case_3_global_sanitizer():
    """테스트 케이스 3: GLOBAL SANITIZER (금지 값 검출)"""
    print("\n" + "=" * 80)
    print("TEST CASE 3: GLOBAL SANITIZER (금지 값 검출)")
    print("=" * 80)
    
    pipeline_results = {
        "land": {
            "details": {
                "address": "N/A",  # 금지 값
                "land_area_sqm": 500,
                "zoning": "제2종일반주거지역"
            }
        },
        "appraisal": {
            "summary": {"land_value_total_krw": None},  # 금지 값
            "details": {"analysis": "토지 가치 분석 내용..." * 50}
        },
        "housing_type": {
            "details": {
                "selected": {"type": "청년형"},
                "insights": {"weaknesses": ["A", "B", "C"]}
            }
        },
        "building_capacity": {
            "summary": {
                "recommended_units": 26,
                "total_floor_area_sqm": 1300,
                "recommended_scale": True
            }
        },
        "feasibility": {
            "summary": {
                "total_project_cost_krw": 11000000000,
                "lh_purchase_price_krw": 6690126893,
                "npv_public_krw": 792999999
            }
        },
        "comprehensive": {
            "details": {
                "decision_basis": ["A", "B", "C"],
                "risks": ["R1", "R2"]
            }
        }
    }
    
    validator = PipelineIntegrityValidator(pipeline_results)
    result = validator.validate()
    
    print(f"\n✅ 검증 결과:")
    print(f"   STATUS: {result['status']}")
    print(f"   ERRORS: {len(result['errors'])}개")
    
    if result['status'] == "FAIL":
        print(f"\n⚠️ 금지 값이 감지되었습니다:")
        for error in result['errors']:
            if "GLOBAL SANITIZER" in error:
                print(f"   - {error}")

def test_case_4_context_mismatch():
    """테스트 케이스 4: Context ID 불일치"""
    print("\n" + "=" * 80)
    print("TEST CASE 4: Context ID 불일치")
    print("=" * 80)
    
    pipeline_results = {
        "land": {
            "context_id": "CTX_001",
            "details": {
                "address": "서울특별시 강남구 역삼동 123-45",
                "land_area_sqm": 500,
                "zoning": "제2종일반주거지역"
            }
        },
        "appraisal": {
            "context_id": "CTX_002",  # 불일치
            "summary": {"land_value_total_krw": 6081933539},
            "details": {"analysis": "토지 가치 분석 내용..." * 50}
        }
    }
    
    validator = PipelineIntegrityValidator(pipeline_results)
    result = validator.validate()
    
    print(f"\n✅ 검증 결과:")
    print(f"   STATUS: {result['status']}")
    print(f"   ERRORS: {len(result['errors'])}개")
    
    if result['status'] == "FAIL":
        print(f"\n⚠️ Context ID 불일치 감지:")
        for error in result['errors']:
            if "Context ID mismatch" in error:
                print(f"   - {error}")

if __name__ == "__main__":
    test_case_1_missing_m4()
    test_case_2_all_pass()
    test_case_3_global_sanitizer()
    test_case_4_context_mismatch()
    
    print("\n" + "=" * 80)
    print("✅ 테스트 완료")
    print("=" * 80)
