"""
Performance Monitoring and Metrics Collection
"""

import time
from typing import Dict, Optional, List
from functools import wraps
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class PerformanceMetric:
    """Performance metric data"""
    operation: str
    duration_ms: float
    timestamp: datetime
    success: bool
    metadata: Dict = field(default_factory=dict)


class PerformanceMonitor:
    """
    Performance monitoring service
    
    Tracks response times, throughput, and system metrics
    """
    
    def __init__(self):
        self._metrics: List[PerformanceMetric] = []
        self._max_metrics = 10000  # Keep last 10k metrics
    
    def record(self, operation: str, duration_ms: float, success: bool = True, **metadata):
        """Record a performance metric"""
        metric = PerformanceMetric(
            operation=operation,
            duration_ms=duration_ms,
            timestamp=datetime.now(),
            success=success,
            metadata=metadata
        )
        
        self._metrics.append(metric)
        
        # Trim if too large
        if len(self._metrics) > self._max_metrics:
            self._metrics = self._metrics[-self._max_metrics:]
    
    def get_stats(self, operation: Optional[str] = None) -> Dict:
        """Get performance statistics"""
        metrics = self._metrics
        
        if operation:
            metrics = [m for m in metrics if m.operation == operation]
        
        if not metrics:
            return {"count": 0}
        
        durations = [m.duration_ms for m in metrics]
        
        return {
            "count": len(metrics),
            "avg_ms": sum(durations) / len(durations),
            "min_ms": min(durations),
            "max_ms": max(durations),
            "p95_ms": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else max(durations),
            "success_rate": sum(1 for m in metrics if m.success) / len(metrics) * 100
        }


# Global monitor instance
_monitor: Optional[PerformanceMonitor] = None


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor


def track_performance(operation: str):
    """
    Decorator to track function performance
    
    Example:
        @track_performance("analyze_land")
        def analyze_land(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration_ms = (time.time() - start) * 1000
                monitor = get_monitor()
                monitor.record(operation, duration_ms, success)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration_ms = (time.time() - start) * 1000
                monitor = get_monitor()
                monitor.record(operation, duration_ms, success)
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
