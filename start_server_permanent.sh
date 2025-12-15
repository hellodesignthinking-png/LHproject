#!/bin/bash

# ZeroSite v38.0 FINAL - 영구 실행 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_DIR="logs"
LOG_FILE="$LOG_DIR/server_$(date +%Y%m%d_%H%M%S).log"
PID_FILE="server.pid"

# 로그 디렉토리 생성
mkdir -p "$LOG_DIR"

# 기존 프로세스 종료
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "🔴 기존 서버 종료 (PID: $OLD_PID)"
        kill -15 "$OLD_PID"
        sleep 2
        kill -9 "$OLD_PID" 2>/dev/null
    fi
    rm -f "$PID_FILE"
fi

# 포트 확인 및 정리
PORT=8000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  포트 $PORT 사용 중, 프로세스 종료"
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

# 서버 시작
echo "🟢 서버 시작 중..."
nohup python -u -m uvicorn app.main:app --host 0.0.0.0 --port $PORT > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# PID 저장
echo "$SERVER_PID" > "$PID_FILE"

# 시작 대기
sleep 8

# 확인
if ps -p "$SERVER_PID" > /dev/null 2>&1; then
    echo "✅ 서버 실행 성공"
    echo "   PID: $SERVER_PID"
    echo "   포트: $PORT"
    echo "   로그: $LOG_FILE"
    
    # Health Check
    if curl -s http://localhost:$PORT/api/v24.1/health > /dev/null 2>&1; then
        echo "   상태: ✅ HEALTHY"
    else
        echo "   상태: ⚠️  응답 없음 (초기화 중)"
    fi
else
    echo "❌ 서버 시작 실패"
    echo "로그 확인:"
    tail -20 "$LOG_FILE"
    exit 1
fi

echo ""
echo "🎉 서버 준비 완료!"
echo ""
echo "접속 URL:"
echo "  http://localhost:$PORT"
echo ""
echo "명령어:"
echo "  중지: kill \$(cat $PID_FILE)"
echo "  로그: tail -f $LOG_FILE"
echo "  재시작: ./start_server_permanent.sh"
