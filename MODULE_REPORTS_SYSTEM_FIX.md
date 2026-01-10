# 모듈별 보고서 (M2-M6) 완전 정리

**작성일**: 2026-01-04  
**상태**: 🔧 IN PROGRESS

---

## 📊 현재 시스템 구조

### 백엔드 API 구조

#### 1. 모듈별 PDF 다운로드 엔드포인트
**파일**: `/home/user/webapp/app/routers/pdf_download_standardized.py`

**엔드포인트**:
```
GET /api/v4/reports/{module}/pdf?context_id={context_id}
```

**지원 모듈**:
- M2: 토지감정평가
- M3: 선호유형분석  
- M4: 건축규모결정
- M5: 사업성분석
- M6: LH심사예측

#### 2. 데이터 소스
- **Primary**: `results_cache` (파이프라인 실행 결과)
- **Fallback**: 테스트 데이터 (`_get_test_data_for_module()`)

### 프론트엔드 구조

**파일**: `/home/user/webapp/frontend/src/components/pipeline/PipelineOrchestrator.tsx`

**다운로드 플로우**:
1. 사용자가 M1-M6 파이프라인 완료
2. 각 모듈 결과 카드에 "PDF 다운로드" 버튼 표시
3. 버튼 클릭 시 `handleDownloadPDF()` 실행
4. API 호출: `/api/v4/reports/{module}/pdf?context_id={contextId}`
5. 브라우저에서 PDF 다운로드

---

## 🔍 문제 진단

### 1. Context ID 처리 문제

**증상**: PDF 다운로드 시 404 또는 빈 데이터 반환

**원인**:
```python
# pdf_download_standardized.py Line 170-199
def _get_real_data_for_module(module: str, context_id: str) -> dict:
    # UUID 형식의 context_id 차단
    if "-" in context_id:
        raise HTTPException(400, "UUID 형식의 context_id는 지원하지 않습니다")
    
    # parcel_id 추출 시도
    parcel_id = context_id.split("_")[0]
    
    # results_cache에서 데이터 조회
    if parcel_id not in results_cache:
        raise HTTPException(404, "파이프라인 결과를 찾을 수 없습니다")
```

**문제점**:
- 프론트엔드가 UUID 형식의 `contextId` 전달
- 백엔드는 `parcel_id` 기반 조회 필요
- 두 시스템 간 ID 형식 불일치

### 2. 테스트 데이터 미사용

**현재 코드** (Line 109):
```python
# TODO: context_id로 실제 데이터 조회
# 현재는 테스트 데이터 사용
test_data = _get_test_data_for_module(module, context_id)
```

**문제**: 
- `_get_test_data_for_module()`이 호출되지만
- 실제로는 `_get_real_data_for_module()`을 호출해야 함
- 또는 테스트 모드 플래그 필요

---

## ✅ 해결 방안

### 방안 1: 테스트 모드 활성화 (빠른 해결)

**목적**: 실제 파이프라인 데이터 없이도 PDF 다운로드 가능

**수정 파일**: `app/routers/pdf_download_standardized.py`

**변경사항**:
1. `_get_test_data_for_module()` 함수 실제 호출
2. 풍부한 테스트 데이터 제공
3. 각 모듈별 샘플 PDF 생성 가능

**구현**:
```python
@router.get("/{module}/pdf")
async def download_module_pdf(
    module: Literal["M2", "M3", "M4", "M5", "M6"],
    context_id: str = Query(...),
    use_test_data: bool = Query(False, description="테스트 데이터 사용")
):
    if use_test_data:
        test_data = _get_test_data_for_module(module, context_id)
    else:
        test_data = _get_real_data_for_module(module, context_id)
    
    # PDF 생성...
```

### 방안 2: Context ID 매핑 구축 (완전한 해결)

**목적**: UUID ↔ parcel_id 양방향 매핑

**구현**:
```python
# 메모리 또는 Redis에 매핑 저장
context_id_mapping = {
    "uuid-format-context-id": "parcel_id_12345",
    "parcel_id_12345": "uuid-format-context-id"
}

def resolve_context_id(context_id: str) -> str:
    """UUID → parcel_id 또는 parcel_id → parcel_id"""
    if "-" in context_id:
        return context_id_mapping.get(context_id, context_id)
    return context_id
```

