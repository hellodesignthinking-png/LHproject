# ZeroSite AUTO RESTORE & LOCK - Phase 2 Complete Design

## 🔒 시스템 모드 확정

**작성일**: 2026-01-11  
**단계**: Phase 2 (완전 복원 및 LOCK)  
**목표**: MOC/TEMPLATE 우선 모드 → DATA-FIRST MODE 완전 전환

---

## 0. 시스템 모드 확정

### ✅ DATA-FIRST MODE (최상위)

```
실제 입력 데이터 → 계산 → 결과 → 출력
데이터 없으면 분석 자체를 중단
```

### ❌ DESIGN-FIRST / TEMPLATE-FIRST MODE (금지)

```
❌ 입력 부족 → 템플릿 출력
❌ 샘플/기본값 자동 대체
❌ 내부 자동 fallback
```

---

## 1. M1 토지·입지 입력 검증 + 연동

### 필수 입력 (Hard Gate)

```python
REQUIRED_FIELDS = {
    "address": "법정동 주소 (NOT NULL)",
    "land_area_sqm": "대지면적 (> 0)",
    "zoning": "용도지역/지구",
    "building_coverage_ratio": "건폐율 (%)",
    "floor_area_ratio": "용적률 (%)",
    "transportation_data": {
        "subway_stations": "지하철역 수",
        "bus_stops": "버스정류장 수"
    },
    "infra_data": {
        "convenience_stores": "편의점 수",
        "hospitals": "병원 수",
        "schools": "학교 수",
        "parks": "공원 수"
    },
    "demographic_data": {
        "one_two_person_ratio": "1-2인 가구 비율 (%)",
        "youth_ratio": "청년층 비율 (%)",
        "rental_ratio": "임차 가구 비율 (%)"
    }
}
```

### 검증 로직

```python
def validate_m1_input(data: Dict) -> Tuple[bool, List[str]]:
    """
    M1 입력 데이터 검증
    
    Returns:
        (valid, missing_fields)
    """
    missing = []
    
    if not data.get("address") or data["address"] in ["없음", "Mock Data", ""]:
        missing.append("address")
    
    if not data.get("land_area_sqm") or data["land_area_sqm"] <= 0:
        missing.append("land_area_sqm")
    
    if not data.get("zoning"):
        missing.append("zoning")
    
    # transportation_data 필수
    transport = data.get("transportation_data", {})
    if not transport or (transport.get("subway_stations", 0) == 0 and transport.get("bus_stops", 0) == 0):
        missing.append("transportation_data")
    
    # infra_data 필수
    infra = data.get("infra_data", {})
    if not infra or all(v == 0 for v in infra.values()):
        missing.append("infra_data")
    
    # demographic_data 필수
    demo = data.get("demographic_data", {})
    if not demo or all(v == 0 for v in demo.values()):
        missing.append("demographic_data")
    
    return (len(missing) == 0, missing)
```

### 동작 규칙

```
❌ 하나라도 NULL/공란이면
→ M2~M6 전부 실행 금지

✅ 출력:
- "M1 DATA MISSING" 상태 안내
- 필수 입력 요청 텍스트
```

---

## 2. M2 토지가치 / 시장 맥락 분석

### 입력 데이터

```python
M2_INPUT = {
    "land_price": "실거래 기준 토지 가격",
    "market_transactions": "주변 거래 데이터 (실제)",
    "redevelopment_status": "재개발/정비 사업 여부",
    "area_growth_rate": "지역 성장률 (실제 통계)"
}
```

### M2의 역할

1. **토지가치 평가**
   - 실거래 기준 가격 분석
   - 주변 비교 사례 분석

2. **지역 시장 구조분석**
   - 경쟁 사업지 현황
   - 임차 수요 구조

3. **장기 성장성 판단**
   - 지역 개발 계획
   - 정책적 우선순위

### 출력 형식

```markdown
입력값 기반 텍스트 + 수치
절대 평균/기본값 출력 금지

예:
"해당 토지는 최근 12개월 실거래 상승률 8.5%를 보이며,
주변 경쟁 사업지는 3건, 임차수요는 1-2인 가구 중심 구조입니다."
```

---

## 3. M3 공급 유형 판단

### 실행 전 확인

```python
def can_execute_m3(m1_result, m2_result) -> bool:
    """M3 실행 가능 여부 판단"""
    if not m1_result or not m1_result.get("address"):
        return False
    
    if not m2_result or not m2_result.get("land_price"):
        return False
    
    return True
```

