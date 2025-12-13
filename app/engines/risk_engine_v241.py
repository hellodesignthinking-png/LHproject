"""
ZeroSite v24.1 - Risk Engine Enhancement
GAP #7: Risk Engine Enhancement (Design Risk, Legal Risk)

Author: ZeroSite Development Team
Version: v24.1.0
Created: 2025-12-12
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RiskCategory(Enum):
    """Risk category enumeration"""
    DESIGN = "DESIGN"
    LEGAL = "LEGAL"
    FINANCIAL = "FINANCIAL"
    CONSTRUCTION = "CONSTRUCTION"
    MARKET = "MARKET"
    REGULATORY = "REGULATORY"


class RiskLevel(Enum):
    """Risk level enumeration"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


@dataclass
class RiskItem:
    """Individual risk item"""
    category: RiskCategory
    description: str
    likelihood: float  # 0.0 to 1.0
    impact: float  # 0.0 to 1.0
    risk_score: float  # likelihood * impact
    level: RiskLevel
    mitigation: str


@dataclass
class DesignRiskAssessment:
    """Design risk assessment (NEW in v24.1)"""
    
    # Design Complexity Risks
    floor_plan_complexity_risk: float  # 0.0 to 1.0
    structural_feasibility_risk: float
    code_compliance_risk: float
    construction_difficulty_risk: float
    
    # Design Quality Indicators
    space_efficiency_score: float  # 0.0 to 1.0
    natural_lighting_score: float
    ventilation_score: float
    accessibility_score: float
    
    # Overall Assessment
    overall_design_risk: float  # 0.0 to 1.0
    risk_level: RiskLevel
    recommendations: List[str]


@dataclass
class LegalRiskAssessment:
    """Legal risk assessment (NEW in v24.1)"""
    
    # Legal Compliance Risks
    zoning_compliance_risk: float  # 0.0 to 1.0
    building_code_risk: float
    environmental_regulation_risk: float
    property_rights_risk: float
    
    # Documentation Risks
    permit_approval_risk: float
    title_verification_risk: float
    contract_validity_risk: float
    
    # Litigation Risks
    neighbor_dispute_risk: float
    regulatory_penalty_risk: float
    
    # Overall Assessment
    overall_legal_risk: float  # 0.0 to 1.0
    risk_level: RiskLevel
    critical_issues: List[str]
    recommended_actions: List[str]


@dataclass
class ComprehensiveRiskProfile:
    """Comprehensive risk profile combining all risk categories"""
    
    design_risks: DesignRiskAssessment
    legal_risks: LegalRiskAssessment
    
    # Aggregate Risk Metrics
    total_risk_score: float  # 0.0 to 1.0
    risk_distribution: Dict[str, float]
    
    # Priority Risks
    critical_risks: List[RiskItem]
    high_priority_risks: List[RiskItem]
    
    # Risk Management
    risk_mitigation_plan: Dict[str, List[str]]
    estimated_mitigation_cost: float
    
    # Overall Assessment
    project_risk_level: RiskLevel
    investment_recommendation: str


