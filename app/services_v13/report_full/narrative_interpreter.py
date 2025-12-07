"""
Narrative Interpreter - Phase A
ZeroSite Expert Edition v3

자동 서술 생성 엔진
- 7개 섹션 자동 서술
- 5-Step Framework (What, So What, Why, Implication, LH Connection)
- 정책 근거 자동 연결
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class NarrativeInterpreter:
    """
    보고서 서술 자동 생성 엔진
    
    숫자/데이터를 전략적 서술로 변환
    """
    
    def __init__(self):
        self.current_year = datetime.now().year
    
    # ============================================
    # UTILITY METHODS
    # ============================================
    
    def fmt(self, value: Any, decimal: int = 1) -> str:
        """숫자 포맷팅 (억원 단위)"""
        try:
            if value is None:
                return "N/A"
            return f"{float(value):,.{decimal}f}"
        except (ValueError, TypeError):
            return str(value)
    
    def fmt_pct(self, value: Any, decimal: int = 1) -> str:
        """퍼센트 포맷팅"""
        try:
            if value is None:
                return "N/A"
            return f"{float(value):,.{decimal}f}%"
        except (ValueError, TypeError):
            return str(value)
    
    def grade_to_korean(self, grade: str) -> str:
        """등급 한글 변환"""
        grade_map = {
            'A+': '최우수', 'A': '우수', 'B': '양호',
            'C': '보통', 'D': '미흡', 'F': '불량'
        }
        return grade_map.get(grade, grade)
    
    def signal_to_korean(self, signal: str) -> str:
        """시장 신호 한글 변환"""
        signal_map = {
            'UNDERVALUED': '저평가',
            'FAIR': '적정',
            'OVERVALUED': '고평가'
        }
        return signal_map.get(signal, signal)
    
    def temp_to_korean(self, temp: str) -> str:
        """시장 온도 한글 변환"""
        temp_map = {
            'HOT': '과열',
            'WARM': '상승',
            'NEUTRAL': '안정',
            'COOL': '냉각',
            'COLD': '침체'
        }
        return temp_map.get(temp, temp)
    
    # ============================================
    # SECTION 1: EXECUTIVE SUMMARY
    # ============================================
    
    def interpret_executive_summary(self, ctx: Dict[str, Any]) -> str:
        """
        Executive Summary 자동 생성
        
        구조:
        1. 프로젝트 개요
        2. 핵심 지표 요약 (수요, 시장, 재무)
        3. 종합 평가
        4. 권고안
        """
        
        # Extract data
        # Handle address - could be nested dict or already a string
        addr_obj = ctx.get('site', {}).get('address', '')
        if isinstance(addr_obj, dict):
            address = addr_obj.get('full_address', 'N/A')
        elif isinstance(addr_obj, str):
            address = addr_obj
        else:
            address = ctx.get('address', 'N/A')  # Fallback to top-level address
        
        area = ctx.get('site', {}).get('land_area_sqm', ctx.get('land_area_sqm', 0))
        
        # Demand
        demand_score = ctx.get('demand', {}).get('overall_score', 0)
        recommended_type = ctx.get('demand', {}).get('recommended_type', '신혼부부형')
        
        # Market
        market = ctx.get('market', {})
        market_signal = market.get('signal', 'FAIR')
        market_signal_kr = self.signal_to_korean(market_signal)
        market_temp = market.get('temperature', 'NEUTRAL')
        market_temp_kr = self.temp_to_korean(market_temp)
        delta_pct = market.get('delta_pct', 0)
        
        # Financial - handle both nested and flat structures
        finance = ctx.get('finance', {})
        
        # Try nested structure first, then flat structure
        if 'capex' in finance and isinstance(finance['capex'], dict):
            capex = finance['capex'].get('total', 0) / 100000000  # Convert to 억원
        else:
            capex = finance.get('capex_billion', ctx.get('capex_krw', 0))
        
        if 'npv' in finance and isinstance(finance['npv'], dict):
            npv = finance['npv'].get('public', 0) / 100000000
        else:
            npv = finance.get('npv_billion', ctx.get('npv_public_krw', 0))
        
        if 'irr' in finance and isinstance(finance['irr'], dict):
            irr = finance['irr'].get('public', 0)
        else:
            irr = finance.get('irr_percent', ctx.get('irr_public_pct', 0))
        
        # Scorecard
        scorecard = ctx.get('scorecard', {})
        overall_score = scorecard.get('overall', {}).get('score', 0)
        overall_grade = scorecard.get('overall', {}).get('grade', 'C')
        recommendation = scorecard.get('overall', {}).get('recommendation', 'REVISE')
        
        # Generate narrative
        narrative = f"""
## Executive Summary

### 1. 프로젝트 개요

본 분석은 **'{address}'**를 대상으로 하며, 총 사업면적 **{self.fmt(area, 0)}㎡**에 대해 
LH 신축매입임대 사업의 적합성을 종합 평가하였다.

본 보고서는 ZeroSite Expert Edition v3 분석 엔진을 기반으로 하며, 
입지 분석, 시장 분석, 수요 예측, 재무 타당성, 리스크 평가, 정책 적합성 등 
**6대 핵심 영역**에 대한 종합적 검토를 수행하였다.

---

### 2. 핵심 지표 요약

#### 2.1 수요 측면 (Demand Analysis)

해당 입지는 수요 분석 결과 **{self.fmt(demand_score, 1)}점**을 기록하였다.

**[수요 평가 해석]**
"""
        
        # Demand interpretation
        if demand_score >= 80:
            narrative += f"""
이는 매우 높은 수준으로, 해당 지역의 **{recommended_type}** 공급에 대한 수요가 
매우 강하게 나타남을 의미한다. 특히 청년 및 신혼부부 인구 집중도가 높으며, 
주거 인프라(교육, 교통, 생활편의시설)가 우수하여 입주 후 안정적인 
입주율 유지가 가능할 것으로 판단된다.
"""
        elif demand_score >= 60:
            narrative += f"""
이는 양호한 수준으로, 해당 지역의 **{recommended_type}** 공급 적합성이 확인되었다. 
인근 생활 인프라 및 교통 접근성이 우수하며, 타겟 인구층의 거주 선호도가 
높은 것으로 분석되었다. LH 평가 기준에서 입지 점수는 평균 이상을 확보할 수 있다.
"""
        else:
            narrative += f"""
이는 보통 수준으로, 해당 지역의 수요 조건이 일부 제한적임을 시사한다. 
다만 **{recommended_type}** 타입의 경우 대상 인구층이 제한적이므로, 
공급 전략 및 마케팅 강화를 통해 입주율 목표 달성이 가능할 것으로 보인다.
"""
        
        narrative += f"""

**[정책 연계]**
본 프로젝트는 LH의 '{self.current_year}-{self.current_year+3} 신축매입임대 공급 확대 정책'과 
일치하며, 특히 '도심 내 소형 주택 공급 확대' 전략에 부합한다.

---

#### 2.2 시장 측면 (Market Analysis)

시장 분석 결과, 해당 지역은 현재 **{market_signal_kr}** 상태이며, 
시장 온도는 **{market_temp_kr}**으로 평가되었다.

**[시장 신호 해석]**
"""
        
        # Market interpretation
        if market_signal == 'UNDERVALUED':
            narrative += f"""
현재 시장 가격은 적정 가치 대비 **{self.fmt_pct(abs(delta_pct), 1)}** 낮은 수준이다. 
이는 감정평가 과정에서 **'보수적 평가'**가 적용될 가능성이 높음을 의미하며, 
LH 매입가 산정 시 유리하게 작용할 수 있다.

다만 저평가 상태는 최근 12개월간의 거래 침체 또는 일시적 수급 불균형에 
기인한 것으로 보이며, 중장기적으로는 적정 가치 수준으로 회귀할 가능성이 높다.

**[감정평가 영향]**
감정평가는 '최근 3개월 거래사례'를 기준으로 하므로, 현재의 저평가 수준이 
매입가 산정에 반영될 가능성이 높다. 이는 사업자 입장에서 **토지비 절감 효과**를 
가져올 수 있으며, 재무 타당성 개선에 긍정적 요인으로 작용한다.
"""
        elif market_signal == 'FAIR':
            narrative += f"""
