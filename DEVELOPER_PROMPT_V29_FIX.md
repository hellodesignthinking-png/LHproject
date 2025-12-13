# ZeroSite v29.0 최종 수정 개발자 프롬프트

**작성일**: 2025-12-13  
**문제**: 용도지역/공시지가가 여전히 하드코드된 Fallback 값 사용  
**심각도**: 🔴 CRITICAL

---

## 🚨 발견된 문제

### 문제 1: Fallback 값이 실제 API 결과를 덮어씀
```javascript
// 📍 위치: public/dashboard.html Line 908-909
// ❌ 문제 코드:
zone_type: zoneType || "제3종일반주거지역",  // 😱 하드코드!
individual_land_price_per_sqm: officialLandPrice || 8500000,  // 😱 하드코드!

// ✅ 실제 API는 정상 작동:
// API 응답: {"zone_type": "준주거지역", "official_price": 22000000}
// 하지만 화면에는: "제3종일반주거지역", 10000000 표시 😡
```

### 문제 2: API 응답 체크 로직 오류
```javascript
// 📍 위치: public/dashboard.html Line 866, 887
// ❌ 현재 코드:
if (landPriceData.status === 'success' && landPriceData.official_price)
if (zoningData.status === 'success' && zoningData.zone_type)

// ⚠️ 문제: API는 'success' 필드를 반환하지만, 체크는 'status' 필드를 확인
// API 실제 응답:
{
  "success": true,           // ← 이걸 체크해야 함!
  "status": "success",       // ← 이것도 있음
  "official_price": 22000000,
  "zone_type": "준주거지역"
}
```

### 문제 3: HTML 미리보기도 동일한 문제
```javascript
// 📍 위치: public/dashboard.html Line 1145 (HTML preview handler)
// ❌ 동일한 하드코드 사용
```

---

## 🎯 해결 방법 (3단계)

### STEP 1: Fallback 값 제거 ✂️

**파일**: `public/dashboard.html`  
**위치**: Line 904-911

**Before:**
```javascript
// Step 4: Prepare final data with FALLBACK values
const data = {
    address: address,
    land_area_sqm: landAreaInput ? parseFloat(landAreaInput) : 660,
    zone_type: zoneType || "제3종일반주거지역",  // ❌ 삭제!
    individual_land_price_per_sqm: officialLandPrice || 8500000,  // ❌ 삭제!
    premium_factors: premiumFactors
};
```

**After:**
```javascript
// Step 4: Prepare final data (API values REQUIRED)
if (!officialLandPrice || !zoneType) {
    resultDiv.innerHTML = `
        <div class="bg-red-50 p-6 rounded-lg border-2 border-red-200">
            <i class="fas fa-exclamation-triangle text-4xl text-red-600 mb-3"></i>
            <p class="text-red-600 font-semibold">데이터 조회 실패</p>
            <p class="text-sm text-gray-600 mt-2">
                ${!officialLandPrice ? '개별공시지가를 조회할 수 없습니다.' : ''}
                ${!zoneType ? '용도지역을 확인할 수 없습니다.' : ''}
            </p>
        </div>
    `;
    progressDiv.classList.add('hidden');
    return;  // 중단!
}

const data = {
    address: address,
    land_area_sqm: landAreaInput ? parseFloat(landAreaInput) : 660,
    zone_type: zoneType,  // ✅ Fallback 제거!
    individual_land_price_per_sqm: officialLandPrice,  // ✅ Fallback 제거!
    premium_factors: premiumFactors
};
```

---

### STEP 2: API 응답 체크 로직 수정 🔧

**파일**: `public/dashboard.html`  
**위치**: Line 864-870, 885-891

**Before:**
```javascript
// Land Price API
if (landPriceResponse.ok) {
    const landPriceData = await landPriceResponse.json();
    if (landPriceData.status === 'success' && landPriceData.official_price) {  // ❌
        officialLandPrice = landPriceData.official_price;
        // ...
    }
}

// Zoning API
if (zoningResponse.ok) {
    const zoningData = await zoningResponse.json();
    if (zoningData.status === 'success' && zoningData.zone_type) {  // ❌
        zoneType = zoningData.zone_type;
        // ...
    }
}
```

