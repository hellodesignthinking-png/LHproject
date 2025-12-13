# 📖 ZeroSite v24.1 감정평가 PDF 다운로드 사용 가이드

## 🎯 빠른 시작

### 웹 브라우저에서 사용 (권장)

1. **Dashboard 접속**
   ```
   https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/public/dashboard.html?tab=appraisal
   ```

2. **감정평가 정보 입력**
   - **주소**: 예) 서울시 마포구 공덕동 123-4
   - **대지면적**: 예) 1500 ㎡
   - **건축면적**: 예) 3600 ㎡ (선택사항)
   - **건축년도**: 예) 2020 (선택사항)
   - **용도지역**: 예) 제3종일반주거지역
   - **개별공시지가**: 예) 8500000 원/㎡ (선택사항)

3. **"감정평가 실행" 버튼 클릭**

4. **결과 확인**
   - 최종 감정평가액 (억원)
   - 3가지 평가방식 결과
     - 원가법 (Cost Approach)
     - 거래사례비교법 (Sales Comparison)
     - 수익환원법 (Income Approach)
   - 각 방식의 가중치
   - 신뢰도 수준

5. **"상세 감정평가 보고서 PDF 다운로드" 버튼 클릭**
   - PDF 자동 다운로드 시작
   - 파일명: `감정평가보고서_YYYYMMDD_HHMMSS.pdf`

---

## 📄 PDF 보고서 구성 (4페이지)

### 📋 1페이지: 종합 개요
- ✅ 평가 기본 정보 (평가일, 대상지, 면적, 신뢰도)
- ✅ 최종 감정평가액 (큰 숫자로 강조)
- ✅ 3방식 종합 비교표
  - 원가법 평가액 + 가중치
  - 거래사례비교법 평가액 + 가중치
  - 수익환원법 평가액 + 가중치
- ✅ 최종 평가액 계산식

### 🔵 2페이지: 원가법 상세
- ✅ 계산 원리 설명
- ✅ 단계별 계산 과정
  1. 토지가액 = 면적 × 개별공시지가
  2. 재조달원가 = 건축면적 × LH 표준단가 × 위치보정
  3. 경과연수 (내용연수 40년 기준)
  4. 감가율 = 경과연수 × 2% (최대 50%)
  5. 감가차감액 = 건물가액 × 감가율
  6. 건물 순가액 = 재조달원가 - 감가차감액
  7. 최종 원가법 평가액 = 토지가액 + 건물 순가액
- ✅ 상세 금액 표

### 🟢 3페이지: 거래사례비교법 상세
- ✅ 계산 원리 설명
- ✅ 거래사례 보정표
  | 사례 | 거래단가 | 시점보정 | 위치보정 | 개별보정 | 보정후단가 | 가중치 |
  |------|---------|---------|---------|---------|----------|-------|
  | 사례1 | 10,000,000 | 1.00 | 0.95 | 1.00 | 9,500,000 | 30% |
  | 사례2 | 11,000,000 | 1.05 | 1.00 | 1.00 | 11,550,000 | 40% |
  | 사례3 | 10,500,000 | 1.00 | 1.00 | 0.98 | 10,290,000 | 30% |
- ✅ 가중평균 단가 계산
- ✅ 최종 평가액 = 가중평균 단가 × 토지면적

### 🟣 4페이지: 수익환원법 상세
- ✅ 계산 원리 설명
- ✅ NOI 계산 과정
  1. 연간 총임대수익
  2. 공실손실 (-5%)
  3. 유효총수익
  4. 운영경비 (-15%)
  5. 순영업소득(NOI)
- ✅ 환원율 (4.5% - 주거용 기준)
- ✅ 최종 평가액 = NOI ÷ 환원율
- ✅ 특기사항 및 참고사항

---

## 🔧 API 직접 사용 (개발자용)

### cURL 예제
```bash
curl -X POST "https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/appraisal/pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울시 강남구 역삼동 100-1",
    "land_area_sqm": 2000,
    "building_area_sqm": 5000,
    "construction_year": 2018,
    "zone_type": "상업지역",
    "individual_land_price_per_sqm": 12000000,
    "annual_rental_income": 300000000
  }' \
  --output appraisal_report.pdf
```

