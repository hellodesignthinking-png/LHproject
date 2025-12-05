# ZeroSite v9.1 - 연결 검토 및 수정사항

**Date**: 2025-12-05  
**Status**: 🔍 종합 검토 중

---

## 🔍 발견된 문제점

### 1. Import 경로 오류

#### ❌ 문제: 잘못된 Import 경로
```python
# analysis_v9_1.py Line 27
from app.services_v9.unit_estimator_v9_0 import UnitEstimatorV9, UnitEstimationResult
# ❌ UnitEstimationResult는 존재하지 않음 (실제는 UnitEstimate)

# analysis_v9_1.py Line 31
from app.orchestrator_v9.engine_orchestrator_v9_0 import EngineOrchestratorV90
# ❌ 실제 경로: app.engines_v9.orchestrator_v9_0

# analysis_v9_1.py Line 911
from app.services_v9.orchestrator_v9_0 import EngineOrchestratorV90
# ❌ 실제 경로: app.engines_v9.orchestrator_v9_0
```

#### ✅ 수정
```python
# Correct imports
from app.services_v9.unit_estimator_v9_0 import UnitEstimatorV9, UnitEstimate
from app.engines_v9.orchestrator_v9_0 import EngineOrchestratorV90
```

---

### 2. AddressResolverV9 초기화 오류

#### ❌ 문제: 잘못된 생성자 호출
```python
# analysis_v9_1.py Line 56
_address_resolver = AddressResolverV9(api_key=kakao_api_key)
# ❌ AddressResolverV9()는 api_key 파라미터를 받지 않음
```

#### ✅ 수정
```python
# AddressResolverV9는 settings에서 자동으로 가져옴
_address_resolver = AddressResolverV9()
```

---

### 3. EngineOrchestratorV90 메서드 호출 불일치

#### ❌ 문제: 잘못된 메서드명
```python
# analysis_v9_1.py Line 762
analysis_result = await orchestrator.run_full_analysis(raw_input)
# ⚠️ EngineOrchestratorV90의 실제 메서드명 확인 필요
```

#### 🔍 확인 필요
실제 EngineOrchestratorV90의 메서드명을 확인하여 수정

---

### 4. PDF Renderer 및 Report Generator 경로

#### ❌ 문제: 존재하지 않는 모듈
```python
# analysis_v9_1.py Line 910
from app.services_v9.pdf_renderer_v9_0 import ReportOrchestrator
# ⚠️ pdf_renderer_v9_0.py에 ReportOrchestrator가 있는지 확인 필요
```

---

## 🛠️ 수정 작업 계획

### Phase 1: Import 경로 수정 (우선순위: 높음)
- [ ] `UnitEstimationResult` → `UnitEstimate`로 변경
- [ ] `app.orchestrator_v9` → `app.engines_v9`로 변경
- [ ] 중복 import 제거

### Phase 2: 생성자 및 초기화 수정 (우선순위: 높음)
- [ ] `AddressResolverV9()` 파라미터 제거
- [ ] Singleton 패턴 검증

### Phase 3: 메서드 호출 검증 (우선순위: 중간)
- [ ] `EngineOrchestratorV90` 메서드명 확인
- [ ] `analyze_comprehensive` vs `run_full_analysis` 통일

### Phase 4: 데이터 흐름 검증 (우선순위: 중간)
- [ ] `raw_input` → `EngineOrchestratorV90` 데이터 전달 확인
- [ ] `auto_calculated_fields` 응답 포함 확인

### Phase 5: 이전 버전(v9.0) 호환성 검증 (우선순위: 낮음)
- [ ] v9.0 API 엔드포인트 여전히 작동하는지 확인
- [ ] 기존 클라이언트 영향 없는지 확인

---

## 📝 상세 수정 목록

### 수정 1: analysis_v9_1.py Import 섹션
**파일**: `app/api/endpoints/analysis_v9_1.py`
**라인**: 18-35

**Before**:
```python
from app.services_v9.unit_estimator_v9_0 import UnitEstimatorV9, UnitEstimationResult
from app.services_v9.normalization_layer_v9_1_enhanced import NormalizationLayerV91

# v9.0 Components (backward compatibility)
from app.orchestrator_v9.engine_orchestrator_v9_0 import EngineOrchestratorV90
from app.models_v9.standard_schema_v9_0 import StandardAnalysisOutput
```

