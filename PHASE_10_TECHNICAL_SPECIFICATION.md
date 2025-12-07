# Phase 10: 5-Type Report System - Technical Specification

## 📋 Project Context

**Project**: ZeroSite Land Report v11.0  
**Phase**: Phase 10 - 5-Type Report System  
**Estimated Time**: 16 hours  
**Current Status**: Phase 0-7 완료 (90% 완성)  
**Last Commit**: c7a88aa (Phase 2 100% COMPLETE)  
**Branch**: feature/expert-report-generator

---

## 🎯 Phase 10 Overview

### **목표**
다양한 이해관계자를 위한 5가지 맞춤형 보고서 시스템 구축

### **5가지 보고서 유형**

1. **LH 제출용 리포트** (LH Submission Report)
   - 공식 LH 심사 양식 준수
   - 모든 필수 항목 포함
   - 엄격한 포맷팅

2. **투자자용 리포트** (Investor Report)
   - 재무 분석 중심
   - ROI, NPV, IRR 강조
   - Executive Summary

3. **시공사용 리포트** (Construction Report)
   - 건축 가능성 중심
   - 법규 제약사항 상세
   - 공사비 추정

4. **경영진용 요약 리포트** (Executive Summary)
   - 1-2페이지 요약
   - 핵심 지표만 표시
   - 의사결정 지원

5. **비교 분석 리포트** (Comparative Analysis Report)
   - 여러 필지 비교
   - 순위 및 추천
   - 시각화 중심

---

## 🏗️ Architecture Design

### **Directory Structure**

```
app/
├── report_types_v11/              # 🆕 Phase 10 Report Types
│   ├── __init__.py
│   ├── base_report.py            # Abstract Base Report Class
│   ├── lh_submission_report.py   # Type 1: LH Submission
│   ├── investor_report.py        # Type 2: Investor Report
│   ├── construction_report.py    # Type 3: Construction Report
│   ├── executive_report.py       # Type 4: Executive Summary
│   └── comparative_report.py     # Type 5: Comparative Analysis
├── report_templates_v11/          # 🆕 Report Templates
│   ├── lh_submission.html
│   ├── investor_report.html
│   ├── construction_report.html
│   ├── executive_summary.html
│   └── comparative_analysis.html
├── report_styles_v11/             # 🆕 Report Stylesheets
│   ├── lh_submission.css
│   ├── investor_report.css
│   ├── construction_report.css
│   ├── executive_summary.css
│   └── comparative_analysis.css
└── api/
    └── endpoints/
        └── report_v11_multi_type.py  # 🆕 Multi-Type Report API
```

---

## 📊 Report Type Specifications

### **Type 1: LH Submission Report**

**목적**: LH 공식 심사용  
**포맷**: A4, 10-15 페이지  
**필수 섹션**:
- 표지 (사업명, 주소, 신청자)
- 토지 기본정보 (면적, 지목, 용도지역)
- 입지 분석 (교통, 교육, 편의시설)
- 수요 분석 (유형별 점수)
- 재무성 분석 (사업비, 임대료)
- 사업 타당성 종합 점수
- LH 심사기준 체크리스트
- 부록 (지도, 차트, 법규 요약)

**특징**:
- ✅ LH 공식 로고 및 워터마크
- ✅ 공식 색상 팔레트 (파랑, 회색)
- ✅ 표준 글꼴 (나눔고딕)
- ✅ 모든 필수 항목 자동 검증

---

### **Type 2: Investor Report**

**목적**: 투자자 설득용  
**포맷**: A4, 5-8 페이지  
**필수 섹션**:
- Executive Summary (1 페이지)
- Investment Highlights (강점 요약)
- Financial Analysis
  - Project Cost Breakdown
  - Revenue Projections
  - ROI, NPV, IRR, Payback Period
- Market Analysis
  - Demand Forecast
  - Competition Analysis
- Risk Assessment
  - Risk Matrix
  - Mitigation Strategies
- Conclusion & Recommendation

**특징**:
- 💰 재무 지표 강조
- 📊 차트 및 그래프 중심
- 🎨 전문적인 비즈니스 디자인
- 🔢 투자 수익률 시뮬레이션

---

### **Type 3: Construction Report**

**목적**: 시공사 실무용  
**포맷**: A4, 8-12 페이지  
**필수 섹션**:
- 부지 개요
- 법규 제약사항
  - 건폐율, 용적률
  - 높이 제한
  - 인허가 요건
- 건축 가능 규모
  - 세대수 추정
  - 건축면적 계산
- 공사비 추정
  - 토목공사
  - 건축공사
  - 부대비용
- 공사 일정 예상
- 기술적 주의사항

