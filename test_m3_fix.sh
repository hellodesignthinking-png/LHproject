#!/bin/bash
set -e

echo "===================================================="
echo "  M3 Result Endpoint Fix - Verification Test"
echo "===================================================="
echo ""

# Step 1: Create new project
echo "Step 1: Creating new project..."
PROJECT_RESPONSE=$(curl -s -X POST http://localhost:49999/api/analysis/projects/create \
  -H "Content-Type: application/json" \
  -d '{"project_name": "M3 Fix Test", "address": "서울특별시 강남구 테헤란로 427"}')

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['project_id'])")
echo "✅ Project Created: $PROJECT_ID"
echo ""

# Step 2: Update M1 data
echo "Step 2: Updating M1 data..."
curl -s -X PUT "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M1/data" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 427",
    "area_sqm": 1000,
    "official_land_price": 20000000,
    "zone_type": "상업지역",
    "far": 1000,
    "bcr": 80,
    "data_sources": ["Kakao Map API"]
  }' > /dev/null
echo "✅ M1 Data Updated"
echo ""

# Step 3: Try to get M3 result (should fail with MODULE_NOT_EXECUTED)
echo "Step 3: Testing M3 result before execution..."
M3_BEFORE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M3/result")
HTTP_CODE=$(echo "$M3_BEFORE" | grep "HTTP_CODE:" | cut -d: -f2)

if [ "$HTTP_CODE" = "409" ]; then
  echo "✅ PASS: M3 not executed → Returns 409 error"
  echo "$M3_BEFORE" | head -20 | python3 -m json.tool 2>/dev/null | grep -E "(error|message|MODULE_NOT_EXECUTED)" || true
else
  echo "❌ FAIL: Expected 409, got $HTTP_CODE"
  echo "$M3_BEFORE" | head -10
fi
echo ""

# Step 4: Approve M1
echo "Step 4: Approving M1..."
curl -s -X POST "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M1/verify" \
  -H "Content-Type: application/json" \
  -d '{"approved": true}' > /dev/null
echo "✅ M1 Approved"
echo ""

# Step 5: Execute M2
echo "Step 5: Executing M2..."
curl -s -X POST "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M2/execute" > /dev/null
echo "✅ M2 Executed"
echo ""

# Step 6: Execute M3
echo "Step 6: Executing M3..."
curl -s -X POST "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M3/execute" > /dev/null
echo "✅ M3 Executed"
echo ""

# Step 7: Get M3 result (should succeed with real data)
echo "Step 7: Testing M3 result after execution..."
M3_AFTER=$(curl -s "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M3/result")

echo "$M3_AFTER" | python3 << 'PYEOF'
import sys, json
data = json.load(sys.stdin)

# Check response structure
print("✅ Response received")

# Check success
if not data.get('success'):
    print(f"❌ FAIL: success = {data.get('success')}")
    sys.exit(1)
print("✅ PASS: success = True")

# Check result_data exists
result_data = data.get('result_data')
if not result_data:
    print(f"❌ FAIL: result_data is missing or empty")
    print(f"Available keys: {list(data.keys())}")
    sys.exit(1)
print("✅ PASS: result_data exists")

# Check M3 schema
selected_type = result_data.get('selected_type')
if not selected_type:
    print(f"❌ FAIL: selected_type is missing")
    print(f"result_data keys: {list(result_data.keys())}")
    sys.exit(1)
print(f"✅ PASS: selected_type = '{selected_type}'")

# Check rationale
rationale = result_data.get('decision_rationale', '')
if len(rationale) < 20:
    print(f"❌ FAIL: decision_rationale too short ({len(rationale)} chars)")
    sys.exit(1)
print(f"✅ PASS: decision_rationale = '{rationale[:50]}...' ({len(rationale)} chars)")

# Check confidence
confidence = result_data.get('confidence', 0)
if confidence == 0:
    print(f"⚠️  WARNING: confidence = 0")
else:
    print(f"✅ PASS: confidence = {confidence}%")

print("\n📊 M3 Result Summary:")
print(f"   Selected Type: {selected_type}")
print(f"   Confidence: {confidence}%")
print(f"   Rationale: {rationale}")

PYEOF

PYRESULT=$?

if [ $PYRESULT -eq 0 ]; then
  echo ""
  echo "===================================================="
  echo "  ✅ ALL TESTS PASSED"
  echo "  M3 result endpoint is working correctly"
  echo "  Test Project ID: $PROJECT_ID"
  echo "===================================================="
else
  echo ""
  echo "===================================================="
  echo "  ❌ SOME TESTS FAILED"
  echo "  Check output above for details"
  echo "  Test Project ID: $PROJECT_ID"
  echo "===================================================="
  exit 1
fi

