# 4. 기술 아키텍처

## 4.1 시스템 기술 스택

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.12
- **Async Runtime**: Uvicorn + asyncio
- **Data Validation**: Pydantic v2

### Frontend
- **UI**: Vanilla JavaScript + HTML5/CSS3
- **Maps**: Leaflet.js 1.9.4
- **Charts**: Chart.js 4.0 (예정)

### APIs & Services
- **Kakao Maps API**: 주소 → 좌표 변환
- **Naver Maps API**: 주변 시설 검색
- **VWorld API**: 용도지역 조회
- **MOIS API**: 인구통계 데이터
- **Google Drive API**: LH 공고문 다운로드

### Data Storage
- **JSON**: LH 규칙 데이터
- **PDF**: LH 공고문 원본
- **Google Sheets**: 분석 결과 백업

## 4.2 코드 구조

```
/home/user/webapp/
├── app/
│   ├── main.py                      # FastAPI 애플리케이션
│   ├── config.py                    # 환경 설정
│   ├── schemas.py                   # Pydantic 모델
│   └── services/
│       ├── analysis_engine.py       # 분석 엔진
│       ├── ai_auto_corrector.py     # AI 자동 교정
│       ├── geo_optimizer.py         # 지리 최적화
│       ├── parcel_cluster.py        # 다필지 클러스터
│       ├── lh_notice_loader.py      # LH 공고문 로더
│       ├── dashboard_builder.py     # 대시보드 빌더
│       ├── kakao_service.py         # Kakao API
│       ├── land_regulation_service.py  # 법규 검토
│       ├── mois_service.py          # 인구통계 API
│       └── building_calculator.py   # 건축 규모 계산
├── static/
│   └── index.html                   # UI
├── data/
│   ├── lh_rules_auto/               # LH 규칙 JSON
│   └── lh_notices/                  # LH 공고문 PDF
└── tests/
    └── test_v5_integration.py       # 통합 테스트
```

**Watermark**: ZeroSite | ZeroSite Land Report v5.0 | Technical Architecture | Page 5
