#!/bin/bash
#
# ZeroSite v3.0.0 - Health Monitoring Script
# Monitors system health and sends alerts if issues detected
#

# Configuration
API_URL="http://localhost:8091"
LOG_FILE="/home/user/webapp/logs/health_monitor.log"
ALERT_EMAIL="admin@example.com"  # Configure your email
CHECK_INTERVAL=60  # Check every 60 seconds
MAX_RESPONSE_TIME=3  # Alert if response time > 3 seconds
MIN_UPTIME=300  # Alert if uptime < 5 minutes (indicates restart)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Function to send alert (email/slack/etc)
send_alert() {
    local subject="$1"
    local message="$2"
    
    log "ALERT" "$subject: $message"
    
    # Email alert (uncomment and configure)
    # echo "$message" | mail -s "$subject" "$ALERT_EMAIL"
    
    # Slack webhook (uncomment and configure)
    # curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"$subject\\n$message\"}" \
    #   YOUR_SLACK_WEBHOOK_URL
    
    # For now, just log
    echo -e "${RED}[ALERT]${NC} $subject"
}

# Function to check health endpoint
check_health() {
    local start_time=$(date +%s.%N)
    local response=$(curl -s -w "\n%{http_code}" --max-time 10 "$API_URL/health" 2>&1)
    local end_time=$(date +%s.%N)
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    
    local response_time=$(echo "$end_time - $start_time" | bc)
    
    if [ "$http_code" = "200" ]; then
        # Parse response
        local status=$(echo "$body" | jq -r '.status // "unknown"' 2>/dev/null)
        local uptime=$(echo "$body" | jq -r '.uptime_seconds // 0' 2>/dev/null)
        
        # Check status
        if [ "$status" = "healthy" ]; then
            log "INFO" "✅ Health check PASSED (${response_time}s, uptime: ${uptime}s)"
            
            # Check response time
            if (( $(echo "$response_time > $MAX_RESPONSE_TIME" | bc -l) )); then
                send_alert "⚠️  Slow Response Time" \
                    "Response time ${response_time}s exceeds threshold ${MAX_RESPONSE_TIME}s"
            fi
            
            # Check if recently restarted
            if (( $(echo "$uptime < $MIN_UPTIME" | bc -l) )); then
                log "WARN" "⚠️  Service recently restarted (uptime: ${uptime}s)"
            fi
            
            return 0
        else
            send_alert "❌ Health Status Degraded" \
                "Status: $status (expected: healthy)"
            return 1
        fi
    else
        send_alert "❌ Health Check Failed" \
            "HTTP $http_code - Service may be down"
        return 1
    fi
}

# Function to check metrics
check_metrics() {
    local response=$(curl -s "$API_URL/metrics" 2>&1)
    
    if [ $? -eq 0 ]; then
        local total=$(echo "$response" | jq -r '.total_requests // 0' 2>/dev/null)
        local success=$(echo "$response" | jq -r '.successful_requests // 0' 2>/dev/null)
        local failed=$(echo "$response" | jq -r '.failed_requests // 0' 2>/dev/null)
        local success_rate=$(echo "$response" | jq -r '.success_rate // 0' 2>/dev/null)
        local avg_time=$(echo "$response" | jq -r '.average_generation_time // 0' 2>/dev/null)
        
        log "INFO" "📊 Metrics: Total=$total, Success=$success, Failed=$failed, Rate=${success_rate}%, AvgTime=${avg_time}s"
        
        # Check for high failure rate
        if (( $(echo "$success_rate < 95" | bc -l) )) && [ "$total" -gt 10 ]; then
            send_alert "⚠️  High Failure Rate" \
                "Success rate ${success_rate}% is below 95% (total requests: $total)"
        fi
        
        # Check for slow generation times
        if (( $(echo "$avg_time > 2.0" | bc -l) )) && [ "$success" -gt 5 ]; then
            send_alert "⚠️  Slow Generation Times" \
                "Average generation time ${avg_time}s exceeds 2s threshold"
        fi
    else
        log "WARN" "⚠️  Could not fetch metrics"
    fi
}

# Function to check disk space
check_disk_space() {
    local usage=$(df -h /home/user/webapp | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -gt 80 ]; then
        send_alert "⚠️  Disk Space Low" \
            "Disk usage at ${usage}% (threshold: 80%)"
    fi
    
    log "INFO" "💾 Disk usage: ${usage}%"
}

# Function to check memory
check_memory() {
    local mem_total=$(free -m | awk 'NR==2 {print $2}')
    local mem_used=$(free -m | awk 'NR==2 {print $3}')
    local mem_pct=$((mem_used * 100 / mem_total))
    
    if [ "$mem_pct" -gt 85 ]; then
        send_alert "⚠️  High Memory Usage" \
            "Memory usage at ${mem_pct}% (${mem_used}MB/${mem_total}MB)"
    fi
    
    log "INFO" "🧠 Memory usage: ${mem_pct}% (${mem_used}MB/${mem_total}MB)"
}

# Function to check if process is running
check_process() {
    if pgrep -f "app_production.py" > /dev/null; then
        log "INFO" "✅ Process is running"
        return 0
    else
        send_alert "🚨 Process Not Running" \
            "app_production.py process is not running!"
        return 1
    fi
}

# Main monitoring loop
main() {
    log "INFO" "=========================================="
    log "INFO" "🚀 Starting ZeroSite Health Monitor"
    log "INFO" "API URL: $API_URL"
    log "INFO" "Check Interval: ${CHECK_INTERVAL}s"
    log "INFO" "=========================================="
    
    while true; do
        echo ""
        log "INFO" "--- Health Check Cycle ---"
        
        # Check if process is running
        if ! check_process; then
            log "ERROR" "Process check failed!"
            # Attempt to restart (optional)
            # cd /home/user/webapp && python app_production.py > logs/server_restart.log 2>&1 &
        fi
        
        # Check health endpoint
        check_health
        
        # Check metrics
        check_metrics
        
        # Check system resources
        check_disk_space
        check_memory
        
        log "INFO" "--- Cycle Complete ---"
        
        # Sleep until next check
        sleep $CHECK_INTERVAL
    done
}

# Handle interrupts
trap 'log "INFO" "Monitoring stopped"; exit 0' INT TERM

# Run monitor
main
