# 🔥 FINAL REPAIR PROGRESS - ZeroSite M2-M6 (2025-12-19)

## 📋 사용자 요구사항 (User's Final Diagnosis)

**핵심 판단**: "코드는 많이 고쳐졌지만, 실제 사용자 체감 결과물은 아직 완성 단계가 아니다"

### 🔴 A. 화면 요약 카드 ↔ 실제 데이터 불일치 (여전히 존재)
- M2: 신뢰도 0% (거래사례 10건, 금액은 계산됨)
- M3: 점수 0점 (청년형 추천은 정상, 신뢰도 85%)
- M4: Legal FAR / Incentive FAR가 "세대수"로 표시, Alt A/B 주차 0대 고정, PDF 다운로드 실패
- M6: 카드 85.0/110점, 승인가능성 77% (PDF 내부 일부 불일치 가능성)

### 🔴 B. PDF 디자인 / 레이아웃 문제
- 모듈별 디자인 통일 X
- 표 간격/폰트 크기 들쭉날쭉
- 숫자 정렬 불량
- 의미 없는 장식 텍스트 (세로로 깨지는 ZERO SITE 등)
- "요약 → 근거 → 해석" 구조가 없음

### 🔴 C. M4 건축규모 PDF 다운로드 오류
- M4 PDF 파일은 서버 어딘가 생성됨
- 하지만 프론트 다운로드 버튼이 실패
- 원인 후보: endpoint 경로 불일치, Content-Type/Content-Disposition 누락, base URL 혼선 (8000/8005), blob 처리 누락

### 🔴 D. M6 심사예측 데이터 연동 구조가 아직 위험함
- summary는 `final_score`
- 본문은 `scores.total` 또는 `weighted_score`
- 표지/요약/본문이 서로 다른 변수를 읽음

---

## ✅ COMPLETED TASKS (지금까지 완료된 작업)

### 1️⃣ 프론트엔드 구조 파악 ✅
**Status**: COMPLETE
**Files**: 
- `/home/user/webapp/frontend/src/components/pipeline/PipelineOrchestrator.tsx` (파이프라인 오케스트레이터, M2-M6 요약 카드)
- `/home/user/webapp/frontend/src/components/pipeline/M4ResultsDisplay.tsx` (M4 상세 결과 화면)

**Findings**:
- `ModuleResultCard` 컴포넌트가 각 모듈의 요약 카드를 렌더링
- 기존 코드는 `m2Result.appraisal.land_value`, `m4Result.legal_capacity.total_units` 등 raw 필드를 직접 참조
- 0 값은 그대로 표시되어 "0세대", "0%", "0점" 문제 발생

### 2️⃣ 백엔드 데이터 계약 완전 통일 ✅
**Status**: COMPLETE
**Files**:
- `/home/user/webapp/app/api/endpoints/pipeline_reports_v4.py` (파이프라인 API 엔드포인트)
- `/home/user/webapp/app/core/canonical_data_contract.py` (이미 존재하는 데이터 계약)

**Changes**:
- `pipeline_result_to_dict()` 함수 수정: 모든 모듈 결과를 canonical format으로 변환
- M2: `convert_m2_to_standard()` 사용
- M3: `convert_m3_to_standard()` 사용
- M4: `M4Summary(legal_units, incentive_units, parking_alt_a, parking_alt_b)` 생성
- M5: `M5Summary(npv_public_krw, irr_pct, roi_pct, grade)` 생성
- M6: `convert_m6_to_standard()` 사용

**Result**:
```json
{
  "appraisal": {
    "module": "M2",
    "summary": {
      "land_value_total_krw": 1621848717,
      "pyeong_price_krw": 10723014,
      "confidence_pct": 85,
      "transaction_count": 10
    },
    "details": { ... }
  },
  "housing_type": {
    "module": "M3",
    "summary": {
      "recommended_type": "청년형",
      "total_score": 85,
      "confidence_pct": 85
    },
    "details": { ... }
  },
  "capacity": {
    "module": "M4",
    "summary": {
      "legal_units": 20,
      "incentive_units": 26,
      "parking_alt_a": 18,
      "parking_alt_b": 20
    },
    "details": { ... }
  },
  "feasibility": {
    "module": "M5",
    "summary": {
      "npv_public_krw": 793000000,
      "irr_pct": 12.8,
      "roi_pct": 15.5,
      "grade": "A"
    },
    "details": { ... }
  },
  "lh_review": {
    "module": "M6",
    "summary": {
      "decision": "GO",
      "total_score": 85.0,
      "max_score": 110,
      "grade": "A",
      "approval_probability_pct": 77
    },
    "details": { ... }
  }
}
```

### 3️⃣ 프론트엔드 요약 카드 수정 ✅
**Status**: COMPLETE
**Files**:
- `/home/user/webapp/frontend/src/components/pipeline/M4ResultsDisplay.tsx`
- `/home/user/webapp/frontend/src/components/pipeline/PipelineOrchestrator.tsx`

**Changes**:
- **M2 카드**: `summary.land_value_total_krw`, `summary.confidence_pct`, `summary.pyeong_price_krw`, `summary.transaction_count` 사용
- **M3 카드**: `summary.recommended_type`, `summary.total_score`, `summary.confidence_pct` 사용
- **M4 카드**: `summary.legal_units`, `summary.incentive_units`, `summary.parking_alt_a`, `summary.parking_alt_b` 사용
  - "Legal FAR" → "법정 세대수"
  - "Incentive FAR" → "인센티브 세대수"
- **M5 카드**: `summary.npv_public_krw`, `summary.irr_pct`, `summary.grade`, `summary.roi_pct` 사용
- **M6 카드**: `summary.decision`, `summary.total_score`, `summary.grade`, `summary.approval_probability_pct` 사용

