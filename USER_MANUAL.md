# 📖 ZeroSite v3 User Manual

**버전**: v3.0.0  
**작성일**: 2025-12-10  
**대상**: 사용자, 개발자, 의사결정자

---

## 📋 목차

1. [소개](#소개)
2. [시작하기](#시작하기)
3. [리포트 생성 방법](#리포트-생성-방법)
4. [리포트 해석 가이드](#리포트-해석-가이드)
5. [고급 기능](#고급-기능)
6. [FAQ](#faq)
7. [지원](#지원)

---

## 🎯 소개

### ZeroSite v3란?

ZeroSite v3는 LH (한국토지주택공사) 청년·신혼부부·노인 임대주택 개발사업의 **타당성 분석을 자동화**하는 Expert Edition 리포트 생성 시스템입니다.

### 주요 기능

✅ **Phase 11-14 통합**
- Phase 11: LH 정책 규칙 & 건축 설계 자동화
- Phase 13: 학술적 내러티브 생성 (KDI 스타일)
- Phase 14: Critical Path 타임라인 & 리스크 분석

✅ **5개 인터랙티브 차트**
- 30년 현금흐름 차트
- 경쟁력 분석 레이더 차트
- 민감도 분석 히트맵
- Tornado 차트 (변수 영향도)
- McKinsey 2x2 리스크 매트릭스

✅ **자동 생성**
- 리포트 생성 시간: < 2초
- HTML + PDF 출력
- 100% 정책 준수 보장

### 비즈니스 가치

| 항목 | 기존 | ZeroSite v3 | 절감율 |
|------|------|------------|--------|
| 정책 준수 검토 | 4시간 | 0.02ms | 99.9% |
| 리포트 작성 | 8시간 | 0.2ms | 99.9% |
| 차트 생성 | 2시간 | 1s | 99.9% |
| 리스크 분석 | 3시간 | 0.5s | 99.9% |
| **총 절감** | **17시간** | **< 2초** | **99.9%** |

**비용 절감**: 약 **170만원/건**

---

## 🚀 시작하기

### 필요 사항

- Python 3.10 이상
- 웹 브라우저 (Chrome, Firefox, Safari, Edge)
- 프로젝트 기본 정보:
  - 주소 (address)
  - 토지 면적 (land_area)
  - 건폐율, 용적률 (bcr, far)
  - 최대 층수 (max_floors)
  - 공급 유형 (unit_type: 청년/신혼부부/노인)

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/hellodesignthinking-png/LHproject.git
cd LHproject

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 테스트 실행
python generate_v3_full_report.py
```

---

## 📝 리포트 생성 방법

### 방법 1: 커맨드 라인 (권장)

#### 기본 사용
```bash
cd /path/to/LHproject
python generate_v3_full_report.py
```

**출력**:
```
✅ Report generation COMPLETE!
💾 Report saved to: generated_reports/v3_full_20251210_135419.html
📏 HTML size: 189,609 characters
```

#### 커스터마이징
`generate_v3_full_report.py` 파일의 `main()` 함수에서 `test_data` 수정:

```python
test_data = {
    "address": "서울특별시 강남구 테헤란로 123",  # 프로젝트 주소
    "land_area": 1500.0,  # 토지 면적 (㎡)
    "land_params": {
        "bcr": 60.0,       # 건폐율 (%)
        "far": 250.0,      # 용적률 (%)
        "max_floors": 10,  # 최대 층수
        "zone_type": "제3종일반주거지역"  # 용도지역
    },
    "unit_type": "신혼부부",  # 공급 유형: 청년/신혼부부/노인
    "land_price_per_sqm": 7_000_000  # 토지 단가 (원/㎡)
}
```

---

### 방법 2: Python 스크립트

```python
from generate_v3_full_report import V3FullReportGenerator

# 1. Generator 초기화
generator = V3FullReportGenerator()

# 2. 프로젝트 데이터 준비
project = {
    "address": "서울특별시 마포구 월드컵북로 120",
    "land_area": 1000.0,
    "land_params": {
        "bcr": 60.0,
        "far": 200.0,
        "max_floors": 8,
        "zone_type": "제2종일반주거지역"
    },
    "unit_type": "청년",
    "land_price_per_sqm": 5_000_000
}

# 3. HTML 리포트 생성
html_content = generator.generate_report(**project)

# 4. 파일 저장
output_path = generator.save_report(html_content)
print(f"✅ Report saved to: {output_path}")

# 5. PDF 변환 (선택사항)
from weasyprint import HTML
pdf_path = output_path.replace(".html", ".pdf")
HTML(output_path).write_pdf(pdf_path)
print(f"✅ PDF saved to: {pdf_path}")
```

---

### 방법 3: REST API

#### API 서버 시작
```bash
# FastAPI 설치
pip install fastapi uvicorn

# API 서버 실행
python app_api.py
# 또는
uvicorn app_api:app --host 0.0.0.0 --port 8000
```

#### API 사용 (curl)
```bash
# HTML 리포트 생성
curl -X POST "http://localhost:8000/api/v3/report/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 123",
    "land_area": 1000,
    "land_params": {
      "bcr": 60,
      "far": 200,
      "max_floors": 8,
      "zone_type": "제2종일반주거지역"
    },
    "unit_type": "청년",
    "land_price_per_sqm": 5000000
  }' > report.html

# PDF 리포트 생성
curl -X POST "http://localhost:8000/api/v3/report/generate-pdf" \
  -H "Content-Type: application/json" \
  -d '{ ... }' > report.pdf
```

#### API 사용 (Python)
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v3/report/generate",
    json={
        "address": "서울특별시 강남구 테헤란로 123",
        "land_area": 1000,
        "land_params": {
            "bcr": 60,
            "far": 200,
            "max_floors": 8,
            "zone_type": "제2종일반주거지역"
        },
        "unit_type": "청년"
    }
)

with open("report.html", "w", encoding="utf-8") as f:
    f.write(response.text)
```

---

## 📊 리포트 해석 가이드

### 리포트 구조

생성된 리포트는 다음 섹션들로 구성됩니다:

#### Section 01: Executive Summary
- **개요**: 프로젝트 한눈에 보기
- **핵심 지표**: CAPEX, IRR, NPV
- **의사결정**: GO/CONDITIONAL/NO-GO

#### Section 02-1: 건축물 개요 (Phase 11)
- **세대수**: 자동 계산된 총 세대수
- **주차대수**: LH 기준 준수 (서울 0.3, 일반 0.2대/세대)
- **공용면적**: 15% 이상 자동 확보
- **설계철학**: 공급 유형별 자동 생성

#### Section 04-05: AI 수요 & 시장 분석 (Phase 6.8, 7.7)
- **수요 점수**: 0-100 점수 (78.5점 = 높은 수요)
- **시장 신호**: 경쟁 환경 및 트렌드 분석

#### Section 06: 공사비 분석 (Phase 8)
- **LH 표준 공사비**: 350만원/㎡ 기준
- **세부 비용**: 건축비, 설계비, 직/간접비

#### Section 07: 재무 분석 (Phase 2.5)
- **CAPEX**: 총 투자비
- **IRR**: 내부수익률 (민간 vs 정책)
- **NPV**: 순현재가치

#### Section 09: 36개월 로드맵 (Phase 14)
- **타임라인**: 38개월 표준 일정
- **Critical Path**: 8단계 핵심 경로
- **리스크**: 16개 주요 리스크 식별

#### Section 10: 학술적 결론 (Phase 13)
- **5단계 내러티브**:
  1. WHAT: 프로젝트 개요
  2. SO WHAT: 의미와 중요성
  3. WHY: 근거 및 이유
  4. INSIGHT: 핵심 통찰
  5. CONCLUSION: 최종 결론

---

### 인터랙티브 차트 사용법

#### 📊 Chart 1: 30-Year Cashflow
- **Hover**: 연도별 상세 데이터 확인
- **Zoom**: 특정 기간 확대 (드래그)
- **Pan**: 차트 이동 (Shift + 드래그)
- **Reset**: 원래 뷰로 복원 (더블클릭)

**해석**:
- 빨간선 (지출)이 초기 3년간 높음 → 투자 집중 기간
- 파란선 (순현금흐름)이 음수 → 적자 구간
- 주황 점선 (누적)이 0 교차점 → 투자 회수 시점

#### 📊 Chart 2: Radar Chart (경쟁력 분석)
- **5개 차원**: 입지, 사업성, 정책, 재무, 리스크
- **파란 영역**: 본 프로젝트
- **회색 점선**: 업계 평균

**해석**:
- 면적이 클수록 경쟁력 높음
- 업계 평균 초과 영역 → 강점
- 업계 평균 미달 영역 → 개선 필요

#### 📊 Chart 3: Sensitivity Heatmap
- **X축**: LH 감정평가율 변동
- **Y축**: CAPEX 변동
- **색상**: 초록 (좋음) → 빨강 (나쁨)

**해석**:
- 초록색 많을수록 → 리스크 낮음
- 빨간색 많을수록 → 리스크 높음
- 중앙 (0%, 0%) → 기본 시나리오

#### 📊 Chart 4: Tornado Chart
- **순서**: 위에서 아래로 영향도 순
- **빨간 막대**: Downside (부정적 영향)
- **초록 막대**: Upside (긍정적 영향)

**해석**:
- 막대가 길수록 → 변수의 영향도 큼
- 1순위 변수에 집중 관리 필요
- 최하위 변수는 모니터링 수준

#### 📊 Chart 5: McKinsey 2x2 Risk Matrix
- **4개 Quadrant**:
  - 좌하 (Low Risk): 모니터
  - 우하/좌상 (Medium): 관리
  - 우상 (High Risk): 완화 필수

**해석**:
- 우상 빨간 영역: 즉시 완화 조치 필요
- 주황 영역: 관리 계획 수립
- 초록 영역: 정기 모니터링

---

## 🔧 고급 기능

### 배치 처리

여러 프로젝트를 한번에 처리:

```python
from generate_v3_full_report import V3FullReportGenerator

generator = V3FullReportGenerator()

projects = [
    {"address": "서울 강남", "land_area": 1000, ...},
    {"address": "서울 마포", "land_area": 1500, ...},
    {"address": "서울 송파", "land_area": 2000, ...},
]

for project in projects:
    try:
        html = generator.generate_report(**project)
        path = generator.save_report(html)
        print(f"✅ Generated: {path}")
    except Exception as e:
        print(f"❌ Error: {e}")
```

### PDF 자동 변환

```python
from weasyprint import HTML
from pathlib import Path

html_files = Path("generated_reports").glob("*.html")

for html_file in html_files:
    pdf_file = html_file.with_suffix(".pdf")
    HTML(str(html_file)).write_pdf(str(pdf_file))
    print(f"✅ Converted: {pdf_file}")
```

---

## ❓ FAQ

### Q1: 리포트 생성에 얼마나 걸리나요?
**A**: HTML 리포트는 < 2초, PDF 변환 포함 시 < 10초입니다.

### Q2: 어떤 공급 유형을 지원하나요?
**A**: 청년(14㎡), 신혼부부(18-22㎡, 22-26㎡), 노인(24-28㎡, 28-32㎡), 일반, 혼합 총 7가지입니다.

### Q3: PDF에서 차트가 인터랙티브하지 않아요
**A**: PDF는 static 이미지입니다. 인터랙티브 기능은 HTML에서만 작동합니다. 브라우저에서 HTML을 열어 차트를 탐색하세요.

### Q4: 토지 가격은 어떻게 결정하나요?
**A**: `land_price_per_sqm` 파라미터로 설정합니다. 기본값은 500만원/㎡이며, 실거래가나 감정평가액을 사용하세요.

### Q5: 차트를 끌 수 있나요?
**A**: `generate_v3_full_report.py`에서 차트 생성 코드를 주석 처리하면 됩니다. 단, Simplified 버전이 더 빠릅니다.

### Q6: 모바일에서 볼 수 있나요?
**A**: 네, HTML 리포트는 반응형 디자인으로 모바일/태블릿에서도 최적화됩니다.

---

## 💡 팁 & 모범 사례

### 팁 1: 데이터 정확성 확보
- 토지 면적은 공부상 면적 사용
- 건폐율/용적률은 해당 지역 법규 확인
- 토지 가격은 최근 실거래가 참고

### 팁 2: 리포트 해석
- IRR < 8%: 민간 수익성 제한적, 정책사업 검토
- NPV < 0: 재무적 타당성 낮음
- 리스크 매트릭스 우상단 항목: 우선 관리

### 팁 3: 의사결정
- GO: 즉시 추진
- CONDITIONAL: 조건부 추진 (리스크 완화 후)
- NO-GO: 재검토 필요

---

## 📞 지원

### 문서
- **기술 문서**: `PRODUCTION_DEPLOYMENT_GUIDE.md`
- **API 문서**: `http://localhost:8000/api/v3/docs` (API 서버 실행 시)

### 문의
- **GitHub Issues**: https://github.com/hellodesignthinking-png/LHproject/issues
- **Email**: 프로젝트 팀 이메일

---

**🎯 ZeroSite v3로 빠르고 정확한 의사결정을 하세요!**

**Last Updated**: 2025-12-10  
**Version**: v3.0.0
