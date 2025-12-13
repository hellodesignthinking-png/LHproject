#!/bin/bash

echo "🧪 ZeroSite v37.0 ULTIMATE 테스트"
echo "================================"
echo ""

BASE_URL="http://localhost:8000/api/v24.1/appraisal"

test_address() {
    local name=$1
    local address=$2
    local land_area=${3:-435}
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📍 $name"
    echo "   주소: $address"
    echo "   면적: ${land_area}㎡"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    result=$(curl -s -X POST "$BASE_URL" \
        -H "Content-Type: application/json" \
        -d "{\"address\":\"$address\",\"land_area_sqm\":$land_area}")
    
    # Check if result contains expected data
    if echo "$result" | grep -q '"status":"success"\|"success":true\|"final_value"'; then
        echo "   ✅ 성공"
        
        # Try to extract final value
        final_value=$(echo "$result" | grep -o '"final_value":[0-9.]*' | head -1 | cut -d':' -f2)
        if [ -n "$final_value" ]; then
            echo "   💰 최종 감정가: ${final_value}억원"
        fi
        
        # Try to extract zone type
        zone=$(echo "$result" | grep -o '"zone_type":"[^"]*"' | head -1 | cut -d'"' -f4)
        if [ -n "$zone" ]; then
            echo "   🏘️ 용도지역: $zone"
        fi
        
        # Try to extract price
        price=$(echo "$result" | grep -o '"individual_land_price_per_sqm":[0-9]*' | head -1 | cut -d':' -f2)
        if [ -n "$price" ]; then
            echo "   💵 개별공시지가: $(printf "%'d" $price)원/㎡"
        fi
        
        # Check API usage
        tx_api=$(echo "$result" | grep -o '"transactions":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$tx_api" ]; then
            echo "   📡 거래사례 출처: $tx_api"
        fi
        
        # Count transactions
        tx_count=$(echo "$result" | grep -o '"transactions":\[' | wc -l)
        if [ "$tx_count" -gt 0 ]; then
            # Try to count actual transaction objects
            tx_items=$(echo "$result" | grep -o '"deal_date"' | wc -l)
            if [ "$tx_items" -gt 0 ]; then
                echo "   📊 거래사례 건수: ${tx_items}건"
            fi
        fi
        
    else
        echo "   ❌ 실패"
        echo "$result" | head -10
    fi
}

# Header
echo "="*70
echo "ZeroSite v37.0 ULTIMATE - Comprehensive Test Suite"
echo "="*70

# Test Suite
test_address "서울 강남" "서울 강남구 역삼동 680-11" 400
test_address "서울 관악" "서울 관악구 신림동 1524-8" 435
test_address "부산 해운대" "부산광역시 해운대구 우동 456" 500
test_address "경기 성남 (분당)" "경기도 성남시 분당구 정자동 600" 350
test_address "제주" "제주특별자치도 제주시 연동 1400" 450

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 테스트 완료"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 API Integration Status:"
echo "   - Address Parsing: v36 Parser (nationwide)"
echo "   - Zone Type: Estimation (v36 database)"
echo "   - Land Price: Estimation (v36 database)"
echo "   - Transactions: MOLIT API or Generated"
echo ""
echo "🎯 Next Steps:"
echo "   1. Check server logs: tail -50 server_v37.log"
echo "   2. View detailed response: curl http://localhost:8000/api/v24.1/appraisal ..."
echo "   3. Generate PDF: Use /appraisal/pdf endpoint"
echo ""
