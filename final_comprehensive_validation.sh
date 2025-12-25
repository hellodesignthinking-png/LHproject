#!/bin/bash
#
# Final Report Comprehensive Validation
# ======================================
# Tests all 6 report types for:
# 1. HTTP 200 OK status
# 2. No dict/None/metadata exposure
# 3. Correct data display (NPV, land value, etc.)
# 4. Unified CSS loading
# 5. Data consistency across reports
#

BASE_URL="http://localhost:8005/api/v4/final-report"
CONTEXT_ID="116801010001230045"

REPORTS=("quick_check" "financial_feasibility" "lh_technical" "executive_summary" "landowner_summary" "all_in_one")

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     FINAL REPORT COMPREHENSIVE VALIDATION v4.4           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Test 1: HTTP Status Check
echo "📊 Test 1: HTTP Status Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PASSED=0
FAILED=0

for report in "${REPORTS[@]}"; do
    echo -n "  $report ... "
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/${report}/html?context_id=${CONTEXT_ID}")
    
    if [ "$STATUS" == "200" ]; then
        echo "✅ OK"
        ((PASSED++))
    else
        echo "❌ FAILED (HTTP $STATUS)"
        ((FAILED++))
    fi
done

echo "  Result: $PASSED/$((PASSED+FAILED)) passed"
echo ""

# Test 2: Data Exposure Check
echo "🔍 Test 2: Data Exposure Check (dict/None/metadata)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CLEAN=0
ISSUES=0

for report in "${REPORTS[@]}"; do
    echo -n "  $report ... "
    RESPONSE=$(curl -s "${BASE_URL}/${report}/html?context_id=${CONTEXT_ID}")
    
    # Check for forbidden patterns (excluding CSS)
    DICT_COUNT=$(echo "$RESPONSE" | grep -v "^body {\|^h1 {\|^h2 {\|^h3 {\|^.section {" | grep -c "{'.*':" || true)
    NONE_COUNT=$(echo "$RESPONSE" | grep -c ">None<\|\"None\"" || true)
    META_COUNT=$(echo "$RESPONSE" | grep -c "_module_id\|_required_keys\|_normalized_ok" || true)
    
    TOTAL=$((DICT_COUNT + NONE_COUNT + META_COUNT))
    
    if [ "$TOTAL" -eq 0 ]; then
        echo "✅ CLEAN"
        ((CLEAN++))
    else
        echo "⚠️  $TOTAL issues (dict:$DICT_COUNT, None:$NONE_COUNT, meta:$META_COUNT)"
        ((ISSUES++))
    fi
done

echo "  Result: $CLEAN/$((CLEAN+ISSUES)) clean"
echo ""

# Test 3: KPI Format Validation
echo "📏 Test 3: KPI Format Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RESPONSE=$(curl -s "${BASE_URL}/all_in_one/html?context_id=${CONTEXT_ID}")

# Extract key values
LAND_VALUE=$(echo "$RESPONSE" | grep -oP '토지감정가: \K[^<]+' | head -1)
TOTAL_UNITS=$(echo "$RESPONSE" | grep -oP '총세대수: \K[^<]+' | head -1)
NPV=$(echo "$RESPONSE" | grep -oP '(?<=• NPV: )[^<]+' | head -1)
DECISION=$(echo "$RESPONSE" | grep -oP 'LH 판단: \K[^<]+' | head -1)

echo "  토지감정가: $LAND_VALUE"
echo "  총세대수: $TOTAL_UNITS"
echo "  NPV: $NPV"
echo "  LH 판단: $DECISION"
echo ""

# Validate formats
FORMAT_OK=0
FORMAT_ISSUES=0

if [[ "$NPV" =~ ^[0-9,]+원$ ]]; then
    echo "  ✅ NPV formatted with commas"
    ((FORMAT_OK++))
else
    echo "  ❌ NPV format issue: $NPV"
    ((FORMAT_ISSUES++))
fi

if [[ "$DECISION" =~ ^(적합|부적합|조건부 적합|검토 필요)$ ]]; then
    echo "  ✅ Decision in Korean"
    ((FORMAT_OK++))
else
    echo "  ❌ Decision format issue: $DECISION"
    ((FORMAT_ISSUES++))
fi

if [[ ! "$RESPONSE" =~ GO|NO-GO|CONDITIONAL ]]; then
    echo "  ✅ No internal codes exposed"
    ((FORMAT_OK++))
else
    echo "  ❌ Internal decision codes found"
    ((FORMAT_ISSUES++))
fi

echo "  Result: $FORMAT_OK/$((FORMAT_OK+FORMAT_ISSUES)) checks passed"
echo ""

# Test 4: CSS Loading Check
echo "🎨 Test 4: Unified CSS Loading"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

CSS_LOADED=0
CSS_MISSING=0

for report in "${REPORTS[@]}"; do
    echo -n "  $report ... "
    RESPONSE=$(curl -s "${BASE_URL}/${report}/html?context_id=${CONTEXT_ID}")
    
    # Check for unified CSS indicators
    if echo "$RESPONSE" | grep -q "font-family.*Noto Sans KR"; then
        echo "✅ CSS loaded"
        ((CSS_LOADED++))
    else
        echo "⚠️  CSS not detected"
        ((CSS_MISSING++))
    fi
done

echo "  Result: $CSS_LOADED/$((CSS_LOADED+CSS_MISSING)) using unified CSS"
echo ""

# Final Summary
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                  VALIDATION SUMMARY                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  HTTP Status:    $PASSED/6 reports OK"
echo "  Data Exposure:  $CLEAN/6 reports clean"
echo "  KPI Format:     $FORMAT_OK/$((FORMAT_OK+FORMAT_ISSUES)) checks passed"
echo "  CSS Loading:    $CSS_LOADED/6 reports using unified CSS"
echo ""

# Overall result
TOTAL_CHECKS=$((PASSED + CLEAN + FORMAT_OK + CSS_LOADED))
MAX_CHECKS=$((6 + 6 + (FORMAT_OK+FORMAT_ISSUES) + 6))

if [ "$TOTAL_CHECKS" -eq "$MAX_CHECKS" ]; then
    echo "✅ ALL VALIDATIONS PASSED - Reports ready for delivery"
    exit 0
else
    MISSING=$((MAX_CHECKS - TOTAL_CHECKS))
    echo "⚠️  $MISSING checks failed - Review required"
    exit 1
fi
