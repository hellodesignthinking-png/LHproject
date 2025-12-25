#!/usr/bin/env python3
"""
Production Monitoring with Real Test Data
실제 테스트 결과를 모니터링 시스템에 기록
"""

import sys
sys.path.insert(0, '.')

from production_monitoring import ProductionMonitor

# Create monitor instance
monitor = ProductionMonitor()

# Record actual test results from production_test_direct.py
test_results = [
    ("quick_check", "prod-test-001", True, 0.1, 51876, 21, 3),
    ("financial_feasibility", "prod-test-001", True, 0.2, 59787, 73, 2),
    ("lh_technical", "prod-test-001", True, 0.1, 21195, 19, 2),
    ("executive_summary", "prod-test-001", True, 0.2, 60301, 32, 3),
    ("landowner_summary", "prod-test-001", True, 0.0, 23729, 10, 1),
    ("all_in_one", "prod-test-001", True, 0.1, 30502, 12, 4),
]

print("📊 Recording production test results to monitoring system...\n")

for report_type, context_id, success, duration_ms, html_size, na_count, kpi_present in test_results:
    monitor.record_generation(
        report_type=report_type,
        context_id=context_id,
        success=success,
        duration_ms=duration_ms,
        html_size=html_size,
        na_count=na_count,
        kpi_present=kpi_present
    )
    print(f"✓ Recorded: {report_type:25} | {html_size:7,} chars | KPI: {kpi_present}/6")

print("\n" + "="*80)
print("📊 PRODUCTION MONITORING DASHBOARD")
print("="*80 + "\n")

# Display dashboard
monitor.print_dashboard()

# Save report
monitor.save_report("production_monitoring_live.txt")
print("\n✅ Live monitoring report saved to: production_monitoring_live.txt")
