# 📚 6종 실시간 생성 보고서 아키텍처

## 🎯 설계 원칙

### 불변 원칙 (Hard Rules)
1. **M2~M6 계산 로직/수치는 절대 수정 금지**
2. **같은 데이터, 다른 구조/톤/강조점**
3. **역할: 보고서 편집자·구성자 (계산자 아님)**

### 공통 전제
- **대상지**: 서울특별시 마포구 월드컵북로 120
- **PNU**: 116801010001230045
- **데이터 소스**: M2~M6 분석 결과 (파이프라인 출력)

---

## 📊 6종 보고서 상세 스펙

### A. 종합 최종보고서 (Master Report)

#### 메타데이터
```json
{
  "report_type": "master",
  "report_name": "종합 최종보고서",
  "english_name": "Comprehensive Master Report",
  "target_audience": ["토지주", "LH", "내부 의사결정자", "파트너사"],
  "purpose": "전체 분석을 하나의 논리 흐름으로 통합한 아카이브용 기준 문서",
  "tone": "중립적, 설명 중심, 결론 강요 금지",
  "pages": "20-25",
  "modules_included": ["M2", "M3", "M4", "M5", "M6"],
  "module_weights": {
    "M2": 25,
    "M3": 20,
    "M4": 20,
    "M5": 20,
    "M6": 15
  }
}
```

#### 구성 (20-25 페이지)
```
1. 표지 (1p)
2. Executive Summary (2p)
   - 핵심 결론 4가지
   - KPI 카드 (토지가격, 공급유형, 규모, IRR)
3. 대상지 식별정보 (1p)
   - 표준 식별정보 표
   - 분석 범위 선언
4. M2 토지감정평가 (4-5p)
   - 평가 개요
   - 거래사례 분석
   - 공공 조정 논리
   - 최종 평가액 산출
5. M3 공급유형 판단 (3-4p)
   - 5개 공급유형 비교표
   - 청년형 매입임대 선정 근거
   - 정책 적합성 분석
6. M4 건축규모 판단 (4-5p)
   - 3개 대안 비교
   - B안(34세대) 선정 근거
   - 법규 검토
7. M5 사업성 분석 (4-5p)
   - 3개 시나리오 비교
   - IRR 4.8% 해석
   - 민감도 분석
8. M6 종합 판단 (2-3p)
   - 모듈별 요약
   - 리스크 평가
   - 최종 판단 (조건부)
9. 부록 (1-2p)
   - 기준 및 가정
   - 주의사항
```

#### 톤 가이드라인
```
✅ 허용:
- "~로 판단됨"
- "~로 분석됨"
- "조건 충족 시 검토 가능"
- "추가 실사 필요"

❌ 금지:
- "확정"
- "보장"
- "반드시 ~해야 함"
- 한쪽(토지주/LH)에 치우친 표현
```

---

### B. 토지주 제출용 보고서 (Landowner Persuasion Report)

#### 메타데이터
```json
{
  "report_type": "landowner",
  "report_name": "토지주 제출용 보고서",
  "english_name": "Landowner Submission Report",
  "target_audience": ["개인 토지주", "가족", "법무대리인"],
  "purpose": "토지의 가치·활용 가능성·검토 적합성 설득",
  "tone": "긍정적, 자산 중심, 가능성 강조",
  "pages": "10-14",
  "modules_included": ["M2", "M3_summary", "M4_B_focus", "M6_positive"],
  "module_weights": {
    "M2": 40,
    "M3": 20,
    "M4": 25,
    "M6": 15
  }
}
```

