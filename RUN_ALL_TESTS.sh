#!/bin/bash
# Run All v3.2 Tests Script

echo "🧪 Running All v3.2 Tests"
echo "======================================"

cd /home/user/webapp

# Run tests and capture output
python3 tests/test_v32_complete.py 2>&1 | tee TEST_RESULTS.log

# Parse results
TOTAL=$(grep -oP "Total Tests: \K\d+" TEST_RESULTS.log 2>/dev/null || echo "0")
ASSERTIONS=$(grep -oP "Total Assertions: \K\d+" TEST_RESULTS.log 2>/dev/null || echo "0")
PASSED=$(grep -oP "✅ Passed: \K\d+" TEST_RESULTS.log 2>/dev/null || echo "0")
FAILED=$(grep -oP "❌ Failed: \K\d+" TEST_RESULTS.log 2>/dev/null || echo "0")

# Calculate percentage
if [ -n "$ASSERTIONS" ] && [ "$ASSERTIONS" -gt 0 ]; then
    PASS_RATE=$(echo "scale=1; $PASSED * 100 / $ASSERTIONS" | bc 2>/dev/null || echo "?")
    echo ""
    echo "======================================"
    echo "📊 Test Results Summary"
    echo "======================================"
    echo "Total Tests: $TOTAL"
    echo "Total Assertions: $ASSERTIONS"
    echo "Passed: $PASSED"
    echo "Failed: $FAILED"
    echo "Pass Rate: $PASS_RATE%"
    echo "======================================"
else
    echo "❌ Could not parse test results"
fi

# Save to file
cat > TEST_SUMMARY.md << EOF
# Test Results ($(date))

## Summary
- Total Tests: $TOTAL
- Total Assertions: $ASSERTIONS
- Passed: $PASSED
- Failed: $FAILED
- Pass Rate: $PASS_RATE%

## Status
$(if [ "$FAILED" -eq 0 ]; then echo "✅ ALL TESTS PASSED"; else echo "⚠️  Some tests failed (see details below)"; fi)

## Full Log
See TEST_RESULTS.log for complete output
EOF

echo "✅ Results saved to TEST_SUMMARY.md and TEST_RESULTS.log"
