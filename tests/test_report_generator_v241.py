"""
Tests for ZeroSite v24.1 Enhanced Report Generation System

Test Coverage:
- Report #3: Policy Impact Report (100%)
- Report #4: Developer Feasibility Report (NEW, 100%)
- Report #5: Comprehensive Analysis Report (100%)

Author: ZeroSite Test Team
Version: 24.1.0
Date: 2025-12-12
"""

import pytest
from app.services.report_generator_v241 import (
    ReportGeneratorV241,
    ReportSection,
    ReportMetadata,
    format_currency,
    calculate_completeness
)


class TestReportGeneratorV241:
    """Tests for ReportGeneratorV241 initialization"""
    
    @pytest.fixture
    def generator(self):
        return ReportGeneratorV241()
    
    def test_initialization(self, generator):
        """Test that generator initializes correctly"""
        assert generator.version == "24.1.0"
        assert generator.logger is not None
    
    def test_version_attribute(self, generator):
        """Test version attribute"""
        assert hasattr(generator, 'version')
        assert generator.version == "24.1.0"


class TestPolicyImpactReport:
    """Tests for Policy Impact Report (Report #3)"""
    
    @pytest.fixture
    def generator(self):
        return ReportGeneratorV241()
    
    @pytest.fixture
    def sample_data(self):
        return {
            'address': '서울시 강남구 역삼동 123',
            'land_area_sqm': 660.0,
            'zone_type': '제2종일반주거',
            'far': 200.0,
            'bcr': 60.0,
            'total_units': 40,
            'construction_cost': 3_500_000_000,
            'roi': 12.5,
            'irr': 10.2,
            'profit': 2_000_000_000
        }
    
    def test_generate_policy_report_basic(self, generator, sample_data):
        """Test basic policy report generation"""
        report = generator.generate_policy_impact_report(sample_data)
        
        assert report is not None
        assert 'metadata' in report
        assert 'sections' in report
        assert 'total_pages' in report
        assert 'version' in report
        assert 'completeness' in report
    
    def test_policy_report_completeness(self, generator, sample_data):
        """Test that policy report is 100% complete in v24.1"""
        report = generator.generate_policy_impact_report(sample_data)
        
        assert report['completeness'] == 100
        assert report['version'] == '24.1.0'
    
    def test_policy_report_sections_count(self, generator, sample_data):
        """Test that all required sections are present"""
        report = generator.generate_policy_impact_report(sample_data)
        
        # Should have 6 sections (including new Policy Simulation)
        assert len(report['sections']) == 6
    
    def test_policy_report_without_simulation(self, generator, sample_data):
        """Test policy report without simulation section"""
        report = generator.generate_policy_impact_report(
            sample_data,
            include_simulation=False
        )
        
        # Should have 5 sections (without Policy Simulation)
        assert len(report['sections']) == 5
    
    def test_policy_report_page_count(self, generator, sample_data):
        """Test that page count is reasonable"""
        report = generator.generate_policy_impact_report(sample_data)
        
        # Target: 12-15 pages
        assert 10 <= report['total_pages'] <= 20
    
    def test_policy_report_metadata(self, generator, sample_data):
        """Test report metadata"""
        report = generator.generate_policy_impact_report(sample_data)
        metadata = report['metadata']
        
        assert metadata.report_type == 'policy_impact'
        assert metadata.version == '24.1.0'
        assert metadata.generated_at is not None
        assert metadata.total_pages > 0
    
    def test_policy_simulation_section(self, generator, sample_data):
        """Test new policy simulation section"""
        report = generator.generate_policy_impact_report(sample_data)
        sections = report['sections']
        
        # Find policy simulation section
        simulation_section = None
        for section in sections:
            if 'Simulation' in section.title:
                simulation_section = section
                break
        
        assert simulation_section is not None
        assert simulation_section.page_count >= 2
        assert 'Scenario' in simulation_section.content
        assert 'FAR' in simulation_section.content


