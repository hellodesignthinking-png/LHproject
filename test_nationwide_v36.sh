#!/bin/bash

# ZeroSite v36.0 NATIONWIDE - Test Script
# Tests 17 addresses from different provinces across South Korea

echo "=================================="
echo "ZeroSite v36.0 NATIONWIDE TEST"
echo "=================================="
echo ""

API_URL="http://localhost:8000/api/v24.1/appraisal"

# Test addresses from 17 different regions
declare -a addresses=(
    "서울특별시 강남구 역삼동 123-45"
    "부산광역시 해운대구 우동 456"
    "인천광역시 연수구 송도동 789"
    "대구광역시 수성구 범어동 100"
    "광주광역시 서구 치평동 200"
    "대전광역시 유성구 봉명동 300"
    "울산광역시 남구 삼산동 400"
    "세종특별자치시 나성동 500"
    "경기도 성남시 분당구 정자동 600"
    "강원특별자치도 춘천시 석사동 700"
    "충청북도 청주시 서원구 분평동 800"
    "충청남도 천안시 동남구 신부동 900"
    "전북특별자치도 전주시 완산구 서노송동 1000"
    "전라남도 목포시 하당동 1100"
    "경상북도 포항시 남구 대도동 1200"
    "경상남도 창원시 성산구 상남동 1300"
    "제주특별자치도 제주시 연동 1400"
)

# Test each address
for i in "${!addresses[@]}"; do
    num=$((i+1))
    address="${addresses[$i]}"
    
    echo "--------------------------------------"
    echo "Test $num/$((${#addresses[@]})): $address"
    echo "--------------------------------------"
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"address\": \"$address\",
            \"land_area_sqm\": 435,
            \"zone_type\": null,
            \"individual_land_price_per_sqm\": null
        }")
    
    # Check if response contains success status
    if echo "$response" | grep -q '"status":"success"'; then
        echo "✅ SUCCESS"
        
        # Extract key information
        final_value=$(echo "$response" | grep -o '"final_value":[0-9.]*' | head -1 | cut -d':' -f2)
        zone=$(echo "$response" | grep -o '"zone_type":"[^"]*"' | head -1 | cut -d'"' -f4)
        
        echo "   → Final Value: ${final_value:-N/A} 억원"
        echo "   → Zone Type: ${zone:-N/A}"
    else
        echo "❌ FAILED"
        echo "$response" | head -5
    fi
    
    echo ""
    sleep 1
done

echo "=================================="
echo "Test Complete!"
echo "=================================="
