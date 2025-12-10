#!/bin/bash
echo "🧪 Generating test reports..."

# Test 1: Gangnam Youth Housing
echo "Test 1: Gangnam Youth Housing"
curl -X POST http://localhost:8091/generate-report \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 강남구 테헤란로 123", "land_area_sqm": 1500, "supply_type": "청년"}' \
  -s | jq '.'
echo ""

# Test 2: Mapo Newlywed Housing  
echo "Test 2: Mapo Newlywed Housing"
curl -X POST http://localhost:8091/generate-report \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 마포구 월드컵북로 200", "land_area_sqm": 2000, "supply_type": "신혼"}' \
  -s | jq '.'
echo ""

# Test 3: Songpa Senior Housing
echo "Test 3: Songpa Senior Housing"
curl -X POST http://localhost:8091/generate-report \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 송파구 올림픽로 300", "land_area_sqm": 1200, "supply_type": "고령"}' \
  -s | jq '.'
echo ""

# Get final metrics
echo "📊 Final Metrics:"
curl -s http://localhost:8091/metrics | jq '.'
