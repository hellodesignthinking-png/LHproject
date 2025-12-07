# 🚀 Phase 1 Development Plan: Executive Summary & Financial Enhancement

**기간**: Week 1-2  
**우선순위**: HIGH  
**목표**: Executive Summary Dashboard + 재무 분석 심화

---

## 📋 Task 1.1: Executive Summary 1페이지 Dashboard

### 목표:
LH 의사결정자를 위한 **1페이지 종합 대시보드** 추가

### 구현 내용:

#### 1. **종합 스코어카드** (5개 항목)
```python
scorecard = {
    'location_score': 85,  # 입지 경쟁력 (교통/인프라/편의시설)
    'financial_score': 45,  # 재무 안정성 (NPV/IRR/DSCR)
    'market_score': 64,     # 시장 수요 (Demand Score)
    'risk_score': 60,       # 리스크 관리 (Risk Matrix)
    'policy_score': 75      # 정책 적합성 (인센티브 활용도)
}
```

**계산 로직**:
- **입지 경쟁력** (0-100):
  - 교통 접근성: 30% (지하철 도보 거리)
  - 인프라: 30% (학교/마트/공원 근접도)
  - 편의시설: 40% (병원/은행/문화시설)

- **재무 안정성** (0-100):
  - NPV > 0: 100점
  - NPV 0~-50억: 80점
  - NPV -50~-100억: 60점
  - NPV -100~-150억: 40점
  - NPV < -150억: 20점

- **시장 수요** (0-100):
  - Demand Score 그대로 사용

- **리스크 관리** (0-100):
  - High Risk 개수 × -10점
  - Medium Risk 개수 × -5점
  - Low Risk 개수 × -2점
  - 시작점: 100점

- **정책 적합성** (0-100):
  - 활용 가능 프로그램 1개당 +20점
  - 시작점: 20점

#### 2. **핵심 지표 Dashboard**
```
┌─────────────────────────────────────────┐
│ 재무 지표          │ 시장 지표         │
│ CAPEX: 145.18억원  │ Signal: UNDERVALUED│
│ NPV: -142.47억원   │ Temp: STABLE      │
│ IRR: -3388.79%     │ Demand: 64.2/100  │
└─────────────────────────────────────────┘
```

#### 3. **최종 권고안 요약**
```
┌────────────────────────────────────────┐
│ 권고: CONDITIONAL (조건부 진행)         │
│                                        │
│ 조건:                                  │
│ 1. 금리 하락 시 재검토 필요            │
│ 2. 공공 지원 프로그램 확보             │
│ 3. 임대료 상승 전망 재확인             │
└────────────────────────────────────────┘
```

### 구현 단계:

**Step 1**: Context Builder에 스코어카드 계산 함수 추가
```python
def _calculate_scorecard(self, context: Dict) -> Dict:
    """Calculate comprehensive scorecard"""
    return {
        'location_score': self._calc_location_score(context),
        'financial_score': self._calc_financial_score(context),
        'market_score': self._calc_market_score(context),
        'risk_score': self._calc_risk_score(context),
        'policy_score': self._calc_policy_score(context),
        'overall_score': self._calc_overall_score(scores)
    }
```

**Step 2**: Template에 Dashboard 섹션 추가
```html
<!-- Part 0: Executive Summary Dashboard -->
<div class="dashboard-page">
    <h1>Executive Summary</h1>
    
    <!-- Scorecard -->
    <div class="scorecard-grid">
        {% for item in scorecard %}
        <div class="score-item {{ 'excellent' if item.score >= 80 else 'good' if item.score >= 60 else 'fair' if item.score >= 40 else 'poor' }}">
            <div class="score-label">{{ item.label }}</div>
            <div class="score-value">{{ item.score }}/100</div>
            <div class="score-status">{{ item.status }}</div>
        </div>
        {% endfor %}
    </div>
    
    <!-- Key Metrics Dashboard -->
    <div class="metrics-dashboard">
        <div class="metric-col">
            <h3>재무 지표</h3>
            <div class="metric">CAPEX: {{ capex_krw }}억원</div>
            <div class="metric">NPV: {{ npv_krw }}억원</div>
            <div class="metric">IRR: {{ irr_pct }}%</div>
        </div>
        <div class="metric-col">
            <h3>시장 지표</h3>
            <div class="metric">Signal: {{ market_signal }}</div>
            <div class="metric">Temp: {{ market_temp }}</div>
            <div class="metric">Demand: {{ demand_score }}/100</div>
        </div>
    </div>
    
    <!-- Final Recommendation -->
    <div class="recommendation-box">
        <h3>최종 권고안: {{ decision }}</h3>
        <ul>
            {% for condition in conditions %}
            <li>{{ condition }}</li>
            {% endfor %}
        </ul>
    </div>
</div>
```

