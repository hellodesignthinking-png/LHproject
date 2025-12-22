# 디자인/폰트/색상 개선 계획
# Design/Font/Color Improvement Plan

**작성일**: 2025-12-22  
**상태**: Phase 4.0 - Design Enhancement  
**대상**: 6종 최종 보고서 (Landowner, Quick Check, Financial, LH Technical, All-in-One, Executive)

---

## 📊 현황 분석

### ✅ 완료된 작업 (Phase 3 완료)
- ✅ Module HTML → Final Report 데이터 흐름 100% 완료
- ✅ N/A 제로 달성 (6/6 reports, 0 N/A)
- ✅ vLAST KPI 추출 파이프라인 통합
- ✅ 기본 디자인 시스템 적용
- ✅ ZEROSITE 워터마크 & 저작권 푸터

### 📝 현재 디자인 요소

#### 폰트 (4종)
1. **'Noto Sans KR', 'Malgun Gothic', sans-serif** (본문 기본)
2. **'Courier New', monospace** (숫자 표시)
3. **'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif** (일부 섹션)
4. **'Noto Sans KR', sans-serif** (강조)

#### 색상 (59개 - 너무 많음!)
주요 색상:
- 파랑: `#007bff`, `#2563EB`, `#3B82F6` (브랜드)
- 녹색: `#10B981`, `#065F46` (긍정/사업성)
- 회색: `#333`, `#666`, `#1F2937` (텍스트)
- 기타: `#EA580C`, `#F59E0B` (강조)

#### 폰트 크기 (12종)
- 11px ~ 24px, 1.2em

---

## 🎯 개선 목표

### 1. 폰트 통일
**문제**: 4종 폰트 혼용으로 일관성 부족  
**해결**:
- **Primary**: `'Pretendard', 'Noto Sans KR', sans-serif` (웹 폰트)
- **Monospace**: `'JetBrains Mono', 'Courier New', monospace` (숫자)
- **Fallback**: `'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif`

### 2. 색상 팔레트 단순화
**문제**: 59개 색상 → 유지보수 어려움  
**해결**: 보고서별 브랜드 색상 + 공통 팔레트

#### 공통 색상 시스템
```css
/* Primary Colors */
--color-primary: #2563EB;        /* 파랑 (정보) */
--color-success: #10B981;        /* 녹색 (긍정) */
--color-warning: #F59E0B;        /* 노랑 (주의) */
--color-danger: #EF4444;         /* 빨강 (위험) */
--color-neutral: #64748B;        /* 회색 (중립) */

/* Text Colors */
--color-text-primary: #1F2937;
--color-text-secondary: #64748B;
--color-text-muted: #9CA3AF;

/* Background Colors */
--color-bg-primary: #FFFFFF;
--color-bg-secondary: #F9FAFB;
--color-bg-accent: #EFF6FF;
```

#### 보고서별 브랜드 색상
| 보고서 | 메인 색상 | 그라데이션 |
|--------|-----------|-----------|
| Landowner Summary | `#2563EB` (파랑) | `#EFF6FF → #DBEAFE` |
| Quick Check | `#F59E0B` (노랑) | `#FFFBEB → #FEF3C7` |
| Financial | `#10B981` (녹색) | `#ECFDF5 → #D1FAE5` |
| LH Technical | `#374151` (회색) | `#F9FAFB → #F3F4F6` |
| All-in-One | `#6B7280` (중회색) | `#F9FAFB → #F3F4F6` |
| Executive | `#8B5CF6` (보라) | `#F5F3FF → #EDE9FE` |

### 3. 타이포그래피 계층 정리
**문제**: 12종 크기 → 과도하게 복잡  
**해결**: 8단계 타이포그래피 스케일

```css
/* Typography Scale */
--text-xs: 11px;     /* 캡션, 주석 */
--text-sm: 12px;     /* 작은 텍스트 */
--text-base: 14px;   /* 본문 (기본) */
--text-lg: 16px;     /* 강조 본문 */
--text-xl: 18px;     /* H3 제목 */
--text-2xl: 20px;    /* H2 제목 */
--text-3xl: 24px;    /* H1 제목 */
--text-4xl: 28px;    /* 커버 페이지 */
```

### 4. 간격(Spacing) 일관성
```css
/* Spacing System */
--space-xs: 8px;
--space-sm: 12px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;
--space-2xl: 48px;
--space-3xl: 64px;
```

### 5. KPI 박스 디자인 개선
**현재 문제**:
- 그라데이션이 과도함
- 가독성 저하
- 인쇄 시 색상 왜곡

**개선안**:
```css
.kpi-summary-box {
    background: var(--color-bg-primary);
    border: 2px solid var(--color-primary);
    border-left: 6px solid var(--color-primary);
    border-radius: 8px;
    padding: var(--space-xl);
    margin: var(--space-xl) 0;
}

.kpi-card {
    background: var(--color-bg-secondary);
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: var(--space-lg);
    transition: box-shadow 0.2s;
}

.kpi-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
```

---

## 🔧 구현 계획

### Phase 4.1: 폰트 개선 (30분)
- [ ] Pretendard 웹폰트 추가 (Google Fonts CDN)
- [ ] JetBrains Mono 숫자 폰트 추가
- [ ] 모든 assembler CSS 폰트 통일

### Phase 4.2: 색상 시스템 통합 (45분)
- [ ] CSS 변수로 색상 팔레트 정의
- [ ] 기존 하드코딩 색상 → CSS 변수로 교체
- [ ] 보고서별 브랜드 색상 클래스 적용

### Phase 4.3: 타이포그래피 스케일 적용 (30분)
- [ ] CSS 변수로 타이포그래피 스케일 정의
- [ ] 모든 h1, h2, h3, p 태그에 스케일 적용
- [ ] line-height 일관성 확보

### Phase 4.4: KPI 박스 디자인 개선 (20분)
- [ ] 과도한 그라데이션 제거
- [ ] 단색 + 테두리 스타일로 변경
- [ ] 호버 효과 추가 (웹 뷰용)

### Phase 4.5: 테스트 & 검증 (15분)
- [ ] 6종 보고서 재생성
- [ ] 시각적 일관성 확인
- [ ] 인쇄 미리보기 테스트

---

## 📈 예상 효과

### ✅ 전
- 4종 폰트 혼용
- 59개 색상 (유지보수 어려움)
- 12종 크기 (과도한 복잡도)
- 그라데이션 과다 사용

### ✅ 후
- 2종 폰트 + fallback
- 15개 핵심 색상 (CSS 변수)
- 8단계 타이포그래피 스케일
- 깔끔한 단색 + 테두리 디자인

### 🎯 핵심 개선 KPI
- 폰트 일관성: **50% → 100%**
- 색상 통일도: **30% → 95%**
- 유지보수성: **중 → 상**
- 인쇄 품질: **중 → 상**
- 브랜드 정체성: **약함 → 강함**

---

## 🚀 Next Steps

1. **우선 진행**: Phase 4.1 (폰트 개선) - 가장 눈에 띄는 효과
2. **두 번째**: Phase 4.2 (색상 시스템) - 브랜드 일관성 확보
3. **세 번째**: Phase 4.3 (타이포그래피) - 가독성 향상
4. **마지막**: Phase 4.4 (KPI 박스) - 전문성 강화

---

**예상 소요 시간**: 2시간 20분  
**우선순위**: P1 (사용자 요청 직접 대응)  
**난이도**: ⭐⭐⭐ (중)
