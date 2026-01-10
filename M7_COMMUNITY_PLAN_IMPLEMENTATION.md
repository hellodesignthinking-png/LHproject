# 🏘️ M7 커뮤니티 계획 모듈 구현 가이드

**작성일**: 2026-01-10  
**버전**: v1.0 (Phase 1 완료)  
**상태**: ✅ 데이터 모델 구축 완료, 통합 작업 진행 중

---

## 📋 M7 모듈 개요

### 핵심 정의

**M7은 계산 모듈이 아닌 '운영·커뮤니티 계획 모듈'입니다.**

- ❌ 새로운 수치 계산 없음
- ❌ 비용·IRR 산정 없음
- ❌ 브랜드 홍보 문구 없음
- ✅ M2~M6 결과를 해석하여 운영 가능한 커뮤니티 계획 도출

### M7의 위상

```
M2~M6: 토지·제도·규모·사업성·LH 판단 → 사업 가능성 증명
M7: 입주자·운영·생활·공동체 → 사업의 "내용" 완성
```

**핵심 질문에 답변**:  
"그래서, 이 건물 안에서는 어떤 삶이 만들어지는가?"

---

## 🎯 M7 모듈 구성 (7개 섹션)

### M7-1. 커뮤니티 기획의 전제 조건

**입력값** (M1~M6에서 자동 연동):
- 위치/권역 특성 (M1)
- 공급 유형 (M3)
- 세대 구성 가정 (M4)
- 사업성 한계 (M5)
- LH 허용 범위 (M6)

### M7-2. 대상 입주자 페르소나 정의

| 구분 | 내용 |
|------|------|
| 1차 대상 | (예) 청년 / 신혼 / 1인가구 |
| 2차 대상 | (예) 지역 종사자 / 창작자 / 돌봄 종사자 |
| 배제 대상 | LH 기준상 부적합 유형 |

**필수 포함**:
- 왜 이 입주자군인가
- 지역과의 연결성
- 공급 유형(M3)과의 정합성

### M7-3. 커뮤니티 목표 설정

**정성 목표**:
- 고립 방지
- 생활 안정
- 지역 연계

**정량 목표** (예시):
- 월 커뮤니티 프로그램 2회 이상
- 입주자 참여율 30% 이상
- 공용공간 이용률 주 3회 이상

### M7-4. 공간 기반 커뮤니티 구성

| 공간 | 기능 | 운영 방식 |
|------|------|-----------|
| 커뮤니티 라운지 | 모임/교육 | 예약제 |
| 공유 주방 | 소규모 교류 | 시간제 |
| 외부 연계 공간 | 지역 프로그램 | 협약 운영 |

**M4 건축 규모와 반드시 연결**

### M7-5. 프로그램 구성 (현실형)

❌ "입주자 교류 프로그램" 같은 추상 문구 금지  
✅ 실제 운영 가능한 수준으로 작성

**예시**:
- 입주 초기 오리엔테이션 (연 1회)
- 월간 생활 워크숍 (자율 참여)
- 지역 연계 프로그램 (분기 1회)

### M7-6. 운영 주체 및 관리 구조

| 항목 | 내용 |
|------|------|
| 운영 주체 | 위탁 / 직접 / 협력 |
| LH 역할 | 감독 / 승인 |
| 입주자 역할 | 참여 / 자율 |
| 분쟁 대응 | 관리 규정 명시 |

**LH 보고서에 매우 중요**

### M7-7. 지속 가능성 & 리스크 관리

- 커뮤니티 과부하 방지
- 참여 강요 금지
- 운영비 과다 발생 방지
- 운영 중단 시 대체안

---

## ✅ 완료된 작업 (Phase 1)

### 1. 데이터 모델 생성

**파일**: `app/models/m7_community_plan.py`

**주요 구성**:
- `ResidentPersona`: 입주자 페르소나
- `CommunityGoal`: 커뮤니티 목표
- `CommunitySpace`: 공간 정의
- `CommunityProgram`: 프로그램 구성
- `OperationStructure`: 운영 구조
- `SustainabilityPlan`: 지속 가능성 계획
- `M7CommunityPlan`: 전체 데이터 모델
- `M7Summary`: 최종보고서용 요약

**핵심 함수**:
```python
def generate_m7_from_context(
    m1_result, m3_result, m4_result, m5_result, m6_result, context_id
) -> M7CommunityPlan
```

M1~M6 결과를 기반으로 M7 커뮤니티 계획을 자동 생성

### 2. Final Report Assembler 통합

**파일**: `app/services/final_report_assembler.py`

**수정 내용**:
- `M7Summary` import 추가
- `FinalReportData` 클래스에 `self.m7` 추가
- `_parse_m7()` 메서드 구현

```python
def _parse_m7(self) -> Optional[M7Summary]:
    """M7 커뮤니티 계획 데이터 추출"""
    # summary 구조 우선 확인
    # fallback 로직 포함
```

