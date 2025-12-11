#!/usr/bin/env python3
"""
GenSpark AI Prompt Generator for Expert v3.2
=============================================
Intelligent prompt generation for AI-powered expert insights

Features:
- Extracts key metrics from v3.2 report data
- Generates structured prompts for GenSpark AI
- Supports multiple prompt types (analysis, recommendations, risk assessment)
- Optimized for LH land acquisition context

Author: ZeroSite v3.2 Development Team
Version: 3.2.0
Date: 2025-12-11
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class GenSparkPromptGenerator:
    """
    GenSpark AI Prompt Generator
    
    Generates intelligent, context-aware prompts for GenSpark AI
    based on Expert v3.2 report data.
    
    Capabilities:
    - Financial analysis prompts
    - A/B scenario comparison prompts
    - Risk assessment prompts
    - Market insights prompts
    - Final recommendation prompts
    """
    
    def __init__(self):
        """Initialize GenSpark Prompt Generator"""
        self.version = "3.2.0"
        self.prompt_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize prompt templates"""
        return {
            "financial_analysis": """
# Financial Analysis Request for LH Land Acquisition

## Project Overview
- **Address**: {address}
- **Land Area**: {land_area_sqm}㎡ ({land_area_pyeong}평)
- **Legal FAR**: {far_legal}%
- **Market Price**: ₩{market_price:,.0f}/㎡

## Financial Metrics
### Scenario A (Youth Housing)
- Total CAPEX: ₩{scenario_a_capex:.1f}억원
- LH Purchase Price: ₩{scenario_a_lh_price:.1f}억원
- Project Profit: ₩{scenario_a_profit:.1f}억원
- ROI: {scenario_a_roi:.2f}%
- IRR: {scenario_a_irr:.2f}%
- Decision: {scenario_a_decision}

### Scenario B (Newlywed Housing)
- Total CAPEX: ₩{scenario_b_capex:.1f}억원
- LH Purchase Price: ₩{scenario_b_lh_price:.1f}억원
- Project Profit: ₩{scenario_b_profit:.1f}억원
- ROI: {scenario_b_roi:.2f}%
- IRR: {scenario_b_irr:.2f}%
- Decision: {scenario_b_decision}

## Analysis Request
Please provide a comprehensive financial analysis focusing on:

1. **Financial Viability Assessment**
   - Evaluate the ROI and IRR for both scenarios
   - Assess profitability given current market conditions
   - Compare against typical LH project benchmarks (target ROI: 5-8%)

2. **Risk Analysis**
   - Identify key financial risks for each scenario
   - Assess sensitivity to construction cost variations
   - Evaluate market price risk

3. **Comparative Analysis**
   - Which scenario offers better financial returns?
   - What are the trade-offs between the two scenarios?
   - How do unit count differences impact overall profitability?

4. **Recommendations**
   - Which scenario would you recommend from a financial perspective?
   - What are the key financial considerations for LH decision-makers?
   - Any suggestions for improving financial outcomes?

Please provide analysis in Korean (한국어) suitable for LH executives.
""",
            
            "scenario_comparison": """
# A/B Scenario Comparison Analysis - LH Land Acquisition

## Project Context
- **Location**: {address}
- **Land Area**: {land_area_sqm}㎡ ({land_area_pyeong}평)
- **Analysis Date**: {analysis_date}

## Scenario A: Youth Housing (청년 주택)
- **Target**: Youth (19-39 years old)
- **Unit Size**: {scenario_a_unit_size}㎡ ({scenario_a_unit_pyeong}평)
- **Total Units**: {scenario_a_unit_count}
- **FAR**: {scenario_a_far_legal}% → {scenario_a_far_final}% (+{scenario_a_far_relaxation}%p)
- **Floors**: {scenario_a_floors}층
- **CAPEX**: ₩{scenario_a_capex:.1f}억원
- **ROI**: {scenario_a_roi:.2f}%
- **AI Demand Score**: {scenario_a_demand_score:.1f}/100
- **Decision**: {scenario_a_decision}

## Scenario B: Newlywed Housing (신혼부부 주택)
- **Target**: Newlywed couples
- **Unit Size**: {scenario_b_unit_size}㎡ ({scenario_b_unit_pyeong}평)
- **Total Units**: {scenario_b_unit_count}
- **FAR**: {scenario_b_far_legal}% → {scenario_b_far_final}% (+{scenario_b_far_relaxation}%p)
- **Floors**: {scenario_b_floors}층
- **CAPEX**: ₩{scenario_b_capex:.1f}억원
- **ROI**: {scenario_b_roi:.2f}%
- **AI Demand Score**: {scenario_b_demand_score:.1f}/100
- **Decision**: {scenario_b_decision}

## Current Recommendation
**System Recommendation**: {recommended_scenario}
**Reasoning**: {recommendation_rationale}

## Analysis Request
As an expert in Korean public housing policy and LH land acquisition, please provide:

1. **Policy Alignment Assessment**
   - Which scenario better aligns with current Korean housing policy priorities?
   - Evaluate in context of youth housing crisis and newlywed housing needs
   - Consider government housing supply targets

2. **Market Demand Analysis**
   - Assess demand for youth housing (19-39) vs. newlywed housing in this location
   - Consider demographic trends and housing preferences
   - Evaluate long-term marketability

3. **Social Impact Evaluation**
   - Which scenario delivers greater social benefit?
   - Consider housing supply contribution to target demographics
   - Evaluate accessibility and affordability

4. **Architectural & Urban Planning Perspective**
   - Assess FAR utilization efficiency
   - Evaluate unit mix appropriateness for location
   - Consider building scale and neighborhood impact

5. **Final Expert Recommendation**
   - Do you agree with the system recommendation?
   - What are the key factors supporting your recommendation?
   - Any alternative approaches to consider?

Please provide analysis in Korean (한국어) with professional terminology suitable for LH executives and policymakers.
""",
            
            "risk_assessment": """
# Risk Assessment Request - LH Land Acquisition Project

## Project Summary
- **Address**: {address}
- **Land Area**: {land_area_sqm}㎡
- **Market Price**: ₩{market_price:,.0f}/㎡
- **Market Confidence**: {market_confidence}

## Financial Risk Indicators
### Scenario A (Youth)
- ROI: {scenario_a_roi:.2f}% (Target: 5-8%)
- Profit: ₩{scenario_a_profit:.1f}억원
- Financial Decision: {scenario_a_decision}

### Scenario B (Newlywed)
- ROI: {scenario_b_roi:.2f}% (Target: 5-8%)
- Profit: ₩{scenario_b_profit:.1f}억원
- Financial Decision: {scenario_b_decision}

## Risk Assessment Request
Please conduct a comprehensive risk analysis covering:

1. **Financial Risks**
   - Profitability risk (negative or low ROI)
   - Construction cost overrun risk
   - LH purchase price uncertainty
   - Market price volatility

2. **Market Risks**
   - Location-specific risks
   - Market confidence level: {market_confidence}
   - Demand uncertainty for target demographics
   - Competition from nearby projects

3. **Policy & Regulatory Risks**
   - FAR relaxation approval uncertainty
   - Zoning regulation changes
   - LH policy changes
   - Government housing policy shifts

4. **Project Execution Risks**
   - Timeline delays
   - Construction quality issues
   - Contractor default risk
   - Material shortage/inflation

5. **Risk Mitigation Strategies**
   - For each major risk, suggest mitigation measures
   - Prioritize top 3 risks requiring immediate attention
   - Recommend risk monitoring framework

Please provide analysis in Korean (한국어) with actionable recommendations for LH risk management team.
""",
            
            "market_insights": """
# Market Insights Request - Seoul Real Estate Market

## Project Location
- **Address**: {address}
- **Land Price**: ₩{market_price:,.0f}/㎡
- **Market Data Confidence**: {market_confidence}
- **Transaction Count**: {market_transaction_count}

## Market Statistics
- **Mean Price**: ₩{market_mean_price:,.0f}/㎡
- **Median Price**: ₩{market_median_price:,.0f}/㎡
- **Standard Deviation**: ₩{market_std_dev:,.0f}
- **Price Range**: ₩{market_min_price:,.0f} ~ ₩{market_max_price:,.0f}
- **Coefficient of Variation**: {market_cv:.1f}%

## Housing Supply Context
- **Youth Housing Units**: {scenario_a_unit_count}
- **Newlywed Housing Units**: {scenario_b_unit_count}

## Market Insights Request
Please provide expert market analysis focusing on:

1. **Location Market Dynamics**
   - Assess current market conditions in this specific area
   - Evaluate price trends and momentum
   - Compare to broader Seoul market trends

2. **Target Demographic Demand**
   - Youth (19-39) housing demand in this location
   - Newlywed couple housing demand
   - Income levels and affordability considerations

3. **Competitive Landscape**
   - Existing and planned public housing in the area
   - Private market competition
   - Supply-demand balance

4. **Price Reasonableness**
   - Is the current market price (₩{market_price:,.0f}/㎡) reasonable?
   - Price appreciation/depreciation outlook
   - Optimal timing for land acquisition

5. **Market Recommendations**
   - Is this a good location for LH land acquisition?
   - Which housing type (youth vs. newlywed) has stronger market fundamentals?
   - Strategic considerations for LH

Please provide analysis in Korean (한국어) with data-driven insights for LH market research team.
""",
            
            "executive_summary": """
# Executive Summary Request - LH Land Acquisition Decision

## Project Overview
**Address**: {address}  
**Land Area**: {land_area_sqm}㎡ ({land_area_pyeong}평)  
**Analysis Date**: {analysis_date}

## Quick Comparison

| Metric | Scenario A (Youth) | Scenario B (Newlywed) | Winner |
|--------|-------------------|----------------------|--------|
| Units | {scenario_a_unit_count} | {scenario_b_unit_count} | {unit_count_winner} |
| FAR | {scenario_a_far_final}% | {scenario_b_far_final}% | {far_winner} |
| CAPEX | ₩{scenario_a_capex:.1f}억 | ₩{scenario_b_capex:.1f}억 | {capex_winner} |
| ROI | {scenario_a_roi:.2f}% | {scenario_b_roi:.2f}% | {roi_winner} |
| Decision | {scenario_a_decision} | {scenario_b_decision} | - |

**System Recommendation**: {recommended_scenario}

## Executive Summary Request
Please provide a concise executive summary (maximum 500 words) suitable for LH CEO and executive committee covering:

1. **Strategic Recommendation**
   - Clear GO/NO-GO recommendation with confidence level
   - Which scenario to pursue (Youth vs. Newlywed) and why
   - Key decision factors

2. **Financial Outlook**
   - Expected ROI and profitability assessment
   - Financial risks and mitigation strategies
   - Budget requirements and approval considerations

3. **Policy & Social Impact**
   - Alignment with Korean housing policy
   - Expected social benefit and impact
   - Public perception considerations

4. **Implementation Priorities**
   - Top 3 action items if project is approved
   - Timeline and resource requirements
   - Critical success factors

5. **Risk Alert**
   - Top 3 risks that require executive attention
   - Deal-breaker risks (if any)
   - Risk mitigation measures

Please write in formal business Korean (한국어) suitable for C-level executives. Be direct, data-driven, and actionable.
"""
        }
    
    def generate_financial_analysis_prompt(self, report_data: Dict) -> str:
        """
        Generate financial analysis prompt
        
        Args:
            report_data: Complete report data from Expert v3.2 generator
        
        Returns:
            Formatted prompt string for GenSpark AI
        """
        template = self.prompt_templates["financial_analysis"]
        
        # Extract and format data
        prompt_data = self._extract_prompt_data(report_data)
        
        # Format the prompt
        try:
            prompt = template.format(**prompt_data)
            return prompt
        except KeyError as e:
            raise ValueError(f"Missing required data field for prompt generation: {e}")
    
    def generate_scenario_comparison_prompt(self, report_data: Dict) -> str:
        """
        Generate A/B scenario comparison prompt
        
        Args:
            report_data: Complete report data from Expert v3.2 generator
        
        Returns:
            Formatted prompt string for GenSpark AI
        """
        template = self.prompt_templates["scenario_comparison"]
        prompt_data = self._extract_prompt_data(report_data)
        
        try:
            prompt = template.format(**prompt_data)
            return prompt
        except KeyError as e:
            raise ValueError(f"Missing required data field for prompt generation: {e}")
    
    def generate_risk_assessment_prompt(self, report_data: Dict) -> str:
        """
        Generate risk assessment prompt
        
        Args:
            report_data: Complete report data from Expert v3.2 generator
        
        Returns:
            Formatted prompt string for GenSpark AI
        """
        template = self.prompt_templates["risk_assessment"]
        prompt_data = self._extract_prompt_data(report_data)
        
        try:
            prompt = template.format(**prompt_data)
            return prompt
        except KeyError as e:
            raise ValueError(f"Missing required data field for prompt generation: {e}")
    
    def generate_market_insights_prompt(self, report_data: Dict) -> str:
        """
        Generate market insights prompt
        
        Args:
            report_data: Complete report data from Expert v3.2 generator
        
        Returns:
            Formatted prompt string for GenSpark AI
        """
        template = self.prompt_templates["market_insights"]
        prompt_data = self._extract_prompt_data(report_data)
        
        try:
            prompt = template.format(**prompt_data)
            return prompt
        except KeyError as e:
            raise ValueError(f"Missing required data field for prompt generation: {e}")
    
    def generate_executive_summary_prompt(self, report_data: Dict) -> str:
        """
        Generate executive summary prompt
        
        Args:
            report_data: Complete report data from Expert v3.2 generator
        
        Returns:
            Formatted prompt string for GenSpark AI
        """
        template = self.prompt_templates["executive_summary"]
        prompt_data = self._extract_prompt_data(report_data)
        
        try:
            prompt = template.format(**prompt_data)
            return prompt
        except KeyError as e:
            raise ValueError(f"Missing required data field for prompt generation: {e}")
    
    def generate_all_prompts(self, report_data: Dict) -> Dict[str, str]:
        """
        Generate all prompt types
        
        Args:
            report_data: Complete report data from Expert v3.2 generator
        
        Returns:
            Dictionary with all prompts by type
        """
        return {
            "financial_analysis": self.generate_financial_analysis_prompt(report_data),
            "scenario_comparison": self.generate_scenario_comparison_prompt(report_data),
            "risk_assessment": self.generate_risk_assessment_prompt(report_data),
            "market_insights": self.generate_market_insights_prompt(report_data),
            "executive_summary": self.generate_executive_summary_prompt(report_data)
        }
    
    def _extract_prompt_data(self, report_data: Dict) -> Dict:
        """
        Extract and format data for prompt generation
        
        Args:
            report_data: Raw report data from Expert v3.2
        
        Returns:
            Formatted data dictionary for prompt templates
        """
        # Get metadata and section data
        metadata = report_data.get('metadata', {})
        section_data = report_data.get('section_03_1_data', {})
        
        # Extract scenario A data
        scenario_a_capex = section_data.get('scenario_a_total_capex', 0) / 100_000_000  # Convert to 억원
        scenario_a_lh_price = section_data.get('scenario_a_lh_price', 0) / 100_000_000
        scenario_a_profit = section_data.get('scenario_a_profit', 0) / 100_000_000
        
        # Extract scenario B data
        scenario_b_capex = section_data.get('scenario_b_total_capex', 0) / 100_000_000
        scenario_b_lh_price = section_data.get('scenario_b_lh_price', 0) / 100_000_000
        scenario_b_profit = section_data.get('scenario_b_profit', 0) / 100_000_000
        
        # Compile formatted data
        prompt_data = {
            # Basic info
            'address': metadata.get('address', 'N/A'),
            'land_area_sqm': metadata.get('land_area_sqm', 0),
            'land_area_pyeong': metadata.get('land_area_pyeong', 0),
            'far_legal': metadata.get('far_legal', 0),
            'market_price': metadata.get('market_price_per_sqm', 0),
            'market_confidence': metadata.get('market_confidence', 'UNKNOWN'),
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            
            # Scenario A (Youth)
            'scenario_a_unit_size': section_data.get('scenario_a_unit_size', 0),
            'scenario_a_unit_pyeong': section_data.get('scenario_a_unit_pyeong', 0),
            'scenario_a_unit_count': section_data.get('scenario_a_unit_count', 0),
            'scenario_a_far_legal': section_data.get('scenario_a_far_legal', 0),
            'scenario_a_far_final': section_data.get('scenario_a_far_final', 0),
            'scenario_a_far_relaxation': section_data.get('scenario_a_far_relaxation', 0),
            'scenario_a_floors': section_data.get('scenario_a_floors', 0),
            'scenario_a_capex': scenario_a_capex,
            'scenario_a_lh_price': scenario_a_lh_price,
            'scenario_a_profit': scenario_a_profit,
            'scenario_a_roi': section_data.get('scenario_a_roi', 0),
            'scenario_a_irr': section_data.get('scenario_a_irr', 0),
            'scenario_a_demand_score': section_data.get('scenario_a_demand_score', 0),
            'scenario_a_decision': section_data.get('scenario_a_decision', 'UNKNOWN'),
            
            # Scenario B (Newlywed)
            'scenario_b_unit_size': section_data.get('scenario_b_unit_size', 0),
            'scenario_b_unit_pyeong': section_data.get('scenario_b_unit_pyeong', 0),
            'scenario_b_unit_count': section_data.get('scenario_b_unit_count', 0),
            'scenario_b_far_legal': section_data.get('scenario_b_far_legal', 0),
            'scenario_b_far_final': section_data.get('scenario_b_far_final', 0),
            'scenario_b_far_relaxation': section_data.get('scenario_b_far_relaxation', 0),
            'scenario_b_floors': section_data.get('scenario_b_floors', 0),
            'scenario_b_capex': scenario_b_capex,
            'scenario_b_lh_price': scenario_b_lh_price,
            'scenario_b_profit': scenario_b_profit,
            'scenario_b_roi': section_data.get('scenario_b_roi', 0),
            'scenario_b_irr': section_data.get('scenario_b_irr', 0),
            'scenario_b_demand_score': section_data.get('scenario_b_demand_score', 0),
            'scenario_b_decision': section_data.get('scenario_b_decision', 'UNKNOWN'),
            
            # Recommendation
            'recommended_scenario': section_data.get('recommended_scenario', 'N/A'),
            'recommendation_rationale': section_data.get('recommendation_rationale', 'N/A'),
            
            # Market data
            'market_transaction_count': section_data.get('market_transaction_count', 0),
            'market_mean_price': section_data.get('market_mean_price', 0),
            'market_median_price': section_data.get('market_median_price', 0),
            'market_std_dev': section_data.get('market_std_dev', 0),
            'market_min_price': section_data.get('market_min_price', 0),
            'market_max_price': section_data.get('market_max_price', 0),
            'market_cv': section_data.get('market_cv', 0),
            
            # Winners (for comparison table)
            'unit_count_winner': 'A' if section_data.get('scenario_a_unit_count', 0) > section_data.get('scenario_b_unit_count', 0) else 'B',
            'far_winner': 'A' if section_data.get('scenario_a_far_final', 0) > section_data.get('scenario_b_far_final', 0) else 'B',
            'capex_winner': 'B' if scenario_b_capex < scenario_a_capex else 'A',  # Lower is better
            'roi_winner': 'A' if section_data.get('scenario_a_roi', 0) > section_data.get('scenario_b_roi', 0) else 'B',
        }
        
        return prompt_data


