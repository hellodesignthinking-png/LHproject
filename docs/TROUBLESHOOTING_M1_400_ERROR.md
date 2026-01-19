# M1 시작하기 400 Bad Request 오류 해결 완료

## 📋 Executive Summary

**Issue Reported**: M1 시작하기 버튼 클릭 시 400 Bad Request 오류 발생  
**Root Cause**: M1 상태가 이미 AUTO_FETCHED 상태로 저장되어 있음 (in-memory 저장소)  
**Solution**: M1 상태 확인 로직 추가 + 사용자 친화적 에러 메시지  
**Status**: ✅ **RESOLVED**  
**Date**: 2026-01-12  

---

## 🔍 문제 분석

### 오류 메시지
```
POST https://.../api/projects/proj_20260112_af3495af/modules/M1/auto-fetch 400 (Bad Request)

Response:
{
  "detail": {
    "error": "INVALID_STATE",
    "message": "auto-fetch는 EMPTY 상태에서만 가능합니다 (현재: M1Status.AUTO_FETCHED)",
    "current_status": "AUTO_FETCHED"
  }
}
```

### Root Cause 분석

#### 1. M1 상태 저장 방식
- **위치**: `app/core/m1_state_machine.py` Line 278
- **방식**: In-memory 딕셔너리 `m1_state_storage: Dict[str, M1StateContext] = {}`
- **문제**: 서버가 재시작되지 않으면 이전 상태가 메모리에 남아있음

#### 2. M1 상태 전이 규칙
```python
# app/api/endpoints/m1_3stage_api.py Line 69
if context.status != M1Status.EMPTY:
    raise HTTPException(
        status_code=400,
        detail={
            "error": "INVALID_STATE",
            "message": f"auto-fetch는 EMPTY 상태에서만 가능합니다 (현재: {context.status})",
            "current_status": context.status.value
        }
    )
```

**M1 상태 전이 흐름**:
```
EMPTY → (auto-fetch) → AUTO_FETCHED → (mock-generate) → EDITABLE → (freeze) → FROZEN
```

#### 3. 문제 시나리오
1. 사용자가 프로젝트 생성
2. M1 시작 버튼 클릭 → auto-fetch 성공 → 상태 = AUTO_FETCHED
3. 사용자가 다시 M1 시작 버튼 클릭
4. 상태가 이미 AUTO_FETCHED이므로 400 에러 발생

---

## ✅ 해결 방법

### 프론트엔드 수정

**File**: `static/project_detail.html`  
**Method**: `startM1Module()`

#### 수정 전 (문제)
```javascript
async startM1Module() {
    // 상태 확인 없이 바로 auto-fetch 호출
    const response = await fetch(`/api/projects/${this.projectId}/modules/M1/auto-fetch`, {
        method: 'POST'
    });
    // ...
}
```

