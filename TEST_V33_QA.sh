#!/bin/bash

################################################################################
# ZeroSite v3.3 Quality Assurance Test Script
################################################################################
# Tests all aspects of PDF generation, accessibility, and quality
# Author: ZeroSite v3.3 Development Team
# Date: 2025-12-12
# Version: 3.3.0
################################################################################

echo ""
echo "================================================================================"
echo "🧪 ZeroSite v3.3 - COMPREHENSIVE QA TEST SUITE"
echo "================================================================================"
echo ""

# Configuration
BASE_URL="http://localhost:8041"
PUBLIC_URL="https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
pass_test() {
    ((TOTAL_TESTS++))
    ((PASSED_TESTS++))
    echo -e "${GREEN}✅ PASS${NC}: $1"
}

fail_test() {
    ((TOTAL_TESTS++))
    ((FAILED_TESTS++))
    echo -e "${RED}❌ FAIL${NC}: $1"
}

info() {
    echo -e "${YELLOW}ℹ️  INFO${NC}: $1"
}

section() {
    echo ""
    echo "────────────────────────────────────────────────────────────────────────────"
    echo "📋 $1"
    echo "────────────────────────────────────────────────────────────────────────────"
}

################################################################################
# Test 1: Server Health Check
################################################################################
section "Test 1: Server Health Check"

HEALTH_RESPONSE=$(curl -s ${BASE_URL}/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    pass_test "Server is running and healthy"
    VERSION=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])" 2>/dev/null)
    info "Server version: $VERSION"
else
    fail_test "Server health check failed"
fi

################################################################################
# Test 2: v3.3 API Endpoint Test
################################################################################
section "Test 2: Expert v3.3 Report Generation"

info "Generating test report for Gangnam..."
API_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v3.2/generate-expert-report" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_area_sqm": 1650.0,
    "bcr_legal": 50.0,
    "far_legal": 300.0
  }')

# Check if response contains required fields
if echo "$API_RESPONSE" | grep -q "pdf_url"; then
    pass_test "API returned pdf_url field"
else
    fail_test "API response missing pdf_url field"
fi

if echo "$API_RESPONSE" | grep -q "3.3.0"; then
    pass_test "API reports version 3.3.0"
else
    fail_test "API version incorrect"
fi

# Extract URLs from response
HTML_URL=$(echo "$API_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['report_url'])" 2>/dev/null)
PDF_URL=$(echo "$API_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['pdf_url'])" 2>/dev/null)
PDF_SIZE=$(echo "$API_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['pdf_size_kb'])" 2>/dev/null)

info "HTML URL: $HTML_URL"
info "PDF URL: $PDF_URL"
info "PDF Size: ${PDF_SIZE}KB"

################################################################################
# Test 3: PDF File Validation
################################################################################
section "Test 3: PDF File Quality Validation"

# Extract filename from URL
PDF_FILENAME=$(basename "$PDF_URL")
PDF_PATH="public/reports/$PDF_FILENAME"

if [ -f "$PDF_PATH" ]; then
    pass_test "PDF file exists on disk"
    
    # Check file size
    ACTUAL_SIZE=$(stat -c%s "$PDF_PATH" 2>/dev/null || stat -f%z "$PDF_PATH" 2>/dev/null)
    ACTUAL_SIZE_KB=$((ACTUAL_SIZE / 1024))
    info "Actual PDF size: ${ACTUAL_SIZE_KB}KB"
    
    if [ $ACTUAL_SIZE_KB -gt 20 ] && [ $ACTUAL_SIZE_KB -lt 500 ]; then
        pass_test "PDF size is within expected range (20-500 KB)"
    else
        fail_test "PDF size out of range: ${ACTUAL_SIZE_KB}KB"
    fi
    
    # Check if it's a valid PDF
    FILE_TYPE=$(file "$PDF_PATH" | grep -o "PDF document")
    if [ -n "$FILE_TYPE" ]; then
        pass_test "File is a valid PDF document"
    else
        fail_test "File is not a valid PDF"
    fi
else
    fail_test "PDF file not found: $PDF_PATH"
fi

################################################################################
# Test 4: Public URL Accessibility
################################################################################
section "Test 4: Public URL Accessibility"

# Replace localhost with public URL
PUBLIC_PDF_URL="${PDF_URL/http:\/\/localhost:8041/$PUBLIC_URL}"
info "Testing public URL: $PUBLIC_PDF_URL"

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PUBLIC_PDF_URL")