**Step 3**: CSS 스타일 추가
```css
.dashboard-page {
    page-break-after: always;
    padding: 40px;
}

.scorecard-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    margin: 40px 0;
}

.score-item {
    text-align: center;
    padding: 30px;
    border-radius: 10px;
    background: #f8f9fa;
    border: 2px solid #dee2e6;
}

.score-item.excellent { border-color: #28a745; background: #d4edda; }
.score-item.good { border-color: #007bff; background: #cce5ff; }
.score-item.fair { border-color: #ffc107; background: #fff3cd; }
.score-item.poor { border-color: #dc3545; background: #f8d7da; }

.score-value {
    font-size: 36px;
    font-weight: bold;
    margin: 10px 0;
}

.metrics-dashboard {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    margin: 40px 0;
}

.recommendation-box {
    background: #fff3cd;
    border: 2px solid #ffc107;
    border-radius: 10px;
    padding: 30px;
    margin-top: 40px;
}
```

---

## 📋 Task 1.2: 종합 스코어카드 구현

### 상세 계산 로직:

#### 입지 경쟁력 (Location Score)
```python
def _calc_location_score(self, context: Dict) -> int:
    """
    Calculate location competitiveness score
    
    Factors:
    - Transit Access: 지하철 도보 10분 이내 = 30점
    - Infrastructure: 학교/마트/공원 500m 이내 = 30점
    - Amenities: 병원/은행/문화시설 1km 이내 = 40점
    """
    score = 0
    
    # 기본 점수 (현재는 주소 기반 추정)
    # TODO: 실제 GIS 데이터 연동 시 정확한 계산
    score += 30  # Transit (default: moderate)
    score += 30  # Infrastructure (default: moderate)
    score += 25  # Amenities (default: moderate)
    
    return min(100, score)
```

#### 재무 안정성 (Financial Score)
```python
def _calc_financial_score(self, context: Dict) -> int:
    """
    Calculate financial stability score
    
    Based on:
    - NPV: Primary indicator
    - IRR: Secondary indicator
    - DSCR: Debt coverage (if available)
    """
    npv_krw = context.get('finance', {}).get('npv', {}).get('public_krw', 0) / 100_000_000
    irr_pct = context.get('finance', {}).get('irr', {}).get('public_pct', 0)
    
    # NPV scoring (70% weight)
    if npv_krw > 0:
        npv_score = 100
    elif npv_krw > -50:
        npv_score = 80
    elif npv_krw > -100:
        npv_score = 60
    elif npv_krw > -150:
        npv_score = 40
    else:
        npv_score = 20
    
    # IRR scoring (30% weight)
    if irr_pct > 5:
        irr_score = 100
    elif irr_pct > 3:
        irr_score = 80
    elif irr_pct > 0:
        irr_score = 60
    elif irr_pct > -10:
        irr_score = 40
    else:
        irr_score = 20
    
    final_score = int(npv_score * 0.7 + irr_score * 0.3)
    return final_score
```

#### 시장 수요 (Market Score)
```python
def _calc_market_score(self, context: Dict) -> int:
    """Use Demand Score directly"""
    demand_score = context.get('demand', {}).get('overall_score', 50)
    return int(demand_score)
```

