# ZeroSite Pipeline Integrity Validator 통합 가이드

## 📌 목적
M1~M6 정합성 체크 자동화 스크립트를 파이프라인 API에 통합하여,
**데이터 부족 시 자동으로 차단**하고 **UX 친화적 메시지를 반환**합니다.

---

## 🔧 통합 위치

### **파일**: `app/api/endpoints/pipeline_reports_v4.py`

### **통합 포인트**: `@router.post("/analyze")` 엔드포인트

```python
from app.utils.pipeline_integrity_validator import (
    PipelineIntegrityValidator,
    PipelineIntegrityExplainer,
    ValidationStatus
)

@router.post("/analyze", response_model=PipelineAnalysisResponse)
async def analyze_parcel_pipeline(request: PipelineAnalysisRequest):
    """
    파이프라인 분석 엔드포인트 (정합성 체크 통합)
    """
    parcel_id = request.parcel_id
    address = request.address
    
    # 1️⃣ 기존 파이프라인 실행
    logger.info(f"🔄 Starting 6-modules pipeline for parcel_id={parcel_id}")
    
    # ... (기존 M1~M6 실행 로직) ...
    
    # 2️⃣ 정합성 검증 (NEW)
    validator = PipelineIntegrityValidator({
        "land": land_result,
        "appraisal": appraisal_result,
        "housing_type": housing_result,
        "building_capacity": capacity_result,
        "feasibility": feasibility_result,
        "comprehensive": comprehensive_result
    })
    
    validation_result = validator.validate()
    
    # 3️⃣ BLOCKED 상태 처리 (NEW)
    if validation_result["status"] == ValidationStatus.BLOCKED.value:
        logger.warning(f"⚠️ Pipeline BLOCKED at {validation_result['block_module']}")
        
        # UX 친화적 메시지 생성
        explainer = PipelineIntegrityExplainer()
        ux_message = explainer.generate_user_friendly_explanation(validation_result)
        
        # 클라이언트에 반환
        return {
            "status": "blocked",
            "block_module": validation_result["block_module"],
            "missing_fields": validation_result["missing_fields"],
            "user_message": ux_message,
            "validation_errors": validation_result["errors"]
        }
    
    # 4️⃣ PASS 상태 → 정상 응답
    return PipelineAnalysisResponse(
        parcel_id=parcel_id,
        analysis_id=parcel_id,
        status="success",
        # ... (기존 응답 필드)
    )
```

---

## 🎯 통합 효과

### **1) 자동 차단 (Hard Gate)**
- M1~M6 중 필수 필드 누락 시 **즉시 차단**
- 불완전한 데이터로 다음 단계 진행 방지

### **2) UX 개선**
```json
{
  "status": "blocked",
  "block_module": "M4",
  "missing_fields": ["total_units", "total_floor_area"],
  "user_message": "📍 현재 상태\n현재 분석은 M4 (건축 규모 판단) 단계에서 중단되었습니다.\n\n❓ 왜 중단되었는가\n..."
}
```

### **3) 보고서 품질 보장**
- PASS된 파이프라인 결과만 M4/M5/M6 보고서 생성
- "추정값" / "임시 데이터" 방지

---

## 🧪 테스트 스크립트

### **파일**: `test_pipeline_integrity.py`

```python
"""
ZeroSite Pipeline Integrity Validator 테스트
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

if __name__ == "__main__":
    test_case_1_missing_m4()
    test_case_2_all_pass()
    print("\n" + "=" * 80)
    print("✅ 테스트 완료")
    print("=" * 80)
```

---

## 🚀 배포 체크리스트

- [x] `app/utils/pipeline_integrity_validator.py` 생성 완료
- [ ] `app/api/endpoints/pipeline_reports_v4.py`에 통합
- [ ] `test_pipeline_integrity.py` 실행 및 검증
- [ ] M4/M5 DATA NOT LOADED 템플릿과 연계
- [ ] 프론트엔드 UX 메시지 표시 로직 추가

---

## 📚 관련 문서

- `M5_DATA_NOT_LOADED_FINAL_REPORT.md`: M5 데이터 부족 시 처리 방식
- `DATA_RELOADING_ENHANCEMENT_PLAN.md`: 데이터 재로딩 로직 계획
- `FINAL_COMPLETION_REPORT.md`: 전체 프로젝트 완료 보고서

---

ⓒ ZeroSite by AntennaHoldings | Natai Heum
