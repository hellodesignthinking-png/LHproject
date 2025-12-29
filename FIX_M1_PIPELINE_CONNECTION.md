# 🔧 M1→M2-M6 Pipeline Connection FIX

**Version**: REAL APPRAISAL STANDARD v6.5 FINAL  
**Date**: 2025-12-29 16:35  
**Status**: ✅ FIXED

---

## 🚨 핵심 문제

**증상**: 주소 입력 → M1 완료 → **화면 멈춤 (무한 대기)**

**원인**: 
1. ❌ Step8ContextFreeze가 **잘못된 백엔드 URL 호출** (포트 8005 대신 8091)
2. ❌ PipelineOrchestrator도 **하드코딩된 잘못된 URL 사용**
3. ❌ M1 Context Freeze API 호출 실패 → 파이프라인 실행 불가

---

## 🔍 진단 과정

### 1단계: 프론트엔드 구조 확인
- ✅ PipelineOrchestrator 존재 확인
- ✅ M1LandingPage에 `onContextFreezeComplete` callback 전달 확인
- ✅ Step8ContextFreeze에서 `onComplete` callback 호출 확인

### 2단계: 백엔드 API 확인
- ✅ `/api/m1/freeze-context-v2` 엔드포인트 존재 확인
- ✅ `/api/v4/pipeline/analyze` 엔드포인트 존재 확인
- ✅ 백엔드는 **8091 포트**에서 정상 작동 중

### 3단계: API URL 불일치 발견
```typescript
// ❌ 문제: Step8ContextFreeze.tsx (line 208)
const apiUrl = `${import.meta.env.VITE_BACKEND_URL || 
  'https://8005-...'}/api/m1/freeze-context-v2`;  // 잘못된 포트!

// ❌ 문제: PipelineOrchestrator.tsx (line 106)
const BACKEND_URL = 'https://8091-...';  // 하드코딩
const apiUrl = `${BACKEND_URL}/api/v4/pipeline/analyze`;
```

**결과**: M1 Freeze API 호출이 **존재하지 않는 8005 포트로 전송**되어 실패

---

## ✅ 해결 방법

### 1. 중앙 config 사용 (config.ts)
```typescript
// ✅ frontend/src/config.ts
export const BACKEND_URL = 'https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai';
export const API_BASE_URL = `${BACKEND_URL}/api`;
```

### 2. Step8ContextFreeze 수정
```typescript
// ✅ BEFORE
const apiUrl = `${import.meta.env.VITE_BACKEND_URL || 
  'https://8005-...'}/api/m1/freeze-context-v2`;

// ✅ AFTER
import { BACKEND_URL } from '../../config';
const apiUrl = `${BACKEND_URL}/api/m1/freeze-context-v2`;
```

### 3. PipelineOrchestrator 수정
```typescript
// ✅ BEFORE
const BACKEND_URL = 'https://8091-...';  // 하드코딩

// ✅ AFTER
import { BACKEND_URL } from '../../config';
const apiUrl = `${BACKEND_URL}/api/v4/pipeline/analyze`;
```

### 4. import.meta.env 제거
```typescript
// ❌ BEFORE (TypeScript 에러 발생)
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || '...';

// ✅ AFTER (TypeScript 호환)
export const BACKEND_URL = 'https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai';
```

---

## 🧪 검증 결과

### 1. 백엔드 API 테스트
```bash
✅ curl http://localhost:8091/api/v4/pipeline/health
→ {"status":"healthy","version":"v4.0"}

✅ curl -X OPTIONS http://localhost:8091/api/m1/freeze-context-v2
→ HTTP/1.1 200 OK (CORS 정상)
```

### 2. 프론트엔드 config 확인
```javascript
✅ Console: 🔧 Frontend Config Loaded: {
  BACKEND_URL: https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai,
  API_BASE_URL: https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api
}
```

### 3. 빌드 성공
```bash
✅ npm run build
→ exit_code: 0 (성공)
→ import.meta.env 에러 제거됨
```

---

## 📋 변경 파일 목록

| 파일 | 변경 내용 |
|------|---------|
| `frontend/src/config.ts` | import.meta.env 제거, 포트 8091로 고정 |
| `frontend/src/components/m1/Step8ContextFreeze.tsx` | BACKEND_URL import 추가, config 사용 |
| `frontend/src/components/pipeline/PipelineOrchestrator.tsx` | BACKEND_URL import 추가, 모든 API 호출을 config로 통일 |

