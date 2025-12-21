# 프론트엔드 통합 가이드 - ZeroSite M2~M6 데이터 연동 수정

**작성일:** 2025-12-19  
**대상:** 프론트엔드 개발자  
**목적:** 백엔드 표준화에 맞춰 프론트엔드 카드/다운로드 로직 수정

---

## 🎯 해결할 문제 (현재 상태)

### 현재 문제점
1. **M2 카드**: 신뢰도 0% (실제 거래사례 10건 있음)
2. **M3 카드**: 점수 0점 (추천유형은 보임)
3. **M4 다운로드**: 실패 (404 또는 타임아웃)
4. **M6 불일치**: 화면에서 0.0/110 vs 85.0/110 동시 표시

### 원인
- 프론트엔드가 백엔드 데이터 구조를 일관되지 않게 읽음
- `confidence.score` vs `confidence_score` vs `reliability.score` 등 여러 키 혼재
- PDF 다운로드 URL/헤더 표준화 안 됨

---

## ✅ 백엔드 변경사항 (완료)

### 1. 표준 데이터 계약 생성
**파일:** `app/core/canonical_data_contract.py`

모든 모듈이 이제 다음 구조를 반환합니다:

```python
{
    "module": "M2|M3|M4|M5|M6",
    "context_id": "...",
    "summary": {
        # 프론트엔드 카드가 읽을 필드 (표준화됨)
    },
    "details": {
        # PDF에서 사용할 상세 데이터
    },
    "meta": {...}
}
```

### 2. M2~M6 Summary 필드 정의

#### M2 Summary
```typescript
interface M2Summary {
    land_value_total_krw: number;     // 1621848717 (정수)
    pyeong_price_krw: number;          // 10723014 (정수)
    confidence_pct: number;             // 85 (0-100 정수)
    transaction_count: number;          // 10
}
```

#### M3 Summary
```typescript
interface M3Summary {
    recommended_type: string;           // "청년형"
    total_score: number;                // 85 (0-100 정수)
    confidence_pct: number;             // 85 (0-100 정수)
    second_choice?: string;             // "신혼부부형" (옵션)
}
```

#### M4 Summary
```typescript
interface M4Summary {
    legal_units: number;                // 20
    incentive_units: number;            // 26
    parking_alt_a?: number;             // 18 (옵션)
    parking_alt_b?: number;             // 20 (옵션)
}
```

#### M5 Summary
```typescript
interface M5Summary {
    npv_public_krw: number;             // 793000000
    irr_pct: number;                    // 12.8
    roi_pct: number;                    // 15.5
    grade: string;                      // "A"
}
```

#### M6 Summary (중요!)
```typescript
interface M6Summary {
    decision: "GO" | "NO-GO" | "CONDITIONAL";
    total_score: number;                // 85.0 (동일 값)
    max_score: number;                  // 110
    grade: "A" | "B" | "C" | "D";
    approval_probability_pct: number;   // 77 (0-100 정수)
}
```

### 3. PDF 다운로드 엔드포인트 표준화
**파일:** `app/routers/pdf_download_standardized.py`

**새로운 표준 URL:**
```
GET /api/v4/reports/{module}/pdf?context_id={id}
```

예:
```
GET /api/v4/reports/M4/pdf?context_id=abc123
```

**응답 헤더 (표준화):**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="M4_건축규모결정_보고서_2025-12-19.pdf"
Content-Length: 171732
```

---

## 🔧 프론트엔드 수정 작업 (필수)

### 1. 모듈 카드 컴포넌트 수정

#### AS-IS (문제 있는 코드)
```typescript
// M2 Card (문제: 여러 키 시도, 일관성 없음)
const M2Card = ({ data }) => {
  const confidence = data.confidence?.score || data.trust_score || 0; // ❌
  const landValue = data.appraisal?.land_value || 0;
  
  return (
    <Card>
      <div>신뢰도: {confidence * 100}%</div>  {/* ❌ 0-1 → 0-100 변환 */}
      <div>토지가치: ₩{landValue.toLocaleString()}</div>
    </Card>
  );
};

// M3 Card (문제: score 키가 없음)
const M3Card = ({ data }) => {
  const score = data.score || 0;  // ❌ score 키 없음
  return <div>점수: {score}점</div>;
};
```

#### TO-BE (수정된 코드)
```typescript
// 모든 모듈 카드가 summary만 읽도록 통일
interface ModuleResult {
  module: string;
  context_id: string;
  summary: any;  // 모듈별 타입 정의 필요
  details: any;
}