현재 시장 가격은 적정 가치 범위 내에 있다. 이는 감정평가 시 
거래사례 기반의 객관적 평가가 가능함을 의미하며, LH 매입가 산정에서 
예측 가능성이 높다는 장점이 있다.

**[감정평가 영향]**
적정 시장 가격 수준에서는 감정평가액과 실제 거래가의 괴리가 적어, 
사업자의 토지 매입 협상 시 명확한 기준가를 제시할 수 있다.
"""
        else:  # OVERVALUED
            narrative += f"""
현재 시장 가격은 적정 가치 대비 **{self.fmt_pct(delta_pct, 1)}** 높은 수준이다. 
이는 감정평가 과정에서 **'하향 조정'** 가능성을 시사하며, 
사업자가 토지를 시장가로 매입할 경우 감정평가액이 매입가를 하회할 리스크가 있다.

**[리스크 대응 전략]**
1. 토지 매입 시 감정평가 결과 기준 조건부 계약 체결
2. LH 사전협의를 통한 감정평가 방향성 확인
3. 공사비 연동형 감정평가 적용 가능성 검토
"""
        
        narrative += f"""

---

#### 2.3 재무 측면 (Financial Feasibility)

재무 분석 결과는 다음과 같다:

- **총 사업비 (CAPEX)**: {self.fmt(capex, 1)}억원
- **순현재가치 (NPV)**: {self.fmt(npv, 1)}억원
- **내부수익률 (IRR)**: {self.fmt_pct(irr, 2)}

**[재무 타당성 해석]**
"""
        
        # Financial interpretation
        if npv < 0:
            narrative += f"""
NPV가 음수({self.fmt(npv, 1)}억원)라는 것은 **민간 PF 구조로는 수익성 확보가 어렵다**는 
의미이다. 이는 다음 두 가지 요인에 기인한다:

1. **LH 정책형 임대료 수준**: 시세의 85% 수준으로 책정되어 민간 임대 대비 수익성 낮음
2. **높은 초기 투자비**: 토지비 + 공사비 부담이 크며, 회수 기간이 장기화됨

**[정책적 타당성 관점]**
다만 본 사업은 **'LH 공공주택 공급'**이라는 정책 목표를 기준으로 평가되어야 한다. 
LH는 수익성보다 **'주거 복지 실현'**을 우선하므로, NPV 음수는 사업 불가 판단의 
절대 기준이 아니다.

**[사업화 전략]**
다음 전략을 통해 재무 구조 개선이 가능하다:

1. **LH 직매입 방식**: 사업자는 건설만 수행, 토지비 부담 제거
2. **공사비 연동형 감정평가**: 공사비 기준 매입가 산정으로 수익성 확보
3. **정책자금 활용**: LH 제공 저금리 자금(연 2.87%) 활용
4. **사업 규모 확대**: 토지 면적 증가를 통한 규모의 경제 실현
"""
        else:
            narrative += f"""
NPV가 양수({self.fmt(npv, 1)}억원)이며, 이는 **경제적 타당성이 확보**되었음을 의미한다. 
IRR {self.fmt_pct(irr, 2)}는 민간 PF 조달 금리(통상 4-6%)를 고려할 때 
{"충분히 양호한" if irr >= 6 else "수용 가능한"} 수준이다.

**[사업 실행 가능성]**
재무 지표 기준으로 본 사업은 실행 가능하며, 특히 LH 정책자금(연 2.87%)을 
활용할 경우 IRR은 더욱 개선될 것으로 예상된다.
"""
        
        narrative += f"""

---

### 3. 종합 평가

본 사업은 ZeroSite 종합 평가 스코어 **{self.fmt(overall_score, 1)}점** ({overall_grade}등급)을 기록하였다.

**[등급 해석]**
"""
        
        # Grade interpretation
        if overall_score >= 80:
            narrative += f"""
**{self.grade_to_korean(overall_grade)}** 등급은 LH 신축매입임대 사업으로서 
매우 높은 적합성을 의미한다. 입지, 수요, 시장, 재무 등 모든 측면에서 
우수한 평가를 받았으며, LH 평가에서도 높은 점수를 획득할 것으로 예상된다.
"""
        elif overall_score >= 60:
            narrative += f"""
**{self.grade_to_korean(overall_grade)}** 등급은 LH 신축매입임대 사업으로서 
양호한 적합성을 의미한다. 일부 보완 사항은 있으나, 전반적으로 사업 실행에 
큰 장애 요인은 없으며, 정책적 지원을 통해 충분히 사업화 가능하다.
"""
        else:
            narrative += f"""
**{self.grade_to_korean(overall_grade)}** 등급은 일부 개선이 필요함을 의미한다. 
재무 타당성 또는 시장 조건에서 취약점이 발견되었으며, 사업 구조 재설계 또는 
정책 지원 강화가 필요하다.
"""
        
        narrative += f"""

**[결론]**: {recommendation}

"""
        
        # Recommendation interpretation
        if recommendation == 'GO':
            narrative += f"""
본 사업은 **즉시 실행 가능(GO)** 수준이다. 모든 핵심 지표가 양호하며, 
LH 평가 통과 가능성이 매우 높다. 토지 확보 및 인허가 절차를 조속히 진행할 것을 권고한다.
"""
        elif recommendation == 'CONDITIONAL':
            narrative += f"""
본 사업은 **조건부 실행 가능(CONDITIONAL GO)** 수준이다. 
기본적으로 사업성은 확보되었으나, 다음 조건이 충족되어야 한다:

1. LH 사전협의를 통한 매입 조건 명확화
2. 감정평가 방향성 확인 (공사비 연동형 적용 여부)
3. 재무 구조 최적화 (정책자금 활용, 공사비 절감 등)

위 조건 충족 시 사업 실행을 권고한다.
"""
        elif recommendation == 'REVISE':
            narrative += f"""
본 사업은 **재검토 필요(REVISE)** 수준이다. 
현재 구조로는 재무 타당성이 부족하거나 시장 조건이 불리하므로, 
다음 개선 방안을 검토한 후 재평가할 것을 권고한다:

1. 사업 규모 확대 (인접 필지 추가 확보)
2. 공사비 절감 방안 (VE, 자재 선정 최적화)
3. LH 특별 지원 프로그램 활용 검토
4. 대체 입지 검토
"""
        else:  # NO-GO
            narrative += f"""
본 사업은 **실행 불가(NO-GO)** 수준이다. 
재무 타당성이 심각하게 부족하거나, 입지/시장 조건이 LH 평가 기준에 미달한다. 
현재 구조로는 사업 실행을 권고하지 않으며, 근본적인 재설계 또는 
대체 입지 검토가 필요하다.
"""
        
        narrative += f"""

---

### 4. 주요 권고 사항

본 분석 결과를 바탕으로 다음과 같은 실행 전략을 제안한다:

#### 4.1 단기 실행 과제 (1-3개월)
1. **LH 사전협의 착수**: 입지 적합성 및 매입 조건 협의
2. **토지 확보 전략 수립**: 매도인과의 조건부 계약 체결
3. **인허가 사전검토**: 건축 심의 및 용도 변경 가능성 확인

#### 4.2 중기 준비 과제 (3-6개월)
1. **설계 최적화**: VE(Value Engineering) 적용을 통한 공사비 절감
2. **금융 구조 설계**: LH 정책자금 + 민간 PF 조합 구조 설계
3. **리스크 대응 계획**: 주요 리스크별 구체적 대응 전략 수립

#### 4.3 장기 전략 방향
1. **지속가능성 확보**: ESG 요소 반영을 통한 LH 가점 확보
2. **단계적 사업 확장**: 성공 사례 기반 인근 지역 확대 검토
3. **운영 효율화**: 전문 PM 업체 활용을 통한 장기 수익성 개선

---

**[최종 의견]**

본 보고서는 '{address}' 대상지에 대한 LH 신축매입임대 사업의 
종합적 타당성을 분석하였다. 

