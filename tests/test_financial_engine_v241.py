"""Tests for Financial Engine v24.1"""
import pytest
from app.engines.financial_engine_v241 import FinancialEngineV241, assess_financial_performance
from app.config.financial_config import get_discount_rate


class TestFinancialEngineV241:
    @pytest.fixture
    def engine(self):
        return FinancialEngineV241()
    
    def test_initialization(self, engine):
        assert engine.version == "24.1.0"
        assert engine.discount_rate == 0.05
    
    def test_payback_period_calculation(self, engine):
        result = engine.calculate_payback_period(
            initial_investment=5_000_000_000,
            annual_cashflows=[1_000_000_000] * 8
        )
        assert result.simple_payback_years > 0
        assert result.discounted_payback_years > result.simple_payback_years
        assert result.assessment in ['EXCELLENT', 'GOOD', 'ACCEPTABLE', 'POOR']
    
    def test_sensitivity_analysis(self, engine):
        base_case = {
            'construction_cost': 3_500_000_000,
            'land_acquisition_cost': 2_000_000_000,
            'revenue_per_unit': 250_000_000,
            'total_units': 40,
            'total_investment': 5_500_000_000,
            'total_revenue': 10_000_000_000
        }
        result = engine.perform_sensitivity_analysis(base_case)
        assert 'base_npv' in result
        assert 'sensitivity_results' in result
        assert len(result['sensitivity_results']) > 0
    
    def test_npv_calculation(self, engine):
        npv = engine.calculate_npv(
            initial_investment=5_000_000_000,
            annual_cashflows=[1_500_000_000] * 5
        )
        assert isinstance(npv, float)
    
    def test_irr_calculation(self, engine):
        irr = engine.calculate_irr(
            initial_investment=5_000_000_000,
            annual_cashflows=[1_500_000_000] * 5
        )
        assert 0 < irr < 1
