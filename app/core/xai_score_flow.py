"""
XAI Score Flow Generator (M1~M6)
==================================

목적:
- M1 FACT → M6 최종 판단까지 전체 흐름을 Sankey Diagram으로 시각화
- 점수의 '합계'가 아니라 '흐름과 손실' 표현
- 설명 가능한 AI (XAI) 구현

Author: ZeroSite Decision OS Team
Date: 2026-01-12
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

# ============================================================
# Sankey Diagram 데이터 구조
# ============================================================

class FlowNode(BaseModel):
    """Sankey Diagram 노드"""
    id: str = Field(..., description="노드 ID (예: M1.road, M2.total)")
    label: str = Field(..., description="노드 라벨 (한글)")
    module: str = Field(..., description="모듈명 (M1/M2/M3/M4/M5/M6)")
    value: Optional[float] = None  # 점수 (M1은 null)
    color: Optional[str] = None  # 색상 (green/yellow/red)

class FlowLink(BaseModel):
    """Sankey Diagram 링크 (흐름)"""
    source: str = Field(..., description="출발 노드 ID")
    target: str = Field(..., description="도착 노드 ID")
    value: float = Field(..., description="흐름 값 (점수 기여도)")
    reason: str = Field(..., description="흐름 이유 (Tooltip용)")
    color: Optional[str] = None  # 링크 색상 (gain: green, loss: red)

class SankeyDiagram(BaseModel):
    """Sankey Diagram 전체 데이터"""
    nodes: List[FlowNode]
    links: List[FlowLink]
    
    # 메타데이터
    total_gain: float = Field(..., description="총 득점")
    total_loss: float = Field(..., description="총 감점")
    final_score: float = Field(..., description="최종 점수")
    final_decision: str = Field(..., description="최종 판단 (GO/CONDITIONAL/NO-GO)")

# ============================================================
# Score Flow Generator
# ============================================================

class ScoreFlowGenerator:
    """
    M1~M6 점수 흐름 생성기
    
    입력:
    - M1 FACT
    - M2 Score
    - M3 Selection
    - M4 (미래)
    - M5 (미래)
    - M6 Final Decision
    
    출력:
    - SankeyDiagram (nodes + links)
    """
    
    def generate(
        self,
        m1_fact: Dict[str, Any],
        m2_score: Dict[str, Any],
        m3_selection: Optional[Dict[str, Any]] = None,
        m4_result: Optional[Dict[str, Any]] = None,
        m5_result: Optional[Dict[str, Any]] = None,
        m6_decision: Optional[Dict[str, Any]] = None
    ) -> SankeyDiagram:
        """
        전체 점수 흐름 생성
        
        Args:
            m1_fact: M1 FACT 데이터
            m2_score: M2 점수 결과
            m3_selection: M3 선택 결과 (optional)
            m4_result: M4 결과 (optional)
            m5_result: M5 결과 (optional)
            m6_decision: M6 최종 판단 (optional)
            
        Returns:
            SankeyDiagram: 전체 흐름 데이터
        """
        nodes = []
        links = []
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # M1 FACT 노드 생성
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        m1_nodes = [
            FlowNode(id="M1.road", label="도로 조건", module="M1", color="blue"),
            FlowNode(id="M1.shape", label="대지 형상", module="M1", color="blue"),
            FlowNode(id="M1.orientation", label="방향/일조", module="M1", color="blue"),
            FlowNode(id="M1.market", label="시세 맥락", module="M1", color="blue"),
            FlowNode(id="M1.building", label="기존 건물", module="M1", color="blue")
        ]
        nodes.extend(m1_nodes)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # M2 점수 노드 생성
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        breakdown = m2_score.get("score_breakdown", {})
        
        # M2 세부 점수 노드
        m2_detail_nodes = [
            FlowNode(id="M2.road", label=f"도로 점수 ({breakdown.get('road', 0):+d})", 
                    module="M2", value=breakdown.get('road', 0), 
                    color=self._get_score_color(breakdown.get('road', 0))),
            FlowNode(id="M2.shape", label=f"형상 점수 ({breakdown.get('shape', 0):+d})", 
                    module="M2", value=breakdown.get('shape', 0),
                    color=self._get_score_color(breakdown.get('shape', 0))),
            FlowNode(id="M2.orientation", label=f"방향 점수 ({breakdown.get('orientation', 0):+d})", 
                    module="M2", value=breakdown.get('orientation', 0),
                    color=self._get_score_color(breakdown.get('orientation', 0))),
            FlowNode(id="M2.market", label=f"시세 점수 ({breakdown.get('market', 0):+d})", 
                    module="M2", value=breakdown.get('market', 0),
                    color=self._get_score_color(breakdown.get('market', 0))),
            FlowNode(id="M2.building", label=f"건물 점수 ({breakdown.get('building', 0):+d})", 
                    module="M2", value=breakdown.get('building', 0),
                    color=self._get_score_color(breakdown.get('building', 0)))
        ]
        nodes.extend(m2_detail_nodes)
        
        # M2 총점 노드
        m2_total = m2_score.get("total_score", 0)
        nodes.append(FlowNode(
            id="M2.total", 
            label=f"M2 총점 ({m2_total}점)", 
            module="M2", 
            value=m2_total,
            color=self._get_score_color(m2_total)
        ))
        
        # M1 → M2 링크 생성
        for i, m1_node in enumerate(m1_nodes):
            m2_node = m2_detail_nodes[i]
            score = breakdown.get(m2_node.id.split('.')[1], 0)
            
            links.append(FlowLink(
                source=m1_node.id,
                target=m2_node.id,
                value=abs(score),  # 절댓값 (흐름 크기)
                reason=breakdown.get(f"{m2_node.id.split('.')[1]}_detail", ""),
                color="green" if score >= 0 else "red"
            ))
        
        # M2 세부 → M2 총점 링크
        for m2_node in m2_detail_nodes:
            score = m2_node.value or 0
            if score != 0:  # 0점은 흐름 생략
                links.append(FlowLink(
                    source=m2_node.id,
                    target="M2.total",
                    value=abs(score),
                    reason=f"{m2_node.label}",
                    color="green" if score >= 0 else "red"
                ))
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # M3 공급유형 노드 생성 (optional)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        if m3_selection:
            recommended_type = m3_selection.get("recommended_type", "UNKNOWN")
            confidence = m3_selection.get("confidence", 0)
            
            # M3 선택 노드
            nodes.append(FlowNode(
                id="M3.selected",
                label=f"공급유형: {recommended_type} ({confidence:.0%})",
                module="M3",
                value=m2_total * confidence,  # 신뢰도 반영
                color="purple"
            ))
            
            # M2 → M3 링크
            links.append(FlowLink(
                source="M2.total",
                target="M3.selected",
                value=m2_total,
                reason=f"M2 {m2_total}점 → {recommended_type} 선택",
                color="purple"
            ))
            
            # 대안 유형 (점선)
            alternatives = m3_selection.get("alternative_types", [])
            for i, alt in enumerate(alternatives[:2]):  # 최대 2개
                nodes.append(FlowNode(
                    id=f"M3.alt{i}",
                    label=f"대안: {alt}",
                    module="M3",
                    color="gray"
                ))
                links.append(FlowLink(
                    source="M2.total",
                    target=f"M3.alt{i}",
                    value=m2_total * 0.3,  # 대안은 약하게
                    reason=f"대안 유형",
                    color="gray"
                ))
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # M6 최종 판단 노드 (optional)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        if m6_decision:
            final_decision = m6_decision.get("decision", "PENDING")
            final_color = {"GO": "green", "CONDITIONAL": "yellow", "NO-GO": "red"}.get(final_decision, "gray")
            
            nodes.append(FlowNode(
                id="M6.decision",
                label=f"최종 판단: {final_decision}",
                module="M6",
                value=m2_total,
                color=final_color
            ))
            
            # M3 → M6 링크 (또는 M2 → M6 직접)
            source_id = "M3.selected" if m3_selection else "M2.total"
            links.append(FlowLink(
                source=source_id,
                target="M6.decision",
                value=m2_total,
                reason=f"최종 판단",
                color=final_color
            ))
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 메타데이터 계산
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        total_gain = sum(breakdown.get(k, 0) for k in breakdown if breakdown.get(k, 0) > 0)
        total_loss = sum(breakdown.get(k, 0) for k in breakdown if breakdown.get(k, 0) < 0)
        
        final_decision_text = m6_decision.get("decision", "PENDING") if m6_decision else m2_score.get("recommendation", "PENDING")
        
        return SankeyDiagram(
            nodes=nodes,
            links=links,
            total_gain=total_gain,
            total_loss=total_loss,
            final_score=m2_total,
            final_decision=final_decision_text
        )
    
    def _get_score_color(self, score: float) -> str:
        """점수에 따른 색상 결정"""
        if score >= 10:
            return "green"
        elif score >= 0:
            return "lightgreen"
        elif score >= -10:
            return "orange"
        else:
            return "red"


# ============================================================
# 전역 인스턴스
# ============================================================

flow_generator = ScoreFlowGenerator()
