#!/bin/bash

# Phase 2.5가 적용된 보고서 다운로드
CONTEXT_ID="116801010001230045"
OUTPUT_DIR="/home/user/webapp/final_reports_phase25"

mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "📥 Phase 2.5 보고서 다운로드"
echo "Context ID: $CONTEXT_ID"
echo "=========================================="
echo ""

# 보고서 유형 배열
REPORT_TYPES=("all_in_one" "financial_feasibility" "lh_technical" "executive_summary" "landowner_summary" "quick_check")

for REPORT_TYPE in "${REPORT_TYPES[@]}"; do
    echo "📄 Downloading: $REPORT_TYPE..."
    
    # API URL (로컬 서버 가정)
    URL="http://localhost:8005/api/v4/final-report/${REPORT_TYPE}/html?context_id=${CONTEXT_ID}"
    OUTPUT_FILE="${OUTPUT_DIR}/${REPORT_TYPE}_${CONTEXT_ID}.html"
    
    # curl로 다운로드
    HTTP_CODE=$(curl -s -o "$OUTPUT_FILE" -w "%{http_code}" "$URL")
    
    if [ "$HTTP_CODE" = "200" ]; then
        SIZE=$(wc -c < "$OUTPUT_FILE")
        echo "   ✅ Success: ${SIZE} bytes"
        echo "   📁 Saved: $OUTPUT_FILE"
    else
        echo "   ❌ Failed: HTTP $HTTP_CODE"
        rm -f "$OUTPUT_FILE"
    fi
    echo ""
done

echo "=========================================="
echo "✅ 다운로드 완료"
echo "=========================================="
echo ""
ls -lh "$OUTPUT_DIR"
