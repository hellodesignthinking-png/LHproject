#!/bin/bash

echo "🚀 LH 토지진단 시스템 서버 시작"
echo "================================"
echo ""

# 가상환경 활성화 (존재하는 경우)
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source venv/bin/activate
fi

# 환경 변수 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사하세요."
    exit 1
fi

echo "✅ 환경 설정 완료"
echo ""
echo "🌐 서버 실행 중..."
echo "   - API 문서: http://localhost:8000/docs"
echo "   - 헬스체크: http://localhost:8000/health"
echo ""
echo "종료하려면 Ctrl+C를 누르세요"
echo ""

# 서버 실행
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
