# 마지막 2개 이슈 해결 결과

## 날짜: 2025-12-27
## 상태: 80% 완료 (M2-M3 완전 작동, M4-M6 데이터 스키마 불일치)

## ✅ 해결된 이슈 1: JSON 직렬화 문제
- **문제**: TypeScore, ScoreBreakdown 등 dataclass 객체가 JSON 직렬화되지 않음
- **해결**: `to_serializable()` helper 함수 추가하여 모든 nested objects를 재귀적으로 dict로 변환
- **파일**: `app/api/endpoints/pipeline_reports_v4.py` lines 492-503
- **테스트**: ✅ 성공 - assembled_data가 성공적으로 저장됨

## ✅ 해결된 이슈 2: Context Storage 저장 문제
- **문제**: Redis 저장 실패 시 인메모리로 fallback하지 않음
- **해결**: `store_frozen_context()`에서 Redis 예외 발생 시 인메모리 저장 추가
- **파일**: `app/services/context_storage.py` lines 113-118
- **테스트**: ✅ 성공 - "store_frozen_context returned: True" 확인됨

## ✅ 해결된 이슈 3: PDF 데이터 조회 문제
- **문제**: PDF 생성 시 `frozen_context['modules']` 데이터를 찾지 못함
- **해결**: `safe_get_module()` 로직을 Phase 3.5D 형식에 맞게 수정
- **파일**: `app/routers/pdf_download_standardized.py` lines 220-248
- **테스트**: ✅ M2-M3 PDF 생성 성공 (PDF document, 9 pages / 6 pages)

## ⚠️ 남은 문제: M4-M6 데이터 스키마 불일치
- **문제**: PDF 생성기가 기대하는 데이터 구조와 pipeline이 저장하는 구조가 다름
  - PDF 생성기 기대: `selected_scenario_id`, `legal_capacity.far_max`, `scenarios[]` 등
  - Pipeline 저장: `total_units`, `incentive_units`, `gross_area_sqm`, `far_used`, `bcr_used`
- **영향**: M4, M5, M6 PDF 생성 실패 (데이터 검증 오류)
- **해결 방안**:
  1. Pipeline에서 PDF 생성기가 요구하는 전체 데이터 구조를 저장하거나
  2. PDF 생성기가 simplified summary 데이터로도 작동하도록 수정
- **파일 위치**:
  - 저장: `app/api/endpoints/pipeline_reports_v4.py` lines 537-582
  - 검증: `app/services/pdf_generators/module_pdf_generator.py`

## 테스트 결과
```bash
# Pipeline 실행
curl -X POST http://localhost:8005/api/v4/pipeline/analyze \
  -H "Content-Type: application/json" \
  -d '{"parcel_id": "PDF-TEST-FINAL", "use_cache": false}'
# → Status: success ✅

# PDF 다운로드
M2: PDF document, version 1.4, 9 pages (154K) ✅
M3: PDF document, version 1.4, 6 pages (125K) ✅
M4: JSON error - missing critical data ❌
M5: JSON error - missing critical data ❌
M6: JSON error - missing critical data ❌
```

## 최종 보고서 (6종) 상태
- 아직 테스트하지 못함 (M4-M6 데이터 문제 해결 후 테스트 필요)

## 로그 레벨 문제 발견
- INFO 레벨 로그가 출력되지 않음
- CRITICAL 레벨로 변경하여 디버깅 성공
- 프로덕션 배포 전 로그 레벨 설정 확인 필요

## 다음 단계
1. M4-M6 데이터 스키마 통일 (pipeline ↔ PDF generator)
2. 최종 보고서 6종 테스트
3. HTML 엔드포인트 테스트
4. 프론트엔드 통합 테스트

## 변경 파일
- `app/api/endpoints/pipeline_reports_v4.py` - JSON 직렬화, 디버그 로그 추가
- `app/services/context_storage.py` - Redis 실패 시 인메모리 fallback
- `app/routers/pdf_download_standardized.py` - Phase 3.5D 데이터 구조 지원

## 커밋 준비 완료
- 브랜치: main
- 상태: 80% 완료, M2-M3 PDF 정상 작동
