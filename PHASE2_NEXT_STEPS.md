# ZeroSite Phase 2 - 다음 단계 권장사항

## 📋 현재 상태 요약 (2026-01-11)

### ✅ 완료된 작업

#### Phase 1 (Service → Real Engine 통합 준비)
- [x] 시스템 모드 재선언 (DATA-FIRST MODE)
- [x] Real Engine 파일 존재 확인
- [x] Service 파일에 Real Engine Import 추가
- [x] Context 스키마 불일치 발견
- [x] 문서화 완료

#### Phase 2 (완전 설계)
- [x] AUTO RESTORE & LOCK 설계 문서 작성
- [x] M1~M6 전체 복원 로직 설계
- [x] MOC/SAMPLE 차단 규칙 정의
- [x] 출력 템플릿 규칙 정의
- [x] Git 커밋 완료

### ⚠️ 진행 필요 작업

#### Phase 2 구현
- [ ] Context 스키마 통일
- [ ] Real Engine 완전 통합
- [ ] 전체 파이프라인 테스트
- [ ] 보고서 템플릿 재적용
- [ ] 최종 LOCK 선언

---

## 🎯 Phase 2 구현 권장 순서

### 1단계: Context 스키마 문서화 및 통일

#### 1.1. 현재 스키마 문서화
```bash
# 각 Context 스키마 확인
- CanonicalLandContext (M1)
- AppraisalContext (M2)
- HousingTypeContext (M3)
- CapacityContext (M4)
- FeasibilityContext (M5)
- LHReviewContext (M6)
```

#### 1.2. 필드 매핑 표 작성
```markdown
| Real Engine Field | Context Field | 변환 로직 |
|-------------------|---------------|-----------|
| context_id        | parcel_id     | UUID → PNU |
| area_sqm          | land_area     | 동일      |
| ...               | ...           | ...       |
```

#### 1.3. 변환 레이어 작성
```python
# app/core/adapters/context_adapter.py

class ContextAdapter:
    """Real Engine ↔ Context 변환"""
    
    @staticmethod
    def land_context_to_m3_input(land_ctx: CanonicalLandContext) -> Dict:
        """M1 Context → M3 Real Engine 입력"""
        ...
    
    @staticmethod
    def m3_output_to_housing_context(m3_result: Dict) -> HousingTypeContext:
        """M3 Real Engine 출력 → M3 Context"""
        ...
```

### 2단계: M1 Hard Gate 구현

#### 2.1. 검증 로직 작성
```python
# app/validators/m1_validator.py

class M1Validator:
    """M1 입력 데이터 검증"""
    
    REQUIRED_FIELDS = {
        "address": str,
        "land_area_sqm": float,
        "zoning": str,
        "transportation_data": dict,
        "infra_data": dict,
        "demographic_data": dict
    }
    
    def validate(self, data: Dict) -> Tuple[bool, List[str]]:
        """검증 실행"""
        ...
```

#### 2.2. Pipeline 통합
```python
# app/core/pipeline/zer0site_pipeline.py

def run_m1(self, input_data: Dict) -> CanonicalLandContext:
    """M1 실행 (Hard Gate)"""
    # 검증
    valid, missing = M1Validator().validate(input_data)
    if not valid:
        raise DataMissingError(missing)
    
    # 실행
    ...
```

### 3단계: M2 시장 맥락 분석 활성화

#### 3.1. M2 Service 업데이트
```python
# app/modules/m2_appraisal/service.py

class AppraisalService:
    """M2 토지가치/시장 맥락 분석"""
    
    def run(self, land_ctx: CanonicalLandContext) -> AppraisalContext:
        """
        실거래 기준 토지가치 평가
        주변 시장 구조 분석
        장기 성장성 판단
        """
        ...
```

#### 3.2. 실제 데이터 연동
```python
# 실거래 API 연동
# 주변 거래 데이터 수집
# 시장 구조 분석 텍스트 생성
```

### 4단계: M3~M6 Real Engine 완전 통합

