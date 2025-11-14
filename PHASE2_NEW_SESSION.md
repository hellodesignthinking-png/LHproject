# 🆕 새창에서 Phase 2 시작하기

## ✅ 준비 완료!

새로운 세션에서 이 문서를 열고 **Phase 2 개발**을 바로 시작할 수 있습니다.

---

## 📍 현재 상태 (2025-11-12)

### Git 상태
```
Branch: phase2/business-simulation
Latest Commits:
  - 13352ec: docs: Phase 2 빠른 시작 가이드 추가
  - c08fc4b: docs: Phase 2 개발 가이드 추가
  - 36760ff: (v2.0-stable) fix: 보고서 생성기에서 dict 접근 방식으로 변경
```

### 서버 상태
- **Port**: 8000
- **URL**: https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai
- **Status**: Running
- **PID**: 2083

### Phase 1 완료 ✅
- 토지진단 자동화
- LH 공식 보고서 생성
- 정책 모니터링 (LH/국토부)
- 프로젝트 관리 시스템
- 회사 브랜딩 ((주)안테나)

---

## 🚀 새창에서 시작하는 3가지 방법

### 방법 1: 빠른 시작 (추천) ⚡

```bash
# 1. 디렉토리 이동
cd /home/user/webapp

# 2. 브랜치 확인
git branch
# * phase2/business-simulation

# 3. 빠른 시작 가이드 열기
cat PHASE2_QUICKSTART.md
```

👉 **PHASE2_QUICKSTART.md**에 즉시 실행 가능한 코드가 있습니다!

### 방법 2: 전체 가이드 읽기 📚

```bash
cd /home/user/webapp
cat PHASE2_GUIDE.md
```

👉 **PHASE2_GUIDE.md**에 전체 개발 계획과 아키텍처가 있습니다.

### 방법 3: 바로 개발 시작 🔨

```bash
# 모듈 디렉토리 생성
cd /home/user/webapp
mkdir -p app/modules/business_simulation

# 파일 생성
cd app/modules/business_simulation
touch __init__.py models.py construction_cost.py purchase_price.py roi_calculator.py service.py

# 첫 번째 파일 편집
# models.py 작성 시작!
```

---

## 📋 Phase 2 개발 체크리스트

### Backend (백엔드)
- [ ] `models.py` - Pydantic 데이터 모델
- [ ] `construction_cost.py` - 건축비 자동 산정
- [ ] `purchase_price.py` - LH 매입가 시뮬레이션
- [ ] `roi_calculator.py` - ROI/IRR 계산
- [ ] `sensitivity.py` - 민감도 분석
- [ ] `service.py` - 비즈니스 로직 통합
- [ ] `app/api/endpoints/business.py` - API 엔드포인트

### Frontend (프론트엔드)
- [ ] React 프로젝트 초기화
- [ ] BusinessSimulator 컴포넌트
- [ ] ROI 차트 시각화
- [ ] 민감도 분석 테이블
- [ ] 기존 시스템 통합

### Testing & Docs (테스트 & 문서)
- [ ] 단위 테스트
- [ ] API 통합 테스트
- [ ] 사용자 매뉴얼
- [ ] API 문서 업데이트

---

## 🎯 첫 번째 기능: 건축비 계산기

`PHASE2_QUICKSTART.md`에 **완전한 예제 코드**가 있습니다:

1. **models.py** - 데이터 모델 (Pydantic)
2. **construction_cost.py** - 계산 로직
3. **business.py** - API 엔드포인트
4. **테스트 curl 명령어**

복사해서 바로 사용하세요! ⚡

---

## 🔗 주요 파일 위치

```
/home/user/webapp/
├── PHASE2_GUIDE.md          ← 📚 전체 개발 가이드
├── PHASE2_QUICKSTART.md     ← ⚡ 빠른 시작 (예제 코드)
├── PHASE2_NEW_SESSION.md    ← 📄 이 파일 (새창 시작용)
├── PLATFORM_ARCHITECTURE.md ← 🏗️ 시스템 아키텍처
├── app/
│   ├── main.py              ← 메인 FastAPI 앱
│   ├── modules/
│   │   ├── policy_monitor/  ← ✅ 정책 모니터링
│   │   ├── project_management/ ← ✅ 프로젝트 관리
│   │   └── business_simulation/  ← 🆕 여기 개발!
│   └── api/endpoints/
│       ├── policy.py        ← ✅ 정책 API
│       ├── projects.py      ← ✅ 프로젝트 API
│       └── business.py      ← 🆕 여기 추가!
└── static/
    └── index.html           ← ✅ 웹 인터페이스
```