**After**:
```python
from app.services_v9.unit_estimator_v9_0 import UnitEstimatorV9, UnitEstimate
from app.services_v9.normalization_layer_v9_1_enhanced import NormalizationLayerV91

# v9.0 Components (backward compatibility)
from app.engines_v9.orchestrator_v9_0 import EngineOrchestratorV90
from app.models_v9.standard_schema_v9_0 import StandardAnalysisOutput
```

---

### 수정 2: AddressResolverV9 초기화
**파일**: `app/api/endpoints/analysis_v9_1.py`
**라인**: 49-57

**Before**:
```python
def get_address_resolver() -> AddressResolverV9:
    """Get or initialize AddressResolverV9 singleton"""
    global _address_resolver
    if _address_resolver is None:
        kakao_api_key = getattr(settings, 'KAKAO_REST_API_KEY', None)
        if not kakao_api_key:
            logger.warning("KAKAO_REST_API_KEY not configured. Address resolution may fail.")
        _address_resolver = AddressResolverV9(api_key=kakao_api_key)
    return _address_resolver
```

**After**:
```python
def get_address_resolver() -> AddressResolverV9:
    """Get or initialize AddressResolverV9 singleton"""
    global _address_resolver
    if _address_resolver is None:
        # AddressResolverV9 automatically gets api_key from settings
        _address_resolver = AddressResolverV9()
    return _address_resolver
```

---

### 수정 3: generate-report 엔드포인트 Import
**파일**: `app/api/endpoints/analysis_v9_1.py`
**라인**: 910-912

**Before**:
```python
from app.services_v9.pdf_renderer_v9_0 import ReportOrchestrator
from app.services_v9.orchestrator_v9_0 import EngineOrchestratorV90
from fastapi.responses import Response
```

**After**:
```python
from app.services_v9.pdf_renderer_v9_0 import ReportOrchestrator
from app.engines_v9.orchestrator_v9_0 import EngineOrchestratorV90
from fastapi.responses import Response
```

---

### 수정 4: _get_normalization_layer 헬퍼 함수 추가
**파일**: `app/api/endpoints/analysis_v9_1.py`
**라인**: 추가 필요

**Add**:
```python
def _get_normalization_layer() -> NormalizationLayerV91:
    """Get or initialize NormalizationLayerV91 (internal helper)"""
    return get_normalization_layer()
```

---

## 🔗 데이터 흐름 검증

### v9.1 Complete Data Flow

```
User Input (4 fields)
    ↓
┌─────────────────────────────────────┐
│  /api/v9/analyze-land               │
├─────────────────────────────────────┤
│  1. address                         │
│  2. land_area                       │
│  3. land_appraisal_price            │
│  4. zone_type                       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  NormalizationLayerV91              │
├─────────────────────────────────────┤
│  ├─ AddressResolverV9               │
│  │   → latitude, longitude          │
│  ├─ ZoningAutoMapperV9              │
│  │   → BCR, FAR, height_limit       │
│  └─ UnitEstimatorV9                 │
│      → unit_count, floors, parking  │
│      → total_gfa, residential_gfa   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  raw_input (16 fields)              │
├─────────────────────────────────────┤
│  User Input (4):                    │
│  1. address                         │
│  2. land_area                       │
│  3. land_appraisal_price            │
│  4. zone_type                       │
│                                     │
│  Auto-Calculated (12):              │
│  5. latitude                        │
│  6. longitude                       │
│  7. building_coverage_ratio         │
│  8. floor_area_ratio                │
│  9. height_limit                    │
│  10. unit_count                     │
│  11. estimated_floors               │
│  12. parking_spaces                 │
│  13. total_gfa                      │
│  14. residential_gfa                │
│  15. construction_cost_per_sqm      │
│  16. total_land_cost                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  EngineOrchestratorV90              │
├─────────────────────────────────────┤
│  ├─ GIS Analysis Engine             │
│  ├─ Financial Analysis Engine       │
│  ├─ LH Evaluation Engine            │
│  ├─ Risk Assessment Engine          │
│  ├─ Demand Analysis Engine          │
│  └─ Final Decision Engine           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  StandardAnalysisOutput             │
├─────────────────────────────────────┤
│  ├─ site_info                       │
│  ├─ gis_result                      │
│  ├─ financial_result                │
│  ├─ lh_scores                       │
│  ├─ risk_assessment                 │
│  ├─ demand_result                   │
│  └─ final_recommendation            │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  API Response                       │
├─────────────────────────────────────┤
│  {                                  │
│    "success": true,                 │
│    "data": {                        │
│      ...analysis_result             │
│    },                               │
│    "auto_calculated_fields": {     │
│      "latitude": 37.578,            │
│      "longitude": 126.889,          │
│      "unit_count": 35,              │
│      ...                            │
│    },                               │
│    "timestamp": "..."               │
│  }                                  │
└─────────────────────────────────────┘
```

