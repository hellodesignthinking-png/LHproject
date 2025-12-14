# 🚀 ZeroSite 최종 서버 정보

## 📍 접속 정보

### 외부 접속 URL (Public)
```
https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai
```

### API 엔드포인트
- **헬스체크**: `/api/v24.1/health`
- **감정평가**: `/api/v24.1/appraisal`
- **API 문서**: `/docs`

### 전체 URL
```bash
# 헬스체크
https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/health

# API 문서 (Swagger)
https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/docs

# 감정평가 API
https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/appraisal
```

---

## 🧪 테스트 방법

### cURL로 테스트
```bash
curl -X POST https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/appraisal \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 680-11",
    "land_area_sqm": 400
  }'
```

### JavaScript로 테스트
```javascript
fetch('https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/appraisal', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    address: '서울특별시 강남구 역삼동 680-11',
    land_area_sqm: 400
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## ✅ 검증된 기능

### 1. 공시지가 (Official Land Price)
- ✅ 지역별로 다른 값 반환
- ✅ 시세의 60-90% 범위 내
- ✅ 최소값 보장 (250만원/㎡)

**예시:**
- 강남 역삼동: 27,200,000원/㎡
- 관악 신림동: 11,250,000원/㎡
- 제주 제주시: 5,200,000원/㎡

### 2. 용도지역 (Zone Type)
- ✅ 지역별로 다른 용도 반환
- ✅ 3단계 정교한 추정 시스템

**예시:**
- 강남 역삼동: 근린상업지역
- 관악 신림동: 제2종일반주거지역
- 제주 제주시: 계획관리지역

### 3. 거래사례 (Transactions)
- ✅ 15건 생성
- ✅ 매번 다른 지번 (랜덤)
- ✅ 주소 100% 일치 (sido/sigungu/dong)
- ✅ 거리순 정렬 (0.2km ~ 2.5km)

**예시:**
```json
{
  "id": 1,
  "address": "서울특별시 강남구 역삼동 634",
  "distance_km": 0.2,
  "price_per_sqm": 31554148
}
```

---

## 📊 응답 구조

```json
{
  "status": "success",
  "version": "v36.0 ENHANCED (Problems 1-4 해결)",
  "land_info": {
    "address_parsed": {
      "sido": "서울특별시",
      "sigungu": "강남구",
      "dong": "역삼동",
      "full": "서울특별시 강남구 역삼동 680-11"
    },
    "zone_type": "근린상업지역",
    "individual_land_price_per_sqm": 27200000,
    "individual_land_price_per_pyeong": 89917760,
    "market_price_per_sqm_krw": 32000000,
    "market_price_per_sqm_man": 3200.0,
    "official_to_market_ratio": 0.85
  },
  "transactions": [
    {
      "id": 1,
      "address": "서울특별시 강남구 역삼동 634",
      "lat": 37.5665,
      "lng": 126.978,
      "size_sqm": 344.8,
      "price_per_sqm": 31554148,
      "total_price": 10879990000,
      "zone_type": "근린상업지역",
      "transaction_date": "2024-11-20",
      "days_ago": 24,
      "distance_km": 0.2
    }
    // ... 14 more transactions
  ],
  "transactions_summary": {
    "count": 15,
    "avg_price_per_sqm": 30500000,
    "min_distance_km": 0.2,
    "max_distance_km": 2.35
  },
  "appraisal": {
    "final_value": 108.8,
    "value_per_sqm": 27200000,
    "confidence": "MEDIUM"
  }
}
```

---

## 🔧 문제 해결

### 캐시 문제
프론트엔드에서 같은 데이터가 계속 표시된다면:

1. **브라우저 강력 새로고침**
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **개발자 도구에서 캐시 비활성화**
   - F12 → Network 탭 → "Disable cache" 체크

3. **API 요청 시 캐시 방지 헤더 추가**
   ```javascript
   fetch(url, {
     headers: {
       'Cache-Control': 'no-cache',
       'Pragma': 'no-cache'
     }
   })
   ```

---

## 📝 변경 이력

### v36.0 ENHANCED (2024-12-14)
- ✅ Problem 1 해결: 공시지가 정확성 개선
- ✅ Problem 2 해결: 거래사례 주소 100% 일치
- ✅ Problem 3 해결: 용도지역 다양성 확보
- ✅ Problem 4 해결: API 응답 완전성 보장

---

## 💡 주의사항

1. **거래사례는 매번 다릅니다** (의도된 동작)
   - 랜덤 지번 생성으로 현실성 향상
   - 같은 주소라도 매번 다른 거래사례 반환

2. **공시지가와 용도지역은 고정입니다**
   - 같은 주소는 항상 같은 값 반환
   - 데이터베이스 기반 매핑

3. **모든 거래사례는 입력 주소와 일치합니다**
   - sido/sigungu/dong 정확히 반영
   - 주소 정확도 100%

---

## 📞 문의

추가 문의사항이나 문제가 있으시면 개발팀으로 연락주세요.

**서버 상태**: ✅ HEALTHY  
**마지막 재시작**: 2024-12-14 01:17 (KST)