### 판단 구조 (절대 점수표 아님)

#### A. 입지/수요/시장 구조 요약

```markdown
"본 대상지는 [주소]에 위치하며,
교통: [지하철 N개소, 버스 M개소]
생활: [편의점 X개소, 병원 Y개소]
인구: [1-2인 가구 Z%]
로 구성됩니다."
```

#### B. 유형별 탈락 논리 (항상 먼저 기술)

```python
REJECTION_LOGIC = {
    "신혼희망타운 I형": [
        "학군·공원 취약 + 주차 공간 부족",
        "자녀 출산 시 이주 → 회전율 불안정"
    ],
    "신혼희망타운 II형": [
        "대지 규모 부족 + 학군·공원·주차 모두 부적합",
        "중형 평형 수요 적음 + 입지 선호도 낮음"
    ],
    "다자녀형": [
        "학교 도보 불가 + 공원 부재 + 주차 불가",
        "다자녀 가구 비중 낮음 + 차량 필수"
    ],
    "고령자형": [
        "의료 시설 접근 불가 + 보행 환경 미검증",
        "고령 인구 비중 낮음 + 청년층 중심 생활권"
    ]
}
```

#### C. 최종 결정 유형

```markdown
"본 대상지는 비교 가능한 다른 공급유형이 존재하나,
정책·수요·사업 구조상 청년형 외 선택지가 성립하기 어렵다.

근거:
1. 입지 조건이 청년층의 거주 결정 우선순위와 정확히 일치
2. 인구 구조가 청년 수요를 뒷받침 (1-2인 가구 비중 높음)
3. 사업 구조가 효율적 (소형 평형 중심 고밀)"
```

### 금지 사항

```
❌ 점수 %만 나열
❌ "적합도" 자동 계산
❌ "신뢰도 %" 자동 문구
❌ "추천" 키워드
❌ "자동 판단" 문구
```

---

## 4. M4 건축규모 판단

### 필수 연결

```python
M4_REQUIRED = {
    "m1_data": ["address", "land_area_sqm", "zoning", "bcr", "far"],
    "m3_data": ["selected_supply_type"]
}
```

### 산정 흐름

#### 1. 법정 최대

```python
def calculate_legal_max(land_area, bcr, far):
    """법정 최대 세대수 산정"""
    # 건폐율 기준 건축면적
    building_area = land_area * (bcr / 100)
    
    # 용적률 기준 연면적
    total_floor_area = land_area * (far / 100)
    
    # 전용면적 기준 세대수
    unit_area = 40  # 청년형 기준
    common_ratio = 0.35  # 공용면적 비율
    
    net_area = total_floor_area * (1 - common_ratio)
    legal_max_units = int(net_area / unit_area)
    
    return {
        "building_area": building_area,
        "total_floor_area": total_floor_area,
        "legal_max_units": legal_max_units,
        "calculation_basis": f"용적률 {far}% × 면적 {land_area}㎡"
    }
```

#### 2. 유형 반영 최대

```python
UNIT_AREA_BY_TYPE = {
    "청년형": {"standard": 40, "min": 16, "max": 50},
    "신혼희망타운 I형": {"standard": 50, "min": 36, "max": 60},
    "신혼희망타운 II형": {"standard": 75, "min": 60, "max": 85},
    "다자녀형": {"standard": 95, "min": 85, "max": 120},
    "고령자형": {"standard": 35, "min": 16, "max": 50}
}
```

#### 3. 현실성 조정

```python
def adjust_for_reality(legal_max, supply_type, parking_space):
    """현실성 기반 조정"""
    # 주차 제약 반영
    parking_required = legal_max * PARKING_STANDARDS[supply_type]
    
    if parking_space < parking_required:
        # 주차 가능 세대수로 조정
        adjusted_units = int(parking_space / PARKING_STANDARDS[supply_type])
    else:
        adjusted_units = legal_max
    
    # LH 심사 현실성 (10% 여유)
    recommended_units = int(adjusted_units * 0.9)
    
    return {
        "theoretical_max": legal_max,
        "parking_adjusted": adjusted_units,
        "recommended_units": recommended_units,
        "adjustment_reason": "주차 제약 및 LH 심사 현실성 반영"
    }
```

### 출력 형식