#### 구성 (10-14 페이지)
```
1. 표지 (1p)
2. 이 대상지의 핵심 가치 요약 (1p)
   - "왜 이 땅이 주목받는가"
   - 3가지 핵심 강점
3. 입지·희소성 설명 (2-3p)
   - M2 요약 (시세 중심)
   - 상암 DMC + 홍대/연남 생활권
   - 교통·인프라 접근성
4. 활용 시나리오 (3-4p)
   - M3: 청년형 매입임대 (1순위)
   - M4: B안 34세대 (최적 규모)
   - 공공주택 특례 장점
5. 예상 사업 구조 (2-3p)
   - 개념 수준 사업 개요
   - 예상 투자 구조 (간략)
6. "왜 검토 대상이 되는가" (2p)
   - M6 Soft 버전
   - 긍정적 평가 포인트
   - 다음 단계 안내
```

#### 톤 가이드라인
```
✅ 허용:
- "높은 가치를 지닌"
- "검토 대상으로 적합"
- "긍정적 평가 가능성"
- "충분한 요건 충족"

❌ 금지:
- "확정"
- "매입 예정"
- "보장"
- "반드시 선정됨"
```

---

### C. LH 제출용 기술검증 보고서 (LH Technical Review Report) ⭐ 최우선

#### 메타데이터
```json
{
  "report_type": "lh_technical",
  "report_name": "LH 제출용 기술검증 보고서",
  "english_name": "LH Technical Validation Report",
  "target_audience": ["LH 담당자", "기술검토위원", "외부 심의자"],
  "purpose": "LH 내부 기술검토 및 사전 검증용",
  "tone": "극도로 객관적, 판단보다 근거 제시",
  "pages": "18-22",
  "modules_included": ["M2", "M3", "M4", "M5", "M6"],
  "module_weights": {
    "M2": 20,
    "M3": 15,
    "M4": 25,
    "M5": 25,
    "M6": 15
  },
  "priority": "HIGHEST"
}
```

#### 구성 (18-22 페이지)
```
1. 표지 (1p)
   - 보고서 유형: LH 기술검증용
2. 분석 개요 & 범위 선언 (1p)
   - 분석 목적
   - 적용 기준: LH 매입임대 운영 기준
   - 분석 범위 및 한계
3. 대상지 식별정보 (1p)
   - 고정 표 (주소, PNU, RUN_ID, 기준일)
4. M2 토지감정평가 (4p)
   - 평가 개요
   - 거래사례 분석 (공공 조정 논리 중심)
   - 최종 평가액: {{ price_per_sqm }} 원/㎡
   - 조정 계수 설명
5. M3 공급유형 판단 (3p)
   - 5개 공급유형 비교표
   - 청년형 매입임대 1순위 근거
   - 정책 부합성 검토
6. M4 건축규모 검토 (4p)
   - 3개 대안 비교표
   - B안(34세대) 선정 근거
   - 법규 및 LH 운영 기준 검토
   - 주차·효율률 검증
7. M5 사업성 검증 (4p)
   - 3개 시나리오 비교
   - IRR 4.8% 해석 (공공 기준)
   - 민감도 분석
   - 재무 안정성 평가
8. M6 종합 판단 (2p)
   - 모듈별 평가 요약
   - 리스크 종합 평가
   - 최종 판단 (조건부 검토 가능)
9. 한계 및 추가 검토 필요사항 (1p)
```

#### 톤 가이드라인
```
✅ 필수 사용:
- "~로 판단됨"
- "~로 해석 가능"
- "LH 기준에 부합"
- "추가 실사 필요"
- "조건부 검토 가능"

❌ 절대 금지:
- 설득용 문장
- 긍정적 형용사 남용
- "탁월한", "우수한" 등
- 확정적 표현
```

---

### D. 사업성·투자 검토 보고서 (Investment Feasibility Report)

#### 메타데이터
```json
{
  "report_type": "investment",
  "report_name": "사업성·투자 검토 보고서",
  "english_name": "Investment Feasibility Report",
  "target_audience": ["투자자", "PF 관계자", "내부 재무팀"],
  "purpose": "자본 투입 관점에서의 타당성 분석",
  "tone": "숫자 중심, 냉정, 비교 가능",
  "pages": "12-16",
  "modules_included": ["M4", "M5", "M6", "M2_premise"],
  "module_weights": {
    "M2": 10,
    "M4": 25,
    "M5": 50,
    "M6": 15
  }
}
```

