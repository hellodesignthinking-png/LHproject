# Classic Templates Fix Plan (마포구 월드컵북로 120 기준)

## 목표
- 모든 M2-M6 템플릿에서 강남 하드코딩 제거
- 대상지 식별 블록 추가
- 마포구 맥락 설명 강화

## 수정 파일
1. m2_classic_appraisal_format.html
2. m3_classic_supply_type.html
3. m4_classic_capacity.html
4. m5_classic_feasibility.html
5. m6_classic_lh_review.html

## 공통 수정사항

### 1. 대상지 식별 블록 (모든 템플릿 Page 2에 추가)
```html
<!-- Site Identity Block -->
<div class="site-identity-section">
    <h2>대상지 식별 정보</h2>
    <table class="identity-table">
        <tr>
            <th>대상지 주소</th>
            <td>{{ meta.address | default(address) }}</td>
        </tr>
        <tr>
            <th>필지번호(PNU)</th>
            <td>{{ meta.parcel_id | default('PNU 확인 필요') }}</td>
        </tr>
        <tr>
            <th>분석 기준일</th>
            <td>{{ meta.eval_base_date | default(appraisal_date) }}</td>
        </tr>
        <tr>
            <th>분석 실행 ID</th>
            <td>{{ meta.run_id | default(report_id) }}</td>
        </tr>
    </table>
</div>
```

### 2. 하드코딩 제거
- ❌ 서울특별시 강남구 역삼동
- ❌ 서울시 강남구 테헤란로
- ✅ {{ meta.address }} 또는 {{ address }} 사용

## 모듈별 추가 수정

### M2 (토지감정평가)
- 거래사례 테이블에 대상지와의 거리 컬럼 추가
- 평가 결론 문장: "마포구 서북권 기준" 명시

### M3 (공급유형)
- Executive Summary에 마포구 맥락 설명 추가
- "청년형" 추천 근거 강화

### M4 (건축규모)
- B안 권장 이유 문장 강화
- 마포구 맥락 설명 추가

### M5 (사업성)
- M2-M4 연결 설명 추가
- "조건부 적정" 해석 명확화

### M6 (종합판단)
- 최종 판단 문장 완전 재작성
- 강남 표현 완전 제거
- M2-M5 연결 스토리 강화
