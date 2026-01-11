# M3 보고서 전면 재작성 진행 현황

## 📋 작업 개요

LH 신축매입임대 공급유형 결정 보고서(M3)를 **정책·입지·수요 분석 보고서** 수준으로 전면 재작성

---

## ✅ 완료된 작업

### 1. M3 HTML 템플릿 전면 재작성 완료
- **파일**: `app/templates_v13/m3_supply_type_format_v2_enhanced.html`
- **커밋**: `c6b4729` - "feat: Create enhanced M3 report template with comprehensive analysis"
- **페이지 수**: 기존 6페이지 → **8페이지** 확장

### 2. 9가지 요구사항 모두 반영

#### ✅ 1. 보고서 성격 재정의
- **I. 보고서 개요 및 목적** 섹션 신규 추가
- 정책 보고서 + 입지·수요 분석 + 사업 의사결정 보고서 성격 명시
- 공급유형 결정의 파급효과 표 포함 (설계/세대/수요/LH 매입)
- ZeroSite 모듈 연계 구조 시각화

#### ✅ 2. 입지 분석 강화 (해석형으로 전환)
- **II. 대상지 입지 분석 (해석형)** 섹션
- ❌ 단순 POI 개수 나열 제거
- ✅ 유형별 출퇴근 가능성 분석 테이블 추가
- ✅ 청년형/신혼형/고령자형 필수 인프라 체크리스트 각각 작성
- ✅ 도보/자전거/생활 동선 관점 해석 포함

#### ✅ 3. 인구·수요 구조 분석 (신규 필수 섹션)
- **III. 인구·수요 구조 분석 (정량)** 섹션 신규 추가
- 연령대별 인구 구조 테이블 (20-34세, 30-39세, 40-64세, 65세 이상)
- 1-2인 가구 비율 및 임차 가구 비중 분석
- 최근 5년 임차 가구 증가 추세 테이블
- **"왜 구조적으로 청년형 수요가 발생할 수밖에 없는지"** 논리 서술

#### ✅ 4. 공급유형별 적합성 비교 (탈락 논리)
- **IV. 공급유형별 적합성 비교 (탈락 논리)** 섹션
- ❌ 단순 점수표 제거
- ✅ 유형별 세부 분석: 입지·수요·사업 구조·LH 정책 우선도 4축 평가
- ✅ 각 유형별 탈락 사유 박스 (청년형/신혼형 I·II/고령자형/다자녀형)
- ✅ "왜 다른 유형은 구조적으로 불리한지" 명확히 서술

#### ✅ 5. M4·M5·M6 연계 논리 (핵심 추가)
- **V. M4·M5·M6 연계 논리** 섹션 신규 추가
- M4 건축규모: 평형 구성, 세대 수, 공용시설, 주차, 건축비 효율성
- M5 사업성: 임대 회전율, 공실 리스크, 임대료 수준, 운영비, 수익성
- M6 LH 심사: 정책 적합성, 수요 안정성, 운영 리스크, 지역 균형, 매입 우선순위
- M3 → M4 → M5 → M6 연쇄 효과 시각화 박스

#### ✅ 6. 종합 판단 강화 (리스크 명시)
- **VI. 종합 판단 및 리스크 요인** 섹션
- ✅ 단정적 표현: "정책·수요·사업 구조상 다른 선택지가 성립하기 어려움"
- ✅ 리스크 요인 2-3개 반드시 명시 (리스크 유형/구체적 리스크/대응 방안)
- ✅ 강점 체크리스트 + 권장사항 목록

#### ✅ 7. 분석 방법론 및 제한사항
- **VII. 분석 방법론 및 제한사항** 섹션
- 5단계 분석 방법론 명시
- 데이터 출처 (통계청, 국토교통부, LH 내부 자료)
- 제한사항 5가지 명시 (정책 변동, 지역 개발, 최종 승인 권한 등)

#### ✅ 8. 보고서 톤 & 디자인
- ❌ 학술 논문 톤 제거
- ✅ 공공기관 실무 보고서 톤으로 변경
- ✅ "~로 판단한다" 대신 "~한 구조이기 때문에 ~로 판단한다" 사용
- ✅ ZeroSite 워터마크 (body::before pseudo-element)
- ✅ 모든 페이지 하단 공통 표기: "ⓒ ZeroSite by AntennaHoldings | Natai Heum"

#### ✅ 9. 최종 출력 목표 충족
- LH 실무자가 추가 설명 없이 이해 가능한 수준
- "이 사업지는 청년형으로 가는 게 맞다"라고 즉시 납득 가능
- 의사결정 근거 문서로서의 위상 확보

---

## 🔄 다음 단계 (백엔드 작업 필요)

### 1. M3SupplyTypeReport 데이터 모델 확장
**현재 모델** (`app/models/phase8_report_types.py`):
```python
class M3SupplyTypeReport(BaseModel):
    # 기존 필드 (15개 정도)
    recommended_housing_type: str
    housing_type_score: float
    candidate_types: List[HousingTypeCandidate]
    # ...
```

