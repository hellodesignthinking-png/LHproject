#!/bin/bash

# ========================================
# ZeroSite 4.0 Staging Deployment Script
# Date: 2025-12-27
# Version: 1.0
# ========================================

set -e  # Exit on error

echo "🚀 ZeroSite 4.0 - Staging Deployment"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
STAGING_PORT=8001
PROJECT_DIR="/home/user/webapp"
CONTEXT_ID="test-staging-001"

# Step 1: Pull latest code
echo -e "${YELLOW}[1/6] Pulling latest code...${NC}"
cd "$PROJECT_DIR"
git pull origin main
echo -e "${GREEN}✅ Code updated${NC}"
echo ""

# Step 2: Install dependencies
echo -e "${YELLOW}[2/6] Installing dependencies...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 3: Create staging environment file
echo -e "${YELLOW}[3/6] Creating staging environment...${NC}"
cat > .env.staging << 'EOF'
APP_ENV=staging
DEBUG=True
LOG_LEVEL=DEBUG
HOST=0.0.0.0
PORT=8001
EOF
echo -e "${GREEN}✅ Staging environment created${NC}"
echo ""

# Step 4: Run automated tests
echo -e "${YELLOW}[4/6] Running automated tests...${NC}"
pytest tests/test_phase35c_data_restoration.py tests/test_data_propagation.py -v --tb=short
TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed (13/13)${NC}"
else
    echo -e "${RED}❌ Tests failed! Aborting deployment.${NC}"
    exit 1
fi
echo ""

# Step 5: Start staging server
echo -e "${YELLOW}[5/6] Starting staging server on port ${STAGING_PORT}...${NC}"
echo "Server will start in background. Check logs with: pm2 logs zerosite-staging"
echo ""

# Check if PM2 is installed
if command -v pm2 &> /dev/null; then
    # Use PM2
    cat > ecosystem.staging.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'zerosite-staging',
    script: 'app/main.py',
    cwd: '/home/user/webapp',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      APP_ENV: 'staging',
      PORT: '8001',
      DEBUG: 'True',
      PYTHONUNBUFFERED: '1'
    },
    error_file: './logs/staging-error.log',
    out_file: './logs/staging-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
EOF
    
    pm2 delete zerosite-staging 2>/dev/null || true
    pm2 start ecosystem.staging.config.js
    
    echo -e "${GREEN}✅ Server started with PM2${NC}"
    echo "View logs: pm2 logs zerosite-staging"
    echo "Stop server: pm2 stop zerosite-staging"
else
    # Use direct Python (background)
    echo "PM2 not found. Starting with Python in background..."
    nohup python3 app/main.py > logs/staging-out.log 2> logs/staging-error.log &
    PYTHON_PID=$!
    echo $PYTHON_PID > /tmp/zerosite-staging.pid
    echo -e "${GREEN}✅ Server started (PID: $PYTHON_PID)${NC}"
    echo "View logs: tail -f logs/staging-out.log"
    echo "Stop server: kill \$(cat /tmp/zerosite-staging.pid)"
fi
echo ""

# Step 6: Wait for server to start
echo -e "${YELLOW}[6/6] Waiting for server to start...${NC}"
sleep 3

# Health check
HEALTH_CHECK=$(curl -s http://localhost:${STAGING_PORT}/health || echo "FAILED")

if [[ "$HEALTH_CHECK" == *"ok"* ]] || [[ "$HEALTH_CHECK" == *"healthy"* ]]; then
    echo -e "${GREEN}✅ Server is healthy!${NC}"
else
    echo -e "${RED}❌ Server health check failed!${NC}"
    echo "Response: $HEALTH_CHECK"
    exit 1
fi
echo ""

# Success message
echo "======================================"
echo -e "${GREEN}🎉 Staging Deployment Complete!${NC}"
echo "======================================"
echo ""
echo "📍 Staging URL: http://localhost:${STAGING_PORT}"
echo "📚 API Docs: http://localhost:${STAGING_PORT}/docs"
echo "🏥 Health: http://localhost:${STAGING_PORT}/health"
echo ""
echo "Next Steps:"
echo "1. Open browser: open http://localhost:${STAGING_PORT}/docs"
echo "2. Test M2 PDF: curl -o test.pdf 'http://localhost:${STAGING_PORT}/api/v4/reports/M2/pdf?context_id=${CONTEXT_ID}'"
echo "3. Visual QA: Follow STAGING_DEPLOYMENT_GUIDE.md"
echo ""
echo -e "${YELLOW}⚠️  Remember to run full Visual QA before production deployment!${NC}"
echo ""