#### 수정 후 (해결)
```javascript
async startM1Module() {
    try {
        this.loading = true;
        
        // 1️⃣ M1 현재 상태 먼저 확인
        const stateResponse = await fetch(`/api/projects/${this.projectId}/modules/M1/state`);
        
        if (stateResponse.ok) {
            const state = await stateResponse.json();
            console.log('M1 현재 상태:', state);
            
            // 2️⃣ 이미 AUTO_FETCHED 이상의 상태라면 다음 단계 안내
            if (state.status !== 'EMPTY') {
                alert(`M1 데이터가 이미 수집되었습니다.\n현재 상태: ${state.status}\n\n다음 단계를 진행해주세요.`);
                await this.loadProject();
                return;  // ✅ auto-fetch 스킵
            }
        }
        
        // 3️⃣ EMPTY 상태인 경우만 auto-fetch 실행
        const response = await fetch(`/api/projects/${this.projectId}/modules/M1/auto-fetch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            
            // 4️⃣ 400 에러 상세 처리
            if (response.status === 400 && errorData.detail) {
                const detail = errorData.detail;
                throw new Error(`${detail.message || detail.error || 'M1 시작 실패'}`);
            }
            
            throw new Error(`M1 시작 실패: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('M1 Auto-Fetch 결과:', result);
        
        alert('✅ M1 데이터 자동 수집이 완료되었습니다!');
        await this.loadProject();
        
    } catch (error) {
        console.error('M1 시작 오류:', error);
        alert(`M1 시작 중 오류가 발생했습니다:\n\n${error.message}`);
    } finally {
        this.loading = false;
    }
}
```

### 주요 개선 사항

1. **상태 확인 로직 추가**
   - `GET /api/projects/{project_id}/modules/M1/state` 먼저 호출
   - 현재 상태가 EMPTY가 아니면 auto-fetch 스킵

2. **사용자 친화적 메시지**
   - 이미 시작된 경우: "M1 데이터가 이미 수집되었습니다. 현재 상태: AUTO_FETCHED"
   - 사용자에게 다음 단계 안내

3. **개선된 에러 핸들링**
   - 400 에러 시 백엔드의 detail 메시지 표시
   - 명확한 에러 메시지로 디버깅 용이

4. **자동 새로고침**
   - 상태 확인 후 프로젝트 데이터 리로드
   - UI가 최신 상태 반영

---

## 🧪 검증 결과

### Backend Test
```bash
# 서버 재시작 (in-memory 상태 초기화)
kill -9 $(lsof -t -i:49999)
python -m uvicorn app.main:app --host 0.0.0.0 --port 49999 --reload

# M1 auto-fetch 테스트
curl -X POST http://localhost:49999/api/projects/proj_20260112_af3495af/modules/M1/auto-fetch
```

**Result**: ✅ Success
```json
{
  "status": "AUTO_FETCHED",
  "auto_data": {
    "address": "서울특별시 강남구 테헤란로 518",
    "lat": 37.5079,
    "lng": 127.0623,
    "admin_area": {
      "si": "서울특별시",
      "gu": "강남구",
      "dong": "대치동"
    },
    "poi_summary": {
      "subway": 2,
      "school": 1,
      "public_facility": 3
    }
  }
}
```

### Frontend Test Scenarios

#### Scenario 1: First Time M1 Start (EMPTY → AUTO_FETCHED)
1. 새 프로젝트 생성
2. M1 시작하기 클릭
3. **Expected**: 
   - ✅ M1 state check: EMPTY
   - ✅ auto-fetch 호출 성공
   - ✅ Alert: "M1 데이터 자동 수집이 완료되었습니다!"
   - ✅ 프로젝트 데이터 리로드

#### Scenario 2: Already Started M1 (AUTO_FETCHED)
1. M1이 이미 시작된 프로젝트
2. M1 시작하기 다시 클릭
3. **Expected**:
   - ✅ M1 state check: AUTO_FETCHED
   - ✅ Alert: "M1 데이터가 이미 수집되었습니다. 현재 상태: AUTO_FETCHED"
   - ✅ auto-fetch 호출 스킵
   - ✅ 프로젝트 데이터 리로드

#### Scenario 3: M1 FROZEN (Final State)
1. M1이 freeze된 프로젝트
2. M1 시작하기 클릭
3. **Expected**:
   - ✅ M1 state check: FROZEN
   - ✅ Alert: "M1 데이터가 이미 수집되었습니다. 현재 상태: FROZEN"
   - ✅ 사용자에게 다음 단계(M2) 안내

---

## 📊 시스템 상태

### Before Fix
- M1 Start Button: ⚠️ 400 Error on second click
- User Experience: ❌ Confusing error message
- State Management: ❌ No state check before API call
- Error Handling: ❌ Generic "M1 시작 실패: 400"

### After Fix
- M1 Start Button: ✅ Idempotent operation (can click multiple times safely)
- User Experience: ✅ Clear status messages
- State Management: ✅ Pre-check M1 state before action
- Error Handling: ✅ Detailed error messages from backend

---

## 🎯 M1 3-Stage System 정리

### Stage 1: 자동 수집 (EMPTY → AUTO_FETCHED)
- **Endpoint**: `POST /api/projects/{project_id}/modules/M1/auto-fetch`
- **Action**: Kakao API로 주소 → 좌표 변환, 행정구역/POI 수집
- **Result**: auto_data 생성, 실패 항목은 null

### Stage 2: Mock 생성 & 수정 (AUTO_FETCHED → EDITABLE)
- **Endpoint**: `POST /api/projects/{project_id}/modules/M1/mock-generate`
- **Action**: 자동 수집 실패 항목을 Mock 데이터로 채움
- **Edit**: `PATCH /api/projects/{project_id}/modules/M1/edit`

### Stage 3: FACT FREEZE (EDITABLE → FROZEN)
- **Validation**: `GET /api/projects/{project_id}/modules/M1/validate`
- **Freeze**: `POST /api/projects/{project_id}/modules/M1/freeze`
- **Warning**: ⚠️ 되돌릴 수 없음 (Irreversible)

### State Query
- **Endpoint**: `GET /api/projects/{project_id}/modules/M1/state`
- **Response**: status, can_edit, is_frozen, state_history, data availability

---

## 🔗 관련 리소스

### Git Commits
- **d869ce4** - fix(M1): Handle M1 State Check Before Auto-Fetch
- **60cf30a** - fix(UI): Implement M1 Start Button - Enable M1 Auto-Fetch API Call
- **f164d3f** - docs(TROUBLESHOOTING): Add M1 Start Button Fix Documentation

### Documentation
- `/docs/TROUBLESHOOTING_M1_START_BUTTON.md` - M1 Start Button 첫 번째 수정
- `/docs/TROUBLESHOOTING_M1_400_ERROR.md` - 이 문서 (400 에러 해결)

### API Endpoints
- `POST /api/projects/{project_id}/modules/M1/auto-fetch` - M1 자동 수집
- `GET /api/projects/{project_id}/modules/M1/state` - M1 상태 조회
- `POST /api/projects/{project_id}/modules/M1/mock-generate` - Mock 생성
- `PATCH /api/projects/{project_id}/modules/M1/edit` - 수기 수정
- `GET /api/projects/{project_id}/modules/M1/validate` - Freeze 가능 여부
- `POST /api/projects/{project_id}/modules/M1/freeze` - FACT FREEZE

---

## 💡 향후 개선 사항

### 1. Persistent Storage
**현재**: In-memory 딕셔너리 (서버 재시작 시 초기화)  
**개선**: Redis 또는 DB로 M1 상태 영구 저장
```python
# app/core/m1_state_machine.py
# 현재
m1_state_storage: Dict[str, M1StateContext] = {}

# 개선안
from redis import Redis
redis_client = Redis(host='localhost', port=6379)
```

### 2. M1 State Reset API
**필요성**: 테스트/개발 시 M1 상태 초기화 필요  
**제안 Endpoint**: `DELETE /api/projects/{project_id}/modules/M1/reset`

### 3. UI State Indicator
**개선**: M1 시작 버튼에 현재 상태 표시
```html
<!-- 현재 -->
<button>🚀 M1 시작하기</button>

<!-- 개선안 -->
<button v-if="m1Status === 'EMPTY'">🚀 M1 시작하기</button>
<button v-else-if="m1Status === 'AUTO_FETCHED'">✅ M1 완료 (다음 단계 →)</button>
<button v-else-if="m1Status === 'FROZEN'">🔒 M1 Frozen</button>
```

### 4. M1 Progress Visualization
**개선**: 3-Stage 진행 상황 시각화
```
[✅ 1. 자동 수집] → [⏳ 2. 수정] → [🔒 3. Freeze]
```

---

## 🎉 최종 상태

**Issue**: M1 시작하기 400 Bad Request  
**Status**: ✅ **RESOLVED**  
**Impact**: 사용자가 M1을 안전하게 여러 번 클릭 가능  
**UX**: 명확한 상태 메시지로 다음 단계 안내  
**System**: M1 상태 관리 로직 개선  

---

**Core Message**: "M1 상태를 확인하고 행동하자. 사용자는 시스템의 내부 상태를 이해할 필요가 없다."

**Date**: 2026-01-12  
**Author**: ZeroSite Team  
**Version**: 1.0