---

## ⚠️ 남은 작업 (Phase 2)

### 1. assemble_all_in_one_report에 M7 데이터 추가

**위치**: `app/services/final_report_assembler.py`

**필요 작업**:
```python
def assemble_all_in_one_report(data: FinalReportData) -> Dict[str, Any]:
    # ... 기존 코드 ...
    
    # M7 커뮤니티 계획 (NEW)
    community_plan = None
    community_summary = None
    if data.m7:
        community_plan = {
            "primary_resident_type": data.m7.primary_resident_type,
            "goal_summary": data.m7.community_goal_summary,
            "programs_count": data.m7.key_programs_count,
            "operation_model": data.m7.operation_model,
            "participation_target": data.m7.participation_target_pct
        }
        community_summary = f"본 사업은 {data.m7.primary_resident_type} 입주자를 대상으로, {data.m7.operation_model} 방식의 커뮤니티 운영을 계획하고 있습니다."
    
    return {
        # ... 기존 반환값 ...
        "community_plan": community_plan,
        "community_summary": community_summary,
    }
```

### 2. Master 템플릿에 M7 섹션 추가

**파일**: `app/templates_v13/master_comprehensive_report.html`

**필요 작업**:
```html
<!-- M7: 커뮤니티 계획 -->
<section id="M7" class="section">
  <div class="section-title">M7. 커뮤니티 계획</div>
  
  <div class="section-subtitle">입주자 특성 및 페르소나</div>
  <div class="info-box">
    <strong>주요 대상:</strong> {{ primary_resident_type }}<br>
    <strong>커뮤니티 목표:</strong> {{ community_goal_summary }}
  </div>
  
  <div class="section-subtitle">운영 계획</div>
  <table>
    <thead>
      <tr>
        <th>항목</th>
        <th>내용</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>운영 모델</td>
        <td>{{ operation_model }}</td>
      </tr>
      <tr>
        <td>월간 프로그램 횟수</td>
        <td>{{ monthly_program_frequency }}회</td>
      </tr>
      <tr>
        <td>참여 목표율</td>
        <td>{{ participation_target_pct }}%</td>
      </tr>
      <tr>
        <td>커뮤니티 공간 수</td>
        <td>{{ space_count }}개</td>
      </tr>
    </tbody>
  </table>
</section>
```

### 3. Template Renderer에 M7 데이터 매핑

**파일**: `app/services/template_renderer.py`

**필요 작업**:
```python
def prepare_master_report_context(data: Dict[str, Any]) -> Dict[str, Any]:
    # ... 기존 코드 ...
    
    # ===== M7: 커뮤니티 계획 =====
    m7_data = data.get('m7', {})
    context['primary_resident_type'] = m7_data.get('primary_resident_type', '일반')
    context['community_goal_summary'] = m7_data.get('goal_summary', '커뮤니티 목표 수립 중')
    context['operation_model'] = m7_data.get('operation_model', '운영 모델 검토 중')
    context['monthly_program_frequency'] = m7_data.get('programs_count', 0) // 12 if m7_data.get('programs_count') else 0
    context['participation_target_pct'] = m7_data.get('participation_target', 30)
    context['space_count'] = m7_data.get('space_count', 0)
    
    return context
```

### 4. 테스트 엔드포인트에 M7 데이터 추가

**파일**: `app/routers/pdf_download_standardized.py`

**필요 작업**:
```python
@router.post("/test/create-context/{context_id}")
async def create_test_context(context_id: str):
    test_context = {
        # ... M2~M6 데이터 ...
        
        # M7 데이터 (NEW)
        "m7_result": {
            "summary": {
                "primary_resident_type": "청년형",
                "community_goal_summary": "입주자 간 고립 방지 및 안전망 구축",
                "key_programs_count": 4,
                "operation_model": "LH 직접 운영 또는 협력 운영",
                "sustainability_score": None,
                "space_count": 2,
                "monthly_program_frequency": 2,
                "participation_target_pct": 30.0
            }
        }
    }
```

### 5. M7 Generator API 엔드포인트 (선택)

M2~M6 결과를 기반으로 M7을 동적으로 생성하는 엔드포인트:

