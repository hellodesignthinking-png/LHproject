#!/bin/bash

# ZeroSite v7.1 Production Deployment Script

set -e  # Exit on error

echo "========================================="
echo "🚀 ZeroSite v7.1 Production Deployment"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/user/webapp"
DEPLOY_DIR="$PROJECT_DIR/deploy"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Functions
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Pre-deployment checks
echo "📋 Pre-deployment checks..."

# Check if running as correct user
if [ "$USER" != "user" ] && [ "$USER" != "root" ]; then
    log_warn "Running as $USER (expected: user or root)"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed!"
    exit 1
fi
log_info "Docker is installed"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    log_error "docker-compose is not installed!"
    exit 1
fi
log_info "docker-compose is installed"

# Check if .env file exists
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    log_error ".env file not found in $DEPLOY_DIR"
    log_info "Please copy env.example.production to .env and configure it"
    exit 1
fi
log_info ".env file found"

# Create backup directory
mkdir -p "$BACKUP_DIR"
log_info "Backup directory ready"

# Backup current deployment (if exists)
if [ "$(docker ps -q -f name=zerosite-app)" ]; then
    echo ""
    echo "💾 Creating backup..."
    
    # Backup logs
    if [ -d "$DEPLOY_DIR/logs" ]; then
        tar -czf "$BACKUP_DIR/logs_$TIMESTAMP.tar.gz" -C "$DEPLOY_DIR" logs
        log_info "Logs backed up"
    fi
    
    # Backup data
    if [ -d "$DEPLOY_DIR/data" ]; then
        tar -czf "$BACKUP_DIR/data_$TIMESTAMP.tar.gz" -C "$DEPLOY_DIR" data
        log_info "Data backed up"
    fi
fi

# Build new image
echo ""
echo "🔨 Building Docker image..."
cd "$DEPLOY_DIR"
docker-compose -f docker-compose.production.yml build --no-cache
log_info "Docker image built successfully"

# Stop existing containers
echo ""
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.production.yml down
log_info "Containers stopped"

# Start new deployment
echo ""
echo "🚀 Starting new deployment..."
docker-compose -f docker-compose.production.yml up -d
log_info "Containers started"

# Wait for health check
echo ""
echo "🏥 Waiting for health check..."
sleep 10

# Check health
MAX_RETRIES=12
RETRY_COUNT=0
HEALTH_OK=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker exec zerosite-app curl -f http://localhost:8000/health > /dev/null 2>&1; then
        HEALTH_OK=true
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Attempt $RETRY_COUNT/$MAX_RETRIES..."
    sleep 5
done

if [ "$HEALTH_OK" = true ]; then
    log_info "Health check passed!"
else
    log_error "Health check failed!"
    log_error "Rolling back..."
    
    # Rollback
    docker-compose -f docker-compose.production.yml down
    exit 1
fi

# Show status
echo ""
echo "📊 Deployment Status:"
docker-compose -f docker-compose.production.yml ps

# Show logs
echo ""
echo "📝 Recent logs:"
docker-compose -f docker-compose.production.yml logs --tail=20

echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""
echo "🌐 Application: http://localhost:8000"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "📚 Useful commands:"
echo "  View logs:    docker-compose -f deploy/docker-compose.production.yml logs -f"
echo "  Stop:         docker-compose -f deploy/docker-compose.production.yml down"
echo "  Restart:      docker-compose -f deploy/docker-compose.production.yml restart"
echo ""
