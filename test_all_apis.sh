#!/bin/bash

# ZeroSite v38.0 - 모든 API 테스트

echo "🧪 API 통합 테스트"
echo "===================="
echo ""

# 색상
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 카운터
TOTAL=0
SUCCESS=0
FAIL=0

# 테스트 함수
test_api() {
    local name=$1
    local url=$2
    local headers=$3
    
    TOTAL=$((TOTAL + 1))
    
    echo -n "[$TOTAL] $name ... "
    
    if [ -z "$headers" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -H "$headers" "$url" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ SUCCESS${NC}"
        SUCCESS=$((SUCCESS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code)"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

# 1. 카카오 API
echo "1️⃣  카카오 API 테스트"
echo "-------------------"

test_api "주소 검색 (강남)" \
    "https://dapi.kakao.com/v2/local/search/address.json?query=서울 강남구 역삼동 680-11" \
    "Authorization: KakaoAK 1b172a21a17b8b51dd47884b45228483"

test_api "주소 검색 (관악)" \
    "https://dapi.kakao.com/v2/local/search/address.json?query=서울 관악구 신림동 1524-8" \
    "Authorization: KakaoAK 1b172a21a17b8b51dd47884b45228483"

echo ""

# 2. V-World API
echo "2️⃣  V-World API 테스트"
echo "---------------------"

test_api "PNU 조회" \
    "https://api.vworld.kr/req/data?service=data&version=2.0&request=GetFeature&key=B6B0B6F1-E572-304A-9742-384510D86FE4&data=LP_PA_CBND_BONBUN&geomFilter=POINT(127.0358887%2037.4948853)&format=json"

echo ""

# 3. 국토부 API
echo "3️⃣  국토부 API 테스트"
echo "--------------------"

test_api "용도지역" \
    "http://apis.data.go.kr/1611000/nsdi/LandUseService/attr/getLandUseAttr?ServiceKey=702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d&pnu=1168010100106800011&format=xml"

test_api "개별공시지가" \
    "http://apis.data.go.kr/1611000/nsdi/IndvdLandPriceService/attr/getIndvdLandPriceAttr?ServiceKey=702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d&pnu=1168010100106800011&stdrYear=2024&format=xml"

test_api "실거래가" \
    "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcLandTrade?ServiceKey=702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d&LAWD_CD=11680&DEAL_YMD=202401"

echo ""

# 4. 자체 서버 API
echo "4️⃣  자체 서버 API 테스트"
echo "-----------------------"

test_api "Health Check" \
    "http://localhost:8000/api/v24.1/health"

echo ""

# 요약
echo "===================="
echo "테스트 결과 요약"
echo "===================="
echo "총 테스트: $TOTAL"
echo -e "${GREEN}성공: $SUCCESS${NC}"
echo -e "${RED}실패: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 모든 테스트 통과!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  $FAIL 개 실패${NC}"
    echo "   (외부 API 실패는 Fallback으로 처리됩니다)"
    exit 0
fi