### 방안 3: 프론트엔드 수정

**목적**: `analysisId` (parcel_id) 사용

**현재 코드**:
```typescript
const finalUrl = `${backendUrl}/api/v4/reports/${moduleId}/pdf?context_id=${contextId}`;
```

**수정 후**:
```typescript
// analysisId는 PNU/parcel_id (실제 데이터 키)
const finalUrl = `${backendUrl}/api/v4/reports/${moduleId}/pdf?context_id=${analysisId}`;
```

---

## 🚀 즉시 실행 계획

### 단계 1: 테스트 모드 활성화 ✅

**목표**: 5분 내 모든 모듈 PDF 다운로드 가능

**작업**:
1. `_get_test_data_for_module()` 구현 완성
2. Line 109 코드 실제 호출로 변경
3. 테스트: 각 모듈별 PDF 생성 확인

### 단계 2: 프론트엔드 analysisId 사용 ⏳

**목표**: 실제 파이프라인 데이터로 PDF 생성

**작업**:
1. `PipelineOrchestrator.tsx` 수정
2. `contextId` → `analysisId` 변경
3. 테스트: 파이프라인 실행 후 PDF 다운로드

### 단계 3: 문서화 ⏳

**작업**:
1. API 사용 예시 작성
2. 프론트엔드 통합 가이드
3. 트러블슈팅 섹션 추가

---

## 📝 테스트 체크리스트

### 백엔드 테스트
```bash
# M2 토지감정평가
curl "http://localhost:49999/api/v4/reports/M2/pdf?context_id=test123" \
  -o M2_test.pdf

# M3 선호유형분석
curl "http://localhost:49999/api/v4/reports/M3/pdf?context_id=test123" \
  -o M3_test.pdf

# M4 건축규모결정
curl "http://localhost:49999/api/v4/reports/M4/pdf?context_id=test123" \
  -o M4_test.pdf

# M5 사업성분석
curl "http://localhost:49999/api/v4/reports/M5/pdf?context_id=test123" \
  -o M5_test.pdf

# M6 LH심사예측
curl "http://localhost:49999/api/v4/reports/M6/pdf?context_id=test123" \
  -o M6_test.pdf
```

### 프론트엔드 테스트
1. M1-M6 파이프라인 완료
2. 각 모듈 카드에서 "PDF 다운로드" 버튼 확인
3. 클릭하여 PDF 다운로드 성공 확인
4. PDF 내용 검증

---

## 🎯 예상 결과

### 성공 시
- ✅ 모든 모듈 (M2-M6) PDF 다운로드 가능
- ✅ 풍부한 데이터가 포함된 전문가급 보고서
- ✅ 한글 파일명 지원
- ✅ 표준화된 포맷 (날짜, 보고서 번호 등)

### 실패 시 대응
- 404 오류 → context_id 검증 강화
- 빈 PDF → 테스트 데이터 확인
- 다운로드 실패 → CORS/헤더 설정 점검

---

## 📚 관련 파일

### 백엔드
- `/home/user/webapp/app/routers/pdf_download_standardized.py` - 메인 라우터
- `/home/user/webapp/app/services/pdf_generators/module_pdf_generator.py` - PDF 생성기
- `/home/user/webapp/app/api/endpoints/pipeline_reports_v4.py` - 파이프라인 결과 캐시

### 프론트엔드
- `/home/user/webapp/frontend/src/components/pipeline/PipelineOrchestrator.tsx` - 메인 오케스트레이터
- `/home/user/webapp/frontend/src/config.ts` - API 설정

### 문서
- `/home/user/webapp/CLASSIC_FORMAT_REPORTS_PORTAL.md` - Classic Format 보고서 (참고용)

---

## ⏭️ 다음 단계

1. **즉시**: 테스트 모드 활성화 및 검증
2. **단기**: 프론트엔드 analysisId 통합
3. **중기**: Context ID 매핑 시스템 구축
4. **장기**: Redis 기반 영구 저장소 구현

---

**작성자**: Claude AI Assistant  
**최종 업데이트**: 2026-01-04
