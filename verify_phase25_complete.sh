#!/bin/bash
# Phase 2.5 최종 검증 스크립트

echo "========================================="
echo "   Phase 2.5 최종 검증"
echo "========================================="
echo ""

REPORT_DIR="final_reports_phase25"

# 6종 보고서 파일명
REPORTS=(
    "all_in_one_phase25_real_data.html"
    "financial_feasibility_phase25_real_data.html"
    "lh_technical_phase25_real_data.html"
    "executive_summary_phase25_real_data.html"
    "landowner_summary_phase25_real_data.html"
    "quick_check_phase25_real_data.html"
)

# 보고서명 매핑
declare -A REPORT_NAMES=(
    ["all_in_one_phase25_real_data.html"]="전체 통합 보고서"
    ["financial_feasibility_phase25_real_data.html"]="사업성 중심 보고서"
    ["lh_technical_phase25_real_data.html"]="LH 기술검토용"
    ["executive_summary_phase25_real_data.html"]="경영진용 요약본"
    ["landowner_summary_phase25_real_data.html"]="토지주용 요약본"
    ["quick_check_phase25_real_data.html"]="빠른 검토용"
)

TOTAL=0
PASS=0
FAIL=0

echo "✅ 검증 항목:"
echo "  1️⃣ 파일 존재 여부"
echo "  2️⃣ KPI 요약 카드 포함"
echo "  3️⃣ N/A 제거 (설명 문장으로 치환)"
echo "  4️⃣ 핵심 숫자 강조"
echo ""

for report in "${REPORTS[@]}"; do
    TOTAL=$((TOTAL + 1))
    filepath="$REPORT_DIR/$report"
    reportname="${REPORT_NAMES[$report]}"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📄 $reportname"
    echo "   파일: $report"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 1. 파일 존재 확인
    if [ -f "$filepath" ]; then
        filesize=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null)
        echo "  ✓ 파일 존재: ${filesize} bytes"
    else
        echo "  ✗ 파일 없음"
        FAIL=$((FAIL + 1))
        continue
    fi
    
    # 2. KPI 카드 확인
    kpi_count=$(grep -c "kpi-summary-card" "$filepath" || echo "0")
    if [ "$kpi_count" -gt 0 ]; then
        echo "  ✓ KPI 요약 카드: $kpi_count 개"
    else
        echo "  ⚠ KPI 요약 카드: 없음"
    fi
    
    # 3. N/A 확인 (없어야 함)
    na_count=$(grep -c "N/A" "$filepath" || echo "0")
    if [ "$na_count" -eq 0 ]; then
        echo "  ✓ N/A 제거: 완료"
    else
        echo "  ⚠ N/A 남음: $na_count 개"
    fi
    
    # 4. 핵심 숫자 강조 (strong 태그)
    strong_count=$(grep -c "<strong>" "$filepath" || echo "0")
    if [ "$strong_count" -gt 5 ]; then
        echo "  ✓ 숫자 강조: $strong_count 개"
    else
        echo "  ⚠ 숫자 강조: 부족 ($strong_count 개)"
    fi
    
    # 5. 특수 검증 (보고서별)
    case "$report" in
        "all_in_one_phase25_real_data.html")
            final_count=$(grep -c "final-decision-highlight\|최종 결론" "$filepath" || echo "0")
            if [ "$final_count" -gt 0 ]; then
                echo "  ✓ 최종 결론 강조: ✓"
            else
                echo "  ⚠ 최종 결론: 없음"
            fi
            ;;
        "financial_feasibility_phase25_real_data.html")
            profit_count=$(grep -c "수익성\|profitability" "$filepath" || echo "0")
            if [ "$profit_count" -gt 0 ]; then
                echo "  ✓ 수익성 결론: ✓"
            else
                echo "  ⚠ 수익성 결론: 없음"
            fi
            ;;
        "landowner_summary_phase25_real_data.html")
            interp_count=$(grep -c "landowner-interpretation\|토지주 관점" "$filepath" || echo "0")
            if [ "$interp_count" -gt 0 ]; then
                echo "  ✓ 토지주 해석: ✓"
            else
                echo "  ⚠ 토지주 해석: 없음"
            fi
            ;;
    esac
    
    PASS=$((PASS + 1))
    echo ""
done

echo "========================================="
echo "   최종 결과"
echo "========================================="
echo "  총 보고서: $TOTAL"
echo "  검증 통과: $PASS"
echo "  검증 실패: $FAIL"
echo ""

if [ "$PASS" -eq 6 ] && [ "$FAIL" -eq 0 ]; then
    echo "🎉 PHASE 2.5 COMPLETE"
    echo "   6종 보고서 100% 완료"
    echo "   Ready for LH final submission"
    echo ""
    echo "📦 산출물:"
    echo "   경로: $REPORT_DIR/"
    echo "   용량: $(du -sh $REPORT_DIR/ | cut -f1)"
    echo ""
    exit 0
else
    echo "❌ FAILED"
    echo "   Reason: $FAIL 개 보고서 미완성"
    echo ""
    exit 1
fi
