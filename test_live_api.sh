#!/bin/bash
# Live API Test Script for Phase 1 & 2 Fixes

echo "🧪 Testing Live API with Phase 1 & 2 Fixes"
echo "============================================"
echo ""

# Test data
TEST_DATA='{
  "address": "서울특별시 마포구 월드컵북로 120",
  "land_area": 660.0,
  "unit_type": "청년",
  "zone_type": "제3종일반주거지역"
}'

echo "📍 Test Data:"
echo "$TEST_DATA"
echo ""

echo "🔄 Calling /api/generate-report..."
echo ""

# Call the API and save response
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/generate-report" \
  -H "Content-Type: application/json" \
  -d "$TEST_DATA")

# Check if successful
if echo "$RESPONSE" | grep -q '"status":"success"'; then
  echo "✅ API call successful!"
  echo ""
  
  # Extract and validate key fields
  echo "🔍 Validating Phase 1 & 2 Fixes..."
  echo ""
  
  # Save HTML report
  echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'report' in data:
    with open('test_report.html', 'w', encoding='utf-8') as f:
        f.write(data['report'])
    print('✅ HTML report saved to test_report.html')
else:
    print('❌ No report in response')
"
  
  echo ""
  echo "📊 Checking for Phase 1 fixes in HTML:"
  
  # Check for Phase 1 fixes
  if grep -q "월드컵북로" test_report.html 2>/dev/null; then
    echo "  ✅ FIX #1: Real address found (not N/A)"
  else
    echo "  ❌ FIX #1: Address still showing N/A"
  fi
  
  if grep -q "660" test_report.html 2>/dev/null; then
    echo "  ✅ FIX #1: Real land area found (not 0.0)"
  else
    echo "  ❌ FIX #1: Land area still showing 0.0"
  fi
  
  if grep -qE "점/100점" test_report.html 2>/dev/null; then
    echo "  ✅ FIX #5: Risk score in 100-point format"
  else
    echo "  ❌ FIX #5: Risk score not in 100-point format"
  fi
  
  if grep -q "전문가 분석" test_report.html 2>/dev/null; then
    echo "  ✅ FIX #7: Narrative sections added"
  else
    echo "  ❌ FIX #7: Narrative sections missing"
  fi
  
  echo ""
  echo "🎉 Live API test complete!"
  echo "📄 Full HTML report saved to: test_report.html"
  echo "📏 File size: $(wc -c < test_report.html) bytes"
  
else
  echo "❌ API call failed"
  echo "$RESPONSE" | head -50
fi
