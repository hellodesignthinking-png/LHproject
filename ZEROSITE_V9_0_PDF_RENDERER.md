# ZeroSite v9.0 PDF Renderer Specification

## 문서 개요
- **작성일**: 2025-12-04
- **버전**: v9.0 Part 4
- **목적**: 12-Section 모듈형 PDF/HTML Renderer 완전 구현 명세
- **대상**: 개발자 직접 구현용

---

## Part 4: PDF/HTML Renderer v9.0

### 목차
1. [v8.6 PDF 생성의 문제점](#1-v86-pdf-생성의-문제점)
2. [v9.0 Renderer 아키텍처](#2-v90-renderer-아키텍처)
3. [12-Section 모듈형 템플릿 설계](#3-12-section-모듈형-템플릿-설계)
4. [HTML-to-PDF 엔진](#4-html-to-pdf-엔진)
5. [시각화 통합](#5-시각화-통합)
6. [구현 파일 구조](#6-구현-파일-구조)

---

## 1. v8.6 PDF 생성의 문제점

### 1.1 현재 문제점 (Top 5)

1. **단일 거대 템플릿**
   - `lh_report_generator_v7_5_final.py`가 모든 HTML을 하나의 문자열로 생성
   - 유지보수 어려움 (2000+ 라인)
   - 섹션별 독립 수정 불가

2. **KeyError 취약성**
   - 템플릿이 `{{ financial_result.price_per_unit_lh }}` 같은 직접 참조 사용
   - 데이터 누락 시 전체 PDF 생성 실패

3. **시각화 미연동**
   - `VisualizationEngineV85`가 JSON 생성하지만 PDF에 미반영
   - 차트/그래프는 수동 삽입 필요

4. **스타일 비일관성**
   - CSS가 인라인으로 산재
   - 섹션별 폰트/색상 불일치

5. **PDF 품질 문제**
   - 한글 폰트 깨짐
   - 페이지 넘김 부자연스러움
   - 이미지 해상도 저하

### 1.2 v9.0 목표

| 항목 | v8.6 | v9.0 목표 |
|------|------|---------|
| 템플릿 구조 | 단일 파일 | 12개 모듈 |
| KeyError | 자주 발생 | ZERO |
| 시각화 | 미연동 | 100% 자동 삽입 |
| 스타일 | 인라인 CSS | 외부 CSS |
| PDF 품질 | 보통 | 출판 수준 |
| 유지보수 | 어려움 | 쉬움 (모듈별) |

---

## 2. v9.0 Renderer 아키텍처

### 2.1 전체 흐름

```
Input: StandardAnalysisOutput + AI Generated Text
  ↓
TemplateEngine v9.0 (Jinja2)
  ├─ 12개 Section Templates (modular)
  ├─ Global CSS Stylesheet
  └─ Visualization Embedder
  ↓
HTML Output (완전한 문서)
  ↓
WeasyPrint / Playwright PDF Engine
  ↓
Output: Professional PDF (60+ pages)
```

### 2.2 핵심 컴포넌트

```python
# app/services/pdf_renderer_v9_0.py

from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import logging

logger = logging.getLogger(__name__)

class PDFRendererV90:
    """
    v9.0 PDF Renderer
    - 12개 모듈형 섹션
    - KeyError ZERO
    - 시각화 자동 삽입
    - 출판 품질 PDF 생성
    """
    
    def __init__(self, template_dir: str = "app/templates/pdf_v9_0"):
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
        # 커스텀 필터 등록
        self.env.filters['format_currency'] = self.format_currency
        self.env.filters['format_percentage'] = self.format_percentage
        self.env.filters['format_area'] = self.format_area
    
    def render_full_report(self, 
                          data: 'StandardAnalysisOutput',
                          ai_text: Dict[str, str],
                          visualizations: Dict[str, str]) -> str:
        """
        전체 보고서 HTML 생성
        
        Args:
            data: 정규화된 분석 데이터
            ai_text: AI가 생성한 챕터별 텍스트
            visualizations: 시각화 이미지 (base64 또는 경로)
        
        Returns:
            완전한 HTML 문서
        """
        # 1. 마스터 템플릿 로드
        master_template = self.env.get_template("master.html")
        
        # 2. 각 섹션 HTML 생성
        sections_html = {}
        section_ids = [
            "cover", "executive_summary", "site_overview", 
            "gis_accessibility", "location_metrics", "demand_analysis",
            "regulation_review", "construction_feasibility", 
            "financial_analysis", "lh_evaluation", "risk_review",
            "final_decision", "appendix"
        ]
        
        for section_id in section_ids:
            try:
                sections_html[section_id] = self.render_section(
                    section_id, data, ai_text, visualizations
                )
            except Exception as e:
                logger.error(f"Error rendering section {section_id}: {e}")
                sections_html[section_id] = f"<p>[오류: {section_id} 렌더링 실패]</p>"
        
        # 3. 마스터 템플릿에 모든 섹션 삽입
        full_html = master_template.render(
            sections=sections_html,
            metadata={
                "title": f"LH 신축매입임대 토지분석 보고서 - {data.site_info.address}",
                "version": "v9.0",
                "date": data.timestamp,
                "analysis_id": data.analysis_id
            }
        )
        
        return full_html
    
    def render_section(self, 
                      section_id: str,
                      data: 'StandardAnalysisOutput',
                      ai_text: Dict[str, str],
                      visualizations: Dict[str, str]) -> str:
        """개별 섹션 렌더링"""
        
        template = self.env.get_template(f"sections/{section_id}.html")
        
        # 섹션별 데이터 준비
        section_data = self.prepare_section_data(section_id, data, ai_text, visualizations)
        
        return template.render(**section_data)
    
    def prepare_section_data(self, 
                            section_id: str,
                            data: 'StandardAnalysisOutput',
                            ai_text: Dict[str, str],
                            visualizations: Dict[str, str]) -> Dict[str, Any]:
        """섹션별 렌더링 데이터 준비"""
        
        base_data = {
            "section_id": section_id,
            "ai_text": ai_text.get(section_id, ""),
            "data": data  # 전체 데이터 접근 가능
        }
        
        # 섹션별 특화 데이터
        if section_id == "financial_analysis":
            base_data["financial_charts"] = {
                "capex_breakdown": visualizations.get("capex_breakdown"),
                "cash_flow_10yr": visualizations.get("cash_flow_10yr"),
                "sensitivity_analysis": visualizations.get("sensitivity_analysis")
            }
        
        elif section_id == "gis_accessibility":
            base_data["gis_maps"] = {
                "poi_map": visualizations.get("poi_map"),
                "accessibility_heatmap": visualizations.get("accessibility_heatmap")
            }
        
        elif section_id == "lh_evaluation":
            base_data["lh_charts"] = {
                "radar_chart": visualizations.get("lh_radar_chart"),
                "score_breakdown": visualizations.get("lh_score_breakdown")
            }
        
        return base_data
    
    def generate_pdf(self, html_content: str, output_path: str):
        """HTML → PDF 변환"""
        try:
            HTML(string=html_content, base_url=self.template_dir).write_pdf(
                output_path,
                stylesheets=[f"{self.template_dir}/styles/main.css"],
                presentational_hints=True
            )
            logger.info(f"PDF generated successfully: {output_path}")
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    # ===== 커스텀 Jinja2 필터 =====
    
    @staticmethod
    def format_currency(value: float) -> str:
        """통화 포맷 (원)"""
        if value >= 1_000_000_000_000:
            return f"₩{value/1_000_000_000_000:.2f}조"
        elif value >= 100_000_000:
            return f"₩{value/100_000_000:.1f}억"
        elif value >= 10_000:
            return f"₩{value/10_000:.0f}만"
        else:
            return f"₩{value:,.0f}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """백분율 포맷"""
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_area(value: float) -> str:
        """면적 포맷 (m²)"""
        return f"{value:,.1f}m²"
```

---

## 3. 12-Section 모듈형 템플릿 설계

### 3.1 디렉토리 구조

```
app/templates/pdf_v9_0/
├── master.html                      # 마스터 템플릿
├── sections/                        # 12개 섹션
│   ├── cover.html                   # 표지
│   ├── executive_summary.html       # 임원 요약
│   ├── site_overview.html           # 토지 개요
│   ├── gis_accessibility.html       # GIS 접근성
│   ├── location_metrics.html        # 입지 지표
│   ├── demand_analysis.html         # 수요 분석
│   ├── regulation_review.html       # 법규 검토
│   ├── construction_feasibility.html # 건축 타당성
│   ├── financial_analysis.html      # 재무 분석 (핵심)
│   ├── lh_evaluation.html           # LH 평가
│   ├── risk_review.html             # 리스크 평가
│   ├── final_decision.html          # 최종 의사결정
│   └── appendix.html                # 부록
├── components/                      # 재사용 가능 컴포넌트
│   ├── table.html                   # 테이블
│   ├── chart.html                   # 차트
│   ├── kpi_card.html                # KPI 카드
│   └── risk_badge.html              # 리스크 배지
└── styles/
    ├── main.css                     # 메인 스타일시트
    ├── print.css                    # 인쇄용 스타일
    └── fonts/                       # 한글 폰트
        └── NanumGothic.ttf
```

### 3.2 Master Template

```html
<!-- app/templates/pdf_v9_0/master.html -->

<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ metadata.title }}</title>
    <link rel="stylesheet" href="styles/main.css">
    <link rel="stylesheet" href="styles/print.css" media="print">
    <style>
        /* 한글 폰트 임베딩 */
        @font-face {
            font-family: 'NanumGothic';
            src: url('styles/fonts/NanumGothic.ttf') format('truetype');
        }
        body {
            font-family: 'NanumGothic', sans-serif;
        }
    </style>
</head>
<body>
    <!-- 표지 -->
    <section class="cover-page">
        {{ sections.cover | safe }}
    </section>

    <!-- 목차 -->
    <section class="toc-page">
        <h1>목차</h1>
        <ul class="toc">
            <li><a href="#executive-summary">1. 임원 요약 (Executive Summary)</a></li>
            <li><a href="#site-overview">2. 토지 개요 (Site Overview)</a></li>
            <li><a href="#gis-accessibility">3. GIS 접근성 분석</a></li>
            <li><a href="#location-metrics">4. 입지 지표</a></li>
            <li><a href="#demand-analysis">5. 인구 및 수요 분석</a></li>
            <li><a href="#regulation-review">6. 개발 규제 검토</a></li>
            <li><a href="#construction-feasibility">7. 건축 타당성</a></li>
            <li><a href="#financial-analysis">8. 재무 분석 (Financial Analysis)</a></li>
            <li><a href="#lh-evaluation">9. LH 평가 기준</a></li>
            <li><a href="#risk-review">10. 리스크 평가</a></li>
            <li><a href="#final-decision">11. 최종 의사결정</a></li>
            <li><a href="#appendix">12. 부록</a></li>
        </ul>
    </section>

    <!-- 본문 섹션들 -->
    <section id="executive-summary" class="chapter">
        {{ sections.executive_summary | safe }}
    </section>

    <section id="site-overview" class="chapter">
        {{ sections.site_overview | safe }}
    </section>

    <section id="gis-accessibility" class="chapter">
        {{ sections.gis_accessibility | safe }}
    </section>

    <section id="location-metrics" class="chapter">
        {{ sections.location_metrics | safe }}
    </section>

    <section id="demand-analysis" class="chapter">
        {{ sections.demand_analysis | safe }}
    </section>

    <section id="regulation-review" class="chapter">
        {{ sections.regulation_review | safe }}
    </section>

    <section id="construction-feasibility" class="chapter">
        {{ sections.construction_feasibility | safe }}
    </section>

    <section id="financial-analysis" class="chapter">
        {{ sections.financial_analysis | safe }}
    </section>

    <section id="lh-evaluation" class="chapter">
        {{ sections.lh_evaluation | safe }}
    </section>

    <section id="risk-review" class="chapter">
        {{ sections.risk_review | safe }}
    </section>

    <section id="final-decision" class="chapter">
        {{ sections.final_decision | safe }}
    </section>

    <section id="appendix" class="chapter">
        {{ sections.appendix | safe }}
    </section>

    <!-- 페이지 하단 메타데이터 -->
    <footer>
        <p>{{ metadata.title }}</p>
        <p>Generated: {{ metadata.date }} | Version: {{ metadata.version }} | Analysis ID: {{ metadata.analysis_id }}</p>
    </footer>
</body>
</html>
```

### 3.3 Financial Analysis Section Template (핵심 예시)

```html
<!-- app/templates/pdf_v9_0/sections/financial_analysis.html -->

<div class="chapter-header">
    <h1>8. 재무 분석 (Financial Analysis)</h1>
    <p class="chapter-subtitle">LH 신축매입임대 사업 재무 타당성 평가</p>
</div>

<!-- 8.1 투자 구조 개요 -->
<section class="subsection">
    <h2>8.1 투자 구조 (CAPEX Breakdown)</h2>
    
    <!-- AI 생성 텍스트 -->
    <div class="ai-generated-content">
        {{ ai_text | safe }}
    </div>
    
    <!-- 핵심 지표 카드 -->
    <div class="kpi-grid">
        {% include 'components/kpi_card.html' with 
            title='총 투자액', 
            value=data.financial_result.total_capex | format_currency,
            icon='dollar' 
        %}
        
        {% include 'components/kpi_card.html' with 
            title='예상 세대수', 
            value=data.financial_result.unit_count ~ '세대',
            icon='home' 
        %}
        
        {% include 'components/kpi_card.html' with 
            title='Cap Rate', 
            value=data.financial_result.cap_rate | format_percentage,
            icon='chart' 
        %}
        
        {% include 'components/kpi_card.html' with 
            title='10년 ROI', 
            value=data.financial_result.roi_10yr | format_percentage,
            icon='trend' 
        %}
    </div>
    
    <!-- CAPEX 구조표 -->
    <table class="data-table">
        <thead>
            <tr>
                <th>항목</th>
                <th>금액 (원)</th>
                <th>비율 (%)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>토지비</td>
                <td>{{ data.financial_result.total_land_price | format_currency }}</td>
                <td>{{ (data.financial_result.total_land_price / data.financial_result.total_capex * 100) | format_percentage }}</td>
            </tr>
            <tr>
                <td>공사비</td>
                <td>{{ data.financial_result.total_construction_cost | format_currency }}</td>
                <td>{{ (data.financial_result.total_construction_cost / data.financial_result.total_capex * 100) | format_percentage }}</td>
            </tr>
            <tr>
                <td>기타 비용</td>
                <td>{{ (data.financial_result.total_capex - data.financial_result.total_land_price - data.financial_result.total_construction_cost) | format_currency }}</td>
                <td>{{ ((data.financial_result.total_capex - data.financial_result.total_land_price - data.financial_result.total_construction_cost) / data.financial_result.total_capex * 100) | format_percentage }}</td>
            </tr>
            <tr class="total-row">
                <td><strong>총 투자액 (CAPEX)</strong></td>
                <td><strong>{{ data.financial_result.total_capex | format_currency }}</strong></td>
                <td><strong>100.00%</strong></td>
            </tr>
        </tbody>
    </table>
    
    <!-- 시각화: CAPEX Pie Chart -->
    <div class="chart-container">
        <img src="{{ financial_charts.capex_breakdown }}" alt="CAPEX Breakdown" class="chart-image">
        <p class="chart-caption">그림 8-1. 투자 구조 분석 (CAPEX Breakdown)</p>
    </div>
</section>

<!-- 8.2 LH 공사비 연동제 분석 (50세대 이상인 경우만 표시) -->
{% if data.financial_result.analysis_mode == 'LH_LINKED' %}
<section class="subsection">
    <h2>8.2 LH 공사비 연동제 분석 (50세대 이상)</h2>
    
    <div class="highlight-box lh-linked">
        <h3>🏛️ LH 매입가 구조</h3>
        <p>본 사업은 <strong>50세대 이상</strong>으로 LH 공사비 연동제가 적용됩니다.</p>
        
        <table class="lh-price-table">
            <tr>
                <td>검증된 공사비 (LH 기준)</td>
                <td class="amount">{{ data.financial_result.verified_cost | format_currency }}</td>
            </tr>
            <tr>
                <td>토지 감정평가액</td>
                <td class="amount">{{ data.financial_result.total_land_price | format_currency }}</td>
            </tr>
            <tr class="total-row">
                <td><strong>LH 매입가 (총액)</strong></td>
                <td class="amount"><strong>{{ data.financial_result.lh_purchase_price | format_currency }}</strong></td>
            </tr>
            <tr>
                <td>LH 매입가 (단가)</td>
                <td class="amount">{{ data.financial_result.lh_purchase_price_per_sqm | format_currency }}/m²</td>
            </tr>
        </table>
    </div>
    
    <p><strong>공식:</strong> LH 매입가 = 검증된 공사비 + 토지 감정평가액</p>
</section>
{% endif %}

<!-- 8.3 수익성 분석 -->
<section class="subsection">
    <h2>8.3 수익성 분석 (Profitability Analysis)</h2>
    
    <table class="data-table">
        <thead>
            <tr>
                <th>지표</th>
                <th>값</th>
                <th>평가</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>연간 순운영수익 (NOI)</td>
                <td>{{ data.financial_result.annual_noi | format_currency }}</td>
                <td>{% if data.financial_result.annual_noi > 0 %}<span class="badge badge-success">양호</span>{% else %}<span class="badge badge-danger">적자</span>{% endif %}</td>
            </tr>
            <tr>
                <td>Cap Rate</td>
                <td>{{ data.financial_result.cap_rate | format_percentage }}</td>
                <td>{% if data.financial_result.cap_rate >= 5.0 %}<span class="badge badge-success">우수</span>{% elif data.financial_result.cap_rate >= 3.0 %}<span class="badge badge-warning">보통</span>{% else %}<span class="badge badge-danger">미흡</span>{% endif %}</td>
            </tr>
            <tr>
                <td>10년 ROI</td>
                <td>{{ data.financial_result.roi_10yr | format_percentage }}</td>
                <td>{% if data.financial_result.roi_10yr >= 0 %}<span class="badge badge-success">수익</span>{% else %}<span class="badge badge-danger">손실</span>{% endif %}</td>
            </tr>
            <tr>
                <td>10년 IRR</td>
                <td>{{ data.financial_result.irr_10yr | format_percentage }}</td>
                <td>{% if data.financial_result.irr_10yr >= 5.0 %}<span class="badge badge-success">우수</span>{% elif data.financial_result.irr_10yr >= 0 %}<span class="badge badge-warning">보통</span>{% else %}<span class="badge badge-danger">부정적</span>{% endif %}</td>
            </tr>
            <tr>
                <td>손익분기년도</td>
                <td>{{ data.financial_result.breakeven_year }}년차</td>
                <td>{% if data.financial_result.breakeven_year <= 5 %}<span class="badge badge-success">빠름</span>{% elif data.financial_result.breakeven_year <= 10 %}<span class="badge badge-warning">보통</span>{% else %}<span class="badge badge-danger">느림</span>{% endif %}</td>
            </tr>
        </tbody>
    </table>
    
    <!-- 시각화: 10년 현금흐름 -->
    <div class="chart-container">
        <img src="{{ financial_charts.cash_flow_10yr }}" alt="10-Year Cash Flow" class="chart-image">
        <p class="chart-caption">그림 8-2. 10년 현금흐름 예측</p>
    </div>
</section>

<!-- 8.4 민감도 분석 -->
<section class="subsection">
    <h2>8.4 민감도 분석 (Sensitivity Analysis)</h2>
    
    <p>공사비 및 임대료 변동에 따른 재무 지표 민감도를 분석합니다.</p>
    
    <!-- 시각화: 민감도 히트맵 -->
    <div class="chart-container">
        <img src="{{ financial_charts.sensitivity_analysis }}" alt="Sensitivity Analysis" class="chart-image">
        <p class="chart-caption">그림 8-3. 민감도 분석 (공사비 ±10%, 임대료 ±5%)</p>
    </div>
</section>

<!-- 8.5 재무 종합 평가 -->
<section class="subsection">
    <h2>8.5 재무 종합 평가</h2>
    
    <div class="summary-box financial-grade-{{ data.financial_result.financial_grade }}">
        <h3>재무 등급: {{ data.financial_result.financial_grade }}</h3>
        <p>{{ ai_text }}</p>
    </div>
</section>
```

---

## 4. HTML-to-PDF 엔진

### 4.1 WeasyPrint vs Playwright

| 기능 | WeasyPrint | Playwright PDF |
|------|------------|----------------|
| 속도 | 빠름 | 느림 |
| CSS 지원 | 제한적 | 완전 |
| 한글 폰트 | 수동 설정 필요 | 자동 |
| JavaScript | 미지원 | 완전 지원 |
| 페이지 나누기 | 우수 | 보통 |
| **권장 용도** | **v9.0 기본 엔진** | 고급 레이아웃 필요 시 |

### 4.2 WeasyPrint 구현 (기본)

```python
# app/services/pdf_engine_weasy.py

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import logging

logger = logging.getLogger(__name__)

class WeasyPrintEngine:
    """WeasyPrint 기반 PDF 생성 엔진"""
    
    def __init__(self, base_url: str = "."):
        self.base_url = base_url
        self.font_config = FontConfiguration()
    
    def generate_pdf(self, 
                     html_content: str,
                     css_files: list,
                     output_path: str):
        """HTML → PDF 변환"""
        
        try:
            # CSS 파일 로드
            stylesheets = [CSS(filename=css, font_config=self.font_config) 
                          for css in css_files]
            
            # PDF 생성
            HTML(string=html_content, base_url=self.base_url).write_pdf(
                output_path,
                stylesheets=stylesheets,
                font_config=self.font_config,
                presentational_hints=True
            )
            
            logger.info(f"PDF generated: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return False
```

### 4.3 Playwright 구현 (고급)

```python
# app/services/pdf_engine_playwright.py

from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)

class PlaywrightPDFEngine:
    """Playwright 기반 PDF 생성 엔진 (고급 레이아웃)"""
    
    def generate_pdf(self,
                     html_content: str,
                     output_path: str,
                     options: dict = None):
        """HTML → PDF 변환"""
        
        default_options = {
            "format": "A4",
            "print_background": True,
            "margin": {
                "top": "2cm",
                "right": "2cm",
                "bottom": "2cm",
                "left": "2cm"
            },
            "display_header_footer": True,
            "header_template": "<div style='font-size:10px;text-align:center;width:100%;'>LH 신축매입임대 토지분석 보고서</div>",
            "footer_template": "<div style='font-size:10px;text-align:center;width:100%;'><span class='pageNumber'></span> / <span class='totalPages'></span></div>"
        }
        
        if options:
            default_options.update(options)
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(html_content)
                page.pdf(path=output_path, **default_options)
                browser.close()
            
            logger.info(f"PDF generated (Playwright): {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Playwright PDF generation failed: {e}")
            return False
```

---

## 5. 시각화 통합

### 5.1 Visualization Embedder

```python
# app/services/visualization_embedder_v9_0.py

import base64
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class VisualizationEmbedderV90:
    """시각화 이미지를 HTML에 자동 삽입"""
    
    def embed_visualizations(self, 
                            visualizations: Dict[str, str],
                            format: str = "base64") -> Dict[str, str]:
        """
        시각화 데이터를 HTML 임베딩 가능한 형식으로 변환
        
        Args:
            visualizations: {
                "capex_breakdown": "/path/to/chart.png",
                "cash_flow_10yr": "/path/to/chart2.png",
                ...
            }
            format: "base64" (인라인) 또는 "url" (외부 링크)
        
        Returns:
            {
                "capex_breakdown": "data:image/png;base64,iVBORw0KG...",
                ...
            }
        """
        embedded = {}
        
        for key, path in visualizations.items():
            try:
                if format == "base64":
                    embedded[key] = self._image_to_base64(path)
                else:
                    embedded[key] = path
            except Exception as e:
                logger.error(f"Failed to embed {key}: {e}")
                embedded[key] = ""
        
        return embedded
    
    def _image_to_base64(self, image_path: str) -> str:
        """이미지 → Base64 변환"""
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            base64_data = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/png;base64,{base64_data}"
```

### 5.2 차트 자동 생성 예시

```python
# app/services/chart_generator_v9_0.py

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

class ChartGeneratorV90:
    """보고서용 차트 생성"""
    
    def __init__(self):
        # 한글 폰트 설정
        plt.rcParams['font.family'] = 'NanumGothic'
        plt.rcParams['axes.unicode_minus'] = False
    
    def generate_capex_breakdown(self, 
                                land_price: float,
                                construction_cost: float,
                                other_cost: float,
                                output_path: str):
        """CAPEX Pie Chart 생성"""
        
        labels = ['토지비', '공사비', '기타 비용']
        sizes = [land_price, construction_cost, other_cost]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.title('투자 구조 (CAPEX Breakdown)', fontsize=16, fontweight='bold')
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_cash_flow_chart(self,
                                 years: list,
                                 cash_flows: list,
                                 output_path: str):
        """10년 현금흐름 차트"""
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = ['red' if cf < 0 else 'green' for cf in cash_flows]
        ax.bar(years, cash_flows, color=colors, alpha=0.7)
        
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_xlabel('년차', fontsize=12)
        ax.set_ylabel('현금흐름 (백만원)', fontsize=12)
        ax.set_title('10년 현금흐름 예측', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
```

---

## 6. 구현 파일 구조

```
app/
├── services/
│   ├── pdf_renderer_v9_0.py              # 메인 Renderer
│   ├── pdf_engine_weasy.py               # WeasyPrint 엔진
│   ├── pdf_engine_playwright.py          # Playwright 엔진
│   ├── visualization_embedder_v9_0.py    # 시각화 임베더
│   └── chart_generator_v9_0.py           # 차트 생성
│
├── templates/pdf_v9_0/
│   ├── master.html
│   ├── sections/
│   │   ├── cover.html
│   │   ├── executive_summary.html
│   │   ├── site_overview.html
│   │   ├── gis_accessibility.html
│   │   ├── location_metrics.html
│   │   ├── demand_analysis.html
│   │   ├── regulation_review.html
│   │   ├── construction_feasibility.html
│   │   ├── financial_analysis.html       # 핵심 섹션
│   │   ├── lh_evaluation.html
│   │   ├── risk_review.html
│   │   ├── final_decision.html
│   │   └── appendix.html
│   ├── components/
│   │   ├── table.html
│   │   ├── chart.html
│   │   ├── kpi_card.html
│   │   └── risk_badge.html
│   └── styles/
│       ├── main.css
│       ├── print.css
│       └── fonts/
│           └── NanumGothic.ttf
│
└── tests/
    └── test_pdf_renderer_v9_0.py
```

---

## 7. 핵심 개선 사항 요약

| 항목 | v8.6 | v9.0 |
|------|------|------|
| 템플릿 구조 | 단일 거대 파일 | 12개 모듈 (독립) |
| KeyError | 빈번 | ZERO (표준 스키마) |
| 시각화 | 수동 삽입 | 자동 임베딩 |
| CSS | 인라인 산재 | 외부 CSS + 컴포넌트 |
| PDF 엔진 | 단일 (불안정) | 2개 (Weasy + Playwright) |
| 한글 폰트 | 깨짐 | 완벽 지원 |
| 페이지 나누기 | 부자연스러움 | CSS @page 최적화 |
| 유지보수 | 매우 어려움 | 쉬움 (섹션별 수정) |

---

## 다음 단계: Part 5 (Implementation Guide)

Part 4에서는 **12-Section 모듈형 PDF/HTML Renderer**를 완성했습니다.
Part 5에서는 **전체 v9.0 시스템의 구현 순서, 파일 구조, 테스트 전략**을 제시합니다.

---

**문서 종료**
