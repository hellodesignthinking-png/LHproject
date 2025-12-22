# ZeroSite Canonical Flow Implementation Guide

**Version:** v8.7+ (Structure Transformation)  
**Date:** 2025-12-03  
**Status:** 🔄 IN PROGRESS  
**Priority:** 🔥 CRITICAL

---

## 🎯 **핵심 목표**

> **감정평가를 모든 분석의 단일 기준선(Single Source of Truth)으로 확립**

### **Before (문제 구조):**
```
Parcel → Zoning → Price → Diagnosis → (Appraisal 흡수/무시) → LH
         ↓        ↓        ↓
      API재호출  API재호출  재계산
```

### **After (정확한 구조):**
```
Parcel → [Appraisal 🔒] → Diagnosis(참조만) → LH(참조만)
         │
         └─► Context Lock (Read-Only)
```

---

## 📐 **Canonical Appraisal Schema**

### **Standard Output Structure**

```json
{
  "context": {
    "appraisal": {
      "version": "v39",
      "locked": true,
      "timestamp": "2025-12-03T10:00:00Z",
      
      "zoning": {
        "confirmed_type": "제2종일반주거지역",
        "building_coverage_ratio": 60.0,
        "floor_area_ratio": 200.0,
        "source": "국토부 API",
        "verified_at": "2025-12-03"
      },
      
      "official_land_price": {
        "standard_price_per_sqm": 3200000,
        "reference_year": 2024,
        "reference_parcel": "서울특별시 마포구 XX-XX",
        "distance_to_standard": 150,
        "source": "표준지공시지가"
      },
      
      "transaction_cases": [
        {
          "price_per_sqm": 4100000,
          "transaction_date": "2024-08-15",
          "distance_m": 180,
          "area_sqm": 650,
          "similarity_score": 0.92,
          "adjusted_for_time": true,
          "adjusted_for_location": true
        },
        {
          "price_per_sqm": 3950000,
          "transaction_date": "2024-06-20",
          "distance_m": 250,
          "area_sqm": 700,
          "similarity_score": 0.88,
          "adjusted_for_time": true,
          "adjusted_for_location": true
        }
      ],
      
      "premium": {
        "development_potential": {
          "rate": 0.08,
          "rationale": "역세권 개발 가능성"
        },
        "location_premium": {
          "rate": 0.05,
          "rationale": "지하철 300m, 학교 400m"
        },
        "policy_benefit": {
          "rate": 0.03,
          "rationale": "LH 우선 매입 지역"
        },
        "total_premium_rate": 0.16
      },
      
      "calculation": {
        "base_price_per_sqm": 3650000,
        "premium_adjusted_per_sqm": 4234000,
        "land_area_sqm": 865.0,
        "final_appraised_total": 3662410000
      },
      
      "confidence": {
        "score": 0.92,
        "factors": {
          "data_completeness": 0.95,
          "case_similarity": 0.90,
          "time_relevance": 0.91
        }
      },
      
      "metadata": {
        "appraisal_engine": "ZeroSite v39",
        "calculation_method": "비교방식",
        "appraiser_note": "3개 거래사례 기준, 프리미엄 16% 적용"
      }
    }
  }
}
```

---

## 🔒 **Step 1: Appraisal Context Lock**

### **Implementation:**

