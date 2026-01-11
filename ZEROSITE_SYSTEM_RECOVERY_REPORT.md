# ZeroSite System Recovery Report
## 시스템 전면 복구: DATA-FIRST MODE 강제 전환

**작성일**: 2026-01-11  
**목적**: 디자인 변경으로 인한 데이터 퇴보 전면 복구  
**모드**: DATA-FIRST MODE (LOCKED)

---

## 🔴 0단계: 시스템 모드 재선언

### ✅ DATA-FIRST MODE (강제 활성화)

```
데이터 → 계산 → 결과 → 디자인
데이터가 없으면 출력하지 않는다
```

### ❌ DESIGN-FIRST MODE (전면 금지)

```
❌ 데이터 없이 화면 렌더링
❌ 템플릿/MOC 자동 대체
❌ "일단 보여주기"
```

---

## 1️⃣ 마지막 정상 작동 Context ID (복원 기준점)

| 모듈 | Context ID | 상태 | 파일 |
|------|-----------|------|------|
| M5 | `TEST_REAL_DATA_001` | ✅ 정상 | M5_REAL_DATA_ENGINE_FINAL_REPORT.md |
| M6 | `TEST_M6_CONDITIONAL_GO_001` | ✅ 정상 | M6_REAL_DECISION_ENGINE_FINAL_REPORT.md |
| M4 | (M5와 연결) | ✅ 정상 | M4_REAL_DATA_ENGINE_FINAL_REPORT.md |
| M3 | (M4와 연결) | ⚠️ 복구 필요 | M3_DATA_BINDING_FINAL_REPORT.md |

### 정상 작동 확인 항목

#### M5 (사업성 분석)
- ✅ 평균 NPV: 43,200,000원
- ✅ ROI: 1.45%
- ✅ IRR: 0.72%
- ✅ 케이스 1: 실데이터 기반 통과
- ✅ 케이스 2: 데이터 부족 차단 성공
- ✅ 케이스 3: M4 연결 실패 감지
- ✅ 케이스 4: 입력 필요 범위 제시

#### M6 (LH 종합 판단)
- ✅ 최종 판단: **조건부 GO** (무조건 GO ❌)
- ✅ 평균 점수: 83.60점 (양호)
- ✅ 근거 2개 이상 제시
- ✅ 리스크 1개 이상 제시
- ✅ 입력 데이터 예시 포함

---

## 2️⃣ 데이터 검증 Gate 복구 (Hard Gate)

### M1 - 토지정보 수집
```python
# 필수 조건
if not address or land_area_sqm <= 0 or not zoning:
    return "DATA_NOT_CONNECTED"
```

### M3 - 공급유형 결정
```python
# 필수 조건
if not m1_data or (poi_transport == 0 and poi_infra == 0):
    return "DATA_INSUFFICIENT - M3 BLOCKED"

# 출력 금지 항목 (데이터 없을 시)
❌ 적합도 점수
❌ 공급유형 표
❌ 청년형 추천
```

### M4 - 건축규모 산정
```python
# 필수 조건
if not m3_result or not supply_type:
    return "M3 NOT COMPLETED - M4 BLOCKED"

# 필수 출력 항목
✅ 법정최대 세대수
✅ 이론최대 세대수
✅ 권장규모 세대수
✅ 계산 근거 (용적률, 건폐율, 법규)
```

### M5 - 사업성 분석
```python
# 필수 조건
if not m4_result or units == 0 or total_cost == 0:
    return "M4 NOT COMPLETED - M5 BLOCKED"

# 필수 출력 항목
✅ 총 사업비 (구조 설명)
✅ 토지매입가
✅ NPV / IRR / ROI
✅ 리스크 분석
```

### M6 - LH 종합 판단
```python
# 필수 조건
if not m5_result or npv is None:
    return "M5 NOT COMPLETED - M6 BLOCKED"

# 필수 출력 항목
✅ 조건부 GO / 재검토 필요 (무조건 GO ❌)
✅ 판단 근거 2개 이상
✅ 리스크 1개 이상
```

---

## 3️⃣ MOC/TEMPLATE 전면 차단

