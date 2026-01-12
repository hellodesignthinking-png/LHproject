#!/bin/bash
set -e

echo "=== ZeroSite Full Pipeline Test ==="
echo ""

# Step 1: Create new project
echo "Step 1: Creating new project..."
PROJECT_RESPONSE=$(curl -s -X POST http://localhost:49999/api/analysis/projects/create \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Full Pipeline Test",
    "address": "서울특별시 강남구 테헤란로 427"
  }')

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
    "official_price_date": "2024-01-01",
    "zone_type": "상업지역",
    "far": 1000,
    "bcr": 80,
    "road_width": 30,
    "subway_stations": [{"name": "삼성역", "line": "2호선", "distance_m": 200}],
    "poi_schools": [{"name": "테헤란초등학교", "distance_m": 500}],
    "data_sources": ["Kakao Map API", "국토교통부 개별공시지가"]
  }' > /dev/null
echo "✅ M1 Data Updated"
echo ""

# Step 3: Approve M1
echo "Step 3: Approving M1..."
curl -s -X POST "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M1/verify" \
  -H "Content-Type: application/json" \
  -d '{"approved": true}' > /dev/null
echo "✅ M1 Approved"
echo ""

# Step 4-8: Execute M2→M6
for MODULE in M2 M3 M4 M5 M6; do
  echo "Step: Executing $MODULE..."
  curl -s -X POST "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/$MODULE/execute" > /dev/null
  echo "✅ $MODULE Executed"
done
echo ""

# Step 9: Verify all results
echo "=== Final Results ==="
echo ""

for MODULE in M1 M2 M3 M4 M5 M6; do
  echo "--- $MODULE Result ---"
  RESULT=$(curl -s "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/$MODULE/result")
  echo "$RESULT" | python3 -m json.tool | grep -E "(status|land_value|unit_price_sqm|selected_type|confidence|message)" | head -10
  echo ""
done

echo "=== Pipeline Test Project ID: $PROJECT_ID ==="
