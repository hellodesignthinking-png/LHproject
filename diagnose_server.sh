#!/bin/bash

echo "🔍 ZeroSite Server Diagnostic"
echo "=============================="

# Check if server is running
echo ""
echo "1. Checking server process..."
if ps aux | grep -E "uvicorn app.main" | grep -v grep > /dev/null; then
    echo "   ✅ Server is running"
    ps aux | grep -E "uvicorn app.main" | grep -v grep
else
    echo "   ❌ Server is NOT running!"
    echo "   → Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
fi

# Check if port 8000 is listening
echo ""
echo "2. Checking port 8000..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "   ✅ Port 8000 is listening"
else
    echo "   ❌ Port 8000 is NOT listening!"
    echo "   → Server is not accessible on port 8000"
fi

# Check if latest code is present
echo ""
echo "3. Checking v7.5 FINAL code..."
if grep -q "v7_5_final" app/main.py; then
    echo "   ✅ v7.5 FINAL code found in app/main.py"
else
    echo "   ❌ v7.5 FINAL code NOT found!"
    echo "   → Pull latest code: git pull origin feature/expert-report-generator"
fi

# Check frontend configuration
echo ""
echo "4. Checking frontend configuration..."
if grep -q "report_mode: 'v7_5_final'" static/index.html; then
    echo "   ✅ Frontend configured for v7.5 FINAL"
else
    echo "   ❌ Frontend NOT configured for v7.5 FINAL!"
    echo "   → Update static/index.html line 1572"
fi

echo ""
echo "=============================="
echo "Diagnostic complete!"
