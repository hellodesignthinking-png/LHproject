# M1 입력 필드 → Context 매핑 전수 점검
**Date**: 2025-12-17  
**Status**: 🔴 **CRITICAL - 병목 구간 진단**

---

## 🎯 목적

**"M1 Landing Page 입력 → Backend Context 저장"까지의 모든 필드를 1:1 매핑하여, 누락/불일치/null 위험 요소를 식별**

---

## 📋 STEP별 필드 매핑 체크리스트

### ✅ STEP 1: Address Search

| # | UI Input | React State | Freeze Request | Backend Context | 상태 | 이슈 |
|---|----------|-------------|----------------|-----------------|------|------|
| 1.1 | 주소 검색창 | `formData.selectedAddress.jibun_address` | `address` | `address` | ✅ OK | - |
| 1.2 | 도로명 주소 | `formData.selectedAddress.road_address` | `road_address` | `road_address` | ✅ OK | - |
| 1.3 | 시도 | `formData.selectedAddress.sido` | ❌ 없음 | `sido` | ⚠️ 누락 | STEP2에서 채움 |
| 1.4 | 시군구 | `formData.selectedAddress.sigungu` | ❌ 없음 | `sigungu` | ⚠️ 누락 | STEP2에서 채움 |
| 1.5 | 동 | `formData.selectedAddress.dong` | ❌ 없음 | `dong` | ⚠️ 누락 | STEP2에서 채움 |

**문제**: STEP1에서 sido/sigungu/dong이 있지만, Freeze Request에서는 STEP2 geocode 값 사용

---

### ✅ STEP 2: Location Verification (Geocoding)

| # | UI Input | React State | Freeze Request | Backend Context | 상태 | 이슈 |
|---|----------|-------------|----------------|-----------------|------|------|
| 2.1 | 위도 | `formData.geocodeData.coordinates.lat` | `coordinates.lat` | `lat` | ✅ OK | - |
| 2.2 | 경도 | `formData.geocodeData.coordinates.lon` | `coordinates.lon` | `lon` | ✅ OK | - |
| 2.3 | 시도 | `formData.geocodeData.sido` | `sido` | `sido` | ✅ OK | - |
| 2.4 | 시군구 | `formData.geocodeData.sigungu` | `sigungu` | `sigungu` | ✅ OK | - |
| 2.5 | 동 | `formData.geocodeData.dong` | `dong` | `dong` | ✅ OK | - |
| 2.6 | 법정동 | `formData.geocodeData.beopjeong_dong` | `beopjeong_dong` | `beopjeong_dong` | ⚠️ 선택 | Optional |
| 2.7 | 좌표 검증 | - | `coordinates_verified: true` | `verified` | ✅ OK | Hard-coded |
| 2.8 | 좌표 출처 | `formData.dataSources.geocode` | `coordinates_source` | `source` | ✅ OK | - |

**문제**: `coordinates_verified` 항상 `true` (실제 검증 로직 없음)

---

### ✅ STEP 3: Cadastral Data (지적정보)

| # | UI Input | React State | Freeze Request | Backend Context | 상태 | 이슈 |
|---|----------|-------------|----------------|-----------------|------|------|
| 3.1 | 본번 | `formData.cadastralData.bonbun` | `bonbun` | `bonbun` | ⚠️ 필수 | **Empty string 허용** |
| 3.2 | 부번 | `formData.cadastralData.bubun` | `bubun` | `bubun` | ⚠️ 필수 | **Empty string 허용** |
| 3.3 | 지목 | `formData.cadastralData.jimok` | `jimok` | `jimok` | ⚠️ 필수 | **Default: '대지'** |
| 3.4 | 면적 (㎡) | `formData.cadastralData.area` | `area` | `area` | 🔴 필수 | **0 허용 (invalid!)** |
| 3.5 | 지적 출처 | `formData.dataSources.cadastral` | `cadastral_source` | `source` | ✅ OK | - |
| 3.6 | 신뢰도 | `formData.dataSources.cadastral.confidence` | `cadastral_confidence` | `confidence` | ⚠️ 선택 | PDF 전용 |

**🔴 CRITICAL 문제**:
1. `bonbun`/`bubun`이 빈 문자열(`''`)이어도 Lock 허용
2. `area`가 `0`이어도 Lock 허용 (물리적으로 불가능!)
3. `jimok` 기본값 '대지'가 실제와 다를 수 있음

