#!/bin/bash

echo "M1→M6 Data Flow Test"
echo ""

# Create project
PROJECT_ID=$(curl -s -X POST http://localhost:49999/api/analysis/projects/create \
  -H "Content-Type: application/json" \
  -d '{"project_name":"DataFlow Test","address":"서울시 강남구"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['project_id'])")

echo "Project: $PROJECT_ID"

# Commit M1 data
curl -s -X PUT "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M1/data" \
  -H "Content-Type: application/json" \
  -d '{"address":"서울시","area_sqm":1500,"official_land_price":25000000,"zone_type":"상업지역"}' \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print('M1 Committed:', d['success'])"

# Approve M1
curl -s -X POST "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M1/verify" \
  -H "Content-Type: application/json" -d '{"approved":true}' > /dev/null

# Execute M2-M6
for M in M2 M3 M4 M5 M6; do
  curl -s -X POST "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/$M/execute" > /dev/null
  echo "$M executed"
done

# Check M2 result
echo ""
curl -s "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M2/result" \
  | python3 -c "import sys, json; d=json.load(sys.stdin); r=d.get('result_data',{}); print(f'M2 Land Value: ₩{r.get(\"land_value\",0):,}'); print(f'M2 Unit Price: ₩{r.get(\"unit_price_sqm\",0):,}/㎡')"

echo ""
echo "Test Project: $PROJECT_ID"
