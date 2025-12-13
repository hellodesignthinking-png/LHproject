#!/bin/bash

echo "🚀 ZeroSite v37.0 ULTIMATE 배포"
echo "================================"
echo ""
echo "✅ 통합 API:"
echo "   - 카카오: 주소 검색 (Ready)"
echo "   - V-World: PNU 생성 (Ready)"
echo "   - 국토부: 용도지역, 개별공시지가, 실거래가 (Ready)"
echo ""

# 1. 서버 종료
echo "🔴 기존 서버 종료..."
pkill -9 -f "python.*uvicorn.*app.main" 2>/dev/null || true
pkill -9 -f "python.*v24_1_server" 2>/dev/null || true
sleep 2

# 2. 캐시 완전 삭제
echo "🗑️  캐시 삭제..."
find /home/user/webapp -name "*.pyc" -delete 2>/dev/null || true
find /home/user/webapp -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 3. 필수 파일 확인
echo ""
echo "📄 필수 파일 확인:"
files=(
    "app/api_keys_config.py"
    "app/utils/lawd_code_mapper.py"
    "app/services/molit_transaction_service.py"
    "app/services/complete_land_info_service_v37.py"
    "app/services/advanced_address_parser_v36.py"
    "app/services/universal_transaction_engine.py"
    "app/data/nationwide_prices.py"
)

all_found=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (없음!)"
        all_found=false
    fi
done

if [ "$all_found" = false ]; then
    echo ""
    echo "❌ 필수 파일이 없습니다. 배포를 중단합니다."
    exit 1
fi

# 4. 서버 시작
echo ""
echo "🟢 서버 시작..."
cd /home/user/webapp
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server_v37.log 2>&1 &
SERVER_PID=$!
echo "   서버 PID: $SERVER_PID"
sleep 8

# 5. 헬스 체크
echo ""
echo "🏥 헬스 체크..."
HEALTH=$(curl -s http://localhost:8000/api/v24.1/health)

if echo "$HEALTH" | grep -q "healthy"; then
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
    echo ""
    echo "================================"
    echo "✅ v37.0 ULTIMATE 배포 완료!"
    echo "================================"
    echo ""
    echo "서버 URL: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "테스트 실행:"
    echo "  ./test_v37_complete.sh"
    echo ""
else
    echo "❌ 서버가 정상적으로 시작되지 않았습니다."
    echo ""
    echo "로그 확인:"
    echo "  tail -50 server_v37.log"
    exit 1
fi