---

### ✅ STEP 4: Legal Info (용도지역)

| # | UI Input | React State | Freeze Request | Backend Context | 상태 | 이슈 |
|---|----------|-------------|----------------|-----------------|------|------|
| 4.1 | 용도지역 | `formData.landUseData.zone_type` | `zone_type` | `zone_type` | 🔴 필수 | **Empty string 허용** |
| 4.2 | 용도지역 상세 | `formData.landUseData.zone_detail` | `zone_detail` | `zone_detail` | ⚠️ 선택 | - |
| 4.3 | 토지이용 | `formData.landUseData.land_use` | `land_use` | `land_use` | ⚠️ 필수 | **Default: '주거용'** |
| 4.4 | FAR (용적률) | `formData.landUseData.far` | `far` | `far` | 🔴 필수 | **0 허용 (invalid!)** |
| 4.5 | BCR (건폐율) | `formData.landUseData.bcr` | `bcr` | `bcr` | 🔴 필수 | **0 허용 (invalid!)** |
| 4.6 | 높이 제한 | - | `height_limit: null` | `height_limit` | ⚠️ 선택 | Hard-coded null |
| 4.7 | 규제사항 | `formData.landUseData.regulations` | `regulations` | `regulations` | ⚠️ 선택 | Empty array 허용 |
| 4.8 | 제한사항 | `formData.landUseData.restrictions` | `restrictions` | `restrictions` | ⚠️ 선택 | Empty array 허용 |
| 4.9 | 용도지역 출처 | `formData.dataSources.land_use` | `zoning_source` | `source` | ✅ OK | - |

**🔴 CRITICAL 문제**:
1. `zone_type`이 빈 문자열이어도 Lock 허용
2. `far`/`bcr`이 `0`이어도 Lock 허용 (M4 계산 불가능!)
3. `land_use` 기본값 '주거용'이 실제와 다를 수 있음

---

### ✅ STEP 5: Road Access (도로정보)

| # | UI Input | React State | Freeze Request | Backend Context | 상태 | 이슈 |
|---|----------|-------------|----------------|-----------------|------|------|
| 5.1 | 접도 여부 | - | `road_contact: '접도'` | `road_contact` | ⚠️ 필수 | Hard-coded '접도' |
| 5.2 | 도로 폭 | `formData.roadInfoData.road_width` | `road_width` | `road_width` | 🔴 필수 | **0 허용 (invalid!)** |
| 5.3 | 도로 유형 | `formData.roadInfoData.road_type` | `road_type` | `road_type` | ⚠️ 필수 | **Default: '소로'** |
| 5.4 | 인근 도로 | `formData.roadInfoData.nearby_roads` | `nearby_roads[]` | `nearby_roads` | ⚠️ 선택 | Empty array 허용 |
| 5.5 | 도로 출처 | `formData.dataSources.road_info` | `road_source` | `source` | ✅ OK | - |

**🔴 CRITICAL 문제**:
1. `road_contact`가 항상 '접도' (실제는 '맹지' 가능)
2. `road_width`가 `0`이어도 Lock 허용
3. `road_type` 기본값 '소로'가 실제와 다를 수 있음

---

### ✅ STEP 6: Market Data (시장정보)

| # | UI Input | React State | Freeze Request | Backend Context | 상태 | 이슈 |
|---|----------|-------------|----------------|-----------------|------|------|
| 6.1 | 공시지가 | `formData.marketData.official_land_price` | `official_land_price` | `official_price` | ⚠️ 선택 | **Optional (중요!)** |
| 6.2 | 공시지가 기준일 | `formData.marketData.official_land_price_date` | `official_land_price_date` | `price_date` | ⚠️ 선택 | Optional |
| 6.3 | 거래사례 (M2용) | `formData.marketData.transactions[0-4]` | `transaction_cases_appraisal[]` | `transactions` | ⚠️ 선택 | **< 3건 시 Warning** |
| 6.4 | 거래사례 (참고용) | `formData.marketData.transactions` | `transaction_cases_reference[]` | `ref_transactions` | ⚠️ 선택 | Unlimited |
| 6.5 | 시장정보 출처 | `formData.dataSources.market_data` | `official_price_source` | `source` | ✅ OK | - |
| 6.6 | Premium: 코너 | - | `corner_lot: false` | `corner_lot` | ⚠️ 선택 | Hard-coded false |
| 6.7 | Premium: 광로 | - | `wide_road: false` | `wide_road` | ⚠️ 선택 | Hard-coded false |
| 6.8 | Premium: 역세권 | - | `subway_proximity: null` | `subway` | ⚠️ 선택 | Hard-coded null |
| 6.9 | Premium: 학군 | - | `school_district: null` | `school` | ⚠️ 선택 | Hard-coded null |
| 6.10 | Premium: 개발계획 | - | `development_plan: null` | `development` | ⚠️ 선택 | Hard-coded null |

