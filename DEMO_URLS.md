# 🌐 M2-M6 데모 URL

**RUN_ID**: `RUN_116801010001230045_1767151892364`  
**대상지**: 서울특별시 마포구 월드컵북로 120  
**PNU**: 116801010001230045  
**생성일**: 2025-12-31

---

## 📊 HTML 보고서

### M2: 토지감정평가 보고서
```
https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/M2/html?context_id=RUN_116801010001230045_1767151892364
```

### M3: 공급유형 판단 보고서
```
https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/M3/html?context_id=RUN_116801010001230045_1767151892364
```

### M4: 건축규모 판단 보고서
```
https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/M4/html?context_id=RUN_116801010001230045_1767151892364
```

### M5: 사업성 분석 보고서
```
https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/M5/html?context_id=RUN_116801010001230045_1767151892364
```

### M6: LH 종합판단 보고서
```
https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/M6/html?context_id=RUN_116801010001230045_1767151892364
```

---

## 📄 PDF 보고서

### M2: 토지감정평가 보고서 (PDF)
```
https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/M2/pdf?context_id=RUN_116801010001230045_1767151892364
```

### M3: 공급유형 판단 보고서 (PDF)
```
https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/M3/pdf?context_id=RUN_116801010001230045_1767151892364
```

### M4: 건축규모 판단 보고서 (PDF)
```
https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/M4/pdf?context_id=RUN_116801010001230045_1767151892364
```

### M5: 사업성 분석 보고서 (PDF)
```
https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/M5/pdf?context_id=RUN_116801010001230045_1767151892364
```

### M6: LH 종합판단 보고서 (PDF)
```
https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/M6/pdf?context_id=RUN_116801010001230045_1767151892364
```

---

## ✅ 검증 포인트

각 보고서에서 확인해야 할 사항:

### 1. 주소 일치
- [ ] "서울특별시 마포구 월드컵북로 120" 표기 확인
- [ ] PNU "116801010001230045" 표기 확인
- [ ] "주소 확인 필요" 문구 없음

### 2. 강남 제거
- [ ] "강남구" 언급 없음
- [ ] "테헤란로" 언급 없음
- [ ] "역삼동" 언급 없음

### 3. 맥락 반영
- [ ] M3: 마포구 생활권 설명 (홍대/연남/합정)
- [ ] M4: LH 매입임대 운영 기준 명시
- [ ] M5: 공공 매입임대 톤 확인
- [ ] M6: 조건부 검토 명시

### 4. 레이아웃
- [ ] 페이지 번호 정상 (Page X of Y)
- [ ] 표 깨짐 없음
- [ ] Classic 스타일 유지

---

## 🔧 테스트 명령어

### 주소 확인
```bash
# M2 주소 확인
curl -s "https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/M2/html?context_id=RUN_116801010001230045_1767151892364" | grep -A 2 "평가 대상"

# M3-M6 주소 확인
for m in M3 M4 M5 M6; do
  echo "=== $m ===" 
  curl -s "https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/$m/html?context_id=RUN_116801010001230045_1767151892364" | grep "월드컵북로" | head -1
done
```

### 강남 제거 확인
```bash
# 모든 모듈에서 강남 키워드 검색
for m in M2 M3 M4 M5 M6; do
  echo "=== $m ===" 
  curl -s "https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/module/$m/html?context_id=RUN_116801010001230045_1767151892364" | grep -i "강남\|테헤란\|역삼" || echo "✅ No Gangnam references"
done
```

---

## 📞 지원

문제 발생 시:
1. Backend 로그 확인: `tail -100 /home/user/webapp/backend.log`
2. 파이프라인 재실행: `POST /api/v4/pipeline/analyze`
3. 캐시 클리어: `use_cache=false` 파라미터 사용

---

**생성일**: 2025-12-31  
**유효기간**: Sandbox 활성 기간 동안  
**상태**: ✅ Active
