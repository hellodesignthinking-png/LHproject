#!/bin/bash

echo "🔄 Restarting API Server with Complete Data Fix..."

# Kill existing server
pkill -f "uvicorn.*main:app" 2>/dev/null || true
sleep 2

# Start server in background
cd /home/user/webapp
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload > api_server.log 2>&1 &

sleep 3

# Check if server started
if ps aux | grep -v grep | grep "uvicorn.*main:app" > /dev/null; then
    echo "✅ API Server started successfully"
    echo "📝 Log file: /home/user/webapp/api_server.log"
    echo "🌐 Listening on: http://0.0.0.0:8005"
    echo ""
    echo "Test URL:"
    echo "http://localhost:8005/api/v4/reports/final/all_in_one/html?context_id=116801010001230045"
else
    echo "❌ Failed to start API server"
    echo "Check logs: tail -f /home/user/webapp/api_server.log"
    exit 1
fi
