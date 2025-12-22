# API 없이 실질적으로 작동하는 해결책 🎯

## 🔴 현실 직시

**사실 확인**:
1. ✅ Kakao API 키는 **정상 작동** (Python httpx 테스트 200 OK)
2. ❌ VWorld/Data.go.kr API는 **물리적으로 차단됨** (502 Bad Gateway, IP 차단)
3. ❌ API 키 재발급/재입력으로는 해결 **불가능**

**결론**: API 키 문제가 아니라 **서버 위치 문제**입니다.

---

## 💡 실질적으로 작동하는 3가지 방법

---

## 방법 1: Mock 데이터를 "실제 데이터"로 변환 ✅ (즉시 가능)

### 개념
Mock 데이터를 사용하되, **사용자가 검증/수정**하면 "실제 데이터"로 간주

### 구현 방안

#### Step 1: Mock 데이터 검증 모드 추가

```typescript
// frontend/src/components/m1/ReviewScreen.tsx

interface DataValidationStatus {
  cadastral: 'unverified' | 'user_verified' | 'api_verified';
  legal: 'unverified' | 'user_verified' | 'api_verified';
  road: 'unverified' | 'user_verified' | 'api_verified';
  market: 'unverified' | 'user_verified' | 'api_verified';
}

// Mock 데이터를 표시하고, 사용자가 "확인" 버튼 클릭
const handleVerifyData = (section: keyof DataValidationStatus) => {
  setValidationStatus(prev => ({
    ...prev,
    [section]: 'user_verified'  // Mock → 사용자 검증 완료
  }));
};

// M1 Lock 조건 수정
const canLock = () => {
  return (
    validationStatus.cadastral !== 'unverified' &&
    validationStatus.legal !== 'unverified' &&
    validationStatus.road !== 'unverified' &&
    validationStatus.market !== 'unverified'
  );
};
```

#### UI 예시

```
┌─────────────────────────────────────────────────┐
│ 지적 정보 (Mock 데이터)                         │
├─────────────────────────────────────────────────┤
│ PNU: 1168010100100120000                        │
│ 면적: 500.00 ㎡                                 │
│ 지목: 대지                                      │
│                                                 │
│ ⚠️ Mock 데이터입니다. 확인 후 체크하세요.       │
│                                                 │
│ [✏️ 수정] [✅ 데이터 확인 - 정확함]             │
│                                  ↑              │
│                           클릭하면 "검증 완료"   │
└─────────────────────────────────────────────────┘
```

#### 장점
- ✅ **즉시 사용 가능**
- ✅ API 의존도 0%
- ✅ 사용자가 책임지고 검증

#### 단점
- ⚠️ 사용자가 직접 확인 필요
- ⚠️ Mock 데이터 정확도 의존

---

## 방법 2: PDF 자동 추출 강화 📄 (권장)

### 현재 상태
```python
# app/services/pdf_parser.py
# 이미 PDF 파싱 기능 구현됨
```

### 개선 방안

#### 2.1 PDF 업로드를 기본 플로우로 변경

**변경 전 (현재)**:
```
Step 3: [API 자동 수집] / [PDF 업로드] / [수동 입력]
         ↓ 사용자 선택
```

**변경 후 (권장)**:
```
Step 3: [PDF 업로드 (권장)] / [수동 입력] / [API 시도]
         ↓ PDF 우선 권장
```

#### 2.2 PDF 업로드 UI 개선

```typescript
// frontend/src/components/m1/Step3DataCollection.tsx

const DataCollectionStep = () => {
  return (
    <div>
      <h2>📊 토지 데이터 수집</h2>
      
      {/* PDF 업로드 강조 */}
      <div className="recommended-method">
        <h3>🎯 권장 방법: PDF 업로드</h3>
        <p>토지대장, 토지이용계획확인서를 업로드하면 자동으로 데이터를 추출합니다.</p>
        
        <input
          type="file"
          accept=".pdf"
          onChange={handlePDFUpload}
        />
        <button onClick={() => uploadPDF()}>
          📄 PDF 업로드하기
        </button>
      </div>
      
      {/* 수동 입력 */}
      <div className="alternative-method">
        <h3>✏️ 대안: 수동 입력</h3>
        <button onClick={() => setMode('manual')}>
          직접 입력하기
        </button>
      </div>
      
      {/* API 시도 (비권장) */}
      <div className="experimental-method">
        <h3>⚠️ 실험적: API 자동 수집 (작동 불안정)</h3>
        <p className="warning">
          현재 한국 공공 API가 해외 서버를 차단하고 있습니다.
          작동하지 않을 가능성이 높습니다.
        </p>
        <button onClick={() => tryAPI()} disabled>
          🔬 API 시도 (비활성화)
        </button>
      </div>
    </div>
  );
};
```

