# 🚨 긴급 수정 필요 사항

**Date**: 2025-12-27  
**Status**: 백엔드 작동, 하지만 PDF/최종보고서 생성 실패

---

## 📊 현재 상태 요약

### ✅ 작동하는 것
1. **백엔드 서버** - 정상 시작
2. **파이프라인 API** - 데이터 생성 성공 (200 OK)
3. **모듈 HTML (M2-M6)** - 모두 200 OK

### ❌ 작동하지 않는 것
1. **모듈 PDF (M2-M6)** - 모두 500 에러
2. **최종 보고서 6종** - HTML 400, PDF 404

---

## 🔍 근본 원인

### Context Storage 문제

**문제**:
```python
# Pipeline에서 데이터 저장 (성공)
context_storage.store_frozen_context(context_id, assembled_data)
→ Redis 실패 → 인메모리 저장 (성공)

# PDF 생성 시 데이터 조회 (실패)
context = context_storage.get_frozen_context(context_id)
→ Redis 없음 → DB fallback 시도 → 테이블 없음 → 실패
→ 인메모리 재시도 없음 ❌
```

**코드 위치**:
- `app/services/context_storage.py` 라인 171-251 (get_frozen_context)
- 인메모리 fallback이 Redis가 None일 때만 작동
- Redis 연결되어 있지만 데이터 없을 때는 DB로만 fallback

---

## 🔧 수정 방법 (3가지 옵션)

### Option 1: Context Storage Get 수정 (권장)

```python
# app/services/context_storage.py의 get_frozen_context 수정

def get_frozen_context(context_id: str) -> Optional[Dict[str, Any]]:
    try:
        key = f"context:{context_id}"
        
        # STEP 1: Try Redis
        if redis_client:
            try:
                data = redis_client.get(key)
                if data:
                    return json.loads(data)
            except Exception as redis_err:
                logger.warning(f"Redis failed: {redis_err}")
        
        # STEP 2: Try in-memory (항상 시도!)
        if key in _memory_storage:
            return _memory_storage[key]['data']
        
        # STEP 3: Try DB fallback
        try:
            db = SessionLocal()
            snapshot = db.query(ContextSnapshot).filter(...).first()
            if snapshot:
                return json.loads(snapshot.context_data)
        except Exception as db_err:
            logger.warning(f"DB fallback failed: {db_err}")
        
        # STEP 4: 최종 인메모리 재시도 (혹시 모르니까)
        if key in _memory_storage:
            return _memory_storage[key]['data']
        
        return None
```

### Option 2: PDF 생성 시 assembled_data 직접 전달

```python
# app/api/endpoints/pipeline_reports_v4.py 수정

# Pipeline 실행 후
assembled_data = {...}  # M2-M6 데이터

# Context storage에 저장
context_storage.store_frozen_context(context_id, assembled_data)

# Response에 assembled_data 포함
return PipelineAnalysisResponse(
    ...
    _assembled_data=assembled_data  # 새 필드 추가
)

# PDF 엔드포인트에서
# 1. context_storage에서 조회 시도
# 2. 실패하면 → 캐시된 pipeline 결과에서 조회
# 3. 그것도 실패하면 → 에러
```

### Option 3: Redis 시작 (임시 해결책)

```bash
# Docker로 Redis 시작
docker run -d -p 6379:6379 redis:latest

# 또는 로컬 설치
apt-get install redis-server
redis-server --daemonize yes
```

---

## 📝 즉시 적용 가능한 Hotfix

### Hotfix 1: In-memory 우선 사용

```python
# app/services/context_storage.py 라인 200 이후에 추가

# STEP 1.5: ALWAYS try in-memory first (before DB)
if key in _memory_storage:
    context_data = _memory_storage[key]['data']
    logger.info(f"✅ [Memory] Context retrieved: {context_id}")
    return context_data
```

### Hotfix 2: PDF 생성 시 에러 무시하고 Mock 데이터 사용

```python
# app/routers/pdf_download_standardized.py

frozen_context = context_storage.get_frozen_context(context_id)

if not frozen_context:
    # ⚠️ TEMPORARY: Use mock data for testing
    logger.warning(f"Context not found, using MOCK DATA for {context_id}")
    frozen_context = {
        "modules": {
            "M2": {"summary": {"land_value": 6081933538, ...}},
            "M3": {"summary": {"recommended_type": "youth", ...}},
            ...
        }
    }
```

---

## 🎯 최종 보고서 엔드포인트 확인 필요

**현재 상태**: 모두 400/404 에러

**확인 필요**:
```bash
# 엔드포인트 존재 여부
grep -r "final.*report" app/api/endpoints/
grep -r "/final/" app/routers/

# 라우터 등록 확인
grep "final" app/main.py
```

**예상 경로**:
```
/api/v4/reports/final/{report_type}/html?context_id=xxx
/api/v4/reports/final/{report_type}/pdf?context_id=xxx
```

**Report Types**:
- all-in-one
- landowner-summary
- lh-technical
- financial-feasibility
- quick-check
- internal-review

---

## ⏰ 예상 소요 시간

| 수정 항목 | 소요 시간 | 우선순위 |
|-----------|-----------|----------|
| Context Storage Get 수정 | 30분 | HIGH |
| 최종 보고서 엔드포인트 확인 | 15분 | HIGH |
| 프론트엔드 주소 입력 테스트 | 10분 | MEDIUM |
| E2E 검증 | 20분 | MEDIUM |

**총 예상 시간**: 1-2시간

---

## 🚀 권장 수정 순서

1. **즉시 (5분)**: Context Storage에 인메모리 fallback 추가
2. **다음 (15분)**: PDF 생성 테스트 → 성공 확인
3. **다음 (15분)**: 최종 보고서 엔드포인트 찾기/수정
4. **다음 (20분)**: 최종 보고서 생성 테스트
5. **마지막 (15분)**: 프론트엔드 통합 테스트

---

## 📞 지금 필요한 Action

### 당장 해야 할 것
```bash
# 1. Context Storage 수정
vim app/services/context_storage.py
# 라인 205 다음에 추가:
# # FALLBACK: Always try memory before DB
# if key in _memory_storage:
#     return _memory_storage[key]['data']

# 2. 서버 재시작 (자동 reload)
# 변경사항 저장하면 자동 반영됨

# 3. 테스트
curl "http://localhost:8005/api/v4/reports/M2/pdf?context_id=test-quick-004" -o /tmp/test.pdf
file /tmp/test.pdf  # PDF file 확인
```

### 다음 해야 할 것
```bash
# 최종 보고서 엔드포인트 찾기
find app -name "*.py" -exec grep -l "final.*report" {} \;

# 없으면 생성 필요
# app/api/endpoints/final_reports_v4.py 생성
```

---

**Status**: 🟡 거의 완성, 마지막 1-2개 이슈만 해결하면 완료  
**ETA**: 1-2시간 내 완전 작동 가능  
**Next Step**: Context Storage 수정 → PDF 테스트