**⚠️ 주의 문제**:
1. `official_land_price` 없어도 Lock 가능 (M2 계산에 중요)
2. Premium factors 전부 hard-coded (실제 분석 안 함)
3. 거래사례 < 3건이어도 Lock 가능 (M2 Warning 발생)

---

### ✅ Optional Inputs (STEP 3-6 중 수집 가능)

| # | UI Input | React State | Freeze Request | Backend Context | 상태 | 이슈 |
|---|----------|-------------|----------------|-----------------|------|------|
| O.1 | 인구 밀도 | - | `population_density: null` | `pop_density` | ⚠️ 선택 | M3용, 미구현 |
| O.2 | 연령 분포 | - | `age_distribution: null` | `age_dist` | ⚠️ 선택 | M3용, 미구현 |
| O.3 | 소득 수준 | - | `income_level: null` | `income` | ⚠️ 선택 | M3용, 미구현 |
| O.4 | 선호 LH 유형 | - | `preferred_lh_types: []` | `lh_types` | ⚠️ 선택 | M3용, 미구현 |
| O.5 | 건축 단가 | - | `construction_unit_cost: null` | `unit_cost` | ⚠️ 선택 | M5용, 미구현 |
| O.6 | 연동제 가능 | - | `linkage_available: false` | `linkage` | ⚠️ 선택 | M5용, 미구현 |
| O.7 | 연동제 대출액 | - | `linkage_loan_amount: null` | `loan` | ⚠️ 선택 | M5용, 미구현 |
| O.8 | 연동제 금리 | - | `linkage_interest_rate: null` | `interest` | ⚠️ 선택 | M5용, 미구현 |

**참고**: 이 필드들은 현재 UI에 없으며, 모두 hard-coded default 값 사용

---

## 🔴 CRITICAL 문제 요약

### 1. **빈 값 / 0 값 허용 문제**

| 필드 | 현재 상태 | 문제 | 영향 |
|------|----------|------|------|
| `bonbun` | Empty string `''` 허용 | 지번 없음 | M1 Context 불완전 |
| `bubun` | Empty string `''` 허용 | 부번 없음 | M1 Context 불완전 |
| `area` | `0` 허용 | 면적 0㎡ 불가능 | **M4 계산 불가** |
| `zone_type` | Empty string `''` 허용 | 용도지역 없음 | **M4 계산 불가** |
| `far` | `0` 허용 | 용적률 0% 불가능 | **M4 계산 불가** |
| `bcr` | `0` 허용 | 건폐율 0% 불가능 | **M4 계산 불가** |
| `road_width` | `0` 허용 | 도로 폭 0m 불가능 | M1 Context 불완전 |

**🚨 결과**: 이 상태로 M1 Lock하면 M4에서 "Division by Zero" 또는 "Invalid Capacity" 에러 발생!

---

### 2. **Hard-coded Default 값 문제**

| 필드 | Hard-coded 값 | 실제 가능 값 | 문제 |
|------|---------------|-------------|------|
| `jimok` | `'대지'` | 전/답/임야/잡종지/대지 등 | 실제와 다를 수 있음 |
| `land_use` | `'주거용'` | 주거용/상업용/공업용 등 | 실제와 다를 수 있음 |
| `road_contact` | `'접도'` | 접도/맹지/이격 등 | 맹지인데 접도로 잘못 표시 |
| `road_type` | `'소로'` | 소로/중로/대로/광로 | 실제와 다를 수 있음 |
| `coordinates_verified` | `true` | true/false | 실제 검증 안 함 |
| `corner_lot` | `false` | true/false | Premium 계산 누락 |
| `wide_road` | `false` | true/false | Premium 계산 누락 |

**🚨 결과**: 사용자가 입력하지 않은 값이 "추정"으로 들어가 M2-M6 결과 왜곡!

---

### 3. **데이터 출처 불일치 문제**