#### 2.3 PDF OCR 품질 향상

```python
# app/services/pdf_parser.py

import PyPDF2
import re
from typing import Dict, Any, Optional

class EnhancedPDFParser:
    """
    개선된 PDF 파서
    - 토지대장 형식 지원
    - 토지이용계획확인서 형식 지원
    - 다양한 레이아웃 대응
    """
    
    def extract_land_data(self, pdf_path: str) -> Dict[str, Any]:
        """PDF에서 토지 데이터 추출"""
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        
        # 데이터 추출
        data = {
            'cadastral': self._extract_cadastral(text),
            'legal': self._extract_legal(text),
            'road': self._extract_road(text),
            'market': self._extract_market(text)
        }
        
        return data
    
    def _extract_cadastral(self, text: str) -> Dict[str, Any]:
        """지적 정보 추출"""
        
        # PNU 추출 (예: 1168010100100120000)
        pnu_pattern = r'\d{19}'
        pnu_match = re.search(pnu_pattern, text)
        pnu = pnu_match.group(0) if pnu_match else ""
        
        # 면적 추출 (예: 500.00㎡, 500제곱미터)
        area_pattern = r'(\d+\.?\d*)\s*(?:㎡|제곱미터|m²)'
        area_match = re.search(area_pattern, text)
        area = float(area_match.group(1)) if area_match else 0.0
        
        # 지목 추출
        jimok_pattern = r'지목\s*[:：]\s*(\S+)'
        jimok_match = re.search(jimok_pattern, text)
        jimok = jimok_match.group(1) if jimok_match else "대지"
        
        return {
            'pnu': pnu,
            'area': area,
            'jimok': jimok
        }
    
    def _extract_legal(self, text: str) -> Dict[str, Any]:
        """법적 정보 추출"""
        
        # 용도지역 추출
        zone_pattern = r'용도지역\s*[:：]\s*([^\n]+)'
        zone_match = re.search(zone_pattern, text)
        use_zone = zone_match.group(1).strip() if zone_match else ""
        
        # 용적률 추출 (예: 200%, 200퍼센트)
        far_pattern = r'용적률\s*[:：]\s*(\d+)\s*%'
        far_match = re.search(far_pattern, text)
        floor_area_ratio = int(far_match.group(1)) if far_match else 0
        
        # 건폐율 추출
        bcr_pattern = r'건폐율\s*[:：]\s*(\d+)\s*%'
        bcr_match = re.search(bcr_pattern, text)
        building_coverage_ratio = int(bcr_match.group(1)) if bcr_match else 0
        
        return {
            'use_zone': use_zone,
            'floor_area_ratio': floor_area_ratio,
            'building_coverage_ratio': building_coverage_ratio
        }
```

#### 장점
- ✅ **법적 유효성** (공식 문서 기반)
- ✅ **높은 정확도**
- ✅ API 의존도 0%
- ✅ **즉시 사용 가능**

#### 단점
- ⚠️ PDF 파일 필요
- ⚠️ OCR 오류 가능성 (수동 확인 필요)

---

## 방법 3: 완전 수동 입력 모드 ✏️ (최후 수단)

### 개념
모든 API를 포기하고, 사용자가 직접 모든 데이터 입력

### 구현 방안

#### 3.1 "API 없음" 모드 추가

```typescript
// frontend/src/components/m1/M1LandingPage.tsx

const [mode, setMode] = useState<'api' | 'pdf' | 'manual' | 'no_api'>('no_api');

// Step 0 건너뛰기
useEffect(() => {
  if (mode === 'no_api') {
    // API 키 설정 단계 자동 건너뛰기
    setCurrentStep(1); // 주소 검색부터 시작
  }
}, [mode]);
```

