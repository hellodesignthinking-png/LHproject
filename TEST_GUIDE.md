# 🧪 ZeroSite v3.2 - 테스트 가이드

**생성일**: 2025-12-11  
**서버 상태**: ✅ RUNNING  
**버전**: v23.0.0 + v3.2.0

---

## 🌐 **서버 주소**

### **공개 URL** (외부 접속용)
```
https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai
```

⚠️ **참고**: 샌드박스 환경 특성상 외부 접속이 제한될 수 있습니다.

### **로컬 URL** (내부 테스트용)
```
http://localhost:8041
```

---

## 📍 **주요 엔드포인트**

### 1. **Health Check** (서버 상태)
```bash
GET http://localhost:8041/health
```

**응답 예시**:
```json
{
    "status": "healthy",
    "version": "23.0.0",
    "uptime_seconds": 20.6,
    "timestamp": "2025-12-11T01:40:23.282776",
    "total_requests": 0,
    "success_rate": "0.0%"
}
```

---

### 2. **API 문서** (Swagger UI)
```bash
# 브라우저에서 열기
http://localhost:8041/api/v23/docs
```

이 페이지에서 모든 API를 직접 테스트할 수 있습니다!

---

### 3. **v23 A/B 리포트 생성**
```bash
POST http://localhost:8041/api/v23/generate-ab-report
```

**요청 예시**:
```bash
curl -X POST http://localhost:8041/api/v23/generate-ab-report \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_area_sqm": 1650.0
  }'
```

---

### 4. **v3.2 Expert 리포트 생성** ⭐ NEW
```bash
POST http://localhost:8041/api/v3.2/generate-expert-report
```

**요청 예시**:
```bash
curl -X POST http://localhost:8041/api/v3.2/generate-expert-report \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_area_sqm": 1650.0,
    "bcr_legal": 50.0,
    "far_legal": 300.0
  }'
```

**응답 예시**:
```json
{
    "status": "success",
    "report_url": "http://localhost:8041/reports/expert_v32_bbfb3f6f_20251211_014030.html",
    "generation_time": 0.01,
    "file_size_kb": 9,
    "version": "3.2.0",
    "sections_included": [
        "Cover",
        "Section 03-1 A/B Comparison"
    ],
    "recommended_scenario": "B",
    "scenario_a_decision": "NO-GO",
    "scenario_b_decision": "NO-GO",
    "metadata": {
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area_sqm": 1650.0,
        "land_area_pyeong": 500.0,
        "market_price_per_sqm": 15000000.0,
        "market_confidence": "LOW"
    },
    "message": "Expert v3.2 report successfully generated. Recommended: Scenario B (신혼부부 주택)"
}
```

---

## 🧪 **테스트 시나리오**

### **시나리오 1: 강남구 (대형 토지)**
```json
{
  "address": "서울특별시 강남구 역삼동 123-45",
  "land_area_sqm": 1650.0,
  "bcr_legal": 50.0,
  "far_legal": 300.0
}
```

**예상 결과**:
- Market Price: ~15,000,000 ₩/㎡ (HIGH)
- Scenario A (Youth): 75 units
- Scenario B (Newlywed): 50 units
- Recommended: 정책 점수 기반

---

### **시나리오 2: 마포구 (중형 토지)**
```json
{
  "address": "서울특별시 마포구 월드컵북로 120",
  "land_area_sqm": 660.0,
  "bcr_legal": 50.0,
  "far_legal": 300.0
}
```

**예상 결과**:
- Market Price: ~9,500,000 ₩/㎡ (MEDIUM)
- Scenario A (Youth): 30 units
- Scenario B (Newlywed): 20 units
- Recommended: Scenario B

---

### **시나리오 3: 노원구 (소형 토지)**
```json
{
  "address": "서울특별시 노원구 상계동 789-12",
  "land_area_sqm": 2000.0,
  "bcr_legal": 50.0,
  "far_legal": 300.0
}
```

**예상 결과**:
- Market Price: ~6,800,000 ₩/㎡ (MEDIUM)
- Scenario A (Youth): 90 units
- Scenario B (Newlywed): 60 units
- Recommended: 재무 분석 기반

---

## 🔧 **테스트 도구**

### **1. curl 명령어** (터미널)
```bash
# Health Check
curl http://localhost:8041/health

# v3.2 Report
curl -X POST http://localhost:8041/api/v3.2/generate-expert-report \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 강남구 역삼동 123-45", "land_area_sqm": 1650.0, "bcr_legal": 50.0, "far_legal": 300.0}'
```