| STEP | React State | Freeze Request 필드 | Backend 필드 | 상태 |
|------|-------------|---------------------|--------------|------|
| 1 | `formData.selectedAddress.sido` | ❌ 미사용 | `sido` | ⚠️ STEP2로 덮어씀 |
| 1 | `formData.selectedAddress.sigungu` | ❌ 미사용 | `sigungu` | ⚠️ STEP2로 덮어씀 |
| 1 | `formData.selectedAddress.dong` | ❌ 미사용 | `dong` | ⚠️ STEP2로 덮어씀 |

**문제**: STEP1 주소 검색에서 이미 sido/sigungu/dong이 있는데, STEP2 Geocoding 결과로 덮어쓰기. 만약 Geocoding 실패 시 null 가능!

---

### 4. **M1 Lock 가능 조건 부재**

**현재 상태**: Lock 버튼이 **항상 활성화**됨 (조건 체크 없음)

**결과**:
- ✅ 주소만 입력 → Lock 가능
- ✅ 지번 없음 → Lock 가능
- ✅ 면적 0 → Lock 가능
- ✅ FAR/BCR 0 → Lock 가능 (M4 에러!)
- ✅ 도로 폭 0 → Lock 가능

**🚨 이 상태에서 M1 Lock하면 100% M4 실패!**

---

## ✅ 해결 방안

### 1. **M1 Lock 최소 조건 강제**

```typescript
// Step8ContextFreeze.tsx

const canLock = (): boolean => {
  const checks = {
    // 필수: 주소
    hasAddress: !!formData.selectedAddress?.jibun_address,
    
    // 필수: 좌표
    hasCoordinates: !!(formData.geocodeData?.coordinates.lat && 
                       formData.geocodeData?.coordinates.lon),
    
    // 필수: 지번 (본번은 필수, 부번은 선택)
    hasJibun: !!formData.cadastralData?.bonbun,
    
    // 필수: 면적 (> 0)
    hasArea: (formData.cadastralData?.area || 0) > 0,
    
    // 필수: 용도지역
    hasZoning: !!formData.landUseData?.zone_type,
    
    // 필수: FAR/BCR (> 0)
    hasFAR: (formData.landUseData?.far || 0) > 0,
    hasBCR: (formData.landUseData?.bcr || 0) > 0,
    
    // 필수: 도로 폭 (> 0)
    hasRoadWidth: (formData.roadInfoData?.road_width || 0) > 0,
    
    // 권장: 공시지가 OR 거래사례
    hasMarketData: !!(formData.marketData?.official_land_price || 
                      formData.marketData?.transactions?.length)
  };
  
  return Object.values(checks).every(v => v === true);
};

const getMissingFields = (): string[] => {
  const missing: string[] = [];
  
  if (!formData.selectedAddress?.jibun_address) missing.push('주소');
  if (!formData.geocodeData?.coordinates.lat) missing.push('좌표');
  if (!formData.cadastralData?.bonbun) missing.push('본번');
  if ((formData.cadastralData?.area || 0) <= 0) missing.push('토지면적');
  if (!formData.landUseData?.zone_type) missing.push('용도지역');
  if ((formData.landUseData?.far || 0) <= 0) missing.push('용적률(FAR)');
  if ((formData.landUseData?.bcr || 0) <= 0) missing.push('건폐율(BCR)');
  if ((formData.roadInfoData?.road_width || 0) <= 0) missing.push('도로 폭');
  
  return missing;
};
```

**Lock 버튼**:
```tsx
<button 
  onClick={startAnalysis}
  disabled={!canLock()}
  className={canLock() ? 'btn-primary' : 'btn-disabled'}
>
  {canLock() ? '분석 시작 (M1 Lock)' : '입력 완료 필요'}
</button>

{!canLock() && (
  <div className="missing-fields-warning">
    ⚠️ 누락된 필수 항목: {getMissingFields().join(', ')}
  </div>
)}
```

---

### 2. **Default 값 제거 및 명시적 입력 요구**

```typescript
// 현재 (잘못됨)
jimok: formData.cadastralData?.jimok || '대지',  // ❌ 추정 금지!

// 수정 (올바름)
jimok: formData.cadastralData?.jimok || '',      // ✅ 비어있으면 에러
```

**Lock 조건 추가**:
```typescript
hasJimok: !!formData.cadastralData?.jimok,  // 빈 문자열 불허
```

