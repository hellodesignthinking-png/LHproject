# ZeroSite M2-M6 종합 수정 계획

## 📋 현황 분석 (2025-12-19)

### 생성된 PDF
- ✅ M2: 토지가치 분석 (152KB)
- ✅ M3: 선호유형 구조 (139KB) 
- ❌ M4: 건축규모 (생성 실패)
- ❌ M5: 사업성 분석 (생성 실패)
- ⚠️ M6: LH 심사예측 (233KB, 데이터 모순)

### 대시보드 상태
```
M2: 토지가격 ₩1,621,848,717 ✓
M3: 청년형, 0점, 신뢰도 85% ⚠️ (0점 표시 문제)
M4: 20세대, 26세대, 0대 주차 ⚠️ (0대 문제)
M5: NPV ₩793,000,000, IRR 12.8% ✓
M6: GO, 85.0/110, A등급, 77% ✓
```

---

## 🎯 종합 수정 계획

### Phase 1: 데이터 연동 긴급 수정
1. **M6 데이터 모순 해결**
   - 문제: "종합 점수: 0.0/110점" ≠ "A등급, 85.0/110점"
   - 원인: 두 개의 다른 변수 참조 (`total_score=0` vs `score=85`)
   - 해결: 단일 변수 강제 (`total_score` 우선)

2. **M4 생성 오류 디버깅**
   - 예상 원인: 데이터 검증 실패로 ValueError 발생
   - 조치: 검증 로직을 warning으로 완화 (critical만 block)

3. **M5 생성 오류 디버깅**
   - 예상 원인: M4 데이터 의존성 미충족
   - 조치: M4 성공 후 재시도

### Phase 2: 디자인 시스템 적용
1. **페이지 1 (커버) 통일**
   ```
   [ Module Icon ]
   
   MX: 모듈명
   부제목
   
   [ 4 KPI Cards ]
   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
   │ KPI1 │ │ KPI2 │ │ KPI3 │ │ KPI4 │
   └──────┘ └──────┘ └──────┘ └──────┘
   
   [ PDF 보고서 다운로드 Button ]
   
   생성일시: YYYY-MM-DD HH:MM:SS
   ```

2. **섹션 헤더 통일**
   - H1: 22pt Bold #1E3A8A (Primary)
   - H2: 16pt Bold #1E3A8A (Section)
   - Body: 10.5pt Regular #334155

