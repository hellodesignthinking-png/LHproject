"""
정책 분석 AI 서비스
OpenAI GPT를 활용한 정책 영향 분석 및 전략 생성
"""

import os
import asyncio
from typing import Dict, List, Optional
from openai import OpenAI


class PolicyAIService:
    """정책 분석 AI 서비스"""
    
    def __init__(self):
        self.client = None
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
    
    async def analyze_policy_impact(
        self, 
        policy_data: Dict,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, str]:
        """
        정책 영향을 AI로 분석
        
        Args:
            policy_data: 정책 데이터
            analysis_type: 분석 유형 (comprehensive/lh/policy/regulation)
            
        Returns:
            AI 분석 결과
        """
        if not self.client:
            return self._get_fallback_analysis(policy_data, analysis_type)
        
        try:
            # 정책 데이터를 텍스트로 변환
            policy_text = self._format_policy_data(policy_data)
            
            # AI 프롬프트 생성
            prompt = self._create_analysis_prompt(policy_text, analysis_type)
            
            # OpenAI API 호출 (동기 -> 비동기 변환)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 LH 신축매입임대 사업 전문가이자 정책 분석가입니다. 정책 변화가 사업에 미치는 영향을 분석하고 구체적인 전략을 제시합니다."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
            )
            
            # 결과 파싱
            analysis_text = response.choices[0].message.content
            return self._parse_analysis_result(analysis_text)
            
        except Exception as e:
            print(f"AI 분석 오류: {e}")
            return self._get_fallback_analysis(policy_data, analysis_type)
    
    def _format_policy_data(self, policy_data: Dict) -> str:
        """정책 데이터를 텍스트로 포맷팅"""
        text_parts = []
        
        # 카테고리 정보
        text_parts.append(f"## 분석 카테고리: {policy_data.get('category', 'N/A')}")
        text_parts.append(f"기간: {policy_data.get('period', 'N/A')}")
        text_parts.append(f"총 업데이트: {policy_data.get('total_count', 0)}건\n")
        
        # 주요 변경사항
        if 'summary' in policy_data and 'key_changes' in policy_data['summary']:
            text_parts.append("### 주요 변경사항:")
            for change in policy_data['summary']['key_changes']:
                text_parts.append(f"- {change}")
            text_parts.append("")
        
        # 상세 데이터
        if 'data' in policy_data:
            text_parts.append("### 상세 정책:")
            for idx, item in enumerate(policy_data['data'][:3], 1):  # 최대 3개만
                text_parts.append(f"\n**{idx}. {item.get('title', 'N/A')}**")
                text_parts.append(f"발행일: {item.get('published_at', 'N/A')}")
                text_parts.append(f"중요도: {item.get('importance', 'N/A')}")
                
                # 내용 요약 (길면 잘라냄)
                content = item.get('content', '')
                if len(content) > 500:
                    content = content[:500] + "..."
                text_parts.append(f"내용:\n{content}")
        
        return "\n".join(text_parts)
    
    def _create_analysis_prompt(self, policy_text: str, analysis_type: str) -> str:
        """분석 프롬프트 생성"""
        base_prompt = f"""
다음 정책 모니터링 결과를 분석하여, LH 신축매입임대 사업자를 위한 구체적인 전략을 제시해주세요.

{policy_text}

다음 형식으로 분석해주세요:

## 1. 핵심 요약
(3-5줄로 전체 상황을 요약)

## 2. 기회 요인
(정책 변화로 인한 긍정적 기회 3-5가지)

## 3. 위험 요인
(주의해야 할 리스크와 도전 과제 3-5가지)

## 4. 즉시 실행 전략 (우선순위 높음)
(지금 당장 해야 할 구체적인 행동 3-5가지)

## 5. 중장기 전략 (3-6개월)
(앞으로 준비해야 할 전략적 과제 3-5가지)

## 6. 비용 영향 대응
(비용 증가 요인에 대한 구체적 대응 방안)

## 7. 최종 권장사항
(종합적인 전략 방향과 핵심 메시지)

각 항목은 구체적이고 실행 가능한 내용으로 작성해주세요.
"""
        return base_prompt
    
    def _parse_analysis_result(self, analysis_text: str) -> Dict[str, str]:
        """AI 분석 결과를 구조화된 딕셔너리로 파싱"""
        sections = {
            "summary": "",
            "opportunities": "",
            "risks": "",
            "immediate_actions": "",
            "mid_term_strategy": "",
            "cost_response": "",
            "recommendations": ""
        }
        
        # 섹션별로 텍스트 분리
        current_section = None
        section_map = {
            "핵심 요약": "summary",
            "기회 요인": "opportunities",
            "위험 요인": "risks",
            "즉시 실행 전략": "immediate_actions",
            "중장기 전략": "mid_term_strategy",
            "비용 영향 대응": "cost_response",
            "최종 권장사항": "recommendations"
        }
        
        lines = analysis_text.split("\n")
        for line in lines:
            # 섹션 헤더 감지
            for header, section_key in section_map.items():
                if header in line and line.startswith("#"):
                    current_section = section_key
                    break
            else:
                # 내용 추가
                if current_section and line.strip():
                    sections[current_section] += line + "\n"
        
        # 각 섹션 정리
        for key in sections:
            sections[key] = sections[key].strip()
        
        return sections
    
    def _get_fallback_analysis(self, policy_data: Dict, analysis_type: str) -> Dict[str, str]:
        """AI 사용 불가 시 기본 분석 제공"""
        return {
            "summary": "정책 모니터링 결과를 기반으로 사업 전략을 수립해야 합니다.",
            "opportunities": """
- 규제 완화 기회 적극 활용
- 인센티브 제도 최대한 활용
- 신규 사업 모델 검토
            """.strip(),
            "risks": """
- 건축비 증가 리스크 관리
- 규제 강화 대비 필요
- 시장 변화 지속 모니터링
            """.strip(),
            "immediate_actions": """
- 관련 부서와 긴급 협의
- 비용 영향 상세 분석
- 프로젝트 일정 재검토
            """.strip(),
            "mid_term_strategy": """
- 장기 대응 계획 수립
- 조직 역량 강화
- 파트너십 구축
            """.strip(),
            "cost_response": """
- 원가 절감 방안 모색
- 가치 공학(VE) 적용
- 대량구매 할인 협상
            """.strip(),
            "recommendations": """
정책 변화를 기회로 활용하되, 리스크 관리에 만전을 기하시기 바랍니다.
지속적인 모니터링과 신속한 대응이 핵심입니다.
            """.strip()
        }


# 싱글톤 인스턴스
_policy_ai_service = None

def get_policy_ai_service() -> PolicyAIService:
    """정책 AI 서비스 싱글톤 인스턴스 반환"""
    global _policy_ai_service
    if _policy_ai_service is None:
        _policy_ai_service = PolicyAIService()
    return _policy_ai_service