---

### 3. **STEP7: Preview & Validation 화면 추가**

```tsx
// Step7Review.tsx

export const Step7Review: React.FC<Step7Props> = ({ formData, onNext, onBack }) => {
  const warnings = getDataQualityWarnings(formData);
  const missing = getMissingFields(formData);
  
  return (
    <div className="step7-review">
      <h2>최종 입력 내용 확인</h2>
      
      {/* 필수 항목 체크 */}
      {missing.length > 0 && (
        <div className="error-box">
          ❌ 누락된 필수 항목: {missing.join(', ')}
        </div>
      )}
      
      {/* 경고 항목 */}
      {warnings.length > 0 && (
        <div className="warning-box">
          {warnings.map(w => (
            <div key={w.field}>
              ⚠️ {w.field}: {w.message}
            </div>
          ))}
        </div>
      )}
      
      {/* 데이터 품질 요약 */}
      <div className="data-quality-summary">
        <h3>데이터 품질</h3>
        <div>API 자동 수집: {getAPIPercentage(formData)}%</div>
        <div>PDF 입력: {getPDFPercentage(formData)}%</div>
        <div>수기 입력: {getManualPercentage(formData)}%</div>
      </div>
      
      {/* 실제 Context 값 미리보기 */}
      <details>
        <summary>Context Preview (개발자용)</summary>
        <pre>{JSON.stringify(buildFreezeRequest(formData), null, 2)}</pre>
      </details>
      
      <div className="button-group">
        <button onClick={onBack}>이전</button>
        <button 
          onClick={onNext}
          disabled={missing.length > 0}
        >
          다음 (확정)
        </button>
      </div>
    </div>
  );
};
```

---

### 4. **API 실패 시 입력 우회 루트**

```tsx
// Step3CadastralData.tsx

const [inputMode, setInputMode] = useState<'api' | 'pdf' | 'manual'>('api');

const handleAPIFailure = (error: Error) => {
  showErrorDialog({
    title: 'API 조회 실패',
    message: '지적정보 자동 조회에 실패했습니다.',
    options: [
      {
        label: '재시도',
        onClick: () => retryAPI()
      },
      {
        label: 'PDF 업로드',
        onClick: () => setInputMode('pdf')
      },
      {
        label: '수기 입력',
        onClick: () => setInputMode('manual')
      }
    ]
  });
};

// PDF 모드
{inputMode === 'pdf' && (
  <PDFUploader 
    onExtracted={(data) => {
      setFormData({
        bonbun: data.bonbun,
        bubun: data.bubun,
        jimok: data.jimok,
        area: data.area,
        source: 'pdf',
        confidence: data.confidence
      });
    }}
  />
)}

// 수기 입력 모드
{inputMode === 'manual' && (
  <ManualInputForm
    fields={['bonbun', 'bubun', 'jimok', 'area']}
    onSubmit={(data) => {
      setFormData({
        ...data,
        source: 'manual'
      });
    }}
  />
)}
```

---

## 🎯 수정 우선순위

### 🔴 P0: CRITICAL (즉시 수정 필요)
1. ✅ Lock 조건 강제 (`area > 0`, `far > 0`, `bcr > 0` 등)
2. ✅ Default 값 제거 (`jimok`, `land_use`, `road_contact` 등)
3. ✅ STEP7 Preview & Validation 화면 추가

### 🟡 P1: HIGH (1-2주 내)
4. ✅ API 실패 시 PDF/수기 입력 우회
5. ✅ 데이터 출처 불일치 해결 (STEP1 vs STEP2)
6. ✅ Premium factors 실제 계산 (현재 hard-coded)

### 🟢 P2: MEDIUM (1개월 내)
7. ✅ Optional inputs UI 추가 (인구밀도, 소득 등)
8. ✅ 좌표 실제 검증 로직
9. ✅ E2E 테스트 추가

---

## 📝 결론

**현재 상태**: M1 입력 → Context 매핑은 **60% 작동** (빈 값/0 값으로 Lock 가능)

**수정 후 기대**: M1 입력 → Context 매핑 **100% 신뢰** (완전한 데이터만 Lock 가능)

**핵심**: 
- ✅ "Lock은 무조건 성공" → ❌
- ✅ "완성된 입력만 Lock 가능" → ⭕️

---

**End of M1 Input to Context Mapping Check**  
**Next**: 위 P0 항목부터 순차 수정