#### 구성 (12-16 페이지)
```
1. 표지 (1p)
2. 사업 구조 개요 (1p)
   - M2 전제 (토지가격)
   - M3 전제 (공급유형)
3. 개발 규모 가정 (3p)
   - M4 요약: B안 34세대
   - 건축 개요
4. 투자비·수익 구조 (5-6p)
   - M5 상세 전개
   - 초기 투자비
   - 예상 수익 구조
   - IRR 4.8% 분석
5. 민간 대비 공공 IRR 비교 (2p)
   - 공공 IRR 4-5% vs 민간 8-12%
   - 리스크 프로파일 비교
6. 투자 관점 리스크 & 회수 구조 (2-3p)
   - 재무 리스크
   - 운영 리스크
   - Exit 전략
7. 종합 판단 (1-2p)
   - M6 투자 관점 버전
```

#### 톤 가이드라인
```
✅ 적극 사용:
- IRR, NPV, 회수 기간
- 민감도 분석
- 리스크 조정 수익률
- 변동성, 레버리지

❌ 지양:
- LH 제출용 문구 그대로 사용
- 공공 보고서 톤
```

---

### E. 사전 검토 리포트 (Quick Review Report)

#### 메타데이터
```json
{
  "report_type": "quick_review",
  "report_name": "사전 검토 리포트",
  "english_name": "Quick Review Report",
  "target_audience": ["내부 임원", "빠른 의사결정자"],
  "purpose": "10분 내 핵심 판단 지원",
  "tone": "압축, 요약, 핵심만",
  "pages": "5-8",
  "modules_included": ["M2_core", "M4_core", "M5_core", "M6_summary"],
  "module_weights": {
    "M2": 20,
    "M4": 25,
    "M5": 35,
    "M6": 20
  }
}
```

#### 구성 (5-8 페이지)
```
1. 대상지 한 장 요약 (1p)
   - 주소, PNU, 위치 개요
   - 핵심 판단 1줄
2. 핵심 수치 카드 (2p)
   - M2: 토지가격
   - M3: 공급유형
   - M4: 규모
   - M5: IRR
3. 리스크 & 포인트 (2p)
   - 강점 3가지
   - 리스크 3가지
   - 완화 방안
4. 최종 판단 (1p)
   - GO / NO-GO / CONDITIONAL
   - 다음 단계
```

#### 톤 가이드라인
```
✅ 특징:
- 표·카드 중심
- 설명 문단 최소화
- 불렛 포인트
- 시각적 아이콘 활용

❌ 지양:
- 장문 설명
- 세부 계산식
```

---

### F. 설명용 프레젠테이션 보고서 (Presentation Report)

#### 메타데이터
```json
{
  "report_type": "presentation",
  "report_name": "설명용 프레젠테이션 보고서",
  "english_name": "Executive Presentation Report",
  "target_audience": ["미팅 참석자 전원"],
  "purpose": "회의·화면 공유·브리핑",
  "tone": "시각 중심, 한 페이지 한 메시지",
  "pages": "10-15 slides",
  "modules_included": ["M2_visual", "M3_visual", "M4_visual", "M5_visual", "M6_visual"],
  "module_weights": {
    "M2": 20,
    "M3": 20,
    "M4": 20,
    "M5": 20,
    "M6": 20
  }
}
```

#### 구성 (10-15 슬라이드)
```
1. 대상지 요약 (1 slide)
2. 입지 & 가치 (M2) (2-3 slides)
   - 위치 지도
   - 가격 카드
   - 조정 논리
3. 공급유형 & 규모 (M3/M4) (3-4 slides)
   - 공급유형 비교 (1 slide)
   - 청년형 선정 근거 (1 slide)
   - 3개 대안 비교 (1 slide)
   - B안 선정 근거 (1 slide)
4. 사업성 핵심 수치 (M5) (3 slides)
   - IRR 카드
   - 시나리오 비교
   - 민감도 그래프
5. 종합 판단 (M6) (2 slides)
   - 모듈별 요약
   - 최종 판단
```

