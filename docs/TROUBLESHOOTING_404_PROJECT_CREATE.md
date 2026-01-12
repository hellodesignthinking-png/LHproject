# 🚨 프로젝트 생성 404 오류 해결 가이드

## 📋 문제 현황
- **URL**: `/static/projects.html`
- **액션**: [+ 새 프로젝트 만들기] 클릭
- **에러**: `POST /api/projects → 404 Not Found`

## 🔍 원인 진단 결과

### ✅ 코드 레벨: 정상
```python
# app/api/endpoints/project_management.py
router = APIRouter(prefix="/api/projects", tags=["Project Management"])

@router.post("", response_model=Project)
async def create_project(request: CreateProjectRequest, ...):
    # 구현 완료
```

```python
# app/main.py (line 356)
app.include_router(project_management_router)
```

### ❌ 실행 레벨: 미반영
- 현재 실행 중인 서버(PID 66607)에 최신 코드가 로드되지 않음
- OpenAPI spec에 `/api/projects` POST 엔드포인트 없음
- 서버 재시작 필요

## 🛠 해결 방법

### Option 1: 서버 재시작 (권장)
```bash
# 1. 현재 서버 종료
pkill -f "python.*49999" || kill 66607

# 2. 서버 재시작
cd /home/user/webapp && python -m uvicorn app.main:app --host 0.0.0.0 --port 49999 --reload
```

### Option 2: 백그라운드에서 재시작
```bash
# 1. 종료
pkill -f "python.*49999"

# 2. 백그라운드로 재시작
cd /home/user/webapp && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 49999 > /tmp/zerosite_backend.log 2>&1 &

# 3. 로그 확인
tail -f /tmp/zerosite_backend.log
```

### Option 3: Supervisor/PM2 사용 (프로덕션)
```bash
# Supervisor 설정 (Python)
[program:zerosite_backend]
command=python -m uvicorn app.main:app --host 0.0.0.0 --port 49999
directory=/home/user/webapp
autostart=true
autorestart=true
```

## 🧪 검증 방법

### 1. Swagger UI 확인
```
URL: http://localhost:49999/docs
확인: POST /api/projects 엔드포인트 존재
```

### 2. curl 테스트
```bash
curl -X POST http://localhost:49999/api/projects \
  -H "Content-Type: application/json" \
  -d '{"project_name":"테스트 프로젝트","land_address":"서울특별시 강남구"}'

# 성공 응답 예시:
{
  "project_id": "proj_20260112_abc123de",
  "project_name": "테스트 프로젝트",
  "land_address": "서울특별시 강남구",
  "status": "DRAFT",
  ...
}
```

### 3. Frontend 테스트
```
1. /static/projects.html 접속
2. [+ 새 프로젝트 만들기] 클릭
3. 프로젝트명/주소 입력
4. [생성] 버튼 클릭
5. ✅ 성공: project_detail.html로 이동
6. ✅ 목록에 새 프로젝트 표시
```

## 📊 완료 기준 (DoD)
- [ ] POST /api/projects → 200/201 응답
- [ ] Swagger UI에 엔드포인트 표시
- [ ] 프로젝트 생성 성공
- [ ] project_detail.html로 자동 이동
- [ ] 프로젝트 목록에 즉시 표시

## 🚨 트러블슈팅

### 문제: 서버 재시작 후에도 404
```bash
# 1. 포트 충돌 확인
lsof -i :49999

# 2. 프로세스 강제 종료
kill -9 $(lsof -t -i:49999)

# 3. 캐시 정리
rm -rf /tmp/zerosite_*

# 4. 재시작
cd /home/user/webapp && python -m uvicorn app.main:app --host 0.0.0.0 --port 49999 --reload
```

### 문제: ImportError
```bash
# 의존성 재설치
cd /home/user/webapp && pip install -r requirements.txt

# Pydantic 모델 확인
python -c "from app.models.project import Project; print('OK')"
```

### 문제: CORS 오류
```python
# app/main.py에서 CORS 설정 확인
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎯 핵심 포인트

1. **코드는 정상**: router가 올바르게 정의되고 include됨
2. **실행이 문제**: 실행 중인 서버에 최신 코드가 반영 안 됨
3. **해결책**: 서버 재시작 (`--reload` 옵션 권장)
4. **검증**: Swagger UI + curl + Frontend 테스트

## 📝 참고: 개발 환경 권장 설정

```bash
# .env 파일
DEBUG=true
RELOAD=true

# 실행 스크립트 (start_server.sh)
#!/bin/bash
cd /home/user/webapp
export DEBUG=true
python -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 49999 \
  --reload \
  --log-level info

# 실행
chmod +x start_server.sh
./start_server.sh
```

---

**🚀 결론**: 서버 재시작만 하면 즉시 해결됩니다!