# Test function
if __name__ == "__main__":
    # Sample report data for testing
    sample_data = {
        'metadata': {
            'address': '서울특별시 마포구 월드컵북로 120',
            'land_area_sqm': 660.0,
            'land_area_pyeong': 200.0,
            'far_legal': 300.0,
            'market_price_per_sqm': 9_500_000,
            'market_confidence': 'LOW'
        },
        'section_03_1_data': {
            'scenario_a_unit_size': 60.0,
            'scenario_a_unit_pyeong': 18.2,
            'scenario_a_unit_count': 30,
            'scenario_a_far_legal': 300.0,
            'scenario_a_far_final': 350.0,
            'scenario_a_far_relaxation': 50.0,
            'scenario_a_floors': 15,
            'scenario_a_total_capex': 17_810_000_000,
            'scenario_a_lh_price': 13_859_000_000,
            'scenario_a_profit': -2_691_000_000,
            'scenario_a_roi': 9.50,
            'scenario_a_irr': -10.0,
            'scenario_a_demand_score': 68.0,
            'scenario_a_decision': 'GO',
            
            'scenario_b_unit_size': 85.0,
            'scenario_b_unit_pyeong': 25.7,
            'scenario_b_unit_count': 20,
            'scenario_b_far_legal': 300.0,
            'scenario_b_far_final': 330.0,
            'scenario_b_far_relaxation': 30.0,
            'scenario_b_floors': 12,
            'scenario_b_total_capex': 17_170_000_000,
            'scenario_b_lh_price': 13_200_000_000,
            'scenario_b_profit': -800_000_000,
            'scenario_b_roi': -6.79,
            'scenario_b_irr': -8.0,
            'scenario_b_demand_score': 71.0,
            'scenario_b_decision': 'NO-GO',
            
            'recommended_scenario': 'B',
            'recommendation_rationale': '신혼부부 주택이 정책 점수가 더 높아 권장됩니다.',
            
            'market_transaction_count': 10,
            'market_mean_price': 9_500_000,
            'market_median_price': 9_700_000,
            'market_std_dev': 760_000,
            'market_min_price': 8_550_000,
            'market_max_price': 10_925_000,
            'market_cv': 8.0,
        }
    }
    
    # Test prompt generator
    generator = GenSparkPromptGenerator()
    
    print("="*80)
    print("GenSpark Prompt Generator - Test Output")
    print("="*80)
    
    # Test financial analysis prompt
    print("\n1. FINANCIAL ANALYSIS PROMPT")
    print("-"*80)
    financial_prompt = generator.generate_financial_analysis_prompt(sample_data)
    print(financial_prompt[:500] + "...")
    print(f"\nPrompt length: {len(financial_prompt)} characters")
    
    # Test scenario comparison prompt
    print("\n2. SCENARIO COMPARISON PROMPT")
    print("-"*80)
    comparison_prompt = generator.generate_scenario_comparison_prompt(sample_data)
    print(comparison_prompt[:500] + "...")
    print(f"\nPrompt length: {len(comparison_prompt)} characters")
    
    # Test all prompts
    print("\n3. ALL PROMPTS GENERATED")
    print("-"*80)
    all_prompts = generator.generate_all_prompts(sample_data)
    for prompt_type, prompt in all_prompts.items():
        print(f"  ✅ {prompt_type}: {len(prompt):,} characters")
    
    print("\n" + "="*80)
    print("✅ GenSpark Prompt Generator is ready!")
    print("="*80)
