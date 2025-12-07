"""
ZeroSite v15 Phase 1 (S-Grade) Services
Government Submission Decision Engine

New Components:
- Decision Tree Generator: Transparent GO/NO-GO logic
- Condition Generator: C1-C4 condition table
- Risk Response Generator: Mitigation strategy matrix
- KPI Generator: 4 executive KPI cards

Purpose: Elevate from "report generator" to "policy decision engine"
"""

from .decision_tree_generator import DecisionTreeGenerator
from .condition_generator import ConditionGenerator as ConditionTableGenerator
from .risk_response_generator import RiskResponseGenerator
from .kpi_generator import KPIGenerator as KPICardGenerator

# v15 Phase 2 components
from .simulation_engine import SimulationEngine, get_simulation_engine
from .sensitivity_chart_generator import SensitivityChartGenerator, get_sensitivity_chart_generator
from .lh_approval_model import LHApprovalModel, get_lh_approval_model
from .government_decision_page import GovernmentDecisionPageGenerator, get_government_decision_page_generator

__all__ = [
    # Phase 1
    'DecisionTreeGenerator',
    'ConditionTableGenerator',
    'RiskResponseGenerator',
    'KPICardGenerator',
    # Phase 2
    'SimulationEngine',
    'SensitivityChartGenerator',
    'LHApprovalModel',
    'GovernmentDecisionPageGenerator',
    'get_simulation_engine',
    'get_sensitivity_chart_generator',
    'get_lh_approval_model',
    'get_government_decision_page_generator'
]

__version__ = '15.0.0'
__author__ = 'ZeroSite Development Team'
