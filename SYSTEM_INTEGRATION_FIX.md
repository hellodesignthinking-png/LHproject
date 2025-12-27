# ZeroSite v4.0 시스템 통합 수정 계획

## 📋 현재 상태 분석

### ✅ 완료된 구현
1. **백엔드 모듈**: M1-M6 모든 모듈 서비스 구현 완료
   - `app/modules/m1_land_info/service.py` ✅
   - `app/modules/m2_appraisal/service.py` ✅
   - `app/modules/m3_lh_demand/service.py` ✅
   - `app/modules/m4_capacity/service_v2.py` ✅
   - `app/modules/m5_feasibility/service.py` ✅
   - `app/modules/m6_lh_review/service_v3.py` ✅

2. **파이프라인 코어**: 6-MODULE 파이프라인 아키텍처
   - `app/core/pipeline/zer0site_pipeline.py` ✅
   - 단방향 데이터 플로우 (M1→M2→M3→M4→M5→M6)
   - M2 AppraisalContext 불변성 보장

3. **보고서 생성**: 6종 최종보고서 API
   - 종합 최종보고서 (All-in-One)
   - 토지주 제출용 요약보고서
   - LH 제출용 기술검증 보고서
   - 사업성·투자 검토 보고서
   - 사전 검토 리포트
   - 설명용 프레젠테이션 보고서

4. **프론트엔드 UI**: Pipeline Orchestrator 구현
   - M1 입력 UI (8 steps)
   - 파이프라인 실행 UI
   - 결과 표시 UI
   - 6종 보고서 다운로드 버튼

### ❌ 미완성/문제점

#### 1. M1 Context Freeze API - 필수 필드 문제
**문제**:
```json
{
  "detail": [
    {"type": "missing", "loc": ["body", "road_address"], "msg": "Field required"},
    {"type": "missing", "loc": ["body", "sido"], "msg": "Field required"},
    {"type": "missing", "loc": ["body", "sigungu"], "msg": "Field required"},
    {"type": "missing", "loc": ["body", "dong"], "msg": "Field required"},
    ...
  ]
}
```

**원인**: `FreezeContextRequest` 모델이 너무 많은 필수 필드 요구

**해결 방안**:
1. M1 Step1-8에서 수집한 데이터를 모두 freeze 요청에 포함
2. 또는 `FreezeContextRequest` 모델의 필드를 Optional로 변경
3. 프론트엔드에서 모든 필수 데이터 수집 확인

#### 2. 파이프라인 실행 후 데이터 저장 문제
**문제**: 파이프라인 실행 결과가 메모리에만 저장되고 DB/Redis에 저장되지 않음

**해결 방안**:
- `results_cache` 딕셔너리 → Redis 또는 SQLite DB로 변경
- `context_id`로 결과 조회 가능하도록 저장 로직 추가

#### 3. 모듈별 보고서 데이터 표시 누락
**문제**: M2-M6 각 모듈의 상세 결과를 프론트엔드에서 표시하지 못함

**해결 방안**:
- 프론트엔드에 M2-M6 결과 표시 컴포넌트 추가
- 각 모듈 데이터를 구조화된 형태로 반환

#### 4. 6종 보고서 API와 실제 데이터 연동 부족
**문제**: 보고서 API는 존재하지만 실제 파이프라인 데이터와 연동되지 않음

**해결 방안**:
- 파이프라인 결과를 context_id로 저장
- 보고서 API에서 context_id로 데이터 조회
- M2-M6 데이터를 보고서에 포함

---

## 🔧 수정 계획

### Priority 1: M1 Context Freeze 수정
**파일**: `app/api/endpoints/m1_step_based.py`

**변경사항**:
```python
# FreezeContextRequest 모델 수정
class FreezeContextRequest(BaseModel):
    # 필수 필드만 유지
    address: str
    area: float
    coordinates: Dict[str, float]
    
    # 나머지는 Optional
    road_address: Optional[str] = None
    jibun_address: Optional[str] = None
    sido: Optional[str] = None
    sigungu: Optional[str] = None
    dong: Optional[str] = None
    zone_type: Optional[str] = None
    bcr: Optional[float] = None
    far: Optional[float] = None
    road_width: Optional[float] = None
    # ... 기타 필드
```

### Priority 2: 파이프라인 결과 저장소 구현
**파일**: `app/api/endpoints/pipeline_reports_v4.py`

**변경사항**:
```python
# 메모리 캐시 → SQLite/Redis로 변경
from app.database import get_db_session
from app.models.pipeline_results import PipelineResultModel

@router.post("/analyze")
async def analyze_pipeline(request: PipelineAnalysisRequest):
    # 파이프라인 실행
    result = pipeline.run(request.parcel_id)
    
    # DB에 저장
    db_result = PipelineResultModel(
        context_id=f"ctx_{uuid.uuid4().hex[:12]}",
        parcel_id=request.parcel_id,
        m1_data=result.land.dict(),
        m2_data=result.appraisal.dict(),
        m3_data=result.housing_type.dict(),
        m4_data=result.capacity.dict(),
        m5_data=result.feasibility.dict(),
        m6_data=result.lh_review.dict(),
        created_at=datetime.now()
    )
    db.add(db_result)
    db.commit()
    
    return {"context_id": db_result.context_id, ...}
```

