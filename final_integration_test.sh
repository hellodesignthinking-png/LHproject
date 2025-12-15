#!/bin/bash

# ZeroSite v38.0 FINAL - 통합 테스트

echo "🎯 ZeroSite 최종 통합 테스트"
echo "=============================="
echo ""

# 1. 서버 상태 확인
echo "1️⃣  서버 상태 확인"
./check_health.sh || {
    echo "❌ 서버가 실행되지 않았습니다."
    echo "   ./start_server_permanent.sh를 먼저 실행하세요."
    exit 1
}
echo ""

# 2. API 연동 테스트
echo "2️⃣  API 연동 테스트"
./test_all_apis.sh
echo ""

# 3. 감정평가 API 테스트
echo "3️⃣  감정평가 API 테스트"
echo ""

for address in \
    "서울 강남구 역삼동 680-11" \
    "서울 관악구 신림동 1524-8" \
    "부산 해운대구 우동 1234"
do
    echo "   테스트: $address"
    
    result=$(curl -s -X POST "http://localhost:8000/api/v24.1/appraisal" \
        -H "Content-Type: application/json" \
        -d "{\"address\":\"$address\",\"land_area_sqm\":400}")
    
    if echo "$result" | grep -q "success"; then
        final_value=$(echo "$result" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('final_appraisal_value', 'N/A'))" 2>/dev/null || echo "N/A")
        echo "   ✅ 평가액: ${final_value}억원"
    else
        echo "   ❌ 실패"
        echo "$result" | head -3
    fi
done

echo ""

# 4. PDF 생성 테스트
echo "4️⃣  PDF 생성 테스트"
./test_pdf_generation.sh
echo ""

# 5. PDF 검증
echo "5️⃣  PDF 품질 검증"
python3 validate_pdf_quality.py
echo ""

# 최종 결과
echo "=============================="
echo "🎊 최종 통합 테스트 완료"
echo "=============================="
echo ""
echo "다음 단계:"
echo "  1. 실제 사용 테스트"
echo "  2. 성능 측정"
echo "  3. 프로덕션 배포"