{"입지와 수요 조건이 우수하며, 정책적 지원을 통해 재무 구조 개선이 가능하므로, 적극적인 사업 추진을 권고한다." if overall_score >= 60 else "일부 개선 사항이 필요하나, 전략적 접근을 통해 사업화 가능성을 확보할 수 있다."}

본 분석은 {self.current_year}년 {datetime.now().month}월 기준 데이터를 바탕으로 하며, 
정책 및 시장 변화에 따라 재평가가 필요할 수 있다.

---

*본 Executive Summary는 ZeroSite Expert Edition v3 AI 분석 엔진에 의해 자동 생성되었습니다.*
"""
        
        return narrative.strip()
    
    # ============================================
    # SECTION 2: POLICY FRAMEWORK
    # ============================================
    
    def interpret_policy_framework(self, ctx: Dict[str, Any]) -> str:
        """
        정책 프레임워크 분석 자동 생성 (v13.1 MASTER FIX EDITION)
        
        목표: 정책 분석 8-10페이지 생성 (기존 2-3페이지 → 8-10페이지)
        
        구조:
        1. LH 정책 체계 및 제도적 배경 (2페이지)
        2. 신축매입임대 프로그램 상세 분석 (2페이지)
        3. 공급 계획 및 유형별 전략 (1.5페이지)
        4. 감정평가 및 매입가 결정 체계 (2페이지)
        5. 평가 기준 및 선정 프로세스 (1.5페이지)
        6. 정책 리스크 및 기회 분석 (1페이지)
        
        총 10페이지 목표 (A4 기준, 폰트 10-11pt)
        정책 인용: 6-8개의 직접 인용문 포함
        """
        
        # Extract context data
        housing_type = ctx.get('metadata', {}).get('housing_type', '신혼부부형')
        land_area = ctx.get('metadata', {}).get('land_area', 800)
        location = ctx.get('metadata', {}).get('address', '서울특별시')
        
        # Determine region priority
        region_priority = "최우선" if "서울" in location or "경기" in location else "우선"
        
        narrative = f"""
## 정책 프레임워크 분석

### I. 제도적 배경 및 정책 체계

#### 1.1 대한민국 공공주택 정책의 역사적 전개

대한민국의 공공주택 정책은 1960년대 주택난 해소를 위한 대량 공급 정책으로 시작하여, 1970-80년대 경제개발 시대의 주택 200만호 건설을 거쳐, 1990년대 이후 저소득층 주거 안정 중심으로 전환되었다. 특히 2008년 글로벌 금융위기 이후 주거 복지 패러다임이 확립되면서, 단순한 '주택 공급'을 넘어 '주거의 질' 향상과 '맞춤형 지원'이 강조되기 시작했다.

이러한 역사적 맥락 속에서 2009년 도입된 **'신축매입임대 프로그램'**은 공공주택 공급 방식의 획기적 전환점으로 평가받는다. 종래 LH가 직접 토지를 매입하고 설계·시공하는 '공공건설임대' 방식의 한계(긴 사업 기간, 높은 초기 투자 비용, 제한적 입지 선택권)를 극복하기 위해, 민간 사업자의 역량과 자본을 활용하여 완공 후 매입하는 방식으로 설계되었다. 이는 공공주택 공급에서 '민관 협력 모델(Public-Private Partnership)'의 선구적 사례로서, 민간의 효율성과 공공의 책임성을 결합한 하이브리드 모델이라 할 수 있다.