### Priority 3: 프론트엔드 M2-M6 결과 표시 컴포넌트
**파일**: `frontend/src/components/pipeline/`

**새로 생성할 파일**:
- `M2AppraisalDisplay.tsx` - 감정평가 결과
- `M3HousingTypeDisplay.tsx` - 주거유형 결과
- `M4CapacityDisplay.tsx` - 건축규모 결과 (이미 존재)
- `M5FeasibilityDisplay.tsx` - 사업성 결과
- `M6LHReviewDisplay.tsx` - LH 심사예측 결과

### Priority 4: 6종 보고서 데이터 연동
**파일**: `app/routers/pdf_download_standardized.py`

**변경사항**:
```python
@router.get("/reports/final/{report_type}/html")
async def get_final_report_html(
    report_type: str,
    context_id: str
):
    # DB에서 파이프라인 결과 조회
    pipeline_result = db.query(PipelineResultModel).filter_by(
        context_id=context_id
    ).first()
    
    if not pipeline_result:
        raise HTTPException(404, "분석 데이터를 찾을 수 없습니다.")
    
    # M2-M6 데이터를 보고서에 포함
    report_data = {
        "m2": pipeline_result.m2_data,
        "m3": pipeline_result.m3_data,
        "m4": pipeline_result.m4_data,
        "m5": pipeline_result.m5_data,
        "m6": pipeline_result.m6_data,
    }
    
    # 보고서 생성
    html = generate_report(report_type, report_data)
    return HTMLResponse(html)
```

---

## 🚀 실행 순서

### Step 1: M1 API 수정
```bash
cd /home/user/webapp
# app/api/endpoints/m1_step_based.py 수정
# FreezeContextRequest 모델의 필드를 Optional로 변경
```

### Step 2: 데이터베이스 모델 추가
```bash
# app/models/pipeline_results.py 생성
# SQLAlchemy 모델 정의
# alembic migration 실행
```

### Step 3: 파이프라인 API 저장 로직 추가
```bash
# app/api/endpoints/pipeline_reports_v4.py 수정
# 파이프라인 결과를 DB에 저장
```

### Step 4: 보고서 API 데이터 연동
```bash
# app/routers/pdf_download_standardized.py 수정
# context_id로 DB 조회 후 보고서 생성
```

### Step 5: 프론트엔드 결과 표시 컴포넌트 추가
```bash
cd frontend/src/components/pipeline
# M2-M6 Display 컴포넌트 생성
# PipelineOrchestrator.tsx에 통합
```

### Step 6: 전체 플로우 테스트
```bash
# 1. M1 입력 → Context Freeze
# 2. 파이프라인 실행 → 결과 저장
# 3. 결과 표시 → M2-M6 데이터 확인
# 4. 6종 보고서 생성 → PDF 다운로드
```

---

## 📊 예상 결과

### ✅ 수정 후 기대 효과
1. **M1→M6 완전한 데이터 플로우**
   - 사용자 입력 → 파이프라인 실행 → 결과 저장 → 보고서 생성

2. **모듈별 상세 결과 표시**
   - M2: 토지 감정가, 신뢰도, 평가 근거
   - M3: LH 선호유형, 수요 예측
   - M4: 법적/인센티브 용적률, 세대수, 주차대수
   - M5: NPV, IRR, ROI, 사업성 판단
   - M6: LH 점수 (110점), 최종 결정 (GO/NO-GO)

3. **6종 보고서 완전 작동**
   - 각 보고서에 실제 파이프라인 데이터 포함
   - HTML/PDF 형식으로 다운로드 가능
   - 대상 독자별 맞춤 콘텐츠

---

## ⚠️ 주의사항

### 데이터 일관성
- M2 AppraisalContext는 생성 후 수정 불가 (frozen=True)
- 역방향 참조 금지 (M4가 M2 수정 불가)
- Context 기반 데이터 전달만 허용

### 성능 고려사항
- 파이프라인 실행 시간: 예상 5-10초
- 보고서 생성 시간: 예상 2-5초
- 메모리 사용량: 파이프라인 결과 캐싱으로 인한 증가

### 보안
- API 키 노출 방지
- Context ID 기반 접근 제어
- 보고서 다운로드 권한 확인

---

**작성일**: 2025-12-27  
**작성자**: Claude AI Assistant  
**우선순위**: 🔴 HIGH  
**예상 소요 시간**: 4-6 hours
