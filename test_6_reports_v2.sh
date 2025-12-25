#!/bin/bash
BASE_URL="http://localhost:8005/api/v4/final-report"
CONTEXT_ID="116801010001230045"

REPORTS=("quick_check" "financial_feasibility" "lh_technical" "executive_summary" "landowner_summary" "all_in_one")

echo "Testing 6 report types..."
echo "========================="

PASSED=0
FAILED=0

for report in "${REPORTS[@]}"; do
    echo -n "Testing $report... "
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/${report}/html?context_id=${CONTEXT_ID}")
    
    if [ "$STATUS" == "200" ]; then
        echo "✅ OK"
        ((PASSED++))
    else
        echo "❌ FAILED (HTTP $STATUS)"
        ((FAILED++))
    fi
done

echo "========================="
echo "Result: $PASSED/$((PASSED+FAILED)) passed"