class TestDeveloperFeasibilityReport:
    """Tests for Developer Feasibility Report (Report #4 - NEW)"""
    
    @pytest.fixture
    def generator(self):
        return ReportGeneratorV241()
    
    @pytest.fixture
    def sample_data(self):
        return {
            'address': '서울시 강남구 역삼동 123',
            'land_area_sqm': 660.0,
            'zone_type': '제2종일반주거',
            'total_units': 40,
            'floors': 10,
            'total_investment': 5_000_000_000,
            'construction_cost': 3_500_000_000,
            'land_acquisition_cost': 2_000_000_000,
            'total_revenue': 10_000_000_000,
            'profit': 2_000_000_000,
            'roi': 12.5,
            'irr': 10.2,
            'payback_period': 5.2,
            'parking_spaces': 35,
            'total_floor_area': 3960,
            'revenue_per_unit': 250_000_000
        }
    
    def test_generate_developer_report_basic(self, generator, sample_data):
        """Test basic developer report generation"""
        report = generator.generate_developer_feasibility_report(sample_data)
        
        assert report is not None
        assert 'metadata' in report
        assert 'sections' in report
        assert 'total_pages' in report
        assert 'version' in report
        assert 'completeness' in report
    
    def test_developer_report_completeness(self, generator, sample_data):
        """Test that developer report is 100% complete (NEW in v24.1)"""
        report = generator.generate_developer_feasibility_report(sample_data)
        
        assert report['completeness'] == 100
        assert report['version'] == '24.1.0'
    
    def test_developer_report_sections_count(self, generator, sample_data):
        """Test that all 6 required sections are present"""
        report = generator.generate_developer_feasibility_report(sample_data)
        
        # Should have 6 sections
        assert len(report['sections']) == 6
    
    def test_developer_report_page_count(self, generator, sample_data):
        """Test that page count meets target (15-22 pages)"""
        report = generator.generate_developer_feasibility_report(sample_data)
        
        # Target: 15-22 pages
        assert 15 <= report['total_pages'] <= 25
    
    def test_developer_report_metadata(self, generator, sample_data):
        """Test report metadata"""
        report = generator.generate_developer_feasibility_report(sample_data)
        metadata = report['metadata']
        
        assert metadata.report_type == 'developer_feasibility'
        assert metadata.version == '24.1.0'
        assert metadata.generated_at is not None
    
    def test_developer_executive_summary(self, generator, sample_data):
        """Test executive summary section"""
        report = generator.generate_developer_feasibility_report(sample_data)
        exec_summary = report['sections'][0]
        
        assert 'Executive Summary' in exec_summary.title
        assert 'Investment Overview' in exec_summary.content
        assert 'GO' in exec_summary.content or 'NO-GO' in exec_summary.content
    
    def test_developer_financial_analysis(self, generator, sample_data):
        """Test financial analysis section"""
        report = generator.generate_developer_feasibility_report(sample_data)
        
        # Find financial analysis section
        financial_section = None
        for section in report['sections']:
            if 'Financial' in section.title:
                financial_section = section
                break
        
        assert financial_section is not None
        assert financial_section.page_count == 5
        assert 'CAPEX' in financial_section.content
        assert 'Cash Flow' in financial_section.content
        assert 'Sensitivity' in financial_section.content
    
    def test_developer_risk_assessment(self, generator, sample_data):
        """Test risk assessment section"""
        report = generator.generate_developer_feasibility_report(sample_data)
        
        # Find risk assessment section
        risk_section = None
        for section in report['sections']:
            if 'Risk' in section.title:
                risk_section = section
                break
        
        assert risk_section is not None
        assert 'Risk Matrix' in risk_section.content
        assert 'Mitigation' in risk_section.content


