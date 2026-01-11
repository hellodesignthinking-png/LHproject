# ZeroSite Design System v1.0
**LH 공공기관 결재용 Decision OS**

---

## 📋 문서 개요

### 목적
ZeroSite를 **"웹서비스"가 아니라 LH 실무·결재에 바로 쓰이는 고급 Decision OS**로 격상

### 대상 사용자
- LH 실무자 (토지·건축·사업성 검토)
- 공공기관 결재라인
- 전문 개발자

### 디자인 포지셔닝

#### ❌ ZeroSite가 아닌 것
- 스타트업 랜딩 페이지
- 데이터 대시보드 템플릿
- 일반 부동산 리포트 사이트

#### ✅ ZeroSite가 맞는 것
- **공공기관 결재용 Decision OS**
- **LH 내부 검토 시스템과 같은 무게감**
- **"한 장 한 장이 판단 근거가 되는 화면"**

### 디자인 결정 기준
> **"LH 실무자가 이 화면을 캡처해 결재라인에 올릴 수 있는가?"**

---

## 🎨 1. 컬러 시스템 (Single Authority Palette)

### Primary Colors
```css
--color-deep-navy: #0A1628;
--color-institutional-blue: #1F3A5F;
```

**사용 규칙:**
- 헤더, 타이틀, 핵심 강조
- 버튼 (1페이지 1개 이하)
- 구분선

### Neutral Colors
```css
--color-background-white: #F8F9FB;
--color-background-section: #FFFFFF;
--color-border-light: #E6E8EC;
--color-text-primary: #0A1628;
--color-text-secondary: #5A5F6A;
--color-text-caption: #9CA3AF;
```

**사용 규칙:**
- 배경은 `#F8F9FB` 고정
- 섹션 배경은 `#FFFFFF`
- 텍스트는 3단계 계층만 사용

### Semantic Colors (최소 사용)
```css
--color-positive: #2E7D32;      /* 조건부 GO */
--color-warning: #C62828;       /* 리스크 */
--color-info: #1976D2;          /* 참고 정보 */
--color-neutral: #616161;       /* 중립 */
```

**사용 규칙:**
- 정보 강조 목적으로만 사용
- 디자인 장식 목적 사용 금지
- 배경색 사용 최소화 (라인/아이콘으로 대체)

### 금지 규칙
- ❌ 그라디언트
- ❌ 3개 이상 컬러 동시 사용
- ❌ 높은 채도 컬러
- ❌ 컬러풀한 차트

---

## 🖋 2. 타이포그래피 시스템

### Font Stack
```css
--font-primary: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
--font-secondary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Courier New', monospace;
```

**사용 규칙:**
- 한글 텍스트: Noto Sans KR
- 숫자/지표: Inter
- 코드/데이터: JetBrains Mono

### Typography Hierarchy

#### H1 - Decision Title (최종 판단 타이틀)
```css
font-size: 28px;
font-weight: 700;
line-height: 1.3;
color: var(--color-deep-navy);
letter-spacing: -0.02em;
```

#### H2 - Module Title (모듈 타이틀)
```css
font-size: 22px;
font-weight: 600;
line-height: 1.4;
color: var(--color-institutional-blue);
```

#### H3 - Section (섹션 제목)
```css
font-size: 18px;
font-weight: 600;
line-height: 1.5;
color: var(--color-text-primary);
```

#### H4 - Subsection (하위 섹션)
```css
font-size: 16px;
font-weight: 500;
line-height: 1.5;
color: var(--color-text-primary);
```

#### Body - Paragraph (본문)
```css
font-size: 15px;
font-weight: 400;
line-height: 1.7;
color: var(--color-text-primary);
```

#### Caption - Metadata (메타정보)
```css
font-size: 13px;
font-weight: 400;
line-height: 1.6;
color: var(--color-text-secondary);
```

#### Label - Input/Tag (라벨)
```css
font-size: 14px;
font-weight: 500;
line-height: 1.5;
color: var(--color-text-secondary);
```

#### Number - Metrics (수치 전용)
```css
font-family: var(--font-secondary);
font-size: 20px;
font-weight: 600;
line-height: 1.3;
color: var(--color-deep-navy);
font-variant-numeric: tabular-nums;
```

### 금지 규칙
- ❌ 5단계 이상 계층
- ❌ 폰트 믹스 (본문에 다양한 폰트 혼용)
- ❌ 장식용 폰트
- ❌ 얇은 폰트 (300 이하)

---

## 🧱 3. 레이아웃 시스템 (Report-First Grid)

### Container
```css
max-width: 1200px;
margin: 0 auto;
padding: 0 80px;
```