---

## ⚠️ 검증이 필요한 부분

### 1. EngineOrchestratorV90 메서드명
```python
# 다음 중 어느 것이 맞는지 확인 필요:
# Option A:
result = await orchestrator.run_full_analysis(raw_input)

# Option B:
result = await orchestrator.analyze_comprehensive(raw_input)

# Option C:
result = await orchestrator.execute_analysis(raw_input)
```

### 2. StandardAnalysisOutput 구조
```python
# 응답 형식 확인 필요:
# Option A: 직접 dict 반환
analysis_result = {...}

# Option B: Pydantic 모델 반환
analysis_result = StandardAnalysisOutput(...)

# Option C: 모델을 dict로 변환
analysis_result = standard_output.dict()
```

### 3. Report Generator 통합
```python
# ReportOrchestrator 존재 여부 확인
# pdf_renderer_v9_0.py에 있는지 확인 필요
```

---

## 🧪 테스트 시나리오

### Test 1: Import 검증
```python
# 모든 import가 작동하는지 확인
from app.api.endpoints.analysis_v9_1 import router
print("✅ Imports successful")
```

### Test 2: Service 초기화
```python
# 모든 서비스가 초기화되는지 확인
from app.api.endpoints.analysis_v9_1 import (
    get_address_resolver,
    get_zoning_mapper,
    get_unit_estimator,
    get_normalization_layer
)

resolver = get_address_resolver()
mapper = get_zoning_mapper()
estimator = get_unit_estimator()
norm_layer = get_normalization_layer()
print("✅ All services initialized")
```

### Test 3: 엔드포인트 호출
```bash
# 4-field input으로 전체 분석 테스트
curl -X POST http://localhost:8000/api/v9/analyze-land \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 마포구 월드컵북로 120",
    "land_area": 1000.0,
    "land_appraisal_price": 9000000,
    "zone_type": "제3종일반주거지역"
  }'
```

---

## 🔧 즉시 수정할 항목 (우선순위 순)

### Priority 1: CRITICAL - Import 오류 (앱 실행 불가)
- [ ] `UnitEstimationResult` → `UnitEstimate`
- [ ] `app.orchestrator_v9` → `app.engines_v9`
- [ ] `AddressResolverV9(api_key=...)` → `AddressResolverV9()`

### Priority 2: HIGH - 데이터 흐름 검증
- [ ] `raw_input` 필드 완전성 확인
- [ ] `auto_calculated_fields` 응답 포함 확인
- [ ] `EngineOrchestratorV90` 메서드명 확인

### Priority 3: MEDIUM - Report Generator
- [ ] `ReportOrchestrator` 존재 확인
- [ ] Report generation 엔드포인트 테스트

### Priority 4: LOW - 이전 버전 호환성
- [ ] v9.0 API 엔드포인트 여전히 작동하는지 확인
- [ ] v9.0 클라이언트 영향 없는지 확인

---

## 📋 체크리스트

### Before Fix
- [ ] 현재 코드에서 import 오류 확인
- [ ] 실제 파일 구조와 import 경로 비교
- [ ] 메서드명과 시그니처 확인
- [ ] 데이터 흐름 문서화

### After Fix
- [ ] 모든 import 오류 해결
- [ ] 서버 시작 가능 확인
- [ ] API 엔드포인트 응답 확인
- [ ] E2E 테스트 통과 확인

---

**Status**: 🔍 검토 완료, 수정 준비 중  
**Next**: Import 오류 수정 → 테스트 → 검증