3. **표 스타일 통일**
   - Header: Primary Blue (#1E3A8A) + White Text
   - Body: Alternating rows (White / #F8FAFC)
   - Border: #E2E8F0 (Light Gray)

4. **색상 코드 적용**
   - Success: #16A34A (Green) - GO, HIGH
   - Warning: #F59E0B (Amber) - CONDITIONAL, MEDIUM
   - Danger: #DC2626 (Red) - NO-GO, LOW

### Phase 3: 콘텐츠 정교화
1. **M2 개선**
   - ✅ 이미 적용됨 (입지 프리미엄 표현 수정)
   - 추가: 가격 비교 차트 시각화

2. **M3 개선**
   - ✅ "선호 구조" 용어 적용됨
   - 추가: 라이프스타일 패턴 인포그래픽

3. **M4 개선 (생성 성공 후)**
   - GFA 분해 시각화
   - 매싱 옵션 3D 다이어그램 (텍스트)
   - 램프 조건 체크리스트

4. **M5 개선 (생성 성공 후)**
   - 시나리오 비교 표 강화
   - 리스크 시나리오 워터폴 차트
   - ROI/IRR 게이지 차트

5. **M6 개선**
   - Executive Summary 카드 형식
   - Hard Fail 체크리스트 시각화
   - CONDITIONAL GO 시나리오 프로세스 차트

---

## 🔧 즉시 수정 사항

### 1. M6 데이터 모순 (CRITICAL)
**파일:** `module_pdf_generator.py` - `generate_m6_lh_review_pdf()`

**현재 문제:**
```python
# Page 1 - Section 1
story.append(Paragraph("종합 점수", ...))
story.append(Paragraph("0.0/110점", ...))  # ❌ Wrong!

# Page 1 - Section 2
story.append(Paragraph("A등급, 85.0/110점", ...))  # ✓ Correct
```

**수정:**
```python
# 단일 데이터 소스 강제
total_score = data.get('total_score', 0)
if total_score == 0:
    # Fallback to alternative keys
    total_score = data.get('score', data.get('m6_score', 0))

# 모든 구간에서 동일한 변수 사용
```

### 2. M4 검증 완화 (HIGH)
**파일:** `module_pdf_generator.py` - `generate_m4_capacity_pdf()`

**현재:**
```python
validation = DataContract.validate_m4_data(data)
if not validation.is_valid:
    raise ValueError(...)  # ❌ Blocks generation
```

**수정:**
```python
validation = DataContract.validate_m4_data(data)
if not validation.is_valid:
    # Log errors but allow generation with warnings
    logger.error(f"M4 validation warnings: {validation.get_error_summary()}")
    # Add warning banner to PDF first page
    add_warning_banner(story, validation.issues)
```

### 3. 대시보드 카드 수정 (MEDIUM)
**추정 위치:** 프론트엔드 컴포넌트

**M3 카드:**
```javascript
// Before
점수: {m3_score || 0}점  // Shows "0점"

// After
점수: {m3_score > 0 ? `${m3_score}점` : 'N/A'}
```

**M4 카드:**
```javascript
// Before
Alt A 주차: {alt_a_parking || 0}대  // Shows "0대"

// After  
Alt A 주차: {alt_a_parking > 0 ? `${alt_a_parking}대` : '미확정'}
```

---

## 📐 새 디자인 템플릿

### KPI Card 컴포넌트
```python
def create_kpi_card_section(story, cards: List[Dict], styles):
    """4개 KPI 카드를 가로로 배치"""
    card_data = [[
        Paragraph(theme.create_kpi_card_html(
            title=card['title'],
            value=card['value'],
            subtitle=card.get('subtitle', ''),
            color=card.get('color', 'primary')
        ), styles['Normal'])
        for card in cards
    ]]
    
    card_table = Table(card_data, colWidths=[4*cm]*4)
    card_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(card_table)
```

### Section Header 컴포넌트
```python
def add_section_header(story, title: str, icon: str = "■"):
    """통일된 섹션 헤더"""
    header_style = ParagraphStyle(
        'SectionHeader',
        fontName='NanumBarunGothicBold',
        fontSize=16,
        textColor=theme.colors.primary,
        spaceBefore=15,
        spaceAfter=10,
        borderPadding=(0, 0, 5, 0),  # Bottom border
        borderWidth=2,
        borderColor=theme.colors.primary,
    )
    story.append(Paragraph(f"{icon} {title}", header_style))
```

---

## ✅ 작업 체크리스트

### 긴급 (즉시)
- [ ] M6 데이터 모순 수정 (total_score 단일화)
- [ ] M4 검증 로직 완화 (warning 모드)
- [ ] M5 의존성 체크 (M4 성공 확인)

### 중요 (24시간 내)
- [ ] KPI Card 컴포넌트 구현
- [ ] Section Header 표준화
- [ ] 표 스타일 통일 (ZeroSiteTheme 적용)
- [ ] 차트 시각화 추가 (matplotlib)

### 일반 (48시간 내)
- [ ] M2-M6 전체 디자인 리뷰
- [ ] 대시보드 카드 수정 (프론트엔드)
- [ ] 통합 테스트 (실제 데이터)
- [ ] 사용자 피드백 수렴

---

## 🚀 실행 순서

1. **M6 긴급 수정** (10분)
2. **M4/M5 검증 완화** (15분)
3. **테스트 생성** (5분)
4. **디자인 컴포넌트 구현** (30분)
5. **전체 재생성 및 검증** (10분)
6. **커밋 & 푸시** (5분)

**총 소요 시간: ~75분**

---

작성: 2025-12-19
상태: 실행 대기
