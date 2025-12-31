# M3-M6 Template Updates (Remaining Work)

## Status
- ✅ M2: Complete (Site Identity Block + Gangnam removal)
- ⏳ M3-M6: Need Site Identity Block + Context explanations

## M3 Template (m3_classic_supply_type.html)

### Insert after line 414 (end of Executive Summary):
```html
<!-- Site Identity Block -->
<div class="summary-page page-break">
    <h1 class="page-title">대상지 식별 정보</h1>
    
    <div class="info-box" style="background-color: #fff3cd; border-left: 4px solid #ffc107;">
        <p style="font-weight: bold;">본 보고서는 아래 단일 대상지에 대한 공급유형 판단 결과입니다.</p>
    </div>

    <table class="data-table">
        <tr>
            <th>대상지 주소</th>
            <td style="font-weight: bold; color: #0066cc;">{{ meta.address }}</td>
        </tr>
        <tr>
            <th>필지번호 (PNU)</th>
            <td>{{ meta.parcel_id }}</td>
        </tr>
        <tr>
            <th>분석 기준일</th>
            <td>{{ meta.eval_base_date }}</td>
        </tr>
        <tr>
            <th>분석 실행 ID</th>
            <td>{{ meta.run_id }}</td>
        </tr>
    </table>

    <div class="info-box" style="background-color: #e7f3ff; border-left: 4px solid #0066cc;">
        <h3>📍 지역 특성 (마포구 맥락)</h3>
        <p>
            <strong>{{ meta.address }}</strong> 일대는<br>
            ① 홍대·연남·합정 생활권의 청년 1~2인 가구 유입,<br>
            ② 상암 DMC 종사자 주거 수요,<br>
            ③ 기존 원룸·다가구 밀집에 따른 소형 임대 수요가 공존하는 지역입니다.
        </p>
        <p style="font-weight: bold;">
            이에 따라 '<strong>{{ summary.kpi_cards[0].value }} 매입임대</strong>'가 
            가장 균형적인 공급 유형으로 판단됩니다.
        </p>
    </div>
</div>
```

## M4 Template (m4_classic_capacity.html)

### Site Identity Block + B안 설명 강화
```html
<!-- After Executive Summary -->
<div class="summary-page page-break">
    <h1 class="page-title">대상지 식별 정보</h1>
    <table class="data-table">
        <tr><th>대상지 주소</th><td>{{ meta.address }}</td></tr>
        <tr><th>필지번호 (PNU)</th><td>{{ meta.parcel_id }}</td></tr>
        <tr><th>분석 기준일</th><td>{{ meta.eval_base_date }}</td></tr>
        <tr><th>분석 실행 ID</th><td>{{ meta.run_id }}</td></tr>
    </table>

    <div class="info-box">
        <h3>권장안(B안) 선정 이유</h3>
        <p>
            B안({{ summary.kpi_cards[0].value }}세대)은 
            마포구 내 유사 필지 개발 사례 대비
            주차 부담, 공용면적 효율, 임대 운영 안정성 측면에서
            가장 균형적인 대안으로 판단됩니다.
        </p>
        <p style="font-weight: bold; color: #d9534f;">
            ⚠️ A안(과밀)은 마포구 지역 특성상 주차·민원·임대 회전율 측면에서
            운영 리스크가 증가할 가능성이 있습니다.
        </p>
    </div>
</div>
```

## M5 Template (m5_classic_feasibility.html)

