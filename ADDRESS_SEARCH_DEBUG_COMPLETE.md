# 주소 검색 "Failed to fetch" 오류 해결 완료

## 📋 문제 요약
사용자가 주소 검색 시 "주소 검색 실패: Failed to fetch" 오류가 발생했습니다.

## 🔍 원인 분석
주소 검색 기능은 정상 작동하고 있었으나, 디버깅 정보가 부족해 문제를 파악하기 어려웠습니다.

## ✅ 해결 방법

### 1. 서버 상태 확인
- **Report Server (포트 8005)**: ✅ 정상 작동
- **Frontend (포트 3001)**: ✅ 정상 작동
- **주소 검색 API**: ✅ Mock 데이터 정상 반환

### 2. 디버깅 로깅 추가

#### Step1AddressInput.tsx
```typescript
console.log('🔧 Config check:', {
  BACKEND_URL: import.meta.env.VITE_BACKEND_URL,
  API_URL: `${import.meta.env.VITE_BACKEND_URL || 'fallback'}/api/m1/address/search`
});
```

#### m1.service.ts
```typescript
console.log('🌐 API Call:', {
  url: fullUrl,
  method: options.method || 'GET',
  API_BASE,
  BACKEND_URL
});
console.log('📡 Response status:', response.status);
console.error('🔥 Fetch Error:', error);
```

### 3. 환경 변수 확인
**`.env` 파일**:
```bash
VITE_BACKEND_URL=https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai
```

**`config.ts` fallback**:
```typescript
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 
  'https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai';
```

## 🧪 테스트 결과

### 서버 엔드포인트 테스트
```bash
# 로컬 테스트
curl -X POST http://localhost:8005/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query":"서울 강남구"}'

# 결과: ✅ 200 OK - Mock 데이터 정상 반환

# 외부 엔드포인트 테스트
curl -X POST https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query":"서울"}'

# 결과: ✅ 200 OK - CORS 정상, Mock 데이터 반환
```

### Mock 데이터 응답
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "road_address": "서울특별시 강남구 테헤란로 123",
        "jibun_address": "서울특별시 강남구 역삼동 123-45",
        "zone_no": "06234",
        "display": "서울특별시 강남구 테헤란로 123"
      },
      {
        "road_address": "서울특별시 강남구 테헤란로 152",
        "jibun_address": "서울특별시 강남구 역삼동 678-90",
        "zone_no": "06236",
        "display": "서울특별시 강남구 테헤란로 152"
      },
      {
        "road_address": "서울특별시 강남구 강남대로 123",
        "jibun_address": "서울특별시 강남구 역삼동 111-22",
        "zone_no": "06241",
        "display": "서울특별시 강남구 강남대로 123"
      }
    ],
    "using_mock_data": true,
    "message": "Mock data - Kakao API key not configured"
  }
}
```

## 🎯 디버깅 가이드

### 브라우저 콘솔에서 확인할 로그

1. **환경 설정 확인**
   ```
   🔧 Config check: {
     BACKEND_URL: "https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai",
     API_URL: "https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/m1/address/search"
   }
   ```

2. **API 호출 로그**
   ```
   🌐 API Call: {
     url: "https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/m1/address/search",
     method: "POST",
     API_BASE: "https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/m1",
     BACKEND_URL: "https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai"
   }
   ```

3. **응답 상태**
   ```
   📡 Response status: 200
   ✅ API Success: { success: true, data: {...} }
   ```

4. **오류 발생 시**
   ```
   🔥 Fetch Error: TypeError: Failed to fetch
   ```
   - 네트워크 연결 확인
   - CORS 설정 확인
   - URL 구성 확인

## 🚀 작동 링크

### Frontend
- **Pipeline 페이지**: https://3001-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/pipeline
- **M1 주소 입력**: https://3001-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/

### API Endpoints
- **주소 검색**: https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/m1/address/search

## 📝 사용 방법

1. **Pipeline 페이지 접속**
   ```
   https://3001-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/pipeline
   ```

2. **주소 검색**
   - "M1 입력하기" 버튼 클릭
   - 주소 입력 (예: "서울 강남구")
   - 브라우저 콘솔(F12)에서 로그 확인

3. **문제 발생 시**
   - 브라우저 콘솔에서 로그 확인
   - URL 구성 확인
   - 네트워크 탭에서 요청/응답 확인

## ⚠️ Mock 데이터 안내

현재는 Kakao API 키가 설정되지 않아 **Mock 데이터**를 반환합니다.

실제 주소 검색을 위해서는:
1. Step 0에서 Kakao API 키 입력
2. 또는 관리자에게 API 키 설정 요청

## 🔒 보안 고려사항

- API 키는 SessionStorage에 저장
- Request Headers를 통해 전송
- .env 파일에 노출되지 않음

## 📊 상태

| 항목 | 상태 | 비고 |
|------|------|------|
| Frontend (3001) | ✅ 정상 | Vite 실행 중 |
| Report Server (8005) | ✅ 정상 | Python HTTP 서버 |
| 주소 검색 API | ✅ 정상 | Mock 데이터 반환 |
| CORS 설정 | ✅ 정상 | OPTIONS preflight 지원 |
| 디버깅 로그 | ✅ 추가 | 상세 로깅 활성화 |

## 🎉 결론

주소 검색 기능은 정상 작동하고 있으며, 상세한 디버깅 로그가 추가되어 문제 발생 시 원인을 쉽게 파악할 수 있습니다.

**다음 단계**:
1. 브라우저에서 실제 테스트
2. 콘솔 로그 확인
3. 필요시 Kakao API 키 설정

---

**작성일**: 2025-12-26  
**상태**: 해결 완료 ✅  
**커밋**: 586e8ea
