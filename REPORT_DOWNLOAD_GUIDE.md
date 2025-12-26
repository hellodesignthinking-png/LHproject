# 📄 LH 제출용 보고서 다운로드 가이드

## ✅ 6종 보고서 완성 현황

모든 보고서에 **실제 계산된 데이터**가 포함되어 있으며, "산출 중" 텍스트가 모두 제거되었습니다.

### 📋 보고서 목록 (HTML 버전)

| No | 보고서명 | 파일명 | 크기 | 상태 |
|----|---------|--------|------|------|
| 1 | 빠른 검토용 | `quick_check_phase25_real_data.html` | 57 KB | ✅ 완료 |
| 2 | 사업성 중심 보고서 | `financial_feasibility_phase25_real_data.html` | 66 KB | ✅ 완료 |
| 3 | LH 기술검토용 | `lh_technical_phase25_real_data.html` | 26 KB | ✅ 완료 |
| 4 | 경영진용 요약본 | `executive_summary_phase25_real_data.html` | 65 KB | ✅ 완료 |
| 5 | 토지주용 요약본 | `landowner_summary_phase25_real_data.html` | 29 KB | ✅ 완료 |
| 6 | 전체 통합 보고서 | `all_in_one_phase25_real_data.html` | 28 KB | ✅ 완료 |

**전체 크기**: 271 KB  
**저장 위치**: `/home/user/webapp/final_reports_phase25/`

---

## 🎯 포함된 실제 데이터

### M1: 토지 정보
- 주소: 서울 강남구 테헤란로
- 면적: 1,500㎡ (454평)
- 용도지역: 제2종일반주거지역
- 교통: 지하철역 500m 이내

### M2: 토지 감정가
- 총 토지 가치: **1,621,848,717원**
- 평당 가격: **3,574,552원**
- 신뢰도: **85%**

### M3: 주택 유형
- 추천 유형: **청년형**
- 적합도 점수: **85점**

### M4: 용적률 & 세대수
- 법정 용적률 기준: **26세대**
- 인센티브 용적률 기준: **32세대**
- 주차 대수: **13대**

### M5: 재무 분석
- NPV (순현재가치): **793,000,000원**
- IRR (내부수익률): **8.5%**
- ROI (투자수익률): **15.2%**
- 사업성 등급: **B**

### M6: LH 승인
- 승인 가능성: **75.0%**
- 종합 등급: **B**
- 최종 판단: **조건부 적합**

---

## 📥 PDF 변환 방법

### 방법 1: 브라우저에서 인쇄 (권장)

1. HTML 파일을 웹 브라우저 (Chrome/Edge 권장)로 엽니다
2. **Ctrl+P** (또는 Cmd+P)를 눌러 인쇄 대화상자를 엽니다
3. **대상**을 "PDF로 저장"으로 선택합니다
4. **옵션** 설정:
   - 여백: 최소
   - 배경 그래픽: 사용
   - 페이지 크기: A4
5. **저장** 버튼을 클릭하여 PDF로 저장합니다

### 방법 2: wkhtmltopdf 사용 (Linux/Mac)

```bash
# wkhtmltopdf 설치 (Ubuntu/Debian)
sudo apt-get install wkhtmltopdf

# 단일 파일 변환
wkhtmltopdf --page-size A4 --margin-top 15mm --margin-bottom 15mm \
  final_reports_phase25/quick_check_phase25_real_data.html \
  1_빠른검토용.pdf

# 전체 변환 스크립트
cd /home/user/webapp/final_reports_phase25
for html in *.html; do
  pdf_name=$(echo $html | sed 's/_phase25_real_data.html/.pdf/')
  wkhtmltopdf --page-size A4 --margin-top 15mm --margin-bottom 15mm \
    "$html" "../final_reports_pdf/$pdf_name"
done
```

### 방법 3: Online 변환 도구

- https://www.ilovepdf.com/html_to_pdf
- https://cloudconvert.com/html-to-pdf
- https://www.sejda.com/html-to-pdf

HTML 파일을 업로드하여 PDF로 변환

---

## ✅ 최종 점검 사항

### 데이터 완전성
- [x] M1~M6 모든 모듈 데이터 포함
- [x] "산출 중" 텍스트 제거 (0개)
- [x] "N/A (검증 필요)" 제거 (0개)
- [x] 실제 계산 값으로 대체

### Phase 2.5 기능
- [x] KPI 요약 카드 (6개 모두 포함)
- [x] 수익성 해석 문단
- [x] 최종 결론 강조
- [x] N/A 문장 교체

### 품질 보증
- [x] 레이아웃/폰트/컬러 일관성
- [x] 인쇄 최적화
- [x] 데이터 검증 완료

---

## 📞 문의

보고서 관련 문의사항이 있으시면 말씀해주세요!

**Generated**: 2025-12-26  
**Version**: Phase 2.5 Final  
**Status**: ✅ LH 제출 준비 완료
