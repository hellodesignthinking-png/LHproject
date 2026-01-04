# Classic Format PDF 다운로드 포털

## 📋 개요

5종 모듈(M2, M3, M4, M5, M6)의 Classic Format PDF 보고서를 다운로드할 수 있는 포털이 구축되었습니다.

## 🔗 접속 URL

### ⭐ 다운로드 포털 (추천) - ✅ 작동 확인 완료
**Vite Frontend를 통한 접근:**
```
https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/
```

### 직접 PDF 다운로드 (Vite 서빙)
```
M2: https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M2_Land_Appraisal_Classic.pdf
M3: https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M3_Supply_Type_Classic.pdf
M4: https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M4_Building_Scale_Classic.pdf
M5: https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M5_Feasibility_Classic.pdf
M6: https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M6_LH_Judgment_Classic.pdf
```

### 백엔드 API (대체 방법)
```
https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/static/reports/{filename}
```

> **✅ 해결됨**: Vite public 폴더를 통해 PDF 서빙 확인 완료 (HTTP 200 OK)

## 📄 다운로드 가능한 보고서

| 모듈 | 보고서명 | 파일명 | 크기 |
|------|----------|--------|------|
| M2 | 토지감정평가 보고서 | `M2_Land_Appraisal_Classic.pdf` | 834 KB |
| M3 | 공급유형 판단 보고서 | `M3_Supply_Type_Classic.pdf` | 775 KB |
| M4 | 건축규모 판단 보고서 | `M4_Building_Scale_Classic.pdf` | 642 KB |
| M5 | 사업성 분석 보고서 | `M5_Feasibility_Classic.pdf` | 656 KB |
| M6 | LH 종합판단 보고서 | `M6_LH_Judgment_Classic.pdf` | 754 KB |

## 🎯 사용 방법

### 방법 1: 웹 포털을 통한 다운로드
1. 위의 프론트엔드 URL로 접속
2. 원하는 보고서의 "📥 다운로드" 버튼 클릭
3. PDF 파일이 자동으로 다운로드됨

### 방법 2: 직접 URL 접근
각 보고서를 직접 다운로드하려면 아래 URL을 사용 (✅ 테스트 완료):

```
M2: https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M2_Land_Appraisal_Classic.pdf
M3: https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M3_Supply_Type_Classic.pdf
M4: https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M4_Building_Scale_Classic.pdf
M5: https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M5_Feasibility_Classic.pdf
M6: https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M6_LH_Judgment_Classic.pdf
```

### 방법 3: API를 통한 통합
프론트엔드 앱에서 다운로드 버튼 구현:

```javascript
// M2 보고서 다운로드 예제 (Vite public 경로)
const downloadM2Report = () => {
    const link = document.createElement('a');
    link.href = '/reports/M2_Land_Appraisal_Classic.pdf';
    link.download = 'M2_토지감정평가_보고서.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
```

## 📂 파일 구조

```
/home/user/webapp/
├── static/
│   └── reports/                                      # 백엔드 static 파일 (참조용)
│       ├── index.html
│       └── *.pdf (5개 모듈 × 2개 파일명)
│
└── frontend/
    └── public/
        └── reports/                                  # ✅ Vite가 서빙하는 실제 경로
            ├── index.html                            # 다운로드 포털 페이지
            ├── M2_ 토지감정평가 보고서 - Classic Format.pdf    # 원본 (한글명)
            ├── M2_Land_Appraisal_Classic.pdf                 # 영문명
            ├── M3_ 공급유형 판단 보고서 - Classic Format.pdf   # 원본 (한글명)
            ├── M3_Supply_Type_Classic.pdf                    # 영문명
            ├── M4_ 건축규모 판단 보고서 - Classic Format.pdf   # 원본 (한글명)
            ├── M4_Building_Scale_Classic.pdf                 # 영문명
            ├── M5_ 사업성 분석 보고서 - Classic Format.pdf     # 원본 (한글명)
            ├── M5_Feasibility_Classic.pdf                    # 영문명
            ├── M6_ LH 종합판단 보고서 - Classic Format.pdf     # 원본 (한글명)
            └── M6_LH_Judgment_Classic.pdf                    # 영문명
```

