# Frontend 디버깅 가이드 - [object Object] 오류 해결

## 🎯 현재 상태

**Frontend URL**: https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/v9/
**문제**: "분석시작" 버튼 클릭 시 `[object Object]` 오류 발생
**해결**: 에러 핸들링 개선 완료 ✅

---

## 🔍 디버깅 방법 (브라우저에서)

### 1단계: Chrome DevTools 열기

1. Frontend URL 접속
2. **F12** 키 또는 **우클릭 → 검사**
3. **Console** 탭과 **Network** 탭 준비

### 2단계: 분석 실행

1. 토지 정보 입력:
   - 주소: `서울특별시 강남구 테헤란로 123`
   - 토지면적: `1000` (m²)
   - 용도지역: `제3종일반주거지역`
   - 계획세대수: `80`

2. **"분석시작"** 버튼 클릭

### 3단계: Console 로그 확인

에러가 발생하면 다음 로그들이 표시됩니다:

```
📤 Sending API request: {
  address: "서울특별시 강남구 테헤란로 123",
  land_area: 1000,
  zone_type: "제3종일반주거지역",
  land_appraisal_price: NaN,  ← 🔥 이게 NaN이면 문제!
  unit_count: 80,
  ...
}

🔍 landData: {
  address: "...",
  land_area_m2: 1000,
  land_price_100m: undefined,  ← 🔥 undefined면 문제!
  ...
}

❌ API Error: API 오류 (422): 입력값 오류: body.land_appraisal_price: field required
```

### 4단계: Network 탭 확인

1. **Network** 탭 클릭
2. `analyze-land` 요청 찾기
3. 클릭하여 상세 확인:

   **Request Payload** (보낸 데이터):
   ```json
   {
     "address": "서울특별시 강남구 테헤란로 123",
     "land_area": 1000,
     "land_appraisal_price": null,  ← 🔥 문제!
     "unit_count": 80
   }
   ```

   **Response** (받은 응답):
   ```json
   {
     "detail": [
       {
         "loc": ["body", "land_appraisal_price"],
         "msg": "field required"
       }
     ]
   }
   ```

---

## 🔥 예상되는 원인 & 해결책

### 원인 1: 토지가격 필드가 비어있음

**증상**:
```
land_appraisal_price: NaN
land_price_100m: undefined
```

**해결책**:
토지가격(억원) 필드에 값 입력:
- 예: `100` (100억원)

---

### 원인 2: 토지면적이 0 또는 비어있음

**증상**:
```
land_area: 0
land_appraisal_price: Infinity
```

**해결책**:
토지면적 필드에 유효한 값 입력:
- 예: `1000` (1000m²)

---

### 원인 3: API 엔드포인트 오류 (500 Internal Server Error)

**증상**:
```
API 오류 (500): Internal Server Error
```

**해결책**:
서버 로그 확인 필요:
```bash
cd /home/user/webapp
tail -50 server.log
```

---

## 📋 체크리스트

디버깅 시 다음을 확인하세요:

- [ ] **Console 탭**: `📤 Sending API request` 로그 확인
- [ ] **landData 값**: 모든 필드가 undefined가 아닌지 확인
- [ ] **apiPayload 값**: NaN, null, undefined 없는지 확인
- [ ] **Network 탭**: Request Payload 내용 확인
- [ ] **Response 탭**: 정확한 에러 메시지 확인
- [ ] **Status Code**: 200, 422, 500 등 확인

---

## 🎯 정확한 에러 정보 수집 방법

아래 정보를 제공해주시면 즉시 해결 가능합니다:

### 1. Console 로그
```
📤 Sending API request: {...}
🔍 landData: {...}
```

### 2. Network Response
```json
{
  "detail": "..."
}
```

### 3. Status Code
```
422 Unprocessable Entity
또는
500 Internal Server Error
```

---

## ✅ 해결 확인

정상 작동 시 다음과 같이 표시됩니다:

### Console:
```
📤 Sending API request: {
  address: "서울특별시 강남구 테헤란로 123",
  land_area: 1000,
  land_appraisal_price: 10000000,  ✅ 정상
  unit_count: 80,
  ...
}

✅ Analysis completed successfully
```

### 화면:
- 로딩 애니메이션 → 결과 표시
- GIS 분석, 재무 분석, LH 평가, 리스크 평가 탭 활성화

---

## 🚀 개선된 에러 메시지

이제 `[object Object]` 대신 명확한 메시지가 표시됩니다:

### Before:
```
❌ 오류 발생
[object Object]
```

### After:
```
❌ 오류 발생
API 오류 (422): 입력값 오류: body.land_appraisal_price: field required
```

또는

```
❌ 오류 발생
API 오류 (500): Internal Server Error
TypeError: cannot convert float infinity to integer
```

---

## 📞 추가 지원

위 방법으로도 해결되지 않으면:

1. Console 전체 로그 캡처
2. Network 탭 스크린샷
3. 입력한 값들 공유

위 3가지를 제공해주시면 즉시 해결해드립니다!

---

**Updated**: 2025-12-04
**Status**: ✅ Enhanced Error Handling Applied
