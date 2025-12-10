#!/bin/bash

echo "=== Generating 3 Sample Reports ==="

# Report 1: Gangnam Youth
curl -s -X POST http://localhost:8040/api/v21/generate-report \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 강남구 역삼동 123-45", "land_area_sqm": 1650.0, "supply_type": "청년"}' | jq -r '.report_url'

# Report 2: Songpa Newlywed
curl -s -X POST http://localhost:8040/api/v21/generate-report \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 송파구 잠실동 456-78", "land_area_sqm": 1800.0, "supply_type": "신혼부부"}' | jq -r '.report_url'

# Report 3: Nowon General
curl -s -X POST http://localhost:8040/api/v21/generate-report \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 노원구 상계동 789-12", "land_area_sqm": 2000.0, "supply_type": "일반"}' | jq -r '.report_url'
