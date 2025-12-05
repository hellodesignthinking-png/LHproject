"""
ZeroSite v11.0 Complete Report Generator
==========================================
Phase 2 Complete Integration:
- v9.1 Analysis Engine
- v10.0 Professional Structure (8 Parts)
- v11.0 LH Score Mapper (100점 채점)
- v11.0 Decision Engine (GO/NO-GO)
- v11.0 Unit-Type Analysis (5 types x 6 criteria)
- v11.0 Pseudo-Data Engine
- v11.0 Feasibility Checker

Target: 43-47 pages with comprehensive LH evaluation
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Import v11.0 engines
from app.lh_score_mapper_v11 import LHScoreMapper, LHScoreBreakdown
from app.lh_decision_engine_v11 import LHDecisionEngine, DecisionResult
from app.unit_type_analyzer_v11 import UnitTypeSuitabilityAnalyzer
from app.pseudo_data_engine_v11 import PseudoDataEngine
from app.feasibility_checker_v11 import FeasibilityChecker
from app.narrative_generator_v11 import NarrativeGenerator


def generate_lh_score_table_html(lh_score: LHScoreBreakdown) -> str:
    """LH 100점 채점표 HTML 생성 (v7.5 스타일)"""
    
    def score_color(score: float, max_score: float) -> str:
        """점수별 색상 결정"""
        percentage = (score / max_score) * 100
        if percentage >= 80:
            return "score-excellent"  # Green
        elif percentage >= 60:
            return "score-good"  # Yellow-green
        elif percentage >= 40:
            return "score-fair"  # Orange
        else:
            return "score-poor"  # Red
    
    html = f"""
    <div class="lh-score-section">
        <h3>📊 LH 신축매입임대 평가 점수</h3>
        
        <div class="total-score-card {score_color(lh_score.total_score, 100)}">
            <div class="score-label">종합 점수</div>
            <div class="score-value">{lh_score.total_score:.1f} / 100</div>
            <div class="grade-badge grade-{lh_score.grade.value}">{lh_score.grade.value} 등급</div>
        </div>
        
        <table class="lh-score-table">
            <thead>
                <tr>
                    <th>평가 영역</th>
                    <th>세부 항목</th>
                    <th>배점</th>
                    <th>득점</th>
                    <th>달성률</th>
                </tr>
            </thead>
            <tbody>
                <!-- 1. 입지 적합성 (25점) -->
                <tr class="category-row">
                    <td rowspan="4"><strong>1. 입지 적합성</strong></td>
                    <td>교통 접근성</td>
                    <td>10</td>
                    <td class="{score_color(lh_score.transportation_access, 10)}">{lh_score.transportation_access:.1f}</td>
                    <td>{(lh_score.transportation_access/10*100):.0f}%</td>
                </tr>
                <tr>
                    <td>생활 편의성</td>
                    <td>8</td>
                    <td class="{score_color(lh_score.living_convenience, 8)}">{lh_score.living_convenience:.1f}</td>
                    <td>{(lh_score.living_convenience/8*100):.0f}%</td>
                </tr>
                <tr>
                    <td>교육 환경</td>
                    <td>7</td>
                    <td class="{score_color(lh_score.education_environment, 7)}">{lh_score.education_environment:.1f}</td>
                    <td>{(lh_score.education_environment/7*100):.0f}%</td>
                </tr>
                <tr class="subtotal-row">
                    <td><strong>소계</strong></td>
                    <td><strong>25</strong></td>
                    <td class="{score_color(lh_score.location_total, 25)}"><strong>{lh_score.location_total:.1f}</strong></td>
                    <td><strong>{(lh_score.location_total/25*100):.0f}%</strong></td>
                </tr>
                
                <!-- 2. 사업 타당성 (30점) -->
                <tr class="category-row">
                    <td rowspan="4"><strong>2. 사업 타당성</strong></td>
                    <td>용적률/건폐율 적정성</td>
                    <td>10</td>
                    <td class="{score_color(lh_score.far_bcr_adequacy, 10)}">{lh_score.far_bcr_adequacy:.1f}</td>
                    <td>{(lh_score.far_bcr_adequacy/10*100):.0f}%</td>
                </tr>
                <tr>
                    <td>세대수 적정성</td>
                    <td>8</td>
                    <td class="{score_color(lh_score.unit_count_adequacy, 8)}">{lh_score.unit_count_adequacy:.1f}</td>
                    <td>{(lh_score.unit_count_adequacy/8*100):.0f}%</td>
                </tr>
                <tr>
                    <td>토지 가격 적정성</td>
                    <td>12</td>
                    <td class="{score_color(lh_score.land_price_adequacy, 12)}">{lh_score.land_price_adequacy:.1f}</td>
                    <td>{(lh_score.land_price_adequacy/12*100):.0f}%</td>
                </tr>
                <tr class="subtotal-row">
                    <td><strong>소계</strong></td>
                    <td><strong>30</strong></td>
                    <td class="{score_color(lh_score.feasibility_total, 30)}"><strong>{lh_score.feasibility_total:.1f}</strong></td>
                    <td><strong>{(lh_score.feasibility_total/30*100):.0f}%</strong></td>
                </tr>
                
                <!-- 3. 정책 정합성 (20점) -->
                <tr class="category-row">
                    <td rowspan="4"><strong>3. 정책 정합성</strong></td>
                    <td>용도지역 적합성</td>
                    <td>8</td>
                    <td class="{score_color(lh_score.zone_suitability, 8)}">{lh_score.zone_suitability:.1f}</td>
                    <td>{(lh_score.zone_suitability/8*100):.0f}%</td>
                </tr>
                <tr>
                    <td>주택 정책 부합도</td>
                    <td>7</td>
                    <td class="{score_color(lh_score.housing_policy_alignment, 7)}">{lh_score.housing_policy_alignment:.1f}</td>
                    <td>{(lh_score.housing_policy_alignment/7*100):.0f}%</td>
                </tr>
                <tr>
                    <td>공급 유형 적합성</td>
                    <td>5</td>
                    <td class="{score_color(lh_score.unit_type_suitability, 5)}">{lh_score.unit_type_suitability:.1f}</td>
                    <td>{(lh_score.unit_type_suitability/5*100):.0f}%</td>
                </tr>
                <tr class="subtotal-row">
                    <td><strong>소계</strong></td>
                    <td><strong>20</strong></td>
                    <td class="{score_color(lh_score.policy_total, 20)}"><strong>{lh_score.policy_total:.1f}</strong></td>
                    <td><strong>{(lh_score.policy_total/20*100):.0f}%</strong></td>
                </tr>
                
                <!-- 4. 재무 건전성 (15점) -->
                <tr class="category-row">
                    <td rowspan="4"><strong>4. 재무 건전성</strong></td>
                    <td>IRR/ROI 수준</td>
                    <td>8</td>
                    <td class="{score_color(lh_score.irr_roi_level, 8)}">{lh_score.irr_roi_level:.1f}</td>
                    <td>{(lh_score.irr_roi_level/8*100):.0f}%</td>
                </tr>
                <tr>
                    <td>투자 회수 기간</td>
                    <td>4</td>
                    <td class="{score_color(lh_score.payback_period, 4)}">{lh_score.payback_period:.1f}</td>
                    <td>{(lh_score.payback_period/4*100):.0f}%</td>
                </tr>
                <tr>
                    <td>자금 조달 가능성</td>
                    <td>3</td>
                    <td class="{score_color(lh_score.financing_feasibility, 3)}">{lh_score.financing_feasibility:.1f}</td>
                    <td>{(lh_score.financing_feasibility/3*100):.0f}%</td>
                </tr>
                <tr class="subtotal-row">
                    <td><strong>소계</strong></td>
                    <td><strong>15</strong></td>
                    <td class="{score_color(lh_score.financial_total, 15)}"><strong>{lh_score.financial_total:.1f}</strong></td>
                    <td><strong>{(lh_score.financial_total/15*100):.0f}%</strong></td>
                </tr>
                
                <!-- 5. 리스크 수준 (10점) -->
                <tr class="category-row">
                    <td rowspan="4"><strong>5. 리스크 수준</strong></td>
                    <td>법규 리스크</td>
                    <td>4</td>
                    <td class="{score_color(lh_score.legal_risk, 4)}">{lh_score.legal_risk:.1f}</td>
                    <td>{(lh_score.legal_risk/4*100):.0f}%</td>
                </tr>
                <tr>
                    <td>시장 리스크</td>
                    <td>3</td>
                    <td class="{score_color(lh_score.market_risk, 3)}">{lh_score.market_risk:.1f}</td>
                    <td>{(lh_score.market_risk/3*100):.0f}%</td>
                </tr>
                <tr>
                    <td>시공 리스크</td>
                    <td>3</td>
                    <td class="{score_color(lh_score.construction_risk, 3)}">{lh_score.construction_risk:.1f}</td>
                    <td>{(lh_score.construction_risk/3*100):.0f}%</td>
                </tr>
                <tr class="subtotal-row">
                    <td><strong>소계</strong></td>
                    <td><strong>10</strong></td>
                    <td class="{score_color(lh_score.risk_total, 10)}"><strong>{lh_score.risk_total:.1f}</strong></td>
                    <td><strong>{(lh_score.risk_total/10*100):.0f}%</strong></td>
                </tr>
                
                <!-- 총점 -->
                <tr class="total-row">
                    <td colspan="2"><strong>📊 총점</strong></td>
                    <td><strong>100</strong></td>
                    <td class="{score_color(lh_score.total_score, 100)}"><strong>{lh_score.total_score:.1f}</strong></td>
                    <td><strong>{lh_score.total_score:.0f}%</strong></td>
                </tr>
            </tbody>
        </table>
        
        <!-- 강점 분석 -->
        <div class="analysis-section strengths">
            <h4>✅ 강점 (Strengths)</h4>
            <ul>
                {"".join([f"<li>{s}</li>" for s in lh_score.strengths])}
            </ul>
        </div>
        
        <!-- 약점 분석 -->
        <div class="analysis-section weaknesses">
            <h4>⚠️ 약점 (Weaknesses)</h4>
            <ul>
                {"".join([f"<li>{w}</li>" for w in lh_score.weaknesses])}
            </ul>
        </div>
        
        <!-- 개선 권고 -->
        <div class="analysis-section recommendations">
            <h4>💡 개선 권고사항 (Recommendations)</h4>
            <ul>
                {"".join([f"<li>{r}</li>" for r in lh_score.recommendations])}
            </ul>
        </div>
    </div>
    
    <style>
        .lh-score-section {{
            margin: 30px 0;
        }}
        
        .total-score-card {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }}
        
        .score-label {{
            font-size: 18px;
            margin-bottom: 10px;
        }}
        
        .score-value {{
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .grade-badge {{
            display: inline-block;
            font-size: 24px;
            font-weight: bold;
            padding: 10px 30px;
            border-radius: 25px;
            margin-top: 10px;
        }}
        
        .grade-A {{ background: #10b981; }}
        .grade-B {{ background: #3b82f6; }}
        .grade-C {{ background: #f59e0b; }}
        .grade-D {{ background: #ef4444; }}
        .grade-F {{ background: #991b1b; }}
        
        .lh-score-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 13px;
        }}
        
        .lh-score-table th {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: bold;
            border: 1px solid #ddd;
        }}
        
        .lh-score-table td {{
            padding: 10px 8px;
            text-align: center;
            border: 1px solid #ddd;
        }}
        
        .lh-score-table .category-row td:first-child {{
            background: #f1f5f9;
            font-weight: bold;
            text-align: left;
        }}
        
        .lh-score-table .subtotal-row {{
            background: #e2e8f0;
            font-weight: bold;
        }}
        
        .lh-score-table .total-row {{
            background: #1e3a8a;
            color: white;
            font-weight: bold;
            font-size: 15px;
        }}
        
        .score-excellent {{
            background-color: #d1fae5 !important;
            color: #065f46;
            font-weight: bold;
        }}
        
        .score-good {{
            background-color: #fef08a !important;
            color: #854d0e;
        }}
        
        .score-fair {{
            background-color: #fed7aa !important;
            color: #9a3412;
        }}
        
        .score-poor {{
            background-color: #fecaca !important;
            color: #991b1b;
        }}
        
        .analysis-section {{
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
        }}
        
        .strengths {{
            background: #d1fae5;
            border-left: 4px solid #10b981;
        }}
        
        .weaknesses {{
            background: #fed7aa;
            border-left: 4px solid #f59e0b;
        }}
        
        .recommendations {{
            background: #dbeafe;
            border-left: 4px solid #3b82f6;
        }}
        
        .analysis-section h4 {{
            margin-top: 0;
            margin-bottom: 15px;
        }}
        
        .analysis-section ul {{
            margin: 0;
            padding-left: 20px;
        }}
        
        .analysis-section li {{
            margin: 8px 0;
        }}
    </style>
    """
    
    return html


print("✅ v11.0 Report Generator Module Loaded (Part 1/3)")


def generate_unit_type_matrix_html(unit_analysis: Dict[str, Any]) -> str:
    """5x7 세대유형 비교 매트릭스 HTML 생성 (v7.5 스타일)"""
    
    types = unit_analysis.get("type_scores", {})
    
    def score_color(score: float) -> str:
        if score >= 85:
            return "score-excellent"
        elif score >= 70:
            return "score-good"
        elif score >= 50:
            return "score-fair"
        else:
            return "score-poor"
    
    type_info = {
        "youth": ("👨‍🎓 청년형", "청년가구 (19-34세)"),
        "newlywed": ("👫 신혼형", "신혼부부 가구"),
        "senior": ("👴 고령자형", "65세 이상 고령자"),
        "general": ("👨‍👩‍👧 일반형", "일반 가구"),
        "vulnerable": ("🤝 취약계층형", "저소득층 가구")
    }
    
    html = """
    <div class="unit-type-matrix-section">
        <h3>📋 세대유형 적합성 비교 매트릭스</h3>
        
        <table class="unit-type-matrix">
            <thead>
                <tr>
                    <th rowspan="2">세대유형</th>
                    <th colspan="6">평가 기준 (0-100점)</th>
                    <th rowspan="2">종합점수</th>
                </tr>
                <tr>
                    <th>인구구조</th>
                    <th>교통</th>
                    <th>인프라</th>
                    <th>정책</th>
                    <th>경제성</th>
                    <th>사회수요</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for type_key, (type_name, type_desc) in type_info.items():
        type_data = types.get(type_key, {})
        scores = type_data.get("detailed_scores", {})
        total = type_data.get("total_score", 0)
        
        demo = scores.get("demographics", 0)
        trans = scores.get("transportation", 0)
        infra = scores.get("infrastructure", 0)
        policy = scores.get("policy", 0)
        econ = scores.get("economic", 0)
        social = scores.get("social", 0)
        
        html += f"""
                <tr>
                    <td class="type-name">
                        <strong>{type_name}</strong><br>
                        <span class="type-desc">{type_desc}</span>
                    </td>
                    <td class="{score_color(demo)}">{demo:.1f}</td>
                    <td class="{score_color(trans)}">{trans:.1f}</td>
                    <td class="{score_color(infra)}">{infra:.1f}</td>
                    <td class="{score_color(policy)}">{policy:.1f}</td>
                    <td class="{score_color(econ)}">{econ:.1f}</td>
                    <td class="{score_color(social)}">{social:.1f}</td>
                    <td class="{score_color(total)} total-score"><strong>{total:.1f}</strong></td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
        
        <div class="matrix-legend">
            <h4>📊 평가 기준</h4>
            <div class="legend-grid">
                <div class="legend-item">
                    <strong>인구구조</strong>: 대상 연령층 인구 비율, 가구 구조 적합성
                </div>
                <div class="legend-item">
                    <strong>교통</strong>: 지하철/버스 접근성, 출퇴근 편의성
                </div>
                <div class="legend-item">
                    <strong>인프라</strong>: 필요 시설(학교/병원/복지관) 근접성
                </div>
                <div class="legend-item">
                    <strong>정책</strong>: 정부 주택정책 우선순위 부합도
                </div>
                <div class="legend-item">
                    <strong>경제성</strong>: 적정 임대료, 수요-공급 균형
                </div>
                <div class="legend-item">
                    <strong>사회수요</strong>: 지역 사회적 필요도, 공공성
                </div>
            </div>
        </div>
    </div>
    
    <style>
        .unit-type-matrix {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 13px;
        }
        
        .unit-type-matrix th {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: bold;
            border: 1px solid #ddd;
        }
        
        .unit-type-matrix td {
            padding: 10px 8px;
            text-align: center;
            border: 1px solid #ddd;
        }
        
        .unit-type-matrix .type-name {
            text-align: left;
            font-weight: bold;
            width: 180px;
        }
        
        .type-desc {
            font-size: 11px;
            color: #666;
            font-weight: normal;
        }
        
        .unit-type-matrix .total-score {
            font-size: 14px;
            font-weight: bold;
            width: 80px;
        }
        
        .matrix-legend {
            margin: 20px 0;
            padding: 20px;
            background: #f8fafc;
            border-radius: 8px;
        }
        
        .legend-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 15px;
        }
        
        .legend-item {
            padding: 10px;
            background: white;
            border-left: 3px solid #3b82f6;
            font-size: 13px;
        }
    </style>
    """
    
    return html


def generate_decision_html(decision_result: DecisionResult) -> str:
    """GO/NO-GO 의사결정 결과 HTML 생성"""
    
    decision_colors = {
        "GO": "decision-go",
        "REVIEW": "decision-review",
        "NO_GO": "decision-nogo"
    }
    
    decision_icons = {
        "GO": "✅",
        "REVIEW": "⚠️",
        "NO_GO": "🛑"
    }
    
    decision_titles = {
        "GO": "사업 추진 권장 (GO)",
        "REVIEW": "조건부 추진 (REVIEW)",
        "NO_GO": "사업 추진 불가 (NO-GO)"
    }
    
    decision_type = decision_result.decision.value
    icon = decision_icons.get(decision_type, "📊")
    title = decision_titles.get(decision_type, "의사결정")
    color_class = decision_colors.get(decision_type, "decision-review")
    
    html = f"""
    <div class="decision-section">
        <div class="decision-card {color_class}">
            <div class="decision-icon">{icon}</div>
            <div class="decision-title">{title}</div>
            <div class="decision-confidence">신뢰도: {decision_result.confidence:.1f}%</div>
        </div>
        
        <div class="decision-detail">
            <h4>🎯 주요 근거</h4>
            <p class="primary-reason">{decision_result.primary_reason}</p>
            
            <h4>📋 세부 근거</h4>
            <ul class="supporting-reasons">
                {"".join([f"<li>{reason}</li>" for reason in decision_result.supporting_reasons])}
            </ul>
        </div>
        
        {_generate_critical_risks_html(decision_result.critical_risks) if decision_result.critical_risks else ""}
        
        <div class="improvement-strategies">
            <h4>🎯 개선 전략</h4>
            <ul>
                {"".join([f"<li>{strategy}</li>" for strategy in decision_result.improvement_strategies])}
            </ul>
        </div>
        
        <div class="priority-actions">
            <h4>⏰ 우선 실행 과제</h4>
            <ol class="action-list">
                {"".join([f"<li>{action}</li>" for action in decision_result.priority_actions])}
            </ol>
        </div>
        
        <div class="executive-summary">
            <h4>📊 경영진 요약</h4>
            <pre class="summary-text">{decision_result.executive_summary}</pre>
        </div>
        
        <div class="next-steps">
            <h4>▶️ Next Steps</h4>
            <ul class="next-steps-list">
                {"".join([f"<li>{step}</li>" for step in decision_result.next_steps])}
            </ul>
        </div>
    </div>
    
    <style>
        .decision-card {{
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            margin: 30px 0;
            color: white;
        }}
        
        .decision-go {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }}
        
        .decision-review {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }}
        
        .decision-nogo {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }}
        
        .decision-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        
        .decision-title {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        
        .decision-confidence {{
            font-size: 20px;
            opacity: 0.9;
        }}
        
        .decision-detail {{
            margin: 30px 0;
            padding: 25px;
            background: #f8fafc;
            border-radius: 10px;
        }}
        
        .primary-reason {{
            font-size: 16px;
            font-weight: bold;
            color: #1e3a8a;
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-left: 4px solid #3b82f6;
        }}
        
        .supporting-reasons {{
            margin: 15px 0;
            padding-left: 25px;
        }}
        
        .supporting-reasons li {{
            margin: 10px 0;
            font-size: 14px;
        }}
        
        .improvement-strategies {{
            margin: 25px 0;
            padding: 20px;
            background: #dbeafe;
            border-radius: 8px;
        }}
        
        .priority-actions {{
            margin: 25px 0;
            padding: 20px;
            background: #fef3c7;
            border-radius: 8px;
        }}
        
        .action-list {{
            margin: 15px 0;
            padding-left: 25px;
        }}
        
        .action-list li {{
            margin: 12px 0;
            font-weight: 500;
        }}
        
        .executive-summary {{
            margin: 25px 0;
            padding: 20px;
            background: #f1f5f9;
            border-radius: 8px;
        }}
        
        .summary-text {{
            white-space: pre-wrap;
            font-family: 'Malgun Gothic', sans-serif;
            font-size: 14px;
            line-height: 1.8;
            margin: 15px 0;
        }}
        
        .next-steps {{
            margin: 25px 0;
            padding: 20px;
            background: #d1fae5;
            border-radius: 8px;
        }}
        
        .next-steps-list {{
            margin: 15px 0;
            padding-left: 25px;
        }}
        
        .next-steps-list li {{
            margin: 10px 0;
            font-weight: 500;
        }}
    </style>
    """
    
    return html


def _generate_critical_risks_html(critical_risks: List) -> str:
    """치명적 리스크 HTML 생성"""
    if not critical_risks:
        return ""
    
    html = """
    <div class="critical-risks-section">
        <h4>🔴 치명적 리스크 ({} 건)</h4>
        <div class="risk-cards">
    """.format(len(critical_risks))
    
    for risk in critical_risks:
        html += f"""
            <div class="risk-card">
                <div class="risk-category">🔴 {risk.category}</div>
                <div class="risk-description">{risk.description}</div>
                <div class="risk-impact"><strong>영향:</strong> {risk.impact}</div>
                <div class="risk-mitigation"><strong>완화방안:</strong> {risk.mitigation}</div>
            </div>
        """
    
    html += """
        </div>
    </div>
    
    <style>
        .critical-risks-section {
            margin: 25px 0;
            padding: 20px;
            background: #fee2e2;
            border-radius: 8px;
            border-left: 4px solid #ef4444;
        }
        
        .risk-cards {
            margin-top: 15px;
        }
        
        .risk-card {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
            border-left: 3px solid #dc2626;
        }
        
        .risk-category {
            font-weight: bold;
            color: #dc2626;
            margin-bottom: 8px;
        }
        
        .risk-description {
            margin: 8px 0;
            font-size: 14px;
        }
        
        .risk-impact {
            margin: 8px 0;
            font-size: 13px;
            color: #666;
        }
        
        .risk-mitigation {
            margin: 8px 0;
            font-size: 13px;
            color: #059669;
        }
    </style>
    """
    
    return html


print("✅ v11.0 Report Generator Module Loaded (Part 2/3)")


# Main v11.0 Report Generator Function
def generate_v11_ultra_pro_report(
    address: str,
    land_area: float,
    land_appraisal_price: int,
    zone_type: str,
    analysis_result: Dict[str, Any]) -> str:
    """
    ZeroSite v11.0 Ultra Professional Report Generator
    
    Generates 43-47 page comprehensive LH evaluation report with:
    - LH 100-point scoring system
    - A/B/C/D/F grading
    - GO/NO-GO decision
    - Unit-type suitability analysis
    - Feasibility checking
    - Realistic data generation
    
    Args:
        address: 대상 부지 주소
        land_area: 토지 면적 (㎡)
        land_appraisal_price: 토지 감정가 (원)
        zone_type: 용도지역
        analysis_result: v9.1 REAL 분석 결과
    
    Returns:
        HTML string (43-47 pages)
    """
    
    print("🚀 v11.0 Report Generation Started...")
    
    # Extract v9.1 analysis data
    basic_info = analysis_result.get("basic_info", {})
    land_info = analysis_result.get("land_info", {})
    dev_plan = analysis_result.get("development_plan", {})
    financial = analysis_result.get("financial_result", {})
    
    coord = basic_info.get("coordinates", {"latitude": 37.5665, "longitude": 126.9780})
    bcr = land_info.get("building_coverage_ratio", 60)
    far = land_info.get("floor_area_ratio", 200)
    unit_count = dev_plan.get("unit_count", 20)
    max_floors = dev_plan.get("max_floors", 5)
    total_gfa = dev_plan.get("total_gross_floor_area", land_area * far / 100)
    
    # ============================================================
    # v11.0 Engine Initialization
    # ============================================================
    
    print("  📊 Initializing v11.0 engines...")
    
    # 1. Pseudo-Data Engine
    pseudo_engine = PseudoDataEngine(address=address, coord=coord)
    pseudo_data = pseudo_engine.generate_comprehensive_report()
    print("  ✅ Pseudo-Data generated")
    
    # 2. Unit-Type Analyzer
    unit_analyzer = UnitTypeSuitabilityAnalyzer()
    unit_analysis = unit_analyzer.analyze_all_types(
        address=address,
        coord=coord,
        zone_type=zone_type,
        land_area=land_area
    )
    recommended_type = unit_analysis.get("recommended_type", "general")
    print(f"  ✅ Unit-Type analyzed: {recommended_type}")
    
    # 3. Feasibility Checker
    feasibility_checker = FeasibilityChecker(
        land_area=land_area,
        bcr=bcr,
        far=far,
        zone_type=zone_type,
        max_floors=max_floors,
        unit_count=unit_count,
        total_gfa=total_gfa
    )
    feasibility_result = feasibility_checker.check_unit_type_feasibility(recommended_type)
    print(f"  ✅ Feasibility checked: {feasibility_result['feasibility_status']}")
    
    # 4. LH Score Mapper
    lh_mapper = LHScoreMapper()
    lh_score = lh_mapper.calculate_lh_score(analysis_result, unit_analysis, pseudo_data)
    print(f"  ✅ LH Score calculated: {lh_score.total_score:.1f}/100 (Grade {lh_score.grade.value})")
    
    # 5. Decision Engine
    decision_engine = LHDecisionEngine()
    decision_result = decision_engine.make_decision(lh_score, analysis_result, feasibility_result)
    print(f"  ✅ Decision made: {decision_result.decision.value}")
    
    # ============================================================
    # Generate v11.0 Enhanced HTML Sections
    # ============================================================
    
    print("  📝 Generating HTML sections...")
    
    lh_score_html = generate_lh_score_table_html(lh_score)
    unit_matrix_html = generate_unit_type_matrix_html(unit_analysis)
    decision_html = generate_decision_html(decision_result)
    
    print("  ✅ All v11.0 sections generated")
    
    # ============================================================
    # Import and Use v10.0 Base Report
    # ============================================================
    
    print("  📄 Using v10.0 base structure...")
    
    # Import v10.0 generator
    from app.report_generator_v10_ultra_pro import generate_v10_ultra_pro_report
    
    # Generate v10.0 base
    v10_html = generate_v10_ultra_pro_report(
        address=address,
        land_area=land_area,
        land_appraisal_price=land_appraisal_price,
        zone_type=zone_type,
        analysis_result=analysis_result
    )
    
    # ============================================================
    # Inject v11.0 Enhancements into v10.0 HTML
    # ============================================================
    
    print("  🔧 Injecting v11.0 enhancements...")
    
    # Replace version number
    v11_html = v10_html.replace("v10.0", "v11.0")
    v11_html = v11_html.replace("v9.1 + v7.5", "v9.1 + v10.0 + v11.0")
    
    # Inject LH Score Table after Part 6 header
    part6_marker = '<div class="section-header">6.1 LH 평가 체계</div>'
    if part6_marker in v11_html:
        v11_html = v11_html.replace(
            part6_marker,
            f'{part6_marker}\n\n{lh_score_html}\n'
        )
        print("  ✅ LH Score Table injected into Part 6")
    
    # Inject Unit-Type Matrix into Part 4
    part4_marker = '<div class="section-header">4.3 경쟁 현황</div>'
    if part4_marker in v11_html:
        v11_html = v11_html.replace(
            part4_marker,
            f'{unit_matrix_html}\n\n<div class="page-break"></div>\n\n{part4_marker}'
        )
        print("  ✅ Unit-Type Matrix injected into Part 4")
    
    # Inject Decision Result into Part 8
    part8_marker = '<div class="section-header">8.1 종합 의견</div>'
    if part8_marker in v11_html:
        v11_html = v11_html.replace(
            part8_marker,
            f'{part8_marker}\n\n{decision_html}\n'
        )
        print("  ✅ Decision Result injected into Part 8")
    
    # Add v11.0 metadata
    v11_html = v11_html.replace(
        '보고서 버전:</strong> v10.0',
        f'''보고서 버전:</strong> v11.0 Ultra Professional Edition<br>
        <strong>LH 평가:</strong> {lh_score.total_score:.1f}/100 (Grade {lh_score.grade.value})<br>
        <strong>의사결정:</strong> {decision_result.decision.value} (신뢰도 {decision_result.confidence:.1f}%)<br>
        <strong>추천 세대유형:</strong> {recommended_type}'''
    )
    
    print("✅ v11.0 Report Generation Complete!")
    print(f"  📄 HTML Length: {len(v11_html):,} characters")
    print(f"  📊 LH Score: {lh_score.total_score:.1f}/100 ({lh_score.grade.value})")
    print(f"  🎯 Decision: {decision_result.decision.value}")
    
    return v11_html


# Quick test function
def test_v11_generator():
    """Test v11.0 generator with sample data"""
    
    test_analysis = {
        "basic_info": {
            "address": "서울특별시 마포구 월드컵북로 120",
            "coordinates": {"latitude": 37.563945, "longitude": 126.913344},
            "legal_dong_code": "11440"
        },
        "land_info": {
            "land_area": 1000,
            "land_appraisal_price": 9000000000,
            "zone_type": "제3종일반주거지역",
            "building_coverage_ratio": 60,
            "floor_area_ratio": 250
        },
        "development_plan": {
            "unit_count": 42,
            "max_floors": 10,
            "parking_spaces": 42,
            "total_gross_floor_area": 2500
        },
        "financial_result": {
            "irr_10yr": 3.6,
            "roi": 37.11,
            "npv_10yr": 580000000,
            "total_investment": 16500000000
        },
        "risk_assessment": {
            "overall_risk": "MEDIUM"
        },
        "final_recommendation": {
            "decision": "PROCEED",
            "confidence": 85.0
        }
    }
    
    html = generate_v11_ultra_pro_report(
        address="서울특별시 마포구 월드컵북로 120",
        land_area=1000,
        land_appraisal_price=9000000000,
        zone_type="제3종일반주거지역",
        analysis_result=test_analysis
    )
    
    return html


print("✅ v11.0 Report Generator Module Loaded (Part 3/3)")
print("=" * 60)
print("ZeroSite v11.0 Ultra Professional Report Generator")
print("=" * 60)
print("📊 Features:")
print("  - LH 100-point scoring system")
print("  - A/B/C/D/F grading")
print("  - GO/NO-GO decision engine")
print("  - 5 unit types x 6 criteria analysis")
print("  - Feasibility checking")
print("  - Realistic data generation")
print("")
print("📄 Usage:")
print("  from app.report_generator_v11_complete import generate_v11_ultra_pro_report")
print("  html = generate_v11_ultra_pro_report(address, land_area, price, zone, analysis)")
print("=" * 60)


if __name__ == "__main__":
    print("\n🧪 Running test...")
    test_html = test_v11_generator()
    print(f"\n✅ Test complete! Generated {len(test_html):,} characters")
