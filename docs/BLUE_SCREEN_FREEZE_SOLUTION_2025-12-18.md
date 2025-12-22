# 🔵 파란색 화면 멈춤 현상 해결 가이드

**작성일**: 2025-12-18  
**대상**: "M1 Lock → 파이프라인 실행 중 파란색 화면에서 멈추는" 문제

---

## 📋 **문제 증상**

사용자가 M1 데이터 입력 완료 후 "🔒 토지 사실 확정 (M1 Lock)" 버튼을 클릭하면:
1. **파란색 로딩 화면**이 표시됨 (`stage === 'M1_FROZEN'`)
2. "🚀 M2→M6 파이프라인 실행 중..." 메시지 표시
3. **화면이 계속 멈춰있고 진행되지 않음**
4. 결과 화면으로 전환되지 않음

---

## 🔍 **근본 원인 분석**

### 1️⃣ **포트 충돌 (Primary Root Cause)**
- **설정**: `vite.config.ts`에서 `port: 3000` 지정
- **실제 실행**: 3000번 포트가 이미 사용 중이어서 **3001번으로 자동 fallback**
- **프록시 미적용**: 3001번에서 실행되면서 `/api` 프록시 설정이 제대로 작동하지 않음
- **백엔드 통신 실패**: 프론트엔드 → 백엔드 API 호출 실패 → 로딩 상태 지속

### 2️⃣ **백엔드 API 상태 (정상)**
```bash
# 테스트 결과
curl -X POST http://localhost:8005/api/v4/pipeline/analyze \
  -H "Content-Type: application/json" \
  -d '{"parcel_id": "116801010007370000", "use_cache": false}'

# 결과: {"status": "success", ...}  ✅ 정상 작동
```

**결론**: 백엔드는 정상이지만, **프론트엔드의 네트워크 요청이 백엔드에 도달하지 못함**

---

## ✅ **해결 방법**

### **Solution 1: 포트 정리 및 재시작 (권장)**

#### **Step 1: 기존 프로세스 종료**
```bash
# 모든 Node.js 프로세스 확인
ps aux | grep node

# 3000/3001번 포트 사용 프로세스 종료
kill -9 <PID_3000>
kill -9 <PID_3001>
```

#### **Step 2: 깨끗하게 재시작**
```bash
cd /home/user/webapp/frontend
PORT=3000 npm run dev
```

#### **Step 3: 확인**
```bash
# 포트 확인
netstat -tlnp | grep :3000

# 예상 출력:
# tcp  0  0  0.0.0.0:3000  0.0.0.0:*  LISTEN  <PID>/node
```

---

### **Solution 2: 프록시 우회 (임시 해결책)**

프론트엔드 코드에서 **절대 URL 사용**:

#### **수정 전**
```typescript
// frontend/src/components/pipeline/PipelineOrchestrator.tsx
const response = await fetch('/api/v4/pipeline/analyze', {
  method: 'POST',
  // ...
});
```

#### **수정 후**
```typescript
// ⚠️ 임시: 프록시를 우회하고 직접 백엔드 호출
const BACKEND_URL = 'http://localhost:8005';
const response = await fetch(`${BACKEND_URL}/api/v4/pipeline/analyze`, {
  method: 'POST',
  // ...
});
```

⚠️ **주의**: 이 방법은 **개발 환경에서만 사용**하고, **배포 시 제거**해야 합니다.

---

### **Solution 3: Vite 프록시 디버깅**

`vite.config.ts` 수정:
```typescript
export default defineConfig({
  server: {
    port: 3000,
    strictPort: true,  // ⭐ 추가: 3000번이 사용 중이면 에러 발생
    proxy: {
      '/api': {
        target: 'http://localhost:8005',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          // ⭐ 디버깅 로그 추가
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('🔀 Proxying:', req.method, req.url, '→', options.target + req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('✅ Proxy response:', proxyRes.statusCode, req.url);
          });
          proxy.on('error', (err, req, res) => {
            console.error('❌ Proxy error:', err.message, req.url);
          });
        }
      }
    }
  }
});
```

---

## 🧪 **테스트 절차**

### **1. 백엔드 API 직접 테스트**
```bash
# Step 1: Context 생성
curl -X POST http://localhost:8005/api/m1/freeze-context-v2 \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 737",
    "coordinates": {"lat": 37.5012, "lon": 127.0396},
    "bonbun": "737",
    "jimok": "대",
    "area": 500,
    "zone_type": "제2종일반주거지역",
    "far": 250,
    "bcr": 60,
    "road_width": 25,
    "official_land_price": 15000000,
    "cadastral_source": "MANUAL",
    "zoning_source": "MANUAL",
    "road_source": "MANUAL",
    "official_price_source": "MANUAL"
  }'

# 출력: {"parcel_id": "116801010007370000", ...}

# Step 2: 파이프라인 실행
curl -X POST http://localhost:8005/api/v4/pipeline/analyze \
  -H "Content-Type: application/json" \
  -d '{"parcel_id": "116801010007370000", "use_cache": false}'

# 예상 출력: {"status": "success", "results": {...}}
```

