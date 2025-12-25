#!/usr/bin/env python3
"""
ZeroSite v4.0 - Production Monitoring Dashboard

Purpose: Monitor report generation performance and quality metrics
Author: ZeroSite Backend Team
Date: 2025-12-25
"""

import time
from datetime import datetime
from typing import Dict, Any, List
from collections import defaultdict


class ProductionMonitor:
    """프로덕션 보고서 생성 모니터링 시스템"""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "report_types": defaultdict(int),
            "errors": [],
            "performance": [],
            "kpi_issues": []
        }
        self.start_time = datetime.now()
    
    def record_generation(
        self,
        report_type: str,
        context_id: str,
        success: bool,
        duration_ms: float,
        html_size: int = 0,
        na_count: int = 0,
        kpi_present: int = 0,
        error: str = None
    ):
        """
        보고서 생성 기록
        
        Args:
            report_type: 보고서 유형
            context_id: Context ID
            success: 성공 여부
            duration_ms: 생성 시간 (밀리초)
            html_size: HTML 크기
            na_count: N/A 발생 횟수
            kpi_present: KPI 표시 개수
            error: 에러 메시지 (실패 시)
        """
        self.metrics["total_requests"] += 1
        
        if success:
            self.metrics["successful_generations"] += 1
            self.metrics["report_types"][report_type] += 1
            
            self.metrics["performance"].append({
                "timestamp": datetime.now().isoformat(),
                "report_type": report_type,
                "context_id": context_id,
                "duration_ms": duration_ms,
                "html_size": html_size,
                "na_count": na_count,
                "kpi_present": kpi_present
            })
            
            # Check for KPI issues
            if kpi_present < 6:
                self.metrics["kpi_issues"].append({
                    "timestamp": datetime.now().isoformat(),
                    "report_type": report_type,
                    "context_id": context_id,
                    "kpi_present": kpi_present,
                    "kpi_missing": 6 - kpi_present
                })
        else:
            self.metrics["failed_generations"] += 1
            self.metrics["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "report_type": report_type,
                "context_id": context_id,
                "error": error
            })
    
    def get_dashboard(self) -> str:
        """모니터링 대시보드 생성"""
        uptime = datetime.now() - self.start_time
        
        # Calculate success rate
        total = self.metrics["total_requests"]
        success_rate = (self.metrics["successful_generations"] / total * 100) if total > 0 else 0
        
        # Average performance
        perf = self.metrics["performance"]
        avg_duration = sum(p["duration_ms"] for p in perf) / len(perf) if perf else 0
        avg_html_size = sum(p["html_size"] for p in perf) / len(perf) if perf else 0
        avg_na_count = sum(p["na_count"] for p in perf) / len(perf) if perf else 0
        avg_kpi_present = sum(p["kpi_present"] for p in perf) / len(perf) if perf else 0
        
        dashboard = f"""
{'='*80}
📊 ZEROSITE v4.0 PRODUCTION MONITORING DASHBOARD
{'='*80}

⏱️  Uptime: {uptime}
📅 Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}

{'='*80}
📈 GENERATION STATISTICS
{'='*80}

Total Requests:        {total}
✅ Successful:         {self.metrics['successful_generations']} ({success_rate:.1f}%)
❌ Failed:             {self.metrics['failed_generations']} ({100-success_rate:.1f}%)

Report Types Generated:
"""
        
        for report_type, count in sorted(self.metrics["report_types"].items()):
            dashboard += f"  - {report_type:25} {count:5} generations\n"
        
        dashboard += f"""
{'='*80}
⚡ PERFORMANCE METRICS
{'='*80}

Average Generation Time:   {avg_duration:.1f} ms
Average HTML Size:         {avg_html_size:,.0f} characters
Average N/A Count:         {avg_na_count:.1f}
Average KPI Present:       {avg_kpi_present:.1f}/6

"""
        
        # Recent errors
        if self.metrics["errors"]:
            dashboard += f"""
{'='*80}
❌ RECENT ERRORS (Last 10)
{'='*80}

"""
            for error in self.metrics["errors"][-10:]:
                dashboard += f"""
  Timestamp:    {error['timestamp']}
  Report Type:  {error['report_type']}
  Context ID:   {error['context_id']}
  Error:        {error['error']}
"""
        
        # KPI issues
        if self.metrics["kpi_issues"]:
            dashboard += f"""
{'='*80}
⚠️  KPI ISSUES (Last 10)
{'='*80}

"""
            for issue in self.metrics["kpi_issues"][-10:]:
                dashboard += f"""
  Timestamp:    {issue['timestamp']}
  Report Type:  {issue['report_type']}
  Context ID:   {issue['context_id']}
  KPI Present:  {issue['kpi_present']}/6 (Missing: {issue['kpi_missing']})
"""
        
        # Health status
        dashboard += f"""
{'='*80}
🏥 SYSTEM HEALTH
{'='*80}

"""
        
        if success_rate >= 95:
            health = "✅ EXCELLENT"
        elif success_rate >= 90:
            health = "✓  GOOD"
        elif success_rate >= 80:
            health = "⚠️  WARNING"
        else:
            health = "❌ CRITICAL"
        
        dashboard += f"Success Rate: {health} ({success_rate:.1f}%)\n"
        
        if avg_kpi_present >= 5.5:
            kpi_health = "✅ EXCELLENT"
        elif avg_kpi_present >= 5.0:
            kpi_health = "✓  GOOD"
        elif avg_kpi_present >= 4.5:
            kpi_health = "⚠️  WARNING"
        else:
            kpi_health = "❌ CRITICAL"
        
        dashboard += f"KPI Display:  {kpi_health} ({avg_kpi_present:.1f}/6)\n"
        
        if avg_na_count <= 2:
            na_health = "✅ EXCELLENT"
        elif avg_na_count <= 5:
            na_health = "✓  GOOD"
        elif avg_na_count <= 10:
            na_health = "⚠️  WARNING"
        else:
            na_health = "❌ CRITICAL"
        
        dashboard += f"N/A Count:    {na_health} ({avg_na_count:.1f})\n"
        
        dashboard += f"\n{'='*80}\n"
        
        return dashboard
    
    def save_report(self, filepath: str):
        """모니터링 리포트를 파일로 저장"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.get_dashboard())
    
    def print_dashboard(self):
        """대시보드를 콘솔에 출력"""
        print(self.get_dashboard())


# Example usage
if __name__ == "__main__":
    monitor = ProductionMonitor()
    
    # Simulate some test data
    monitor.record_generation(
        report_type="all_in_one",
        context_id="test-001",
        success=True,
        duration_ms=1250.5,
        html_size=39888,
        na_count=2,
        kpi_present=6
    )
    
    monitor.record_generation(
        report_type="financial_feasibility",
        context_id="test-002",
        success=True,
        duration_ms=980.2,
        html_size=13700,
        na_count=4,
        kpi_present=5
    )
    
    monitor.record_generation(
        report_type="quick_check",
        context_id="test-003",
        success=False,
        duration_ms=0,
        error="Redis connection failed"
    )
    
    # Print dashboard
    monitor.print_dashboard()
    
    # Save to file
    monitor.save_report("production_monitoring_report.txt")
    print("\n✅ Report saved to: production_monitoring_report.txt")
