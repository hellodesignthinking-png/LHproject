#!/bin/bash

# ZeroSite v4.0 - Load Testing Scenarios
# Locust 성능 테스트 자동 실행 스크립트

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
OUTPUT_DIR="tests/load_test_results"

# 결과 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

echo "🚀 ZeroSite v4.0 Load Testing Started"
echo "Target: $BASE_URL"
echo "Output: $OUTPUT_DIR"
echo ""

# 1. Baseline Test (기본 성능 측정)
echo "📊 [1/5] Running Baseline Test..."
locust -f tests/locustfile.py \
    --host="$BASE_URL" \
    --users 10 \
    --spawn-rate 2 \
    --run-time 2m \
    --headless \
    --html "$OUTPUT_DIR/baseline_report.html" \
    --csv "$OUTPUT_DIR/baseline" \
    --only-summary

echo "✅ Baseline Test Complete"
echo ""

# 2. Load Test (일반 부하 테스트)
echo "📊 [2/5] Running Load Test..."
locust -f tests/locustfile.py \
    --host="$BASE_URL" \
    --users 50 \
    --spawn-rate 5 \
    --run-time 5m \
    --headless \
    --html "$OUTPUT_DIR/load_report.html" \
    --csv "$OUTPUT_DIR/load" \
    --only-summary

echo "✅ Load Test Complete"
echo ""

# 3. Stress Test (스트레스 테스트)
echo "📊 [3/5] Running Stress Test..."
locust -f tests/locustfile.py \
    --host="$BASE_URL" \
    --users 200 \
    --spawn-rate 20 \
    --run-time 3m \
    --headless \
    --html "$OUTPUT_DIR/stress_report.html" \
    --csv "$OUTPUT_DIR/stress" \
    --only-summary \
    --class-picker StressTestUser

echo "✅ Stress Test Complete"
echo ""

# 4. Spike Test (급격한 트래픽 증가)
echo "📊 [4/5] Running Spike Test..."
locust -f tests/locustfile.py \
    --host="$BASE_URL" \
    --users 100 \
    --spawn-rate 50 \
    --run-time 1m \
    --headless \
    --html "$OUTPUT_DIR/spike_report.html" \
    --csv "$OUTPUT_DIR/spike" \
    --only-summary \
    --class-picker SpikeTestUser

echo "✅ Spike Test Complete"
echo ""

# 5. Endurance Test (장시간 테스트)
echo "📊 [5/5] Running Endurance Test..."
locust -f tests/locustfile.py \
    --host="$BASE_URL" \
    --users 30 \
    --spawn-rate 3 \
    --run-time 10m \
    --headless \
    --html "$OUTPUT_DIR/endurance_report.html" \
    --csv "$OUTPUT_DIR/endurance" \
    --only-summary

echo "✅ Endurance Test Complete"
echo ""

# 결과 요약 생성
echo "📈 Generating Test Summary..."

cat > "$OUTPUT_DIR/summary.md" << 'EOF'
# ZeroSite v4.0 Load Testing Summary

## Test Date
$(date)

## Test Scenarios

### 1. Baseline Test
- **Users**: 10
- **Duration**: 2 minutes
- **Purpose**: 기본 성능 측정

### 2. Load Test
- **Users**: 50
- **Duration**: 5 minutes
- **Purpose**: 일반적인 부하 테스트

### 3. Stress Test
- **Users**: 200
- **Duration**: 3 minutes
- **Purpose**: 시스템 한계 테스트

### 4. Spike Test
- **Users**: 100 (50/sec spawn rate)
- **Duration**: 1 minute
- **Purpose**: 급격한 트래픽 증가 대응

### 5. Endurance Test
- **Users**: 30
- **Duration**: 10 minutes
- **Purpose**: 장시간 안정성 테스트

## Key Metrics

### Response Time Targets
- **API Endpoints**: < 200ms (P95)
- **Analysis Requests**: < 5s (P95)
- **Dashboard Pages**: < 500ms (P95)

### Success Rate Target
- **Overall**: > 99.5%

### Throughput Target
- **Requests/sec**: > 100 RPS

## Results

상세 결과는 각 HTML 리포트를 참고하세요:
- [Baseline Report](baseline_report.html)
- [Load Report](load_report.html)
- [Stress Report](stress_report.html)
- [Spike Report](spike_report.html)
- [Endurance Report](endurance_report.html)

## CSV Data Files

각 테스트의 원시 데이터:
- `baseline_stats.csv`, `baseline_exceptions.csv`, `baseline_failures.csv`
- `load_stats.csv`, `load_exceptions.csv`, `load_failures.csv`
- `stress_stats.csv`, `stress_exceptions.csv`, `stress_failures.csv`
- `spike_stats.csv`, `spike_exceptions.csv`, `spike_failures.csv`
- `endurance_stats.csv`, `endurance_exceptions.csv`, `endurance_failures.csv`
EOF

echo "✅ Summary Generated: $OUTPUT_DIR/summary.md"
echo ""
echo "🎉 All Load Tests Complete!"
echo "📁 Results saved to: $OUTPUT_DIR"
echo ""
echo "🌐 View HTML Reports:"
echo "  - Baseline:   file://$PWD/$OUTPUT_DIR/baseline_report.html"
echo "  - Load:       file://$PWD/$OUTPUT_DIR/load_report.html"
echo "  - Stress:     file://$PWD/$OUTPUT_DIR/stress_report.html"
echo "  - Spike:      file://$PWD/$OUTPUT_DIR/spike_report.html"
echo "  - Endurance:  file://$PWD/$OUTPUT_DIR/endurance_report.html"