✅ **백엔드가 정상이면** → 프론트엔드 프록시 문제  
❌ **백엔드가 실패하면** → 백엔드 수정 필요

---

### **2. 프론트엔드 네트워크 디버깅**

브라우저 개발자 도구 → Network 탭:
1. **M1 Lock 버튼 클릭**
2. `/api/v4/pipeline/analyze` 요청 확인
3. **Status Code 확인**:
   - `200 OK` → 성공
   - `404 Not Found` → 프록시 미작동
   - `(pending)` 또는 `(cancelled)` → 요청 전송 실패
   - CORS 에러 → 백엔드 CORS 설정 확인

---

## 🎯 **현재 상태 (2025-12-18 해결 완료)**

### ✅ **적용된 해결책**
1. **기존 프로세스 종료**: 3000번/3001번 Node.js 프로세스 모두 종료
2. **깨끗한 재시작**: `PORT=3000 npm run dev`로 정확히 3000번에서 실행
3. **프록시 정상 작동 확인**: `/api` → `http://localhost:8005` 프록시 활성화

### 🔗 **새로운 접속 URL**
```
https://3000-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/pipeline
```

### 📊 **동작 확인**
- M1 데이터 입력 → M1 Lock → 파이프라인 실행 → **결과 화면 정상 표시** ✅
- 평균 실행 시간: **약 1-2초**

---

## 📝 **추가 개선 사항**

### **1. Mock 데이터 사용자 검증 모드**
`ReviewScreen.tsx`에서 추가된 기능:
- **체크박스 검증**: 각 섹션(지적, 법적, 도로, 시장)에 "이 Mock 데이터를 검증하고 사용합니다" 체크박스
- **M1 Lock 조건**: Mock 데이터 사용 시 **모든 체크박스 체크** 필수
- **대안 제공**: PDF 업로드 또는 수동 입력 가능

### **2. 에러 처리 개선**
`PipelineOrchestrator.tsx`:
- **상세한 에러 메시지**: 백엔드 에러를 파싱하여 사용자에게 표시
- **재시도 버튼**: 실패 시 "🔄 다시 시도" 버튼 제공
- **새로운 분석 시작**: "🆕 새로운 분석 시작" 버튼으로 M1부터 재시작

---

## 🚀 **사용자 워크플로우 (API 없이 전체 파이프라인 실행)**

### **시나리오: VWorld/Data.go.kr API 차단 상황**

#### **Option 1: Mock 데이터 검증 모드** ⭐ **추천**
1. **Step 0**: "Mock 데이터로 진행" 클릭
2. **Step 1**: "서울 강남구" 검색 → 주소 선택
3. **Step 2**: 좌표 자동 표시 → 확인
4. **Step 3 (Review)**:
   - Mock 데이터가 자동으로 표시됨
   - **각 섹션의 체크박스 체크** ✅ (4개)
   - "🔒 토지 사실 확정 (M1 Lock)" 버튼 활성화
5. **M1 Lock 클릭** → 파이프라인 자동 실행 → 결과 확인

#### **Option 2: PDF 업로드**
1. **Step 0**: "PDF 업로드 방식 선택"
2. 공시지가확인서 또는 토지대장 PDF 업로드
3. 자동 파싱 → 데이터 검토 → M1 Lock → 파이프라인 실행

#### **Option 3: 수동 입력**
1. **Step 0**: "API 키 없이 수동 입력"
2. 각 필드를 하나씩 직접 입력 (지번, 면적, 지목, 용도지역, 도로 폭, 공시지가 등)
3. 거래사례도 `TransactionEditor` 컴포넌트로 직접 입력
4. M1 Lock → 파이프라인 실행

---

## 📚 **관련 문서**

- **Mock 데이터 검증 모드**: `/docs/PRACTICAL_SOLUTIONS_NO_API_2025-12-18.md`
- **거래사례 직접 입력 가이드**: `/docs/TRANSACTION_MANUAL_INPUT_GUIDE_2025-12-18.md`
- **API 키 차단 해결 가이드**: `/docs/API_KEY_BLOCKING_SOLUTION_2025-12-18.md`

---

## 🔴 **최종 결론**

### **문제**: 포트 충돌로 인한 프록시 미작동 → 백엔드 통신 실패 → 로딩 화면 멈춤
### **해결**: 3000번 포트로 깨끗하게 재시작 → 프록시 정상 작동 → 파이프라인 실행 성공 ✅
### **추가**: Mock 데이터 검증 모드로 **API 없이도 전체 파이프라인 실행 가능**

---

**작성자**: ZeroSite Development Team  
**최종 업데이트**: 2025-12-18 04:35 UTC
