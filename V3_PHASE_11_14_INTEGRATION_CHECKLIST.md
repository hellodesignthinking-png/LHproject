# V3 Template Phase 11-14 Integration Checklist

## 현재 상태 분석

### ✅ v3 Template 존재하는 섹션
1. **Section 01**: Executive Summary
2. **Section 02**: 대상지 개요 (Site Overview)
3. **Section 03**: 도시계획 및 법규
4. **Section 04**: Phase 6.8 AI 수요 예측
5. **Section 05**: Phase 7.7 시장 분석
6. **Section 06**: Phase 8 공사비 분석
7. **Section 07**: Phase 2.5 재무 분석
8. **Section 08**: 정책 프레임워크 분석
9. **Section 09**: 36개월 실행 로드맵
10. **Section 10**: 학술적 결론
11. **Section 11**: 리스크 매트릭스
12. **Section 12**: 부록

### ❌ v3 Template에 누락된 Phase 11-14 섹션
1. **Phase 11**: LH Policy Rules & Architecture Design (건축 설계)
2. **Phase 13**: Academic Narrative Engine (학술 서사)
3. **Phase 14**: Critical Path Timeline (공정 일정)

---

## 통합 계획

### Option 1: Section 02-1 확장 (건축물 개요 → Phase 11 통합)
**현재**: Section 02-1 "건축물 개요"가 있지만 Phase 11 데이터 미반영
**수정**: Phase 11 데이터를 Section 02-1에 통합
- LH 공급 유형별 세대수 계산
- 15% 공용면적 규칙
- 주차대수 산정 (서울 0.3, 일반 0.2)
- 설계 철학 자동 생성

### Option 2: Section 07-1 신규 생성 (Phase 11 Architecture Design)
**신규 섹션**: Section 07-1 "Phase 11: 건축 설계 자동화"
**위치**: Section 07 (재무 분석) 이후
**내용**:
- 5가지 LH 공급 유형 분석
- 자동 세대수 계산
- 단위면적별 배분
- 공용면적/주차장 규칙
- 설계 철학 narrative

### Option 3: Section 09 확장 (36개월 로드맵 → Phase 14 통합)
**현재**: Section 09 "36개월 실행 로드맵" 존재
**수정**: Phase 14 Critical Path 데이터 통합
- 8단계 Critical Path
- 16개 주요 리스크
- 마일스톤 추적
- 의존성 분석

### Option 4: Section 10 확장 (학술적 결론 → Phase 13 통합)
**현재**: Section 10 "학술적 결론" 존재
**수정**: Phase 13 Academic Narrative 통합
- 5단계 서사 구조 (WHAT/SO WHAT/WHY/INSIGHT/CONCLUSION)
- KDI 연구보고서 스타일
- 정책 의미 분석
- 투자 프레임워크

---

## 권장 통합 방안 (Recommended Integration)

### 🎯 Phase 11 통합: Section 02-1 확장
**파일**: `app/services_v13/report_full/lh_expert_edition_v3.html.jinja2`
**라인**: ~2627-2788 (Section 02-1 건축물 개요)

**추가할 변수**:
```jinja2
{{ phase_11_total_units }}        # 총 세대수
{{ phase_11_unit_distribution }}  # 유형별 세대수 배분
{{ phase_11_common_area_ratio }}  # 공용면적 비율
{{ phase_11_parking_count }}      # 주차대수
{{ phase_11_parking_ratio }}      # 주차비율
{{ phase_11_design_philosophy }}  # 설계 철학 (narrative)
```

### 🎯 Phase 14 통합: Section 09 확장
**파일**: `app/services_v13/report_full/lh_expert_edition_v3.html.jinja2`
**라인**: ~4790-5200 (Section 09 로드맵)

**추가할 변수**:
```jinja2
{{ phase_14_timeline }}           # Timeline 객체
{{ phase_14_total_months }}       # 총 개월수
{{ phase_14_phases }}             # 8단계 리스트
{{ phase_14_critical_path }}      # Critical Phase ID 리스트
{{ phase_14_key_risks }}          # 16개 주요 리스크
{{ phase_14_narrative }}          # 일정 분석 narrative
```

### 🎯 Phase 13 통합: Section 10 확장
**파일**: `app/services_v13/report_full/lh_expert_edition_v3.html.jinja2`
**라인**: ~5200-5400 (Section 10 학술적 결론)

**추가할 변수**:
```jinja2
{{ phase_13_narrative }}          # AcademicNarrative 객체
{{ phase_13_what }}               # WHAT 섹션
{{ phase_13_so_what }}            # SO WHAT 섹션
{{ phase_13_why }}                # WHY 섹션
{{ phase_13_insight }}            # INSIGHT 섹션
{{ phase_13_conclusion }}         # CONCLUSION 섹션
```

---

## 실행 단계

### Step 1: 변수 매핑 확인
**파일**: `generate_v3_phase_integrated_report.py`
**확인 사항**:
- Phase 11 데이터가 context에 포함되는가?
- Phase 13 데이터가 context에 포함되는가?
- Phase 14 데이터가 context에 포함되는가?

### Step 2: 템플릿 수정
**파일**: `app/services_v13/report_full/lh_expert_edition_v3.html.jinja2`
**수정 위치**:
1. Section 02-1 (라인 2627-2788)
2. Section 09 (라인 4790-5200)
3. Section 10 (라인 5200-5400)

### Step 3: 통합 테스트
**테스트 스크립트**:
```bash
cd /home/user/webapp
python generate_v3_phase_integrated_report.py
```

**확인 사항**:
- HTML 생성 성공
- Phase 11 데이터 출력 확인
- Phase 13 데이터 출력 확인
- Phase 14 데이터 출력 확인
- PDF 변환 가능 확인

---

## 예상 결과

### Before (현재)
- v3 템플릿: Phase 6.8, 7.7, 8, 2.5만 반영
- Phase 11-14: 별도 데모 리포트로만 존재
- 통합 안됨

### After (수정 후)
- v3 템플릿: Phase 6.8, 7.7, 8, 2.5, **11, 13, 14** 모두 반영
- 완전 통합 리포트 생성 가능
- 단일 PDF로 모든 Phase 데이터 출력

---

## 체크리스트

- [ ] Phase 11 변수가 context에 포함되는지 확인
- [ ] Phase 13 변수가 context에 포함되는지 확인
- [ ] Phase 14 변수가 context에 포함되는지 확인
- [ ] Section 02-1에 Phase 11 통합
- [ ] Section 09에 Phase 14 통합
- [ ] Section 10에 Phase 13 통합
- [ ] 통합 테스트 실행
- [ ] HTML 생성 확인
- [ ] PDF 변환 확인
- [ ] 데모 리포트와 비교 검증

---

**생성일**: 2025-12-10
**상태**: 점검 중