**After:**
```javascript
// Land Price API
if (landPriceResponse.ok) {
    const landPriceData = await landPriceResponse.json();
    console.log('🏘️ Land Price Response:', landPriceData);  // 디버깅
    
    if (landPriceData.success && landPriceData.official_price) {  // ✅ 수정
        officialLandPrice = landPriceData.official_price;
        document.getElementById('progress-land-price').innerHTML = 
            `<i class="fas fa-check-circle mr-2 text-green-600"></i>개별공시지가: ${officialLandPrice.toLocaleString()}원/㎡ (${landPriceData.parsed_gu} ${landPriceData.parsed_dong})`;
    } else {
        document.getElementById('progress-land-price').innerHTML = 
            '<i class="fas fa-times-circle mr-2 text-red-600"></i>개별공시지가 조회 실패';
    }
}

// Zoning API
if (zoningResponse.ok) {
    const zoningData = await zoningResponse.json();
    console.log('🗺️ Zoning Response:', zoningData);  // 디버깅
    
    if (zoningData.success && zoningData.zone_type) {  // ✅ 수정
        zoneType = zoningData.zone_type;
        document.getElementById('progress-zoning').innerHTML = 
            `<i class="fas fa-check-circle mr-2 text-green-600"></i>용도지역: ${zoneType} (건폐율 ${zoningData.bcr_legal}%, 용적률 ${zoningData.far_legal}%)`;
    } else {
        document.getElementById('progress-zoning').innerHTML = 
            '<i class="fas fa-times-circle mr-2 text-red-600"></i>용도지역 조회 실패';
    }
}
```

---

### STEP 3: HTML 미리보기도 동일하게 수정 🔧

**파일**: `public/dashboard.html`  
**위치**: Line 1122-1179 (HTML preview event listener)

**수정 사항**: 위 STEP 1-2와 동일한 로직 적용

---

## 🧪 테스트 시나리오

### 테스트 1: 강남구 테헤란로 427
```
입력: "서울 강남구 테헤란로 427", 660㎡

기대 결과:
✅ 개별공시지가: 22,000,000원/㎡ (강남구 역삼동)
✅ 용도지역: 준주거지역 (건폐율 70%, 용적률 400%)
✅ 최종 평가액: 약 145억원

❌ 절대 안되는 것:
- 개별공시지가: 10,000,000원/㎡ 표시
- 용도지역: 제3종일반주거지역 표시
```

### 테스트 2: 마포구 월드컵북로 120
```
입력: "서울 마포구 월드컵북로 120", 660㎡

기대 결과:
✅ 개별공시지가: 15,000,000원/㎡ (마포구 상암동)
✅ 용도지역: 제2종일반주거지역 (건폐율 60%, 용적률 200%)
✅ 최종 평가액: 약 99억원

❌ 절대 안되는 것:
- 개별공시지가: 8,500,000원/㎡ 표시
- 용도지역: 제3종일반주거지역 표시
```

### 테스트 3: 송파구 잠실동 19-1
```
입력: "서울 송파구 잠실동 19-1", 660㎡

기대 결과:
✅ 개별공시지가: 18,000,000원/㎡ (송파구 잠실동)
✅ 용도지역: 제3종일반주거지역 (건폐율 50%, 용적률 250%)
✅ 최종 평가액: 약 119억원
```

### 테스트 4: 다른 주소로 2번 실행
```
1차: "서울 강남구 테헤란로 427" → 22M원/㎡, 준주거지역
2차: "서울 마포구 월드컵북로 120" → 15M원/㎡, 제2종일반주거지역

✅ 확인 사항: 두 결과가 명확히 다른지 확인
❌ 절대 안되는 것: 두 주소 모두 10M원/㎡, 제3종일반주거지역
```

---

## 📝 최종 체크리스트

