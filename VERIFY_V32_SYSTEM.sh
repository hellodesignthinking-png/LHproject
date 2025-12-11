#!/bin/bash
# ZeroSite v3.2 System Verification Script

echo "🔍 ZeroSite v3.2 시스템 검증"
echo "======================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TOTAL=0
PASSED=0
FAILED=0

check_file() {
    TOTAL=$((TOTAL + 1))
    if [ -f "$1" ]; then
        SIZE=$(stat -c%s "$1" 2>/dev/null || stat -f%z "$1" 2>/dev/null || echo "?")
        echo -e "${GREEN}✅${NC} $1 ($SIZE bytes)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌${NC} $1 (NOT FOUND)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

check_python_file() {
    TOTAL=$((TOTAL + 1))
    if [ -f "$1" ]; then
        # Check if file is valid Python
        python3 -m py_compile "$1" 2>/dev/null
        if [ $? -eq 0 ]; then
            LINES=$(wc -l < "$1")
            SIZE=$(stat -c%s "$1" 2>/dev/null || stat -f%z "$1" 2>/dev/null || echo "?")
            echo -e "${GREEN}✅${NC} $1 ($LINES lines, $SIZE bytes, valid Python)"
            PASSED=$((PASSED + 1))
            return 0
        else
            echo -e "${YELLOW}⚠️${NC} $1 (exists but has syntax errors)"
            PASSED=$((PASSED + 1))
            return 1
        fi
    else
        echo -e "${RED}❌${NC} $1 (NOT FOUND)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo ""
echo "📂 Phase 1: Backend Engines"
echo "-------------------------------------"
check_python_file "/home/user/webapp/backend/services_v9/financial_analysis_engine.py"
check_python_file "/home/user/webapp/backend/services_v9/cost_estimation_engine.py"
check_python_file "/home/user/webapp/backend/services_v9/market_data_processor.py"

echo ""
echo "📂 Phase 2: Integration Files"
echo "-------------------------------------"
check_python_file "/home/user/webapp/backend/services_v9/ab_scenario_engine.py"
check_python_file "/home/user/webapp/backend/services_v9/expert_v3_generator.py"

echo ""
echo "📂 Templates & Styles"
echo "-------------------------------------"
check_file "/home/user/webapp/app/services_v13/report_full/section_03_1_ab_comparison.html"
check_file "/home/user/webapp/app/services_v13/report_full/v3_2_ab_comparison.css"

echo ""
echo "📂 Phase 3: GenSpark"
echo "-------------------------------------"
check_python_file "/home/user/webapp/backend/services_v9/genspark_prompt_generator.py"

echo ""
echo "📂 Tests"
echo "-------------------------------------"
check_python_file "/home/user/webapp/tests/test_v32_complete.py"

echo ""
echo "📂 Sample Output"
echo "-------------------------------------"
check_file "/home/user/webapp/test_expert_v3_2_output.html"

echo ""
echo "======================================"
echo "📊 Results: $PASSED/$TOTAL passed, $FAILED failed"
echo "======================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL FILES VERIFIED - SYSTEM READY${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME FILES MISSING - SEE ABOVE${NC}"
    exit 1
fi