#### 디자인 규칙
```
✅ 필수:
- 슬라이드 1장 = 메시지 1개
- 표 1개 = 슬라이드 1장
- 문장 3줄 초과 금지
- 아이콘/색상 적극 활용

❌ 금지:
- 한 슬라이드에 표 2개 이상
- 긴 문단
- 복잡한 계산식
```

---

## 🔄 데이터 플로우

### 공통 데이터 소스
```
Pipeline Output (M2~M6)
  ├─ context_id (RUN_ID)
  ├─ M2: appraisal_result
  ├─ M3: supply_type_result
  ├─ M4: capacity_result
  ├─ M5: feasibility_result
  └─ M6: final_review_result
```

### 보고서별 데이터 매핑
```python
REPORT_DATA_MAPPING = {
    "master": {
        "modules": ["M2", "M3", "M4", "M5", "M6"],
        "emphasis": "balanced",
        "detail_level": "full"
    },
    "landowner": {
        "modules": ["M2", "M3_summary", "M4_B", "M6_positive"],
        "emphasis": "value_focused",
        "detail_level": "simplified"
    },
    "lh_technical": {
        "modules": ["M2", "M3", "M4", "M5", "M6"],
        "emphasis": "technical_validation",
        "detail_level": "full_with_standards"
    },
    "investment": {
        "modules": ["M2_premise", "M4", "M5", "M6"],
        "emphasis": "financial_metrics",
        "detail_level": "numbers_focused"
    },
    "quick_review": {
        "modules": ["M2_core", "M4_core", "M5_core", "M6_summary"],
        "emphasis": "decision_support",
        "detail_level": "executive_summary"
    },
    "presentation": {
        "modules": ["M2_visual", "M3_visual", "M4_visual", "M5_visual", "M6_visual"],
        "emphasis": "visual_communication",
        "detail_level": "slides"
    }
}
```

---

## 📏 공통 컴포넌트

### 대상지 식별정보 표 (모든 보고서 공통)
```html
<table class="site-identity-table">
    <tr>
        <th>대상지 주소</th>
        <td>{{ meta.address }}</td>
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
        <td style="font-family: monospace;">{{ meta.run_id }}</td>
    </tr>
    <tr>
        <th>적용 기준</th>
        <td>LH 매입임대 운영 기준 / 공공주택 사업 기준</td>
    </tr>
</table>
```

---

## ✅ 최종 검증 체크리스트

모든 보고서는 다음 질문에 "YES"여야 합니다:

1. **계산 불변성**: 이 보고서는 M2~M6 계산을 바꾸지 않았는가? ☐
2. **목적 적합성**: 같은 데이터로 목적에 맞게 다르게 말하고 있는가? ☐
3. **독자 명확성**: 독자가 누구인지 명확히 느껴지는가? ☐
4. **설명 충분성**: 설명이 부족한 페이지는 없는가? ☐
5. **관점 일관성**: LH/토지주/투자자 관점이 섞이지 않았는가? ☐

---

## 🚀 구현 우선순위

### Phase 1 (최우선)
1. **C. LH 제출용 기술검증 보고서** ⭐⭐⭐
2. 대상지 식별정보 표 공통 컴포넌트화
3. 백엔드 라우팅 추가

### Phase 2
4. **A. 종합 최종보고서**
5. **B. 토지주 제출용 보고서**

### Phase 3
6. **D. 사업성·투자 검토 보고서**
7. **E. 사전 검토 리포트**

### Phase 4
8. **F. 설명용 프레젠테이션 보고서**

---

**문서 작성일**: 2025-12-31  
**작성자**: Claude (AI Assistant)  
**문서 상태**: ✅ **READY FOR IMPLEMENTATION**