### 코드 수정 체크리스트:
- [ ] Line 908-909: Fallback 값 제거
- [ ] Line 904-911: API 실패 시 에러 표시 + 중단
- [ ] Line 866: `landPriceData.status` → `landPriceData.success` 수정
- [ ] Line 887: `zoningData.status` → `zoningData.success` 수정
- [ ] Line 868-869: 상세 성공 메시지 (구/동 포함)
- [ ] Line 889-890: 상세 성공 메시지 (건폐율/용적률 포함)
- [ ] Line 1145 영역: HTML 미리보기에도 동일 수정
- [ ] console.log 추가 (디버깅용)

### 테스트 체크리스트:
- [ ] 브라우저 개발자 도구에서 console.log 확인
- [ ] 4개 주소 각각 다른 결과 확인
- [ ] "사용된 데이터" 섹션에 올바른 값 표시 확인
- [ ] PDF 다운로드 시 올바른 값 사용 확인
- [ ] HTML 미리보기 시 올바른 값 사용 확인

### Git 커밋 체크리스트:
- [ ] 수정 후 Git commit
- [ ] 커밋 메시지에 "fix(v29.0): Remove fallback hardcodes" 포함
- [ ] 서버 재시작
- [ ] 최종 테스트

---

## 🎯 예상 결과

### Before (현재 - 잘못됨):
```
주소: 서울 강남구 테헤란로 427
→ 개별공시지가: 10,000,000원/㎡  ❌ (하드코드 fallback)
→ 용도지역: 제3종일반주거지역  ❌ (하드코드 fallback)
```

### After (수정 후 - 올바름):
```
주소: 서울 강남구 테헤란로 427
→ 개별공시지가: 22,000,000원/㎡  ✅ (API에서 가져옴)
→ 용도지역: 준주거지역  ✅ (API에서 가져옴)
→ 파싱 정보: 강남구 역삼동  ✅
→ 건폐율/용적률: 70% / 400%  ✅
```

---

## 💡 핵심 포인트

### 1. **절대 규칙**: Fallback 금지!
```javascript
// ❌ 절대 안됨
const value = apiValue || hardcodedFallback;

// ✅ 올바름
if (!apiValue) {
    showError("API 조회 실패");
    return;
}
const value = apiValue;
```

### 2. API 응답 필드 정확히 체크
```javascript
// API 실제 응답 구조:
{
  "success": true,        // ← 이걸 체크!
  "status": "success",    // ← 참고용
  "official_price": 22000000,
  "zone_type": "준주거지역"
}
```

### 3. 사용자에게 명확한 피드백
```
✅ 성공: "개별공시지가: 22,000,000원/㎡ (강남구 역삼동)"
❌ 실패: "개별공시지가 조회 실패 - API 연동 오류"
```

---

## 🚀 실행 순서

1. **파일 백업**: `cp public/dashboard.html public/dashboard.html.backup`
2. **코드 수정**: 위 STEP 1-3 적용
3. **Git 커밋**: `git add . && git commit -m "fix(v29.0): Remove all fallback hardcodes"`
4. **서버 재시작**: `pkill python; sleep 2; python v24_1_server.py &`
5. **브라우저 테스트**: 4개 주소로 테스트
6. **결과 확인**: console.log + 화면 출력 확인

---

## ✅ 성공 기준

### 각 주소마다 다른 결과가 나와야 함:
- **강남 테헤란로**: 22M원/㎡, 준주거지역
- **마포 월드컵북로**: 15M원/㎡, 제2종일반주거지역
- **송파 잠실동**: 18M원/㎡, 제3종일반주거지역

### 같은 주소는 항상 같은 결과:
- 테헤란로 2번 실행 → 2번 모두 22M원/㎡, 준주거지역

### Fallback 값 절대 안 나옴:
- 10,000,000원/㎡ 절대 안 나와야 함
- 8,500,000원/㎡ 절대 안 나와야 함
- "제3종일반주거지역"만 나오면 안 됨

---

**이 프롬프트대로 수정하면 v29.0 완전 해결!** ✅

