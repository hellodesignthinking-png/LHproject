"""
ZeroSite v11.0 - Risk Matrix Generator
=======================================
6×6 리스크 매트릭스 시각화 엔진

목적: 리스크 평가 결과를 전문적인 매트릭스 형태로 시각화
- 6개 리스크 유형 × 6개 평가 항목
- High/Medium/Low 색상 코딩
- 상세 설명 툴팁
- 치명적 리스크 하이라이트

Author: ZeroSite Team
Date: 2025-12-05
"""

from typing import Dict, Any, List, Tuple
from enum import Enum


class RiskLevel(Enum):
    """리스크 수준"""
    CRITICAL = "CRITICAL"  # 치명적 (즉시 해결 필요)
    HIGH = "HIGH"  # 높음 (사업 추진 전 해결 필요)
    MEDIUM = "MEDIUM"  # 보통 (관리 필요)
    LOW = "LOW"  # 낮음 (모니터링)
    NONE = "NONE"  # 없음


class RiskMatrixGenerator:
    """
    리스크 매트릭스 HTML 생성 엔진
    
    6개 리스크 유형:
    1. 규제 리스크 (Regulatory)
    2. 재무 리스크 (Financial)
    3. 토지비 리스크 (Land Cost)
    4. 세대유형 리스크 (Unit Type)
    5. 세대수 리스크 (Unit Count)
    6. 기타 사업 리스크 (Other Business)
    
    6개 평가 항목:
    1. 발생 가능성 (Probability)
    2. 영향도 (Impact)
    3. 대응 난이도 (Mitigation Difficulty)
    4. 비용 (Cost)
    5. 일정 영향 (Schedule Impact)
    6. 종합 평가 (Overall)
    """
    
    def __init__(self):
        self.risk_categories = {
            'regulatory': '규제 리스크',
            'financial': '재무 리스크',
            'land_cost': '토지비 리스크',
            'unit_type': '세대유형 리스크',
            'unit_count': '세대수 리스크',
            'other_business': '기타 사업 리스크'
        }
        
        self.evaluation_criteria = {
            'probability': '발생<br>가능성',
            'impact': '영향도',
            'mitigation': '대응<br>난이도',
            'cost': '비용<br>영향',
            'schedule': '일정<br>영향',
            'overall': '종합<br>평가'
        }
    
    # ========================================================================
    # 1. Risk Matrix HTML Generation
    # ========================================================================
    
    def generate_risk_matrix_html(
        self,
        decision_result: Dict[str, Any],
        lh_result: Dict[str, Any]
    ) -> str:
        """
        6×6 리스크 매트릭스 HTML 생성
        
        Args:
            decision_result: Decision Engine 결과
            lh_result: LH Score Mapper 결과
            
        Returns:
            리스크 매트릭스 HTML
        """
        # 리스크 데이터 추출
        risks = self._analyze_risks(decision_result, lh_result)
        
        # 치명적 리스크 목록
        critical_risks = decision_result.get('critical_risks', [])
        
        html = f"""
        <div class="risk-matrix-section">
            <h3>🎯 리스크 평가 매트릭스 (6×6)</h3>
            
            <div class="matrix-summary">
                <div class="summary-card critical-count">
                    <div class="label">치명적 리스크</div>
                    <div class="value">{len(critical_risks)}개</div>
                </div>
                <div class="summary-card high-count">
                    <div class="label">높은 리스크</div>
                    <div class="value">{self._count_by_level(risks, 'HIGH')}개</div>
                </div>
                <div class="summary-card medium-count">
                    <div class="label">보통 리스크</div>
                    <div class="value">{self._count_by_level(risks, 'MEDIUM')}개</div>
                </div>
                <div class="summary-card low-count">
                    <div class="label">낮은 리스크</div>
                    <div class="value">{self._count_by_level(risks, 'LOW')}개</div>
                </div>
            </div>
            
            <div class="risk-matrix-container">
                <table class="risk-matrix-table">
                    <thead>
                        <tr>
                            <th class="category-header">리스크 유형</th>
        """
        
        # Column headers
        for criterion_key, criterion_name in self.evaluation_criteria.items():
            html += f'<th class="criterion-header">{criterion_name}</th>\n'
        
        html += """
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Risk rows
        for risk_key, risk_name in self.risk_categories.items():
            risk_data = risks.get(risk_key, {})
            is_critical = self._is_critical_risk(risk_key, critical_risks)
            
            row_class = "critical-risk-row" if is_critical else ""
            
            html += f'<tr class="{row_class}">\n'
            html += f'<td class="risk-name-cell">'
            
            if is_critical:
                html += f'<span class="critical-badge">🚨 CRITICAL</span><br>'
            
            html += f'<strong>{risk_name}</strong></td>\n'
            
            # Evaluation cells
            for criterion in self.evaluation_criteria.keys():
                cell_data = risk_data.get(criterion, {})
                level = cell_data.get('level', 'NONE')
                score = cell_data.get('score', 0)
                description = cell_data.get('description', '')
                
                cell_class = self._get_cell_class(level)
                
                html += f'''
                <td class="risk-cell {cell_class}" data-tooltip="{description}">
                    <div class="cell-content">
                        <div class="risk-score">{score}/10</div>
                        <div class="risk-level">{self._translate_level(level)}</div>
                    </div>
                </td>
                '''
            
            html += '</tr>\n'
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <!-- Risk Legends -->
            <div class="risk-legends">
                <div class="legend-item">
                    <span class="legend-color risk-critical"></span>
                    <span class="legend-label">치명적 (9-10점): 즉시 해결 필요</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color risk-high"></span>
                    <span class="legend-label">높음 (7-8점): 사업 추진 전 해결</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color risk-medium"></span>
                    <span class="legend-label">보통 (4-6점): 관리 및 모니터링</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color risk-low"></span>
                    <span class="legend-label">낮음 (1-3점): 정상 수준</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color risk-none"></span>
                    <span class="legend-label">없음 (0점): 리스크 없음</span>
                </div>
            </div>
        """
        
        # Critical Risks Detail
        if critical_risks:
            html += self._generate_critical_risks_detail(critical_risks)
        
        # Risk Explanations
        html += self._generate_risk_explanations(risks)
        
        html += """
        </div>
        
        <style>
        .risk-matrix-section {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .matrix-summary {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            justify-content: space-around;
        }
        
        .summary-card {
            flex: 1;
            padding: 15px;
            background: white;
            border-radius: 6px;
            text-align: center;
            border: 2px solid #ddd;
        }
        
        .summary-card .label {
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .summary-card .value {
            font-size: 28px;
            font-weight: bold;
        }
        
        .critical-count { border-color: #dc3545; }
        .critical-count .value { color: #dc3545; }
        .high-count { border-color: #fd7e14; }
        .high-count .value { color: #fd7e14; }
        .medium-count { border-color: #ffc107; }
        .medium-count .value { color: #e6a800; }
        .low-count { border-color: #28a745; }
        .low-count .value { color: #28a745; }
        
        .risk-matrix-container {
            overflow-x: auto;
            margin: 20px 0;
        }
        
        .risk-matrix-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .risk-matrix-table th {
            background: #2c3e50;
            color: white;
            padding: 12px 8px;
            font-size: 12px;
            font-weight: 600;
            text-align: center;
            border: 1px solid #1a252f;
        }
        
        .category-header {
            width: 150px;
            text-align: left !important;
        }
        
        .criterion-header {
            width: 100px;
        }
        
        .risk-matrix-table td {
            padding: 10px 8px;
            border: 1px solid #ddd;
            text-align: center;
        }
        
        .risk-name-cell {
            text-align: left !important;
            font-weight: 500;
        }
        
        .critical-badge {
            display: inline-block;
            background: #dc3545;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .critical-risk-row {
            background: #fff5f5 !important;
        }
        
        .risk-cell {
            position: relative;
            cursor: help;
            min-height: 60px;
        }
        
        .risk-cell:hover {
            transform: scale(1.05);
            z-index: 10;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* Risk Level Colors */
        .risk-critical {
            background: #dc3545 !important;
            color: white !important;
            font-weight: bold;
        }
        
        .risk-high {
            background: #fd7e14 !important;
            color: white !important;
        }
        
        .risk-medium {
            background: #ffc107 !important;
            color: #333 !important;
        }
        
        .risk-low {
            background: #28a745 !important;
            color: white !important;
        }
        
        .risk-none {
            background: #e9ecef !important;
            color: #6c757d !important;
        }
        
        .cell-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
        }
        
        .risk-score {
            font-size: 16px;
            font-weight: bold;
        }
        
        .risk-level {
            font-size: 10px;
            text-transform: uppercase;
        }
        
        /* Tooltip */
        .risk-cell[data-tooltip]:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            z-index: 1000;
            max-width: 300px;
            white-space: normal;
            width: max-content;
        }
        
        .risk-legends {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 6px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .legend-color {
            width: 24px;
            height: 24px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        
        .legend-label {
            font-size: 13px;
            color: #333;
        }
        
        .risk-detail-section {
            margin-top: 30px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            border: 2px solid #dc3545;
        }
        
        .risk-detail-section h4 {
            color: #dc3545;
            margin-bottom: 15px;
        }
        
        .risk-item {
            margin-bottom: 15px;
            padding: 12px;
            background: #fff5f5;
            border-left: 4px solid #dc3545;
        }
        
        .risk-item-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .risk-item-description {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .risk-item-impact {
            font-size: 13px;
            color: #dc3545;
            font-weight: 500;
        }
        
        .risk-explanations {
            margin-top: 25px;
            padding: 20px;
            background: white;
            border-radius: 8px;
        }
        
        .risk-explanations h4 {
            margin-bottom: 20px;
            color: #2c3e50;
        }
        
        .explanation-item {
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }
        
        .explanation-title {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        
        .explanation-content {
            font-size: 14px;
            line-height: 1.6;
            color: #555;
        }
        
        .explanation-content ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        
        .explanation-content li {
            margin: 5px 0;
        }
        </style>
        """
        
        return html
    
    # ========================================================================
    # 2. Risk Analysis
    # ========================================================================
    
    def _analyze_risks(
        self,
        decision_result: Dict[str, Any],
        lh_result: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        리스크 상세 분석
        
        각 리스크 유형에 대해 6개 항목 평가
        """
        risks = {}
        
        # 1. Regulatory Risk
        risks['regulatory'] = self._analyze_regulatory_risk(lh_result)
        
        # 2. Financial Risk
        risks['financial'] = self._analyze_financial_risk(decision_result, lh_result)
        
        # 3. Land Cost Risk
        risks['land_cost'] = self._analyze_land_cost_risk(lh_result)
        
        # 4. Unit Type Risk
        risks['unit_type'] = self._analyze_unit_type_risk(lh_result)
        
        # 5. Unit Count Risk
        risks['unit_count'] = self._analyze_unit_count_risk(lh_result)
        
        # 6. Other Business Risk
        risks['other_business'] = self._analyze_other_business_risk(decision_result, lh_result)
        
        return risks
    
    def _analyze_regulatory_risk(self, lh_result: Dict) -> Dict[str, Any]:
        """규제 리스크 분석"""
        zone_score = lh_result.get('category_scores', {}).get('policy_alignment', 0)
        zone_max = 20
        
        # 정책 부합도가 낮을수록 규제 리스크 높음
        risk_score = max(0, 10 - (zone_score / zone_max * 10))
        
        return {
            'probability': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '용도지역 및 건축 규제 위반 가능성'
            },
            'impact': {
                'level': self._score_to_level(risk_score + 1),
                'score': min(10, int(risk_score + 1)),
                'description': '인허가 불가 시 사업 중단'
            },
            'mitigation': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '설계 변경으로 대응 가능 여부'
            },
            'cost': {
                'level': self._score_to_level(risk_score - 1),
                'score': max(0, int(risk_score - 1)),
                'description': '규제 대응 추가 비용'
            },
            'schedule': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '인허가 지연 가능성'
            },
            'overall': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '규제 리스크 종합 평가'
            }
        }
    
    def _analyze_financial_risk(self, decision_result: Dict, lh_result: Dict) -> Dict[str, Any]:
        """재무 리스크 분석"""
        financial_score = lh_result.get('category_scores', {}).get('financial_soundness', 0)
        financial_max = 15
        
        risk_score = max(0, 10 - (financial_score / financial_max * 10))
        
        return {
            'probability': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': 'IRR/ROI 미달 가능성'
            },
            'impact': {
                'level': self._score_to_level(risk_score + 2),
                'score': min(10, int(risk_score + 2)),
                'description': '투자 손실 발생 규모'
            },
            'mitigation': {
                'level': self._score_to_level(risk_score + 1),
                'score': min(10, int(risk_score + 1)),
                'description': '재무 구조 개선 난이도'
            },
            'cost': {
                'level': self._score_to_level(risk_score + 2),
                'score': min(10, int(risk_score + 2)),
                'description': '재무 리스크 대응 비용'
            },
            'schedule': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '자금 조달 지연 영향'
            },
            'overall': {
                'level': self._score_to_level(risk_score + 1),
                'score': min(10, int(risk_score + 1)),
                'description': '재무 리스크 종합 평가'
            }
        }
    
    def _analyze_land_cost_risk(self, lh_result: Dict) -> Dict[str, Any]:
        """토지비 리스크 분석"""
        # 토지비가 총 투자비의 60% 이상이면 리스크
        # 간단한 추정: 사업성 점수로 역산
        business_score = lh_result.get('category_scores', {}).get('business_feasibility', 0)
        business_max = 30
        
        risk_score = max(0, 8 - (business_score / business_max * 8))
        
        return {
            'probability': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '토지비 과다 발생 가능성'
            },
            'impact': {
                'level': self._score_to_level(risk_score + 1),
                'score': min(10, int(risk_score + 1)),
                'description': '수익성 악화 정도'
            },
            'mitigation': {
                'level': self._score_to_level(8),  # 토지비는 변경 어려움
                'score': 8,
                'description': '토지비 조정 난이도 (매우 높음)'
            },
            'cost': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '토지비 리스크 추가 비용'
            },
            'schedule': {
                'level': self._score_to_level(risk_score - 2),
                'score': max(0, int(risk_score - 2)),
                'description': '토지비로 인한 일정 영향'
            },
            'overall': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '토지비 리스크 종합 평가'
            }
        }
    
    def _analyze_unit_type_risk(self, lh_result: Dict) -> Dict[str, Any]:
        """세대유형 리스크 분석"""
        unit_type_score = lh_result.get('score_details', {}).get('policy', {}).get('unit_type_score', 70)
        
        # 세대유형 적합도가 낮을수록 리스크
        risk_score = max(0, 10 - (unit_type_score / 100 * 10))
        
        return {
            'probability': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '부적합 세대유형 선정 가능성'
            },
            'impact': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '입주자 유치 실패 영향'
            },
            'mitigation': {
                'level': self._score_to_level(risk_score - 3),
                'score': max(0, int(risk_score - 3)),
                'description': '세대유형 변경 용이성'
            },
            'cost': {
                'level': self._score_to_level(risk_score - 2),
                'score': max(0, int(risk_score - 2)),
                'description': '세대유형 조정 비용'
            },
            'schedule': {
                'level': self._score_to_level(risk_score - 2),
                'score': max(0, int(risk_score - 2)),
                'description': '세대유형 변경 일정 영향'
            },
            'overall': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '세대유형 리스크 종합 평가'
            }
        }
    
    def _analyze_unit_count_risk(self, lh_result: Dict) -> Dict[str, Any]:
        """세대수 리스크 분석"""
        unit_count_score = lh_result.get('score_details', {}).get('business', {}).get('unit_count', 45)
        
        # 30세대 미만이면 고위험
        if unit_count_score < 30:
            risk_score = 9
        elif unit_count_score < 40:
            risk_score = 6
        elif unit_count_score < 50:
            risk_score = 3
        else:
            risk_score = 1
        
        return {
            'probability': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': 'LH 최소 기준 미달 가능성'
            },
            'impact': {
                'level': self._score_to_level(risk_score + 1),
                'score': min(10, int(risk_score + 1)),
                'description': 'LH 매입 거부 시 영향'
            },
            'mitigation': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '세대수 증대 가능성'
            },
            'cost': {
                'level': self._score_to_level(risk_score - 1),
                'score': max(0, int(risk_score - 1)),
                'description': '세대수 증대 추가 비용'
            },
            'schedule': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '설계 변경 일정 지연'
            },
            'overall': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '세대수 리스크 종합 평가'
            }
        }
    
    def _analyze_other_business_risk(self, decision_result: Dict, lh_result: Dict) -> Dict[str, Any]:
        """기타 사업 리스크 분석"""
        total_score = lh_result.get('total_score', 50)
        
        # 총점이 낮을수록 기타 리스크 높음
        risk_score = max(0, 10 - (total_score / 100 * 10))
        
        return {
            'probability': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '예상치 못한 리스크 발생 가능성'
            },
            'impact': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '기타 리스크 종합 영향도'
            },
            'mitigation': {
                'level': self._score_to_level(risk_score - 1),
                'score': max(0, int(risk_score - 1)),
                'description': '기타 리스크 대응 난이도'
            },
            'cost': {
                'level': self._score_to_level(risk_score - 1),
                'score': max(0, int(risk_score - 1)),
                'description': '기타 리스크 대응 비용'
            },
            'schedule': {
                'level': self._score_to_level(risk_score - 1),
                'score': max(0, int(risk_score - 1)),
                'description': '기타 리스크 일정 영향'
            },
            'overall': {
                'level': self._score_to_level(risk_score),
                'score': int(risk_score),
                'description': '기타 사업 리스크 종합 평가'
            }
        }
    
    # ========================================================================
    # 3. Helper Functions
    # ========================================================================
    
    def _score_to_level(self, score: float) -> str:
        """점수를 리스크 레벨로 변환"""
        if score >= 9:
            return 'CRITICAL'
        elif score >= 7:
            return 'HIGH'
        elif score >= 4:
            return 'MEDIUM'
        elif score >= 1:
            return 'LOW'
        else:
            return 'NONE'
    
    def _get_cell_class(self, level: str) -> str:
        """리스크 레벨에 따른 CSS 클래스 반환"""
        return f"risk-{level.lower()}"
    
    def _translate_level(self, level: str) -> str:
        """리스크 레벨 한글 번역"""
        translations = {
            'CRITICAL': '치명적',
            'HIGH': '높음',
            'MEDIUM': '보통',
            'LOW': '낮음',
            'NONE': '없음'
        }
        return translations.get(level, level)
    
    def _count_by_level(self, risks: Dict, level: str) -> int:
        """특정 레벨의 리스크 개수 카운트"""
        count = 0
        for risk_data in risks.values():
            for criterion_data in risk_data.values():
                if criterion_data.get('level') == level:
                    count += 1
        return count
    
    def _is_critical_risk(self, risk_key: str, critical_risks: List) -> bool:
        """해당 리스크가 치명적 리스크인지 확인"""
        risk_keywords = {
            'regulatory': ['규제', 'regulatory', '용도지역'],
            'financial': ['재무', 'financial', 'IRR', 'ROI'],
            'land_cost': ['토지', 'land', '감정가'],
            'unit_type': ['세대유형', 'unit type', '공급유형'],
            'unit_count': ['세대수', 'unit count', '호수'],
            'other_business': ['기타', 'other', '사업']
        }
        
        keywords = risk_keywords.get(risk_key, [])
        
        for risk in critical_risks:
            risk_str = str(risk).lower()
            for keyword in keywords:
                if keyword.lower() in risk_str:
                    return True
        return False
    
    def _generate_critical_risks_detail(self, critical_risks: List) -> str:
        """치명적 리스크 상세 설명 HTML"""
        html = """
        <div class="risk-detail-section">
            <h4>🚨 치명적 리스크 상세</h4>
            <p style="color: #666; margin-bottom: 20px;">
                아래 리스크는 사업 추진 전 반드시 해결되어야 하는 치명적 요인입니다.
            </p>
        """
        
        for i, risk in enumerate(critical_risks, 1):
            if isinstance(risk, dict):
                category = risk.get('category', '기타')
                description = risk.get('description', str(risk))
                impact = risk.get('impact', '사업 추진 불가')
            else:
                category = '기타'
                description = str(risk)
                impact = '사업 추진 불가'
            
            html += f"""
            <div class="risk-item">
                <div class="risk-item-title">#{i}. {category}</div>
                <div class="risk-item-description">{description}</div>
                <div class="risk-item-impact">💥 영향: {impact}</div>
            </div>
            """
        
        html += "</div>"
        return html
    
    def _generate_risk_explanations(self, risks: Dict) -> str:
        """리스크 상세 설명 HTML"""
        html = """
        <div class="risk-explanations">
            <h4>📋 리스크 유형별 상세 설명</h4>
        """
        
        explanations = {
            'regulatory': {
                'title': '규제 리스크',
                'content': '''
                    용도지역, 건축법, 주택법 등 관련 법규 위반 가능성을 평가합니다.
                    <ul>
                        <li><strong>발생 시 영향:</strong> 인허가 불가, 사업 중단</li>
                        <li><strong>대응 방안:</strong> 사전 법규 검토, 설계 변경, 전문가 자문</li>
                        <li><strong>모니터링:</strong> 법규 변경 사항 지속 확인</li>
                    </ul>
                '''
            },
            'financial': {
                'title': '재무 리스크',
                'content': '''
                    IRR, ROI 등 수익성 지표가 기준치에 미달하여 투자 손실이 발생할 가능성을 평가합니다.
                    <ul>
                        <li><strong>발생 시 영향:</strong> 투자 손실, 자금 조달 실패</li>
                        <li><strong>대응 방안:</strong> 재무 구조 개선, 건축비 절감, 금융 조건 협상</li>
                        <li><strong>모니터링:</strong> 월별 재무 지표 추적</li>
                    </ul>
                '''
            },
            'land_cost': {
                'title': '토지비 리스크',
                'content': '''
                    토지비가 총 투자비의 60% 이상을 차지하여 수익성 확보가 어려울 가능성을 평가합니다.
                    <ul>
                        <li><strong>발생 시 영향:</strong> 수익성 급감, 사업성 악화</li>
                        <li><strong>대응 방안:</strong> 감정가 재조정 협상, 용적률 최대 활용</li>
                        <li><strong>모니터링:</strong> 토지비 비중 지속 확인</li>
                    </ul>
                '''
            },
            'unit_type': {
                'title': '세대유형 리스크',
                'content': '''
                    선정된 세대유형이 지역 특성 및 LH 정책에 부합하지 않아 입주자 유치가 어려울 가능성을 평가합니다.
                    <ul>
                        <li><strong>발생 시 영향:</strong> 입주율 저하, LH 매입 거부</li>
                        <li><strong>대응 방안:</strong> 세대유형 재검토, 복합 공급 유형 고려</li>
                        <li><strong>모니터링:</strong> 지역 수요 변화 추적</li>
                    </ul>
                '''
            },
            'unit_count': {
                'title': '세대수 리스크',
                'content': '''
                    세대수가 LH 최소 기준(30세대)에 미달하여 사업 추진이 불가능할 가능성을 평가합니다.
                    <ul>
                        <li><strong>발생 시 영향:</strong> LH 매입 불가, 사업 중단</li>
                        <li><strong>대응 방안:</strong> 설계 변경으로 세대수 증대</li>
                        <li><strong>모니터링:</strong> 세대수 확정 전 면밀한 검토</li>
                    </ul>
                '''
            },
            'other_business': {
                'title': '기타 사업 리스크',
                'content': '''
                    위 5가지 외 예상치 못한 리스크 (민원, 환경, 시장 변화 등)가 발생할 가능성을 평가합니다.
                    <ul>
                        <li><strong>발생 시 영향:</strong> 일정 지연, 추가 비용 발생</li>
                        <li><strong>대응 방안:</strong> 예비비 확보, 리스크 매니지먼트 체계 구축</li>
                        <li><strong>모니터링:</strong> 주기적 리스크 재평가</li>
                    </ul>
                '''
            }
        }
        
        for risk_key, explanation in explanations.items():
            html += f"""
            <div class="explanation-item">
                <div class="explanation-title">{explanation['title']}</div>
                <div class="explanation-content">{explanation['content']}</div>
            </div>
            """
        
        html += "</div>"
        return html


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    print("✅ Risk Matrix Generator v11.0 Module Loaded")
    print("="*60)
    
    # Test
    generator = RiskMatrixGenerator()
    
    test_decision = {
        'decision': 'REVIEW',
        'critical_risks': [
            {'category': '세대수 부족', 'description': '30세대 미만', 'impact': 'LH 매입 불가'},
            {'category': '재무 리스크', 'description': 'IRR 2.0% 미만', 'impact': '투자 손실'}
        ]
    }
    
    test_lh = {
        'total_score': 66.5,
        'category_scores': {
            'location_suitability': 18.0,
            'business_feasibility': 23.0,
            'policy_alignment': 16.0,
            'financial_soundness': 12.0
        },
        'score_details': {
            'policy': {'unit_type_score': 75},
            'business': {'unit_count': 28}
        }
    }
    
    html = generator.generate_risk_matrix_html(test_decision, test_lh)
    print(f"✅ Risk Matrix HTML Generated: {len(html):,} characters")
    
    print("\n" + "="*60)
    print("✅ Risk Matrix Generator Test Complete")
