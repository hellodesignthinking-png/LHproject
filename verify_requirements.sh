#!/bin/bash
set -e

echo "==================================================="
echo "  ZeroSite Decision OS - Requirements Verification"
echo "==================================================="
echo ""

# Run pipeline
echo "Creating test project with real address..."
PROJECT_RESPONSE=$(curl -s -X POST http://localhost:49999/api/analysis/projects/create \
  -H "Content-Type: application/json" \
  -d '{"project_name": "Requirements Test", "address": "서울특별시 강남구 테헤란로 518"}')

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['project_id'])")
echo "✅ Project ID: $PROJECT_ID"
echo ""

# Update M1 with real-like data
curl -s -X PUT "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M1/data" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 518",
    "area_sqm": 1200,
    "official_land_price": 25000000,
    "official_price_date": "2024-01-01",
    "zone_type": "상업지역",
    "far": 800,
    "bcr": 70,
    "road_width": 25,
    "subway_stations": [{"name": "삼성역", "line": "2호선", "distance_m": 300}],
    "poi_schools": [{"name": "개포초등학교", "distance_m": 600}],
    "data_sources": ["Kakao Map API", "국토교통부 개별공시지가", "토지이용규제정보"]
  }' > /dev/null

# Approve and execute pipeline
curl -s -X POST "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M1/verify" \
  -H "Content-Type: application/json" -d '{"approved": true}' > /dev/null

for MODULE in M2 M3 M4 M5 M6; do
  curl -s -X POST "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/$MODULE/execute" > /dev/null
done

echo "Pipeline executed. Verifying requirements..."
echo ""

# Verification function
verify_requirement() {
  local MODULE=$1
  local REQUIREMENT=$2
  local CHECK_SCRIPT=$3
  
  RESULT=$(curl -s "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/$MODULE/result")
  CHECK_RESULT=$(echo "$RESULT" | python3 -c "$CHECK_SCRIPT" 2>&1)
  
  if [ "$CHECK_RESULT" = "PASS" ]; then
    echo "✅ $MODULE: $REQUIREMENT"
  else
    echo "❌ $MODULE: $REQUIREMENT - $CHECK_RESULT"
  fi
}

echo "--- Requirement A: M1 Real Data Loading ---"
verify_requirement "M1" "Address loaded" "import sys, json; d=json.load(sys.stdin); print('PASS' if d.get('result_data', {}).get('address') else 'FAIL')"
verify_requirement "M1" "Area > 0" "import sys, json; d=json.load(sys.stdin); print('PASS' if d.get('result_data', {}).get('area_sqm', 0) > 0 else 'FAIL: area=0')"
verify_requirement "M1" "Official price > 0" "import sys, json; d=json.load(sys.stdin); print('PASS' if d.get('result_data', {}).get('official_land_price', 0) > 0 else 'FAIL')"
echo ""

echo "--- Requirement E: Minimum Output Conditions ---"
verify_requirement "M2" "total_land_value > 0" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('land_value', 0); print('PASS' if v > 0 else f'FAIL: {v}')"
verify_requirement "M2" "unit_price_per_sqm > 0" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('unit_price_sqm', 0); print('PASS' if v > 0 else f'FAIL: {v}')"

verify_requirement "M3" "selected_type not empty" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('selected_type', ''); print('PASS' if v else 'FAIL')"
verify_requirement "M3" "rationale length > 20" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('decision_rationale', ''); print('PASS' if len(v) > 20 else f'FAIL: len={len(v)}')"

verify_requirement "M4" "legal_units > 0" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('legal_units', 0); print('PASS' if v > 0 else f'FAIL: {v}')"
verify_requirement "M4" "incentive_units >= legal_units" "import sys, json; d=json.load(sys.stdin); r=d.get('result_data', {}); l=r.get('legal_units', 0); i=r.get('incentive_units', 0); print('PASS' if i >= l else f'FAIL: {i}<{l}')"
verify_requirement "M4" "parking_count >= 1" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('parking_count', 0); print('PASS' if v >= 1 else f'FAIL: {v}')"

verify_requirement "M5" "NPV != 0" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('npv', 0); print('PASS' if v != 0 else 'FAIL')"
verify_requirement "M5" "IRR != 0" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('irr', 0); print('PASS' if v != 0 else 'FAIL')"
verify_requirement "M5" "ROI != 0" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('roi', 0); print('PASS' if v != 0 else 'FAIL')"
verify_requirement "M5" "cost_breakdown exists" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('cost_breakdown'); print('PASS' if v else 'FAIL')"

verify_requirement "M6" "decision in [GO, CONDITIONAL, NO-GO]" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('decision', ''); print('PASS' if v in ['GO', 'CONDITIONAL', 'NO-GO'] else f'FAIL: {v}')"
verify_requirement "M6" "risk_list >= 3" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('risk_list', []); print('PASS' if len(v) >= 3 else f'FAIL: {len(v)}')"
verify_requirement "M6" "recommendations not empty" "import sys, json; d=json.load(sys.stdin); v=d.get('result_data', {}).get('recommendations', []); print('PASS' if len(v) > 0 else 'FAIL')"

echo ""
echo "==================================================="
echo "  Verification Complete"
echo "  Test Project ID: $PROJECT_ID"
echo "==================================================="