```python
# app/services/appraisal_engine_v39.py

class AppraisalContextLock:
    """감정평가 결과 잠금 메커니즘"""
    
    def __init__(self):
        self._locked = False
        self._appraisal_data = None
    
    def lock(self, appraisal_result: Dict) -> None:
        """감정평가 결과를 잠그고 이후 수정 불가능하게 만듦"""
        if self._locked:
            raise ValueError("❌ Appraisal context already locked!")
        
        self._appraisal_data = appraisal_result
        self._appraisal_data['locked'] = True
        self._appraisal_data['locked_at'] = datetime.now().isoformat()
        self._locked = True
        
        print(f"🔒 Appraisal context LOCKED at {self._appraisal_data['locked_at']}")
        print(f"   Final appraised value: {appraisal_result['calculation']['final_appraised_total']:,.0f}원")
    
    def get(self, key_path: str) -> Any:
        """
        잠긴 감정평가 데이터 읽기 (수정 불가)
        
        Args:
            key_path: "zoning.confirmed_type" or "calculation.final_appraised_total"
        """
        if not self._locked:
            raise ValueError("❌ Appraisal context not yet locked!")
        
        keys = key_path.split('.')
        data = self._appraisal_data
        
        for key in keys:
            data = data.get(key)
            if data is None:
                raise KeyError(f"❌ Key not found in appraisal context: {key_path}")
        
        return data
    
    def is_locked(self) -> bool:
        """감정평가 컨텍스트가 잠겼는지 확인"""
        return self._locked
    
    def get_full_context(self) -> Dict:
        """전체 감정평가 컨텍스트 반환 (읽기 전용)"""
        if not self._locked:
            raise ValueError("❌ Appraisal context not yet locked!")
        
        return deepcopy(self._appraisal_data)  # 복사본 반환 (수정 방지)


# Global instance
appraisal_context = AppraisalContextLock()
```

### **Usage in Main Flow:**

```python
# app/main.py or analysis orchestrator

# 1. Run appraisal
appraisal_result = run_appraisal_engine(parcel_input)

# 2. Lock the context
appraisal_context.lock(appraisal_result)

# 3. Pass locked context to subsequent engines
diagnosis_result = run_land_diagnosis(appraisal_context)
lh_result = run_lh_analysis(appraisal_context)
```

---

## 📊 **Step 2: Land Diagnosis Refactoring**

### **Current Problem:**

```python
# ❌ WRONG - 토지진단이 데이터를 재조회
def analyze_land_diagnosis(parcel):
    zoning = fetch_zoning_from_api(parcel)  # 중복 API 호출!
    price = fetch_official_price(parcel)    # 중복 API 호출!
    cases = fetch_transactions(parcel)      # 중복 API 호출!
    
    # ... 분석 로직
```

### **Correct Implementation:**

```python
# ✅ CORRECT - 감정평가 컨텍스트만 참조
def analyze_land_diagnosis(appraisal_ctx: AppraisalContextLock) -> Dict:
    """
    토지진단 엔진 (감정평가 결과 기반)
    
    Args:
        appraisal_ctx: 잠긴 감정평가 컨텍스트 (읽기 전용)
    
    Returns:
        진단 결과 (개발적합성, 리스크, 점수)
    """
    
    # 1. 감정평가 결과에서 데이터 추출 (API 호출 없음!)
    zoning = appraisal_ctx.get('zoning.confirmed_type')
    land_price = appraisal_ctx.get('calculation.final_appraised_total')
    premium = appraisal_ctx.get('premium.total_premium_rate')
    
    print(f"📊 Land Diagnosis using appraisal context:")
    print(f"   Zoning (from appraisal): {zoning}")
    print(f"   Appraised value: {land_price:,.0f}원")
    print(f"   Premium applied: {premium*100:.1f}%")
    
    # 2. 개발적합성 판단 (해석만)
    buildability_score = calculate_buildability(
        zoning=zoning,
        premium_rate=premium,
        confidence=appraisal_ctx.get('confidence.score')
    )
    
    # 3. 리스크 플래그
    risk_flags = identify_risks(
        zoning=zoning,
        transaction_count=len(appraisal_ctx.get('transaction_cases'))
    )
    
    # 4. 진단 요약
    diagnosis_summary = generate_diagnosis_summary(
        buildability_score=buildability_score,
        risk_flags=risk_flags,
        appraised_value=land_price
    )
    
    return {
        'buildability_score': buildability_score,
        'risk_flags': risk_flags,
        'diagnosis_summary': diagnosis_summary,
        'based_on_appraisal': True,  # 명시적 표시
        'appraisal_reference': {
            'zoning': zoning,
            'appraised_value': land_price,
            'premium_rate': premium
        }
    }


def calculate_buildability(zoning: str, premium_rate: float, confidence: float) -> int:
    """
    개발적합성 점수 계산 (0-100)
    
    감정평가 결과를 기반으로 해석만 수행
    """
    base_score = 70  # 기본 점수
    
    # 용도지역 가산점
    if '준주거' in zoning:
        base_score += 15
    elif '제3종' in zoning:
        base_score += 10
    elif '제2종' in zoning:
        base_score += 5
    
    # 프리미엄 반영 (높을수록 개발 가치 높음)
    premium_bonus = min(premium_rate * 50, 15)
    
    # 신뢰도 반영
    confidence_bonus = confidence * 10
    
    final_score = min(base_score + premium_bonus + confidence_bonus, 100)
    
    return int(final_score)


def identify_risks(zoning: str, transaction_count: int) -> List[str]:
    """리스크 플래그 식별"""
    risks = []
    
    # 거래사례 부족
    if transaction_count < 2:
        risks.append("거래사례 부족 (감정평가 신뢰도 영향)")
    
    # 용도지역 제약
    if '제1종' in zoning:
        risks.append("저층 제한 (용도지역 제약)")
    
    # 개발행위 허가 필요
    if any(keyword in zoning for keyword in ['녹지', '보전']):
        risks.append("개발행위 허가 필요 (규제 지역)")
    
    return risks
```