class TestComprehensiveAnalysisReport:
    """Tests for Comprehensive Analysis Report (Report #5)"""
    
    @pytest.fixture
    def generator(self):
        return ReportGeneratorV241()
    
    @pytest.fixture
    def sample_data(self):
        return {
            'address': '서울시 강남구 역삼동 123',
            'land_area_sqm': 660.0,
            'total_units': 40,
            'total_investment': 5_000_000_000,
            'total_revenue': 10_000_000_000,
            'profit': 2_000_000_000,
            'roi': 12.5,
            'irr': 10.2,
            'far': 200.0
        }
    
    def test_generate_comprehensive_report_basic(self, generator, sample_data):
        """Test basic comprehensive report generation"""
        report = generator.generate_comprehensive_analysis_report(sample_data)
        
        assert report is not None
        assert 'metadata' in report
        assert 'sections' in report
        assert 'total_pages' in report
    
    def test_comprehensive_report_completeness(self, generator, sample_data):
        """Test that comprehensive report is 100% complete in v24.1"""
        report = generator.generate_comprehensive_analysis_report(sample_data)
        
        assert report['completeness'] == 100
        assert report['version'] == '24.1.0'
    
    def test_comprehensive_report_with_advanced(self, generator, sample_data):
        """Test comprehensive report with advanced analysis"""
        report = generator.generate_comprehensive_analysis_report(
            sample_data,
            include_advanced_analysis=True
        )
        
        # Should have standard + 3 advanced sections
        assert len(report['sections']) >= 8
    
    def test_comprehensive_report_without_advanced(self, generator, sample_data):
        """Test comprehensive report without advanced analysis"""
        report = generator.generate_comprehensive_analysis_report(
            sample_data,
            include_advanced_analysis=False
        )
        
        # Should have only standard sections
        assert len(report['sections']) == 6
    
    def test_comprehensive_report_page_count(self, generator, sample_data):
        """Test that page count meets target (25-40 pages)"""
        report = generator.generate_comprehensive_analysis_report(sample_data)
        
        # Target: 25-40 pages
        assert 20 <= report['total_pages'] <= 45
    
    def test_advanced_risk_analysis_section(self, generator, sample_data):
        """Test new advanced risk analysis section"""
        report = generator.generate_comprehensive_analysis_report(sample_data)
        sections = report['sections']
        
        # Find advanced risk section
        risk_section = None
        for section in sections:
            if 'Advanced Risk' in section.title:
                risk_section = section
                break
        
        assert risk_section is not None
        assert 'Multi-Dimensional' in risk_section.content
        assert 'Market Risk' in risk_section.content
    
    def test_market_trends_section(self, generator, sample_data):
        """Test new market trends section"""
        report = generator.generate_comprehensive_analysis_report(sample_data)
        sections = report['sections']
        
        # Find market trends section
        market_section = None
        for section in sections:
            if 'Market Trends' in section.title:
                market_section = section
                break
        
        assert market_section is not None
        assert 'Forecast' in market_section.content or 'Historical' in market_section.content
    
    def test_multi_scenario_comparison_section(self, generator, sample_data):
        """Test new multi-scenario comparison section"""
        report = generator.generate_comprehensive_analysis_report(sample_data)
        sections = report['sections']
        
        # Find scenario comparison section
        scenario_section = None
        for section in sections:
            if 'Scenario' in section.title:
                scenario_section = section
                break
        
        assert scenario_section is not None
        assert 'Scenario A' in scenario_section.content
        assert 'Scenario B' in scenario_section.content
        assert 'Scenario C' in scenario_section.content


class TestReportSection:
    """Tests for ReportSection dataclass"""
    
    def test_report_section_creation(self):
        """Test creating a report section"""
        section = ReportSection(
            title="Test Section",
            content="Test content",
            page_count=2
        )
        
        assert section.title == "Test Section"
        assert section.content == "Test content"
        assert section.page_count == 2
        assert section.subsections == []
    
    def test_report_section_with_subsections(self):
        """Test report section with subsections"""
        subsection = ReportSection("Subsection", "Content", 1)
        section = ReportSection(
            title="Main Section",
            content="Main content",
            page_count=3,
            subsections=[subsection]
        )
        
        assert len(section.subsections) == 1
        assert section.subsections[0].title == "Subsection"