```python
@router.post("/api/m7/generate")
async def generate_m7_community_plan(context_id: str):
    """M1~M6 결과를 기반으로 M7 커뮤니티 계획을 생성합니다."""
    from app.models.m7_community_plan import generate_m7_from_context
    
    # Context에서 M1~M6 데이터 로드
    context = context_storage.get_frozen_context(context_id)
    
    # M7 생성
    m7_plan = generate_m7_from_context(
        m1_result=context.get("m1_result", {}),
        m3_result=context.get("m3_result", {}),
        m4_result=context.get("m4_result", {}),
        m5_result=context.get("m5_result"),
        m6_result=context.get("m6_result"),
        context_id=context_id
    )
    
    # M7 Summary 변환
    m7_summary = m7_to_summary(m7_plan)
    
    # Context에 저장
    context["m7_result"] = {
        "summary": {
            "primary_resident_type": m7_summary.primary_resident_type,
            "community_goal_summary": m7_summary.community_goal_summary,
            "key_programs_count": m7_summary.key_programs_count,
            "operation_model": m7_summary.operation_model,
            "sustainability_score": m7_summary.sustainability_score,
            "space_count": m7_summary.space_count,
            "monthly_program_frequency": m7_summary.monthly_program_frequency,
            "participation_target_pct": m7_summary.participation_target_pct
        }
    }
    context_storage.store_frozen_context(context_id, context)
    
    return {
        "success": True,
        "context_id": context_id,
        "m7_summary": m7_summary
    }
```

---

## 📄 M7 출력 보고서 위치 (6종 보고서 기준)

| 보고서 | M7 반영 방식 |
|--------|--------------|
| A. 종합 최종보고서 | 전문 수록 (8~12p) |
| B. 토지주 제출용 | 요약 2~3p |
| C. LH 기술검증 | 운영 가능성 중심 요약 |
| D. 투자 검토 | 운영 리스크 관점 요약 |
| E. 사전 검토 | 1페이지 핵심 |
| F. PT | 2~3 슬라이드 |

---

## 🚨 M7 절대 금지 사항

- ❌ 새로운 수치 계산
- ❌ 비용·IRR 산정
- ❌ 브랜드 홍보 문구
- ❌ 실행 불가능한 프로그램 나열
- ❌ 추상적 컨셉 소개서
- ❌ "입주자 만족도 향상" 같은 모호한 표현

---

## ✅ M7 작성 톤 & 스타일

### 공공주택 행정 문서 톤

- "~로 판단됨"
- "~수준의 운영이 가능"
- "~방식을 계획하고 있습니다"

### 과장·기대·확정 표현 금지

- ❌ "혁신적인 커뮤니티"
- ❌ "입주자 100% 만족"
- ❌ "최고의 생활 환경"
- ✅ "입주자 간 고립 방지를 목표로 함"
- ✅ "월 2회 수준의 프로그램 운영이 가능한 것으로 판단됨"

---

## 🧪 테스트 방법

### 1. M7 데이터 모델 테스트

```python
from app.models.m7_community_plan import generate_m7_from_context

m7_plan = generate_m7_from_context(
    m1_result={"address": "서울시 마포구"},
    m3_result={"selected": {"name": "청년형"}},
    m4_result={"summary": {"legal_units": 20}},
    m5_result=None,
    m6_result=None,
    context_id="test_m7_001"
)

print(f"입주자 유형: {m7_plan.resident_persona.primary_type}")
print(f"프로그램 수: {len(m7_plan.programs)}")
print(f"공간 수: {len(m7_plan.community_spaces)}")
```

### 2. Final Report Assembler 테스트

```python
from app.services.final_report_assembler import FinalReportData

test_context = {
    "m7_result": {
        "summary": {
            "primary_resident_type": "청년형",
            "community_goal_summary": "고립 방지 및 안전망 구축",
            "key_programs_count": 4,
            "operation_model": "LH 직접 운영"
        }
    }
}

data = FinalReportData(test_context, "test_m7_002")
print(f"M7 파싱 결과: {data.m7}")
```

---

## 📚 관련 파일

### 신규 생성
- `app/models/m7_community_plan.py` ⭐ **핵심**

### 수정
- `app/services/final_report_assembler.py` (M7 파싱 추가)

### 수정 예정
- `app/services/template_renderer.py` (M7 데이터 매핑)
- `app/templates_v13/master_comprehensive_report.html` (M7 섹션)
- `app/routers/pdf_download_standardized.py` (테스트 데이터)

---

## 🎯 다음 단계

### 우선순위 1 (필수)
1. `assemble_all_in_one_report`에 M7 데이터 통합
2. Master 템플릿에 M7 섹션 추가
3. Template Renderer에 M7 매핑

### 우선순위 2 (권장)
4. 테스트 엔드포인트에 M7 샘플 데이터 추가
5. M7 Generator API 엔드포인트 구현

### 우선순위 3 (개선)
6. M7 자동 생성 로직 고도화
7. M7 검증 로직 추가 (QA)

---

## 🎉 결론

**M7 커뮤니티 계획 모듈의 Phase 1이 완료되었습니다!**

- ✅ 데이터 모델 완성
- ✅ Final Report Assembler 통합
- ⚠️ 템플릿 및 렌더러 통합 필요

**다음 작업**: Phase 2 통합 작업을 완료하면 M7이 최종 보고서에 포함됩니다! 🚀

---

**작성**: ZeroSite Development Team  
**참고**: M7 MODULE KICK-OFF PROMPT 사용 가능
