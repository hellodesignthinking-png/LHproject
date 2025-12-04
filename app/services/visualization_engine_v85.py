"""
ZeroSite v8.5 Visualization Engine
시각화 데이터 생성 엔진 (JSON 포맷)
프론트엔드에서 D3.js, Charts.js, ApexCharts 등으로 렌더링 가능
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class VisualizationEngineV85:
    """v8.5 시각화 데이터 생성 엔진"""
    
    def __init__(self):
        logger.info("🎨 Visualization Engine v8.5 initialized")
    
    def generate_all_visualizations(
        self,
        financial_result: Dict[str, Any],
        lh_scores: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        모든 시각화 데이터 생성
        
        Args:
            financial_result: 재무 계산 결과
            lh_scores: LH 평가 점수
            analysis_data: 분석 데이터 (입지, 인프라 등)
            
        Returns:
            Dict with all visualization data
        """
        try:
            visualizations = {
                "financial_bar_chart": self._build_financial_bar_chart(financial_result),
                "infra_radar_chart": self._build_infra_radar_chart(analysis_data),
                "infra_grade_gauge": self._build_infra_grade_gauge(analysis_data),
                "lh_eval_framework_chart": self._build_lh_eval_framework(lh_scores),
                "cost_structure_pie": self._build_cost_structure_pie(financial_result),
                "roi_trend_line": self._build_roi_trend_line(financial_result)
            }
            
            logger.info(f"✅ Generated {len(visualizations)} visualizations")
            return visualizations
            
        except Exception as e:
            logger.error(f"❌ Visualization generation failed: {e}")
            return {}
    
    def _build_financial_bar_chart(self, financial_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        재무 요약 바 차트 데이터 생성
        LH Purchase vs Cost Structure
        """
        land_appraisal = financial_result.get("land_appraisal", 0)
        verified_cost = financial_result.get("verified_cost", 0)
        lh_purchase = financial_result.get("lh_purchase_price", 0)
        total_cost = financial_result.get("total_cost", 0)
        
        return {
            "type": "bar",
            "title": "재무 구조 비교",
            "data": {
                "categories": ["토지 감정가", "Verified Cost", "LH 매입가", "총 사업비"],
                "series": [
                    {
                        "name": "금액 (억원)",
                        "data": [
                            round(land_appraisal / 100_000_000, 1),
                            round(verified_cost / 100_000_000, 1),
                            round(lh_purchase / 100_000_000, 1),
                            round(total_cost / 100_000_000, 1)
                        ]
                    }
                ],
                "colors": ["#0047AB", "#28a745", "#ffc107", "#dc3545"]
            },
            "options": {
                "horizontal": False,
                "dataLabels": True,
                "yAxisTitle": "금액 (억원)"
            }
        }
    
    def _build_infra_radar_chart(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        인프라 레이더 차트 데이터 생성
        6개 카테고리: 교육, 교통, 의료, 상업, 문화, 안전
        """
        # POI 분석 데이터에서 점수 추출
        poi_data = analysis_data.get("poi_analysis", {})
        
        categories = ["교육", "교통", "의료", "상업", "문화/여가", "안전"]
        scores = [
            poi_data.get("education_score", 0),
            poi_data.get("transportation_score", 0),
            poi_data.get("healthcare_score", 0),
            poi_data.get("commercial_score", 0),
            poi_data.get("cultural_score", 0),
            analysis_data.get("safety_score", 70)  # 기본값
        ]
        
        return {
            "type": "radar",
            "title": "인프라 종합 평가",
            "data": {
                "categories": categories,
                "series": [
                    {
                        "name": "현재 점수",
                        "data": scores
                    },
                    {
                        "name": "LH 기준 (70점)",
                        "data": [70, 70, 70, 70, 70, 70]
                    }
                ],
                "colors": ["#0047AB", "#28a745"]
            },
            "options": {
                "max": 100,
                "markers": True
            }
        }
    
    def _build_infra_grade_gauge(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        인프라 등급 게이지 차트 데이터 생성
        """
        poi_data = analysis_data.get("poi_analysis", {})
        overall_score = poi_data.get("overall_infrastructure_score", 0)
        grade = poi_data.get("livability_grade", "C")
        
        # 등급별 색상
        grade_colors = {
            "A+": "#28a745", "A": "#28a745",
            "B+": "#17a2b8", "B": "#17a2b8",
            "C": "#ffc107",
            "D": "#fd7e14",
            "F": "#dc3545"
        }
        
        return {
            "type": "gauge",
            "title": "종합 인프라 점수",
            "data": {
                "value": round(overall_score, 1),
                "max": 100,
                "grade": grade,
                "color": grade_colors.get(grade, "#ffc107")
            },
            "options": {
                "startAngle": -90,
                "endAngle": 90,
                "ranges": [
                    {"from": 0, "to": 50, "color": "#dc3545", "label": "F~D"},
                    {"from": 50, "to": 70, "color": "#ffc107", "label": "C"},
                    {"from": 70, "to": 85, "color": "#17a2b8", "label": "B"},
                    {"from": 85, "to": 100, "color": "#28a745", "label": "A"}
                ]
            }
        }
    
    def _build_lh_eval_framework(self, lh_scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        LH 평가 프레임워크 시각화 데이터
        4대 카테고리: 입지(35%), 규모(20%), 사업성(30%), 법규(15%)
        """
        # lh_scores 직접 사용
        
        categories = [
            {"name": "입지", "weight": 35, "score": lh_scores.get("location", 0), "icon": "🗺️", "color": "#0047AB"},
            {"name": "규모", "weight": 20, "score": lh_scores.get("scale", 0), "icon": "🏗️", "color": "#28a745"},
            {"name": "사업성", "weight": 30, "score": lh_scores.get("financial", 0), "icon": "💰", "color": "#ffc107"},
            {"name": "법규", "weight": 15, "score": lh_scores.get("regulation", 0), "icon": "📋", "color": "#dc3545"}
        ]
        
        # 가중 평균 계산
        total_score = sum(c["score"] * c["weight"] / 100 for c in categories)
        
        return {
            "type": "mixed",
            "title": "LH 평가 프레임워크",
            "data": {
                "categories": categories,
                "total_score": round(total_score, 1),
                "grade": self._calculate_grade(total_score)
            },
            "options": {
                "displayType": "card",  # card, bar, radar 중 선택 가능
                "showWeights": True,
                "showIcons": True
            }
        }
    
    def _build_cost_structure_pie(self, financial_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        비용 구조 파이 차트
        """
        breakdown = financial_result.get("cost_breakdown", {})
        
        land_cost = breakdown.get("land_acquisition", {}).get("subtotal", 0)
        construction_cost = breakdown.get("construction_hard_costs", {}).get("subtotal", 0)
        soft_cost = breakdown.get("soft_costs", {}).get("subtotal", 0)
        ffe_cost = breakdown.get("ffe_costs", 0)
        
        return {
            "type": "pie",
            "title": "총 사업비 구조",
            "data": {
                "labels": ["토지비", "건축비", "설계·감리비", "집기비"],
                "series": [
                    round(land_cost / 100_000_000, 1),
                    round(construction_cost / 100_000_000, 1),
                    round(soft_cost / 100_000_000, 1),
                    round(ffe_cost / 100_000_000, 1)
                ],
                "colors": ["#0047AB", "#28a745", "#ffc107", "#17a2b8"]
            },
            "options": {
                "donut": True,
                "showPercentage": True
            }
        }
    
    def _build_roi_trend_line(self, financial_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        ROI 추세 라인 차트 (민감도 분석)
        """
        sensitivity = financial_result.get("sensitivity", {})
        
        scenarios = ["Pessimistic", "Base", "Optimistic"]
        roi_values = [
            sensitivity.get("pessimistic", {}).get("return_metrics", {}).get("irr_percent", 0),
            financial_result.get("roi", 0),
            sensitivity.get("optimistic", {}).get("return_metrics", {}).get("irr_percent", 0)
        ]
        
        return {
            "type": "line",
            "title": "ROI 민감도 분석",
            "data": {
                "categories": scenarios,
                "series": [
                    {
                        "name": "ROI (%)",
                        "data": roi_values
                    },
                    {
                        "name": "LH 목표 (15%)",
                        "data": [15, 15, 15]
                    }
                ],
                "colors": ["#0047AB", "#dc3545"]
            },
            "options": {
                "markers": True,
                "dataLabels": True,
                "yAxisTitle": "ROI (%)"
            }
        }
    
    def _calculate_grade(self, score: float) -> str:
        """점수를 등급으로 변환"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C"
        elif score >= 40:
            return "D"
        else:
            return "F"


# 테스트 함수
def test_visualization_engine():
    """시각화 엔진 테스트"""
    engine = VisualizationEngineV85()
    
    # 테스트 데이터
    test_analysis = {
        "poi_analysis": {
            "education_score": 85.0,
            "transportation_score": 78.0,
            "healthcare_score": 72.0,
            "commercial_score": 88.0,
            "cultural_score": 65.0,
            "overall_infrastructure_score": 77.6,
            "livability_grade": "B+"
        },
        "lh_scores": {
            "location": 78,
            "scale": 65,
            "financial": 12,
            "regulation": 91
        },
        "safety_score": 75
    }
    
    test_financial = {
        "land_appraisal": 8_662_500_000,
        "verified_cost": 13_483_290_240,
        "lh_purchase_price": 22_145_790_240,
        "total_cost": 23_186_642_381,
        "roi": -4.49,
        "cost_breakdown": {
            "land_acquisition": {"subtotal": 8_662_500_000},
            "construction_hard_costs": {"subtotal": 13_483_290_240},
            "soft_costs": {"subtotal": 1_040_852_141},
            "ffe_costs": 0
        },
        "sensitivity": {
            "pessimistic": {"return_metrics": {"irr_percent": -8.2}},
            "optimistic": {"return_metrics": {"irr_percent": -1.5}}
        }
    }
    
    result = engine.generate_all_visualizations(test_analysis, test_financial)
    
    print("="*80)
    print("Visualization Engine v8.5 Test Results")
    print("="*80)
    for key, viz in result.items():
        print(f"\n{key}:")
        print(f"  Type: {viz.get('type')}")
        print(f"  Title: {viz.get('title')}")
    
    return result


if __name__ == "__main__":
    test_visualization_engine()