```markdown
법정 최대는 3,000㎡ (용적률 300%)이며,
공급유형 청년형 기준으로 권장 세대수는 22세대입니다.

계산 근거:
- 법정 최대: 용적률 300% × 면적 500㎡ = 연면적 1,500㎡
- 전용면적: 1,500㎡ × (1-0.35) = 975㎡
- 세대수: 975㎡ ÷ 40㎡/세대 = 24세대
- 주차 조정: 24세대 × 0.3대/세대 = 7.2대 (8대 확보 가능)
- 권장 세대수: 22세대 (10% 여유)
```

### 금지 사항

```
❌ 주차 0대 자동 출력
❌ 임의 세대수 자동 생성
❌ 계산 과정 없는 "카드 결과만"
❌ 고정 20세대/26세대
```

---

## 5. M5 사업성 분석

### 필수 연결

```python
M5_REQUIRED = {
    "m4_data": ["recommended_units", "total_floor_area"],
    "input_data": ["construction_cost_per_sqm", "land_price"]
}
```

### 산정 흐름

#### 1. 비용 구조 산정

```python
def calculate_cost_structure(units, floor_area, land_price, const_cost_per_sqm):
    """비용 구조 상세 산정"""
    # 토지비
    land_cost = land_price
    
    # 공사비
    construction_cost = floor_area * const_cost_per_sqm
    
    # 간접비 (공사비의 20%)
    indirect_cost = construction_cost * 0.2
    
    # 총 사업비
    total_cost = land_cost + construction_cost + indirect_cost
    
    return {
        "land_cost": land_cost,
        "construction_cost": construction_cost,
        "indirect_cost": indirect_cost,
        "total_cost": total_cost,
        "cost_per_unit": total_cost / units,
        "breakdown": {
            "토지비 비중": f"{(land_cost/total_cost)*100:.1f}%",
            "공사비 비중": f"{(construction_cost/total_cost)*100:.1f}%",
            "간접비 비중": f"{(indirect_cost/total_cost)*100:.1f}%"
        }
    }
```

#### 2. 수익 구조 산정

```python
def calculate_revenue_structure(units, floor_area, lh_purchase_price_per_sqm):
    """수익 구조 상세 산정"""
    # LH 매입가
    total_revenue = floor_area * lh_purchase_price_per_sqm
    
    # 연간 임대수익 (LH 임대료 기준)
    annual_rent_per_unit = 300000 * 12  # 월 30만원
    annual_rent = annual_rent_per_unit * units
    
    return {
        "total_revenue": total_revenue,
        "revenue_per_unit": total_revenue / units,
        "annual_rent": annual_rent,
        "rent_per_unit": annual_rent_per_unit
    }
```

#### 3. 지표 계산

```python
def calculate_financial_metrics(cost, revenue, annual_rent, years=20):
    """NPV 중심 재무 지표 계산"""
    # NPV 계산 (할인율 5%)
    discount_rate = 0.05
    npv = -cost["total_cost"]
    for year in range(1, years + 1):
        npv += annual_rent / ((1 + discount_rate) ** year)
    npv += revenue["total_revenue"] / ((1 + discount_rate) ** years)
    
    # IRR 계산 (간이)
    irr = ((revenue["total_revenue"] + annual_rent * years) / cost["total_cost"] - 1) / years
    
    # ROI 계산
    roi = ((revenue["total_revenue"] - cost["total_cost"]) / cost["total_cost"]) * 100
    
    return {
        "npv": npv,
        "irr": irr * 100,
        "roi": roi,
        "breakeven_years": cost["total_cost"] / annual_rent
    }
```

### 출력 구조

```markdown
비용 구조:
- 총 사업비: 4,500,000,000원
  - 토지비: 2,000,000,000원 (44.4%)
  - 공사비: 2,000,000,000원 (44.4%)
  - 간접비: 500,000,000원 (11.1%)

수익 구조:
- LH 매입가: 5,000,000,000원
- 연간 임대수익: 250,000,000원 (22세대 × 월 30만원 × 12개월)

재무 지표:
- NPV: +43,200,000원 (할인율 5%, 20년 기준)
- IRR: 0.72%
- ROI: 1.45%
- 손익분기: 18.0년

리스크:
- 주차 공간 부족으로 입주자 불편 가능
- 주변 임대료 상승 시 LH 임대료 경쟁력 약화 우려
```

### 금지 사항

```
❌ 구버전 결과
❌ N/A 기준 자동
❌ IRR=0.0만 나열
❌ 계산 근거 없는 숫자만
```

---

## 6. M6 종합 판단

### 필수 연결

