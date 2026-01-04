#!/bin/bash
# Backend Restart Script
# Kills old backend and starts new one with correct module path

echo "🔄 Restarting backend..."

# Kill existing backend
pkill -9 -f "uvicorn.*49999" 2>/dev/null || echo "No existing backend process"

# Wait for port to be released
sleep 2

# Start new backend with correct module path
cd /home/user/webapp
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 49999 --reload > /tmp/backend.log 2>&1 &

PID=$!
echo "✅ Backend started with PID: $PID"
echo "📝 Logs: /tmp/backend.log"

# Wait for startup
sleep 5

# Check if running
if ps -p $PID > /dev/null; then
    echo "✅ Backend is running on http://localhost:49999"
    echo "📚 API Docs: http://localhost:49999/docs"
else
    echo "❌ Backend failed to start. Check logs:"
    tail -20 /tmp/backend.log
    exit 1
fi