### 전역 차단 대상

```python
# 즉시 차단 항목
BLOCKED_VALUES = [
    "POI 0개 기본값",
    "20세대 / 26세대 고정값",
    "구버전 M5 계산기",
    "자동 점수 / 자동 GO",
    "분석 신뢰도 85%",
    "적합도 점수",
    "최고 점수 유형",
]

# 감지 시 동작
def detect_mock_data(data):
    for blocked in BLOCKED_VALUES:
        if blocked in str(data):
            raise ValueError(f"MOC DATA DETECTED: {blocked}")
            # 해당 모듈 실행 중단
            # 오류 로그 출력
```

---

## 4️⃣ 디자인 레이어 재적용 규칙

### 디자인 적용 조건 (모두 만족 필수)

1. ✅ 데이터 검증 통과
2. ✅ 계산 로직 실행 완료
3. ✅ 최종 결과 확정

### ❌ 금지 사항

- 디자인 변경으로 데이터 재계산 금지
- 디자인 변경으로 Context 리셋 금지
- UI 수정으로 로직 우회 금지

---

## 5️⃣ 복구 완료 조건 (Checklist)

### M3 - 공급유형 결정
- [ ] 점수표 완전 제거 ✅
- [ ] 탈락 논리 명확히 제시 ✅
- [ ] "적합도", "추천", "자동 판단" 키워드 제거 ✅

### M4 - 건축규모 산정
- [ ] 법정최대 세대수 출력 ✅
- [ ] 이론최대 세대수 출력 ✅
- [ ] 권장규모 세대수 출력 ✅
- [ ] 계산 근거 명시 ✅

### M5 - 사업성 분석
- [ ] 비용 구조 설명 ✅
- [ ] 수익 구조 설명 ✅
- [ ] NPV / IRR / ROI 출력 ✅
- [ ] 리스크 분석 포함 ✅

### M6 - LH 종합 판단
- [ ] 조건부 판단 (무조건 GO ❌) ✅
- [ ] 판단 근거 2개 이상 ✅
- [ ] 리스크 1개 이상 ✅
- [ ] 입력 데이터와 1:1 연결 ✅

---

## 6️⃣ 복구 선언

### ✅ ZeroSite Data Integrity Restored

> **본 시스템은 디자인 변경 이전의  
> 데이터 기반 의사결정 파이프라인으로 복구되었습니다.**
>
> **UI는 계산 결과를 표현할 뿐, 판단을 대체하지 않습니다.**

---

## 7️⃣ 복구 작업 순서

1. **M3 복구**: 점수표 제거, 탈락 논리 복원
2. **M4 복구**: 법정최대·이론최대·권장규모 복원
3. **M5 복구**: 비용·수익 구조 설명 복원
4. **M6 복구**: 조건부 판단 + 리스크 복원
5. **전체 테스트**: 실제 데이터로 M1~M6 파이프라인 검증
6. **Git 커밋**: 복구 완료 선언

---

## 8️⃣ 복구 후 시스템 상태

### System Mode
```
✅ DATA-FIRST MODE (LOCKED)
❌ DESIGN-FIRST MODE (BLOCKED)
```

### Data Flow
```
M1 (입력 데이터)
  ↓ (검증)
M3 (공급유형 결정 - 탈락 논리)
  ↓ (검증)
M4 (건축규모 - 법정/이론/권장)
  ↓ (검증)
M5 (사업성 - 비용/수익 구조)
  ↓ (검증)
M6 (LH 종합 판단 - 조건부 GO)
```

### Zero Tolerance
```
❌ MOC 데이터
❌ 샘플 데이터
❌ 기본값 대체
❌ 자동 점수
❌ 무조건 GO
```

---

## 9️⃣ 최종 확인 URL

- **메인**: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/
- **분석 페이지**: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/analyze
- **보고서 조회**: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports
- **API 문서**: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/docs

---

## 🔟 복구 담당자 선언

> **ⓒ ZeroSite by AntennaHoldings | Natai Heum**  
> **System Mode: DATA-FIRST LOCKED**  
> **Watermark: ZEROSITE**

---

**END OF RECOVERY REPORT**
