#!/usr/bin/env python3
"""
Pipeline Performance Benchmark
================================

Performance testing for 6-MODULE Pipeline

Metrics:
- Execution time per module
- Total pipeline execution time
- Memory usage
- Throughput (analyses per second)

Author: ZeroSite Refactoring Team  
Date: 2025-12-17
"""

import sys
import time
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.pipeline.zer0site_pipeline import ZeroSitePipeline


def benchmark_single_run():
    """Benchmark single pipeline run"""
    print("\n" + "="*80)
    print("⚡ Single Pipeline Run Benchmark")
    print("="*80 + "\n")
    
    pipeline = ZeroSitePipeline()
    parcel_id = "1168010100100010001"
    
    # Warm-up run
    print("🔥 Warming up...")
    pipeline.run(parcel_id)
    
    # Timed run
    print("⏱️  Benchmarking...")
    start_time = time.time()
    result = pipeline.run(parcel_id)
    end_time = time.time()
    
    execution_time_ms = (end_time - start_time) * 1000
    
    print(f"\n✅ Pipeline completed")
    print(f"   Execution Time: {execution_time_ms:.2f}ms")
    print(f"   Success: {result.success}")
    print(f"\n📊 Results:")
    print(f"   Land Value: ₩{result.appraisal.land_value:,.0f}")
    print(f"   LH Score: {result.lh_review.total_score:.1f}/110")
    print(f"   Decision: {result.lh_review.decision}")
    
    return execution_time_ms


def benchmark_multiple_runs(count=10):
    """Benchmark multiple pipeline runs"""
    print("\n" + "="*80)
    print(f"⚡ Multiple Pipeline Runs Benchmark ({count} runs)")
    print("="*80 + "\n")
    
    pipeline = ZeroSitePipeline()
    parcel_id = "1168010100100010001"
    
    times = []
    
    for i in range(count):
        start_time = time.time()
        result = pipeline.run(parcel_id)
        end_time = time.time()
        
        execution_time_ms = (end_time - start_time) * 1000
        times.append(execution_time_ms)
        
        print(f"   Run {i+1}/{count}: {execution_time_ms:.2f}ms")
    
    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    throughput = 1000 / avg_time  # analyses per second
    
    print(f"\n📊 Statistics:")
    print(f"   Average: {avg_time:.2f}ms")
    print(f"   Min: {min_time:.2f}ms")
    print(f"   Max: {max_time:.2f}ms")
    print(f"   Throughput: {throughput:.2f} analyses/second")
    
    return {
        "avg_time_ms": avg_time,
        "min_time_ms": min_time,
        "max_time_ms": max_time,
        "throughput": throughput
    }


def benchmark_deterministic_consistency():
    """Verify deterministic consistency"""
    print("\n" + "="*80)
    print("🔍 Deterministic Consistency Check")
    print("="*80 + "\n")
    
    pipeline = ZeroSitePipeline()
    parcel_id = "1168010100100010001"
    
    # Run 5 times
    results = []
    for i in range(5):
        result = pipeline.run(parcel_id)
        results.append({
            "land_value": result.appraisal.land_value,
            "confidence_score": result.appraisal.confidence_metrics.confidence_score,
            "lh_score": result.lh_review.total_score
        })
    
    # Check consistency
    first_result = results[0]
    all_consistent = all(
        r["land_value"] == first_result["land_value"] and
        r["confidence_score"] == first_result["confidence_score"] and
        r["lh_score"] == first_result["lh_score"]
        for r in results
    )
    
    if all_consistent:
        print("✅ All 5 runs produced identical results (deterministic)")
        print(f"   Land Value: ₩{first_result['land_value']:,.0f}")
        print(f"   Confidence: {first_result['confidence_score']:.2f}")
        print(f"   LH Score: {first_result['lh_score']:.1f}")
    else:
        print("❌ Results are NOT consistent:")
        for i, r in enumerate(results, 1):
            print(f"   Run {i}: ₩{r['land_value']:,.0f}, " +
                  f"conf={r['confidence_score']:.2f}, " +
                  f"lh={r['lh_score']:.1f}")
    
    return all_consistent


def check_context_immutability():
    """Verify all contexts are immutable"""
    print("\n" + "="*80)
    print("🔒 Context Immutability Check")
    print("="*80 + "\n")
    
    pipeline = ZeroSitePipeline()
    result = pipeline.run("1168010100100010001")
    
    contexts = [
        ("M1 Land", result.land),
        ("M2 Appraisal", result.appraisal),
        ("M3 Housing Type", result.housing_type),
        ("M4 Capacity", result.capacity),
        ("M5 Feasibility", result.feasibility),
        ("M6 LH Review", result.lh_review)
    ]
    
    all_frozen = True
    
    for name, context in contexts:
        try:
            # Try to modify a field (will fail if frozen)
            if hasattr(context, "land_value"):
                context.land_value = 999999999
            elif hasattr(context, "selected_type"):
                context.selected_type = "TEST"
            elif hasattr(context, "decision"):
                context.decision = "TEST"
            else:
                # Try to set any attribute
                context._test_field = "TEST"
            
            print(f"   ❌ {name}: NOT frozen (modification succeeded)")
            all_frozen = False
            
        except Exception as e:
            print(f"   ✅ {name}: Frozen ({type(e).__name__})")
    
    if all_frozen:
        print(f"\n✅ All 6 contexts are immutable (frozen=True)")
    else:
        print(f"\n❌ Some contexts are NOT immutable!")
    
    return all_frozen


def main():
    """Run all benchmarks"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*17 + "🚀 6-MODULE PIPELINE PERFORMANCE BENCHMARK" + " "*19 + "║")
    print("╚" + "="*78 + "╝")
    
    # Run benchmarks
    single_time = benchmark_single_run()
    multi_stats = benchmark_multiple_runs(count=10)
    is_deterministic = benchmark_deterministic_consistency()
    is_immutable = check_context_immutability()
    
    # Final summary
    print("\n" + "="*80)
    print("📊 BENCHMARK SUMMARY")
    print("="*80)
    print(f"   Single Run: {single_time:.2f}ms")
    print(f"   Average (10 runs): {multi_stats['avg_time_ms']:.2f}ms")
    print(f"   Throughput: {multi_stats['throughput']:.2f} analyses/sec")
    print(f"   Deterministic: {'✅ YES' if is_deterministic else '❌ NO'}")
    print(f"   Immutable Contexts: {'✅ YES' if is_immutable else '❌ NO'}")
    print("="*80)
    
    # Performance rating
    avg_time = multi_stats['avg_time_ms']
    if avg_time < 100:
        rating = "🚀 EXCELLENT"
    elif avg_time < 200:
        rating = "✅ GOOD"
    elif avg_time < 500:
        rating = "⚠️  ACCEPTABLE"
    else:
        rating = "❌ NEEDS OPTIMIZATION"
    
    print(f"\n   Performance Rating: {rating}")
    print(f"   Status: {'🟢 PASS' if is_deterministic and is_immutable else '🔴 FAIL'}")
    print("\n")
    
    # Return success if all checks pass
    return is_deterministic and is_immutable


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
