#!/bin/bash
echo "🧪 Testing All Modules (M2-M6)..."
echo "================================="

BASE_URL="https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai"

# Test M2
echo ""
echo "Testing M2 (토지감정평가)..."
curl -s -o /dev/null -w "M2: %{http_code}\n" "$BASE_URL/demo/m2_classic"

# Test M3
echo "Testing M3 (공급 유형 판단)..."
curl -s -o /dev/null -w "M3: %{http_code}\n" "$BASE_URL/demo/m3_supply_type"

# Test M4
echo "Testing M4 (건축 규모 판단)..."
curl -s -o /dev/null -w "M4: %{http_code}\n" "$BASE_URL/demo/m4_building_scale"

# Test M5
echo "Testing M5 (사업성 분석)..."
curl -s -o /dev/null -w "M5: %{http_code}\n" "$BASE_URL/demo/m5_feasibility"

# Test M6
echo "Testing M6 (LH 종합 판단)..."
curl -s -o /dev/null -w "M6: %{http_code}\n" "$BASE_URL/demo/m6_comprehensive"

echo ""
echo "================================="
echo "✅ Integration test complete!"
