# Classic Format PDF 다운로드 포털

## 📋 개요

5종 모듈(M2, M3, M4, M5, M6)의 Classic Format PDF 보고서를 다운로드할 수 있는 포털이 구축되었습니다.

## 🔗 접속 URL

### 프론트엔드 다운로드 포털
```
https://3000-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/static/reports/
```

### 백엔드 API (직접 다운로드)
```
https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/static/reports/{filename}
```

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
각 보고서를 직접 다운로드하려면 아래 URL을 사용:

```
M2: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/static/reports/M2_Land_Appraisal_Classic.pdf
M3: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/static/reports/M3_Supply_Type_Classic.pdf
M4: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/static/reports/M4_Building_Scale_Classic.pdf
M5: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/static/reports/M5_Feasibility_Classic.pdf
M6: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/static/reports/M6_LH_Judgment_Classic.pdf
```

### 방법 3: API를 통한 통합
프론트엔드 앱에서 다운로드 버튼 구현:

```javascript
// M2 보고서 다운로드 예제
const downloadM2Report = () => {
    const link = document.createElement('a');
    link.href = '/static/reports/M2_Land_Appraisal_Classic.pdf';
    link.download = 'M2_토지감정평가_보고서.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
```

## 📂 파일 구조

```
/home/user/webapp/
└── static/
    └── reports/
        ├── index.html                                    # 다운로드 포털 페이지
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

### 백엔드 (FastAPI)
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
- [x] 다운로드 포털 페이지 (index.html) 생성
- [x] Git에 커밋 및 원격 저장소에 푸시
- [x] 프론트엔드/백엔드 URL 확인

## 📌 중요 사항

1. **파일명 인코딩**: 한글 파일명과 영문 파일명 모두 제공하여 다양한 환경에서 호환성 보장
2. **CORS 설정**: 백엔드에서 CORS 미들웨어가 활성화되어 있어 프론트엔드에서 접근 가능
3. **캐시 정책**: static 파일은 브라우저에 캐시되므로 빠른 다운로드 가능
4. **.gitignore**: static/reports가 gitignore에 포함되었으나 `-f` 플래그로 강제 추가됨

## 🚀 배포 상태

- **프론트엔드**: https://3000-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai
- **백엔드 API**: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai
- **다운로드 포털**: https://3000-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/static/reports/

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