---

## 🏛️ **Step 3: LH Analysis Refactoring**

### **Current Problem:**

```python
# ❌ WRONG - LH 분석이 자체 토지가액 계산
def calculate_lh_feasibility(parcel):
    land_value = parcel.area * some_price  # 자체 계산!
    # ...
```

### **Correct Implementation:**

```python
# ✅ CORRECT - 감정평가액을 입력으로 사용
def analyze_lh_feasibility(
    appraisal_ctx: AppraisalContextLock,
    expected_units: int,
    total_floor_area: float
) -> Dict:
    """
    LH 사업성 분석 (감정평가 기반)
    
    Args:
        appraisal_ctx: 감정평가 컨텍스트
        expected_units: 예상 세대수
        total_floor_area: 총 연면적
    
    Returns:
        LH 매입 가능성, ROI, 의사결정
    """
    
    # 1. 감정평가액 추출 (이것이 토지가액 기준!)
    land_appraised_value = appraisal_ctx.get('calculation.final_appraised_total')
    
    print(f"🏛️ LH Analysis based on appraisal:")
    print(f"   Land appraised value: {land_appraised_value:,.0f}원")
    print(f"   Analysis mode: {'LH_LINKED' if expected_units >= 50 else 'STANDARD'}")
    
    # 2. LH 매입가 계산 (감정평가액 + 건축비)
    construction_cost = calculate_lh_construction_cost(
        total_floor_area=total_floor_area,
        lh_unit_cost=2800000
    )
    
    lh_purchase_price = land_appraised_value + construction_cost
    
    # 3. 총 사업비 계산
    total_project_cost = calculate_total_project_cost(
        land_cost=land_appraised_value,
        construction_cost=construction_cost
    )
    
    # 4. ROI 계산
    roi = ((lh_purchase_price - total_project_cost) / total_project_cost) * 100
    
    # 5. 의사결정
    decision = make_lh_decision(roi=roi, units=expected_units)
    
    return {
        'land_appraised_value': land_appraised_value,
        'construction_cost': construction_cost,
        'lh_purchase_price': lh_purchase_price,
        'total_project_cost': total_project_cost,
        'roi': roi,
        'decision': decision,
        'based_on_appraisal': True,
        'appraisal_reference': {
            'appraised_value': land_appraised_value,
            'appraisal_version': appraisal_ctx.get('metadata.appraisal_engine')
        }
    }


def make_lh_decision(roi: float, units: int) -> str:
    """
    LH 의사결정 (감정평가 기반)
    
    Note: NO-GO가 나와도 감정평가가 틀린 것이 아님!
          사업성 판단 결과일 뿐.
    """
    if roi >= 10.0 and units >= 50:
        return "GO"
    elif roi >= 5.0 and units >= 50:
        return "CONDITIONAL"
    else:
        return "NO-GO"
```

---

## 📘 **Step 4: Report Structure Update**

### **New Report Structure:**