#### 3.2 수동 입력 폼 개선

```typescript
// frontend/src/components/m1/ManualInputForm.tsx

const ManualInputForm: React.FC = () => {
  const [formData, setFormData] = useState({
    // 지적 정보
    pnu: '',
    bonbun: '',
    bubun: '',
    area: 0,
    jimok: '',
    
    // 법적 정보
    use_zone: '',
    floor_area_ratio: 0,
    building_coverage_ratio: 0,
    
    // 도로 정보
    road_contact: '',
    road_width: 0,
    
    // 시장 정보
    official_land_price: 0,
    official_land_price_date: '',
    transactions: []
  });
  
  return (
    <form>
      <h2>토지 정보 직접 입력</h2>
      
      {/* 지적 정보 */}
      <fieldset>
        <legend>지적 정보</legend>
        
        <label>
          PNU (19자리):
          <input
            type="text"
            value={formData.pnu}
            onChange={(e) => setFormData({...formData, pnu: e.target.value})}
            placeholder="1168010100100120000"
            maxLength={19}
          />
        </label>
        
        <label>
          본번:
          <input
            type="text"
            value={formData.bonbun}
            onChange={(e) => setFormData({...formData, bonbun: e.target.value})}
            placeholder="123"
          />
        </label>
        
        <label>
          부번:
          <input
            type="text"
            value={formData.bubun}
            onChange={(e) => setFormData({...formData, bubun: e.target.value})}
            placeholder="45"
          />
        </label>
        
        <label>
          면적 (㎡):
          <input
            type="number"
            value={formData.area}
            onChange={(e) => setFormData({...formData, area: parseFloat(e.target.value)})}
            placeholder="500.00"
            step="0.01"
          />
        </label>
        
        <label>
          지목:
          <select
            value={formData.jimok}
            onChange={(e) => setFormData({...formData, jimok: e.target.value})}
          >
            <option value="">선택하세요</option>
            <option value="대지">대지</option>
            <option value="전">전</option>
            <option value="답">답</option>
            <option value="임야">임야</option>
            <option value="공장용지">공장용지</option>
            {/* 더 많은 지목... */}
          </select>
        </label>
      </fieldset>
      
      {/* 법적 정보 */}
      <fieldset>
        <legend>법적 정보</legend>
        
        <label>
          용도지역:
          <select
            value={formData.use_zone}
            onChange={(e) => setFormData({...formData, use_zone: e.target.value})}
          >
            <option value="">선택하세요</option>
            <option value="제1종일반주거지역">제1종일반주거지역</option>
            <option value="제2종일반주거지역">제2종일반주거지역</option>
            <option value="제3종일반주거지역">제3종일반주거지역</option>
            <option value="준주거지역">준주거지역</option>
            <option value="일반상업지역">일반상업지역</option>
            {/* 더 많은 용도지역... */}
          </select>
        </label>
        
        <label>
          용적률 (%):
          <input
            type="number"
            value={formData.floor_area_ratio}
            onChange={(e) => setFormData({...formData, floor_area_ratio: parseInt(e.target.value)})}
            placeholder="200"
            min="0"
            max="1000"
          />
        </label>
        
        <label>
          건폐율 (%):
          <input
            type="number"
            value={formData.building_coverage_ratio}
            onChange={(e) => setFormData({...formData, building_coverage_ratio: parseInt(e.target.value)})}
            placeholder="60"
            min="0"
            max="100"
          />
        </label>
      </fieldset>
      
      {/* 도로 정보 */}
      <fieldset>
        <legend>도로 정보</legend>
        
        <label>
          도로 접면:
          <select
            value={formData.road_contact}
            onChange={(e) => setFormData({...formData, road_contact: e.target.value})}
          >
            <option value="">선택하세요</option>
            <option value="북측">북측</option>
            <option value="남측">남측</option>
            <option value="동측">동측</option>
            <option value="서측">서측</option>
            <option value="각지">각지</option>
          </select>
        </label>
        
        <label>
          도로 폭 (m):
          <input
            type="number"
            value={formData.road_width}
            onChange={(e) => setFormData({...formData, road_width: parseFloat(e.target.value)})}
            placeholder="8.0"
            step="0.5"
            min="0"
          />
        </label>
      </fieldset>
      
      {/* 시장 정보 */}
      <fieldset>
        <legend>시장 정보</legend>
        
        <label>
          공시지가 (원/㎡):
          <input
            type="number"
            value={formData.official_land_price}
            onChange={(e) => setFormData({...formData, official_land_price: parseInt(e.target.value)})}
            placeholder="10000000"
            step="100000"
          />
        </label>
        
        <label>
          공시지가 기준일:
          <input
            type="date"
            value={formData.official_land_price_date}
            onChange={(e) => setFormData({...formData, official_land_price_date: e.target.value})}
          />
        </label>
      </fieldset>
      
      {/* 거래사례 */}
      <TransactionEditor
        transactions={formData.transactions}
        onChange={(transactions) => setFormData({...formData, transactions})}
      />
      
      <button type="submit">
        ✅ 입력 완료 - M1 Lock
      </button>
    </form>
  );
};
```