```python
M6_REQUIRED = {
    "m1_data": ["address", "land_area_sqm", "zoning"],
    "m2_data": ["market_analysis"],
    "m3_data": ["selected_supply_type"],
    "m4_data": ["recommended_units"],
    "m5_data": ["npv", "irr", "roi"]
}
```

### 판단 프레임

#### 1. 정책 적합성

```markdown
LH 청년 주거 안정 정책 우선순위 부합
청년형 신축매입임대는 정책 부합도 가장 높음
신혼·다자녀형 대비 우선순위 상위
```

#### 2. 사업 안정성

```markdown
NPV 양수(+43,200,000원)로 사업성 확보
IRR 0.72%, ROI 1.45%로 안정적 수익 구조
소형 평형 다수 세대 구조로 임대수익 안정
```

#### 3. 운영 리스크

```markdown
주차 공간 부족으로 입주자 불편 가능
주변 임대료 상승 시 경쟁력 약화 우려
생활 인프라 부족 시 청년 만족도 저하
```

#### 4. 리스크 관리방안

```markdown
주차 불가 조건 사전 고지 (차량 비보유 청년 대상)
LH 임대료는 시세 대비 30-40% 저렴하므로 경쟁력 유지
최소 생활 편의시설 확보되어 있음
```

#### 5. 조건부 판단

```python
DECISION_TYPES = {
    "GO": "전 조건 충족, 즉시 진행 가능",
    "조건부 GO": "일부 리스크 존재, 보완 후 진행 권장",
    "재검토 필요": "중대 리스크 존재, 추가 검토 필요",
    "STOP": "사업 불가, 입지 또는 사업성 근본 문제"
}
```

### 출력 형식

```markdown
## 최종 판단: 조건부 GO

### 판단 근거 (2개 이상)
1. 청년형 공급유형이 입지·수요·사업 구조와 정합
   - 1-2인 가구 비중 65%로 청년 수요 구조적
   - 대중교통 접근 가능 + 역세권 프리미엄 부재
   - 소형 고밀 전략으로 세대수 확보 및 임대수익 안정

2. NPV 양수(+43,200,000원)로 사업성 확보
   - 총 사업비 4,500,000,000원 대비 합리적 수익 구조
   - 연간 임대수익 250,000,000원으로 안정적 현금흐름
   - 손익분기 18.0년으로 장기 운영 가능

### 리스크 (1개 이상)
1. 주차 공간 부족으로 입주자 불편 가능
   - 청년층 차량 비보유율 60%로 치명적이지 않음
   - 입주자 모집 시 '주차 불가' 조건 사전 고지 필요

2. 주변 임대료 상승 시 LH 임대료 경쟁력 약화 우려
   - LH 임대료는 시세 대비 30-40% 저렴하므로 경쟁력 유지
   - 시세 상승 시 오히려 LH 임대 수요 증가

3. 생활 인프라 부족 시 청년 만족도 저하
   - 최소 생활 편의시설 확보 (편의점·소형 상업)
   - 청년층 배달·온라인 소비 의존도 높아 생활 가능

### 보완방안
- 주차 불가 조건 사전 고지 강화
- M7 커뮤니티 계획 수립 필요
- 입주자 만족도 정기 조사 시행

### 판단 신뢰도
높음 (입지·수요·사업 정합성 확보)
```

### 금지 사항

```
❌ 자동 GO 출력
❌ 점수표 위주 출력
❌ 근거 없는 등급
❌ 무조건 A등급
```

---

## 🔐 핵심 동작 규칙 (전역 LOCK)

### ❗ MOC/SAMPLE 자동 대체 금지

```python
BLOCKED_VALUES = [
    "POI 0개 기본값",
    "20세대 / 26세대 고정값",
    "구버전 M5 계산기",
    "자동 점수 / 자동 GO",
    "분석 신뢰도 85%",
    "적합도 점수",
    "최고 점수 유형",
    "Mock Data",
    "Sample Data",
    "템플릿 기본값"
]

def detect_moc_data(data: Any) -> bool:
    """MOC/SAMPLE 데이터 감지"""
    data_str = str(data)
    for blocked in BLOCKED_VALUES:
        if blocked in data_str:
            logger.error(f"🔴 MOC DATA DETECTED: {blocked}")
            return True
    return False
```

### ❗ FallBack 금지

```python
def handle_data_missing(missing_fields: List[str]) -> Dict:
    """데이터 부족 시 처리"""
    return {
        "error": True,
        "error_type": "DATA_MISSING",
        "message": "필수 입력 데이터가 부족하여 분석을 수행할 수 없습니다.",
        "missing_fields": missing_fields,
        "action": "데이터 입력 요청",
        "output": "❌ 계산/판단/결과 없음"
    }
```