**Zero Value Handling**:
```javascript
// BEFORE:
value: `${m4Result.legal_capacity?.total_units || 0}세대`  // Shows "0세대"

// AFTER:
value: m4Result.summary?.legal_units 
  ? `${m4Result.summary.legal_units}세대` 
  : 'N/A (검증 필요)'  // Shows "N/A (검증 필요)"
```

### 4️⃣ 커밋 및 푸시 ✅
**Status**: COMPLETE
**Commit**: `493b8aa` - "feat(DataContract): Enforce summary/details separation for M2-M6"
**Branch**: `feature/expert-report-generator`

---

## ⏳ REMAINING TASKS (남은 작업)

### 🔴 1. M4 PDF 다운로드 오류 수정 (HIGH PRIORITY)
**Status**: PENDING
**Target**: Frontend + Backend

**Frontend 수정 필요**:
```typescript
// 현재 프론트엔드에서 M4 PDF 다운로드 버튼 찾기
// blob 처리 로직 추가
const downloadM4PDF = async (reportId: string) => {
  const response = await fetch(`/api/v4/reports/m4/pdf?report_id=${reportId}`);
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `M4_건축규모_분석보고서_${new Date().toISOString().split('T')[0]}.pdf`;
  a.click();
};
```

**Backend 확인 필요**:
```python
# /app/routers/pdf_download_standardized.py 확인
# Content-Type: application/pdf
# Content-Disposition: attachment; filename="..."
```

### 🔴 2. M6 Single Source of Truth 완전 관철 (HIGH PRIORITY)
**Status**: PENDING
**Target**: PDF Generator

**수정 필요 파일**: `/home/user/webapp/app/services/pdf_generators/module_pdf_generator.py`

**Current Issues**:
- PDF 표지: `data.get('total_score')` 사용 가능
- PDF 요약: `data.get('scores', {}).get('total')` 사용 가능
- PDF 본문: `data.get('weighted_score')` 사용 가능

**Required Fix**:
```python
def generate_m6_lh_review_pdf(data: Dict[str, Any], ...):
    # 🔥 SINGLE SOURCE OF TRUTH
    summary = data.get('summary', {})
    total_score = summary.get('total_score')  # ONLY source
    
    # 표지에서 사용
    cover_score = total_score
    
    # 요약에서 사용
    summary_score = total_score
    
    # 본문에서 사용
    body_score = total_score
    
    # 레이더 차트에서 사용
    chart_total = total_score
```

### 🔴 3. PDF 디자인 시스템 통일 (MEDIUM PRIORITY)
**Status**: PENDING
**Target**: PDF Generator

**Required**: Apply `/home/user/webapp/app/services/pdf_generators/report_theme.py` (already exists!)

**Changes**:
```python
from app.services.pdf_generators.report_theme import ZeroSiteTheme

theme = ZeroSiteTheme()

# 표지
story.append(theme.create_cover_page(title, subtitle))

# 섹션 헤더
story.append(theme.create_section_header("1. 감정평가 요약"))

# 표
story.append(theme.create_data_table(data, headers))

# 차트
story.append(theme.create_chart_placeholder(chart_img))
```

---

## 📊 PROGRESS SUMMARY

| Task | Status | Priority | ETA |
|------|--------|----------|-----|
| 프론트엔드 구조 파악 | ✅ COMPLETE | HIGH | - |
| 백엔드 데이터 계약 통일 | ✅ COMPLETE | HIGH | - |
| 프론트엔드 요약 카드 수정 | ✅ COMPLETE | HIGH | - |
| 커밋 및 푸시 | ✅ COMPLETE | HIGH | - |
| M4 PDF 다운로드 오류 수정 | ⏳ PENDING | HIGH | 30min |
| M6 Single Source of Truth | ⏳ PENDING | HIGH | 20min |
| PDF 디자인 시스템 통일 | ⏳ PENDING | MEDIUM | 45min |
| 최종 통합 테스트 | ⏳ PENDING | HIGH | 30min |

**Total Completed**: 4/8 tasks (50%)  
**Total Remaining**: 4/8 tasks (50%)  
**Estimated Time to Complete**: ~2 hours

---

## 🎯 EXPECTED RESULTS AFTER ALL TASKS COMPLETE

### Before Fix:
```
화면 카드:
- M2 신뢰도: 0%
- M3 점수: 0점
- M4: Legal FAR 0세대, Alt A 0대
- M6: 85.0/110점 (일부 불일치)

PDF:
- 디자인 통일 X
- 표 간격 들쭉날쭉
- M6 점수 불일치 (0.0 vs 85.0)
- M4 다운로드 실패
```

### After Fix:
```
화면 카드:
- M2 신뢰도: 85% (또는 N/A)
- M3 점수: 85점 (또는 N/A)
- M4: 법정 세대수 20세대, Alt A 18대 (또는 N/A)
- M6: 85.0/110점 (완전 일치)

PDF:
- 통일된 디자인 (NanumBarunGothic, 동일한 표 스타일)
- M6 점수 100% 일치 (표지/요약/본문 모두 85.0/110)
- M4 다운로드 성공
- 명확한 '요약 → 근거 → 해석' 구조
```

---

## 📞 NEXT STEPS

1. **Immediate**: M4 PDF 다운로드 수정 (30min)
2. **Immediate**: M6 SSOT 관철 (20min)
3. **Follow-up**: PDF 디자인 통일 (45min)
4. **Final**: 통합 테스트 및 최종 커밋 (30min)

**Total ETA**: ~2 hours for complete fix

---

**Generated**: 2025-12-19  
**Status**: IN PROGRESS (50% complete)  
**Next Action**: M4 PDF download fix
