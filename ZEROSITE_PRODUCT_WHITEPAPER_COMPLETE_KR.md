# ZeroSite 제품 백서
## 감정평가 기반 공공주택 분석 OS (Appraisal-First Public Housing Analysis Operating System)

**Version**: 1.0  
**Release Date**: 2025-12-14  
**Document Type**: Technical Whitepaper (기술 백서)  
**Language**: Korean (한글) with English Abstract  
**Pages**: 35 pages

---

## Executive Summary (요약)

**ZeroSite**는 **감정평가(Real Estate Appraisal)를 절대 기준축으로 하는 공공주택 토지 분석 운영체제(Operating System)**입니다.

### 핵심 가치 제안

1. **단일 진실의 원천 (Single Source of Truth)**  
   - 모든 분석·심사·의사결정이 **감정평가 결과에서 출발**
   - 데이터 불일치 제로, 설명 책임 명확

2. **LH 신축매입임대 전문화**  
   - LH 공사 사전심사 통과 확률 예측 (AI Judge)
   - 7대 주택유형별 최적 시나리오 자동 생성

3. **완전 자동화 워크플로우**  
   - 주소 입력 → 30초 이내 5종 보고서 생성
   - 감정평가 23p + LH 제출 12p + 정책분석 15p + 사업성 18p + 전문가 30p

### 시장 기회

- **LH 신축매입임대 시장 규모**: 연간 3조원 이상
- **기존 문제점**: 감정평가·사업성·정책 판단의 분절, 심사 불확실성 높음
- **ZeroSite 해결책**: 통합 플랫폼 + AI 사전심사 예측

---

## English Abstract

**ZeroSite** is an Appraisal-First Operating System for Public Housing Land Analysis, specifically designed for LH Corporation's Build-to-Rent (BTR) program in South Korea.

**Key Features**:
- **Single Source of Truth**: All analyses stem from professional real estate appraisal (v39 standard)
- **AI Pre-Screening Judge**: Predicts LH approval probability with 6-factor scoring
- **Automated Workflow**: Address → 30sec → 5 types of reports (3p~30p)

**Target Market**: $3B+ annual LH BTR market  
**Status**: Production-ready (v40.6)  
**Tech Stack**: FastAPI, ReportLab, Rule-Based AI (ML-ready architecture)

---

## Table of Contents (목차)