#### 4.1. M3 통합
```python
# app/modules/m3_lh_demand/service.py

def run(self, land_ctx, appraisal_ctx):
    """M3 실행 (Real Engine)"""
    # Context → Real Engine 입력 변환
    m3_input = ContextAdapter.to_m3_input(land_ctx, appraisal_ctx)
    
    # Real Engine 실행
    analyzer = M3EnhancedAnalyzer(context_id, m3_input, frozen_context)
    m3_result = analyzer.generate_full_m3_report_data()
    
    # Real Engine 출력 → Context 변환
    housing_ctx = ContextAdapter.to_housing_context(m3_result)
    
    return housing_ctx
```

#### 4.2. M4~M6 동일 패턴 적용
```python
# M4: Real Data Analyzer 통합
# M5: Real Data Engine 통합
# M6: Real Decision Engine 통합
```

### 5단계: MOC/SAMPLE 차단 코드 구현

#### 5.1. 전역 검출 함수
```python
# app/core/validators/moc_detector.py

class MOCDetector:
    """MOC/SAMPLE 데이터 검출"""
    
    BLOCKED_VALUES = [
        "POI 0개 기본값",
        "20세대 / 26세대 고정값",
        "Mock Data",
        "Sample Data",
        ...
    ]
    
    def detect(self, data: Any) -> Tuple[bool, str]:
        """MOC 데이터 감지"""
        ...
```

#### 5.2. Pipeline 적용
```python
def run_module(self, module_name, input_data):
    """모듈 실행 (MOC 차단)"""
    # MOC 검출
    is_moc, moc_type = MOCDetector().detect(input_data)
    if is_moc:
        raise MOCDataError(f"{module_name}: {moc_type} detected")
    
    # 실행
    ...
```

### 6단계: 전체 파이프라인 테스트

#### 6.1. 실제 데이터 준비
```python
TEST_INPUT = {
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_area_sqm": 500.0,
    "zoning": "제2종일반주거지역",
    "bcr": 60.0,
    "far": 250.0,
    "transportation_data": {
        "subway_stations": 2,
        "bus_stops": 5
    },
    "infra_data": {
        "convenience_stores": 8,
        "hospitals": 2,
        "schools": 3,
        "parks": 1
    },
    "demographic_data": {
        "one_two_person_ratio": 65,
        "youth_ratio": 35,
        "rental_ratio": 55
    }
}
```

#### 6.2. 테스트 실행
```bash
# M1~M6 전체 파이프라인 테스트
curl -X POST http://localhost:49999/api/v4/pipeline/analyze \
  -H "Content-Type: application/json" \
  -d @test_input.json

# 예상 결과:
# - M1: Context 생성 완료
# - M2: 시장 맥락 분석 완료
# - M3: 청년형 선택 (탈락 논리 명시)
# - M4: 법정 25세대 / 이론 28세대 / 권장 22세대
# - M5: NPV +43,200,000원, IRR 0.72%, ROI 1.45%
# - M6: 조건부 GO (근거 2개 + 리스크 3개)
```

### 7단계: 보고서 템플릿 재적용

#### 7.1. M3 템플릿
```html
<!-- app/templates_v13/m3_supply_type_decision_os.html -->
<!-- 점수표 제거, 탈락 논리 중심 -->
```

#### 7.2. M4~M6 템플릿
```html
<!-- M4: 법정/이론/권장 세 가지 출력 -->
<!-- M5: 비용/수익 구조 설명 -->
<!-- M6: 조건부 GO + 근거 + 리스크 -->
```

### 8단계: 최종 LOCK 선언

#### 8.1. LOCK 파일 생성
```python
# app/core/lock/data_first_lock.py

"""
ZeroSite DATA-FIRST MODE LOCK
==============================

본 파일은 ZeroSite가 항상 DATA-FIRST MODE로만 동작하도록 보장합니다.

LOCKED:
- Real Engine만 사용
- MOC/SAMPLE 전면 차단
- FallBack 금지
- 데이터 없으면 중단

DO NOT MODIFY THIS FILE!
"""

DATA_FIRST_MODE_LOCKED = True
MOC_DETECTION_ENABLED = True
FALLBACK_DISABLED = True
```

#### 8.2. 시스템 시작 시 검증
```python
# app/main.py

from app.core.lock.data_first_lock import (
    DATA_FIRST_MODE_LOCKED,
    MOC_DETECTION_ENABLED,
    FALLBACK_DISABLED
)

assert DATA_FIRST_MODE_LOCKED, "DATA-FIRST MODE must be locked"
assert MOC_DETECTION_ENABLED, "MOC detection must be enabled"
assert FALLBACK_DISABLED, "Fallback must be disabled"

logger.info("✅ ZeroSite DATA-FIRST MODE LOCKED")
```

