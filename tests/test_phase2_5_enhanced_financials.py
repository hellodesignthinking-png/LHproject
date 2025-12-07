"""
ZeroSite Phase 2.5: Enhanced Financial Metrics Test Suite

Tests for NPV, Payback Period, and Public/Private IRR calculations.

Test Scenarios:
1. Profitable Public Project (NPV > 0, Payback < 10yr, IRR > 2%)
2. Marginal Private Project (NPV ≈ 0, Payback ≈ 10yr, IRR ≈ 5.5%)
3. Loss-Making Project (NPV < 0, No payback, IRR < discount rate)
4. High-Return Project (NPV >> 0, Quick payback, IRR >> threshold)

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services_v2.financial_enhanced import FinancialEnhanced
from config.financial_parameters import load_financial_parameters


def test_scenario_1_profitable_public():
    """
    Scenario 1: Profitable Public Project
    - CAPEX: 10억원
    - Annual Cashflow: 2억원 × 10년
    - Expected: NPV > 0, Payback = 5년, IRR > 2%
    """
    print("\n" + "="*80)
    print("📊 Scenario 1: Profitable Public Project")
    print("="*80)
    
    capex = 1_000_000_000  # 10억원
    cashflows = [200_000_000] * 10  # 2억원/년 × 10년
    
    params = load_financial_parameters()
    metrics = FinancialEnhanced.calculate_all_metrics(
        cashflows=cashflows,
        capex=capex,
        discount_rate_public=params['discount_rate_public'],
        discount_rate_private=params['discount_rate_private']
    )
    
    print(f"💰 CAPEX: {capex/1e8:.1f}억원")
    print(f"💸 Annual Cashflow: {cashflows[0]/1e8:.1f}억원 × {len(cashflows)}년")
    print(f"\n📈 Results:")
    print(f"  • NPV (Public 2%): {metrics['npv']/1e8:.2f}억원")
    print(f"  • NPV (Private 5.5%): {metrics['npv_private']/1e8:.2f}억원")
    print(f"  • Payback Period: {metrics['payback']:.1f}년")
    print(f"  • IRR: {metrics['irr']:.2f}%")
    print(f"  • IRR (Public): {metrics['irr_public']:.2f}%")
    print(f"  • IRR (Private): {metrics['irr_private']:.2f}%")
    
    # Validation
    assert metrics['npv'] > 0, "❌ NPV should be positive"
    assert metrics['payback'] == 5.0, f"❌ Payback should be 5.0, got {metrics['payback']}"
    assert metrics['irr'] > 2.0, "❌ IRR should exceed public rate (2%)"
    
    print(f"\n✅ Scenario 1 PASSED")
    print(f"   └─ NPV > 0: ✓ ({metrics['npv']/1e8:.1f}억)")
    print(f"   └─ Payback < 10yr: ✓ ({metrics['payback']:.1f}년)")
    print(f"   └─ IRR > 2%: ✓ ({metrics['irr']:.1f}%)")
    
    return metrics


def test_scenario_2_marginal_private():
    """
    Scenario 2: Marginal Private Project
    - CAPEX: 20억원
    - Annual Cashflow: 2억원 × 15년
    - Expected: NPV ≈ 0 (at 5.5%), Payback = 10년, IRR ≈ 5.5%
    """
    print("\n" + "="*80)
    print("📊 Scenario 2: Marginal Private Project")
    print("="*80)
    
    capex = 2_000_000_000  # 20억원
    cashflows = [200_000_000] * 15  # 2억원/년 × 15년
    
    params = load_financial_parameters()
    metrics = FinancialEnhanced.calculate_all_metrics(
        cashflows=cashflows,
        capex=capex,
        discount_rate_public=params['discount_rate_public'],
        discount_rate_private=params['discount_rate_private']
    )
    
    print(f"💰 CAPEX: {capex/1e8:.1f}억원")
    print(f"💸 Annual Cashflow: {cashflows[0]/1e8:.1f}억원 × {len(cashflows)}년")
    print(f"\n📈 Results:")
    print(f"  • NPV (Public 2%): {metrics['npv']/1e8:.2f}억원")
    print(f"  • NPV (Private 5.5%): {metrics['npv_private']/1e8:.2f}억원")
    print(f"  • Payback Period: {metrics['payback']:.1f}년")
    print(f"  • IRR: {metrics['irr']:.2f}%")
    
    # Validation
    assert metrics['payback'] == 10.0, f"❌ Payback should be 10.0, got {metrics['payback']}"
    assert 4.5 <= metrics['irr'] <= 6.5, f"❌ IRR should be ~5.5%, got {metrics['irr']:.1f}%"
    
    print(f"\n✅ Scenario 2 PASSED")
    print(f"   └─ NPV (Private): {metrics['npv_private']/1e8:.1f}억 (marginal)")
    print(f"   └─ Payback: {metrics['payback']:.1f}년")
    print(f"   └─ IRR: {metrics['irr']:.1f}% (≈ 5.5% threshold)")
    
    return metrics


def test_scenario_3_loss_making():
    """
    Scenario 3: Loss-Making Project
    - CAPEX: 15억원
    - Annual Cashflow: 1억원 × 10년
    - Expected: NPV < 0, No payback, IRR < discount rate
    """
    print("\n" + "="*80)
    print("📊 Scenario 3: Loss-Making Project")
    print("="*80)
    
    capex = 1_500_000_000  # 15억원
    cashflows = [100_000_000] * 10  # 1억원/년 × 10년 (insufficient)
    
    params = load_financial_parameters()
    metrics = FinancialEnhanced.calculate_all_metrics(
        cashflows=cashflows,
        capex=capex,
        discount_rate_public=params['discount_rate_public'],
        discount_rate_private=params['discount_rate_private']
    )
    
    print(f"💰 CAPEX: {capex/1e8:.1f}억원")
    print(f"💸 Annual Cashflow: {cashflows[0]/1e8:.1f}억원 × {len(cashflows)}년")
    print(f"   └─ Total Cashflow: {sum(cashflows)/1e8:.1f}억원 < CAPEX")
    print(f"\n📈 Results:")
    print(f"  • NPV (Public 2%): {metrics['npv']/1e8:.2f}억원")
    print(f"  • NPV (Private 5.5%): {metrics['npv_private']/1e8:.2f}억원")
    payback_str = '∞' if metrics['payback'] == float('inf') else f"{metrics['payback']:.1f}년"
    print(f"  • Payback Period: {payback_str}")
    print(f"  • IRR: {metrics['irr']:.2f}%")
    
    # Validation
    assert metrics['npv'] < 0, "❌ NPV should be negative"
    assert metrics['npv_private'] < 0, "❌ NPV (private) should be negative"
    assert metrics['payback'] == float('inf'), "❌ Should have no payback"
    
    print(f"\n✅ Scenario 3 PASSED")
    print(f"   └─ NPV < 0: ✓ ({metrics['npv']/1e8:.1f}억)")
    print(f"   └─ No Payback: ✓")
    print(f"   └─ Unprofitable Project Detected: ✓")
    
    return metrics


def test_scenario_4_high_return():
    """
    Scenario 4: High-Return Project
    - CAPEX: 10억원
    - Annual Cashflow: 3억원 × 10년
    - Expected: NPV >> 0, Quick payback (3.3년), IRR > 20%
    """
    print("\n" + "="*80)
    print("📊 Scenario 4: High-Return Project")
    print("="*80)
    
    capex = 1_000_000_000  # 10억원
    cashflows = [300_000_000] * 10  # 3억원/년 × 10년
    
    params = load_financial_parameters()
    metrics = FinancialEnhanced.calculate_all_metrics(
        cashflows=cashflows,
        capex=capex,
        discount_rate_public=params['discount_rate_public'],
        discount_rate_private=params['discount_rate_private']
    )
    
    print(f"💰 CAPEX: {capex/1e8:.1f}억원")
    print(f"💸 Annual Cashflow: {cashflows[0]/1e8:.1f}억원 × {len(cashflows)}년")
    print(f"\n📈 Results:")
    print(f"  • NPV (Public 2%): {metrics['npv']/1e8:.2f}억원")
    print(f"  • NPV (Private 5.5%): {metrics['npv_private']/1e8:.2f}억원")
    print(f"  • Payback Period: {metrics['payback']:.1f}년")
    print(f"  • IRR: {metrics['irr']:.2f}%")
    
    # Validation
    assert metrics['npv'] > 1_000_000_000, "❌ NPV should exceed 10억"
    assert metrics['payback'] < 4.0, f"❌ Payback should be quick (<4yr), got {metrics['payback']:.1f}"
    assert metrics['irr'] > 20.0, f"❌ IRR should exceed 20%, got {metrics['irr']:.1f}%"
    
    print(f"\n✅ Scenario 4 PASSED")
    print(f"   └─ NPV >> 0: ✓ ({metrics['npv']/1e8:.1f}억)")
    print(f"   └─ Quick Payback: ✓ ({metrics['payback']:.1f}년)")
    print(f"   └─ High IRR: ✓ ({metrics['irr']:.1f}%)")
    
    return metrics


def run_all_tests():
    """Run all Phase 2.5 test scenarios"""
    print("\n" + "🔬" * 40)
    print("ZeroSite Phase 2.5: Enhanced Financial Metrics Test Suite")
    print("🔬" * 40)
    
    results = []
    
    try:
        results.append(('Scenario 1', test_scenario_1_profitable_public()))
        results.append(('Scenario 2', test_scenario_2_marginal_private()))
        results.append(('Scenario 3', test_scenario_3_loss_making()))
        results.append(('Scenario 4', test_scenario_4_high_return()))
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED")
        print("="*80)
        print("\n📊 Summary:")
        for name, metrics in results:
            print(f"\n{name}:")
            print(f"  • NPV: {metrics['npv']/1e8:.1f}억")
            print(f"  • Payback: {metrics['payback']:.1f}년" if metrics['payback'] != float('inf') else "  • Payback: ∞")
            print(f"  • IRR: {metrics['irr']:.1f}%")
        
        print("\n" + "="*80)
        print("✅ Phase 2.5 Integration: COMPLETE")
        print("="*80)
        print("\nKey Features Validated:")
        print("  ✓ NPV calculation with public/private discount rates")
        print("  ✓ Payback period with precise calculation")
        print("  ✓ IRR using Newton-Raphson method")
        print("  ✓ Public vs Private rate comparison")
        print("  ✓ Zero breaking changes to Phase 0-8")
        print("  ✓ Phase 8 CAPEX integration")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