---

### **2. Python 스크립트**
```python
import requests
import json

# API endpoint
url = "http://localhost:8041/api/v3.2/generate-expert-report"

# Request data
data = {
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_area_sqm": 1650.0,
    "bcr_legal": 50.0,
    "far_legal": 300.0
}

# Send request
response = requests.post(url, json=data)

# Print result
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

---

### **3. Postman / Insomnia**
1. URL: `http://localhost:8041/api/v3.2/generate-expert-report`
2. Method: `POST`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "address": "서울특별시 강남구 역삼동 123-45",
  "land_area_sqm": 1650.0,
  "bcr_legal": 50.0,
  "far_legal": 300.0
}
```

---

### **4. Swagger UI** (추천!)
```
http://localhost:8041/api/v23/docs
```

브라우저에서 위 주소를 열고:
1. `/api/v3.2/generate-expert-report` 찾기
2. "Try it out" 클릭
3. 파라미터 입력
4. "Execute" 클릭
5. 응답 확인

---

## 📊 **생성된 리포트 확인**

### **리포트 목록 보기**
```bash
GET http://localhost:8041/api/v23/reports/list
```

### **리포트 다운로드**
```bash
# API 응답에서 받은 report_url 사용
curl http://localhost:8041/reports/expert_v32_XXXXX.html > report.html

# 또는 브라우저에서 직접 열기
http://localhost:8041/reports/expert_v32_XXXXX.html
```

### **로컬 파일 확인**
```bash
ls -lh /home/user/webapp/public/reports/
```

---

## 🎯 **빠른 테스트 스크립트**

완전 자동 테스트:

```bash
#!/bin/bash
# quick_test.sh

echo "🧪 ZeroSite v3.2 Quick Test"
echo "================================"

# 1. Health Check
echo "1. Health Check..."
curl -s http://localhost:8041/health | python3 -m json.tool

# 2. Generate Report (강남)
echo ""
echo "2. Generating Gangnam Report..."
RESPONSE=$(curl -s -X POST http://localhost:8041/api/v3.2/generate-expert-report \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 강남구 역삼동 123-45", "land_area_sqm": 1650.0, "bcr_legal": 50.0, "far_legal": 300.0}')

echo "$RESPONSE" | python3 -m json.tool

# 3. Extract report URL
REPORT_URL=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['report_url'])")

echo ""
echo "✅ Report generated: $REPORT_URL"

# 4. Download report
echo ""
echo "3. Downloading report..."
curl -s "$REPORT_URL" > test_report.html
SIZE=$(stat -c%s test_report.html 2>/dev/null || stat -f%z test_report.html 2>/dev/null)

echo "✅ Downloaded: test_report.html ($SIZE bytes)"
```

사용법:
```bash
chmod +x quick_test.sh
./quick_test.sh
```

---

## 🐛 **문제 해결**

### **서버가 응답하지 않음**
```bash
# 서버 프로세스 확인
ps aux | grep v23_server.py

# 서버 재시작
cd /home/user/webapp
python3 v23_server.py
```

### **"port is not open" 오류**
샌드박스 외부에서는 접속이 제한될 수 있습니다.
→ 로컬 테스트 (localhost:8041) 사용 권장

### **API 호출 실패**
```bash
# 서버 로그 확인
tail -f /home/user/webapp/logs/zerosite_v23_production.log
```

---

## 📝 **테스트 체크리스트**

- [ ] Health check 응답 확인
- [ ] API 문서 (Swagger UI) 접속
- [ ] v23 A/B 리포트 생성 테스트
- [ ] v3.2 Expert 리포트 생성 테스트
- [ ] 3개 시나리오 (강남, 마포, 노원) 테스트
- [ ] 생성된 리포트 HTML 확인
- [ ] 리포트 다운로드 테스트

---

## 🎉 **성공 기준**

✅ Health check가 "healthy" 반환  
✅ API가 200 OK 응답  
✅ 리포트 URL 생성됨  
✅ HTML 파일 다운로드 가능  
✅ 리포트에 Section 03-1 포함  
✅ A/B 비교 데이터 표시됨  
✅ 권장 시나리오 표시됨  

---

## 📞 **지원**

문제가 있으시면:
1. 서버 로그 확인
2. 검증 스크립트 실행 (`./VERIFY_V32_SYSTEM.sh`)
3. 테스트 결과 공유

---

**Server**: http://localhost:8041  
**API Docs**: http://localhost:8041/api/v23/docs  
**Status**: ✅ RUNNING  
**Version**: v23.0.0 + v3.2.0