---

## 🧪 개발 워크플로우

### 1. 코드 작성
```bash
cd /home/user/webapp/app/modules/business_simulation
# models.py 작성
```

### 2. API 추가
```bash
cd /home/user/webapp/app/api/endpoints
# business.py 작성
```

### 3. 라우터 등록
```python
# app/main.py에 추가
from app.api.endpoints import business
app.include_router(business.router)
```

### 4. 서버 재시작
```bash
cd /home/user/webapp
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 테스트
```bash
curl -X POST "http://localhost:8000/api/business/calculate-cost" \
  -H "Content-Type: application/json" \
  -d '{"unit_type": "YOUTH", "gross_area": 1000, "region": "서울", "num_units": 20}'
```

### 6. 커밋
```bash
cd /home/user/webapp
git add .
git commit -m "feat: 건축비 자동 산정 기능 구현"
```

---

## 🎨 핵심 기능 3가지

### 1️⃣ 건축비 자동 산정
```
입력: 면적, 유형, 지역
출력: 총 건축비, 항목별 비용, 평당 단가
```

### 2️⃣ LH 매입가 시뮬레이션
```
입력: 토지비, 건축비, 사업 유형
출력: LH 매입가, 적정이윤, 평당 가격
```

### 3️⃣ ROI/IRR 계산
```
입력: 투자 현금흐름
출력: ROI (%), IRR (%), 회수 기간
```

---

## 💡 개발 팁

### Pydantic 모델 활용
```python
from pydantic import BaseModel, Field

class CostRequest(BaseModel):
    gross_area: float = Field(gt=0, description="연면적")
    # 자동 검증!
```

### 비동기 API
```python
@router.post("/calculate")
async def calculate(request: CostRequest):
    # 비동기 처리
    result = await service.calculate(request)
    return result
```

### 에러 핸들링
```python
from fastapi import HTTPException

try:
    result = calculator.calculate(request)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

---

## 🐛 문제 해결

### 서버가 안 보이는 경우
```bash
ps aux | grep uvicorn
# 프로세스가 없으면 재시작
cd /home/user/webapp && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Import 오류
```bash
# 파일 존재 확인
ls -la app/modules/business_simulation/
# __init__.py가 있는지 확인!
```

### Git 브랜치 확인
```bash
cd /home/user/webapp
git branch
# * phase2/business-simulation 인지 확인
```

---

## 📊 개발 예상 시간

| 작업 | 예상 시간 |
|------|----------|
| 데이터 모델 | 1-2시간 |
| 건축비 계산 | 2-3시간 |
| LH 매입가 | 2-3시간 |
| ROI/IRR | 3-4시간 |
| API 통합 | 2시간 |
| 테스트 | 2-3시간 |
| **총계** | **12-17시간** |

---

## 🎓 참고 자료

### 실제 데이터 (2025년 기준)
- 청년주택 평당 건축비: **120만원** (서울 1.2배)
- LH 적정이윤: **7-10%**
- 최소 사업 규모: **10세대 이상**

### LH 공식 자료
- LH 토지임대부 분양주택 가이드
- 주택도시기금 융자 조건
- 건축비 적정성 평가 기준

---

## ✅ 시작 전 최종 체크

- [ ] `/home/user/webapp` 디렉토리에 있음
- [ ] `git branch`로 `phase2/business-simulation` 확인
- [ ] 서버 실행 중 확인 (`ps aux | grep uvicorn`)
- [ ] `PHASE2_QUICKSTART.md` 파일 확인
- [ ] `PHASE2_GUIDE.md` 파일 확인

---

## 🚀 지금 바로 시작하세요!

```bash
# 1단계: 위치 확인
cd /home/user/webapp && pwd

# 2단계: 빠른 시작 가이드 열기
cat PHASE2_QUICKSTART.md

# 3단계: 첫 번째 파일 생성
mkdir -p app/modules/business_simulation
cd app/modules/business_simulation
touch __init__.py models.py

# 4단계: 개발 시작! 🎉
```

---

**Phase 2 개발을 시작할 준비가 완료되었습니다!** 🎉

새창을 열고 이 파일(`PHASE2_NEW_SESSION.md`)을 다시 열면 바로 이어서 개발할 수 있습니다.

---

**생성일**: 2025-11-12  
**브랜치**: phase2/business-simulation  
**기반**: v2.0-stable (commit 36760ff)  
**문서**: PHASE2_GUIDE.md, PHASE2_QUICKSTART.md  
**서버**: Running on port 8000