```markdown
# ZeroSite 분석 보고서 v8.7+

## 보고서 구조 (3단 분리)

### [SECTION 1] 감정평가 결과 (FACT)
**기준 엔진:** ZeroSite v39  
**계산 방식:** 비교방식

#### 1.1 토지가액 산정
- **최종 감정가**: 36.6억원
- **단가**: 4,234,000원/㎡
- **면적**: 865㎡

#### 1.2 산정 근거
- 공시지가 기준: 3,200,000원/㎡
- 거래사례 3건 평균: 4,050,000원/㎡
- 프리미엄 적용: +16%
  - 개발잠재력: +8%
  - 입지프리미엄: +5%
  - 정책수혜: +3%

#### 1.3 신뢰도
- 감정평가 신뢰도: 92%
- 거래사례 유사도: 90%

---

### [SECTION 2] 토지진단 결과 (INTERPRETATION)
**기준 데이터:** 감정평가 결과 참조

#### 2.1 개발적합성
- 개발적합성 점수: 88/100
- 용도지역: 제2종일반주거지역 (감정평가 확정)
- 프리미엄 수준: 높음 (16%)

#### 2.2 리스크 요인
- 주차확보 검토 필요
- 일조사선 제약 있음
- 거래사례 충분 (3건)

#### 2.3 종합 진단
**감정평가 기준상 개발 적합 토지**  
프리미엄 16% 적용된 점 고려 시 시장성 양호

---

### [SECTION 3] LH 사업성 판단 (DECISION)
**기준 토지가액:** 감정평가액 36.6억원

#### 3.1 재무 분석
- 토지가액: 36.6억원 (감정평가 기준)
- 건축비: 140억원
- LH 매입가: 176.6억원
- 총 사업비: 185억원
- **ROI: -4.49%**

#### 3.2 최종 의사결정
**판단: NO-GO**

**사유:**
- ROI가 음수로 사업성 부족
- 감정평가액 대비 건축비 과다
- 세대당 매입가 3.15억원 (높음)

**중요:**
> 본 NO-GO 판단은 **사업성 판단 결과**이며,
> **감정평가액 36.6억원 자체는 시장 적정가**입니다.

---

## 보고서 면책사항

본 보고서의 토지가액은 **ZeroSite 감정평가 엔진 v39** 기준으로 산출되었습니다.

- **감정평가**: 시장 적정가 산정 (FACT)
- **토지진단**: 개발 적합성 해석 (INTERPRETATION)
- **LH 판단**: 사업성 의사결정 (DECISION)

각 단계는 독립적이며, NO-GO 판단이 감정평가의 부정확성을 의미하지 않습니다.
```

---

## ✅ **Developer Checklist**

### **Before Deployment:**

- [ ] **Appraisal Engine**
  - [ ] v39 로직 수정하지 않았는가?
  - [ ] 프리미엄 계산식 그대로인가?
  - [ ] Context lock 적용했는가?

- [ ] **Land Diagnosis**
  - [ ] API 재호출 제거했는가?
  - [ ] appraisal_ctx만 사용하는가?
  - [ ] 독립적인 감정평가 시도하지 않는가?

- [ ] **LH Analysis**
  - [ ] 감정평가액을 토지가액으로 사용하는가?
  - [ ] "LH 기준 토지가" 같은 별도 계산 없는가?
  - [ ] NO-GO 시 감정평가 탓하지 않는가?

- [ ] **Report**
  - [ ] 3단 구조 (감정/진단/판단) 명확한가?
  - [ ] 감정평가 v39 명시했는가?
  - [ ] 면책사항 추가했는가?

---

## 🎯 **Expected Benefits**

이 구조 전환 후:

1. ✅ **예전 감정평가 결과와 현재 결과 일치**
2. ✅ **프리미엄 로직 "증발" 문제 해결**
3. ✅ **용도지역/공시지가/사례 데이터 불일치 제거**
4. ✅ **"왜 이 결과가 나왔는지" 설명 가능**
5. ✅ **LH·감정평가사·디벨로퍼 모두 납득 가능**

---

**End of Implementation Guide**