### Grid System
```css
/* 기본 그리드 */
display: grid;
grid-template-columns: repeat(12, 1fr);
gap: 24px;

/* 2단 레이아웃 */
grid-template-columns: 2fr 1fr;

/* 3단 레이아웃 (지표용) */
grid-template-columns: repeat(3, 1fr);
```

### Spacing Scale
```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-xxl: 48px;
--spacing-xxxl: 64px;
```

**사용 규칙:**
- 섹션 간 간격: `--spacing-xxl` (48px)
- 블록 내 요소 간격: `--spacing-lg` (24px)
- 텍스트 줄 간격: `--spacing-md` (16px)

### 구성 규칙
1. **한 화면 = 하나의 판단**
2. **카드 UI 최소화** (배경색 차이로 구분 금지)
3. **수직 흐름 고정**: 요약 → 근거 → 리스크

---

## 🧩 4. 컴포넌트 라이브러리

### 📌 Header (상단 고정 헤더)

**구성 요소:**
- 프로젝트명 (H2)
- 주소 / 분석 기준일 (Caption)
- Context ID (Caption, 우측 정렬)

**HTML 구조:**
```html
<header class="zs-header">
  <div class="zs-header__container">
    <div class="zs-header__main">
      <h2 class="zs-header__title">M6 LH 종합 판단</h2>
      <p class="zs-header__meta">
        <span>서울특별시 강남구 역삼동 123-45</span>
        <span class="zs-header__divider">|</span>
        <span>분석일: 2026년 01월 11일</span>
      </p>
    </div>
    <div class="zs-header__context">
      <span class="zs-label">Context ID</span>
      <span class="zs-number">1168010100005200012</span>
    </div>
  </div>
</header>
```

**CSS:**
```css
.zs-header {
  background: var(--color-background-section);
  border-bottom: 2px solid var(--color-deep-navy);
  padding: var(--spacing-xl) 0;
  margin-bottom: var(--spacing-xxl);
}

.zs-header__container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 80px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.zs-header__title {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-institutional-blue);
  margin-bottom: var(--spacing-sm);
}

.zs-header__meta {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.zs-header__divider {
  margin: 0 var(--spacing-sm);
  color: var(--color-border-light);
}

.zs-header__context {
  text-align: right;
}
```

---

### 📊 Summary Block (핵심 요약 블록)

**구성 요소:**
- 지표 3~4개
- 배경 없음 / 라인 구분만
- 숫자 강조 (Inter 폰트)

**HTML 구조:**
```html
<section class="zs-summary">
  <div class="zs-summary__item">
    <span class="zs-summary__label">총 세대수</span>
    <span class="zs-summary__value">16세대</span>
  </div>
  <div class="zs-summary__item">
    <span class="zs-summary__label">연면적</span>
    <span class="zs-summary__value">864.00㎡</span>
  </div>
  <div class="zs-summary__item">
    <span class="zs-summary__label">NPV</span>
    <span class="zs-summary__value zs-summary__value--positive">43,200,000원</span>
  </div>
  <div class="zs-summary__item">
    <span class="zs-summary__label">판정</span>
    <span class="zs-summary__value">조건부 GO</span>
  </div>
</section>
```

**CSS:**
```css
.zs-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
  border: 1px solid var(--color-border-light);
  background: var(--color-background-section);
  margin-bottom: var(--spacing-xxl);
}

.zs-summary__item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.zs-summary__label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.zs-summary__value {
  font-family: var(--font-secondary);
  font-size: 20px;
  font-weight: 600;
  color: var(--color-deep-navy);
  font-variant-numeric: tabular-nums;
}

.zs-summary__value--positive {
  color: var(--color-positive);
}

.zs-summary__value--warning {
  color: var(--color-warning);
}
```

---

### 📝 Section (섹션)

**구성 요소:**
- 섹션 제목 (H3)
- 본문 텍스트 (문단형)
- 하위 섹션 (H4)

**HTML 구조:**
```html
<section class="zs-section">
  <h3 class="zs-section__title">정책 적합성 판단</h3>
  <div class="zs-section__content">
    <p>입지는 서울특별시 강남구 역삼동 123-45로, 용도지역은 제2종일반주거지역입니다.</p>
    <p>선정된 공급유형은 청년형으로, LH 공공임대주택 정책에 부합합니다.</p>
  </div>
</section>
```

**CSS:**
```css
.zs-section {
  margin-bottom: var(--spacing-xxl);
}

.zs-section__title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 2px solid var(--color-deep-navy);
}

.zs-section__content {
  line-height: 1.7;
}

.zs-section__content p {
  margin-bottom: var(--spacing-md);
  color: var(--color-text-primary);
}
```

---

### 📊 Table (표)

**구성 요소:**
- 엑셀 같은 단정한 스타일
- 헤더 배경 최소화
- 숫자 우측 정렬