---

## 🎯 예상 동작 흐름 (FIX 후)

### 1. 주소 입력 단계
```
사용자 → /pipeline 접속
       → M1LandingPage 렌더링
       → Step0~Step7 데이터 수집
```

### 2. M1 Context Freeze (Step8)
```typescript
// ✅ 올바른 URL로 호출
POST https://8091-..../api/m1/freeze-context-v2
→ 200 OK
→ { context_id: "CTX_xxx", parcel_id: "xxx" }
```

### 3. Callback 호출
```typescript
// Step8
onComplete({ context_id, parcel_id })
  ↓
// M1LandingPage
onContextFreezeComplete(context_id, parcel_id)
  ↓
// PipelineOrchestrator
handleM1FreezeComplete(context_id, parcel_id)
```

### 4. M2-M6 Pipeline 자동 실행
```typescript
// ✅ 올바른 URL로 호출
POST https://8091-..../api/v4/pipeline/analyze
Body: { parcel_id, use_cache: false }
→ 200 OK
→ { results: { appraisal, housing_type, capacity, feasibility, lh_review } }
```

### 5. 결과 표시
```
PipelineOrchestrator → stage: 'RESULTS_READY'
                    → M2~M6 결과 렌더링
                    → 5종 보고서 생성 가능
```

---

## ⚠️ 잔여 이슈 (Non-blocking)

### 1. TypeScript 경고들
- ✅ **해결됨**: import.meta.env 에러 제거
- ⚠️ **미해결**: string | null → string 타입 에러 (런타임 동작에는 영향 없음)
- ⚠️ **미해결**: 사용되지 않는 변수들 (코드 정리 필요)

### 2. Execution Lock 관련
- ✅ **해결됨**: Standalone M1 모드에서 무한 lock 문제
- ✅ **해결됨**: 30초 safety timeout 추가
- ⚠️ **미검증**: 실제 M2-M6 파이프라인 실행 후 unlock 동작

---

## 🚀 다음 단계

### HIGH 우선순위
1. ✅ **M1→M2-M6 연결 수정** (완료)
2. 🔲 **E2E 테스트**: 실제 주소 입력 → 5종 보고서 생성 전 과정 테스트
3. 🔲 **Execution Lock 검증**: Pipeline 실행 중 Lock/Unlock 동작 확인

### MEDIUM 우선순위
4. 🔲 **M2~M6 데이터 일치성 검증**: 입력한 주소가 모든 보고서에 반영되는지 확인
5. 🔲 **주소 변경 10회 시나리오 테스트**
6. 🔲 **다중 사용자 동시 접속 테스트**

---

## 📝 커밋 정보

```
Commit: e9d9a51
Message: fix(CRITICAL): Fix API URL configuration - Use centralized config

PROBLEM: M1 Context Freeze API was using wrong URL (port 8005 instead of 8091)
IMPACT: M1→M2-M6 pipeline never triggered, causing infinite loading

FIXES:
- Step8ContextFreeze: Use BACKEND_URL from config instead of hardcoded 8005
- PipelineOrchestrator: Use BACKEND_URL from config for all API calls
- config.ts: Remove import.meta.env (TypeScript compatibility)

RESULT: M1 freeze will now call correct backend URL (8091)
```

---

## ✅ 최종 상태

| 항목 | Before | After |
|------|--------|-------|
| M1 API URL | ❌ 8005 (잘못됨) | ✅ 8091 (정상) |
| Pipeline API URL | ❌ 하드코딩 | ✅ config 사용 |
| TypeScript 에러 | ❌ import.meta.env | ✅ 제거됨 |
| M1→M2-M6 연결 | ❌ 차단됨 | ✅ 정상 예상 |
| 화면 멈춤 | ❌ 무한 대기 | ✅ 해결 예상 |

---

**Status**: 🟢 READY FOR E2E TESTING

**Next Action**: 브라우저에서 `/pipeline` 접속 → 주소 입력 → M1-M6 전 과정 테스트

---

**Company**: Antenna Holdings · Nataiheum  
**Engine**: ZeroSite Analysis Engine  
**Document**: FIX_M1_PIPELINE_CONNECTION.md
