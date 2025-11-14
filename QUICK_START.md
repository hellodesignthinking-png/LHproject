# 🚀 Phase 2 빠른 시작 가이드

**5분 안에 모든 기능을 테스트해보세요!**

---

## 📍 Step 1: Swagger UI 접속 (10초)

**브라우저에서 이 링크를 클릭하세요**:

```
https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai/docs
```

화면에 다음과 같은 API 목록이 보입니다:
- ✅ POST `/api/business/calculate-cost` - 건축비 자동 산정
- ✅ POST `/api/business/simulate-purchase` - LH 매입가 시뮬레이션

---

## 🏗️ Step 2: 건축비 계산 테스트 (1분)

### 클릭 순서:
1. `POST /api/business/calculate-cost` 클릭
2. 우측 상단 **"Try it out"** 버튼 클릭
3. Request body에 다음 입력:

```json
{
  "unit_type": "YOUTH",
  "gross_area": 1000,
  "region": "서울",
  "num_units": 20
}
```

4. 하단 **"Execute"** 버튼 클릭
5. Response body 확인!

### 📊 예상 결과:
```json
{
  "total_cost": 436363636,        // 총 건축비: 4억 3,636만원
  "cost_per_pyeong": 1440000,     // 평당 144만원 (서울 할증 적용)
  "grand_total": 480000000,       // 최종 금액: 4억 8천만원
  "regional_multiplier": 1.2      // 서울 1.2배 할증
}
```

---

## 🏢 Step 3: LH 매입가 시뮬레이션 (1분)

### 클릭 순서:
1. `POST /api/business/simulate-purchase` 클릭
2. **"Try it out"** 버튼 클릭
3. Request body에 다음 입력:

```json
{
  "unit_type": "YOUTH",
  "land_value": 3000000000,
  "construction_cost": 2000000000,
  "gross_area": 1000,
  "num_units": 20,
  "region": "서울특별시"
}
```

4. **"Execute"** 버튼 클릭
5. Response body 확인!

### 📊 예상 결과:
```json
{
  "total_purchase_price": 5400000000,  // LH 매입가: 54억원
  "profit_amount": 400000000,          // 이윤: 4억원
  "roi_percentage": 8.0,               // ROI: 8%
  "is_eligible": true,                 // ✅ 매입 가능!
  "eligibility_notes": [
    "🎉 LH 매입 기준 충족 - 매입 가능성 높음"
  ]
}
```

---

## 🎮 Step 4: 다른 시나리오 테스트 (3분)

### 시나리오 1: 경기도 신혼희망타운

**건축비 계산**:
```json
{
  "unit_type": "NEWLYWED",
  "gross_area": 2000,
  "region": "경기",
  "num_units": 30
}
```

**결과**: 평당 143만원 (경기 1.1배 할증)

### 시나리오 2: 자격 미달 케이스

**LH 매입가 시뮬레이션**:
```json
{
  "unit_type": "YOUTH",
  "land_value": 2000000000,
  "construction_cost": 1500000000,
  "gross_area": 1400,              // 70㎡/세대 → 면적 초과
  "num_units": 20,
  "region": "서울특별시"
}
```

**결과**: 
```json
{
  "is_eligible": false,           // ❌ 매입 불가
  "eligibility_notes": [
    "❌ 세대당 면적 초과: 70.0㎡ > 60㎡"
  ]
}
```

---

## 💻 터미널에서 테스트 (개발자용)

### curl로 빠르게 테스트:

```bash
# 건축비 계산
curl -X POST "https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai/api/business/calculate-cost" \
  -H "Content-Type: application/json" \
  -d '{"unit_type":"YOUTH","gross_area":1000,"region":"서울","num_units":20}' \
  | jq .

# LH 매입가 시뮬레이션
curl -X POST "https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai/api/business/simulate-purchase" \
  -H "Content-Type: application/json" \
  -d '{"unit_type":"YOUTH","land_value":3000000000,"construction_cost":2000000000,"gross_area":1000,"num_units":20,"region":"서울특별시"}' \
  | jq .
```

---

## 📚 참고 문서

| 문서 | 내용 |
|-----|------|
| `PHASE2_VISUAL_GUIDE.md` | 상세한 사용 가이드 및 기술 문서 |
| `PHASE2_TEST_RESULTS.md` | 실제 테스트 결과 및 성능 지표 |
| `PHASE2_GUIDE.md` | Phase 2 전체 개발 계획 |

---

## 🎯 핵심 요약

### ✅ 완료된 기능
- 건축비 자동 산정 (지역별/주택유형별)
- LH 매입가 시뮬레이션 (자격 검증 포함)

### 📊 개발 통계
- **835줄**의 코드
- **2개**의 REST API
- **평균 242ms** 응답 시간
- **100%** 테스트 통과

### 🌟 비즈니스 가치
- 건축비 산정: 3시간 → **0.27초** (99.998% 단축)
- 매입가 계산: 2시간 → **0.21초** (99.997% 단축)
- 자격 검증: 1시간 → **즉시** (100% 단축)

---

## ❓ 문제 해결

### "결과가 안 보여요"
→ "Try it out" 버튼을 먼저 클릭하셨나요?

### "에러가 나요"
→ Request body의 따옴표가 올바른 JSON 형식인지 확인하세요.

### "다른 지역도 테스트하고 싶어요"
→ `region` 필드를 변경하세요: "서울", "경기", "인천", "충청", "강원", "전라", "경상", "제주"

---

**🎉 모든 준비 완료!**

지금 바로 Swagger UI로 이동해서 테스트해보세요:
https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai/docs