---

## 📦 예상 산출물

### 코드
```
app/core/adapters/context_adapter.py (신규)
app/validators/m1_validator.py (신규)
app/core/validators/moc_detector.py (신규)
app/core/lock/data_first_lock.py (신규)
app/modules/m2_appraisal/service.py (업데이트)
app/modules/m3_lh_demand/service.py (업데이트)
app/modules/m4_capacity/service_v2.py (업데이트)
app/modules/m5_feasibility/service.py (업데이트)
app/modules/m6_lh_review/service.py (업데이트)
```

### 템플릿
```
app/templates_v13/m3_supply_type_decision_os.html (업데이트)
app/templates_v13/m4_building_scale_decision_os.html (업데이트)
app/templates_v13/m5_feasibility_decision_os.html (업데이트)
app/templates_v13/m6_lh_review_decision_os.html (업데이트)
```

### 테스트
```
tests/test_m1_validator.py (신규)
tests/test_moc_detector.py (신규)
tests/test_pipeline_real_data.py (신규)
```

### 문서
```
CONTEXT_SCHEMA_MAPPING.md (신규)
PHASE2_IMPLEMENTATION_COMPLETE.md (신규)
ZEROSITE_FINAL_LOCK_DECLARATION.md (신규)
```

---

## 🔗 관련 문서

### Phase 1
- `ZEROSITE_SYSTEM_RECOVERY_REPORT.md`
- `ZEROSITE_SYSTEM_RECOVERY_PHASE1_COMPLETE.md`
- `ZEROSITE_DATA_INTEGRITY_RESTORED.md`

### Phase 2
- `ZEROSITE_AUTO_RESTORE_AND_LOCK.md` (설계)
- `M3_REAL_DECISION_ENGINE_DESIGN.md`

---

## ⏱️ 예상 작업 시간

- **Context 스키마 통일**: 2-3시간
- **M1 Hard Gate 구현**: 1-2시간
- **M2 활성화**: 2-3시간
- **M3~M6 Real Engine 완전 통합**: 4-6시간
- **MOC/SAMPLE 차단**: 1-2시간
- **전체 테스트**: 2-3시간
- **템플릿 재적용**: 2-3시간
- **최종 LOCK**: 1시간

**총 예상**: 15-23시간

---

## 🎯 최종 목표

### 복원 완료 상태
```
✅ M1: Hard Gate 적용, 실제 데이터만 허용
✅ M2: 시장 맥락 분석 활성화
✅ M3: 점수표 제거, 탈락 논리 중심
✅ M4: 법정/이론/권장 세 가지 출력
✅ M5: 비용/수익 구조 + NPV/IRR/ROI
✅ M6: 조건부 GO + 근거 2개 + 리스크 1개
✅ MOC/SAMPLE: 전면 차단
✅ FallBack: 완전 금지
✅ 디자인: 데이터 이후만
```

### LOCK 상태
```
🔒 DATA-FIRST MODE: PERMANENTLY LOCKED
🔒 Real Engine: EXCLUSIVELY USED
🔒 MOC Detection: ALWAYS ENABLED
🔒 FallBack: DISABLED FOREVER
```

---

## 📞 다음 단계 문의

다음 중 하나를 선택하여 진행하시면 됩니다:

### 옵션 1: 단계별 구현
```
"1단계부터 시작해줘 (Context 스키마 문서화)"
```

### 옵션 2: 핵심 우선 구현
```
"M3부터 완전 통합해줘 (가장 중요한 모듈)"
```

### 옵션 3: 테스트 우선
```
"실제 데이터로 현재 상태 테스트해줘"
```

### 옵션 4: 전체 자동 구현
```
"Phase 2 전체를 한 번에 구현해줘"
```

---

**ⓒ ZeroSite by AntennaHoldings | Natai Heum**  
**System Mode: DATA-FIRST LOCKED**  
**Phase: 2 of 2 (Ready for Implementation)**  
**Date: 2026-01-11**

---

**END OF PHASE 2 NEXT STEPS**