const M2Card = ({ data }: { data: ModuleResult }) => {
  const { summary } = data;  // ✅ summary만 읽기
  
  return (
    <Card>
      <CardItem 
        label="토지가치" 
        value={`₩${summary.land_value_total_krw.toLocaleString()}원`} 
      />
      <CardItem 
        label="평당가격" 
        value={`₩${summary.pyeong_price_krw.toLocaleString()}원`} 
      />
      <CardItem 
        label="신뢰도" 
        value={`${summary.confidence_pct}%`}  // ✅ 이미 0-100 정수
      />
      <CardItem 
        label="거래사례" 
        value={`${summary.transaction_count}건`} 
      />
    </Card>
  );
};

const M3Card = ({ data }: { data: ModuleResult }) => {
  const { summary } = data;
  
  return (
    <Card>
      <CardItem 
        label="추천유형" 
        value={summary.recommended_type} 
      />
      <CardItem 
        label="종합점수" 
        value={`${summary.total_score}점`}  // ✅ 이미 0-100 정수
      />
      <CardItem 
        label="신뢰도" 
        value={`${summary.confidence_pct}%`} 
      />
      {summary.second_choice && (
        <CardItem 
          label="차선책" 
          value={summary.second_choice} 
        />
      )}
    </Card>
  );
};

const M4Card = ({ data }: { data: ModuleResult }) => {
  const { summary } = data;
  
  return (
    <Card>
      <CardItem 
        label="법정용적률" 
        value={`${summary.legal_units}세대`} 
      />
      <CardItem 
        label="인센티브" 
        value={`${summary.incentive_units}세대`} 
      />
      <CardItem 
        label="주차(대안A)" 
        value={summary.parking_alt_a ? `${summary.parking_alt_a}대` : '미확정'} 
      />
      <CardItem 
        label="주차(대안B)" 
        value={summary.parking_alt_b ? `${summary.parking_alt_b}대` : '미확정'} 
      />
    </Card>
  );
};

const M6Card = ({ data }: { data: ModuleResult }) => {
  const { summary } = data;
  
  return (
    <Card>
      <CardItem 
        label="최종판정" 
        value={<Badge type={summary.decision}>{summary.decision}</Badge>} 
      />
      <CardItem 
        label="종합점수" 
        value={`${summary.total_score}/${summary.max_score}점`}  // ✅ 단일 소스
      />
      <CardItem 
        label="등급" 
        value={<Badge>{summary.grade}</Badge>} 
      />
      <CardItem 
        label="승인가능성" 
        value={`${summary.approval_probability_pct}%`} 
      />
    </Card>
  );
};
```

---

### 2. PDF 다운로드 함수 수정

#### AS-IS (문제 있는 코드)
```typescript
// 문제: 포트 하드코딩, 잘못된 경로, blob 처리 없음
const downloadM4PDF = async (contextId: string) => {
  const url = `http://localhost:8000/report/m4?id=${contextId}`;  // ❌
  window.open(url);  // ❌ 에러 처리 없음
};
```

#### TO-BE (수정된 코드)
```typescript
// 환경변수에서 base URL 가져오기
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * 표준화된 PDF 다운로드 함수
 * 모든 M2~M6 모듈에서 사용
 */
const downloadModulePDF = async (
  module: 'M2' | 'M3' | 'M4' | 'M5' | 'M6',
  contextId: string
) => {
  try {
    // ✅ 표준 URL 사용
    const url = `${API_BASE_URL}/api/v4/reports/${module}/pdf?context_id=${contextId}`;
    
    // ✅ fetch로 blob 다운로드
    const response = await fetch(url);
    
    if (!response.ok) {
      // ✅ 에러 처리
      const errorText = await response.text();
      throw new Error(`PDF 다운로드 실패 (${response.status}): ${errorText}`);
    }
    
    // ✅ Blob 변환
    const blob = await response.blob();
    
    // ✅ Content-Disposition에서 파일명 추출 (옵션)
    const contentDisposition = response.headers.get('Content-Disposition');
    const filenameMatch = contentDisposition?.match(/filename="?(.+?)"?$/);
    const filename = filenameMatch ? filenameMatch[1] : `${module}_보고서.pdf`;
    
    // ✅ 다운로드 트리거
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(downloadUrl);
    
    // ✅ 성공 토스트
    showToast('PDF 다운로드 완료', 'success');
    
  } catch (error) {
    // ✅ 에러 토스트
    console.error('PDF 다운로드 오류:', error);
    showToast(
      `PDF 다운로드 실패: ${error.message}`,
      'error'
    );
  }
};

