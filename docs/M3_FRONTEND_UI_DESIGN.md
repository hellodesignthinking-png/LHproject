# M3 Frontend UI 설계서 (LH 설득 + 개발 실행 가능)

## 🎯 목표

**M3 결과를 보고 '왜 이 유형인지' 바로 납득시키는 UI**

---

## 📐 UI 구조 (5개 카드)

### 1️⃣ Hero Card (결론 고정)

```tsx
<HeroCard>
  <Title>추천 공급유형</Title>
  <RecommendedType color={getColorByScore(85)}>
    청년 매입임대
  </RecommendedType>
  <Score>
    LH 통과 점수: <Strong>85</Strong> / 100
  </Score>
</HeroCard>
```

**색상 규칙**:
- `85점 이상`: Deep Blue (#0066cc)
- `75~84점`: Blue (#4CAF50)
- `70~74점`: Gray (#999)

---

### 2️⃣ 점수 분해 Card (신뢰 핵심)

```tsx
<ScoreBreakdownCard>
  <Title>평가 항목별 점수</Title>
  <ScoreTable>
    <Row>
      <Label>정책 적합성</Label>
      <Bar value={27} max={30} />
      <Score>27 / 30</Score>
    </Row>
    <Row>
      <Label>입지·수요 일치</Label>
      <Bar value={22} max={25} />
      <Score>22 / 25</Score>
    </Row>
    <Row>
      <Label>토지가격 부담</Label>
      <Bar value={15} max={20} />
      <Score>15 / 20</Score>
    </Row>
    <Row>
      <Label>인허가 리스크</Label>
      <Bar value={13} max={15} />
      <Score>13 / 15</Score>
    </Row>
    <Row>
      <Label>운영 안정성</Label>
      <Bar value={8} max={10} />
      <Score>8 / 10</Score>
    </Row>
  </ScoreTable>
</ScoreBreakdownCard>
```

**막대 그래프 + 숫자 병기**

---

### 3️⃣ 후보 유형 비교 Card

```tsx
<ComparisonCard>
  <Title>후보 유형 비교</Title>
  <ComparisonChart>
    <Bar type="청년 매입임대" value={85} color="#0066cc">
      ██████████ 85
    </Bar>
    <Bar type="신혼부부 매입임대" value={78} color="#4CAF50">
      ████████░░ 78
    </Bar>
    <Bar type="일반 공공임대" value={71} color="#999">
      ███████░░░ 71
    </Bar>
  </ComparisonChart>
</ComparisonCard>
```

**상위 3개만 표시**

---

### 4️⃣ 탈락 사유 Card (중요)

```tsx
<RejectionCard>
  <Title>탈락 유형 및 사유</Title>
  <RejectionList>
    <Item>
      <Icon>❌</Icon>
      <Type>고령자 복지주택</Type>
      <Reason>입지 특성과 주요 수요층 불일치</Reason>
    </Item>
    <Item>
      <Icon>❌</Icon>
      <Type>역세권 청년주택</Type>
      <Reason>토지가격 과도 및 사업성 불안정</Reason>
    </Item>
  </RejectionList>
  <Note>
    ⚠️ LH 실무자의 '반박 포인트 선제 차단'
  </Note>
</RejectionCard>
```

**70점 미만 유형만 표시**

---

### 5️⃣ 자동 생성 서술 Card (보고서 직결)

```tsx
<PersuasionCard>
  <Title>LH 설득 논리 (자동 생성)</Title>
  <Content>
    본 대상지는 도심 접근성과 직주근접성이 우수하여
    청년 매입임대 유형이 정책 적합성 및 운영 안정성 측면에서
    가장 높은 심사 통과 가능성을 보인다.
  </Content>
  <Actions>
    <Button icon="📋" onClick={copyToClipboard}>
      복사
    </Button>
    <Note>M6·보고서에 자동 연계됩니다</Note>
  </Actions>
</PersuasionCard>
```

---

## 🔗 M3 → M4 연결 UX

### ✅ M3 완료 시

```tsx
<CTAButton 
  enabled={m3Status === 'COMPLETED'}
  onClick={navigateToM4}
>
  이 공급유형 기준으로 건축 규모 산정 →
</CTAButton>
```

### ❌ M3 미완료 시

```tsx
<CTAButton 
  disabled={true}
  icon="🔒"
>
  M3 분석 완료 후 진행 가능
</CTAButton>
```

---

## 📊 데이터 흐름

```typescript
// M3 API 호출
const m3Result = await fetch(`/api/reports/m3/${contextId}`);

// 데이터 구조
interface M3Result {
  recommended_type: string;
  lh_pass_score: number;
  ranking: Array<{
    type: string;
    total_score: number;
    policy_score: number;
    location_score: number;
    price_score: number;
    permit_score: number;
    operation_score: number;
    rationale: string;
  }>;
  rejection_reasons: Record<string, string>;
  lh_persuasion_text: string;
}
```

---

## 🎨 디자인 시스템

### 색상

- **Primary (Deep Blue)**: #0066cc (85점 이상)
- **Success (Green)**: #4CAF50 (75~84점)
- **Neutral (Gray)**: #999 (70~74점)
- **Danger (Red)**: #f44336 (탈락)

### 타이포그래피

- **Hero Title**: 32px, Bold
- **Card Title**: 20px, Bold
- **Body**: 16px, Regular
- **Score**: 24px, Bold

---

## 🔧 구현 우선순위

1. ✅ **Hero Card** (가장 중요)
2. ✅ **점수 분해 Card** (신뢰도 확보)
3. ✅ **후보 유형 비교 Card**
4. ✅ **탈락 사유 Card** (LH 설득)
5. ✅ **서술 Card** (보고서 연계)

---

## 🚀 기대 효과

- ✔ **M3 결과를 보고 '왜 이 유형인지' 바로 납득**
- ✔ **M4가 과도해질 수 없는 구조**
- ✔ **M6 종합판단의 신뢰도 급상승**
- ✔ **보고서 없이도 화면만으로 설명 가능**

---

ⓒ ZeroSite by AntennaHoldings | Natai Heum
Module: **M3 Frontend UI Design**
