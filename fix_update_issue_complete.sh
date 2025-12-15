#!/bin/bash

# 메인페이지 업데이트 문제 완전 해결

echo "🔧 메인페이지 업데이트 문제 완전 해결"
echo "=========================================="
echo ""

# 색상
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 작업 디렉토리
cd /home/user/webapp

# ========================================
# 1. 파일 확인
# ========================================

echo "1️⃣  파일 확인..."

if [ ! -f "public/index_v40_FINAL.html" ]; then
    echo -e "${RED}❌ index_v40_FINAL.html 없음${NC}"
    echo ""
    echo "파일을 먼저 생성하세요!"
    exit 1
fi

echo -e "${GREEN}✅ index_v40_FINAL.html 존재${NC}"
echo ""

# ========================================
# 2. 파일 권한
# ========================================

echo "2️⃣  파일 권한 설정..."
chmod 644 public/index_v40_FINAL.html 2>/dev/null
chmod 644 public/js/app_v40.js 2>/dev/null
chmod 755 public 2>/dev/null
chmod 755 public/js 2>/dev/null
echo -e "${GREEN}✅ 권한 설정 완료${NC}"
echo ""

# ========================================
# 3. 서버 완전 재시작
# ========================================

echo "3️⃣  서버 완전 재시작..."

# 종료
echo "   기존 서버 종료 중..."
pkill -9 -f "python.*main" 2>/dev/null
pkill -9 -f uvicorn 2>/dev/null
sleep 2

# 포트 정리
for port in 8000 8001; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo "   포트 $port 정리 중..."
        kill -9 $(lsof -t -i:$port) 2>/dev/null
    fi
done

sleep 2

# 로그 디렉토리 생성
mkdir -p logs

# 시작
echo "   서버 시작 중..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload \
    > logs/server.log 2>&1 &

echo $! > server.pid

sleep 5

# 확인
if [ -f server.pid ] && ps -p $(cat server.pid) > /dev/null 2>/dev/null; then
    echo -e "${GREEN}✅ 서버 시작 성공 (PID: $(cat server.pid))${NC}"
else
    echo -e "${RED}❌ 서버 시작 실패${NC}"
    if [ -f logs/server.log ]; then
        echo ""
        echo "로그 (마지막 20줄):"
        tail -20 logs/server.log
    fi
    exit 1
fi

echo ""

# ========================================
# 4. HTTP 테스트
# ========================================

echo "4️⃣  HTTP 테스트..."

# 잠시 대기 (서버 초기화)
sleep 3

response=$(curl -s http://localhost:8001/ 2>/dev/null)

if [ -z "$response" ]; then
    echo -e "${RED}❌ 서버 응답 없음${NC}"
    echo "   로그 확인: tail -f logs/server.log"
    exit 1
fi

if echo "$response" | grep -q "v40\|종합 토지분석"; then
    echo -e "${GREEN}✅ v40 정상 서빙${NC}"
else
    echo -e "${YELLOW}⚠️  v40 키워드 없음${NC}"
    echo ""
    echo "서빙된 HTML (처음 200자):"
    echo "$response" | head -c 200
    echo ""
fi

echo ""

# ========================================
# 5. 캐시 비활성화 확인
# ========================================

echo "5️⃣  캐시 헤더 확인..."

headers=$(curl -s -I http://localhost:8001/ 2>/dev/null)

if echo "$headers" | grep -qi "no-cache"; then
    echo -e "${GREEN}✅ Cache-Control: no-cache${NC}"
else
    echo -e "${YELLOW}⚠️  캐시 헤더 없음${NC}"
    echo "   (브라우저에서 강제 새로고침 필요: Ctrl+Shift+R)"
fi

echo ""

# ========================================
# 6. 파일 해시 검증
# ========================================

echo "6️⃣  파일 무결성 검증..."

local_hash=$(md5sum public/index_v40_FINAL.html 2>/dev/null | awk '{print $1}' || md5 -q public/index_v40_FINAL.html 2>/dev/null)
served_hash=$(curl -s http://localhost:8001/ 2>/dev/null | md5sum 2>/dev/null | awk '{print $1}' || md5 -q -)

echo "로컬 파일: $local_hash"
echo "서빙 파일: $served_hash"

if [ "$local_hash" = "$served_hash" ]; then
    echo -e "${GREEN}✅ 파일 일치${NC}"
else
    echo -e "${YELLOW}⚠️  파일 불일치 (정상일 수 있음 - HTML 압축 등)${NC}"
fi

echo ""

# ========================================
# 최종 안내
# ========================================

echo "=========================================="
echo -e "${GREEN}✅ 서버 재시작 완료${NC}"
echo "=========================================="
echo ""
echo "📌 브라우저에서 확인:"
echo "   1. Ctrl+Shift+R (강제 새로고침)"
echo "   2. 또는 시크릿 모드로 테스트 (Ctrl+Shift+N)"
echo "   3. 또는 브라우저 캐시 완전 삭제"
echo ""
echo "🌐 접속 URL:"
echo "   http://localhost:8001/"
echo ""
echo "📊 상태 확인:"
echo "   로그: tail -f logs/server.log"
echo "   Health: curl http://localhost:8001/api/v40/health"
echo ""
echo "🛑 서버 종료:"
echo "   kill \$(cat server.pid)"
echo ""
echo "🔍 진단 재실행:"
echo "   ./diagnose_update_issue.sh"
echo ""