// 사용 예
<button onClick={() => downloadModulePDF('M4', contextId)}>
  M4 PDF 다운로드
</button>
```

---

### 3. API 클라이언트 설정

#### 환경변수 설정 (.env)
```bash
# 개발 환경
VITE_API_BASE_URL=http://localhost:8000

# 프로덕션 환경
VITE_API_BASE_URL=https://api.zerosite.com
```

#### API Client (axios 예시)
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,  // PDF 생성은 시간이 걸릴 수 있음
  headers: {
    'Content-Type': 'application/json',
  }
});

// PDF 다운로드용 (blob 응답)
const pdfClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 60000,  // PDF 생성은 더 시간이 걸릴 수 있음
  responseType: 'blob',  // ✅ blob으로 받기
});

export { apiClient, pdfClient };
```

---

## 🧪 테스트 체크리스트

### 1. 카드 표시 테스트
- [ ] M2 카드: 신뢰도가 85% (0% 아님)
- [ ] M3 카드: 점수가 85점 (0점 아님)
- [ ] M4 카드: 세대수가 20/26 (0 아님)
- [ ] M5 카드: NPV, IRR, ROI 정상 표시
- [ ] M6 카드: 점수가 85.0/110 (0.0 아님)

### 2. PDF 다운로드 테스트
- [ ] M4 다운로드: 성공 (파일명: M4_건축규모결정_보고서_2025-12-19.pdf)
- [ ] M5 다운로드: 성공
- [ ] M6 다운로드: 성공
- [ ] 다운로드 실패 시: 에러 메시지 표시 (HTTP 코드 포함)

### 3. 데이터 일관성 테스트
- [ ] M6 요약 카드 점수 = PDF 표지 점수 = PDF 본문 점수
- [ ] M2 신뢰도 = 거래사례 기반 (0%가 아님)

---

## 📋 마이그레이션 체크리스트

### Phase 1: 백엔드 배포 (완료)
- [x] `canonical_data_contract.py` 추가
- [x] `pdf_download_standardized.py` 추가
- [x] M6 PDF 생성기 수정 (단일 소스)
- [x] 차트 데이터 링크 수정

### Phase 2: 프론트엔드 수정 (필요)
- [ ] 모듈 카드 컴포넌트 수정 (summary 사용)
- [ ] PDF 다운로드 함수 표준화
- [ ] API base URL 환경변수 사용
- [ ] 에러 처리 추가

### Phase 3: 통합 테스트
- [ ] 개발 환경에서 E2E 테스트
- [ ] 모든 모듈 카드 확인
- [ ] 모든 PDF 다운로드 확인

### Phase 4: 배포
- [ ] 프론트엔드 빌드 & 배포
- [ ] 프로덕션 환경 테스트
- [ ] 사용자 피드백 수집

---

## 🆘 트러블슈팅

### Q1: M2/M3 카드에 여전히 0 표시
**A:** 백엔드가 아직 표준 포맷을 반환하지 않을 수 있음
```typescript
// 임시 fallback 로직
const confidence = data.summary?.confidence_pct ?? 
                  (data.confidence?.score * 100) ?? 
                  0;
```

### Q2: PDF 다운로드 404 에러
**A:** 라우터가 등록되지 않았을 수 있음
```python
# main.py에서 확인
from app.routers import pdf_download_standardized
app.include_router(pdf_download_standardized.router)
```

### Q3: CORS 에러
**A:** 백엔드 CORS 설정 확인
```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 기본 포트
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📞 도움 필요 시

- **백엔드 API 문서**: `/docs` (Swagger UI)
- **데이터 계약 파일**: `app/core/canonical_data_contract.py`
- **PDF 라우터**: `app/routers/pdf_download_standardized.py`
- **테스트 스크립트**: `test_chart_data_linking.py`

---

**작성자:** ZeroSite Backend Team  
**최종 수정:** 2025-12-19 09:00 UTC