**특징**:
- 🏗️ 건축 실무 중심
- 📐 상세 설계 요구사항
- 📋 법규 체크리스트
- 💵 공사비 상세 내역

---

### **Type 4: Executive Summary**

**목적**: 경영진 의사결정용  
**포맷**: A4, 1-2 페이지  
**필수 섹션**:
- 프로젝트 개요 (3-4줄)
- 핵심 지표 대시보드
  - 종합 적합도: 85/100
  - 예상 ROI: 12.5%
  - 사업 기간: 36개월
  - 총 사업비: 50억원
- 강점 / 약점 (각 3개)
- 추천 여부: ⭐⭐⭐⭐☆ (4.5/5)
- Next Steps

**특징**:
- ⚡ 초고속 스캔 가능
- 📊 시각적 대시보드
- ✅ 명확한 추천 의견
- 🎯 의사결정 지원

---

### **Type 5: Comparative Analysis Report**

**목적**: 여러 후보지 비교  
**포맷**: A4, 6-10 페이지  
**필수 섹션**:
- 비교 대상 요약 (테이블)
- 종합 순위
  1. 후보지 A: 92점
  2. 후보지 B: 88점
  3. 후보지 C: 75점
- 항목별 비교 차트
  - 입지 점수
  - 수요 점수
  - 재무성 점수
  - LH 적합도
- 레이더 차트 (다차원 비교)
- 추천 우선순위
- 각 후보지별 간단 요약

**특징**:
- 🔍 사이드바이사이드 비교
- 📊 시각화 중심
- 🏆 명확한 순위
- 📋 의사결정 매트릭스

---

## 🔧 Implementation Plan

### **Phase 10.1: Base Infrastructure (3시간)**

**목표**: 공통 기반 클래스 및 인터페이스 구축

**Tasks**:
1. `BaseReport` 추상 클래스 생성
   - 공통 메서드: `generate()`, `validate()`, `export_pdf()`, `export_html()`
   - 공통 속성: `report_id`, `created_at`, `data_source`

2. `ReportConfig` 데이터 클래스
   - 각 리포트 타입별 설정
   - 템플릿 경로, 스타일시트, 필수 섹션

3. `ReportValidator` 유틸리티
   - 필수 필드 검증
   - 데이터 무결성 체크

**Deliverables**:
- `app/report_types_v11/base_report.py`
- `app/report_types_v11/report_config.py`
- `app/report_types_v11/report_validator.py`

---

### **Phase 10.2: LH Submission Report (3시간)**

**목표**: Type 1 - LH 제출용 리포트 완성

**Tasks**:
1. LH 공식 템플릿 설계
2. 필수 섹션 자동 생성
3. LH 심사기준 체크리스트 통합
4. PDF 생성 및 검증

**Deliverables**:
- `app/report_types_v11/lh_submission_report.py`
- `app/report_templates_v11/lh_submission.html`
- `app/report_styles_v11/lh_submission.css`

**Test**:
```python
python test_lh_submission_report_v11.py
```

---

### **Phase 10.3: Investor & Construction Reports (4시간)**

**목표**: Type 2 (Investor) + Type 3 (Construction) 완성

**Tasks**:
1. **Investor Report**
   - 재무 분석 섹션 강화
   - ROI/NPV/IRR 계산 통합
   - 투자 시뮬레이션 차트

2. **Construction Report**
   - 법규 제약사항 상세화
   - 공사비 추정 로직
   - 건축 가능 규모 계산

**Deliverables**:
- `app/report_types_v11/investor_report.py`
- `app/report_types_v11/construction_report.py`
- Templates & Styles

**Test**:
```python
python test_investor_report_v11.py
python test_construction_report_v11.py
```

---

### **Phase 10.4: Executive & Comparative Reports (3시간)**

**목표**: Type 4 (Executive) + Type 5 (Comparative) 완성

**Tasks**:
1. **Executive Summary**
   - 1-2 페이지 압축 포맷
   - 핵심 지표 대시보드
   - 시각적 추천 시스템

2. **Comparative Analysis**
   - 다중 필지 데이터 비교
   - 순위 알고리즘
   - 레이더 차트 생성

**Deliverables**:
- `app/report_types_v11/executive_report.py`
- `app/report_types_v11/comparative_report.py`
- Templates & Styles

**Test**:
```python
python test_executive_report_v11.py
python test_comparative_report_v11.py
```

---

### **Phase 10.5: Multi-Type API (2시간)**

**목표**: 통합 API 엔드포인트 구축

**Tasks**:
1. `/api/v11/generate-report` 엔드포인트
   - Query Param: `report_type` (lh_submission, investor, construction, executive, comparative)
   - Request Body: 분석 데이터
   - Response: PDF/HTML URL