#### 장점
- ✅ **완전한 통제력**
- ✅ API 의존도 0%
- ✅ **즉시 사용 가능**

#### 단점
- ⚠️ 시간 소요 큼
- ⚠️ 수작업 오류 가능성
- ⚠️ 사용자 부담

---

## 🎯 최종 권장사항

### 우선순위

```
1순위: 방법 2 (PDF 자동 추출) 📄
       → 법적 유효성 + 자동화

2순위: 방법 1 (Mock 데이터 검증) ✅
       → 빠른 테스트 + 사용자 검증

3순위: 방법 3 (완전 수동 입력) ✏️
       → 최후 수단
```

### 즉시 구현 가능한 조합

```
┌────────────────────────────────────────────┐
│ Step 0: API 키 설정 건너뛰기 (Skip)        │
├────────────────────────────────────────────┤
│ Step 1: 주소 검색 (Kakao API ✅ 작동)      │
│         또는 직접 입력                     │
│         ↓                                  │
│ Step 2: 좌표 확인                          │
│         ↓                                  │
│ Step 3: 데이터 수집 방법 선택              │
│                                            │
│   Option A: 📄 PDF 업로드 (1순위)         │
│   → 자동 추출 + 사용자 확인               │
│                                            │
│   Option B: ✅ Mock 데이터 사용           │
│   → Mock 표시 + 사용자 검증 버튼          │
│   → "데이터 확인 완료" 체크               │
│                                            │
│   Option C: ✏️ 직접 입력                  │
│   → 모든 필드 수동 입력                   │
│         ↓                                  │
│ Step 4: M1 Lock                            │
│         ↓                                  │
│ Step 5: M2-M6 감정평가 자동 실행 ✅        │
└────────────────────────────────────────────┘
```

---

## 🔧 구현 계획

### Phase 1: Mock 데이터 검증 모드 (30분)
```typescript
1. ReviewScreen.tsx에 검증 상태 추가
2. "데이터 확인" 버튼 추가
3. M1 Lock 조건 수정 (검증 완료 필수)
```

### Phase 2: PDF 업로드 UI 개선 (1시간)
```typescript
1. Step3 화면에서 PDF 업로드를 기본 옵션으로 변경
2. PDF 파서 품질 향상 (정규식 패턴 개선)
3. 추출 실패 시 수동 입력 폴백
```

### Phase 3: 완전 수동 입력 폼 (2시간)
```typescript
1. ManualInputForm 컴포넌트 생성
2. 모든 필드에 대한 입력 UI
3. 유효성 검증 로직
```

---

## ✅ 결론

**API 키는 문제가 아닙니다. API 서버가 차단된 것입니다.**

**3가지 실질적 해결책**:
1. 📄 **PDF 업로드** (최우선 권장)
2. ✅ **Mock 데이터 검증** (빠른 구현)
3. ✏️ **완전 수동 입력** (최후 수단)

**모두 API 없이 작동 가능합니다!**

---

**작성일**: 2025-12-18  
**작성자**: ZeroSite Development Team  
**버전**: v1.0 Final Solution
