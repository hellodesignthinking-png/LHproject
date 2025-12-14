#!/bin/bash

# 서버 헬스 체크

URL="http://localhost:8000/api/v24.1/health"

echo "🏥 Health Check..."
echo ""

response=$(curl -s -w "\n%{http_code}" "$URL")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo "✅ 서버 정상"
    echo "$body" | python -m json.tool 2>/dev/null || echo "$body"
else
    echo "❌ 서버 오류 (HTTP $http_code)"
    echo "$body"
    exit 1
fi

echo ""
echo "프로세스 확인:"
if [ -f "server.pid" ]; then
    PID=$(cat server.pid)
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "  PID $PID: ✅ 실행 중"
        ps -p "$PID" -o pid,vsz,rss,etime,cmd | head -2
    else
        echo "  PID $PID: ❌ 종료됨"
    fi
else
    echo "  PID 파일 없음"
fi