**HTML 구조:**
```html
<table class="zs-table">
  <thead>
    <tr>
      <th>항목</th>
      <th>값</th>
      <th>단위</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>총 세대수</td>
      <td class="zs-table__number">16</td>
      <td>세대</td>
    </tr>
    <tr>
      <td>연면적</td>
      <td class="zs-table__number">864.00</td>
      <td>㎡</td>
    </tr>
  </tbody>
</table>
```

**CSS:**
```css
.zs-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: var(--spacing-xl);
  font-size: 14px;
}

.zs-table thead {
  border-bottom: 2px solid var(--color-deep-navy);
}

.zs-table th {
  padding: var(--spacing-md);
  text-align: left;
  font-weight: 600;
  color: var(--color-text-primary);
  background: var(--color-background-white);
}

.zs-table td {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
}

.zs-table tbody tr:last-child td {
  border-bottom: none;
}

.zs-table__number {
  font-family: var(--font-secondary);
  font-variant-numeric: tabular-nums;
  text-align: right;
}
```

---

### ⚠️ Risk Section (리스크 섹션)

**구성 요소:**
- 좌측 라인 + 경고 아이콘
- 붉은 배경 ❌
- 리스크 항목 리스트

**HTML 구조:**
```html
<section class="zs-risk">
  <h3 class="zs-risk__title">
    <span class="zs-risk__icon">⚠️</span>
    주요 리스크
  </h3>
  <ul class="zs-risk__list">
    <li class="zs-risk__item">
      <strong>공사비 상승 리스크:</strong>
      철근·레미콘 등 주요 자재 가격 변동에 민감합니다.
    </li>
    <li class="zs-risk__item">
      <strong>LH 매입 단가 협의 리스크:</strong>
      LH 감정평가 결과에 따른 단가 하락 가능성이 있습니다.
    </li>
  </ul>
</section>
```

**CSS:**
```css
.zs-risk {
  border-left: 4px solid var(--color-warning);
  padding-left: var(--spacing-lg);
  margin-bottom: var(--spacing-xxl);
}

.zs-risk__title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-warning);
  margin-bottom: var(--spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.zs-risk__icon {
  font-size: 20px;
}

.zs-risk__list {
  list-style: none;
  padding: 0;
}

.zs-risk__item {
  margin-bottom: var(--spacing-md);
  line-height: 1.7;
  color: var(--color-text-primary);
}

.zs-risk__item strong {
  color: var(--color-warning);
  font-weight: 600;
}
```

---

### 🔘 Button (버튼)

**구성 요소:**
- 사각형, 라운드 최소
- 1페이지 1개 이하

**HTML 구조:**
```html
<button class="zs-button zs-button--primary">보고서 다운로드</button>
<button class="zs-button zs-button--secondary">목록으로</button>
```

**CSS:**
```css
.zs-button {
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.zs-button--primary {
  background: var(--color-deep-navy);
  color: white;
}

.zs-button--primary:hover {
  background: var(--color-institutional-blue);
}

.zs-button--secondary {
  background: transparent;
  color: var(--color-deep-navy);
  border: 1px solid var(--color-border-light);
}

.zs-button--secondary:hover {
  background: var(--color-background-white);
}
```

---

## 📄 5. PDF / 출력 최적화

### 워터마크
```css
@media print {
  body::before {
    content: 'ZEROSITE';
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-45deg);
    font-size: 120px;
    font-weight: 900;
    color: rgba(0, 0, 0, 0.03);
    z-index: -1;
    pointer-events: none;
  }
}
```

### 인쇄 최적화
```css
@media print {
  @page {
    size: A4;
    margin: 2cm;
  }

  body {
    background: white;
  }

  .zs-header,
  .zs-section,
  .zs-table {
    break-inside: avoid;
  }

  .zs-button {
    display: none;
  }
}
```

---

## 🔒 6. 금지 디자인 패턴

### 절대 금지
- ❌ KPI 카드 남발
- ❌ 대시보드식 차트 배열
- ❌ 모바일 앱 같은 UI
- ❌ SaaS 랜딩페이지 히어로 섹션
- ❌ 그라디언트 남용
- ❌ 애니메이션 중심 UI

---

## 📌 7. 최종 디자인 선언

> **ZeroSite는 '보여주기 위한 화면'이 아니라
> '판단을 남기기 위한 시스템'이다.
> 모든 디자인은 판단의 무게를 가볍게 만들어서는 안 된다.**

---

## 📝 문서 정보

- **버전:** v1.0
- **작성일:** 2026-01-11
- **작성자:** ZeroSite Design Team
- **상태:** Production Ready

---

**ⓒ ZeroSite by AntennaHoldings | Natai Heum**  
**Design System: ZeroSite Decision OS**
