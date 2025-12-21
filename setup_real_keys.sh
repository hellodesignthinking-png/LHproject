#!/bin/bash

# ============================================================================
# ZeroSite M1 v2.0 - Real API Keys Setup Script
# ============================================================================
# Created: 2025-12-17
# Purpose: Interactive script to configure production API keys
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Working directory
WORK_DIR="/home/user/webapp"
ENV_FILE="${WORK_DIR}/.env"
ENV_BACKUP="${WORK_DIR}/.env.backup.$(date +%Y%m%d_%H%M%S)"

echo -e "${CYAN}============================================================================${NC}"
echo -e "${CYAN}  ZeroSite M1 v2.0 - Real API Keys Setup${NC}"
echo -e "${CYAN}============================================================================${NC}"
echo ""

# Function to print step headers
print_step() {
    echo -e "${BLUE}[STEP $1]${NC} ${GREEN}$2${NC}"
}

# Function to print info
print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    print_error ".env file not found at: $ENV_FILE"
    exit 1
fi

# Backup current .env
print_step "1" "Backing up current .env file"
cp "$ENV_FILE" "$ENV_BACKUP"
print_success "Backup created: $ENV_BACKUP"
echo ""

# Read current keys
print_step "2" "Checking current API key status"
echo ""

KAKAO_KEY=$(grep "^KAKAO_REST_API_KEY=" "$ENV_FILE" | cut -d'=' -f2-)
VWORLD_KEY=$(grep "^VWORLD_API_KEY=" "$ENV_FILE" | cut -d'=' -f2-)
DATA_KEY=$(grep "^DATA_GO_KR_API_KEY=" "$ENV_FILE" | cut -d'=' -f2-)

echo "Current Keys:"
echo "---------------------------------------------------"
printf "Kakao REST API:  %-40s" "$KAKAO_KEY"
if [[ "$KAKAO_KEY" == *"test"* ]] || [[ "$KAKAO_KEY" == *"your"* ]]; then
    echo -e "${RED}[MOCK]${NC}"
else
    echo -e "${GREEN}[CONFIGURED]${NC}"
fi

printf "VWorld API:      %-40s" "$VWORLD_KEY"
if [[ "$VWORLD_KEY" == *"test"* ]] || [[ "$VWORLD_KEY" == *"your"* ]]; then
    echo -e "${RED}[MOCK]${NC}"
else
    echo -e "${GREEN}[CONFIGURED]${NC}"
fi

printf "Data.go.kr API:  %-40s" "$DATA_KEY"
if [[ "$DATA_KEY" == *"test"* ]] || [[ "$DATA_KEY" == *"your"* ]]; then
    echo -e "${RED}[MOCK]${NC}"
else
    echo -e "${GREEN}[CONFIGURED]${NC}"
fi
echo "---------------------------------------------------"
echo ""

# Ask user if they want to update keys
print_step "3" "API Key Configuration"
echo ""

read -p "$(echo -e ${CYAN}"Do you want to update API keys now? (y/n): "${NC})" -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Skipping API key update. You can manually edit .env later."
    echo ""
    echo -e "${YELLOW}To manually update keys:${NC}"
    echo "  1. Open .env file: nano $ENV_FILE"
    echo "  2. Replace placeholder values with your real API keys"
    echo "  3. Save and exit (Ctrl+X, then Y, then Enter)"
    echo "  4. Restart backend: ./restart_backend.sh"
    exit 0
fi

echo ""
print_info "Please enter your API keys. Press Enter to skip any key."
print_info "Refer to REAL_API_KEYS_SETUP_GUIDE.md for obtaining keys."
echo ""