1. [문제 정의 & 시장 맥락](#1-문제-정의--시장-맥락)
2. [ZeroSite의 핵심 철학](#2-zerosite의-핵심-철학)
3. [전체 아키텍처 (v40.6 고정)](#3-전체-아키텍처-v406-고정)
4. [감정평가 엔진 (v39 기반)](#4-감정평가-엔진-v39-기반)
5. [토지진단 / 규모검토](#5-토지진단--규모검토)
6. [시나리오 엔진](#6-시나리오-엔진)
7. [LH AI Judge v1.0 (Rule-based)](#7-lh-ai-judge-v10-rule-based)
8. [보고서 5종 체계](#8-보고서-5종-체계)
9. [데이터 책임 & 정책 정합성](#9-데이터-책임--정책-정합성)
10. [로드맵](#10-로드맵)

---

## 1. 문제 정의 & 시장 맥락

### 1.1 LH 신축매입임대 사업의 구조

**LH 신축매입임대**는 한국토지주택공사(LH)가 민간이 건설한 주택을 준공 즉시 매입하여 공공임대주택으로 공급하는 제도입니다.

**사업 흐름**:
```
토지소유주/개발사 → 사전심사 신청 → LH 심사 → 승인 → 건설 → 준공 매입 → 임대운영
```

**시장 규모**:
- 연간 LH 신축매입임대 예산: **약 3조원**
- 연간 신청 건수: 약 500~700건
- 승인율: 평균 40~50% (지역별 편차 큼)

### 1.2 기존 의사결정 프로세스의 문제점

#### 문제 1: 분절된 판단 구조

현재 LH 신축매입임대 사업에서는 **3가지 서로 다른 판단 주체**가 독립적으로 움직입니다:

1. **감정평가사** (Appraiser)
   - 역할: 토지가격 감정
   - 기준: 부동산 공시법, 감정평가법
   - 산출물: 감정평가서 (23~30p)

2. **사업성 컨설턴트** (Feasibility Consultant)
   - 역할: 개발사업 수익성 분석
   - 기준: IRR, NPV, 재무모델
   - 산출물: 사업성 분석 보고서 (15~20p)

3. **LH 담당자** (LH Reviewer)
   - 역할: 정책 부합성 판단, 최종 승인
   - 기준: LH 내부 지침, 주택도시기금 가이드라인
   - 산출물: 심사의견서

**핵심 문제**: 이 3자의 기준이 **서로 다르고**, **데이터도 따로** 관리됩니다.

**예시**:
- 감정평가사: "이 토지는 ㎡당 3천만원"
- 사업성 컨설턴트: "㎡당 2.8천만원 기준으로 사업성 분석" (10% 차이)
- LH 담당자: "공시지가 기준으로 검토하면..." (또 다른 기준)

→ **결과**: 동일한 토지에 대해 3가지 다른 가격이 병존

#### 문제 2: 사전 심사 불확실성

LH 담당자도 **승인 여부를 사전에 예측하기 어렵습니다**:

- 내부 지침이 수백 페이지에 달함
- 6가지 평가요소(입지, 가격, 규모, 구조, 계획, 리스크)를 종합 판단
- 각 요소별 가중치가 명문화되지 않음
- 담당자 경험에 의존

→ **결과**: 
- 신청자 입장: "이 토지는 통과할까?" 예측 불가
- LH 입장: 일관성 있는 심사 어려움

#### 문제 3: 보고서 재작성의 비효율

각 단계마다 **중복 작업** 발생:

1. 감정평가사가 토지 조사 (거래사례 15건 수집)
2. 사업성 컨설턴트가 같은 지역 거래사례 다시 조사
3. LH 제출 시 또 다시 자료 정리

→ 같은 데이터를 3번 수집·분석·보고

### 1.3 시장 요구사항

위 문제들로 인해 시장에서는 다음을 절실히 필요로 합니다:

1. **단일 기준점** (Single Source of Truth)
   - 모든 분석의 출발점이 되는 **하나의 권위 있는 데이터**

2. **사전 예측 도구** (Pre-Screening Tool)
   - LH 승인 가능성을 **신청 전에 미리 예측**

3. **자동화 플랫폼** (Automated Platform)
   - 주소만 입력하면 필요한 모든 보고서가 **30초 내 생성**

---

## 2. ZeroSite의 핵심 철학

### 2.1 Why Appraisal-First? (왜 감정평가가 기준인가?)

ZeroSite는 **감정평가(Appraisal)**를 전체 시스템의 절대 기준축으로 삼았습니다. 이유는 명확합니다:

#### 이유 1: 법적 권위 (Legal Authority)

감정평가는 대한민국에서 **법적으로 유일하게 인정받는 부동산 가격 산정 방법**입니다:

- 근거 법률: 「감정평가 및 감정평가사에 관한 법률」
- 부동산 공시법에 따른 표준지 공시지가
- 법원·국세청이 인정하는 공신력

→ 감정평가사가 작성한 감정평가서는 **법적 증거능력**을 가짐

#### 이유 2: 표준화된 방법론 (Standardized Methodology)

감정평가는 **3대 감정평가 방식**이라는 국제 표준을 따릅니다:

1. **원가법** (Cost Approach)
   - 공시지가 × 토지면적 × 위치계수

2. **거래사례비교법** (Sales Comparison Approach)
   - 인근 거래사례 15건 이상 수집 → 조정 → 비교평가

3. **수익환원법** (Income Approach)
   - 예상 임대수익 / 환원이율

→ 어떤 감정평가사가 평가해도 **±10% 이내**로 수렴

#### 이유 3: 데이터의 완전성 (Data Completeness)

감정평가서에는 **모든 필요한 정보**가 이미 들어있습니다:

| 정보 | 감정평가서 포함 여부 |
|------|---------------------|
| 토지 위치·면적 | ✅ |
| 용도지역 (Zoning) | ✅ |
| 건폐율·용적률 | ✅ |
| 공시지가 | ✅ |
| 거래사례 15건+ | ✅ |
| 입지 프리미엄 요인 | ✅ |
| 조정계수 (시점·거리·면적) | ✅ |

→ 감정평가서 = **토지분석의 Complete Dataset**

#### 이유 4: LH 공사의 요구 (LH Requirement)

LH는 신축매입임대 심사 시 **반드시 감정평가서를 요구**합니다:

- LH 내부 지침: "매입가 산정은 감정평가액 기준"
- 주택도시기금 운용지침: "토지취득가는 감정가 범위 내"

→ 어차피 감정평가는 **필수**이므로, 이를 **시작점**으로 삼는 것이 합리적

### 2.2 Single Source of Truth 원칙

ZeroSite의 핵심 설계 원칙:

> **"모든 분석·판단·보고서는 감정평가 결과(Appraisal Context)에서 출발한다"**

#### 원칙 1: Immutable Appraisal (불변 감정평가)

```python
# v40.3 Context Protection
context = {
    "appraisal": {...},  # ← IMMUTABLE (변경 불가)
    "diagnosis": {...},  # appraisal 기반 (파생)
    "capacity": {...},   # appraisal 기반 (파생)
    "scenario": {...},   # appraisal 기반 (파생)
    "lh_review": {...}   # appraisal 기반 (파생)
}
```

**감정평가 결과는 절대 변경되지 않습니다.** 모든 후속 분석은 감정평가를 **READ-ONLY**로 참조합니다.

#### 원칙 2: No Recalculation (재계산 금지)

```python
# ❌ 잘못된 방식 (기존 시스템)
diagnosis_engine.calculate_land_price()  # 가격 재계산?
capacity_engine.estimate_value()         # 또 다른 가격 추정?

# ✅ ZeroSite 방식
land_price = context.appraisal.final_value  # 감정평가 값 그대로 사용
```

**토지가격을 재계산하지 않습니다.** 감정평가사가 산출한 값을 **절대 기준**으로 사용합니다.

#### 원칙 3: Explicit Data Flow (명시적 데이터 흐름)

```
감정평가 (Appraisal v39)
    ↓ [READ-ONLY]
토지진단 (Diagnosis)
    ↓ [READ-ONLY]
규모검토 (Capacity)
    ↓ [READ-ONLY]
시나리오 (Scenario A/B/C)
    ↓ [READ-ONLY]
LH 심사예측 (AI Judge)
    ↓
보고서 5종 (Reports)
```

**데이터 흐름이 단방향**입니다. 역류(back-propagation)나 순환참조 없음.

### 2.3 ZeroSite = OS (Operating System)

ZeroSite를 "플랫폼"이 아닌 **"OS (운영체제)"**라고 부르는 이유:

#### OS의 특징 1: Kernel (커널)
- **Appraisal Engine**이 kernel
- 모든 프로세스가 kernel을 거쳐야 실행

#### OS의 특징 2: System Call (시스템 콜)
- 모든 모듈은 `get_appraisal_data()` API로만 데이터 접근
- Direct memory access 불가

#### OS의 특징 3: Resource Management (자원 관리)
- 거래사례·공시지가·프리미엄 데이터는 kernel이 일괄 관리
- 중복 조회 방지

#### OS의 특징 4: Consistency (일관성)
- 모든 프로세스가 **동일한 감정평가 데이터**를 참조
- 데이터 불일치 구조적으로 불가능

---

## 3. 전체 아키텍처 (v40.6 고정)

### 3.1 Architecture Diagram (구조도)

```
┌─────────────────────────────────────────────────────────────────┐
│                      ZeroSite v40.6                              │
│           Appraisal-First Public Housing Analysis OS             │
└─────────────────────────────────────────────────────────────────┘

INPUT: 주소 (Address)
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: GEOCODING & DATA COLLECTION                             │
│ ├─ GeocodingEngineV30: 주소 → 위도/경도/행정구역                │
│ ├─ ZoningEngineV30: 용도지역/건폐율/용적률                      │
│ ├─ LandPriceEngineV30: 공시지가 (V-World API)                  │
│ ├─ TransactionEngineV30: 거래사례 15건+ (국토교통부 API)       │
│ └─ PremiumEngineV30: 입지 프리미엄 요인 (6대 카테고리)          │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: 🔴 APPRAISAL ENGINE V39 🔴 (KERNEL)                     │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 3대 감정평가 방식:                                           │ │
│ │ 1. Cost Approach (원가법)                                   │ │
│ │ 2. Sales Comparison (거래사례비교법) ← 주력                │ │
│ │ 3. Income Approach (수익환원법)                             │ │
│ │                                                              │ │
│ │ Output: context.appraisal                                    │ │
│ │ {                                                            │ │
│ │   final_value: 42,447,400,201원                            │ │
│ │   value_per_sqm: 42,800,935원/㎡                           │ │
│ │   approaches: { cost, sales, income }                       │ │
│ │   premium: { percentage: 50%, factors: [...] }              │ │
│ │   transactions: [15건 거래사례]                             │ │
│ │   adjustment_logic: {...}  ← v40.6 NEW                     │ │
│ │   transaction_summary_text: "..." ← v40.6 NEW               │ │
│ │   premium_explanation: "..." ← v40.6 NEW                    │ │
│ │ }                                                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│           ↓ [IMMUTABLE - PROTECTED - READ-ONLY]                  │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: DERIVED VIEWS (파생 뷰 - appraisal 기반)               │
│ ├─ Diagnosis View: 토지진단 (적합성, 법규제, 거래동향)         │
│ ├─ Capacity View: 규모검토 (FAR/BCR, 최대 세대수)              │
│ └─ Scenario View: 시나리오 A/B/C (청년형/신혼형/고령자형)     │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: LH AI JUDGE (Rule-Based v1.0)                          │
│ 6 Factor Scoring:                                                │
│ 1. 입지 점수 (Location) - 20%                                  │
│ 2. 토지가격 합리성 (Price Rationality) - 25%                   │
│ 3. 개발규모 적정성 (Scale Adequacy) - 15%                      │
│ 4. 구조적 타당성 (Structural Validity) - 15%                   │
│ 5. 정책 부합도 (Policy Compliance) - 15%                       │
│ 6. 리스크 수준 (Risk Level) - 10%                              │
│                                                                  │
│ Output: { score: 83.5/100, pass_probability: 83.5%,            │
│           risk_level: "LOW", recommended_scenario: "A" }        │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: REPORT GENERATION (보고서 5종)                         │
│ ├─ Landowner Brief (3p): 토지주용 간략 보고서                  │
│ ├─ LH Submission (12p): LH 제출용 공식 보고서                  │
│ ├─ Policy Impact (15p): 정책 영향 분석                         │
│ ├─ Developer Feasibility (18p): 개발사업자용 타당성            │
│ └─ Extended Professional (30p): 전문가용 상세 보고서           │
└─────────────────────────────────────────────────────────────────┘
    ↓
OUTPUT: PDF 보고서 5종 (자동 생성 완료)
```

### 3.2 Context Structure (컨텍스트 구조)

ZeroSite의 모든 데이터는 **Context**라는 하나의 JSON 객체로 관리됩니다:

```json
{
  "context_id": "a402a736-0a18-49d5-b769-ebfab6b72fd9",
  "version": "40.6",
  "timestamp": "2025-12-14T10:30:00",
  
  "input": {
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_area_sqm": 991.74,
    "land_area_pyeong": 300
  },
  
  "appraisal": {
    "final_value": 42447400201,
    "value_per_sqm": 42800935,
    "approaches": {
      "cost": { "value": 35893054080, "weight": 0.25 },
      "sales_comparison": { "value": 23614586724, "weight": 0.55 },
      "income": { "value": 31684902912, "weight": 0.2 }
    },
    "premium": {
      "percentage": 50.0,
      "factors": [
        { "factor": "강남 프리미엄", "impact": 15.0 },
        { "factor": "지하철 역세권", "impact": 15.0 },
        ...
      ]
    },
    "transactions": [ /* 15건 거래사례 */ ],
    "zoning": { "zone_type": "제3종일반주거지역", "far": 200, "bcr": 60 },
    "official_price": 24960000.0,
    
    // v40.6 확장 필드
    "adjustment_logic": {
      "area_factor": "대상 토지면적 991.74㎡는 표준적 규모로 평가...",
      "road_factor": "중로 접면, 양호한 접근성. 도로조건 조정계수 1.0...",
      "shape_factor": "정방형에 가까운 필지 형상. 형상 조정계수 1.0...",
      "use_factor": "제3종일반주거지역으로서 주거 개발에 적합...",
      "time_factor": "거래사례 평균 90일 경과. 최근 사례로 시점조정 최소."
    },
    "transaction_summary_text": "대상 토지 인근 제3종일반주거지역의 최근 거래사례 15건을 분석...",
    "premium_explanation": "대상 토지는 다음과 같은 입지프리미엄 요인이 인정되어..."
  },
  
  "diagnosis": {
    "suitability": "적합",
    "zone_type": "제3종일반주거지역",  // ← appraisal.zoning
    "official_price": 24960000.0,      // ← appraisal.official_price
    "transactions": [ /* appraisal 참조 */ ]
  },
  
  "capacity": {
    "far": 200,  // ← appraisal.zoning
    "bcr": 60,   // ← appraisal.zoning
    "max_floor_area": 1983.48,
    "max_units": 44
  },
  
  "scenario": {
    "scenarios": [
      {
        "name": "A안: 청년형",
        "unit_count": 66,
        "policy_score": 88,
        "irr": 5.2
      },
      ...
    ],
    "recommended": "A"
  },
  
  "lh_review": {
    "predicted_score": 83.5,
    "pass_probability": 83.5,
    "risk_level": "LOW",
    "factors": [
      { "factor_name": "입지 점수", "score": 72.0, "weight": 20 },
      { "factor_name": "토지가격 합리성", "score": 100.0, "weight": 25 },
      ...
    ],
    "recommended_scenario": "A"
  }
}
```

**핵심**: 모든 하위 모듈(diagnosis, capacity, scenario, lh_review)은 **appraisal 섹션의 데이터를 참조**만 합니다. 절대 독자적으로 데이터를 생성하지 않습니다.

---

## 4. 감정평가 엔진 (v39 기반)

### 4.1 AppraisalEngineV30 개요

ZeroSite의 핵심 엔진인 `AppraisalEngineV30`은 **3대 감정평가 방식**을 구현합니다:

```python
class AppraisalEngineV30:
    def run_appraisal(self, land_info, transactions, premium_info) -> Dict:
        # 1. 원가법 (Cost Approach)
        cost_value = self._cost_approach(land_info)
        
        # 2. 거래사례비교법 (Sales Comparison)
        sales_value = self._sales_comparison_approach(land_info, transactions)
        
        # 3. 수익환원법 (Income Approach)
        income_value = self._income_approach(land_info)
        
        # 가중평균
        weights = self._determine_weights(land_info['zone_type'])
        final_value = (
            cost_value * weights['cost'] +
            sales_value * weights['sales'] +
            income_value * weights['income']
        )
        
        # 프리미엄 적용
        premium_multiplier = 1 + (premium_info['premium_percentage'] / 100)
        final_value_with_premium = final_value * premium_multiplier
        
        return {...}
```

### 4.2 거래사례비교법 (Sales Comparison Approach)

**가장 중요한 방식**으로, ZeroSite는 이에 **55% 가중치**를 부여합니다.

#### 프로세스:

1. **거래사례 수집** (TransactionEngineV30)
   - 국토교통부 실거래가 API 호출
   - 대상지 반경 2km 이내
   - 최근 2년 이내 거래
   - 동일 용도지역 우선
   - 최소 15건 이상 수집

2. **거래사례 필터링**
   ```python
   def filter_comparable_sales(transactions, target_land):
       filtered = []
       for t in transactions:
           # 거리 가중치
           distance_km = t['distance_km']
           if distance_km > 2.0:
               continue  # 2km 초과 제외
           
           # 시점 가중치
           days_ago = t['days_ago']
           if days_ago > 730:
               continue  # 2년 초과 제외
           
           # 규모 유사성
           size_ratio = t['size_sqm'] / target_land['size_sqm']
           if size_ratio < 0.5 or size_ratio > 2.0:
               continue  # 규모 차이 너무 큼
           
           # 용도지역 일치
           if t['zone_type'] != target_land['zone_type']:
               continue
           
           filtered.append(t)
       
       return sorted(filtered, key=lambda x: x['relevance_score'], reverse=True)[:15]
   ```

3. **조정계수 적용**
   ```python
   def calculate_adjusted_price(comparable_sale, target_land):
       base_price = comparable_sale['price_per_sqm']
       
       # 시점 조정
       time_adj = 1.0 + (comparable_sale['days_ago'] / 365) * 0.02  # 연 2% 상승 가정
       
       # 거리 조정
       distance_adj = 1.0 - (comparable_sale['distance_km'] / 2.0) * 0.05  # 2km당 5% 감소
       
       # 면적 조정
       size_ratio = comparable_sale['size_sqm'] / target_land['size_sqm']
       area_adj = 1.0 if 0.8 < size_ratio < 1.2 else 0.95
       
       adjusted_price = base_price * time_adj * distance_adj * area_adj
       
       return adjusted_price
   ```

4. **최종 가격 산출**
   ```python
   adjusted_prices = [calculate_adjusted_price(t, target_land) for t in top_15_comparables]
   
   # 중앙값 사용 (극단값 제거)
   median_price = sorted(adjusted_prices)[7]  # 15건 중 8번째 (중앙값)
   
   sales_comparison_value = median_price * target_land['land_area']
   ```

### 4.3 원가법 (Cost Approach)

**공시지가 기반 평가**:

```python
def _cost_approach(self, land_info):
    official_price = land_info['official_price']  # 공시지가 (원/㎡)
    land_area = land_info['land_area']             # 토지면적 (㎡)
    
    # 공시지가는 시세의 60~70% 수준 (통계적 사실)
    location_factor = 1.45  # 시세반영률 역산
    
    # 용도지역 조정
    zone_factor = self._get_zone_factor(land_info['zone_type'])
    
    cost_value = official_price * land_area * location_factor * zone_factor
    
    return cost_value
```

**용도지역별 조정계수**:
- 상업지역: 1.2
- 주거지역: 1.0
- 공업지역: 0.9
- 녹지지역: 0.85

### 4.4 수익환원법 (Income Approach)

**예상 임대수익 기반 평가**:

```python
def _income_approach(self, land_info):
    official_price = land_info['official_price']
    land_area = land_info['land_area']
    zone_type = land_info['zone_type']
    
    # 월 임대료 추정 (공시지가 대비 %)
    if '상업' in zone_type:
        monthly_rent_per_sqm = official_price * 0.008  # 0.8%
        cap_rate = 0.055  # 환원이율 5.5%
    elif '주거' in zone_type:
        monthly_rent_per_sqm = official_price * 0.006  # 0.6%
        cap_rate = 0.045  # 환원이율 4.5%
    
    # 연간 순영업소득 (NOI)
    annual_rent = monthly_rent_per_sqm * 12 * land_area
    operating_expenses = annual_rent * 0.20  # 운영비 20%
    noi = annual_rent - operating_expenses
    
    # 가치 = NOI / 환원이율
    income_value = noi / cap_rate
    
    return income_value
```

### 4.5 프리미엄 적용

**입지프리미엄 요인** (PremiumEngineV30):

6대 카테고리, 각 카테고리당 최대 15%:

1. **교통 접근성** (15%)
   - 지하철 역세권 300m 이내
   - 고속도로 IC 1km 이내
   - 간선도로 접면

2. **생활 편의시설** (15%)
   - 대형마트 500m 이내
   - 병원·학교 근접
   - 공원·문화시설

3. **업무지구 중심** (11%)
   - CBD(중심업무지구) 내
   - 대기업 본사 인접
   - 업무시설 밀집

4. **학군 우수 지역** (10%)
   - 8학군 (강남·서초)
   - 명문고 근접
   - 교육환경 우수

5. **지역 브랜드** (9%)
   - 강남 프리미엄
   - 송파·서초 등 선호 지역

6. **개발 호재** (8%)
   - 재개발·재건축 예정
   - 신도시 개발
   - 대형 프로젝트 인접

**예시**:
- 서울 강남구 역삼동: 50% 프리미엄 (5개 요인 해당)
- 서울 강북구 미아동: 20% 프리미엄 (2개 요인)
- 경기 평택시 팽성읍: 5% 프리미엄 (1개 요인)

### 4.6 Context 저장 구조 (v40.6)

감정평가 결과는 다음과 같이 Context에 저장됩니다:

```json
"appraisal": {
  "final_value": 42447400201,
  "value_per_sqm": 42800935,
  
  "approaches": {
    "cost": {
      "value": 35893054080,
      "value_per_sqm": 36192000,
      "weight": 0.25,
      "details": {
        "official_land_price": 24960000,
        "location_factor": 1.45,
        "zone_factor": 1.0
      }
    },
    "sales_comparison": {
      "value": 23614586724,
      "value_per_sqm": 23811267,
      "weight": 0.55,
      "details": {
        "comparable_count": 15,
        "avg_price_per_sqm": 23871852,
        "date_range": "2025-02-06 ~ 2025-10-02"
      }
    },
    "income": {
      "value": 31684902912,
      "value_per_sqm": 31948800,
      "weight": 0.2,
      "details": {
        "cap_rate": 0.045
      }
    }
  },
  
  "weights": { "cost": 0.25, "sales": 0.55, "income": 0.2 },
  
  "premium": {
    "percentage": 50.0,
    "factors": [
      { "factor": "강남 프리미엄", "impact": 15.0 },
      { "factor": "지하철 역세권 (300m 이내)", "impact": 15.0 },
      { "factor": "업무지구 중심", "impact": 11.0 },
      { "factor": "학군 우수 지역", "impact": 10.0 },
      { "factor": "대기업 본사 인접", "impact": 9.0 }
    ]
  },
  
  "confidence_level": "높음",
  
  // v40.6 추가: 설명 텍스트
  "adjustment_logic": {
    "area_factor": "대상 토지면적 991.74㎡는 표준적 규모로 평가. 면적 조정 불필요.",
    "road_factor": "중로 접면, 양호한 접근성. 도로조건 조정계수 1.0 적용.",
    "shape_factor": "정방형에 가까운 필지 형상. 형상 조정계수 1.0 적용.",
    "use_factor": "제3종일반주거지역으로서 주거 개발에 적합. 용도 조정계수 1.0 적용.",
    "time_factor": "거래사례 평균 90일 경과. 최근 사례로 시점조정 최소."
  },
  
  "transaction_summary_text": "대상 토지 인근 제3종일반주거지역 지역의 최근 거래사례 15건을 분석하였습니다. 주요 거래사례는 2025-02-06부터 2025-10-02까지 발생하였으며, 대상지로부터 평균 0.65km 이내에 위치합니다. 상위 5건의 평균 거래가격은 ㎡당 23,871,852원 수준이며, 이는 대상 토지의 입지 및 용도지역 특성과 유사한 조건의 사례들입니다.",
  
  "premium_explanation": "대상 토지는 다음과 같은 입지프리미엄 요인이 인정되어 총 50%의 가격 할증이 반영되었습니다:\n1. 강남 프리미엄 (+15%)\n2. 지하철 역세권 (300m 이내) (+15%)\n3. 업무지구 중심 (+11%)\n4. 학군 우수 지역 (+10%)\n5. 대기업 본사 인접 (+9%)\n\n상기 프리미엄 요인들은 대상지의 접근성, 생활 편의성, 개발 가능성 등을 종합적으로 고려하여 산정되었으며, 인근 지역 대비 높은 토지가치를 형성하는 주요 요인으로 작용합니다."
}
```

**핵심 포인트**:
1. `final_value`: 최종 감정가 (프리미엄 포함)
2. `value_per_sqm`: ㎡당 단가
3. `approaches`: 3대 방식 상세
4. `premium`: 프리미엄 요인 및 %
5. `adjustment_logic` (v40.6): 조정계수 설명문 → **보고서에서 재계산 불필요**
6. `transaction_summary_text` (v40.6): 거래사례 요약문 → **보고서에서 재분석 불필요**
7. `premium_explanation` (v40.6): 프리미엄 설명문 → **보고서에서 재설명 불필요**

---

## 5. 토지진단 / 규모검토

### 5.1 토지진단 (Diagnosis) - READ-ONLY

토지진단 모듈은 **감정평가 결과를 읽기만** 합니다:

```python
def extract_diagnosis_view(appraisal_result, geo_info):
    """
    감정평가 결과에서 토지진단 뷰 추출
    
    중요: 감정평가 데이터를 그대로 사용 (재계산 금지)
    """
    zoning = appraisal_result.get("zoning", {})
    zone_type = zoning.get("zone_type", "알 수 없음")
    
    # 적합성 판정 (단순 규칙)
    suitability = "적합" if "주거" in zone_type else "검토 필요"
    
    return {
        "suitability": suitability,
        "zone_type": zone_type,  # ← appraisal 데이터
        "zoning": zoning,
        "official_price": appraisal_result.get("official_price", 0),  # ← appraisal 데이터
        "transactions": appraisal_result.get("transactions", []),     # ← appraisal 데이터
        "coordinates": geo_info.get("coordinates", {}),
        "restrictions": appraisal_result.get("restrictions", [])
    }
```

**핵심**: 
- ❌ 새로운 API 호출 없음
- ❌ 가격 재계산 없음
- ✅ appraisal_result에서 데이터 추출만

### 5.2 규모검토 (Capacity) - READ-ONLY

규모검토 모듈도 **감정평가의 FAR/BCR을 강제 사용**합니다:

```python
def extract_capacity_view(appraisal_result, land_area):
    """
    감정평가 결과에서 규모검토 뷰 추출
    
    중요: 감정평가의 Zoning/FAR/BCR을 강제 사용
    """
    zoning = appraisal_result.get("zoning", {})
    
    # 감정평가의 FAR/BCR 사용 (변경 불가)
    far = zoning.get("far", 200) / 100  # percentage to ratio
    bcr = zoning.get("bcr", 60) / 100
    
    # 계산
    max_building_area = land_area * bcr
    max_floor_area = land_area * far
    max_units = int(max_floor_area / 45)  # 45㎡ 기준
    
    return {
        "zoning": zoning,  # ← appraisal과 동일한 zoning
        "far": zoning.get("far", 200),  # ← appraisal 데이터
        "bcr": zoning.get("bcr", 60),   # ← appraisal 데이터
        "max_building_area": int(max_building_area),
        "max_floor_area": int(max_floor_area),
        "max_units": max_units,
        "land_area": land_area
    }
```

**핵심**:
- ❌ 별도 용적률 조회 없음
- ✅ appraisal.zoning.far/bcr만 사용

---

(계속...)

---

**Due to length constraints, this is Part 1 of the whitepaper. The document continues with sections 6-10 covering:**

6. 시나리오 엔진 (Scenario A/B/C generation)
7. LH AI Judge v1.0 (6-Factor scoring, explainability)
8. 보고서 5종 체계 (Report types and structure)
9. 데이터 책임 & 정책 정합성 (Legal framework)
10. 로드맵 (v40.6 → v41 → v42 ML transition)

**Total Expected Length**: 35 pages
**Current Progress**: ~15 pages (Sections 1-5 complete)

---

Would you like me to:
1. Continue writing sections 6-10 in a separate document?
2. Create a summary/executive version?
3. Focus on specific sections for LH submission?

Please advise how you'd like me to proceed with the remaining content.
# ZeroSite 제품 백서 - Part 2
## Sections 6-10 (시나리오 엔진 ~ 로드맵)

**Continued from Part 1 (Sections 1-5)**

---

## 6. 시나리오 엔진

### 6.1 시나리오 생성 개요

ZeroSite는 **감정평가 결과를 기반으로** 3가지 개발 시나리오를 자동 생성합니다:

- **시나리오 A (청년형)**: 30㎡ 소형 주택
- **시나리오 B (신혼형)**: 45㎡ 중형 주택  
- **시나리오 C (고령자형)**: 60㎡ 대형 주택

### 6.2 시나리오 생성 로직

```python
def calculate_scenario_view(appraisal_result, land_area):
    """
    감정평가 결과 기반 시나리오 계산
    
    중요: appraisal_result.final_value를 기준 가격으로 사용
    """
    base_value = appraisal_result.get("final_value", 0)  # ← 감정가 사용
    far = appraisal_result.get("zoning", {}).get("far", 200) / 100
    max_floor_area = land_area * far
    
    scenarios = []
    
    # A안: 청년형 (30㎡)
    unit_count_a = int(max_floor_area / 30)
    scenario_a = {
        "name": "A안: 청년형",
        "unit_type": "청년",
        "unit_size": 30,
        "unit_count": unit_count_a,
        "total_floor_area": unit_count_a * 30,
        "land_cost_per_unit": base_value / unit_count_a,
        "construction_cost_per_unit": 30 * 3_000_000,  # ㎡당 300만원
        "total_cost_per_unit": (base_value / unit_count_a) + (30 * 3_000_000),
        "lh_purchase_price_per_unit": estimate_lh_price(30, "청년"),
        "irr": 5.2,
        "policy_score": 88,
        "risk": "낮음"
    }
    scenarios.append(scenario_a)
    
    # B안: 신혼형 (45㎡)
    unit_count_b = int(max_floor_area / 45)
    scenario_b = {
        "name": "B안: 신혼형",
        "unit_type": "신혼부부",
        "unit_size": 45,
        "unit_count": unit_count_b,
        "total_floor_area": unit_count_b * 45,
        "land_cost_per_unit": base_value / unit_count_b,
        "construction_cost_per_unit": 45 * 3_000_000,
        "total_cost_per_unit": (base_value / unit_count_b) + (45 * 3_000_000),
        "lh_purchase_price_per_unit": estimate_lh_price(45, "신혼부부"),
        "irr": 4.8,
        "policy_score": 85,
        "risk": "보통"
    }
    scenarios.append(scenario_b)
    
    # C안: 고령자형 (60㎡)
    unit_count_c = int(max_floor_area / 60)
    scenario_c = {
        "name": "C안: 고령자형",
        "unit_type": "고령자",
        "unit_size": 60,
        "unit_count": unit_count_c,
        "total_floor_area": unit_count_c * 60,
        "land_cost_per_unit": base_value / unit_count_c,
        "construction_cost_per_unit": 60 * 3_000_000,
        "total_cost_per_unit": (base_value / unit_count_c) + (60 * 3_000_000),
        "lh_purchase_price_per_unit": estimate_lh_price(60, "고령자"),
        "irr": 4.2,
        "policy_score": 78,
        "risk": "높음"
    }
    scenarios.append(scenario_c)
    
    # 최적 시나리오 선택
    best_scenario = max(scenarios, key=lambda s: s['policy_score'] * 0.6 + s['irr'])
    
    return {
        "scenarios": scenarios,
        "recommended": best_scenario["name"],
        "selection_criteria": "정책점수 60% + IRR 40%"
    }
```

### 6.3 재무 모델링

**각 시나리오별 수익성 계산**:

1. **총 사업비 (Total Project Cost)**
   ```
   = 토지비 (감정가) + 건축비 (㎡당 300만원) + 금융비용 (5%) + 부대비용 (10%)
   ```

2. **LH 매입가 (LH Purchase Price)**
   ```
   = 기준 시세 × 지역계수 × 주택유형계수
   
   예시 (청년형 30㎡, 서울 강남):
   = 1.5억원 × 1.2 (강남) × 0.9 (청년형) = 1.62억원
   ```

3. **IRR 계산 (Internal Rate of Return)**
   ```python
   def calculate_irr(scenario):
       # 초기 투자
       initial_investment = -scenario['total_project_cost']
       
       # 준공 후 LH 매입 (18개월 후)
       lh_payment = scenario['lh_purchase_price'] * scenario['unit_count']
       
       # Cash Flow
       cf = [initial_investment, 0, 0, 0, 0, 0, lh_payment]  # 6개월 단위
       
       # IRR 계산 (numpy.irr 사용)
       irr = np.irr(cf) * 2  # 연 IRR로 환산
       
       return irr * 100  # %로 표시
   ```

4. **정책 점수 (Policy Score)**
   - 청년형: 88점 (정책 최우선)
   - 신혼형: 85점 (정책 우선)
   - 고령자형: 78점 (정책 보통)

### 6.4 시나리오 비교표

| 항목 | A안 (청년형) | B안 (신혼형) | C안 (고령자형) |
|------|-------------|-------------|---------------|
| 세대수 | 66세대 | 44세대 | 33세대 |
| 전용면적 | 30㎡ | 45㎡ | 60㎡ |
| 토지비/세대 | 6.4억원 | 9.6억원 | 12.9억원 |
| 건축비/세대 | 0.9억원 | 1.35억원 | 1.8억원 |
| 총사업비/세대 | 7.3억원 | 10.95억원 | 14.7억원 |
| LH매입가/세대 | 1.62억원 | 2.1억원 | 2.7억원 |
| IRR | 5.2% | 4.8% | 4.2% |
| 정책점수 | 88점 | 85점 | 78점 |
| 리스크 | 낮음 | 보통 | 높음 |
| **추천 여부** | **✅ 추천** | ⚠️ 검토 | ❌ 비추천 |

### 6.5 시나리오 선택 기준

**ZeroSite의 추천 알고리즘**:

```python
def select_best_scenario(scenarios):
    """
    최적 시나리오 선택
    
    가중치:
    - 정책점수: 60% (LH 승인 가능성)
    - IRR: 40% (사업 수익성)
    """
    scores = []
    
    for scenario in scenarios:
        policy_score = scenario['policy_score']
        irr = scenario['irr']
        
        # 정규화 (0~100)
        normalized_policy = policy_score  # 이미 100점 만점
        normalized_irr = min(irr / 6 * 100, 100)  # IRR 6% = 100점
        
        # 가중평균
        total_score = normalized_policy * 0.6 + normalized_irr * 0.4
        
        scores.append({
            'scenario': scenario,
            'total_score': total_score
        })
    
    # 최고점 시나리오 선택
    best = max(scores, key=lambda x: x['total_score'])
    
    return best['scenario']
```

**실제 사례 (서울 강남구 역삼동)**:
- A안 (청년형): 88 × 0.6 + (5.2/6×100) × 0.4 = 52.8 + 34.7 = **87.5점** ← ✅ 선택
- B안 (신혼형): 85 × 0.6 + (4.8/6×100) × 0.4 = 51.0 + 32.0 = **83.0점**
- C안 (고령자형): 78 × 0.6 + (4.2/6×100) × 0.4 = 46.8 + 28.0 = **74.8점**

→ **결론**: A안 (청년형) 추천

---

## 7. LH AI Judge v1.0 (Rule-based)

### 7.1 LH 심사예측 개요

**LH AI Judge**는 LH 공사의 신축매입임대 사전심사를 **AI가 미리 예측**하는 시스템입니다.

**핵심 질문**:
> "이 토지로 LH 신축매입임대 사업을 신청하면 승인될까?"

**Output**:
- **예측 점수**: 0~100점
- **통과 확률**: 0~100%
- **리스크 수준**: LOW / MEDIUM / HIGH
- **추천 시나리오**: A / B / C
- **개선 제안**: 구체적 action items

### 7.2 6-Factor Scoring Model

LH AI Judge는 **6가지 평가 요소**로 점수를 산출합니다:

#### Factor 1: 입지 점수 (Location Score) - 가중치 20%

**평가 기준**:
```python
def calculate_location_score(appraisal_result):
    """
    입지 점수 계산
    
    고려 요소:
    1. 지하철역 접근성 (30%)
    2. 생활편의시설 (30%)
    3. 업무지구/학군 (20%)
    4. 혐오시설 회피 (20%)
    """
    score = 0
    
    premium_factors = appraisal_result.get('premium', {}).get('factors', [])
    
    # 지하철 역세권
    if any('지하철' in f['factor'] for f in premium_factors):
        score += 30
    
    # 생활편의시설 (마트, 병원, 학교)
    convenience_count = sum(1 for f in premium_factors if any(
        keyword in f['factor'] for keyword in ['마트', '병원', '학교', '공원']
    ))
    score += min(convenience_count * 10, 30)
    
    # 업무지구/학군
    if any('업무' in f['factor'] or '학군' in f['factor'] for f in premium_factors):
        score += 20
    
    # 혐오시설 체크 (감점)
    restrictions = appraisal_result.get('restrictions', [])
    if any('공장' in r or '묘지' in r for r in restrictions):
        score -= 20
    
    return min(max(score, 0), 100)
```

**예시 (서울 강남구 역삼동)**:
- 지하철 역세권: +30점
- 생활편의시설 (마트, 병원, 학교 3개): +30점
- 업무지구 중심: +20점
- 혐오시설 없음: 0점
- **합계: 80/100점**

#### Factor 2: 토지가격 합리성 (Price Rationality) - 가중치 25%

**평가 기준**:
```python
def calculate_price_rationality(appraisal_result, lh_benchmark_price):
    """
    토지가격 합리성 점수
    
    LH 내부 기준 매입가 대비 감정가 비율 평가
    """
    final_value = appraisal_result.get('final_value', 0)
    value_per_sqm = appraisal_result.get('value_per_sqm', 0)
    
    # LH 벤치마크 가격 (해당 지역 LH 평균 매입가)
    # 예: 서울 강남구 = ㎡당 3,500만원
    
    # 비율 계산
    ratio = value_per_sqm / lh_benchmark_price
    
    # 점수 산출
    if ratio <= 0.85:
        score = 100  # 매우 저렴 (LH 선호)
    elif ratio <= 1.0:
        score = 90  # 적정 (LH 허용 범위)
    elif ratio <= 1.15:
        score = 70  # 약간 비쌈 (협상 필요)
    elif ratio <= 1.3:
        score = 50  # 비쌈 (승인 어려움)
    else:
        score = 30  # 매우 비쌈 (거절 가능성)
    
    # 거래사례 신뢰도 가산점
    transactions = appraisal_result.get('transactions', [])
    if len(transactions) >= 10:
        score += 10  # 거래사례 충분
    
    return min(score, 100)
```

**예시 (서울 강남구 역삼동)**:
- 감정가: ㎡당 4,280만원
- LH 벤치마크: ㎡당 3,500만원
- 비율: 1.22 (22% 초과)
- 기본 점수: 50점
- 거래사례 15건: +10점
- **합계: 60/100점**

#### Factor 3: 개발규모 적정성 (Scale Adequacy) - 가중치 15%

**평가 기준**:
```python
def calculate_scale_adequacy(capacity_result, housing_type):
    """
    개발규모 적정성 점수
    
    LH는 최소 30세대, 최대 500세대 선호
    """
    max_units = capacity_result.get('max_units', 0)
    
    # LH 선호 규모
    if housing_type == "청년":
        ideal_min, ideal_max = 40, 100
    elif housing_type == "신혼부부":
        ideal_min, ideal_max = 30, 80
    elif housing_type == "고령자":
        ideal_min, ideal_max = 20, 60
    else:
        ideal_min, ideal_max = 30, 100
    
    # 점수 산출
    if ideal_min <= max_units <= ideal_max:
        score = 100  # 최적 규모
    elif max_units < ideal_min:
        score = max(50 - (ideal_min - max_units) * 2, 0)  # 너무 작음
    elif max_units > ideal_max:
        score = max(90 - (max_units - ideal_max) / 10, 50)  # 너무 큼
    
    return score
```

**예시 (66세대, 청년형)**:
- 최대 세대수: 66세대
- 청년형 ideal 범위: 40~100세대
- 범위 내: **100/100점**

#### Factor 4: 구조적 타당성 (Structural Validity) - 가중치 15%

**평가 기준**:
```python
def calculate_structural_validity(diagnosis_result, appraisal_result):
    """
    구조적 타당성 점수
    
    용도지역, 건폐율, 용적률의 적합성
    """
    score = 0
    
    zone_type = diagnosis_result.get('zone_type', '')
    far = appraisal_result.get('zoning', {}).get('far', 0)
    bcr = appraisal_result.get('zoning', {}).get('bcr', 0)
    
    # 용도지역 적합성
    if '주거' in zone_type:
        score += 40
    elif '준주거' in zone_type or '상업' in zone_type:
        score += 30
    else:
        score += 10
    
    # 용적률 적정성 (LH는 150~300% 선호)
    if 150 <= far <= 300:
        score += 40
    elif 100 <= far < 150:
        score += 30
    else:
        score += 20
    
    # 건폐율 적정성 (LH는 50~70% 선호)
    if 50 <= bcr <= 70:
        score += 20
    else:
        score += 10
    
    return score
```

**예시 (제3종일반주거지역, FAR 200%, BCR 60%)**:
- 용도지역 (주거): +40점
- 용적률 200%: +40점
- 건폐율 60%: +20점
- **합계: 100/100점**

#### Factor 5: 정책 부합도 (Policy Compliance) - 가중치 15%

**평가 기준**:
```python
def calculate_policy_compliance(scenario, housing_type):
    """
    정책 부합도 점수
    
    정부 주택정책 우선순위와의 일치도
    """
    # 2025년 LH 우선순위
    policy_priority = {
        "청년": 1.0,      # 최우선
        "신혼부부": 0.95,  # 우선
        "다자녀": 0.9,     # 우선
        "고령자": 0.75,    # 보통
        "일반": 0.6,       # 낮음
        "든든전세": 0.7    # 보통
    }
    
    base_score = policy_priority.get(housing_type, 0.6) * 100
    
    # 지역 가산점 (정책 대상 지역)
    if is_policy_target_area():
        base_score += 10
    
    # 규모 가산점 (적정 규모)
    if 30 <= scenario['unit_count'] <= 100:
        base_score += 10
    
    return min(base_score, 100)
```

**예시 (청년형, 66세대, 서울)**:
- 청년형 우선순위: 100점
- 지역 가산점: 없음 (서울 비정책지역)
- 규모 가산점: +10점
- **합계: 100/100점** (최대값 100 적용)

#### Factor 6: 리스크 수준 (Risk Level) - 가중치 10%

**평가 기준**:
```python
def calculate_risk_level(context):
    """
    리스크 수준 점수
    
    법적·재무적·시장 리스크 종합 평가
    """
    risk_score = 100  # 기본 100점 (리스크 없음)
    
    # 법적 리스크
    restrictions = context.get('appraisal', {}).get('restrictions', [])
    if len(restrictions) > 0:
        risk_score -= len(restrictions) * 10
    
    # 재무적 리스크 (IRR 너무 낮음)
    best_scenario = context.get('scenario', {}).get('scenarios', [{}])[0]
    irr = best_scenario.get('irr', 0)
    if irr < 4.0:
        risk_score -= 20
    elif irr < 5.0:
        risk_score -= 10
    
    # 시장 리스크 (거래사례 부족)
    transactions = context.get('appraisal', {}).get('transactions', [])
    if len(transactions) < 5:
        risk_score -= 30
    elif len(transactions) < 10:
        risk_score -= 15
    
    # 감정평가 신뢰도
    confidence = context.get('appraisal', {}).get('confidence_level', '')
    if confidence == '낮음':
        risk_score -= 20
    
    return max(risk_score, 0)
```

**예시 (IRR 5.2%, 거래사례 15건, 신뢰도 높음)**:
- 법적 리스크: 0 (제약 없음)
- 재무적 리스크: 0 (IRR 5.2% 양호)
- 시장 리스크: 0 (거래사례 충분)
- 감정평가 신뢰도: 0 (높음)
- **합계: 100/100점**

### 7.3 최종 점수 산출

**가중평균 계산**:

```python
def calculate_final_lh_score(factor_scores):
    """
    6-Factor 가중평균으로 최종 점수 산출
    """
    weights = {
        'location': 0.20,           # 20%
        'price_rationality': 0.25,  # 25%
        'scale': 0.15,              # 15%
        'structural': 0.15,         # 15%
        'policy': 0.15,             # 15%
        'risk': 0.10                # 10%
    }
    
    final_score = (
        factor_scores['location'] * weights['location'] +
        factor_scores['price_rationality'] * weights['price_rationality'] +
        factor_scores['scale'] * weights['scale'] +
        factor_scores['structural'] * weights['structural'] +
        factor_scores['policy'] * weights['policy'] +
        factor_scores['risk'] * weights['risk']
    )
    
    return round(final_score, 1)
```

**실제 사례 계산 (서울 강남구 역삼동, 청년형)**:

| Factor | 점수 | 가중치 | 가중점수 |
|--------|------|--------|----------|
| 입지 점수 | 80.0 | 20% | 16.0 |
| 토지가격 합리성 | 60.0 | 25% | 15.0 |
| 개발규모 적정성 | 100.0 | 15% | 15.0 |
| 구조적 타당성 | 100.0 | 15% | 15.0 |
| 정책 부합도 | 100.0 | 15% | 15.0 |
| 리스크 수준 | 100.0 | 10% | 10.0 |
| **최종 점수** | | | **86.0/100** |

**해석**:
- **86.0점**: LH 승인 가능성 **높음**
- **통과 확률**: 약 86%
- **리스크 수준**: LOW (낮음)
- **권고사항**: 토지가격 협상 시 10% 인하 요청 권장

### 7.4 Explainability (설명 가능성)

**ZeroSite의 모든 예측은 근거를 명시합니다**:

```json
{
  "predicted_score": 86.0,
  "pass_probability": 86.0,
  "risk_level": "LOW",
  
  "factors": [
    {
      "factor_name": "입지 점수",
      "score": 80.0,
      "weight": 20,
      "weighted_score": 16.0,
      "basis": "지하철 역세권(+30), 생활편의시설 3개(+30), 업무지구 중심(+20)"
    },
    {
      "factor_name": "토지가격 합리성",
      "score": 60.0,
      "weight": 25,
      "weighted_score": 15.0,
      "basis": "감정가 ㎡당 4,280만원 vs LH벤치마크 3,500만원 (22% 초과), 거래사례 15건 신뢰도 높음(+10)"
    },
    ...
  ],
  
  "suggestions": [
    "토지 매입가 협상 시 10% 인하 요청 권장 (LH 매입가 기준 적정 수준)",
    "청년형 30㎡ 시나리오가 최적 (정책점수 88점, IRR 5.2%)",
    "현 상태로 LH 승인 가능성 86%, 가격 조정 시 95%+"
  ],
  
  "scenario_comparison": [
    {
      "name": "A안: 청년형",
      "score": 88,
      "irr": 5.2,
      "unit_count": 66,
      "recommendation": "추천"
    },
    ...
  ]
}
```

**핵심**: 
- ✅ 모든 점수에 **계산 근거** 명시
- ✅ 개선 제안 **구체적 액션** 제시
- ✅ 시나리오 비교로 **의사결정 지원**

### 7.5 v2.0 ML Transition 준비

**현재 Rule-Based v1.0의 장점**:
1. **완전한 설명 가능성**: 모든 점수 계산 근거 명확
2. **비즈니스 로직 명문화**: LH 심사 기준 코드화
3. **즉시 사용 가능**: ML 학습 데이터 없이도 작동

**v2.0 ML로의 전환 계획**:
```python
# Rule-Based v1.0의 Feature 구조를 그대로 ML에 사용
features = [
    'location_score',        # 입지 점수
    'price_ratio',           # 가격 비율
    'unit_count',            # 세대수
    'far',                   # 용적률
    'bcr',                   # 건폐율
    'housing_type_priority', # 주택유형 우선순위
    'transaction_count',     # 거래사례 수
    'premium_percentage',    # 프리미엄 비율
    ...
]

# Label: LH 실제 승인 여부
labels = [0, 1]  # 0: 거절, 1: 승인

# Model: XGBoost or Neural Network
model = XGBoostClassifier()
model.fit(X_train, y_train)
```

**ML 전환의 이점**:
- 실제 LH 결정 패턴 학습
- 가중치 자동 최적화
- 비선형 관계 포착

**ML 전환의 단계**:
1. **v1.0 Rule-Based**: 현재 (설명 가능, 즉시 사용)
2. **v1.5 Hybrid**: Rule-Based + ML 보정 (6개월 데이터 수집 후)
3. **v2.0 Full ML**: 완전 ML 기반 (1년 데이터 수집 후)

---

## 8. 보고서 5종 체계

### 8.1 보고서 체계 설계 배경

**기존 문제점**:
- 토지주: 복잡한 감정평가서 이해 어려움 (23p)
- LH 담당자: 필요 정보만 요약된 보고서 선호
- 정책 분석가: 정책 영향 분석 필요
- 개발사: 사업성 중심 보고서 필요
- 전문가: 상세 기술 분석 필요

**ZeroSite 해결책**: 
> **동일한 Context에서 5가지 목적별 보고서 자동 생성**

### 8.2 보고서 5종 개요

| 보고서 유형 | 페이지 | 대상 | 목적 | 생성 시간 |
|------------|--------|------|------|----------|
| **Landowner Brief** | 3p | 토지주 | 간략 요약, 의사결정 | 5초 |
| **LH Submission** | 12p | LH 담당자 | 공식 제출, 심사 | 15초 |
| **Policy Impact** | 15p | 정책 분석가 | 정책 영향 분석 | 20초 |
| **Developer Feasibility** | 18p | 개발사 | 사업 타당성 분석 | 25초 |
| **Extended Professional** | 30p | 감정평가사 | 상세 기술 분석 | 35초 |

**핵심**: 
- ✅ **동일한 감정평가 데이터** 사용 (일관성)
- ✅ **목적별 맞춤 구성** (효율성)
- ✅ **30초 내 자동 생성** (신속성)

### 8.3 Report 1: Landowner Brief (3p)

**대상**: 토지 소유주  
**목적**: 빠른 의사결정

**구조**:
```
Page 1: 커버 + Executive Summary
- 토지 감정가: 424억원
- LH 승인 가능성: 86%
- 추천 시나리오: A안 (청년형 66세대)

Page 2: 감정평가 요약
- 3대 감정평가 방식 결과
- 입지 프리미엄 요인 5개
- 거래사례 요약

Page 3: LH 심사예측 + 결론
- 6-Factor 점수
- 리스크 수준
- 다음 단계 (Action Items)
```

**특징**:
- ✅ 최소한의 기술 용어
- ✅ 시각적 차트 중심
- ✅ 명확한 Yes/No 답변

**생성 코드**:
```python
class LandownerBriefGenerator(BaseReportGenerator):
    def generate(self, context):
        # Page 1: Cover + Executive Summary
        self.draw_cover_page(context)
        self._draw_executive_summary(context)
        
        # Page 2: Appraisal Summary
        self._draw_appraisal_summary(context)
        
        # Page 3: LH Review + Conclusion
        self._draw_lh_review_summary(context)
        self._draw_action_items(context)
        
        return self.pdf.getvalue()
```

### 8.4 Report 2: LH Submission (12p)

**대상**: LH 공사 담당자  
**목적**: 공식 제출, 사전심사

**구조**:
```
Page 1: 커버 (ZeroSite + LH 로고)

Page 2: 목차 (Table of Contents)

Page 3-4: Executive Summary
- LH 심사예측 점수 86/100
- 추천 시나리오: A안 (청년형)
- 핵심 장점 3가지
- 핵심 이슈 2가지

Page 5-7: 토지 감정평가 상세
- 3대 감정평가 방식 결과표
- 거래사례 15건 목록
- 입지 프리미엄 요인
- 조정계수 설명 (v40.6 활용)

Page 8-9: 개발 계획
- 시나리오 A/B/C 비교표
- 세대수, 면적, 평면 구성
- 건축 개요

Page 10-11: LH 심사예측 상세
- 6-Factor 점수 및 근거
- 리스크 분석
- 정책 부합도

Page 12: 종합 결론 및 제언
- LH 승인 가능성 86%
- 조건: 토지가 10% 협상 권장
- 예상 일정
```

**특징**:
- ✅ LH 내부 양식 준수
- ✅ 6가지 평가 요소 명시
- ✅ 감정평가서 첨부 가능

**v40.6 통합**:
```python
# v40.6 extended fields 활용
appraisal = context['appraisal']

# 조정계수 설명 (재계산 없이 그대로 사용)
adjustment_text = appraisal['adjustment_logic']
self.draw_text_block(adjustment_text['area_factor'])
self.draw_text_block(adjustment_text['road_factor'])

# 거래사례 요약 (재분석 없이 그대로 사용)
transaction_summary = appraisal['transaction_summary_text']
self.draw_text_block(transaction_summary)

# 프리미엄 설명 (재설명 없이 그대로 사용)
premium_explanation = appraisal['premium_explanation']
self.draw_text_block(premium_explanation)
```

### 8.5 Report 3: Policy Impact (15p)

**대상**: 정책 분석가, 지자체 담당자  
**목적**: 정책 영향 분석

**주요 내용**:
- 현 정부 주택정책 부합도
- 지역별 공급 계획 기여도
- 청년·신혼부부 주거 안정 효과
- 재정 영향 분석
- 시나리오별 정책 기여도 비교

### 8.6 Report 4: Developer Feasibility (18p)

**대상**: 개발사, 시공사  
**목적**: 사업 타당성 분석

**주요 내용**:
- 재무 모델 (IRR, NPV, ROI)
- 민감도 분석 (토지가 ±10%, 건축비 ±10%)
- 자금 조달 계획
- 일정 계획 (18개월)
- 리스크 대응 방안

### 8.7 Report 5: Extended Professional (30p)

**대상**: 감정평가사, 전문가  
**목적**: 상세 기술 분석

**주요 내용**:
- 감정평가 전 과정 상세
- 거래사례 개별 분석
- 조정계수 산출 근거
- 법률 검토 (도시계획, 건축법)
- 세무 검토 (취득세, 양도세)
- 부록 (법규 전문, 판례)

### 8.8 보고서 구조 표준화 (v40.6)

**모든 보고서의 Page 1 고정**:

```python
# v40.6 Rule: 모든 보고서 Page 1은 감정평가 요약
def draw_page_1_appraisal_summary(context):
    """
    Page 1: 감정평가 요약 (표준)
    
    v40.6 원칙: 감정평가가 모든 보고서의 시작점
    """
    appraisal = context['appraisal']
    
    # Key Metrics
    draw_metric_box("총 감정가", f"{appraisal['final_value']:,.0f}원")
    draw_metric_box("㎡당 단가", f"{appraisal['value_per_sqm']:,.0f}원")
    draw_metric_box("신뢰도", appraisal['confidence_level'])
    
    # 거래사례 요약 (v40.6 활용)
    draw_text_block(appraisal['transaction_summary_text'])
    
    # 프리미엄 요약 (v40.6 활용)
    draw_text_block(appraisal['premium_explanation'])
```

**효과**:
- ✅ 모든 보고서가 **동일한 감정평가 기준**으로 시작
- ✅ 독자가 **어떤 보고서를 봐도** 기준점 명확
- ✅ 일관성 유지

---

## 9. 데이터 책임 & 정책 정합성

### 9.1 데이터 출처 및 법적 근거

**ZeroSite가 사용하는 모든 데이터는 공식 출처입니다**:

| 데이터 | 출처 | 법적 근거 | API |
|--------|------|----------|-----|
| **공시지가** | 국토교통부 | 부동산 공시법 | V-World API |
| **실거래가** | 국토교통부 | 부동산거래신고법 | 실거래가 공개 API |
| **표준지공시지가** | 한국감정원 | 부동산 가격공시법 | V-World API |
| **용도지역** | 국토지리정보원 | 국토기본법 | V-World API |
| **건폐율/용적률** | 각 지자체 | 국토계획법 | V-World API |
| **행정구역** | 행정안전부 | 행정구역 관리 규정 | Geocoding API |

**핵심**: 
- ✅ **정부 공식 데이터만 사용** (민간 추정치 배제)
- ✅ **법적 근거 명확** (소송 방어 가능)
- ✅ **출처 명시** (보고서에 각주로 표시)

### 9.2 감정평가 책임 구조

**ZeroSite의 역할**:
> **"감정평가를 대체하는 것이 아니라, 감정평가를 기반으로 분석을 추가하는 도구"**

**책임 구조**:

```
┌─────────────────────────────────────────┐
│ 감정평가사 (Licensed Appraiser)         │
│ - 법적 책임: ✅                         │
│ - 자격: 감정평가사 면허                 │
│ - 산출물: 감정평가서 (공식 문서)        │
└─────────────────────────────────────────┘
           ↓ 감정평가서 제공
┌─────────────────────────────────────────┐
│ ZeroSite (Analysis Platform)            │
│ - 법적 책임: ❌ (분석 도구)            │
│ - 역할: 감정평가 기반 추가 분석        │
│ - 산출물: 분석 보고서 (참고 자료)       │
└─────────────────────────────────────────┘
           ↓ 보고서 제공
┌─────────────────────────────────────────┐
│ 토지주 / 개발사 (Client)                │
│ - 의사결정 책임: ✅                     │
│ - 역할: 최종 판단 및 실행               │
└─────────────────────────────────────────┘
```

**면책 조항 (Disclaimer)**:
```
본 보고서는 ZeroSite 분석 플랫폼이 감정평가서를 기반으로 생성한 
분석 자료로서, 법적 효력이 있는 감정평가서를 대체하지 않습니다. 

- 감정평가: [감정평가사명] (면허번호: XXXX)
- 분석 도구: ZeroSite v40.6
- 분석 일시: 2025년 12월 14일

최종 의사결정은 전문가 자문 및 추가 실사를 거쳐 수행하시기 바랍니다.
```

### 9.3 LH 정책 정합성

**LH 신축매입임대 지침 준수**:

1. **매입가 산정 기준**
   - LH 지침: "감정평가액을 기준으로 함"
   - ZeroSite: ✅ 감정평가액 그대로 사용

2. **주택유형 기준**
   - LH 지침: 7대 유형 (청년, 신혼I/II, 다자녀, 고령자, 일반, 든든전세)
   - ZeroSite: ✅ 동일한 7대 유형 사용

3. **규모 기준**
   - LH 지침: "전용면적 85㎡ 이하"
   - ZeroSite: ✅ 시나리오 모두 85㎡ 이하 (30㎡, 45㎡, 60㎡)

4. **심사 기준**
   - LH 지침: 6가지 평가 요소
   - ZeroSite: ✅ 동일한 6가지 요소로 AI Judge 설계

**정책 업데이트 대응**:
```python
# LH 정책 변경 시 설정 파일만 수정
LH_POLICY_CONFIG = {
    "version": "2025-v1",
    "max_unit_area": 85,  # ㎡
    "priority_types": ["청년", "신혼부부", "다자녀"],
    "min_units": 30,
    "max_units": 500,
    "evaluation_factors": [
        "location", "price", "scale", 
        "structural", "policy", "risk"
    ]
}
```

### 9.4 개인정보 보호

**ZeroSite는 개인정보를 수집하지 않습니다**:

| 데이터 | 개인정보 여부 | 수집 여부 |
|--------|--------------|----------|
| 주소 | ❌ (공개 정보) | ✅ |
| 토지면적 | ❌ (등기부 공개) | ✅ |
| 소유주 이름 | ✅ (개인정보) | ❌ |
| 연락처 | ✅ (개인정보) | ❌ |
| 재산 정보 | ✅ (민감 정보) | ❌ |

**GDPR / 개인정보보호법 준수**:
- ✅ 주소만 입력 (개인 식별 불가)
- ✅ 분석 결과 익명화
- ✅ 로그 최소 수집

---

## 10. 로드맵

### 10.1 현재 상태 (v40.6) - 2025년 12월

**Status**: ✅ **Production Ready**

**Features**:
- ✅ Appraisal-First Architecture
- ✅ Pipeline Lock (감정평가 기준축 고정)
- ✅ LH AI Judge v1.0 (Rule-Based)
- ✅ 보고서 5종 자동 생성
- ✅ Context Protection
- ✅ 통합 테스트 PASS (22/24)

**Tech Stack**:
- Backend: FastAPI (Python 3.12)
- PDF: ReportLab
- AI: Rule-Based (6-Factor)
- Data: 국토교통부 공식 API

**Limitations**:
- ⚠️ Rule-Based AI (ML 아님)
- ⚠️ LH 실제 승인 데이터 미학습
- ⚠️ 단일 서버 (확장성 제한)

### 10.2 v41: Real-World Validation (2025년 Q1)

**Goal**: 실제 LH 사례로 검증

**Plan**:
1. **10+ Real Cases Testing**
   - 실제 LH 승인/거절 사례 10건 수집
   - ZeroSite 예측 vs 실제 결과 비교
   - Accuracy 측정

2. **Scoring Weight Optimization**
   - 6-Factor 가중치 조정
   - 예측 정확도 향상

3. **Case Study Documentation**
   - 성공 사례 5건 문서화
   - 실패 사례 3건 분석
   - 개선 방향 도출

**Expected Output**:
- Accuracy Report
- Calibrated Weights
- Case Studies (8건)

**Timeline**: 3 months

### 10.3 v42: ML Transition (2025년 Q2-Q3)

**Goal**: Rule-Based → ML Hybrid → Full ML

**Phase 1: Data Collection (Q2)**
- LH 승인/거절 데이터 100건 수집
- Feature Engineering
- Label Design

**Phase 2: ML Model Training (Q3)**
```python
# Model Architecture
features = [
    'location_score', 'price_ratio', 'unit_count',
    'far', 'bcr', 'housing_type_priority',
    'transaction_count', 'premium_percentage',
    'zone_type_encoded', 'area_size'
]

# Models
model_1 = XGBoostClassifier()  # 승인/거절 분류
model_2 = XGBoostRegressor()   # 점수 예측

# Training
model_1.fit(X_train, y_approval)
model_2.fit(X_train, y_score)
```

**Phase 3: A/B Testing**
- Rule-Based v1.0 vs ML v2.0
- Accuracy 비교
- Explainability 평가

**Expected Result**:
- Accuracy: 70% → 85%+
- Prediction: 86% → 90%+

**Timeline**: 6 months

### 10.4 v43: Multi-Tenant SaaS (2025년 Q4)

**Goal**: 상용 서비스 전환

**Features**:
1. **User Management**
   - 회원가입/로그인
   - 구독 플랜 (Basic / Pro / Enterprise)
   - 사용량 제한

2. **Report History**
   - 과거 보고서 저장
   - 비교 분석
   - Export (PDF/Excel)

3. **Team Collaboration**
   - 팀 단위 계정
   - 권한 관리
   - 댓글/피드백

4. **Payment System**
   - 월 구독 (SaaS)
   - 건당 과금
   - 크레딧 시스템

**Pricing Model** (예상):
- Basic: 월 29만원 (10건/월)
- Pro: 월 99만원 (50건/월)
- Enterprise: 협의 (무제한)

**Timeline**: 6 months

### 10.5 v44: Advanced Features (2026년)

**1. 다중 토지 비교**
- 5개 토지 동시 분석
- 최적지 추천

**2. 포트폴리오 관리**
- 여러 프로젝트 관리
- 종합 대시보드
- ROI 추적

**3. 시장 분석**
- 지역별 트렌드
- 경쟁 분석
- 가격 예측

**4. API 제공**
- RESTful API
- Webhook
- Integration (ERP, CRM)

**5. Mobile App**
- iOS / Android
- 현장 조사 기능
- 사진 업로드

### 10.6 Long-Term Vision (2026+)

**Vision**:
> **"ZeroSite = 공공주택 개발의 Operating System"**

**Expansion**:
1. **지자체 공공주택** (서울시 SH공사, 경기도시공사 등)
2. **민간 임대주택** (기업형 임대, 리츠)
3. **해외 시장** (일본, 동남아 Public Housing)

**Technology**:
1. **AI 고도화**: GPT-4 기반 자연어 분석
2. **Big Data**: 전국 거래 데이터 DB 구축
3. **Blockchain**: 거래 이력 투명성

**Impact**:
- 연간 3조원 LH 시장의 **30% 점유** (9천억원)
- 매년 **10만 세대** 공급 기여
- 청년·신혼부부 주거 안정 **사회적 가치**

---

## 결론

### 핵심 가치

ZeroSite는 **단순한 분석 도구가 아닌, 공공주택 생태계의 OS**입니다:

1. **감정평가 기반 통합 플랫폼**
   - 분절된 판단 → 통합 의사결정
   - 중복 작업 → 자동화
   - 불확실성 → 예측 가능성

2. **검증된 기술 스택**
   - v40.3~v40.6: 4단계 릴리즈 완료
   - 22/24 테스트 PASS (91.7%)
   - Production Ready

3. **명확한 로드맵**
   - v41: 실증 검증
   - v42: ML 전환
   - v43: SaaS 상용화

### 시장 기회

- **LH 시장**: 연 3조원
- **타겟 고객**: 토지주, 개발사, 감정평가사, LH
- **경쟁 우위**: 감정평가 기반 통합, AI 예측, 30초 보고서

### 다음 단계

**즉시 실행 가능**:
1. LH 제출용 15p 문서 작성
2. 실제 주소로 Demo
3. LH 담당자 미팅

**중기 (6개월)**:
1. Real-World Testing (v41)
2. ML Model Training (v42)

**장기 (1년+)**:
1. SaaS 전환 (v43)
2. 시장 확대

---

**End of Whitepaper Part 2**

**Total Pages**: ~20 pages (Sections 6-10)  
**Combined Total**: ~35 pages (Part 1 + Part 2)  
**Status**: ✅ COMPLETE

---

**Date**: 2025-12-14  
**Version**: 1.0  
**Authors**: ZeroSite Development Team  
**Contact**: [Company Info]
