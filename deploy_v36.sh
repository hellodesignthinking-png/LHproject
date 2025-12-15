#!/bin/bash

echo "=================================="
echo "ZeroSite v36.0 NATIONWIDE"
echo "FORCE DEPLOYMENT"
echo "=================================="
echo ""

# Step 1: Kill existing processes
echo "Step 1: Stopping all Python processes..."
pkill -9 -f "python.*v24_1_server" || true
pkill -9 -f "python.*uvicorn.*app.main" || true
sleep 2
echo "✅ Processes stopped"
echo ""

# Step 2: Clear all Python cache
echo "Step 2: Clearing Python cache..."
find /home/user/webapp -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /home/user/webapp -type f -name "*.pyc" -delete 2>/dev/null || true
find /home/user/webapp -type f -name "*.pyo" -delete 2>/dev/null || true
echo "✅ Cache cleared"
echo ""

# Step 3: Restart server
echo "Step 3: Starting v36.0 server..."
cd /home/user/webapp
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server_v36.log 2>&1 &
SERVER_PID=$!
echo "✅ Server started (PID: $SERVER_PID)"
echo ""

# Step 4: Wait for server to be ready
echo "Step 4: Waiting for server to be ready..."
sleep 8
echo ""

# Step 5: Health check
echo "Step 5: Health check..."
HEALTH=$(curl -s http://localhost:8000/api/v24.1/health)
echo "$HEALTH"
echo ""

if echo "$HEALTH" | grep -q "healthy"; then
    echo "=================================="
    echo "✅ v36.0 DEPLOYMENT SUCCESS!"
    echo "=================================="
    echo ""
    echo "Server is running at: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo ""
    echo "Run nationwide tests:"
    echo "  ./test_nationwide_v36.sh"
    echo ""
else
    echo "=================================="
    echo "❌ DEPLOYMENT FAILED"
    echo "=================================="
    echo ""
    echo "Check logs:"
    echo "  tail -50 server_v36.log"
    echo ""
    exit 1
fi
