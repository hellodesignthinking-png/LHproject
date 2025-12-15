#!/bin/bash

# 메인페이지 업데이트 문제 진단

echo "🔍 ZeroSite 메인페이지 업데이트 문제 진단"
echo "=============================================="
echo ""

# 색상
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 작업 디렉토리
cd /home/user/webapp

# ========================================
# 1. 파일 존재 확인
# ========================================

echo -e "${BLUE}1️⃣  파일 존재 확인${NC}"
echo "----------------------------------------"

# v40 파일들
files=(
    "public/index_v40_FINAL.html"
    "public/js/app_v40.js"
    "app/api/v40/router.py"
    "app/main.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        # 수정 시간 및 크기
        mod_time=$(stat -c "%y" "$file" 2>/dev/null || stat -f "%Sm" "$file" 2>/dev/null)
        size=$(stat -c "%s" "$file" 2>/dev/null || stat -f "%z" "$file" 2>/dev/null)
        
        echo -e "${GREEN}✅ $file${NC}"
        echo "   수정: $mod_time"
        echo "   크기: $((size / 1024))KB"
    else
        echo -e "${RED}❌ $file (없음)${NC}"
    fi
done

echo ""

# ========================================
# 2. 서버 프로세스 확인
# ========================================

echo -e "${BLUE}2️⃣  서버 프로세스 확인${NC}"
echo "----------------------------------------"

# 실행 중인 Python 서버
python_procs=$(ps aux | grep -E "python.*main\.py|uvicorn" | grep -v grep)

if [ -n "$python_procs" ]; then
    echo -e "${GREEN}✅ 서버 실행 중${NC}"
    echo "$python_procs" | head -3
else
    echo -e "${RED}❌ 서버 미실행${NC}"
fi

echo ""

# ========================================
# 3. 포트 확인
# ========================================

echo -e "${BLUE}3️⃣  포트 확인${NC}"
echo "----------------------------------------"

for port in 8000 8001 3000; do
    if lsof -i :$port >/dev/null 2>&1; then
        proc=$(lsof -i :$port | grep LISTEN | awk '{print $1, $2}')
        echo -e "${GREEN}✅ 포트 $port 사용 중${NC}"
        echo "   $proc"
    else
        echo -e "${YELLOW}⚠️  포트 $port 사용 안 함${NC}"
    fi
done

echo ""

# ========================================
# 4. 라우팅 설정 확인
# ========================================

echo -e "${BLUE}4️⃣  라우팅 설정 확인${NC}"
echo "----------------------------------------"

if [ -f "app/main.py" ]; then
    # root redirect 확인
    if grep -q "index_v40_FINAL" app/main.py; then
        echo -e "${GREEN}✅ Root redirect → index_v40_FINAL.html${NC}"
    elif grep -q "FileResponse.*index\|RedirectResponse.*index" app/main.py; then
        echo -e "${YELLOW}⚠️  Root redirect 설정 있음 (다른 파일)${NC}"
        grep -n "FileResponse\|RedirectResponse" app/main.py | grep -i index | head -3
    else
        echo -e "${RED}❌ Root redirect 설정 없음${NC}"
    fi
    
    # static files 설정
    if grep -q "StaticFiles.*public" app/main.py; then
        echo -e "${GREEN}✅ Static files 마운트: /public${NC}"
    else
        echo -e "${RED}❌ Static files 설정 없음${NC}"
    fi
else
    echo -e "${RED}❌ app/main.py 없음${NC}"
fi

echo ""

# ========================================
# 5. 실제 서빙 파일 확인
# ========================================

echo -e "${BLUE}5️⃣  실제 서빙 파일 확인 (HTTP 테스트)${NC}"
echo "----------------------------------------"

# localhost 테스트
for port in 8001 8000; do
    if curl -s "http://localhost:$port/" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ http://localhost:$port/ 응답${NC}"
        
        # HTML 제목 추출
        title=$(curl -s "http://localhost:$port/" | grep -o "<title>.*</title>" | head -1)
        if [ -n "$title" ]; then
            echo "   $title"
        fi
        
        # v40 키워드 확인
        if curl -s "http://localhost:$port/" | grep -q "v40\|종합 토지분석"; then
            echo -e "   ${GREEN}✅ v40 키워드 포함${NC}"
        else
            echo -e "   ${YELLOW}⚠️  v40 키워드 없음 (이전 버전?)${NC}"
        fi
        
        break
    else
        echo -e "${YELLOW}⚠️  http://localhost:$port/ 응답 없음${NC}"
    fi
done

echo ""

# ========================================
# 6. 파일 해시 비교 (캐시 확인)
# ========================================

echo -e "${BLUE}6️⃣  파일 해시 확인${NC}"
echo "----------------------------------------"

if [ -f "public/index_v40_FINAL.html" ]; then
    hash=$(md5sum public/index_v40_FINAL.html 2>/dev/null | awk '{print $1}' || md5 -q public/index_v40_FINAL.html 2>/dev/null)
    echo "index_v40_FINAL.html: $hash"
    
    # 서버에서 받은 파일 해시
    if curl -s "http://localhost:8001/" > /tmp/served_index.html 2>/dev/null; then
        served_hash=$(md5sum /tmp/served_index.html 2>/dev/null | awk '{print $1}' || md5 -q /tmp/served_index.html 2>/dev/null)
        echo "서빙된 파일: $served_hash"
        
        if [ "$hash" = "$served_hash" ]; then
            echo -e "${GREEN}✅ 파일 일치 (캐시 문제 아님)${NC}"
        else
            echo -e "${RED}❌ 파일 불일치 (서버가 다른 파일 서빙)${NC}"
        fi
    fi
fi

echo ""

# ========================================
# 7. 최근 수정 이력
# ========================================

echo -e "${BLUE}7️⃣  최근 수정 이력${NC}"
echo "----------------------------------------"

echo "최근 수정된 v40 관련 파일:"
find . -name "*v40*.html" -o -name "*v40*.js" -o -name "main.py" 2>/dev/null | \
    xargs ls -lt 2>/dev/null | head -5

echo ""

# ========================================
# 최종 진단
# ========================================

echo "=============================================="
echo -e "${BLUE}📊 최종 진단${NC}"
echo "=============================================="

# 점수 계산
score=0

# 파일 존재
if [ -f "public/index_v40_FINAL.html" ]; then
    score=$((score + 20))
    echo -e "${GREEN}✅ 파일 존재 (+20)${NC}"
else
    echo -e "${RED}❌ 파일 없음${NC}"
fi

# 서버 실행
if [ -n "$python_procs" ]; then
    score=$((score + 30))
    echo -e "${GREEN}✅ 서버 실행 (+30)${NC}"
else
    echo -e "${RED}❌ 서버 미실행${NC}"
fi

# 라우팅 설정
if [ -f "app/main.py" ] && grep -q "index_v40" app/main.py; then
    score=$((score + 30))
    echo -e "${GREEN}✅ 라우팅 설정 (+30)${NC}"
else
    echo -e "${YELLOW}⚠️  라우팅 미설정 또는 다른 파일${NC}"
fi

# 실제 서빙
if curl -s "http://localhost:8001/" 2>/dev/null | grep -q "v40\|종합 토지분석"; then
    score=$((score + 20))
    echo -e "${GREEN}✅ v40 서빙 중 (+20)${NC}"
else
    echo -e "${YELLOW}⚠️  v40 서빙 안 됨${NC}"
fi

echo ""
echo "총점: $score/100"
echo ""

if [ $score -ge 80 ]; then
    echo -e "${GREEN}✅ 시스템 정상 - 브라우저 캐시 문제일 가능성 높음${NC}"
    echo ""
    echo "👉 해결 방법:"
    echo "   1. Ctrl+Shift+R (강제 새로고침)"
    echo "   2. 시크릿 모드로 테스트"
    echo "   3. 브라우저 캐시 완전 삭제"
elif [ $score -ge 50 ]; then
    echo -e "${YELLOW}⚠️  부분 문제 - 라우팅 또는 서버 재시작 필요${NC}"
    echo ""
    echo "👉 해결 방법:"
    echo "   1. ./fix_update_issue_complete.sh 실행"
    echo "   2. 서버 재시작"
    echo "   3. app/main.py 라우팅 확인"
else
    echo -e "${RED}❌ 심각한 문제 - 파일 또는 서버 설정 오류${NC}"
    echo ""
    echo "👉 해결 방법:"
    echo "   1. 파일 존재 확인"
    echo "   2. ./fix_update_issue_complete.sh 실행"
    echo "   3. 라우팅 설정"
fi

echo ""
echo "=============================================="