# Kakao API Key
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🔑 Kakao REST API Key${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Purpose: Address search & Geocoding (CRITICAL)"
echo "Get it from: https://developers.kakao.com/"
echo "Current: $KAKAO_KEY"
echo ""
read -p "Enter Kakao REST API Key (or press Enter to skip): " NEW_KAKAO_KEY
if [ ! -z "$NEW_KAKAO_KEY" ]; then
    # Validate format (32 characters alphanumeric)
    if [[ ${#NEW_KAKAO_KEY} -eq 32 ]]; then
        KAKAO_KEY="$NEW_KAKAO_KEY"
        print_success "Kakao API key updated"
    else
        print_error "Invalid Kakao key format (should be 32 characters). Skipping."
    fi
else
    print_info "Keeping existing Kakao key"
fi
echo ""

# VWorld API Key
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🔑 VWorld API Key${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Purpose: Cadastral data & Land use regulations (CRITICAL)"
echo "Get it from: http://www.vworld.kr/"
echo "Current: $VWORLD_KEY"
echo ""
read -p "Enter VWorld API Key (or press Enter to skip): " NEW_VWORLD_KEY
if [ ! -z "$NEW_VWORLD_KEY" ]; then
    VWORLD_KEY="$NEW_VWORLD_KEY"
    print_success "VWorld API key updated"
else
    print_info "Keeping existing VWorld key"
fi
echo ""

# Data.go.kr API Key
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🔑 Data.go.kr API Key${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Purpose: Market data & Transaction history (Important)"
echo "Get it from: https://www.data.go.kr/"
echo "Current: $DATA_KEY"
echo ""
read -p "Enter Data.go.kr API Key (or press Enter to skip): " NEW_DATA_KEY
if [ ! -z "$NEW_DATA_KEY" ]; then
    DATA_KEY="$NEW_DATA_KEY"
    print_success "Data.go.kr API key updated"
else
    print_info "Keeping existing Data.go.kr key"
fi
echo ""

# Update .env file
print_step "4" "Updating .env file"
echo ""

# Use sed to update keys
sed -i "s|^KAKAO_REST_API_KEY=.*|KAKAO_REST_API_KEY=$KAKAO_KEY|" "$ENV_FILE"
sed -i "s|^VWORLD_API_KEY=.*|VWORLD_API_KEY=$VWORLD_KEY|" "$ENV_FILE"
sed -i "s|^LAND_REGULATION_API_KEY=.*|LAND_REGULATION_API_KEY=$VWORLD_KEY|" "$ENV_FILE"
sed -i "s|^LAND_USE_REGULATION_API_KEY=.*|LAND_USE_REGULATION_API_KEY=$VWORLD_KEY|" "$ENV_FILE"
sed -i "s|^BUILDING_REGISTRY_API_KEY=.*|BUILDING_REGISTRY_API_KEY=$VWORLD_KEY|" "$ENV_FILE"
sed -i "s|^DATA_GO_KR_API_KEY=.*|DATA_GO_KR_API_KEY=$DATA_KEY|" "$ENV_FILE"
sed -i "s|^MOIS_API_KEY=.*|MOIS_API_KEY=$DATA_KEY|" "$ENV_FILE"

print_success ".env file updated successfully"
echo ""

# Show updated status
print_step "5" "Updated API Key Status"
echo ""
echo "Updated Keys:"
echo "---------------------------------------------------"
printf "Kakao REST API:  %-40s" "$KAKAO_KEY"
if [[ "$KAKAO_KEY" == *"test"* ]] || [[ "$KAKAO_KEY" == *"your"* ]]; then
    echo -e "${RED}[MOCK]${NC}"
else
    echo -e "${GREEN}[REAL KEY]${NC}"
fi

printf "VWorld API:      %-40s" "$VWORLD_KEY"
if [[ "$VWORLD_KEY" == *"test"* ]] || [[ "$VWORLD_KEY" == *"your"* ]]; then
    echo -e "${RED}[MOCK]${NC}"
else
    echo -e "${GREEN}[REAL KEY]${NC}"
fi

printf "Data.go.kr API:  %-40s" "$DATA_KEY"
if [[ "$DATA_KEY" == *"test"* ]] || [[ "$DATA_KEY" == *"your"* ]]; then
    echo -e "${RED}[MOCK]${NC}"
else
    echo -e "${GREEN}[REAL KEY]${NC}"
fi
echo "---------------------------------------------------"
echo ""

# Ask to restart backend
print_step "6" "Restart Backend Service"
echo ""

read -p "$(echo -e ${CYAN}"Do you want to restart the backend now? (y/n): "${NC})" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Restarting backend with new API keys..."
    echo ""
    
    # Kill existing backend
    print_info "Stopping existing backend..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
    
    # Start backend
    print_info "Starting backend..."
    cd "$WORK_DIR"
    source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
    BACKEND_PID=$!
    
    print_success "Backend started with PID: $BACKEND_PID"
    echo ""
    
    # Wait for backend to start
    print_info "Waiting for backend to initialize (10 seconds)..."
    sleep 10
    
    # Test health endpoint
    print_info "Testing backend health..."
    if curl -s http://localhost:8000/api/m1/health > /dev/null 2>&1; then
        print_success "Backend is healthy!"
    else
        print_error "Backend health check failed. Check backend.log for details."
    fi
    echo ""
else
    print_info "Backend not restarted. To restart manually:"
    echo "  cd $WORK_DIR && ./restart_backend.sh"
    echo ""
fi

# Test API keys
print_step "7" "Testing API Keys (Optional)"
echo ""

read -p "$(echo -e ${CYAN}"Do you want to test API keys now? (y/n): "${NC})" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    print_info "Testing address search with real API..."
    
    RESPONSE=$(curl -s -X POST http://localhost:8000/api/m1/address/search \
        -H "Content-Type: application/json" \
        -d '{"query": "서울특별시 강남구 테헤란로 521"}')
    
    # Check if response contains success
    if echo "$RESPONSE" | grep -q '"success":true' && echo "$RESPONSE" | grep -q "suggestions"; then
        print_success "Address search API test PASSED!"
        echo ""
        echo "Response preview:"
        echo "$RESPONSE" | python3 -m json.tool | head -20
    else
        print_error "Address search API test FAILED!"
        echo "Response:"
        echo "$RESPONSE" | python3 -m json.tool
    fi
    echo ""
else
    print_info "Skipping API tests. You can test manually later."
    echo ""
fi

# Final summary
echo -e "${CYAN}============================================================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${CYAN}============================================================================${NC}"
echo ""
echo -e "${GREEN}✅ Next Steps:${NC}"
echo ""
echo "1. Test individual endpoints:"
echo "   curl -X POST http://localhost:8000/api/m1/address/search \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"query\": \"서울특별시 강남구 테헤란로 521\"}'"
echo ""
echo "2. Test unified data collection:"
echo "   curl -X POST http://localhost:8000/api/m1/collect-all \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"address\": \"서울특별시 강남구 테헤란로 521\", \"lat\": 37.501, \"lon\": 127.039}'"
echo ""
echo "3. Test full M1 flow in frontend:"
echo "   https://3001-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/pipeline"
echo ""
echo -e "${YELLOW}📚 Documentation:${NC}"
echo "   - Setup guide: $WORK_DIR/REAL_API_KEYS_SETUP_GUIDE.md"
echo "   - Backup file: $ENV_BACKUP"
echo "   - Backend logs: $WORK_DIR/backend.log"
echo ""
echo -e "${GREEN}🎉 Happy testing with real API data!${NC}"
echo ""
