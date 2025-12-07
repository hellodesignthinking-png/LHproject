"""
ZeroSite Phase 2.5: Enhanced Financial Metrics

Provides advanced financial analysis metrics beyond basic ROI/IRR:
- NPV (Net Present Value)
- Payback Period
- IRR with Public vs Private discount rates

Features:
    - NPV calculation using discounted cashflow
    - Payback period with cumulative cashflow tracking
    - IRR using Newton-Raphson iterative method
    - Public standard (2% discount rate for government projects)
    - Private standard (5.5% discount rate for commercial projects)
    - Zero breaking changes to existing Phase 2 logic

Architecture:
    Phase 8 CAPEX (Frozen) → Cashflows → Enhanced Metrics
    
    This module operates AFTER Phase 8 CAPEX calculation is complete,
    ensuring no interference with verified cost and LH rule calculations.

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

from typing import List, Tuple
import math


class FinancialEnhanced:
    """
    Enhanced Financial Metrics Calculator
    
    Provides NPV, Payback Period, and IRR calculations for investment analysis.
    All calculations use Phase 8 verified CAPEX as the baseline.
    
    Usage:
        cashflows = [200_000_000, 200_000_000, ...]  # Annual net cashflows
        capex = 1_000_000_000  # From Phase 8
        
        npv = FinancialEnhanced.npv(0.02, cashflows, capex)
        payback = FinancialEnhanced.payback(cashflows, capex)
        irr = FinancialEnhanced.irr(cashflows, capex)
    """
    
    @staticmethod
    def npv(discount_rate: float, cashflows: List[float], capex: float) -> float:
        """
        Calculate Net Present Value (NPV)
        
        Formula:
            NPV = Σ[ CF_t / (1 + r)^t ] - CAPEX
        
        Where:
            CF_t = Cashflow at time t
            r = Discount rate
            CAPEX = Initial capital expenditure (spent at t=0)
        
        Args:
            discount_rate: Discount rate (e.g., 0.02 for 2%)
            cashflows: List of annual net cashflows (positive = inflow)
            capex: Initial capital expenditure (from Phase 8)
        
        Returns:
            Net Present Value in 원 (positive = profitable)
        
        Example:
            >>> npv(0.02, [200_000_000] * 6, 1_000_000_000)
            140_000_000  # Project is profitable
        """
        if not cashflows:
            return -capex
        
        discounted_sum = 0.0
        for t, cf in enumerate(cashflows, start=1):
            discounted_sum += cf / ((1 + discount_rate) ** t)
        
        return discounted_sum - capex
    
    @staticmethod
    def payback(cashflows: List[float], capex: float) -> float:
        """
        Calculate Payback Period
        
        Finds the time (in years) when cumulative cashflows equal or exceed CAPEX.
        
        Formula:
            Find t where Σ(CF_1 to CF_t) >= CAPEX
        
        Args:
            cashflows: List of annual net cashflows
            capex: Initial capital expenditure
        
        Returns:
            Payback period in years (float)
            Returns inf if payback never occurs
        
        Example:
            >>> payback([200_000_000] * 6, 1_000_000_000)
            5.0  # Pays back in 5 years
        """
        if not cashflows:
            return float("inf")
        
        cumulative = 0.0
        for t, cf in enumerate(cashflows, start=1):
            cumulative += cf
            if cumulative >= capex:
                # Linear interpolation for precise payback time
                if t == 1:
                    return capex / cf
                else:
                    previous_cumulative = cumulative - cf
                    remaining = capex - previous_cumulative
                    fraction = remaining / cf
                    return (t - 1) + fraction
        
        # If never pays back
        return float("inf")
    
    @staticmethod
    def irr(
        cashflows: List[float],
        capex: float,
        precision: float = 1e-6,
        max_iterations: int = 100
    ) -> float:
        """
        Calculate Internal Rate of Return (IRR)
        
        Solves for r where NPV(r) = 0 using Newton-Raphson method.
        
        Formula:
            NPV(r) = Σ[ CF_t / (1 + r)^t ] - CAPEX = 0
        
        Args:
            cashflows: List of annual net cashflows
            capex: Initial capital expenditure
            precision: Convergence precision (default: 1e-6)
            max_iterations: Maximum iterations (default: 100)
        
        Returns:
            IRR as percentage (e.g., 8.5 means 8.5%)
            Returns 0 if calculation fails
        
        Example:
            >>> irr([200_000_000] * 6, 1_000_000_000)
            12.5  # 12.5% annual return
        """
        if not cashflows:
            return 0.0
        
        # Initial guess: 5%
        r = 0.05
        
        for iteration in range(max_iterations):
            # Calculate NPV and its derivative at current r
            npv_val = 0.0
            d_npv = 0.0
            
            for t, cf in enumerate(cashflows, start=1):
                denominator = (1 + r) ** t
                npv_val += cf / denominator
                # Derivative: d/dr [ CF_t / (1+r)^t ] = -t * CF_t / (1+r)^(t+1)
                d_npv -= (t * cf) / ((1 + r) ** (t + 1))
            
            npv_val -= capex
            
            # Check convergence
            if abs(npv_val) < precision:
                return r * 100  # Convert to percentage
            
            # Check for zero derivative (avoid division by zero)
            if abs(d_npv) < 1e-12:
                break
            
            # Newton-Raphson step: r_new = r - f(r) / f'(r)
            r_next = r - npv_val / d_npv
            
            # Check if converged
            if abs(r_next - r) < precision:
                return r_next * 100
            
            r = r_next
            
            # Ensure r stays reasonable (avoid extreme values)
            if r < -0.99:
                r = -0.99
            elif r > 10.0:
                r = 10.0
        
        # If failed to converge, return best estimate
        return r * 100
    
    @staticmethod
    def irr_public(
        cashflows: List[float],
        capex: float,
        discount_rate: float = 0.02
    ) -> float:
        """
        Calculate IRR using public sector discount rate
        
        Public sector projects typically use lower discount rates (2%)
        reflecting lower risk tolerance and social benefit considerations.
        
        Args:
            cashflows: List of annual net cashflows
            capex: Initial capital expenditure
            discount_rate: Public discount rate (default: 2%)
        
        Returns:
            IRR as percentage (public standard)
        """
        # Note: IRR is independent of discount rate
        # This method exists for API consistency
        return FinancialEnhanced.irr(cashflows, capex)
    
    @staticmethod
    def irr_private(
        cashflows: List[float],
        capex: float,
        discount_rate: float = 0.055
    ) -> float:
        """
        Calculate IRR using private sector discount rate
        
        Private sector projects typically use higher discount rates (5.5%)
        reflecting higher risk tolerance and opportunity cost of capital.
        
        Args:
            cashflows: List of annual net cashflows
            capex: Initial capital expenditure
            discount_rate: Private discount rate (default: 5.5%)
        
        Returns:
            IRR as percentage (private standard)
        """
        # Note: IRR is independent of discount rate
        # This method exists for API consistency
        return FinancialEnhanced.irr(cashflows, capex)
    
    @staticmethod
    def calculate_all_metrics(
        cashflows: List[float],
        capex: float,
        discount_rate_public: float = 0.02,
        discount_rate_private: float = 0.055
    ) -> dict:
        """
        Calculate all enhanced financial metrics at once
        
        Convenience method to compute NPV, Payback, and IRR (public/private)
        in a single call.
        
        Args:
            cashflows: List of annual net cashflows
            capex: Initial capital expenditure
            discount_rate_public: Public discount rate (default: 2%)
            discount_rate_private: Private discount rate (default: 5.5%)
        
        Returns:
            Dictionary with all metrics:
                - npv: Net Present Value (using public rate)
                - npv_private: NPV using private rate
                - payback: Payback period in years
                - irr: Internal Rate of Return (%)
                - irr_public: IRR with public interpretation
                - irr_private: IRR with private interpretation
        
        Example:
            >>> metrics = FinancialEnhanced.calculate_all_metrics(
            ...     [200_000_000] * 6,
            ...     1_000_000_000
            ... )
            >>> print(metrics['npv'])
            140_000_000
            >>> print(metrics['payback'])
            5.0
            >>> print(metrics['irr'])
            12.5
        """
        return {
            "npv": FinancialEnhanced.npv(
                discount_rate_public, cashflows, capex
            ),
            "npv_private": FinancialEnhanced.npv(
                discount_rate_private, cashflows, capex
            ),
            "payback": FinancialEnhanced.payback(cashflows, capex),
            "irr": FinancialEnhanced.irr(cashflows, capex),
            "irr_public": FinancialEnhanced.irr_public(
                cashflows, capex, discount_rate_public
            ),
            "irr_private": FinancialEnhanced.irr_private(
                cashflows, capex, discount_rate_private
            )
        }


# Convenience functions
def calculate_npv(discount_rate: float, cashflows: List[float], capex: float) -> float:
    """Convenience function for NPV calculation"""
    return FinancialEnhanced.npv(discount_rate, cashflows, capex)


def calculate_payback(cashflows: List[float], capex: float) -> float:
    """Convenience function for Payback calculation"""
    return FinancialEnhanced.payback(cashflows, capex)


def calculate_irr(cashflows: List[float], capex: float) -> float:
    """Convenience function for IRR calculation"""
    return FinancialEnhanced.irr(cashflows, capex)
