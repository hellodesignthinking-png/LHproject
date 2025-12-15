#!/bin/bash

###############################################################################
# Quick Data Test Script (즉시 확인)
#
# Purpose: Quick verification of key data points for a single address
#
# Author: ZeroSite Development Team
# Date: 2024-12-14
###############################################################################

API_URL="http://localhost:8000/api/v24.1/appraisal"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default test address (강남)
ADDRESS="${1:-서울특별시 강남구 역삼동 680-11}"
LAND_AREA="${2:-400}"

echo "========================================================================"
echo "ZeroSite Quick Data Test"
echo "========================================================================"
echo ""
echo "Testing Address: $ADDRESS"
echo "Land Area: ${LAND_AREA}㎡"
echo ""

# Make API call
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{
        \"address\": \"$ADDRESS\",
        \"land_area_sqm\": $LAND_AREA
    }")

# Check if valid JSON
if ! echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Invalid JSON response${NC}"
    echo "$RESPONSE"
    exit 1
fi

# Extract all key fields
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}1. 주소 파싱 (Address Parsing)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SIDO=$(echo "$RESPONSE" | jq -r '.land_info.address_parsed.sido // "MISSING"')
SIGUNGU=$(echo "$RESPONSE" | jq -r '.land_info.address_parsed.sigungu // "MISSING"')
DONG=$(echo "$RESPONSE" | jq -r '.land_info.address_parsed.dong // "MISSING"')
echo "   시·도: $SIDO"
echo "   시·군·구: $SIGUNGU"
echo "   읍·면·동: $DONG"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}2. 용도지역 (Zone Type)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ZONE_TYPE=$(echo "$RESPONSE" | jq -r '.land_info.zone_type // "MISSING"')
echo "   용도지역: $ZONE_TYPE"
if [ "$ZONE_TYPE" != "MISSING" ]; then
    echo -e "   ${GREEN}✓ OK${NC}"
else
    echo -e "   ${RED}✗ MISSING${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}3. 공시지가 (Official Land Price)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
OFFICIAL_PRICE=$(echo "$RESPONSE" | jq -r '.land_info.individual_land_price_per_sqm // 0')
OFFICIAL_PRICE_PYEONG=$(echo "$RESPONSE" | jq -r '.land_info.individual_land_price_per_pyeong // 0')
echo "   공시지가 (㎡): ₩$(printf "%'d" $OFFICIAL_PRICE)/㎡"
echo "   공시지가 (평): ₩$(printf "%'d" $OFFICIAL_PRICE_PYEONG)/평"
if [ "$OFFICIAL_PRICE" -gt 0 ]; then
    echo -e "   ${GREEN}✓ OK (양수)${NC}"
else
    echo -e "   ${RED}✗ ERROR (0 or negative)${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}4. 시장가격 (Market Price)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
MARKET_PRICE=$(echo "$RESPONSE" | jq -r '.land_info.market_price_per_sqm_krw // 0')
MARKET_PRICE_MAN=$(echo "$RESPONSE" | jq -r '.land_info.market_price_per_sqm_man // 0')
echo "   시장가 (㎡): ₩$(printf "%'d" $MARKET_PRICE)/㎡"
echo "   시장가 (만원): $(printf "%'.0f" $MARKET_PRICE_MAN)만원/㎡"
if [ "$MARKET_PRICE" -gt 0 ]; then
    echo -e "   ${GREEN}✓ OK (양수)${NC}"
else
    echo -e "   ${RED}✗ ERROR (0 or negative)${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}5. 공시지가/시세 비율 (Official/Market Ratio)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RATIO=$(echo "$RESPONSE" | jq -r '.land_info.official_to_market_ratio // 0')
RATIO_PERCENT=$(awk "BEGIN {printf \"%.1f\", $RATIO * 100}")
echo "   비율: ${RATIO_PERCENT}%"
if (( $(awk "BEGIN {print ($RATIO >= 0.5 && $RATIO <= 0.9)}") )); then
    echo -e "   ${GREEN}✓ OK (50-90% 범위)${NC}"
else
    echo -e "   ${YELLOW}⚠ Warning (범위 벗어남)${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}6. 거래사례 (Transaction Cases)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TX_COUNT=$(echo "$RESPONSE" | jq -r '.transactions_summary.count // 0')
TX_AVG_PRICE=$(echo "$RESPONSE" | jq -r '.transactions_summary.avg_price_per_sqm // 0')
echo "   거래사례 수: $TX_COUNT건"
echo "   평균 단가: ₩$(printf "%'d" $TX_AVG_PRICE)/㎡"
if [ "$TX_COUNT" -ge 10 ]; then
    echo -e "   ${GREEN}✓ OK (10건 이상)${NC}"
else
    echo -e "   ${RED}✗ ERROR (10건 미만)${NC}"
fi

# Show first 3 transactions
echo ""
echo "   첫 3개 거래사례:"
for i in 0 1 2; do
    TX_ADDR=$(echo "$RESPONSE" | jq -r ".transactions[$i].address // \"N/A\"")
    TX_PRICE=$(echo "$RESPONSE" | jq -r ".transactions[$i].price_per_sqm // 0")
    TX_DIST=$(echo "$RESPONSE" | jq -r ".transactions[$i].distance_km // 0")
    
    echo "   [$((i+1))] $TX_ADDR"
    echo "       단가: ₩$(printf "%'d" $TX_PRICE)/㎡, 거리: ${TX_DIST}km"
    
    # Check address matching
    if echo "$TX_ADDR" | grep -q "$SIDO"; then
        echo -e "       ${GREEN}✓ 주소 일치${NC}"
    else
        echo -e "       ${RED}✗ 주소 불일치${NC}"
    fi
done
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}7. 감정평가 결과 (Appraisal Result)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
FINAL_VALUE=$(echo "$RESPONSE" | jq -r '.appraisal.final_value // 0')
CONFIDENCE=$(echo "$RESPONSE" | jq -r '.appraisal.confidence // "N/A"')
echo "   최종 감정가: ${FINAL_VALUE}억원"
echo "   신뢰도: $CONFIDENCE"
echo ""

echo "========================================================================"
echo -e "${GREEN}✅ Quick Test Complete${NC}"
echo "========================================================================"