### Python 예제
```python
import requests

url = "https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/appraisal/pdf"
data = {
    "address": "서울시 강남구 역삼동 100-1",
    "land_area_sqm": 2000,
    "building_area_sqm": 5000,
    "construction_year": 2018,
    "zone_type": "상업지역",
    "individual_land_price_per_sqm": 12000000,
    "annual_rental_income": 300000000
}

response = requests.post(url, json=data)

if response.status_code == 200:
    with open("appraisal_report.pdf", "wb") as f:
        f.write(response.content)
    print("PDF 다운로드 완료!")
else:
    print(f"Error: {response.status_code}")
```

### JavaScript 예제
```javascript
async function downloadAppraisalPDF() {
    const data = {
        address: "서울시 강남구 역삼동 100-1",
        land_area_sqm: 2000,
        building_area_sqm: 5000,
        construction_year: 2018,
        zone_type: "상업지역",
        individual_land_price_per_sqm: 12000000,
        annual_rental_income: 300000000
    };
    
    const response = await fetch('/api/v24.1/appraisal/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'appraisal_report.pdf';
    a.click();
}
```

---

## 📊 테스트 시나리오

### 시나리오 1: 신축 아파트 (서울)
```json
{
  "address": "서울시 마포구 공덕동 123-4",
  "land_area_sqm": 1500,
  "building_area_sqm": 3600,
  "construction_year": 2020,
  "zone_type": "제3종일반주거지역",
  "individual_land_price_per_sqm": 8500000
}
```
**예상 결과**: 
- 원가법: ~258억원
- 거래사례비교법: ~191억원
- 수익환원법: ~104억원
- 최종: ~222억원

### 시나리오 2: 구축 건물 (서울 외곽)
```json
{
  "address": "경기도 고양시 일산동구 장항동 100",
  "land_area_sqm": 2000,
  "building_area_sqm": 4000,
  "construction_year": 2005,
  "zone_type": "제2종일반주거지역",
  "individual_land_price_per_sqm": 5000000
}
```
**예상 결과**:
- 감가율 높음 (경과연수 20년)
- 위치보정계수 낮음 (1.05x)
- 최종 평가액 중간 수준

### 시나리오 3: 상업용 건물 (강남)
```json
{
  "address": "서울시 강남구 역삼동 100-1",
  "land_area_sqm": 2000,
  "building_area_sqm": 5000,
  "construction_year": 2018,
  "zone_type": "상업지역",
  "individual_land_price_per_sqm": 12000000,
  "annual_rental_income": 300000000
}
```
**예상 결과**:
- 개별공시지가 높음 (1,200만원/㎡)
- 수익환원법 가중치 높음
- 최종 평가액 높음

---

## ❓ FAQ

### Q1: PDF 다운로드가 안 돼요
**A**: 다음을 확인하세요:
1. 먼저 "감정평가 실행" 버튼을 클릭하여 평가 완료
2. 브라우저 팝업 차단 해제
3. 다운로드 폴더 권한 확인

### Q2: PDF에 계산 과정이 안 보여요
**A**: PDF는 4페이지로 구성되어 있으며, 2-4페이지에 각 방식의 상세 계산이 있습니다. PDF 뷰어에서 모든 페이지를 확인하세요.

### Q3: 거래사례비교법 값이 이상해요
**A**: 
- 거래사례가 없는 경우: 개별공시지가 × 130% (시세반영률) 사용
- 보정률과 가중치가 별도로 적용됨 (이중 적용 없음)
- 위치보정계수 확인 (서울 1.15x, 수도권 1.05x, 기타 1.0x)

### Q4: 건축면적을 안 넣었는데도 원가법 값이 나와요
**A**: 건축면적이 없는 경우 토지만 평가합니다 (건물가액 0원).

### Q5: PDF 파일명을 변경하고 싶어요
**A**: 다운로드 후 파일명을 수동으로 변경하거나, API 호출 시 response에서 Content-Disposition 헤더를 수정하세요.

---

## 🔗 관련 링크

- **Live System**: https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/
- **Dashboard**: https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/public/dashboard.html?tab=appraisal
- **API Docs**: https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/docs
- **GitHub**: https://github.com/hellodesignthinking-png/LHproject

---

## 📞 지원

문제가 발생하면 다음 정보를 포함하여 문의하세요:
- 입력한 데이터 (JSON)
- 브라우저 콘솔 에러 메시지
- PDF 파일 크기 (0 bytes인지 확인)
- 서버 로그 (개발자용)

---

**작성일**: 2025-12-13  
**버전**: v24.1.0  
**문서 버전**: 1.0