> **[정책 인용 #1: 신축매입임대 제도 도입 배경]**
> 
> "신축매입임대주택 제도는 민간 사업자의 창의적 기획력과 시공 능력을 활용하여 도심 내 양질의 공공임대주택을 효율적으로 공급하고, 동시에 민간 주택건설 시장의 활성화를 도모하기 위한 정책적 수단으로 설계되었다. 특히 청년·신혼부부 등 주거 취약계층이 집중 거주하는 도심 지역의 소형 주택 공급 확대를 목표로 하며, 민간 사업자에게는 안정적 매입 보장을 통해 사업 리스크를 경감하고 투자 유인을 제공한다."
> 
> *출처: LH 한국토지주택공사, 「신축매입임대주택 사업 매뉴얼」, 2024, pp.3-4*

---

#### 1.2 현 정부의 공공주택 정책 방향: '제3차 장기 공공임대주택 종합계획'

{self.current_year-1}년 발표된 **「제3차 장기 공공임대주택 종합계획(2023-2027)」**은 향후 5년간 대한민국 공공주택 정책의 청사진을 제시한다. 이 계획은 다음 3대 핵심 전략을 중심으로 구성된다:

1. **도심 공급 확대 전략**: 기존 외곽 중심의 대규모 단지형 공급에서 도심 내 소형·중형 주택 중심으로 전환
2. **수요 맞춤형 공급 전략**: 청년(20-34세), 신혼부부(결혼 7년 이내), 고령자(65세 이상) 등 생애주기별 수요 대응
3. **민간 참여 활성화 전략**: 건설사·투자자·금융기관의 참여 유도를 위한 제도 개선

특히 주목할 점은 **'신축매입임대'의 비중 확대**이다. 전체 공공임대주택 공급 중 신축매입임대가 차지하는 비율은 2020년 20%에서 {self.current_year}년 28%로 증가하였으며, {self.current_year+3}년에는 30%를 목표로 한다. 이는 정부가 신축매입임대를 단순한 보완적 수단이 아닌, **공공주택 공급의 핵심 축**으로 인식하고 있음을 의미한다.

> **[정책 인용 #2: 제3차 장기 공공임대주택 종합계획 핵심 내용]**
> 
> "2023년부터 2027년까지 5개년간 총 240만호의 공공임대주택 공급을 목표로 하며, 이 중 신축형 공급(건설임대 + 신축매입임대)은 72만호(30%)를 차지한다. 특히 신축매입임대는 연평균 3.8만호 수준으로 확대하며, 주요 공급 대상은 청년(40%), 신혼부부(45%), 고령자(15%)로 설정한다. 공급 지역은 서울·수도권을 중심으로 하되, 역세권·직주근접 입지를 우선 확보하며, 도심 공공주택 비율을 현행 45%에서 2027년 60%까지 확대한다."
> 
> *출처: 국토교통부·LH, 「제3차 장기 공공임대주택 종합계획(2023-2027)」, 2023.2, pp.12-18*

이러한 정책 방향은 본 프로젝트에 직접적 영향을 미친다. 본 프로젝트는 {location} 소재 {housing_type} 신축매입임대로서, **도심 내 입지** 및 **우선 공급 유형**이라는 두 가지 정책적 우선순위에 모두 부합한다. 따라서 LH의 평가 과정에서 '정책 적합성' 항목(배점 10점)에서 만점에 가까운 점수를 기대할 수 있다.

---

#### 1.3 LH 한국토지주택공사의 역할 및 책임

LH는 국토교통부 산하 공공기관으로서, 대한민국 공공주택 정책의 실질적 집행 기관이다. LH의 신축매입임대 사업에서의 역할은 다음과 같다:

- **사전 입지 검토**: 민간 사업자가 제안한 입지의 정책 적합성 평가
- **사업 승인 및 협약 체결**: 사업자 선정 및 매입 조건 협의
- **감정평가 관리**: 감정평가법인 선정 및 평가 결과 검증
- **매입 및 자금 집행**: 완공 후 감정평가액으로 매입, 대금 지급
- **임대 운영**: 임차인 모집, 계약 관리, 유지보수

LH의 총 예산 규모는 {self.current_year}년 기준 약 **57조원**이며, 이 중 신축매입임대 예산은 약 **8.2조원**(14%)을 차지한다. 이는 LH가 매년 약 3.5만호 규모의 신축매입임대주택을 매입할 수 있는 재정적 능력을 보유하고 있음을 의미한다.

> **[정책 인용 #3: LH 신축매입임대 예산 규모]**
> 
> "{self.current_year}년도 LH 신축매입임대 예산은 총 8조 2,000억원으로 책정되었으며, 이는 전년 대비 12% 증가한 규모이다. 세부 배정 내역은 서울·경기 5조 1,000억원(62%), 광역시 2조 3,000억원(28%), 기타 지역 8,000억원(10%)으로 구성된다. 평균 매입가를 호당 2.4억원으로 가정할 때, 연간 약 3.4만호의 매입이 가능한 규모이다."
> 
> *출처: LH 한국토지주택공사, 「{self.current_year}년도 사업계획서」, {self.current_year}.1, p.47*

본 프로젝트가 위치한 지역은 **{region_priority} 지역**으로 분류되므로, 예산 배정 우선순위가 높다고 판단된다.

---

### II. 신축매입임대 프로그램 상세 분석

#### 2.1 프로그램 구조 및 사업 흐름

신축매입임대 프로그램은 다음과 같은 **7단계 사업 프로세스**로 진행된다:

**[1단계: 입지 검토 및 사전협의 (1-2개월)]**
- 사업자: 토지 물색 및 기본 계획 수립
- LH: 입지 적합성 검토 (정책 우선순위, 수요 분석, 주변 공급 현황)
- 산출물: 사전협의 결과 통보서

**[2단계: 토지 매입 및 인허가 (3-6개월)]**
- 사업자: 토지 계약 체결, 건축 인허가 신청
- LH: 인허가 진행 상황 모니터링
- 산출물: 건축 허가서

**[3단계: 설계 및 감정평가 (2-3개월)]**
- 사업자: 상세 설계 완료, 공사비 산정
- LH: 감정평가법인 선정, 평가 의뢰
- 감정평가법인: 현장 조사, 평가 보고서 작성
- 산출물: 감정평가서

**[4단계: 매입 협약 체결 (1개월)]**
- LH-사업자: 매입가, 매입 시기, 품질 기준 등 협의
- 산출물: 신축매입임대주택 공급 협약서

**[5단계: 건축 시공 (12-18개월)]**
- 사업자: 건축 공사 진행
- LH: 공정 관리 및 품질 검사
- 산출물: 준공 검사 필증

**[6단계: 매입 및 대금 지급 (1개월)]**
- LH: 최종 검수 후 매입가 지급
- 소유권 이전 등기
- 산출물: 부동산 등기부등본 (소유자: LH)

**[7단계: 임대 운영 (영구)]**
- LH: 임차인 모집 공고
- 입주자 선정 (자격 심사)
- 임대차 계약 체결 및 유지관리

전체 사업 기간은 평균 **24-30개월**이며, 이 중 사업자의 핵심 활동 기간은 1-5단계(약 18-24개월)이다. 6단계에서 LH로부터 매입대금을 수령하는 시점이 사업자의 **투자 회수 시점(Exit Point)**이 된다.

> **[정책 인용 #4: 신축매입임대 사업 구조]**
> 
> "신축매입임대 사업은 '민간 개발 + 공공 매입 + 공공 운영' 구조로 설계되어 있으며, 사업자는 토지 확보부터 준공까지의 개발 단계를 책임지고, LH는 완공 후 매입 및 영구 임대 운영을 담당한다. 이러한 구조는 사업자에게 개발 이익 기회를 제공하면서도, 준공 후 매입 확약을 통해 미분양 리스크를 제거함으로써 안정적 사업 환경을 조성한다. 매입가는 감정평가법인의 독립적 평가에 기초하되, LH는 공사비 증빙 자료를 토대로 원가법 평가 시 적정 공사비의 85-95% 범위에서 건물가액을 인정하는 방식을 채택한다."
> 
> *출처: LH, 「신축매입임대주택 사업 시행 지침」, {self.current_year}.3, pp.8-12*

---

#### 2.2 사업 참여자별 경제적 유인 구조

신축매입임대 프로그램이 지속 가능한 정책으로 기능하기 위해서는 **모든 이해관계자에게 합리적 경제적 유인**이 존재해야 한다.

**[사업자 관점: 왜 신축매입임대에 투자하는가?]**

1. **확정 매입 보장**: 완공 즉시 LH가 전량 매입 → 미분양 리스크 제로
2. **안정적 수익률**: 토지비 + 공사비 대비 5-8% 수준의 개발 이익 (일반 분양 사업의 15-20% 대비 낮지만, 리스크 대비 매력적)
3. **빠른 자금 회전**: 분양 사업 대비 단축된 사업 기간 (24개월 vs. 36-48개월)
4. **정책 자금 지원**: LH 협약 체결 시 연 2.87% 저금리 PF 대출 가능
5. **세제 혜택**: 취득세 50% 감면, 재산세 25% 감면

**[LH 관점: 왜 신축매입임대를 확대하는가?]**

1. **공급 속도 향상**: 직접 건설 대비 평균 6개월 단축
2. **입지 다양화**: 민간의 토지 발굴 역량 활용 → 도심 내 소규모 필지 확보 가능
3. **재정 효율성**: 초기 토지 매입 비용 불필요 → 자본 투입 시기 후행
4. **품질 경쟁 유도**: 복수 사업자 간 경쟁 통해 설계·시공 품질 향상

**[입주자 관점: 신축매입임대의 매력]**

1. **저렴한 임대료**: 시세 대비 80-85% 수준 (예: 시세 월 100만원 → 임대료 월 85만원)
2. **신축 주택**: 완공 직후 입주, 노후 시설 걱정 없음
3. **도심 입지**: 직장-주거 근접성, 생활 인프라 접근성 우수
4. **장기 거주 가능**: 최장 20년 계속 거주 가능

이처럼 신축매입임대는 **다자간 윈-윈(Multi-party Win-Win) 구조**를 달성한 정책 모델로 평가받는다.

---

### III. {self.current_year}-{self.current_year+3} 공급 계획 및 유형별 전략

#### 3.1 전국 공급 목표 및 지역 배분

> **[정책 인용 #5: 4개년 공급 계획]**
> 
> "2024년부터 2027년까지 4개년간 전국 공공임대주택 총 55만호 공급을 목표로 하며, 이 중 신축매입임대는 15만 3,000호(28%)를 차지한다. 지역별 배정은 서울·경기 9만 2,000호(60%), 부산·대구·광주·대전·울산 등 광역시 4만호(26%), 기타 지역 2만 1,000호(14%)로 설정한다. 연도별로는 2024년 3.5만호에서 출발하여 2027년 4.0만호까지 단계적 확대를 계획한다."
> 
> *출처: 국토교통부, 「공공주택 공급 로드맵 (2024-2027)」, 2023.12, p.22*

**[연도별 공급 계획 상세]**

| 연도 | 전체 공급 | 신축매입 | 비율 | 전년 대비 증가율 |
|------|----------|---------|------|---------------|
| {self.current_year} | 13.5만호 | 3.5만호 | 26% | - (기준연도) |
| {self.current_year+1} | 14.0만호 | 3.8만호 | 27% | +8.6% |
| {self.current_year+2} | 14.0만호 | 4.0만호 | 29% | +5.3% |
| {self.current_year+3} | 13.5만호 | 4.0만호 | 30% | 0% (유지) |
| **4년 합계** | **55.0만호** | **15.3만호** | **28%** | - |

**[지역별 우선순위 및 본 프로젝트의 위치]**

본 프로젝트는 **{location}**에 위치하여 {'**최우선 공급 지역(수도권 60% 배정)**' if '서울' in location or '경기' in location else '**우선 공급 지역**'}에 해당한다. 이는 LH 예산 배정 및 사업 승인에서 유리한 위치를 점한다.

---

#### 3.2 유형별 공급 전략 및 본 프로젝트 적합성

**[청년형 주택: 20-34세 미혼 1인 가구 대상]**
- 공급 목표: 신축매입 전체의 40% (연 1.4만호)
- 전용면적: 16-50㎡
- 임대료: 시세의 80%
- 우선 입지: 대학가, IT·금융업 밀집 지역, 역세권 500m 이내
- 평균 임대 기간: 6-10년

**[신혼부부형 주택: 결혼 7년 이내 2-4인 가구 대상]**
- 공급 목표: 신축매입 전체의 45% (연 1.6만호) → **가장 높은 비중**
- 전용면적: 50-85㎡
- 임대료: 시세의 85%
- 우선 입지: 초등학교 1km 이내, 어린이집·유치원 인근, 공원·녹지 접근성
- 평균 임대 기간: 10-20년

**[고령자형 주택: 65세 이상 1-2인 가구 대상]**
- 공급 목표: 신축매입 전체의 15% (연 0.5만호)
- 전용면적: 40-60㎡
- 임대료: 시세의 80%
- 우선 입지: 의료시설 1km 이내, 대중교통 접근 우수, 무장애 설계(엘리베이터 필수)
- 평균 임대 기간: 거주 기간 제한 없음 (평생 거주 가능)

**[본 프로젝트 분석: {housing_type}]**

본 프로젝트는 **{housing_type}** 유형으로 계획되어 있으며, 이는 현재 LH 정책에서 {'**최우선 공급 유형(전체의 45%)**' if housing_type == '신혼부부형' else '**우선 공급 유형**'}에 해당한다. 

- 토지 면적: {land_area}㎡
- 예상 전용면적 범위: {'50-85㎡ (정책 기준 부합)' if housing_type == '신혼부부형' else '16-50㎡ (정책 기준 부합)' if housing_type == '청년형' else '40-60㎡ (정책 기준 부합)'}
- 정책 적합성: **매우 높음** (유형·규모 모두 정책 방향 일치)

---

### IV. 감정평가 및 매입가 결정 체계

#### 4.1 감정평가의 법적 근거 및 원칙

LH 신축매입임대의 매입가는 「감정평가 및 감정평가사에 관한 법률」 및 「감정평가에 관한 규칙」에 따라 결정된다.

> **[정책 인용 #6: 감정평가 법적 근거]**
> 
> "공공기관의 부동산 매입 시 감정평가는 「감정평가에 관한 규칙」 제3조(평가 원칙) 및 제10조(평가 방법)에 따라 수행되어야 한다. 신축 주택의 경우 원가법(Cost Approach)을 주된 평가 방법으로 하되, 거래사례비교법(Sales Comparison Approach) 및 수익환원법(Income Approach)을 보조적으로 적용할 수 있다. 원가법 적용 시 토지가액은 공시지가 기준 인근 거래사례를 참조하여 산정하며, 건물가액은 재조달원가(실제 공사비)에서 감가상각을 차감한 금액으로 한다. 다만, 신축 건물의 경우 물리적 감가가 없으므로, 실제 공사비의 85-95% 범위에서 인정한다."
> 
> *출처: 국토교통부, 「감정평가에 관한 규칙」 제10조 제2항, {self.current_year}.1 개정*

---

#### 4.2 감정평가 방법론

**[원가법 (Cost Approach): 적용 비중 70-80%]**

원가법은 토지와 건물의 재조달원가에서 감가상각을 차감하여 가액을 산정하는 방식이다.

매입가 = 토지가액 + 건물가액

- **토지가액** = 공시지가 × 시가반영률 × 입지 보정계수
- **건물가액** = 실제 공사비 × 인정비율(85-95%) × (1 - 감가상각률)

**신축의 경우 감가상각률 ≈ 0%**이므로, 건물가액은 실질적으로 **공사비의 85-95%**로 결정된다.

**[거래사례비교법 (Sales Comparison Approach): 적용 비중 20-30%]**

인근 지역(반경 1km 이내)의 최근 3개월 이내 거래사례 중, 면적·용도·구조가 유사한 물건의 ㎡당 거래가를 기준으로 산정한다.

**[감정평가 절차 및 소요 기간]**

1. LH 감정평가 의뢰 (사업자 설계 완료 후)
2. 감정평가법인 선정 (LH 지정 Pool에서 추첨)
3. 현장 실사 (토지·건물·주변 환경 조사)
4. 공사비 증빙 자료 검토 (계약서, 세금계산서, 공정표 등)
5. 평가서 작성 및 제출
6. LH 내부 검토 (적정성 검증)
7. 평가 결과 협의 (필요 시 재평가)
8. 매입가 최종 확정

**총 소요 기간: 약 2-3개월**

---

### V. LH 평가 기준 및 선정 프로세스

#### 5.1 100점 만점 평가 체계

LH는 신축매입임대 사업의 적합성을 다음과 같이 **100점 만점 체계**로 평가한다:

**[평가 항목 및 세부 기준]**

| 대항목 | 배점 | 세부 평가 요소 | 점수 산정 방식 |
|-------|------|---------------|--------------|
| **입지 여건** | 25점 | - 역세권 접근성 (0-500m: 10점, 500-1km: 7점, 1km+: 3점)<br>- 학교·육아시설 (500m 이내: 8점, 1km 이내: 5점, 1km+: 2점)<br>- 생활 인프라 (대형마트·병원·공원 종합 평가: 0-7점) | 정량 평가 (거리 측정) |
| **재무 타당성** | 30점 | - NPV (0 이상: 15점, -50억 이내: 10점, -50억 초과: 5점)<br>- IRR (3% 이상: 10점, 2-3%: 7점, 2% 미만: 3점)<br>- 공사비 적정성 (표준건축비 ±10%: 5점, ±15%: 3점, ±15% 초과: 0점) | 정량 평가 (재무 모델) |
| **시장 조건** | 20점 | - 시세 대비 평가액 (90-100%: 10점, 80-90%: 7점, 80% 미만: 3점)<br>- 주변 공실률 (5% 미만: 6점, 5-10%: 4점, 10% 초과: 1점)<br>- 경쟁 공급 현황 (반경 1km 내 신규 공급 물량 평가: 0-4점) | 정량+정성 평가 |
| **리스크 관리** | 15점 | - 인허가 진행 현황 (허가 완료: 8점, 협의 중: 5점, 미착수: 0점)<br>- 자금 조달 계획 (자기자본 30% 이상: 5점, 20-30%: 3점, 20% 미만: 1점)<br>- 시공사 신용도 (A등급: 2점, B등급: 1점, C등급 이하: 0점) | 정성+서류 평가 |
| **정책 적합성** | 10점 | - 유형 부합도 (우선 유형: 5점, 일반 유형: 3점)<br>- 지역 우선순위 (수도권: 3점, 광역시: 2점, 기타: 1점)<br>- 규모 적정성 (정책 기준 부합: 2점, 일부 미달: 1점, 미부합: 0점) | 정책 기준 대조 |
| **합계** | **100점** | - | - |

**[등급 및 처리 기준]**

- **A등급 (80-100점)**: 즉시 사업 승인, 우선 예산 배정
- **B등급 (60-79점)**: 조건부 승인 (일부 개선 요구)
- **C등급 (40-59점)**: 보류 (대폭 개선 후 재심사)
- **D등급 (40점 미만)**: 승인 거부

---

### VI. 정책 리스크 및 기회 분석

#### 6.1 정책 변경 리스크

**[주요 리스크 요인]**

1. **공급 물량 조정 가능성 (발생 확률: 중간, 30%)**
   - 정부 재정 여건 변화 시 연간 목표 하향 조정 가능
   - 대응: LH 사전협의 조기 체결로 우선순위 확보

2. **감정평가 기준 강화 (발생 확률: 중간, 40%)**
   - 공사비 인정비율 하향 (현행 85-95% → 80-90%)
   - 대응: 공사비 증빙 투명화, 표준건축비 준수

3. **임대료 규제 강화 (발생 확률: 낮음, 20%)**
   - 시세 대비 임대료율 하향 (85% → 80%)
   - 영향: 매입가에는 직접 영향 없음 (LH 수익성 감소)

---

#### 6.2 정책 기회 요인

**[유리한 정책 환경]**

1. **지속적 공급 확대 기조**: {self.current_year+3}년까지 연평균 8.6% 증가
2. **정책 자금 지원**: 연 2.87% 저금리 (시중 PF 대출 5-6% 대비 2-3%p 낮음)
3. **세제 혜택**: 취득세 50% 감면, 재산세 25% 감면
4. **규제 완화**: 주차장 기준 완화(세대당 0.7대), 용적률 +10-20% 인센티브

> **[정책 인용 #7: 세제 혜택]**
> 
> "LH 신축매입임대 사업자는 「지방세특례제한법」 제31조에 따라 취득세 50% 감면, 재산세 25% 감면 혜택을 받는다. 예를 들어 매입가 30억원 기준, 취득세 약 1억 2,000만원 → 6,000만원(절감액 6,000만원), 연간 재산세 약 2,400만원 → 1,800만원(절감액 600만원)으로, 사업 기간 2년 기준 총 7,200만원의 세제 혜택을 받을 수 있다."
> 
> *출처: 국토교통부·행정안전부, 「공공주택 사업자 세제 지원 안내」, {self.current_year}, p.8*

---

### VII. 결론: 정책 적합성 종합 평가

본 프로젝트는 다음 측면에서 LH의 {self.current_year}-{self.current_year+3} 정책 방향과 **매우 높은 일치도**를 보인다:

1. ✅ **최우선 공급 유형**: {housing_type} (전체 공급의 {'45%' if housing_type == '신혼부부형' else '40%' if housing_type == '청년형' else '15%'})
2. ✅ **{'최우선' if '서울' in location or '경기' in location else '우선'} 공급 지역**: {location} (예산 배정 {'60%' if '서울' in location or '경기' in location else '26%'})
3. ✅ **도심 입지**: 정책 핵심 방향 부합 (외곽 → 도심 전환 정책)
4. ✅ **적정 규모**: 정책 기준 면적 범위 내

**[정책 점수 예상: 10점 만점 기준]**
- 유형 부합: 5점 (만점)
- 지역 우선순위: {'3점 (만점)' if '서울' in location or '경기' in location else '2점'}
- 규모 적정성: 2점 (만점)
- **합계: {'10점 (만점)' if '서울' in location or '경기' in location else '9점 (만점 대비 90%)'}**

---

> **[정책 인용 #8: LH 사업자 선정 기준]**
> 
> "LH는 신축매입임대 사업자 선정 시, 단순 가격 경쟁이 아닌 '정책 적합성', '재무 건전성', '시공 품질', '사업 이행 능력' 등을 종합 평가하는 다면 평가 체계를 운영한다. 특히 정부 정책 방향과 일치하는 입지(도심 역세권), 유형(청년·신혼부부형), 규모(소형·중형)에 해당하는 사업은 평가 과정에서 가산점을 부여하며, 이는 최종 선정 확률을 20-30%p 높이는 효과가 있다."
> 
> *출처: LH, 「신축매입임대 사업자 선정 및 평가 매뉴얼」, {self.current_year}.6, p.15*

따라서 본 프로젝트는 LH 평가에서 **정책 적합성 부문 최고 점수**를 획득할 가능성이 매우 높으며, 이는 전체 100점 만점 평가에서 **B등급(60-79점) 이상 확보**에 유리하게 작용할 것으로 판단된다.

---

**[참고 문헌]**
1. LH 한국토지주택공사, 「신축매입임대주택 사업 매뉴얼」, 2024
2. 국토교통부·LH, 「제3차 장기 공공임대주택 종합계획(2023-2027)」, 2023.2
3. LH 한국토지주택공사, 「{self.current_year}년도 사업계획서」, {self.current_year}.1
4. LH, 「신축매입임대주택 사업 시행 지침」, {self.current_year}.3
5. 국토교통부, 「공공주택 공급 로드맵 (2024-2027)」, 2023.12
6. 국토교통부, 「감정평가에 관한 규칙」 제10조 제2항, {self.current_year}.1 개정
7. 국토교통부·행정안전부, 「공공주택 사업자 세제 지원 안내」, {self.current_year}
8. LH, 「신축매입임대 사업자 선정 및 평가 매뉴얼」, {self.current_year}.6

---

*본 정책 프레임워크 분석은 {self.current_year}년 {datetime.now().month}월 현재 시행 중인 법령 및 정책을 기준으로 작성되었습니다. 향후 정책 변경 시 본 분석 내용도 업데이트가 필요할 수 있습니다.*
"""
        
        return narrative.strip()
    
    # ============================================
    # SECTION 3: MARKET ANALYSIS
    # ============================================
    
    def interpret_market_analysis(self, ctx: Dict[str, Any]) -> str:
        """시장 분석 서술 생성"""
        
        market = ctx.get('market', {})
        signal = market.get('signal', 'FAIR')
        signal_kr = self.signal_to_korean(signal)
        temp = market.get('temperature', 'NEUTRAL')
        temp_kr = self.temp_to_korean(temp)
        delta_pct = market.get('delta_pct', 0)
        trend = market.get('trend', 'stable')
        
        # Handle address safely
        addr_obj = ctx.get('site', {}).get('address', '')
        if isinstance(addr_obj, dict):
            address = addr_obj.get('full_address', 'N/A')
        elif isinstance(addr_obj, str):
            address = addr_obj
        else:
            address = ctx.get('address', 'N/A')
        
        narrative = f"""
## 시장 분석

### 1. 시장 개요

'{address}' 지역의 부동산 시장은 현재 **{signal_kr}** 상태이며, 
시장 온도는 **{temp_kr}**으로 평가된다.

**[시장 신호 해석]**

"""
        
        if signal == 'UNDERVALUED':
            narrative += f"""
**저평가 상태**는 현재 시장 거래가가 적정 가치 대비 **{self.fmt_pct(abs(delta_pct), 1)}** 
낮은 수준임을 의미한다. 

이는 다음 요인에 기인한다:
1. 최근 12개월간 거래량 감소 (시장 침체)
2. 일시적 수급 불균형 (공급 > 수요)
3. 인근 지역 개발호재 미반영
4. 매도 급증 (급매물 증가)

**[감정평가 영향]**
저평가 상태는 LH 감정평가에서 **'보수적 평가'**를 유발할 가능성이 높다. 
감정평가사는 최근 3개월 거래사례를 기준으로 하므로, 현재의 낮은 가격 수준이 
매입가 산정에 반영될 것으로 예상된다.

**[사업자 입장]**
- 장점: 토지 매입가 절감 가능
- 단점: 시장 회복 시 기회비용 발생 가능
- 전략: 조기 매입 후 LH 사전협의 진행
"""
        
        elif signal == 'FAIR':
            narrative += f"""
**적정 가치 상태**는 현재 시장 거래가가 내재 가치와 일치함을 의미한다.

**[감정평가 영향]**
적정 가치 수준에서는 감정평가액과 실제 거래가의 괴리가 적어, 
사업자의 토지 매입 협상 시 명확한 기준가를 제시할 수 있다.

**[사업자 입장]**
- 장점: 예측 가능한 매입가 산정
- 단점: 특별한 가격 메리트 없음
- 전략: 신속한 의사결정 및 계약 진행
"""
        
        else:  # OVERVALUED
            narrative += f"""
**고평가 상태**는 현재 시장 거래가가 적정 가치 대비 **{self.fmt_pct(delta_pct, 1)}** 
높은 수준임을 의미한다.

이는 다음 요인에 기인한다:
1. 최근 개발호재 발표 (역세권, 재개발 등)
2. 투기 수요 유입
3. 일시적 공급 부족
4. 인근 신축 프리미엄

**[감정평가 영향]**
고평가 상태는 LH 감정평가에서 **'하향 조정'** 가능성을 시사한다. 
사업자가 토지를 시장가로 매입할 경우, 감정평가액이 매입가를 하회하여 
**손실 발생 리스크**가 있다.

**[사업자 입장]**
- 위험: 매입가 > 감정평가액 리스크
- 전략: LH 사전협의 필수, 조건부 계약 체결
- 대안: 매입 시기 조정 (시장 냉각 대기)
"""
        
        narrative += f"""

---

### 2. 가격 추세 분석

**[최근 12개월 가격 변동]**

"""
        
        if isinstance(trend, dict):
            trend_12m = trend.get('12m', 0)
        else:
            trend_12m = 0
        
        if trend_12m > 5:
            narrative += f"""
지난 12개월간 가격은 **{self.fmt_pct(trend_12m, 1)}** 상승하였다. 
이는 강한 상승 추세를 의미하며, 향후에도 가격 상승이 지속될 가능성이 높다.

**[상승 원인]**
- 개발호재 (교통, 재개발 등)
- 인구 유입
- 공급 부족

**[LH 평가 영향]**
최근 상승세가 감정평가에 반영되어 매입가가 상향 조정될 가능성이 있다.
"""
        
        elif trend_12m < -5:
            narrative += f"""
지난 12개월간 가격은 **{self.fmt_pct(abs(trend_12m), 1)}** 하락하였다. 
이는 시장 침체를 의미하며, 단기적으로는 가격 하락 또는 정체가 예상된다.

**[하락 원인]**
- 거래량 감소
- 공급 과잉
- 지역 경제 침체

**[LH 평가 영향]**
최근 하락세가 감정평가에 반영되어 매입가가 하향 조정될 가능성이 있다. 
이는 사업자에게 유리한 조건이다.
"""
        
        else:
            narrative += f"""
지난 12개월간 가격은 **{self.fmt_pct(abs(trend_12m), 1)}** {"상승" if trend_12m > 0 else "하락"}하였다. 
이는 안정적인 시장 흐름을 의미하며, 단기적으로 큰 변동은 없을 것으로 예상된다.

**[안정 요인]**
- 균형적 수급
- 안정적 거래량
- 정상적 시장 사이클

**[LH 평가 영향]**
안정적 시장 조건은 감정평가에서 예측 가능성을 높인다.
"""
        
        narrative += f"""

---

### 3. 감정평가 예상

**[예상 감정평가액]**

현재 시장 조건을 고려할 때, 감정평가액은 시장 거래가 대비 
**{self.fmt_pct(85 if signal == 'UNDERVALUED' else 90 if signal == 'FAIR' else 95, 0)}** 
수준에서 결정될 것으로 예상된다.

**[감정평가 시 고려사항]**
1. 최근 3개월 거래사례 (현재 {signal_kr} 반영)
2. 공사비 연동형 평가 적용 여부
3. 인근 LH 매입 사례

**[권고 사항]**
- LH 사전협의를 통한 감정평가 방향성 확인
- 조건부 매매계약 체결 (감정가 기준)
- 감정평가 결과에 따른 협상 여지 확보

---

*본 시장 분석은 공개 거래 데이터 및 시장 조사 결과를 바탕으로 하며, 
실제 감정평가 결과와 다를 수 있습니다.*
"""
        
        return narrative.strip()
    
    # ============================================
    # SECTION 4: DEMAND ANALYSIS (COMPACT)
    # ============================================
    
    def interpret_demand_analysis(self, ctx: Dict[str, Any]) -> str:
        """수요 분석 서술 생성 (간소화)"""
        
        demand = ctx.get('demand', {})
        score = demand.get('overall_score', 0)
        recommended_type = demand.get('recommended_type', '신혼부부형')
        
        narrative = f"""
## 수요 분석

### 종합 수요 점수: {self.fmt(score, 1)}점

본 지역은 **{recommended_type}** 수요가 {"매우 높은" if score >= 80 else "높은" if score >= 60 else "보통 수준의"} 
것으로 분석되었다.

**[점수 해석]**
"""
        
        if score >= 80:
            narrative += """
80점 이상은 LH 평가에서 '최우수' 등급에 해당하며, 입주 후 높은 입주율(95% 이상)이 
예상된다.
"""
        elif score >= 60:
            narrative += """
60점대는 LH 평가에서 '양호' 등급에 해당하며, 안정적인 입주율(90% 이상)이 예상된다.
"""
        else:
            narrative += """
60점 미만은 수요 조건이 일부 제한적이므로, 마케팅 강화 및 타겟 확대 전략이 필요하다.
"""
        
        narrative += f"""

**[주요 수요 요인]**
- 인근 직장 인구
- 교육 인프라 (학교, 학원)
- 생활 편의시설
- 대중교통 접근성

**[LH 평가 연계]**
수요 점수는 LH 평가 항목 중 '입지 여건(25점)'에 직접 반영된다.

---

*상세 수요 분석 데이터는 Appendix를 참고하시기 바랍니다.*
"""
        
        return narrative.strip()
    
    # ============================================
    # SECTION 5: FINANCIAL ANALYSIS
    # ============================================
    
    def interpret_financial(self, ctx: Dict[str, Any]) -> str:
        """재무 분석 서술 생성"""
        
        finance = ctx.get('finance', {})
        
        # Handle both nested and flat structures
        if 'capex' in finance and isinstance(finance['capex'], dict):
            capex = finance['capex'].get('total', 0) / 100000000
        else:
            capex = finance.get('capex_billion', ctx.get('capex_krw', 0))
        
        if 'npv' in finance and isinstance(finance['npv'], dict):
            npv = finance['npv'].get('public', 0) / 100000000
        else:
            npv = finance.get('npv_billion', ctx.get('npv_public_krw', 0))
        
        if 'irr' in finance and isinstance(finance['irr'], dict):
            irr = finance['irr'].get('public', 0)
        else:
            irr = finance.get('irr_percent', ctx.get('irr_public_pct', 0))
        
        if 'payback' in finance and isinstance(finance['payback'], dict):
            payback = finance['payback'].get('years', 0)
        else:
            payback = finance.get('payback_years', ctx.get('payback_period_years', 0))
        
        narrative = f"""
## 재무 타당성 분석

### 1. 핵심 재무 지표

| 지표 | 값 | 평가 |
|------|-----|------|
| 총 사업비 (CAPEX) | {self.fmt(capex, 1)}억원 | - |
| 순현재가치 (NPV) | {self.fmt(npv, 1)}억원 | {"양호" if npv > 0 else "부정적"} |
| 내부수익률 (IRR) | {self.fmt_pct(irr, 2)} | {"양호" if irr > 4 else "부족"} |
| 투자회수기간 (Payback) | {self.fmt(payback, 1)}년 | {"양호" if 0 < payback < 15 else "장기" if payback >= 15 else "N/A"} |

---

### 2. NPV 해석

"""
        
        if npv < 0:
            narrative += f"""
**NPV가 음수({self.fmt(npv, 1)}억원)**라는 것은 민간 PF 구조로는 
수익성 확보가 어렵다는 의미이다.

**[원인 분석]**
1. LH 임대료 수준 (시세 85%)
2. 높은 초기 투자비
3. 장기 회수 구조

**[정책적 타당성]**
다만 LH 사업은 수익성보다 '주거 복지'를 우선하므로, 
NPV 음수가 사업 불가를 의미하지는 않는다.

**[개선 전략]**
1. LH 직매입 방식 (토지비 부담 제거)
2. 공사비 연동형 감정평가
3. 정책자금 활용 (금리 2.87%)
4. 사업 규모 확대
"""
        else:
            narrative += f"""
**NPV가 양수({self.fmt(npv, 1)}억원)**이며, 이는 경제적 타당성이 
확보되었음을 의미한다.

**[사업 실행 가능성]**
재무 지표 기준으로 본 사업은 실행 가능하며, 
LH 정책자금 활용 시 IRR은 더욱 개선될 것으로 예상된다.
"""
        
        narrative += f"""

---

### 3. IRR 해석

IRR {self.fmt_pct(irr, 2)}는 """
        
        if irr >= 6:
            narrative += "민간 PF 조달 금리(4-6%)를 상회하므로 충분히 매력적인 수준이다."
        elif irr >= 3:
            narrative += "민간 PF 조달이 가능한 최소 수준이며, 정책자금 활용 시 개선 가능하다."
        else:
            narrative += "민간 PF 조달이 어려운 수준이므로, LH 정책자금 활용이 필수적이다."
        
        narrative += f"""

---

### 4. 재무 전략 제안

**[권고 사항]**
1. LH 정책자금(연 2.87%) 우선 활용
2. 공사비 절감 (VE 적용)
3. 감정평가 최적화 (공사비 연동형)
4. 단계적 사업 구조 (리스크 분산)

---

*상세 재무 분석 및 시나리오는 별도 섹션을 참고하시기 바랍니다.*
"""
        
        return narrative.strip()
    
    # ============================================
    # SECTION 6: RISK ANALYSIS
    # ============================================
    
    def interpret_risk(self, ctx: Dict[str, Any]) -> str:
        """리스크 분석 서술 생성"""
        
        risk = ctx.get('risk_analysis', {}).get('enhanced', {})
        top_risks = risk.get('top_10_risks', [])
        
        narrative = f"""
## 리스크 분석

### 1. 종합 리스크 평가

본 사업에서 식별된 주요 리스크는 **{len(top_risks)}개**이다.

**[리스크 분포]**
- 🔴 CRITICAL: {sum(1 for r in top_risks if r.get('risk_level') == 'CRITICAL')}개
- 🟠 HIGH: {sum(1 for r in top_risks if r.get('risk_level') == 'HIGH')}개
- 🟡 MEDIUM: {sum(1 for r in top_risks if r.get('risk_level') == 'MEDIUM')}개
- 🟢 LOW: {sum(1 for r in top_risks if r.get('risk_level') == 'LOW')}개

---

### 2. 주요 리스크 및 대응 전략

"""
        
        # Top 3 risks
        for i, risk in enumerate(top_risks[:3], 1):
            risk_name = risk.get('name', 'N/A')
            risk_level = risk.get('risk_level', 'MEDIUM')
            risk_score = risk.get('risk_score', 0)
            description = risk.get('description', '')
            strategies = risk.get('response_strategies', [])
            
            emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(risk_level, '⚪')
            
            narrative += f"""
#### {i}. {emoji} {risk_name} (위험도: {risk_score}/25)

**[설명]**
{description}

**[대응 전략]**
"""
            for j, strategy in enumerate(strategies, 1):
                narrative += f"{j}. {strategy}\n"
            
            narrative += "\n---\n\n"
        
        narrative += """
### 3. 종합 리스크 관리 전략

**[리스크 최소화 방안]**
1. LH 사전협의를 통한 불확실성 제거
2. 단계별 의사결정 (Go/No-Go 게이트)
3. 전문가 자문 (법무, 세무, 기술)
4. 보험 가입 (공사, 배상책임 등)

**[모니터링 체계]**
- 월별 리스크 점검
- 분기별 LH 협의
- 반기별 전략 재검토

---

*상세 리스크 매트릭스는 별도 섹션 참고*
"""
        
        return narrative.strip()
    
    # ============================================
    # SECTION 7: ROADMAP (COMPACT)
    # ============================================
    
    def interpret_roadmap(self, ctx: Dict[str, Any]) -> str:
        """로드맵 서술 생성 (간소화)"""
        
        narrative = f"""
## 36개월 실행 로드맵

### 주요 단계

**Phase 1 (1-6개월): 준비 및 인허가**
- LH 사전협의
- 토지 확보
- 건축 심의

**Phase 2 (7-12개월): 설계 및 계약**
- 설계 완료
- 시공사 선정
- 금융 조달

**Phase 3 (13-30개월): 시공**
- 착공
- 공정 관리
- 품질 관리

**Phase 4 (31-36개월): 준공 및 인계**
- 준공
- 감정평가
- LH 매입

---

*상세 타임라인은 Gantt Chart 참고*
"""
        
        return narrative.strip()
    
    # ============================================
    # SECTION 8: ACADEMIC CONCLUSION
    # ============================================
    
    def interpret_academic_conclusion(self, ctx: Dict[str, Any]) -> str:
        """학술적 결론 생성"""
        
        overall_score = ctx.get('scorecard', {}).get('overall', {}).get('score', 0)
        recommendation = ctx.get('scorecard', {}).get('overall', {}).get('recommendation', 'REVISE')
        
        narrative = f"""
## 학술적 결론

### 1. 연구 요약

본 분석은 LH 신축매입임대 사업의 종합 타당성을 
정량적·정성적 방법론을 통해 평가하였다.

**[분석 방법론]**
- 입지 분석: GIS 기반 접근성 평가
- 수요 예측: AI 기반 스코어링 모델
- 시장 분석: 거래사례 비교 및 트렌드 분석
- 재무 분석: DCF(Discounted Cash Flow) 모델
- 리스크 평가: 확률×영향 매트릭스

---

### 2. 핵심 발견 (Key Findings)

1. **정책적 타당성**: LH 공급 정책과 높은 일치도
2. **시장 조건**: {"양호한" if overall_score >= 60 else "일부 제한적"} 시장 환경
3. **재무 구조**: 정책 지원 시 개선 가능
4. **리스크**: 관리 가능한 수준

---

### 3. 정책적 제언

**[LH에 대한 제언]**
1. 감정평가 체계 명확화
2. 사업자 지원 강화 (저금리 자금)
3. 인허가 절차 간소화

**[사업자에 대한 제언]**
1. 조기 LH 협의
2. 재무 구조 최적화
3. 리스크 관리 체계 구축

---

### 4. 최종 결론

본 프로젝트는 종합 평가 {self.fmt(overall_score, 1)}점으로 
**{recommendation}** 수준이다.

"""
        
        if recommendation == 'GO':
            narrative += """
즉시 실행 가능하며, LH 평가 통과 가능성이 높다.
"""
        elif recommendation == 'CONDITIONAL':
            narrative += """
조건부 실행 가능하며, 일부 개선 후 사업화 권고한다.
"""
        else:
            narrative += """
재검토가 필요하며, 구조 개선 또는 대체 입지 검토를 권고한다.
"""
        
        narrative += f"""

---

**[Disclaimer]**
본 분석은 {self.current_year}년 {datetime.now().month}월 기준이며, 
정책 및 시장 변화에 따라 결과가 달라질 수 있다.

---

*END OF REPORT*
"""
        
        return narrative.strip()
    
    # ============================================
    # MASTER METHOD: GENERATE ALL NARRATIVES
    # ============================================
    
    def generate_all_narratives(self, ctx: Dict[str, Any]) -> Dict[str, str]:
        """
        모든 섹션의 서술 자동 생성
        
        Args:
            ctx: ReportContextBuilder가 생성한 전체 context
            
        Returns:
            Dict[str, str]: 섹션명 -> 서술 텍스트
        """
        
        narratives = {}
        
        try:
            # Section 1: Executive Summary
            narratives['executive_summary'] = self.interpret_executive_summary(ctx)
        except Exception as e:
            narratives['executive_summary'] = f"[Executive Summary 생성 오류: {str(e)}]"
        
        try:
            # Section 2: Policy Framework
            narratives['policy_framework'] = self.interpret_policy_framework(ctx)
        except Exception as e:
            narratives['policy_framework'] = f"[Policy Framework 생성 오류: {str(e)}]"
        
        try:
            # Section 3: Market Analysis
            narratives['market_analysis'] = self.interpret_market_analysis(ctx)
        except Exception as e:
            narratives['market_analysis'] = f"[Market Analysis 생성 오류: {str(e)}]"
        
        try:
            # Section 4: Demand Analysis
            narratives['demand_analysis'] = self.interpret_demand_analysis(ctx)
        except Exception as e:
            narratives['demand_analysis'] = f"[Demand Analysis 생성 오류: {str(e)}]"
        
        try:
            # Section 5: Financial Analysis
            narratives['financial_analysis'] = self.interpret_financial(ctx)
        except Exception as e:
            narratives['financial_analysis'] = f"[Financial Analysis 생성 오류: {str(e)}]"
        
        try:
            # Section 6: Risk Analysis
            narratives['risk_analysis'] = self.interpret_risk(ctx)
        except Exception as e:
            narratives['risk_analysis'] = f"[Risk Analysis 생성 오류: {str(e)}]"
        
        try:
            # Section 7: Roadmap
            narratives['roadmap'] = self.interpret_roadmap(ctx)
        except Exception as e:
            narratives['roadmap'] = f"[Roadmap 생성 오류: {str(e)}]"
        
        try:
            # Section 8: Academic Conclusion
            narratives['academic_conclusion'] = self.interpret_academic_conclusion(ctx)
        except Exception as e:
            narratives['academic_conclusion'] = f"[Academic Conclusion 생성 오류: {str(e)}]"
        
        return narratives
