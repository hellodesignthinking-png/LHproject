#!/bin/bash

echo "Testing M3 MODULE_NOT_EXECUTED scenario..."
echo ""

# Create a new project
PROJECT_RESPONSE=$(curl -s -X POST http://localhost:49999/api/analysis/projects/create \
  -H "Content-Type: application/json" \
  -d '{"project_name": "M3 Not Executed Test", "address": "서울특별시 강남구"}')

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['project_id'])")
echo "Project Created: $PROJECT_ID"
echo ""

# Try to get M3 result without executing it
echo "Attempting to get M3 result (should return 409 error)..."
RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:49999/api/analysis/projects/$PROJECT_ID/modules/M3/result")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

echo "HTTP Code: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" = "409" ]; then
  echo "✅ PASS: Returns 409 Conflict"
  echo ""
  echo "Response Body:"
  echo "$BODY" | python3 -m json.tool 2>&1 | head -20
  echo ""
  echo "✅ M3 NOT_EXECUTED validation works correctly!"
else
  echo "❌ FAIL: Expected 409, got $HTTP_CODE"
  echo "Response:"
  echo "$BODY" | head -20
fi