### ❗ 디자인은 데이터 이후

```
1. 데이터 확인
2. 검증 Gate 통과
3. 계산 실행
4. 텍스트 생성
5. 시각화 적용
```

---

## 🧾 공통 출력 템플릿 규칙

### 1) 헤더

```markdown
## ZeroSite Decision OS - M{N} 보고서

**프로젝트**: [프로젝트명]
**주소**: [법정동 주소]
**Context ID**: [UUID 또는 PNU]
**분석일**: 2026년 01월 11일
```

### 2) 입력 요약

```markdown
## 입력 데이터 요약

- 대지면적: 500㎡
- 용도지역: 제2종일반주거지역
- 건폐율: 60%
- 용적률: 250%
- 교통: 지하철 2개소, 버스 5개소
- 생활: 편의점 8개소, 병원 2개소
- 인구: 1-2인 가구 65%, 청년층 35%
```

### 3) 해석형 본문

```markdown
## 분석 결과

본 대상지는 [주소]에 위치하며, [왜 ○○인지]를 문장으로 자세히 설명합니다.

[입지 조건] + [수요 구조] + [사업 구조] 측면에서
[공급유형/건축규모/사업성/판단]이 도출됩니다.

근거는 다음과 같습니다:
1. [근거 1]
2. [근거 2]
```

### 4) 숫자 표시

```markdown
## 계산 결과

- 법정 최대: 25세대
  - 계산식: 용적률 250% × 면적 500㎡ ÷ 전용 40㎡
  
- 권장규모: 22세대
  - 주차 조정: 8대 확보 가능
  - LH 심사 여유: 10% 반영
```

### 5) 리스크 + 보완

```markdown
## 리스크 및 보완방안

### 리스크
1. [리스크 1]
2. [리스크 2]

### 보완방안
1. [보완 1]
2. [보완 2]

### 추가 입력 요구
- [필요한 데이터 1]
- [필요한 데이터 2]
```

### 6) 문서 하단

```markdown
---

본 분석은 **입력된 실제 데이터**를 기반으로 하며,
샘플/MOC/기본값/추정값은 사용되지 않습니다.

**ZeroSite Decision OS**  
**ⓒ ZeroSite by AntennaHoldings | Natai Heum**

System Mode: DATA-FIRST LOCKED
```

---

## ✨ 최종 요약

### 복원 목표

- ✅ M2 포함 모든 모듈이 실제 입력 데이터 기반으로 동작
- ✅ MOC/샘플/템플릿 기반 출력은 절대 발생하지 않음
- ✅ 정확한 의사결정 보고서가 생성

### LOCK 원칙

- 🔒 DATA-FIRST MODE 영구 적용
- 🔒 MOC/SAMPLE/TEMPLATE 전면 차단
- 🔒 FallBack 금지 (데이터 없으면 중단)
- 🔒 디자인은 항상 데이터 이후

---

## 📋 구현 체크리스트

### M1 토지·입지
- [ ] 필수 입력 검증 Gate
- [ ] transportation_data 실제 값 연동
- [ ] infra_data 실제 값 연동
- [ ] demographic_data 실제 값 연동

### M2 토지가치
- [ ] 실거래 기준 가격 분석
- [ ] 주변 거래 데이터 연동
- [ ] 시장 구조 분석 텍스트

### M3 공급유형
- [ ] 점수표 완전 제거
- [ ] 탈락 논리 구현
- [ ] 근거 중심 서술

### M4 건축규모
- [ ] 법정최대 계산
- [ ] 이론최대 계산
- [ ] 권장규모 계산
- [ ] 계산 근거 명시

### M5 사업성
- [ ] 비용 구조 설명
- [ ] 수익 구조 설명
- [ ] NPV/IRR/ROI 계산
- [ ] 리스크 분석

### M6 종합판단
- [ ] 조건부 GO 구현
- [ ] 판단 근거 2개 이상
- [ ] 리스크 1개 이상
- [ ] 보완방안 제시

### MOC/TEMPLATE 차단
- [ ] 전역 검출 함수
- [ ] FallBack 금지 로직
- [ ] 데이터 없으면 중단

---

**END OF AUTO RESTORE & LOCK DESIGN**

**ⓒ ZeroSite by AntennaHoldings | Natai Heum**  
**System Mode: DATA-FIRST LOCKED**  
**Phase: 2 of 2 (Design Complete)**