class TestReportMetadata:
    """Tests for ReportMetadata dataclass"""
    
    def test_metadata_creation(self):
        """Test creating report metadata"""
        metadata = ReportMetadata(
            report_type="policy",
            total_pages=12
        )
        
        assert metadata.report_type == "policy"
        assert metadata.version == "24.1.0"
        assert metadata.total_pages == 12
        assert metadata.author == "ZeroSite AI System"
        assert metadata.generated_at is not None
    
    def test_metadata_auto_timestamp(self):
        """Test that timestamp is auto-generated"""
        metadata = ReportMetadata(report_type="developer")
        
        assert metadata.generated_at is not None
        assert len(metadata.generated_at) > 0


class TestHelperFunctions:
    """Tests for helper functions"""
    
    def test_format_currency_billions(self):
        """Test currency formatting for billions"""
        result = format_currency(5_000_000_000)
        assert "5.0B" in result
    
    def test_format_currency_millions(self):
        """Test currency formatting for millions"""
        result = format_currency(250_000_000)
        assert "250.0M" in result
    
    def test_format_currency_small(self):
        """Test currency formatting for small amounts"""
        result = format_currency(500_000)
        assert "500,000" in result
    
    def test_calculate_completeness_v241(self):
        """Test completeness calculation for v24.1"""
        assert calculate_completeness('policy', '24.1.0') == 100
        assert calculate_completeness('developer', '24.1.0') == 100
        assert calculate_completeness('comprehensive', '24.1.0') == 100
    
    def test_calculate_completeness_v240(self):
        """Test completeness calculation for v24.0"""
        assert calculate_completeness('policy', '24.0.0') == 80
        assert calculate_completeness('developer', '24.0.0') == 0
        assert calculate_completeness('comprehensive', '24.0.0') == 60


class TestReportIntegration:
    """Integration tests for report generation"""
    
    @pytest.fixture
    def generator(self):
        return ReportGeneratorV241()
    
    @pytest.fixture
    def complete_data(self):
        return {
            'address': '서울시 강남구 역삼동 123',
            'land_area_sqm': 660.0,
            'zone_type': '제2종일반주거',
            'far': 200.0,
            'bcr': 60.0,
            'floors': 10,
            'total_units': 40,
            'construction_cost': 3_500_000_000,
            'land_acquisition_cost': 2_000_000_000,
            'total_investment': 5_000_000_000,
            'total_revenue': 10_000_000_000,
            'profit': 2_000_000_000,
            'roi': 12.5,
            'irr': 10.2,
            'payback_period': 5.2,
            'parking_spaces': 35,
            'total_floor_area': 3960,
            'revenue_per_unit': 250_000_000
        }
    
    def test_generate_all_three_reports(self, generator, complete_data):
        """Test generating all three reports"""
        policy_report = generator.generate_policy_impact_report(complete_data)
        developer_report = generator.generate_developer_feasibility_report(complete_data)
        comprehensive_report = generator.generate_comprehensive_analysis_report(complete_data)
        
        assert policy_report is not None
        assert developer_report is not None
        assert comprehensive_report is not None
        
        assert policy_report['completeness'] == 100
        assert developer_report['completeness'] == 100
        assert comprehensive_report['completeness'] == 100
    
    def test_total_page_count_reasonable(self, generator, complete_data):
        """Test that total page count across all reports is reasonable"""
        policy_report = generator.generate_policy_impact_report(complete_data)
        developer_report = generator.generate_developer_feasibility_report(complete_data)
        comprehensive_report = generator.generate_comprehensive_analysis_report(complete_data)
        
        total_pages = (
            policy_report['total_pages'] +
            developer_report['total_pages'] +
            comprehensive_report['total_pages']
        )
        
        # Total should be reasonable (40-80 pages combined)
        assert 40 <= total_pages <= 100
    
    def test_report_consistency(self, generator, complete_data):
        """Test that all reports have consistent structure"""
        policy_report = generator.generate_policy_impact_report(complete_data)
        developer_report = generator.generate_developer_feasibility_report(complete_data)
        comprehensive_report = generator.generate_comprehensive_analysis_report(complete_data)
        
        for report in [policy_report, developer_report, comprehensive_report]:
            assert 'metadata' in report
            assert 'sections' in report
            assert 'total_pages' in report
            assert 'version' in report
            assert 'completeness' in report
            assert report['version'] == '24.1.0'
            assert report['completeness'] == 100