2. `/api/v11/generate-all-reports` 엔드포인트
   - 5가지 리포트 일괄 생성
   - ZIP 파일로 반환

3. API 문서 자동 생성 (FastAPI Swagger)

**Deliverables**:
- `app/api/endpoints/report_v11_multi_type.py`

**API Test**:
```bash
curl -X POST "http://localhost:8000/api/v11/generate-report?report_type=lh_submission" \
  -H "Content-Type: application/json" \
  -d @test_data.json
```

---

### **Phase 10.6: Integration & Testing (1시간)**

**목표**: 전체 통합 및 E2E 테스트

**Tasks**:
1. 모든 리포트 타입 통합 테스트
2. 성능 최적화 (PDF 생성 속도)
3. 에러 핸들링 검증
4. 문서 업데이트

**Deliverables**:
- `test_phase10_integration.py`
- `PHASE_10_COMPLETION_REPORT.md`

---

## 📦 Data Models

### **ReportRequest**

```python
from pydantic import BaseModel
from typing import Literal, List, Optional

class ReportRequest(BaseModel):
    report_type: Literal[
        "lh_submission",
        "investor",
        "construction",
        "executive",
        "comparative"
    ]
    analysis_data: dict  # From Phase 0-7 outputs
    parcels: List[dict]  # For comparative reports
    options: Optional[dict] = {}
```

### **ReportResponse**

```python
class ReportResponse(BaseModel):
    report_id: str
    report_type: str
    status: Literal["success", "error"]
    html_url: Optional[str]
    pdf_url: Optional[str]
    created_at: str
    error_message: Optional[str] = None
```

---

## 🧪 Testing Strategy

### **Unit Tests**
- 각 리포트 타입별 독립 테스트
- 템플릿 렌더링 검증
- PDF 생성 검증

### **Integration Tests**
- API 엔드포인트 테스트
- 다중 리포트 생성 테스트
- 에러 시나리오 테스트

### **Performance Tests**
- PDF 생성 속도 (목표: < 3초)
- 동시 요청 처리 (목표: 10 concurrent requests)

---

## 📈 Success Criteria

### **Phase 10 완료 조건**

✅ **모든 5가지 리포트 타입 구현**
- LH Submission ✅
- Investor ✅
- Construction ✅
- Executive ✅
- Comparative ✅

✅ **API 엔드포인트 동작**
- `/api/v11/generate-report` ✅
- `/api/v11/generate-all-reports` ✅

✅ **품질 검증**
- 모든 유닛 테스트 PASS ✅
- PDF 생성 성공률 > 99% ✅
- 평균 생성 시간 < 3초 ✅

✅ **문서화**
- API 문서 (Swagger) ✅
- 사용자 가이드 ✅
- 완료 보고서 ✅

---

## 🚀 Deployment Strategy

### **Rollout Plan**

1. **Phase 10.1-10.4**: Feature Branch 개발
2. **Phase 10.5**: Integration Testing
3. **Phase 10.6**: Pull Request 생성
4. **Merge to Main**: 전체 테스트 통과 후

### **Git Workflow**

```bash
# Current branch: feature/expert-report-generator
git checkout -b feature/phase10-report-types

# After each phase completion:
git add .
git commit -m "feat(Phase10.X): [Description]"

# Final PR:
git push origin feature/phase10-report-types
# Create PR to feature/expert-report-generator
```

---

## 📋 Phase 10 Task Breakdown

### **Total Estimated Time: 16 hours**

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 10.1 | Base Infrastructure | 3h | ⏳ Pending |
| 10.2 | LH Submission Report | 3h | ⏳ Pending |
| 10.3 | Investor & Construction | 4h | ⏳ Pending |
| 10.4 | Executive & Comparative | 3h | ⏳ Pending |
| 10.5 | Multi-Type API | 2h | ⏳ Pending |
| 10.6 | Integration & Testing | 1h | ⏳ Pending |

---

## 🎯 Next Steps

**즉시 시작 가능!**

1. ✅ Technical Specification 완료
2. 🚀 Phase 10.1 시작: Base Infrastructure
3. 📝 Git Branch 생성: `feature/phase10-report-types`
4. 💻 코드 개발 시작

**명령어**:
```bash
cd /home/user/webapp
git checkout -b feature/phase10-report-types
mkdir -p app/report_types_v11 app/report_templates_v11 app/report_styles_v11
touch app/report_types_v11/__init__.py
```

---

**Phase 10 개발 준비 완료! 🎉**

Let's build the 5-Type Report System! 💪
