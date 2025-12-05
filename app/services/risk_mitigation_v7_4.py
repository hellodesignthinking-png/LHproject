"""
ZeroSite v7.4 Risk Mitigation Framework

Comprehensive risk assessment and mitigation strategy framework for LH projects:
- Risk identification across all categories
- Risk quantification (impact × likelihood scoring)
- Mitigation strategy generation
- Contingency planning
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskCategory(Enum):
    """Risk categories"""
    FINANCIAL = "financial"
    REGULATORY = "regulatory"
    MARKET = "market"
    OPERATIONAL = "operational"
    CONSTRUCTION = "construction"
    LEGAL = "legal"
    INDUSTRY = "industry"  # Industry-specific risks
    STRATEGIC = "strategic"  # Strategic and business model risks


class RiskLevel(Enum):
    """Risk severity levels"""
    CRITICAL = "critical"  # Impact ≥ 4 AND Likelihood ≥ 4
    HIGH = "high"          # Impact × Likelihood ≥ 12
    MEDIUM = "medium"      # Impact × Likelihood ≥ 6
    LOW = "low"            # Impact × Likelihood < 6


@dataclass
class Risk:
    """Risk definition"""
    id: str
    category: RiskCategory
    title: str
    description: str
    impact_score: int  # 1-5 scale
    likelihood_score: int  # 1-5 scale
    risk_score: int  # impact × likelihood
    risk_level: RiskLevel
    current_controls: List[str]
    mitigation_strategies: List[str]
    contingency_plan: str
    owner: str
    timeline: str


class RiskMitigationFramework:
    """
    Risk Mitigation Framework for LH Projects
    
    Provides comprehensive risk management including:
    - Risk identification across all project phases
    - Quantitative risk scoring (impact × likelihood)
    - Mitigation strategy recommendations
    - Contingency planning
    """
    
    def __init__(self):
        """Initialize risk mitigation framework"""
        self.risks: List[Risk] = []
        logger.info("⚠️  Risk Mitigation Framework v7.4 initialized")
    
    def assess_project_risks(
        self,
        data: Dict[str, Any],
        financial_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Assess all project risks comprehensively
        
        Args:
            data: ZeroSite analysis data
            financial_analysis: Financial feasibility analysis results
        
        Returns:
            Comprehensive risk assessment with mitigation strategies
        """
        logger.info("🔍 Conducting comprehensive risk assessment")
        
        self.risks = []
        
        # 1. Financial Risks
        self._assess_financial_risks(data, financial_analysis)
        
        # 2. Regulatory Risks
        self._assess_regulatory_risks(data)
        
        # 3. Market Risks
        self._assess_market_risks(data)
        
        # 4. Operational Risks
        self._assess_operational_risks(data)
        
        # 5. Construction Risks
        self._assess_construction_risks(data)
        
        # 6. Legal Risks
        self._assess_legal_risks(data)
        
        # 7. Industry-Specific Risks
        self._assess_industry_specific_risks(data)
        
        # 8. Seoul-Specific Risks
        self._assess_seoul_specific_risks(data)
        
        # 9. Strategic Risks
        self._assess_strategic_risks(data)
        
        # Generate risk matrix
        risk_matrix = self._generate_risk_matrix()
        
        # Generate executive summary
        executive_summary = self._generate_risk_executive_summary()
        
        # Generate mitigation roadmap
        mitigation_roadmap = self._generate_mitigation_roadmap()
        
        logger.info(f"✅ Risk assessment complete: {len(self.risks)} risks identified")
        
        return {
            'risks': [self._risk_to_dict(r) for r in self.risks],
            'risk_matrix': risk_matrix,
            'executive_summary': executive_summary,
            'mitigation_roadmap': mitigation_roadmap,
            'risk_statistics': self._calculate_risk_statistics()
        }
    
    def _assess_financial_risks(
        self,
        data: Dict[str, Any],
        financial_analysis: Dict[str, Any] = None
    ):
        """Assess financial risks"""
        
        # Risk 1: Construction Cost Overrun
        capex_risk_score = 3  # Default medium impact
        if financial_analysis and 'capex' in financial_analysis:
            total_capex = financial_analysis['capex']['total_capex']
            if total_capex > 10_000_000_000:  # > 100억
                capex_risk_score = 4
        
        self.risks.append(Risk(
            id="FIN-001",
            category=RiskCategory.FINANCIAL,
            title="건설 비용 초과 위험",
            description="예상 건설 비용이 초과될 경우 프로젝트 수익성 저하 및 LH 매입가 기준 미달 가능성",
            impact_score=4,
            likelihood_score=capex_risk_score,
            risk_score=4 * capex_risk_score,
            risk_level=self._calculate_risk_level(4, capex_risk_score),
            current_controls=[
                "상세 견적 산출 (설계 단계)",
                "시장 조사 기반 단가 산정",
                "예비비 10% 포함"
            ],
            mitigation_strategies=[
                "고정가 계약(Lump Sum Contract) 체결로 비용 확정",
                "가치공학(VE) 적용하여 비용 최적화",
                "분기별 공정-비용 모니터링 시스템 구축",
                "예비비를 12-15%로 상향 조정",
                "주요 자재 사전 확보 계약 체결"
            ],
            contingency_plan="비용 10% 초과 시: 설계 변경 검토 및 LH 협의, 20% 초과 시: 프로젝트 재평가",
            owner="재무팀 / 건설팀",
            timeline="설계 단계부터 지속 관리"
        ))
        
        # Risk 2: Operating Expense Volatility
        self.risks.append(Risk(
            id="FIN-002",
            category=RiskCategory.FINANCIAL,
            title="운영 비용 변동성 위험",
            description="관리비, 유지보수비, 재산세 등 운영비용의 예상치 못한 증가로 인한 NOI 감소",
            impact_score=3,
            likelihood_score=3,
            risk_score=9,
            risk_level=RiskLevel.MEDIUM,
            current_controls=[
                "과거 유사 프로젝트 벤치마크",
                "인플레이션 2% 가정 포함",
                "대체 적립금 연간 60만원/세대"
            ],
            mitigation_strategies=[
                "장기 유지보수 계약 체결로 비용 안정화",
                "에너지 효율 설비 도입으로 공용 관리비 절감",
                "운영비 준비금 3개월분 확보",
                "전문 PM 업체 선정하여 비용 효율화",
                "입주자 교육 프로그램으로 시설 관리 개선"
            ],
            contingency_plan="OpEx 15% 초과 시: 관리 방식 재검토 및 효율화 조치 시행",
            owner="운영팀 / PM팀",
            timeline="운영 개시 후 지속 관리"
        ))
        
        # Risk 3: Vacancy Rate Risk
        meets_lh_target = False
        if financial_analysis and 'returns' in financial_analysis:
            meets_lh_target = financial_analysis['returns'].get('meets_lh_target', False)
        
        vacancy_likelihood = 2 if meets_lh_target else 4
        
        self.risks.append(Risk(
            id="FIN-003",
            category=RiskCategory.FINANCIAL,
            title="공실률 위험",
            description="목표 입주율 미달 시 임대 수익 감소 및 LH 수익률 기준 미충족",
            impact_score=5,
            likelihood_score=vacancy_likelihood,
            risk_score=5 * vacancy_likelihood,
            risk_level=self._calculate_risk_level(5, vacancy_likelihood),
            current_controls=[
                "1차년도 입주율 80% 보수적 가정",
                "안정기 입주율 95% 목표",
                "위치 기반 수요 분석 완료"
            ],
            mitigation_strategies=[
                "사전 임대(Pre-leasing) 프로그램 운영 (준공 3개월 전)",
                "입주 인센티브 제공 (첫 달 임대료 할인 등)",
                "다양한 유닛 타입 믹스로 수요층 확대",
                "적극적 마케팅 캠페인 (온라인/오프라인)",
                "LH 공공주택 포털 적극 활용",
                "지역 커뮤니티 및 기업 연계 임대"
            ],
            contingency_plan="입주율 70% 미만 지속 시: 임대료 조정 및 마케팅 전략 재수립",
            owner="마케팅팀 / 임대관리팀",
            timeline="준공 6개월 전부터 집중 관리"
        ))
        
        # Risk 4: Interest Rate Risk (if financed)
        self.risks.append(Risk(
            id="FIN-004",
            category=RiskCategory.FINANCIAL,
            title="금리 변동 위험",
            description="차입금 사용 시 금리 상승으로 인한 재무 비용 증가",
            impact_score=3,
            likelihood_score=3,
            risk_score=9,
            risk_level=RiskLevel.MEDIUM,
            current_controls=[
                "현재 금리 수준 반영",
                "LH 협력 금융기관 우대금리 가능"
            ],
            mitigation_strategies=[
                "고정금리 대출 우선 고려",
                "금리 상한 계약(Interest Rate Cap) 검토",
                "자기자본 비율 최대화하여 차입 최소화",
                "LH 정책금융 활용 (저리 대출)",
                "금리 스왑(Swap) 상품 검토"
            ],
            contingency_plan="금리 2%p 상승 시: 재무구조 재검토 및 상환 계획 조정",
            owner="재무팀 / CFO",
            timeline="자금조달 단계"
        ))
    
    def _assess_regulatory_risks(self, data: Dict[str, Any]):
        """Assess regulatory and legal compliance risks"""
        
        # Risk 5: Zoning Change Risk
        zoning_data = data.get('zoning', {})
        zoning_complexity = len([k for k, v in zoning_data.items() if v and v != 'N/A'])
        
        zoning_likelihood = 2 if zoning_complexity > 10 else 1
        
        self.risks.append(Risk(
            id="REG-001",
            category=RiskCategory.REGULATORY,
            title="용도지역 변경 위험",
            description="프로젝트 진행 중 용도지역 변경으로 인한 건축 계획 변경 및 승인 지연",
            impact_score=4,
            likelihood_score=zoning_likelihood,
            risk_score=4 * zoning_likelihood,
            risk_level=self._calculate_risk_level(4, zoning_likelihood),
            current_controls=[
                "현재 용도지역 확인 완료",
                "도시계획 변경 예정 사항 조사"
            ],
            mitigation_strategies=[
                "지자체 도시계획과 사전 협의",
                "용도지역 변경 모니터링 시스템 구축",
                "복수 설계안 준비 (용도지역별)",
                "법률 자문 확보",
                "주민 설명회 및 의견 수렴"
            ],
            contingency_plan="용도지역 변경 시: 즉시 설계 재검토 및 LH 협의, 필요시 프로젝트 일시 중단",
            owner="법무팀 / 개발팀",
            timeline="착공 전 6개월 집중 모니터링"
        ))
        
        # Risk 6: Policy Change Risk
        self.risks.append(Risk(
            id="REG-002",
            category=RiskCategory.REGULATORY,
            title="주택정책 변경 위험",
            description="LH 신축매입임대 정책 변경, 임대료 규제 강화, 세제 변경 등",
            impact_score=4,
            likelihood_score=3,
            risk_score=12,
            risk_level=RiskLevel.HIGH,
            current_controls=[
                "현행 LH 정책 기준 준수",
                "관련 법령 정기 모니터링"
            ],
            mitigation_strategies=[
                "LH 본사와 긴밀한 협력 관계 유지",
                "정책 변경 사전 정보 입수 채널 구축",
                "유연한 사업 구조 설계",
                "정부 정책 방향성 상시 모니터링",
                "업계 협회 가입 및 정보 공유"
            ],
            contingency_plan="중대 정책 변경 시: LH와 재협상, 사업 구조 재설계, 최악의 경우 사업 철회 검토",
            owner="전략기획팀 / 경영진",
            timeline="프로젝트 전 기간"
        ))
        
        # Risk 7: Permit Approval Delay
        self.risks.append(Risk(
            id="REG-003",
            category=RiskCategory.REGULATORY,
            title="인허가 지연 위험",
            description="건축허가, 착공신고 등 인허가 절차 지연으로 인한 공사 일정 차질",
            impact_score=3,
            likelihood_score=3,
            risk_score=9,
            risk_level=RiskLevel.MEDIUM,
            current_controls=[
                "인허가 요건 사전 검토",
                "지자체 협의 진행"
            ],
            mitigation_strategies=[
                "인허가 전문 대행업체 활용",
                "사전 협의 제도 적극 활용",
                "필요 서류 조기 준비",
                "담당 공무원과 정기 소통",
                "인허가 일정에 버퍼 20% 추가"
            ],
            contingency_plan="인허가 3개월 지연 시: 전체 일정 재조정, 6개월 지연 시: LH와 재협의",
            owner="개발팀 / 법무팀",
            timeline="인허가 신청 전후 6개월"
        ))
    
    def _assess_market_risks(self, data: Dict[str, Any]):
        """Assess market and demand risks"""
        
        # Risk 8: Demand Volatility
        typedemand = data.get('typedemand', {})
        demand_analysis = typedemand.get('demand_analysis', {})
        overall_suitability = demand_analysis.get('overall_suitability', 'N/A')
        
        demand_likelihood = 2 if overall_suitability == '적합' else 3
        
        self.risks.append(Risk(
            id="MKT-001",
            category=RiskCategory.MARKET,
            title="수요 변동성 위험",
            description="목표 수요층(청년, 신혼부부 등)의 수요 감소 또는 선호도 변화",
            impact_score=4,
            likelihood_score=demand_likelihood,
            risk_score=4 * demand_likelihood,
            risk_level=self._calculate_risk_level(4, demand_likelihood),
            current_controls=[
                "TypeDemand 5-Type 분석 완료",
                "인구통계 데이터 기반 예측"
            ],
            mitigation_strategies=[
                "유닛 믹스 다변화 (청년/신혼부부/다자녀/고령자 혼합)",
                "유연한 유닛 전환 설계 (타입 간 전환 가능)",
                "정기적 시장 수요 조사 (분기별)",
                "입주자 만족도 조사 및 피드백 반영",
                "지역 고용 시장 동향 모니터링"
            ],
            contingency_plan="특정 타입 수요 급감 시: 유닛 전환 및 타겟층 재설정",
            owner="마케팅팀 / 전략팀",
            timeline="운영 전 기간"
        ))
        
        # Risk 9: Competition Intensification
        geooptimizer = data.get('geooptimizer', {})
        alternatives = geooptimizer.get('alternatives', [])
        
        competition_likelihood = 3 if len(alternatives) > 2 else 2
        
        self.risks.append(Risk(
            id="MKT-002",
            category=RiskCategory.MARKET,
            title="경쟁 심화 위험",
            description="인근 지역 유사 공공임대 또는 민간 임대 공급 증가로 인한 경쟁 심화",
            impact_score=3,
            likelihood_score=competition_likelihood,
            risk_score=3 * competition_likelihood,
            risk_level=self._calculate_risk_level(3, competition_likelihood),
            current_controls=[
                "GeoOptimizer로 대안지 3곳 비교 분석",
                "경쟁 프로젝트 현황 조사"
            ],
            mitigation_strategies=[
                "차별화된 커뮤니티 시설 제공",
                "프리미엄 서비스 패키지 (무료 Wi-Fi, 공유 오피스 등)",
                "브랜딩 및 마케팅 강화",
                "입주자 만족도 극대화 전략",
                "지속적인 경쟁사 모니터링"
            ],
            contingency_plan="경쟁 심화 시: 임대료 조정, 인센티브 강화, 서비스 차별화",
            owner="마케팅팀 / 운영팀",
            timeline="임대 개시 전후 12개월"
        ))
        
        # Risk 10: Macroeconomic Downturn
        self.risks.append(Risk(
            id="MKT-003",
            category=RiskCategory.MARKET,
            title="거시경제 침체 위험",
            description="경기 침체, 실업률 증가 등으로 인한 임대 수요 전반 감소",
            impact_score=5,
            likelihood_score=2,
            risk_score=10,
            risk_level=RiskLevel.MEDIUM,
            current_controls=[
                "보수적 재무 가정",
                "다양한 시나리오 분석"
            ],
            mitigation_strategies=[
                "공공주택의 경기방어적 특성 활용",
                "LH 협력 관계로 안정성 확보",
                "비용 구조 유연성 확보",
                "재무 준비금 충분히 확보",
                "장기 임대 계약 유도 (안정적 현금흐름)"
            ],
            contingency_plan="경기 침체 시: 임대료 탄력적 조정, 입주 조건 완화, 정부 지원책 활용",
            owner="경영진 / 재무팀",
            timeline="프로젝트 전 기간"
        ))
    
    def _assess_operational_risks(self, data: Dict[str, Any]):
        """Assess operational and management risks"""
        
        # Risk 11: Property Management Quality
        self.risks.append(Risk(
            id="OPS-001",
            category=RiskCategory.OPERATIONAL,
            title="관리 품질 저하 위험",
            description="부실한 시설 관리 및 입주자 서비스로 인한 만족도 저하 및 공실 증가",
            impact_score=3,
            likelihood_score=2,
            risk_score=6,
            risk_level=RiskLevel.MEDIUM,
            current_controls=[
                "전문 PM 업체 선정 예정",
                "관리비 적정 수준 책정"
            ],
            mitigation_strategies=[
                "검증된 PM 업체 선정 (실적 및 평판 확인)",
                "PM 계약서에 KPI 명시 (입주자 만족도, 대응 시간 등)",
                "정기 관리 품질 감사",
                "입주자 의견 수렴 시스템 구축",
                "PM 성과급 제도 도입"
            ],
            contingency_plan="관리 품질 문제 발생 시: PM 업체 교체 검토, 자체 관리 전환 고려",
            owner="운영팀 / PM팀",
            timeline="운영 기간"
        ))
        
        # Risk 12: Maintenance Cost Overrun
        self.risks.append(Risk(
            id="OPS-002",
            category=RiskCategory.OPERATIONAL,
            title="유지보수 비용 초과 위험",
            description="예상보다 높은 유지보수 비용 발생으로 인한 수익성 저하",
            impact_score=3,
            likelihood_score=3,
            risk_score=9,
            risk_level=RiskLevel.MEDIUM,
            current_controls=[
                "대체 적립금 연 60만원/세대 책정",
                "예방 정비 계획 수립 예정"
            ],
            mitigation_strategies=[
                "고품질 자재 및 설비 초기 투자로 고장률 최소화",
                "예방 정비 프로그램 운영 (정기 점검)",
                "장기 유지보수 계약으로 비용 고정",
                "에너지 관리 시스템(EMS) 도입으로 설비 최적화",
                "유지보수 이력 DB 구축 및 분석"
            ],
            contingency_plan="유지보수 비용 20% 초과 시: 관리 방식 재검토 및 설비 교체 계획 수립",
            owner="시설팀 / 운영팀",
            timeline="운영 기간"
        ))
    
    def _assess_construction_risks(self, data: Dict[str, Any]):
        """Assess construction-related risks"""
        
        # Risk 13: Construction Delay
        self.risks.append(Risk(
            id="CON-001",
            category=RiskCategory.CONSTRUCTION,
            title="공사 지연 위험",
            description="공사 지연으로 인한 임대 개시 지연 및 재무 손실",
            impact_score=4,
            likelihood_score=3,
            risk_score=12,
            risk_level=RiskLevel.HIGH,
            current_controls=[
                "공정 계획 수립",
                "예비 공기 포함"
            ],
            mitigation_strategies=[
                "검증된 시공사 선정 (유사 프로젝트 경험)",
                "공정 관리 시스템 도입 (주간 모니터링)",
                "Critical Path Method(CPM) 적용",
                "공기 단축 인센티브 조항 포함",
                "날씨 등 외부 요인 대비 버퍼 확보",
                "주요 자재 조기 발주"
            ],
            contingency_plan="공사 3개월 지연 시: 임대 일정 조정 및 LH 협의, 6개월 지연 시: 손해배상 청구",
            owner="건설팀 / PM",
            timeline="공사 기간"
        ))
        
        # Risk 14: Quality Defects
        self.risks.append(Risk(
            id="CON-002",
            category=RiskCategory.CONSTRUCTION,
            title="시공 품질 하자 위험",
            description="시공 하자로 인한 재시공 비용 및 입주자 불만",
            impact_score=3,
            likelihood_score=2,
            risk_score=6,
            risk_level=RiskLevel.MEDIUM,
            current_controls=[
                "시공사 자체 품질관리",
                "감리 용역 예정"
            ],
            mitigation_strategies=[
                "독립적인 감리단 선정",
                "단계별 품질 검사 시스템",
                "하자보수 보증금 충분히 확보",
                "준공 전 입주자 사전 점검",
                "시공사 품질 인증 요구 (ISO 9001 등)"
            ],
            contingency_plan="중대 하자 발견 시: 시공사 책임 재시공, 필요시 법적 조치",
            owner="건설팀 / 감리단",
            timeline="공사 및 하자보수 기간"
        ))
    
    def _assess_legal_risks(self, data: Dict[str, Any]):
        """Assess legal and compliance risks"""
        
        # Risk 15: Contract Disputes
        self.risks.append(Risk(
            id="LEG-001",
            category=RiskCategory.LEGAL,
            title="계약 분쟁 위험",
            description="시공사, PM, 입주자 등과의 계약 분쟁 발생",
            impact_score=3,
            likelihood_score=2,
            risk_score=6,
            risk_level=RiskLevel.MEDIUM,
            current_controls=[
                "표준 계약서 사용 예정",
                "법무 검토 진행"
            ],
            mitigation_strategies=[
                "명확한 계약서 작성 (권리 의무 명시)",
                "분쟁 해결 조항 포함 (중재, 조정)",
                "법률 자문 상시 확보",
                "계약 이행 모니터링 시스템",
                "사전 협의 및 문서화"
            ],
            contingency_plan="분쟁 발생 시: 중재/조정 우선 시도, 최후 수단으로 소송",
            owner="법무팀 / 경영지원팀",
            timeline="계약 체결 시점부터"
        ))
        
        # Risk 16: Land Title and Ownership Issues
        self.risks.append(Risk(
            id="LEG-002",
            category=RiskCategory.LEGAL,
            title="토지 권리관계 하자 위험",
            description="근저당권, 가압류, 소유권 분쟁 등 토지 권리관계 문제로 인한 사업 지연",
            impact_score=5,
            likelihood_score=2,
            risk_score=10,
            risk_level=RiskLevel.HIGH,
            current_controls=[
                "등기부등본 확인",
                "법무법인 권리분석 예정"
            ],
            mitigation_strategies=[
                "법무법인을 통한 정밀 권리분석 실시",
                "말소 가능한 권리관계 사전 해소",
                "소유권보험 가입 검토",
                "매도인 표명 보증(R&W) 요구",
                "에스크로 계약 활용"
            ],
            contingency_plan="중대 권리 하자 발견 시: 매매 계약 해제 조건 활용 또는 매도인과 가격 재협상",
            owner="법무팀 / 개발팀",
            timeline="매수 단계"
        ))
    
    def _assess_industry_specific_risks(self, data: Dict[str, Any]):
        """Assess construction industry-specific risks"""
        
        # Risk 17: Labor Shortage
        self.risks.append(Risk(
            id="IND-001",
            category=RiskCategory.CONSTRUCTION,
            title="건설 인력 부족 위험",
            description="숙련 건설 인력 부족으로 인한 공사 지연 및 인건비 상승",
            impact_score=4,
            likelihood_score=4,
            risk_score=16,
            risk_level=RiskLevel.CRITICAL,
            current_controls=[
                "시공사 인력 확보 능력 검토"
            ],
            mitigation_strategies=[
                "대형 시공사 선정으로 인력 풀 확보",
                "장기 노무 공급 계약 체결",
                "외국인 근로자 활용 방안 검토",
                "모듈화/프리캐스트 공법 적용으로 현장 인력 최소화",
                "비수기 공사 일정 조정"
            ],
            contingency_plan="인력 부족 심화 시: 공정 조정 및 LH와 일정 재협의",
            owner="건설팀 / 시공사",
            timeline="착공 후"
        ))
        
        # Risk 18: Supply Chain Disruption
        self.risks.append(Risk(
            id="IND-002",
            category=RiskCategory.CONSTRUCTION,
            title="자재 공급망 중단 위험",
            description="주요 건설 자재(철근, 레미콘 등) 공급 차질로 인한 공사 중단",
            impact_score=4,
            likelihood_score=3,
            risk_score=12,
            risk_level=RiskLevel.HIGH,
            current_controls=[
                "복수 자재 공급처 확인"
            ],
            mitigation_strategies=[
                "핵심 자재 장기 공급계약 체결",
                "복수 공급선 확보 (Dual Sourcing)",
                "자재 적정 재고 확보 (Critical Path 자재)",
                "국산 자재 우선 사용으로 수입 의존도 감소",
                "공급망 모니터링 시스템 구축"
            ],
            contingency_plan="공급 중단 시: 대체 자재 사용 승인 및 공정 재조정",
            owner="구매팀 / 건설팀",
            timeline="착공 전부터 준공까지"
        ))
        
        # Risk 19: Material Price Volatility
        self.risks.append(Risk(
            id="IND-003",
            category=RiskCategory.FINANCIAL,
            title="건설 자재비 급등 위험",
            description="철근, 레미콘 등 주요 자재 가격 급등으로 인한 공사비 초과",
            impact_score=4,
            likelihood_score=3,
            risk_score=12,
            risk_level=RiskLevel.HIGH,
            current_controls=[
                "현재 시장 단가 기준 견적",
                "예비비 10% 확보"
            ],
            mitigation_strategies=[
                "고정가격 자재 공급계약 체결 (Price Lock-in)",
                "자재비 연동 조항 계약서 포함 (물가연동제)",
                "조기 발주로 가격 확정",
                "대체 자재 사용 가능한 설계",
                "자재비 예비비 15%로 상향"
            ],
            contingency_plan="자재비 20% 초과 상승 시: VE 적용 및 LH와 공사비 재협의",
            owner="구매팀 / 재무팀",
            timeline="설계 확정부터 공사 완료까지"
        ))
    
    def _assess_seoul_specific_risks(self, data: Dict[str, Any]):
        """Assess Seoul-specific geographic and community risks"""
        
        address = data.get('address', '')
        is_gangnam = '강남' in address or '서초' in address or '송파' in address
        
        # Risk 20: Neighborhood Opposition
        self.risks.append(Risk(
            id="SEO-001",
            category=RiskCategory.REGULATORY,
            title="지역 주민 반대 위험",
            description="인근 주민들의 신축 반대, 일조권/조망권 민원으로 인한 사업 지연",
            impact_score=4,
            likelihood_score=3 if is_gangnam else 2,
            risk_score=12 if is_gangnam else 8,
            risk_level=RiskLevel.HIGH if is_gangnam else RiskLevel.MEDIUM,
            current_controls=[
                "인허가 절차 준수",
                "법적 요건 충족"
            ],
            mitigation_strategies=[
                "사전 주민 설명회 개최 (착공 3개월 전)",
                "일조권/조망권 시뮬레이션 자료 준비",
                "지역 편익시설 제공 방안 검토",
                "주민 의견 수렴 및 반영",
                "동사무소/구청과 사전 협의",
                "투명한 커뮤니케이션 채널 구축"
            ],
            contingency_plan="강한 반대 시: 설계 일부 변경 검토 및 보상 방안 협의",
            owner="홍보팀 / 개발팀",
            timeline="인허가 신청 전부터"
        ))
        
        # Risk 21: Traffic and Access Issues
        self.risks.append(Risk(
            id="SEO-002",
            category=RiskCategory.OPERATIONAL,
            title="교통 접근성 악화 위험",
            description="공사 중 교통 혼잡 및 주차 문제로 인한 민원 및 입주 기피",
            impact_score=3,
            likelihood_score=3,
            risk_score=9,
            risk_level=RiskLevel.MEDIUM,
            current_controls=[
                "현장 교통 영향 평가 예정"
            ],
            mitigation_strategies=[
                "교통영향평가 실시 및 개선 대책 수립",
                "충분한 주차 공간 확보 (법정 기준 110%)",
                "대중교통 접근성 개선 방안 협의",
                "공사 중 주변 도로 교통 관리 계획",
                "입주민용 셔틀버스 운영 검토"
            ],
            contingency_plan="교통 민원 다발 시: 교통 개선 대책 즉시 시행",
            owner="개발팀 / 시공사",
            timeline="착공 전 및 공사 기간"
        ))
        
        # Risk 22: Environmental Impact
        self.risks.append(Risk(
            id="SEO-003",
            category=RiskCategory.REGULATORY,
            title="환경 영향 및 민원 위험",
            description="공사 소음, 분진, 진동으로 인한 인근 주민 민원 및 공사 중단 명령",
            impact_score=3,
            likelihood_score=4,
            risk_score=12,
            risk_level=RiskLevel.HIGH,
            current_controls=[
                "환경영향 최소화 공법 검토"
            ],
            mitigation_strategies=[
                "저소음 공법 적용 (예: 무진동 공법)",
                "방음벽, 분진 차단막 설치",
                "소음 측정기 설치 및 실시간 모니터링",
                "야간/주말 공사 제한",
                "환경관리 책임자 배치",
                "주민 고충처리 센터 운영"
            ],
            contingency_plan="민원 집중 발생 시: 공사 시간 조정 및 추가 저감 조치 시행",
            owner="건설팀 / 환경안전팀",
            timeline="착공부터 준공까지"
        ))
    
    def _assess_strategic_risks(self, data: Dict[str, Any]):
        """Assess strategic and business model risks"""
        
        # Risk 23: LH Purchase Rejection Risk
        self.risks.append(Risk(
            id="STR-001",
            category=RiskCategory.FINANCIAL,
            title="LH 매입 거부 위험",
            description="LH 기준 미충족 또는 정책 변경으로 완공 후 LH 매입 거부",
            impact_score=5,
            likelihood_score=2,
            risk_score=10,
            risk_level=RiskLevel.HIGH,
            current_controls=[
                "LH 신축매입임대 기준 준수",
                "사전 LH 협의"
            ],
            mitigation_strategies=[
                "LH와 사전 MOU 체결 (매입 조건 명시)",
                "단계별 LH 검토 및 승인 확보",
                "LH 기준 초과 달성 목표 설정",
                "대체 Exit 전략 수립 (일반 임대, 매각)",
                "LH 담당자 정기 커뮤니케이션"
            ],
            contingency_plan="LH 매입 거부 시: 일반 주택 임대 전환 또는 제3자 매각",
            owner="사업개발팀 / 경영진",
            timeline="사업 전 단계"
        ))
        
        # Risk 24: Target Tenant Shortage
        self.risks.append(Risk(
            id="STR-002",
            category=RiskCategory.MARKET,
            title="목표 임차인 부족 위험",
            description="청년/신혼부부 등 타겟 임차인 공급 부족으로 입주율 저하",
            impact_score=4,
            likelihood_score=3,
            risk_score=12,
            risk_level=RiskLevel.HIGH,
            current_controls=[
                "인구통계 분석 완료",
                "TypeDemand 분석 실시"
            ],
            mitigation_strategies=[
                "복수 타겟층 설정 (청년+신혼부부+다자녀)",
                "유닛 타입 유연화 설계",
                "인근 기업/대학 제휴 임대",
                "공공주택 특별공급 활용",
                "임대 조건 경쟁력 강화"
            ],
            contingency_plan="타겟 수요 부족 시: 임대 대상 확대 및 LH 협의",
            owner="마케팅팀 / 사업기획팀",
            timeline="설계 단계부터"
        ))
        
        # Risk 25: Technology Obsolescence
        self.risks.append(Risk(
            id="STR-003",
            category=RiskCategory.OPERATIONAL,
            title="시설 노후화 및 기술 진부화 위험",
            description="준공 후 10-20년 운영 시 건물 시설 및 기술의 진부화로 경쟁력 저하",
            impact_score=3,
            likelihood_score=4,
            risk_score=12,
            risk_level=RiskLevel.HIGH,
            current_controls=[
                "최신 건축 기준 적용"
            ],
            mitigation_strategies=[
                "스마트홈 시스템 도입 (IoT, AI)",
                "친환경 인증 획득 (녹색건축, LEED)",
                "리모델링 가능한 구조 설계",
                "에너지 효율 최상급 설비 (등급 1+)",
                "장기 유지보수 계획 수립 (Major Repair Fund)"
            ],
            contingency_plan="10년 후 대규모 리모델링 계획 및 예산 확보",
            owner="개발팀 / 운영팀",
            timeline="설계 단계부터 장기 운영"
        ))
    
    def _generate_risk_matrix(self) -> Dict[str, Any]:
        """Generate risk matrix visualization data"""
        matrix = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for risk in self.risks:
            matrix[risk.risk_level.value].append({
                'id': risk.id,
                'title': risk.title,
                'category': risk.category.value,
                'impact': risk.impact_score,
                'likelihood': risk.likelihood_score,
                'score': risk.risk_score
            })
        
        return matrix
    
    def _generate_risk_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary of risk assessment"""
        total_risks = len(self.risks)
        
        risk_counts = {
            'critical': len([r for r in self.risks if r.risk_level == RiskLevel.CRITICAL]),
            'high': len([r for r in self.risks if r.risk_level == RiskLevel.HIGH]),
            'medium': len([r for r in self.risks if r.risk_level == RiskLevel.MEDIUM]),
            'low': len([r for r in self.risks if r.risk_level == RiskLevel.LOW])
        }
        
        # Top 3 risks
        top_risks = sorted(self.risks, key=lambda r: r.risk_score, reverse=True)[:3]
        
        # Category breakdown
        category_counts = {}
        for category in RiskCategory:
            category_counts[category.value] = len([r for r in self.risks if r.category == category])
        
        return {
            'total_risks': total_risks,
            'risk_counts_by_level': risk_counts,
            'top_3_risks': [
                {
                    'id': r.id,
                    'title': r.title,
                    'score': r.risk_score,
                    'level': r.risk_level.value
                }
                for r in top_risks
            ],
            'category_breakdown': category_counts,
            'overall_risk_level': self._determine_overall_risk_level(risk_counts)
        }
    
    def _generate_mitigation_roadmap(self) -> Dict[str, List[Dict]]:
        """Generate prioritized mitigation roadmap"""
        roadmap = {
            'immediate_action': [],  # Critical and High risks
            'short_term': [],        # Medium risks
            'ongoing_monitoring': [] # Low risks
        }
        
        for risk in self.risks:
            risk_info = {
                'id': risk.id,
                'title': risk.title,
                'category': risk.category.value,
                'level': risk.risk_level.value,
                'key_mitigation': risk.mitigation_strategies[0] if risk.mitigation_strategies else 'N/A',
                'owner': risk.owner,
                'timeline': risk.timeline
            }
            
            if risk.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                roadmap['immediate_action'].append(risk_info)
            elif risk.risk_level == RiskLevel.MEDIUM:
                roadmap['short_term'].append(risk_info)
            else:
                roadmap['ongoing_monitoring'].append(risk_info)
        
        return roadmap
    
    def _calculate_risk_statistics(self) -> Dict[str, Any]:
        """Calculate risk statistics"""
        if not self.risks:
            return {}
        
        risk_scores = [r.risk_score for r in self.risks]
        
        return {
            'total_risks': len(self.risks),
            'average_risk_score': sum(risk_scores) / len(risk_scores),
            'max_risk_score': max(risk_scores),
            'min_risk_score': min(risk_scores),
            'risks_with_mitigation': len([r for r in self.risks if r.mitigation_strategies])
        }
    
    def _calculate_risk_level(self, impact: int, likelihood: int) -> RiskLevel:
        """Calculate risk level based on impact and likelihood"""
        score = impact * likelihood
        
        # Critical: Impact ≥ 4 AND Likelihood ≥ 4
        if impact >= 4 and likelihood >= 4:
            return RiskLevel.CRITICAL
        
        # High: Score ≥ 12
        if score >= 12:
            return RiskLevel.HIGH
        
        # Medium: Score ≥ 6
        if score >= 6:
            return RiskLevel.MEDIUM
        
        # Low: Score < 6
        return RiskLevel.LOW
    
    def _determine_overall_risk_level(self, risk_counts: Dict[str, int]) -> str:
        """Determine overall project risk level"""
        if risk_counts['critical'] > 0:
            return 'critical'
        elif risk_counts['high'] >= 3:
            return 'high'
        elif risk_counts['high'] > 0 or risk_counts['medium'] >= 5:
            return 'medium'
        else:
            return 'low'
    
    def _risk_to_dict(self, risk: Risk) -> Dict[str, Any]:
        """Convert Risk object to dictionary"""
        return {
            'id': risk.id,
            'category': risk.category.value,
            'title': risk.title,
            'description': risk.description,
            'impact_score': risk.impact_score,
            'likelihood_score': risk.likelihood_score,
            'risk_score': risk.risk_score,
            'risk_level': risk.risk_level.value,
            'current_controls': risk.current_controls,
            'mitigation_strategies': risk.mitigation_strategies,
            'contingency_plan': risk.contingency_plan,
            'owner': risk.owner,
            'timeline': risk.timeline
        }


def assess_project_risks_quick(
    data: Dict[str, Any],
    financial_analysis: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Quick risk assessment function
    
    Convenience function for rapid risk evaluation
    """
    framework = RiskMitigationFramework()
    return framework.assess_project_risks(data, financial_analysis)
