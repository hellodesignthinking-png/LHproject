#!/bin/bash

echo "=========================================="
echo "🧪 Frontend Scenario Test"
echo "=========================================="
echo ""

# Test 1: Empty land_price (should fail gracefully)
echo "Test 1: Missing land_price_100m (NaN scenario)"
echo "Expected: 422 Validation Error with clear message"
curl -s -X POST "http://localhost:8000/api/v9/analyze-land" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구",
    "land_area": 1000,
    "zone_type": "제3종일반주거지역",
    "land_appraisal_price": null,
    "unit_count": 80
  }' | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'detail' in data:
    print('✅ Error handled correctly:')
    if isinstance(data['detail'], list):
        for err in data['detail']:
            print(f'   - {err[\"loc\"]}: {err[\"msg\"]}')
    else:
        print(f'   - {data[\"detail\"]}')
else:
    print('❌ Unexpected response')
"

echo ""
echo "Test 2: Valid data (should succeed)"
curl -s -X POST "http://localhost:8000/api/v9/analyze-land" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 123",
    "land_area": 1000,
    "zone_type": "제3종일반주거지역",
    "unit_count": 80
  }' | python3 -c "
import json, sys
data = json.load(sys.stdin)
if data.get('success'):
    result = data['data']
    print('✅ API Success')
    print(f'   IRR: {result.get(\"financial_result\", {}).get(\"irr_10yr\", 0):.2f}%')
    print(f'   Grade: {result.get(\"financial_result\", {}).get(\"overall_grade\", \"N/A\")}')
else:
    print('❌ API Failed:', data.get('message'))
"

echo ""
echo "=========================================="
echo "✅ Tests Complete"
echo "=========================================="