#### 리스크 관리 (Risk Score)
```python
def _calc_risk_score(self, context: Dict) -> int:
    """
    Calculate risk management score
    
    Start from 100, deduct based on risk levels:
    - High Risk: -10 points each
    - Medium Risk: -5 points each
    - Low Risk: -2 points each
    """
    score = 100
    
    risks = context.get('risk_analysis', {}).get('identified_risks', [])
    
    for risk in risks:
        level = risk.get('level', 'medium').lower()
        if level == 'high':
            score -= 10
        elif level == 'medium':
            score -= 5
        elif level == 'low':
            score -= 2
    
    return max(0, score)
```

#### 정책 적합성 (Policy Score)
```python
def _calc_policy_score(self, context: Dict) -> int:
    """
    Calculate policy eligibility score
    
    Based on number of applicable support programs:
    - Each program: +20 points
    - Base score: 20 points
    """
    score = 20
    
    # TODO: Implement policy program checker
    # For now, assume 2-3 programs are applicable
    applicable_programs = 2  # LH 매입약정, 서울시 인센티브
    
    score += applicable_programs * 20
    
    return min(100, score)
```

---

## 📋 Task 1.3-1.6: 재무 분석 심화

### 민감도 분석 (Sensitivity Analysis)

#### 5개 시나리오 정의:
```python
scenarios = {
    'best_case': {
        'rent_multiplier': 1.20,      # 임대료 +20%
        'construction_cost_multiplier': 0.90,  # 건축비 -10%
        'vacancy_rate': 0.02,         # 공실률 2%
        'discount_rate': 0.025        # 할인율 2.5%
    },
    'optimistic': {
        'rent_multiplier': 1.10,      # 임대료 +10%
        'construction_cost_multiplier': 0.95,  # 건축비 -5%
        'vacancy_rate': 0.03,         # 공실률 3%
        'discount_rate': 0.0287       # 할인율 2.87%
    },
    'base_case': {
        'rent_multiplier': 1.00,      # 임대료 기준
        'construction_cost_multiplier': 1.00,  # 건축비 기준
        'vacancy_rate': 0.05,         # 공실률 5%
        'discount_rate': 0.0287       # 할인율 2.87%
    },
    'pessimistic': {
        'rent_multiplier': 0.90,      # 임대료 -10%
        'construction_cost_multiplier': 1.10,  # 건축비 +10%
        'vacancy_rate': 0.08,         # 공실률 8%
        'discount_rate': 0.035        # 할인율 3.5%
    },
    'worst_case': {
        'rent_multiplier': 0.80,      # 임대료 -20%
        'construction_cost_multiplier': 1.20,  # 건축비 +20%
        'vacancy_rate': 0.12,         # 공실률 12%
        'discount_rate': 0.04         # 할인율 4.0%
    }
}
```

### Tornado Diagram 데이터 구조:
```python
tornado_data = {
    'variables': [
        {
            'name': '임대료',
            'base_npv': -142.47,
            'npv_plus_10': -92.47,   # 임대료 +10%
            'npv_minus_10': -192.47  # 임대료 -10%
        },
        {
            'name': '건축비',
            'base_npv': -142.47,
            'npv_plus_10': -172.47,  # 건축비 +10%
            'npv_minus_10': -112.47  # 건축비 -10%
        },
        # ... more variables
    ]
}
```

### 30년 현금흐름표:
```python
def _build_extended_cashflow(self, capex, annual_revenue, annual_opex):
    """Generate 30-year cash flow"""
    cashflows = []
    
    for year in range(1, 31):
        if year == 1:
            # Construction year
            cashflow = -capex
        else:
            # Operating years
            revenue = annual_revenue * (1.02 ** (year - 1))  # 2% annual growth
            opex = annual_opex * (1.015 ** (year - 1))      # 1.5% annual growth
            cashflow = revenue - opex
        
        cashflows.append({
            'year': year,
            'revenue': revenue if year > 1 else 0,
            'opex': opex if year > 1 else 0,
            'noi': cashflow if year > 1 else 0,
            'cumulative': sum([cf for cf in cashflows])
        })
    
    return cashflows
```

