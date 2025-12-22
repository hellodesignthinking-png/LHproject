#!/bin/bash

# ============================================================================
# Backend Restart Script - M1 v2.0
# ============================================================================
# Purpose: Quick script to restart backend with updated .env configuration
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

WORK_DIR="/home/user/webapp"

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ZeroSite M1 v2.0 - Backend Restart${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Step 1: Kill existing backend
echo -e "${YELLOW}[1/4]${NC} Stopping existing backend..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ Backend stopped${NC}"
echo ""

# Step 2: Verify .env exists
echo -e "${YELLOW}[2/4]${NC} Checking .env configuration..."
if [ ! -f "$WORK_DIR/.env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi

# Show current API key status
KAKAO_KEY=$(grep "^KAKAO_REST_API_KEY=" "$WORK_DIR/.env" | cut -d'=' -f2-)
VWORLD_KEY=$(grep "^VWORLD_API_KEY=" "$WORK_DIR/.env" | cut -d'=' -f2-)

echo "Current API Keys:"
echo "  Kakao:  ${KAKAO_KEY:0:16}..."
echo "  VWorld: ${VWORLD_KEY:0:16}..."
echo -e "${GREEN}✅ .env file loaded${NC}"
echo ""

# Step 3: Activate virtualenv and start backend
echo -e "${YELLOW}[3/4]${NC} Starting backend service..."
cd "$WORK_DIR"

if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo ""

# Step 4: Wait and test health
echo -e "${YELLOW}[4/4]${NC} Testing backend health..."
sleep 5

for i in {1..6}; do
    if curl -s http://localhost:8000/api/m1/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy!${NC}"
        echo ""
        
        # Show health details
        echo "Health Check Response:"
        curl -s http://localhost:8000/api/m1/health | python3 -m json.tool
        echo ""
        
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  Backend Ready!${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "🌐 Backend URL: http://localhost:8000"
        echo "📚 API Docs: http://localhost:8000/docs"
        echo "📊 Health: http://localhost:8000/api/m1/health"
        echo "📝 Logs: tail -f backend.log"
        echo ""
        exit 0
    fi
    echo "Waiting for backend to start... ($i/6)"
    sleep 2
done

echo -e "${RED}❌ Backend health check failed after 15 seconds${NC}"
echo "Check logs: tail -f backend.log"
exit 1
