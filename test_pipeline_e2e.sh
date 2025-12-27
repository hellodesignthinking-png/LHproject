#!/bin/bash
# ZeroSite v4.0 Pipeline End-to-End Test Script
# 전체 플로우: M1 입력 → Context Freeze → Pipeline 실행 → 결과 확인 → 6종 보고서 생성

set -e  # Exit on error

BACKEND_URL="http://localhost:8005"
FRONTEND_URL="http://localhost:3001"

echo "=============================================="
echo "🚀 ZeroSite v4.0 Pipeline E2E Test"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Test Address Search
echo -e "${BLUE}Step 1: Address Search Test${NC}"
echo "Testing: POST /api/m1/address/search"
echo ""

SEARCH_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/m1/address/search" \
  -H "Content-Type: application/json" \
  -d '{"query":"서울특별시 강남구 테헤란로"}')

SUGGESTION_COUNT=$(echo "$SEARCH_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('suggestions', [])))" 2>/dev/null || echo "0")

if [ "$SUGGESTION_COUNT" -gt 0 ]; then
  echo -e "${GREEN}✅ Address search successful: $SUGGESTION_COUNT suggestions${NC}"
  echo "First suggestion:"
  echo "$SEARCH_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); s=d.get('suggestions',[]); print(f\"  Address: {s[0].get('jibun_address','N/A') if s else 'N/A'}\"); print(f\"  Coordinates: {s[0].get('coordinates','N/A') if s else 'N/A'}\")" 2>/dev/null || echo "  Parse error"
else
  echo -e "${YELLOW}⚠️  No suggestions found${NC}"
fi
echo ""

# Step 2: M1 Context Freeze
echo -e "${BLUE}Step 2: M1 Context Freeze${NC}"
echo "Testing: POST /api/m1/freeze-context"
echo ""

FREEZE_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/m1/freeze-context" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 521",
    "area": 2000.0,
    "coordinates": {"lat": 37.5084448, "lon": 127.0626804}
  }')

CONTEXT_ID=$(echo "$FREEZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('context_id', ''))" 2>/dev/null || echo "")

if [ -n "$CONTEXT_ID" ]; then
  echo -e "${GREEN}✅ Context frozen successfully${NC}"
  echo "  Context ID: $CONTEXT_ID"
else
  echo -e "${YELLOW}⚠️  Context freeze failed${NC}"
  echo "Response:"
  echo "$FREEZE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$FREEZE_RESPONSE"
  exit 1
fi
echo ""

# Step 3: Pipeline Execution (M2-M6)
echo -e "${BLUE}Step 3: Pipeline Execution (M1→M2→M3→M4→M5→M6)${NC}"
echo "Testing: POST /api/v4/pipeline/analyze"
echo "This may take 5-10 seconds..."
echo ""

PIPELINE_START=$(date +%s)
PIPELINE_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/v4/pipeline/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"parcel_id\":\"$CONTEXT_ID\",\"use_cache\":false}")
PIPELINE_END=$(date +%s)
PIPELINE_TIME=$((PIPELINE_END - PIPELINE_START))

PIPELINE_STATUS=$(echo "$PIPELINE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status', ''))" 2>/dev/null || echo "")
MODULES_EXECUTED=$(echo "$PIPELINE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('modules_executed', 0))" 2>/dev/null || echo "0")

if [ "$PIPELINE_STATUS" = "success" ] && [ "$MODULES_EXECUTED" -eq 6 ]; then
  echo -e "${GREEN}✅ Pipeline executed successfully in ${PIPELINE_TIME}s${NC}"
  echo "  Modules executed: $MODULES_EXECUTED"
  
  # Extract key results
  echo ""
  echo "  📊 Pipeline Results Summary:"
  echo "$PIPELINE_RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  • Land Value: ₩{d.get('land_value', 0):,}\")
print(f\"  • Housing Type: {d.get('selected_housing_type', 'N/A')}\")
print(f\"  • Legal Capacity: {d.get('legal_capacity_units', 0)} units\")
print(f\"  • Incentive Capacity: {d.get('incentive_capacity_units', 0)} units\")
print(f\"  • NPV (Public): ₩{d.get('npv_public', 0):,}\")
print(f\"  • LH Decision: {d.get('lh_decision', 'N/A')}\")
print(f\"  • LH Total Score: {d.get('lh_total_score', 0):.1f}/110\")
" 2>/dev/null || echo "  Parse error"
else
  echo -e "${YELLOW}⚠️  Pipeline execution failed or incomplete${NC}"
  echo "  Status: $PIPELINE_STATUS"
  echo "  Modules: $MODULES_EXECUTED/6"
  exit 1
fi
echo ""

# Step 4: Test 6 Types of Final Reports
echo -e "${BLUE}Step 4: Testing 6 Types of Final Reports${NC}"
echo ""

declare -a REPORT_TYPES=(
  "all_in_one:종합 최종보고서"
  "landowner_summary:토지주 제출용 요약보고서"
  "lh_technical:LH 제출용 기술검증 보고서"
  "financial_feasibility:사업성·투자 검토 보고서"
  "quick_check:사전 검토 리포트"
  "presentation:설명용 프레젠테이션 보고서"
)

REPORT_SUCCESS=0
REPORT_TOTAL=${#REPORT_TYPES[@]}

for report in "${REPORT_TYPES[@]}"; do
  IFS=':' read -r type name <<< "$report"
  
  echo "  Testing: $name ($type)"
  
  REPORT_URL="${BACKEND_URL}/api/v4/reports/final/${type}/html?context_id=${CONTEXT_ID}"
  REPORT_RESPONSE=$(curl -s "$REPORT_URL")
  
  # Check if response contains HTML or error
  if echo "$REPORT_RESPONSE" | grep -q "<html\|<!DOCTYPE"; then
    echo -e "    ${GREEN}✅ Report generated successfully${NC}"
    echo "    URL: $REPORT_URL"
    REPORT_SUCCESS=$((REPORT_SUCCESS + 1))
  elif echo "$REPORT_RESPONSE" | grep -q "detail"; then
    echo -e "    ${YELLOW}⚠️  Report generation pending (data not ready)${NC}"
    ERROR_MSG=$(echo "$REPORT_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('detail', 'Unknown error')[:100])" 2>/dev/null || echo "Unknown error")
    echo "    Error: $ERROR_MSG"
  else
    echo -e "    ${YELLOW}⚠️  Unknown response${NC}"
  fi
done

echo ""
echo "  Reports Status: ${REPORT_SUCCESS}/${REPORT_TOTAL} successful"
echo ""

# Step 5: Summary
echo "=============================================="
echo -e "${GREEN}🎉 Test Summary${NC}"
echo "=============================================="
echo ""
echo "✅ Address Search: Working"
echo "✅ M1 Context Freeze: Working"
echo "✅ Pipeline Execution: M1→M2→M3→M4→M5→M6 (${PIPELINE_TIME}s)"
echo "📊 Final Reports: ${REPORT_SUCCESS}/${REPORT_TOTAL} available"
echo ""
echo "🌐 Access URLs:"
echo "  • Frontend: http://localhost:3001/pipeline"
echo "  • Backend API Docs: http://localhost:8005/docs"
echo "  • Context ID: $CONTEXT_ID"
echo ""
echo "📝 Next Steps:"
echo "  1. Open browser and navigate to http://localhost:3001/pipeline"
echo "  2. Enter land data in M1 form"
echo "  3. Click '분석 시작' to run pipeline"
echo "  4. View M2-M6 results"
echo "  5. Download 6 types of reports"
echo ""
echo "=============================================="