### Site Identity Block + M2-M4 연결 설명
```html
<!-- After Executive Summary -->
<div class="summary-page page-break">
    <h1 class="page-title">대상지 식별 정보</h1>
    <table class="data-table">
        <tr><th>대상지 주소</th><td>{{ meta.address }}</td></tr>
        <tr><th>필지번호 (PNU)</th><td>{{ meta.parcel_id }}</td></tr>
        <tr><th>분석 기준일</th><td>{{ meta.eval_base_date }}</td></tr>
    </table>

    <div class="info-box">
        <h3>사업성 분석의 전제</h3>
        <p>
            본 사업성 분석은 M2(토지감정평가) 결과와 M4(건축규모 판단) 결과를 
            전제로 수행되었습니다.
        </p>
        <ul>
            <li>토지가치: M2 평가액 기준</li>
            <li>건축규모: M4 권장안(B안) 기준</li>
            <li>운영 방식: M3 추천 공급유형 기준</li>
        </ul>
        <p style="font-weight: bold;">
            본 사업은 고수익형이 아니라,
            공공 매입임대 목적에 부합하는 안정형 사업 구조로,
            조건부 적정 수준의 사업성으로 판단됩니다.
        </p>
    </div>
</div>
```

## M6 Template (m6_classic_lh_review.html)

### CRITICAL: Complete Rewrite of Final Decision Section

#### 1. Remove ALL Gangnam references
- Find line with "테헤란로" → Remove or change to generic company address

#### 2. Add Site Identity Block (top priority)
```html
<div class="summary-page page-break">
    <h1 class="page-title">대상지 식별 정보</h1>
    <table class="data-table">
        <tr><th>대상지 주소</th><td style="font-weight: bold; color: #0066cc;">{{ meta.address }}</td></tr>
        <tr><th>필지번호 (PNU)</th><td>{{ meta.parcel_id }}</td></tr>
        <tr><th>분석 기준일</th><td>{{ meta.eval_base_date }}</td></tr>
        <tr><th>분석 실행 ID</th><td>{{ meta.run_id }}</td></tr>
    </table>
</div>
```

#### 3. Rewrite Final Decision Text
Find the "최종 판단" section and replace with:
```html
<div class="final-decision-box">
    <h2>최종 LH 판단</h2>
    <p style="font-size: 14pt; line-height: 1.8;">
        본 대상지는 <strong style="color: #0066cc;">{{ meta.address }}</strong>에 위치한 사업지로,
        M2(토지감정평가) ~ M5(사업성 분석) 결과를 종합할 때<br>
        <strong>즉시 매입 확정 대상은 아니나</strong>,<br>
        <strong style="color: #28a745;">조건 충족 시 LH 매입 검토가 가능한 사업지</strong>로 판단됩니다.
    </p>
    
    <div class="score-interpretation">
        <h3>종합 점수 해석</h3>
        <p>
            종합 점수 {{ summary.kpi_cards[0].value }}점은 
            LH 내부 일반 권고 기준(80점)에는 미달하나,
            입지 적합성 및 사업 구조의 안정성을 고려할 때
            <strong>조건부 검토 대상</strong>으로 분류 가능합니다.
        </p>
    </div>
</div>
```

#### 4. Add M2-M5 Story Flow
```html
<div class="module-connection-story">
    <h3>📊 모듈 간 연결 스토리</h3>
    <div class="story-flow">
        <div class="story-step">
            <strong>M2 토지평가</strong> → 
            {{ meta.address }} 기준 감정가 산정
        </div>
        <div class="story-step">
            <strong>M3 공급유형</strong> → 
            지역 특성 기반 {{ summary.kpi_cards[2].value }} 추천
        </div>
        <div class="story-step">
            <strong>M4 건축규모</strong> → 
            {{ summary.kpi_cards[3].value }}세대 권장 (B안)
        </div>
        <div class="story-step">
            <strong>M5 사업성</strong> → 
            IRR {{ summary.kpi_cards[4].value }}, 조건부 적정
        </div>
        <div class="story-step">
            <strong>M6 종합판단</strong> → 
            {{ summary.decision }}
        </div>
    </div>
</div>
```

## Implementation Priority
1. M6 (가장 중요) - 최종 판단 문장 + 강남 제거
2. M3 - 마포구 맥락 설명
3. M4 - B안 설명
4. M5 - M2-M4 연결

## Verification Checklist
- [ ] All templates display {{ meta.address }}
- [ ] No "강남구" or "테헤란로" or "역삼동" anywhere
- [ ] Site Identity Block in all M2-M6
- [ ] Context explanations added
- [ ] Final decision text in M6 mentions actual address
