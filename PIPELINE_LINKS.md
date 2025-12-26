# 🌐 Pipeline & API 링크 (최종 업데이트)

## ✅ Pipeline Frontend

**🎯 메인 페이지**:
```
https://3001-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/pipeline
```

**홈페이지**:
```
https://3001-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/
```

---

## 📊 API 보고서 링크 (포트 8005)

### Base URL
```
https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai
```

### 1. 전체 통합 보고서 (All-in-One) ⭐
```
https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/v4/reports/final/all_in_one/html?context_id=116801010001230045
```

### 2. 빠른 검토용 (Quick Check)
```
https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/v4/reports/final/quick_check/html?context_id=116801010001230045
```

### 3. 사업성 중심 보고서 (Financial Feasibility)
```
https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/v4/reports/final/financial_feasibility/html?context_id=116801010001230045
```

### 4. LH 기술검토용 (LH Technical)
```
https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/v4/reports/final/lh_technical/html?context_id=116801010001230045
```

### 5. 경영진용 요약본 (Executive Summary)
```
https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/v4/reports/final/executive_summary/html?context_id=116801010001230045
```

### 6. 토지주용 요약본 (Landowner Summary)
```
https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/v4/reports/final/landowner_summary/html?context_id=116801010001230045
```

---

## 🔍 서비스 상태

| 서비스 | 포트 | 상태 | 공개 URL |
|--------|------|------|----------|
| Pipeline Frontend | 3001 | ✅ RUNNING | https://3001-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai |
| API Server | 8005 | ✅ RUNNING | https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai |

---

## 📥 사용 방법

### 1. Pipeline 페이지 접속
1. 위의 Pipeline Frontend 링크를 클릭
2. `/pipeline` 경로로 이동하여 전체 파이프라인 확인

### 2. API 보고서 확인
1. 원하는 보고서 링크를 클릭
2. 브라우저에서 HTML 보고서 열람
3. PDF로 저장: **Ctrl+P** (Windows) 또는 **Cmd+P** (Mac)
   - "대상"을 **"PDF로 저장"**으로 선택
   - **배경 그래픽** 체크 ✅
   - 저장 버튼 클릭

---

## 📊 포함된 데이터 (모든 보고서 공통)

- **M1**: 서울 강남구 테헤란로, 1,500㎡ (454평)
- **M2**: 토지가치 1,621,848,717원, 평당 3,574,552원
- **M3**: 청년형 주택, 적합도 85점
- **M4**: 26세대 (법정) / 32세대 (인센티브)
- **M5**: NPV 7.9억원, IRR 8.5%, ROI 15.2%
- **M6**: 승인 가능성 75%, 등급 B, 조건부 적합

---

## ⚠️ 주의사항

### Sandbox URL 변경
- Sandbox는 재시작 시 URL이 변경될 수 있습니다
- 현재 Sandbox ID: `iwm3znz7z15o7t0185x5u-b9b802c4`
- URL이 작동하지 않으면 새로운 Sandbox ID로 URL을 업데이트해야 합니다

### 서비스 재시작
Frontend 서비스를 재시작해야 하는 경우:
```bash
cd /home/user/webapp/frontend
pkill -f "npm run dev"
npm run dev > ../frontend_service.log 2>&1 &
```

API 서버를 재시작해야 하는 경우:
```bash
cd /home/user/webapp
bash restart_api_server.sh
```

---

## 🎯 빠른 테스트

### Pipeline 페이지 테스트
```bash
curl -I https://3001-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/pipeline
```

### API 테스트
```bash
curl -I https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/api/v4/reports/final/all_in_one/html?context_id=116801010001230045
```

---

**생성일**: 2025-12-26 04:54 UTC  
**Sandbox ID**: iwm3znz7z15o7t0185x5u-b9b802c4  
**Frontend Port**: 3001  
**API Port**: 8005  
**Status**: ✅ ALL SERVICES ACTIVE
