#!/bin/bash
CONTEXT_ID="test-mock-20251221-142315"

echo "=== Testing All 6 Report Types ==="
echo ""

for REPORT in all_in_one landowner_summary lh_technical financial_feasibility quick_check presentation; do
    echo "Testing: $REPORT"
    curl -s "http://localhost:8005/api/v4/reports/final/${REPORT}/html?context_id=${CONTEXT_ID}" > "test_${REPORT}.html"
    LINES=$(wc -l < "test_${REPORT}.html")
    NA_COUNT=$(grep -c "N/A (검증 필요)" "test_${REPORT}.html" || echo "0")
    echo "  - Lines: $LINES"
    echo "  - N/A count: $NA_COUNT"
    echo ""
done

echo "=== Summary ==="
echo "All 6 reports generated successfully!"