class RiskEngineV241:
    """
    Enhanced Risk Analysis Engine for ZeroSite v24.1
    
    NEW FEATURES (GAP #7):
    - Design Risk Assessment
    - Legal Risk Assessment
    - Comprehensive Risk Profiling
    
    Features:
    - Multi-category risk analysis
    - Quantitative risk scoring
    - Mitigation strategy generation
    - Risk-adjusted recommendations
    """
    
    def __init__(self):
        """Initialize Risk Engine v24.1"""
        self.version = "24.1.0"
        
        # Risk weight configuration
        self.risk_weights = {
            "design": 0.25,
            "legal": 0.30,
            "financial": 0.20,
            "construction": 0.15,
            "market": 0.10
        }
    
    def assess_design_risks(
        self,
        land_area: float,
        floors: int,
        unit_count: int,
        floor_area_ratio: float,
        building_coverage_ratio: float,
        height_limit: Optional[float] = None,
        sunlight_compliant: bool = True,
        parking_ratio: float = 1.0
    ) -> DesignRiskAssessment:
        """
        Assess design-related risks (NEW in v24.1)
        
        Args:
            land_area: Land area in ㎡
            floors: Number of floors
            unit_count: Number of units
            floor_area_ratio: FAR (%)
            building_coverage_ratio: BCR (%)
            height_limit: Height limit in meters
            sunlight_compliant: Sunlight compliance status
            parking_ratio: Parking ratio per unit
            
        Returns:
            Comprehensive design risk assessment
        """
        # Calculate building footprint
        building_footprint = land_area * (building_coverage_ratio / 100)
        
        # 1. Floor Plan Complexity Risk
        floor_plan_risk = self._assess_floor_plan_complexity(
            building_footprint, floors, unit_count
        )
        
        # 2. Structural Feasibility Risk
        structural_risk = self._assess_structural_feasibility(
            floors, building_footprint, height_limit
        )
        
        # 3. Code Compliance Risk
        compliance_risk = self._assess_code_compliance(
            sunlight_compliant, parking_ratio, floor_area_ratio
        )
        
        # 4. Construction Difficulty Risk
        construction_risk = self._assess_construction_difficulty(
            floors, building_footprint, unit_count
        )
        
        # Quality Indicators
        space_efficiency = self._calculate_space_efficiency(
            land_area, unit_count, floor_area_ratio
        )
        
        lighting_score = self._calculate_lighting_score(
            sunlight_compliant, building_coverage_ratio
        )
        
        ventilation_score = self._calculate_ventilation_score(
            building_coverage_ratio, floors
        )
        
        accessibility_score = self._calculate_accessibility_score(
            floors, unit_count
        )
        
        # Overall Design Risk
        overall_risk = (
            floor_plan_risk * 0.30 +
            structural_risk * 0.25 +
            compliance_risk * 0.25 +
            construction_risk * 0.20
        )
        
        risk_level = self._classify_risk_level(overall_risk)
        
        # Generate Recommendations
        recommendations = self._generate_design_recommendations(
            floor_plan_risk, structural_risk, compliance_risk,
            construction_risk, space_efficiency
        )
        
        return DesignRiskAssessment(
            floor_plan_complexity_risk=floor_plan_risk,
            structural_feasibility_risk=structural_risk,
            code_compliance_risk=compliance_risk,
            construction_difficulty_risk=construction_risk,
            space_efficiency_score=space_efficiency,
            natural_lighting_score=lighting_score,
            ventilation_score=ventilation_score,
            accessibility_score=accessibility_score,
            overall_design_risk=overall_risk,
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    def assess_legal_risks(
        self,
        zone_type: str,
        floor_area_ratio: float,
        far_limit: float,
        building_coverage_ratio: float,
        bcr_limit: float,
        height: float,
        height_limit: Optional[float] = None,
        environmental_impact: str = "LOW",
        title_status: str = "CLEAR",
        neighbor_agreements: bool = True
    ) -> LegalRiskAssessment:
        """
        Assess legal and regulatory risks (NEW in v24.1)
        
        Args:
            zone_type: Zoning type
            floor_area_ratio: Actual FAR
            far_limit: FAR limit
            building_coverage_ratio: Actual BCR
            bcr_limit: BCR limit
            height: Building height
            height_limit: Height limit
            environmental_impact: Environmental impact level
            title_status: Title verification status
            neighbor_agreements: Neighbor agreement status
            
        Returns:
            Comprehensive legal risk assessment
        """
        # 1. Zoning Compliance Risk
        zoning_risk = self._assess_zoning_compliance(
            floor_area_ratio, far_limit, building_coverage_ratio, bcr_limit
        )
        
        # 2. Building Code Risk
        code_risk = self._assess_building_code_risk(
            height, height_limit, zone_type
        )
        
        # 3. Environmental Regulation Risk
        env_risk = self._assess_environmental_risk(environmental_impact)
        
        # 4. Property Rights Risk
        property_risk = self._assess_property_rights_risk(title_status)
        
        # 5. Permit Approval Risk
        permit_risk = self._assess_permit_approval_risk(
            zoning_risk, code_risk, env_risk
        )
        
        # 6. Title Verification Risk
        title_risk = self._assess_title_risk(title_status)
        
        # 7. Contract Validity Risk
        contract_risk = self._assess_contract_risk(property_risk, title_risk)
        
        # 8. Neighbor Dispute Risk
        neighbor_risk = self._assess_neighbor_dispute_risk(neighbor_agreements)
        
        # 9. Regulatory Penalty Risk
        penalty_risk = self._assess_regulatory_penalty_risk(
            zoning_risk, code_risk, env_risk
        )
        
        # Overall Legal Risk
        overall_risk = (
            zoning_risk * 0.20 +
            code_risk * 0.15 +
            env_risk * 0.15 +
            property_risk * 0.10 +
            permit_risk * 0.15 +
            title_risk * 0.10 +
            contract_risk * 0.05 +
            neighbor_risk * 0.05 +
            penalty_risk * 0.05
        )
        
        risk_level = self._classify_risk_level(overall_risk)
        
        # Identify Critical Issues
        critical_issues = self._identify_critical_legal_issues(
            zoning_risk, code_risk, env_risk, property_risk, permit_risk
        )
        
        # Generate Recommended Actions
        actions = self._generate_legal_recommendations(
            zoning_risk, code_risk, env_risk, property_risk,
            permit_risk, neighbor_risk
        )
        
        return LegalRiskAssessment(
            zoning_compliance_risk=zoning_risk,
            building_code_risk=code_risk,
            environmental_regulation_risk=env_risk,
            property_rights_risk=property_risk,
            permit_approval_risk=permit_risk,
            title_verification_risk=title_risk,
            contract_validity_risk=contract_risk,
            neighbor_dispute_risk=neighbor_risk,
            regulatory_penalty_risk=penalty_risk,
            overall_legal_risk=overall_risk,
            risk_level=risk_level,
            critical_issues=critical_issues,
            recommended_actions=actions
        )
    
    def generate_comprehensive_risk_profile(
        self,
        design_assessment: DesignRiskAssessment,
        legal_assessment: LegalRiskAssessment,
        financial_risk: float = 0.3,
        construction_risk: float = 0.2,
        market_risk: float = 0.2
    ) -> ComprehensiveRiskProfile:
        """
        Generate comprehensive risk profile
        
        Args:
            design_assessment: Design risk assessment
            legal_assessment: Legal risk assessment
            financial_risk: Financial risk score (0.0-1.0)
            construction_risk: Construction risk score (0.0-1.0)
            market_risk: Market risk score (0.0-1.0)
            
        Returns:
            Comprehensive risk profile
        """
        # Calculate Total Risk Score
        total_risk = (
            design_assessment.overall_design_risk * self.risk_weights["design"] +
            legal_assessment.overall_legal_risk * self.risk_weights["legal"] +
            financial_risk * self.risk_weights["financial"] +
            construction_risk * self.risk_weights["construction"] +
            market_risk * self.risk_weights["market"]
        )
        
        # Risk Distribution
        risk_dist = {
            "design": design_assessment.overall_design_risk,
            "legal": legal_assessment.overall_legal_risk,
            "financial": financial_risk,
            "construction": construction_risk,
            "market": market_risk
        }
        
        # Identify Priority Risks
        critical_risks, high_risks = self._identify_priority_risks(
            design_assessment, legal_assessment,
            financial_risk, construction_risk, market_risk
        )
        
        # Generate Mitigation Plan
        mitigation_plan = self._generate_mitigation_plan(
            design_assessment, legal_assessment, critical_risks, high_risks
        )
        
        # Estimate Mitigation Cost
        mitigation_cost = self._estimate_mitigation_cost(
            critical_risks, high_risks
        )
        
        # Project Risk Level
        project_risk_level = self._classify_risk_level(total_risk)
        
        # Investment Recommendation
        recommendation = self._generate_investment_recommendation(
            total_risk, project_risk_level, critical_risks
        )
        
        return ComprehensiveRiskProfile(
            design_risks=design_assessment,
            legal_risks=legal_assessment,
            total_risk_score=total_risk,
            risk_distribution=risk_dist,
            critical_risks=critical_risks,
            high_priority_risks=high_risks,
            risk_mitigation_plan=mitigation_plan,
            estimated_mitigation_cost=mitigation_cost,
            project_risk_level=project_risk_level,
            investment_recommendation=recommendation
        )
    
    # Helper Methods - Design Risk
    
    def _assess_floor_plan_complexity(
        self,
        footprint: float,
        floors: int,
        units: int
    ) -> float:
        """Assess floor plan complexity risk"""
        units_per_floor = units / floors if floors > 0 else 0
        area_per_unit = footprint / units_per_floor if units_per_floor > 0 else 0
        
        # Risk increases with high unit density
        if units_per_floor > 8:
            complexity_risk = 0.7
        elif units_per_floor > 5:
            complexity_risk = 0.5
        elif units_per_floor > 3:
            complexity_risk = 0.3
        else:
            complexity_risk = 0.1
        
        # Adjust for unit size (very small units are risky)
        if area_per_unit < 25:
            complexity_risk = min(1.0, complexity_risk + 0.2)
        
        return complexity_risk
    
    def _assess_structural_feasibility(
        self,
        floors: int,
        footprint: float,
        height_limit: Optional[float]
    ) -> float:
        """Assess structural feasibility risk"""
        risk = 0.0
        
        # Height risk
        if floors > 20:
            risk += 0.4
        elif floors > 15:
            risk += 0.3
        elif floors > 10:
            risk += 0.2
        else:
            risk += 0.1
        
        # Footprint risk (very small or very large)
        if footprint < 200:
            risk += 0.2
        elif footprint > 2000:
            risk += 0.3
        
        # Height limit risk
        if height_limit:
            estimated_height = floors * 3.0
            if estimated_height > height_limit:
                risk += 0.4
        
        return min(1.0, risk)
    
    def _assess_code_compliance(
        self,
        sunlight_compliant: bool,
        parking_ratio: float,
        far: float
    ) -> float:
        """Assess code compliance risk"""
        risk = 0.0
        
        if not sunlight_compliant:
            risk += 0.4
        
        if parking_ratio < 0.8:
            risk += 0.3
        elif parking_ratio < 1.0:
            risk += 0.1
        
        if far > 300:
            risk += 0.2
        
        return min(1.0, risk)
    
    def _assess_construction_difficulty(
        self,
        floors: int,
        footprint: float,
        units: int
    ) -> float:
        """Assess construction difficulty risk"""
        risk = 0.0
        
        # More floors = more complex
        if floors > 15:
            risk += 0.3
        elif floors > 10:
            risk += 0.2
        
        # Small footprint = difficult
        if footprint < 300:
            risk += 0.2
        
        # High unit count = complex coordination
        if units > 50:
            risk += 0.2
        elif units > 30:
            risk += 0.1
        
        return min(1.0, risk)
    
    def _calculate_space_efficiency(
        self,
        land_area: float,
        units: int,
        far: float
    ) -> float:
        """Calculate space efficiency score"""
        total_floor_area = land_area * (far / 100)
        area_per_unit = total_floor_area / units if units > 0 else 0
        
        # Optimal range: 40-80 ㎡ per unit
        if 40 <= area_per_unit <= 80:
            return 0.9
        elif 30 <= area_per_unit < 40 or 80 < area_per_unit <= 100:
            return 0.7
        elif area_per_unit < 30:
            return 0.4
        else:
            return 0.6
    
    def _calculate_lighting_score(
        self,
        sunlight_compliant: bool,
        bcr: float
    ) -> float:
        """Calculate natural lighting score"""
        score = 0.5 if sunlight_compliant else 0.3
        
        # Lower BCR = better lighting
        if bcr < 40:
            score += 0.3
        elif bcr < 60:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_ventilation_score(self, bcr: float, floors: int) -> float:
        """Calculate ventilation score"""
        # Lower BCR and fewer floors = better ventilation
        base_score = 1.0 - (bcr / 100) * 0.5
        
        if floors > 15:
            base_score *= 0.8
        
        return max(0.0, min(1.0, base_score))
    
    def _calculate_accessibility_score(self, floors: int, units: int) -> float:
        """Calculate accessibility score"""
        # Assume elevator required for >5 floors
        if floors > 5:
            return 0.8  # Good with elevator
        elif floors <= 3:
            return 0.9  # Excellent for walk-up
        else:
            return 0.7  # Moderate
    
    def _generate_design_recommendations(
        self,
        floor_plan_risk: float,
        structural_risk: float,
        compliance_risk: float,
        construction_risk: float,
        space_efficiency: float
    ) -> List[str]:
        """Generate design recommendations"""
        recommendations = []
        
        if floor_plan_risk > 0.6:
            recommendations.append("Simplify floor plan layout to reduce complexity")
        
        if structural_risk > 0.6:
            recommendations.append("Conduct detailed structural feasibility study")
        
        if compliance_risk > 0.5:
            recommendations.append("Review code compliance requirements and adjust design")
        
        if construction_risk > 0.5:
            recommendations.append("Engage construction experts early in design phase")
        
        if space_efficiency < 0.6:
            recommendations.append("Optimize space efficiency to improve marketability")
        
        if not recommendations:
            recommendations.append("Design meets standard risk thresholds")
        
        return recommendations
    
    # Helper Methods - Legal Risk
    
    def _assess_zoning_compliance(
        self,
        far: float,
        far_limit: float,
        bcr: float,
        bcr_limit: float
    ) -> float:
        """Assess zoning compliance risk"""
        risk = 0.0
        
        # FAR compliance
        if far > far_limit * 1.1:
            risk += 0.5
        elif far > far_limit:
            risk += 0.3
        
        # BCR compliance
        if bcr > bcr_limit * 1.1:
            risk += 0.5
        elif bcr > bcr_limit:
            risk += 0.3
        
        return min(1.0, risk)
    
    def _assess_building_code_risk(
        self,
        height: float,
        height_limit: Optional[float],
        zone_type: str
    ) -> float:
        """Assess building code compliance risk"""
        risk = 0.1  # Base risk
        
        if height_limit and height > height_limit:
            risk += 0.6
        
        # Certain zones have stricter codes
        if "주거" in zone_type or "residential" in zone_type.lower():
            risk += 0.1
        
        return min(1.0, risk)
    
    def _assess_environmental_risk(self, impact_level: str) -> float:
        """Assess environmental regulation risk"""
        impact_risks = {
            "MINIMAL": 0.1,
            "LOW": 0.2,
            "MEDIUM": 0.4,
            "HIGH": 0.7,
            "CRITICAL": 0.9
        }
        
        return impact_risks.get(impact_level.upper(), 0.3)
    
    def _assess_property_rights_risk(self, title_status: str) -> float:
        """Assess property rights risk"""
        status_risks = {
            "CLEAR": 0.1,
            "MINOR_ISSUES": 0.3,
            "ENCUMBRANCES": 0.6,
            "DISPUTED": 0.9
        }
        
        return status_risks.get(title_status.upper(), 0.5)
    
    def _assess_permit_approval_risk(
        self,
        zoning_risk: float,
        code_risk: float,
        env_risk: float
    ) -> float:
        """Assess permit approval risk"""
        # Higher underlying risks = higher permit risk
        base_risk = (zoning_risk + code_risk + env_risk) / 3.0
        
        # Add bureaucratic delay risk
        return min(1.0, base_risk + 0.2)
    
    def _assess_title_risk(self, title_status: str) -> float:
        """Assess title verification risk"""
        return self._assess_property_rights_risk(title_status)
    
    def _assess_contract_risk(
        self,
        property_risk: float,
        title_risk: float
    ) -> float:
        """Assess contract validity risk"""
        return (property_risk + title_risk) / 2.0
    
    def _assess_neighbor_dispute_risk(self, agreements: bool) -> float:
        """Assess neighbor dispute risk"""
        return 0.2 if agreements else 0.7
    
    def _assess_regulatory_penalty_risk(
        self,
        zoning_risk: float,
        code_risk: float,
        env_risk: float
    ) -> float:
        """Assess regulatory penalty risk"""
        max_risk = max(zoning_risk, code_risk, env_risk)
        
        if max_risk > 0.7:
            return 0.6
        elif max_risk > 0.5:
            return 0.4
        else:
            return 0.2
    
    def _identify_critical_legal_issues(
        self,
        zoning_risk: float,
        code_risk: float,
        env_risk: float,
        property_risk: float,
        permit_risk: float
    ) -> List[str]:
        """Identify critical legal issues"""
        issues = []
        
        if zoning_risk > 0.6:
            issues.append("CRITICAL: Zoning compliance violations detected")
        
        if code_risk > 0.6:
            issues.append("CRITICAL: Building code compliance issues")
        
        if env_risk > 0.6:
            issues.append("CRITICAL: Environmental regulation concerns")
        
        if property_risk > 0.7:
            issues.append("CRITICAL: Property rights disputes")
        
        if permit_risk > 0.7:
            issues.append("HIGH: Permit approval risk")
        
        if not issues:
            issues.append("No critical legal issues identified")
        
        return issues
    
    def _generate_legal_recommendations(
        self,
        zoning_risk: float,
        code_risk: float,
        env_risk: float,
        property_risk: float,
        permit_risk: float,
        neighbor_risk: float
    ) -> List[str]:
        """Generate legal recommendations"""
        actions = []
        
        if zoning_risk > 0.5:
            actions.append("Obtain legal counsel for zoning variance application")
        
        if code_risk > 0.5:
            actions.append("Conduct comprehensive code compliance review")
        
        if env_risk > 0.5:
            actions.append("Complete environmental impact assessment")
        
        if property_risk > 0.6:
            actions.append("Resolve title issues before proceeding")
        
        if permit_risk > 0.6:
            actions.append("Engage permitting consultant to expedite approvals")
        
        if neighbor_risk > 0.5:
            actions.append("Obtain neighbor consent agreements")
        
        if not actions:
            actions.append("Standard legal due diligence recommended")
        
        return actions
    
    # Helper Methods - Comprehensive Profile
    
    def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify risk level"""
        if risk_score >= 0.75:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.50:
            return RiskLevel.HIGH
        elif risk_score >= 0.30:
            return RiskLevel.MEDIUM
        elif risk_score >= 0.15:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _identify_priority_risks(
        self,
        design: DesignRiskAssessment,
        legal: LegalRiskAssessment,
        financial: float,
        construction: float,
        market: float
    ) -> Tuple[List[RiskItem], List[RiskItem]]:
        """Identify priority risks"""
        all_risks = []
        
        # Design Risks
        if design.overall_design_risk > 0.5:
            all_risks.append(RiskItem(
                category=RiskCategory.DESIGN,
                description="Design complexity and feasibility concerns",
                likelihood=design.overall_design_risk,
                impact=0.8,
                risk_score=design.overall_design_risk * 0.8,
                level=design.risk_level,
                mitigation="Simplify design, conduct feasibility studies"
            ))
        
        # Legal Risks
        if legal.overall_legal_risk > 0.5:
            all_risks.append(RiskItem(
                category=RiskCategory.LEGAL,
                description="Legal compliance and regulatory issues",
                likelihood=legal.overall_legal_risk,
                impact=0.9,
                risk_score=legal.overall_legal_risk * 0.9,
                level=legal.risk_level,
                mitigation="Legal review, compliance corrections"
            ))
        
        # Financial Risks
        if financial > 0.5:
            all_risks.append(RiskItem(
                category=RiskCategory.FINANCIAL,
                description="Financial viability concerns",
                likelihood=financial,
                impact=0.95,
                risk_score=financial * 0.95,
                level=self._classify_risk_level(financial),
                mitigation="Financial restructuring, cost optimization"
            ))
        
        # Sort by risk score
        all_risks.sort(key=lambda x: x.risk_score, reverse=True)
        
        # Separate critical and high
        critical = [r for r in all_risks if r.level == RiskLevel.CRITICAL]
        high = [r for r in all_risks if r.level == RiskLevel.HIGH]
        
        return critical, high
    
    def _generate_mitigation_plan(
        self,
        design: DesignRiskAssessment,
        legal: LegalRiskAssessment,
        critical: List[RiskItem],
        high: List[RiskItem]
    ) -> Dict[str, List[str]]:
        """Generate mitigation plan"""
        plan = {
            "immediate_actions": [],
            "short_term": [],
            "long_term": []
        }
        
        # Immediate actions for critical risks
        if critical:
            plan["immediate_actions"].append("Address all critical risk items")
            plan["immediate_actions"].extend([r.mitigation for r in critical])
        
        # Short-term for high risks
        if high:
            plan["short_term"].extend([r.mitigation for r in high])
        
        # Long-term based on design and legal
        plan["long_term"].extend(design.recommendations)
        plan["long_term"].extend(legal.recommended_actions[:2])
        
        return plan
    
    def _estimate_mitigation_cost(
        self,
        critical: List[RiskItem],
        high: List[RiskItem]
    ) -> float:
        """Estimate mitigation cost"""
        # Simple estimation
        critical_cost = len(critical) * 50_000_000  # 50M per critical
        high_cost = len(high) * 20_000_000  # 20M per high
        
        return critical_cost + high_cost
    
    def _generate_investment_recommendation(
        self,
        total_risk: float,
        risk_level: RiskLevel,
        critical_risks: List[RiskItem]
    ) -> str:
        """Generate investment recommendation"""
        if risk_level == RiskLevel.CRITICAL or critical_risks:
            return "NOT RECOMMENDED: Critical risks must be mitigated before investment"
        elif risk_level == RiskLevel.HIGH:
            return "CAUTION: High risks present. Proceed only with comprehensive mitigation plan"
        elif risk_level == RiskLevel.MEDIUM:
            return "CONDITIONAL: Acceptable with standard risk mitigation measures"
        else:
            return "RECOMMENDED: Risk profile acceptable for investment"


# Module exports
__all__ = [
    "RiskEngineV241",
    "DesignRiskAssessment",
    "LegalRiskAssessment",
    "ComprehensiveRiskProfile",
    "RiskCategory",
    "RiskLevel",
    "RiskItem"
]