**필요한 신규 필드** (약 50개 이상):
- 입지 분석 관련 (15개)
  - transport_subway_distance, transport_subway_time, transport_subway_rating
  - commute_youth_fit, commute_newlywed_fit, commute_senior_fit
  - youth_commercial_count, youth_night_safety
  - newlywed_edu_count, newlywed_parking
  - senior_medical_count, senior_walkability
  - location_summary, transport_interpretation
  
- 인구·수요 구조 (20개)
  - region_name
  - pop_youth_count, pop_youth_ratio
  - pop_newlywed_count, pop_newlywed_ratio
  - household_single_count, household_single_ratio, household_single_rent_ratio
  - trend_year_5, trend_rent_5, trend_single_rent_5
  - age_structure_interpretation
  - structural_demand_conclusion
  - why_structural_demand

- 유형별 비교 (10개)
  - type_comparison: List[TypeComparison]
  - type_details: List[TypeDetail]
  
- M4·M5·M6 연계 (15개)
  - m4_linkage_explanation
  - m4_unit_mix_advantage
  - m4_cost_efficiency
  - m5_linkage_explanation
  - m5_turnover_advantage
  - m5_vacancy_risk
  - m6_linkage_explanation
  - m6_policy_fit
  - m6_strategic_insight
  - m4_design_direction
  - m5_business_advantage
  - m6_approval_advantage

- 리스크 및 권장사항 (5개)
  - strengths: List[str]
  - risk_factors: List[RiskFactor]
  - risk_management_strategy
  - recommendations: List[str]
  - final_decision_rationale

### 2. Phase8ModuleReportGenerator 로직 업데이트
**파일**: `app/services/phase8_module_report_generator.py`
**메소드**: `generate_m3_report()`

업데이트 필요 사항:
- 인구 데이터 통계 생성 로직
- 입지 해석 로직 (청년형/신혼형/고령자형 체크리스트)
- 유형별 탈락 사유 생성 로직
- M4·M5·M6 연계 설명 생성 로직
- 리스크 요인 2-3개 자동 도출

### 3. 테스트 및 검증
- Mock 데이터로 M3 보고서 생성 테스트
- HTML 렌더링 확인
- PDF 변환 테스트
- 실제 사업지 데이터로 검증

---

## 📊 현재 상태

| 항목 | 상태 | 비고 |
|------|------|------|
| M3 HTML 템플릿 | ✅ 완료 | 8페이지, 9가지 요구사항 모두 반영 |
| 데이터 모델 확장 | ⏳ 진행 중 | 약 50개 신규 필드 추가 필요 |
| 생성 로직 업데이트 | ⏳ 대기 중 | 데이터 모델 완성 후 진행 |
| 테스트 | ⏳ 대기 중 | 전체 로직 완성 후 진행 |

---

## 📝 커밋 히스토리

- **c6b4729**: feat: Create enhanced M3 report template with comprehensive analysis
  - 8-page comprehensive report structure
  - Population & demand structure analysis (NEW)
  - Interpretative location analysis (not POI counts)
  - Supply type elimination logic
  - M4·M5·M6 module linkage
  - Risk factors & mitigation
  - ZeroSite branding & watermarks

---

## 🎯 최종 목표

### 완성 시 기대 효과

1. **LH 실무자 관점**
   - 추가 설명 없이 보고서만으로 의사결정 가능
   - "청년형으로 가야 하는 이유"를 즉시 이해
   - M4·M5·M6 진행 시 근거 자료로 활용

2. **ZeroSite 플랫폼 관점**
   - M3가 전체 파이프라인의 분기점 역할 수행
   - 이후 모듈 (M4·M5·M6)과의 논리적 연결 강화
   - 보고서 품질이 "추천서" → "의사결정 근거서" 수준으로 상향

3. **사업 수행자 관점**
   - 공급유형 선택에 대한 확신 확보
   - 리스크 요인 사전 인지 및 대응 방안 확보
   - LH 심사 통과 가능성 제고

---

## 🔗 관련 파일

### 완료
- `app/templates_v13/m3_supply_type_format_v2_enhanced.html` ✅

### 진행 예정
- `app/models/phase8_report_types.py` (M3SupplyTypeReport 확장)
- `app/services/phase8_module_report_generator.py` (generate_m3_report 업데이트)

---

## 📌 주의사항

1. **기존 M3 보고서와의 호환성**
   - 기존 템플릿: `m3_supply_type_format.html`
   - 신규 템플릿: `m3_supply_type_format_v2_enhanced.html`
   - 백엔드에서 어느 템플릿을 사용할지 선택 가능하도록 설계

2. **데이터 생성 로직 복잡도**
   - 약 50개 이상의 신규 필드 생성 필요
   - 실제 통계 데이터 연동 vs Mock 데이터 생성 선택 필요
   - 성능 최적화 고려 (캐싱, 비동기 처리 등)

3. **테스트 우선순위**
   - Phase 1: Mock 데이터로 HTML 렌더링 확인
   - Phase 2: 실제 M1·M2 데이터와 연동
   - Phase 3: PDF 변환 및 최종 검증

---

**작성일**: 2026-01-11  
**작성자**: ZeroSite Development Team  
**브랜치**: `feature/expert-report-generator`  
**최신 커밋**: `c6b4729`