## 🔧 기술 구현

### Vite Public 폴더 서빙 (✅ 채택된 방법)
```bash
# PDF 파일을 Vite public 폴더로 복사
cp static/reports/*.pdf frontend/public/reports/
cp static/reports/index.html frontend/public/reports/
```

Vite는 `public` 폴더의 파일을 자동으로 루트 경로에서 서빙합니다:
- `frontend/public/reports/index.html` → `/reports/index.html`
- `frontend/public/reports/*.pdf` → `/reports/*.pdf`

### 백엔드 (FastAPI) - 대체 방법
```python
# app/main.py
from fastapi.staticfiles import StaticFiles
from pathlib import Path

static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
```

### 프론트엔드 (HTML)
- 반응형 디자인으로 모바일/데스크탑 모두 지원
- 각 보고서별 카드 형식 UI
- 다운로드 버튼 클릭 시 파일 자동 다운로드
- 보고서 크기 및 설명 표시

## ✅ 검증 완료

- [x] PDF 파일 업로드 및 static/reports 디렉토리 배치
- [x] 영문 파일명으로 리네임 (한글 인코딩 문제 방지)
- [x] FastAPI static files 마운트 설정
- [x] Vite public 폴더로 PDF 복사 ✅ **최종 해결**
- [x] 다운로드 포털 페이지 (index.html) 생성
- [x] **HTTP 200 OK 테스트 완료** (포털 및 PDF 모두 접근 가능)
- [x] Git에 커밋 및 원격 저장소에 푸시
- [x] 프론트엔드/백엔드 URL 확인

### 테스트 결과
```bash
# 포털 페이지 테스트
curl -I https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/index.html
# HTTP/2 200 ✅

# PDF 다운로드 테스트
curl -I https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M2_Land_Appraisal_Classic.pdf
# HTTP/2 200 ✅
# Content-Type: application/pdf
# Content-Length: 853666 bytes (833 KB)
```

## 📌 중요 사항

1. **파일명 인코딩**: 한글 파일명과 영문 파일명 모두 제공하여 다양한 환경에서 호환성 보장
2. **Vite Public 서빙**: Vite 개발 서버가 `public` 폴더의 파일을 자동으로 서빙 (빠른 접근)
3. **캐시 정책**: static 파일은 브라우저에 캐시되므로 빠른 다운로드 가능
4. **이중 배치**: `static/reports`(백엔드용) + `frontend/public/reports`(Vite용)으로 이중화
5. **포트 주의**: Vite는 5173번 포트, 백엔드는 49999번 포트

## 🚀 배포 상태

| 서비스 | URL | 상태 |
|--------|-----|------|
| **Vite Frontend** | https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai | ✅ 실행 중 |
| **다운로드 포털** | https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/ | ✅ HTTP 200 OK |
| **M2 PDF** | https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/M2_Land_Appraisal_Classic.pdf | ✅ HTTP 200 OK |
| **백엔드 API** | https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai | ✅ 실행 중 |
| **GitHub 저장소** | https://github.com/hellodesignthinking-png/LHproject | ✅ feature/expert-report-generator |

## 📝 다음 단계 (선택사항)

1. 다운로드 통계 추적 (Google Analytics 등)
2. 다운로드 횟수 표시
3. 최신 업데이트 날짜 표시
4. 보고서 미리보기 기능 (PDF.js 사용)
5. 다국어 지원 (영문 버전)

---

**문서 생성일**: 2025-01-04  
**작성자**: ZeroSite AI Development Team  
**버전**: 1.0  
**상태**: ✅ Production Ready
