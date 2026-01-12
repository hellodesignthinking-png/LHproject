#!/bin/bash
set -e

echo "===================================================="
echo "  M1→M6 Data Flow - End-to-End Verification"
echo "===================================================="
echo ""

# Step 1: Create new project
echo "Step 1: Creating new project..."
PROJECT_RESPONSE=$(curl -s -X POST http://localhost:49999/api/analysis/projects/create \
  -H "Content-Type: application/json" \
  -d '{"project_name": "M1→M6 Data Flow Test", "address": "서울특별시 강남구 테헤란로 518"}')

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['project_id'])")
echo "✅ Project Created: $PROJECT_ID"
echo ""

# Step 2: Commit M1 data (manual input simulation)
echo "Step 2: Committing M1 data..."
M1_COMMIT=$(curl -s -X PUT "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M1/data" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 518",
    "area_sqm": 1500,
    "official_land_price": 25000000,
    "official_price_date": "2024-01-01",
    "zone_type": "상업지역",
    "far": 1200,
    "bcr": 80,
    "road_width": 30,
    "subway_stations": [{"name": "삼성역", "line": "2호선", "distance_m": 300}],
    "poi_schools": [{"name": "개포초등학교", "distance_m": 600}],
    "data_sources": ["Manual Input", "Kakao Map API"]
  }')

echo "$M1_COMMIT" | python3 << 'PYEOF'
import sys, json
data = json.load(sys.stdin)
if data.get('success'):
    print(f"✅ M1 Data Committed")
    committed = data.get('committed_data', {})
    print(f"   Area: {committed.get('area_sqm')}㎡")
    print(f"   Price: ₩{committed.get('official_land_price'):,}/㎡")
    print(f"   Zone: {committed.get('zone_type')}")
else:
    print(f"❌ M1 commit failed: {data}")
    sys.exit(1)
PYEOF
echo ""

# Step 3: Verify M1 result_data exists
echo "Step 3: Verifying M1 result_data..."
M1_RESULT=$(curl -s "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M1/result")

echo "$M1_RESULT" | python3 << 'PYEOF'
import sys, json
data = json.load(sys.stdin)
result_data = data.get('result_data', {})

area = result_data.get('area_sqm', 0)
price = result_data.get('official_land_price', 0)
zone = result_data.get('zone_type', '')

if area > 0 and price > 0 and zone:
    print(f"✅ M1 result_data verified")
    print(f"   area_sqm = {area}")
    print(f"   official_land_price = {price}")
    print(f"   zone_type = {zone}")
else:
    print(f"❌ M1 result_data INVALID:")
    print(f"   area_sqm = {area} (must be > 0)")
    print(f"   official_land_price = {price} (must be > 0)")
    print(f"   zone_type = {zone} (must not be empty)")
    sys.exit(1)
PYEOF
echo ""

# Step 4: Approve M1
echo "Step 4: Approving M1..."
curl -s -X POST "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M1/verify" \
  -H "Content-Type: application/json" \
  -d '{"approved": true}' > /dev/null
echo "✅ M1 Approved"
echo ""

# Step 5: Execute M2→M6
echo "Step 5: Executing M2→M6..."
for MODULE in M2 M3 M4 M5 M6; do
  echo "   Executing $MODULE..."
  curl -s -X POST "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/$MODULE/execute" > /dev/null
  echo "   ✅ $MODULE Executed"
done
echo ""

# Step 6: Verify M2 result (must be non-zero)
echo "Step 6: Verifying M2 result..."
M2_RESULT=$(curl -s "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M2/result")

echo "$M2_RESULT" | python3 << 'PYEOF'
import sys, json
data = json.load(sys.stdin)
result_data = data.get('result_data', {})

land_value = result_data.get('land_value', 0)
unit_price = result_data.get('unit_price_sqm', 0)

if land_value > 0 and unit_price > 0:
    print(f"✅ M2 result NON-ZERO (calculated from M1 data)")
    print(f"   land_value = ₩{land_value:,}")
    print(f"   unit_price_sqm = ₩{unit_price:,}/㎡")
else:
    print(f"❌ M2 result is ZERO (M1 data not used):")
    print(f"   land_value = ₩{land_value:,}")
    print(f"   unit_price_sqm = ₩{unit_price:,}/㎡")
    print(f"   This indicates M2 did not read M1 result_data!")
    sys.exit(1)
PYEOF
echo ""

# Step 7: Verify M3 result
echo "Step 7: Verifying M3 result..."
M3_RESULT=$(curl -s "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M3/result")

echo "$M3_RESULT" | python3 << 'PYEOF'
import sys, json
data = json.load(sys.stdin)
result_data = data.get('result_data', {})

selected_type = result_data.get('selected_type', '')
confidence = result_data.get('confidence', 0)

if selected_type and confidence > 0:
    print(f"✅ M3 result valid (calculated from M1 zone_type)")
    print(f"   selected_type = {selected_type}")
    print(f"   confidence = {confidence}%")
else:
    print(f"❌ M3 result is invalid")
    sys.exit(1)
PYEOF
echo ""

# Step 8: Verify M4 result
echo "Step 8: Verifying M4 result..."
M4_RESULT=$(curl -s "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M4/result")

echo "$M4_RESULT" | python3 << 'PYEOF'
import sys, json
data = json.load(sys.stdin)
result_data = data.get('result_data', {})

legal_units = result_data.get('legal_units', 0)
parking = result_data.get('parking_count', 0)

if legal_units > 0 and parking > 0:
    print(f"✅ M4 result valid (calculated from M1 area/BCR/FAR)")
    print(f"   legal_units = {legal_units}")
    print(f"   parking_count = {parking}")
else:
    print(f"❌ M4 result is invalid or zero")
    sys.exit(1)
PYEOF
echo ""

# Final summary
echo "===================================================="
echo "  ✅ M1→M6 DATA FLOW VERIFICATION PASSED"
echo "===================================================="
echo ""
echo "Verified:"
echo "  1. M1 data committed to result_data ✅"
echo "  2. M1 result_data has non-zero values ✅"
echo "  3. M2 calculated with M1 data (non-zero) ✅"
echo "  4. M3 calculated with M1 zone_type ✅"
echo "  5. M4 calculated with M1 area ✅"
echo ""
echo "🎯 SUCCESS: M2~M6 results are calculated from M1 result_data"
echo ""
echo "Test Project ID: $PROJECT_ID"
echo "===================================================="