if [ "$HTTP_STATUS" = "200" ]; then
    pass_test "PDF is publicly accessible (HTTP 200)"
else
    fail_test "PDF not accessible (HTTP $HTTP_STATUS)"
fi

# Check Content-Type header
CONTENT_TYPE=$(curl -s -I "$PUBLIC_PDF_URL" | grep -i "content-type" | awk '{print $2}' | tr -d '\r')

if echo "$CONTENT_TYPE" | grep -q "application/pdf"; then
    pass_test "PDF served with correct Content-Type"
else
    fail_test "Incorrect Content-Type: $CONTENT_TYPE"
fi

################################################################################
# Test 5: Multiple Scenarios Test
################################################################################
section "Test 5: Multiple Scenario Generation"

# Test scenario 2: Mapo
info "Generating report for Mapo..."
MAPO_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v3.2/generate-expert-report" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 마포구 월드컵북로 120",
    "land_area_sqm": 660.0,
    "bcr_legal": 50.0,
    "far_legal": 300.0
  }')

if echo "$MAPO_RESPONSE" | grep -q "success"; then
    pass_test "Mapo scenario generated successfully"
else
    fail_test "Mapo scenario generation failed"
fi

# Test scenario 3: Nowon
info "Generating report for Nowon..."
NOWON_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v3.2/generate-expert-report" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 노원구 상계동 567-89",
    "land_area_sqm": 990.0,
    "bcr_legal": 60.0,
    "far_legal": 250.0
  }')

if echo "$NOWON_RESPONSE" | grep -q "success"; then
    pass_test "Nowon scenario generated successfully"
else
    fail_test "Nowon scenario generation failed"
fi

################################################################################
# Test 6: API Response Validation
################################################################################
section "Test 6: API Response Structure Validation"

# Check all required fields are present
REQUIRED_FIELDS=("status" "report_url" "pdf_url" "generation_time" "file_size_kb" "pdf_size_kb" "version" "sections_included" "recommended_scenario")

for field in "${REQUIRED_FIELDS[@]}"; do
    if echo "$API_RESPONSE" | grep -q "\"$field\""; then
        pass_test "Field '$field' present in response"
    else
        fail_test "Field '$field' missing from response"
    fi
done

################################################################################
# Test 7: Generation Performance
################################################################################
section "Test 7: Performance Metrics"

GEN_TIME=$(echo "$API_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['generation_time'])" 2>/dev/null)

info "Generation time: ${GEN_TIME}s"

if [ $(echo "$GEN_TIME < 5.0" | bc) -eq 1 ]; then
    pass_test "Generation time under 5 seconds"
else
    fail_test "Generation time too slow: ${GEN_TIME}s"
fi

################################################################################
# Test 8: Report Count
################################################################################
section "Test 8: Generated Reports Summary"

HTML_COUNT=$(ls -1 public/reports/*.html 2>/dev/null | wc -l)
PDF_COUNT=$(ls -1 public/reports/*.pdf 2>/dev/null | wc -l)

info "Total HTML reports: $HTML_COUNT"
info "Total PDF reports: $PDF_COUNT"

if [ $PDF_COUNT -ge 1 ]; then
    pass_test "At least one PDF report generated"
else
    fail_test "No PDF reports found"
fi

if [ $HTML_COUNT -ge 1 ]; then
    pass_test "At least one HTML report generated"
else
    fail_test "No HTML reports found"
fi

################################################################################
# Final Summary
################################################################################
echo ""
echo "================================================================================"
echo "📊 TEST SUMMARY"
echo "================================================================================"
echo ""
echo "Total Tests:  $TOTAL_TESTS"
echo -e "${GREEN}Passed:       $PASSED_TESTS${NC}"

if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}Failed:       $FAILED_TESTS${NC}"
else
    echo "Failed:       $FAILED_TESTS"
fi

echo ""
PASS_RATE=$(echo "scale=1; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)
echo "Pass Rate:    ${PASS_RATE}%"

echo ""
echo "================================================================================"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED - ZEROSITE V3.3 IS PRODUCTION READY${NC}"
    echo "================================================================================"
    echo ""
    echo "🌐 PUBLIC PDF URL (Latest Test):"
    echo "$PUBLIC_PDF_URL"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED - REVIEW REQUIRED${NC}"
    echo "================================================================================"
    exit 1
fi