### 재무 비율 계산:
```python
def _calculate_financial_ratios(self, context: Dict) -> Dict:
    """Calculate DSCR, LTV, ROI, ROE"""
    
    finance = context.get('finance', {})
    capex = finance.get('capex', {}).get('total_krw', 0)
    noi = finance.get('noi_annual', 0)
    
    # DSCR (Debt Service Coverage Ratio)
    # Assuming 70% LTV, 4% interest, 20-year loan
    loan_amount = capex * 0.7
    interest_rate = 0.04
    annual_debt_service = loan_amount * (interest_rate / (1 - (1 + interest_rate) ** -20))
    dscr = noi / annual_debt_service if annual_debt_service > 0 else 0
    
    # LTV (Loan to Value)
    property_value = capex  # Simplified
    ltv = (loan_amount / property_value) * 100 if property_value > 0 else 0
    
    # ROI (Return on Investment)
    npv = finance.get('npv', {}).get('public_krw', 0)
    roi = (npv / capex) * 100 if capex > 0 else 0
    
    # ROE (Return on Equity)
    equity = capex * 0.3  # 30% equity
    roe = (npv / equity) * 100 if equity > 0 else 0
    
    return {
        'dscr': round(dscr, 2),
        'ltv': round(ltv, 2),
        'roi': round(roi, 2),
        'roe': round(roe, 2)
    }
```

---

## 📁 파일 수정 목록

### 1. Context Builder
**파일**: `app/services_v13/report_full/report_context_builder.py`

**추가 함수**:
- `_calculate_scorecard()`
- `_calc_location_score()`
- `_calc_financial_score()`
- `_calc_market_score()`
- `_calc_risk_score()`
- `_calc_policy_score()`
- `_build_sensitivity_analysis()`
- `_build_tornado_diagram_data()`
- `_build_extended_cashflow()`
- `_calculate_financial_ratios()`

### 2. Template
**파일**: `app/services_v13/report_full/lh_expert_edition_v3.html.jinja2`

**추가 섹션**:
- Part 0: Executive Summary Dashboard (1 page)
- Section 8.3: 민감도 분석 (2-3 pages)
- Section 8.4: Tornado Diagram (1 page)
- Section 8.5: 30년 현금흐름표 (2 pages)
- Section 8.6: 재무 비율 분석 (1 page)

---

## 🧪 테스트 계획

### Unit Tests:
```python
def test_scorecard_calculation():
    """Test scorecard calculation logic"""
    builder = ReportContextBuilder()
    context = {...}  # Sample context
    scorecard = builder._calculate_scorecard(context)
    
    assert 0 <= scorecard['location_score'] <= 100
    assert 0 <= scorecard['financial_score'] <= 100
    assert 0 <= scorecard['overall_score'] <= 100

def test_sensitivity_analysis():
    """Test 5-scenario sensitivity analysis"""
    builder = ReportContextBuilder()
    scenarios = builder._build_sensitivity_analysis(...)
    
    assert len(scenarios) == 5
    assert 'best_case' in scenarios
    assert 'worst_case' in scenarios
```

### Integration Tests:
```python
def test_executive_summary_generation():
    """Test full Executive Summary page generation"""
    context = builder.build_expert_context(
        address="서울시 강남구 역삼동 123",
        land_area_sqm=500.0
    )
    
    assert 'executive_summary' in context
    assert 'scorecard' in context['executive_summary']
    assert len(context['executive_summary']['scorecard']) == 5
```

---

## 📈 예상 결과

### Before (현재):
- Executive Summary: 기본 지표만 나열
- 재무 분석: NPV/IRR/10년 현금흐름
- 의사결정 지원도: 60/100

### After (Phase 1 완료):
- Executive Summary: 1페이지 Dashboard + 스코어카드
- 재무 분석: 
  - NPV/IRR/30년 현금흐름
  - 5개 시나리오 민감도 분석
  - Tornado Diagram
  - DSCR/LTV/ROI/ROE
- 의사결정 지원도: 75/100 (+15)

---

## 🚀 시작!

**다음 작업**: Context Builder에 스코어카드 계산 함수 추가

**예상 완료**: Week 1 (Day 5-7)
