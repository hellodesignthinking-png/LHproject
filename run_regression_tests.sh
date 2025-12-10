#!/bin/bash
# ZeroSite v23 Regression Test Runner
# Local test execution script

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 ZeroSite v23 Regression Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo ""
    echo "▶ Running: $test_name"
    echo "─────────────────────────────────────────────────────"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test 1: Ground Truth Verification
run_test "Ground Truth Verification" \
    "python test_ground_truth_verification.py > test_results.log 2>&1 && cat test_results.log"

# Test 2: V23 Improvements
run_test "V23 Improvements Tests" \
    "python test_v23_improvements.py > v23_test_results.log 2>&1 && cat v23_test_results.log"

# Test 3: Sensitivity Analysis Module
run_test "Sensitivity Analysis Module" \
    "python -c 'from app.services_v13.sensitivity_analysis import SensitivityAnalyzer; \
     analyzer = SensitivityAnalyzer(); \
     result = analyzer.analyze_comprehensive(30000000000, 0.92, 24200000000, 2200); \
     assert len(result[\"scenarios\"]) == 9; \
     assert result[\"summary\"][\"go_count\"] == 3; \
     print(\"✓ Sensitivity Analysis OK\")'"

# Test 4: Dynamic CAPEX Calculator
run_test "Dynamic CAPEX Calculator" \
    "python -c 'from app.services_v13.dynamic_capex_calculator import DynamicCapexCalculator; \
     calc = DynamicCapexCalculator(); \
     result = calc.calculate_dynamic_land_cost(24200000000, 30000000000); \
     assert result[\"land_cost_eok\"] == 150.0; \
     print(\"✓ Dynamic CAPEX OK\")'"

# Test 5: Data Validation Summary Exists
run_test "Data Validation Summary" \
    "test -f v23_data_validation_summary.md && grep -q '검증 완료' v23_data_validation_summary.md && echo '✓ Validation summary OK'"

# Test 6: Python Syntax Check
run_test "Python Syntax Check" \
    "python -m py_compile app/services_v13/sensitivity_analysis.py && \
     python -m py_compile app/services_v13/dynamic_capex_calculator.py && \
     python -m py_compile app/services_v13/land_trade_api.py && \
     echo '✓ Syntax check OK'"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
