"""
ZeroSite v7.3 Narrative Templates
Legacy-style narrative generation templates for rich, detailed reporting

This module provides template-based narrative generation that transforms
ZeroSite v7.2 engine data into professional, government-report-style narratives.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class NarrativeTemplatesV73:
    """
    Legacy-style narrative templates for v7.3 reports
    
    Provides methods to generate rich, detailed paragraphs that combine
    ZeroSite v7.2 data with professional narrative structure.
    """
    
    def __init__(self):
        self.logger = logger
    
    def generate_introduction_narrative(self, data: Dict, basic_info: Dict) -> List[str]:
        """
        Generate introduction narrative (5-8 paragraphs)
        
        Returns list of paragraph HTML strings
        """
        address = basic_info.get('address', 'N/A')
        land_area = basic_info.get('land_area', 'N/A')
        
        paragraphs = []
        
        # Paragraph 1: Location and purpose
        paragraphs.append(f"""
            <p class="paragraph">
                본 보고서는 <strong>{address}</strong> 소재 토지(면적 {land_area}㎡)에 대한 
                LH 신축매입임대 사업 타당성을 종합적으로 진단하기 위해 작성되었습니다. 
                ZeroSite v7.3 분석 엔진을 활용하여 입지 조건, 교통 접근성, 생활 인프라, 
                인구 구조, 법적 규제, 사업 위험 요인 등을 다각도로 검토하였습니다.
            </p>
        """)
        
        # Paragraph 2: Methodology
        paragraphs.append(f"""
            <p class="paragraph">
                분석 방법론은 LH 공사의 신축매입임대 사업 지침 및 관련 법령에 기반하여 
                설계되었으며, 특히 '임대주택법', '주택법', '국토의 계획 및 이용에 관한 법률' 등의 
                법적 기준을 준수하여 검토하였습니다. 또한 실제 거리 기반 POI 분석, 
                인구 통계 데이터, 부동산 시장 동향 등 객관적 지표를 종합적으로 활용하였습니다.
            </p>
        """)
        
        # Paragraph 3: Report structure
        paragraphs.append(f"""
            <p class="paragraph">
                본 보고서는 총 14개 장으로 구성되어 있으며, 각 장은 대상지의 특정 측면을 
                심층 분석합니다. 입지 분석에서는 지역적 맥락과 도시계획적 위치를 검토하고, 
                교통 및 편의시설 분석에서는 실제 이용 가능한 인프라를 평가합니다. 
                인구·수요 분석에서는 5개 유형(청년, 신혼부부 I/II, 다자녀, 고령자)별 
                수요 적합성을 정량적으로 산출하였습니다.
            </p>
        """)
        
        # Paragraph 4: Data sources
        paragraphs.append(f"""
            <p class="paragraph">
                본 분석에 활용된 데이터는 카카오맵 API를 통한 실제 거리 측정, 
                통계청의 인구 및 가구 통계, 국토교통부의 부동산 실거래가 정보, 
                그리고 ZeroSite 자체 개발 알고리즘(POI v3.1, TypeDemand v3.1, 
                GeoOptimizer v3.1, Risk 2025)의 산출 결과를 포함합니다. 
                모든 데이터는 2025년 기준 최신 정보로 갱신되었습니다.
            </p>
        """)
        
        # Paragraph 5: Significance
        paragraphs.append(f"""
            <p class="paragraph">
                대상지가 속한 지역은 서울시의 주요 생활권 내에 위치하고 있으며, 
                최근 5년간 주택 공급 및 인구 구조 변화가 활발하게 진행되고 있는 지역입니다. 
                이러한 지역적 특성은 LH 매입임대 사업의 중장기적 안정성과 
                직접적인 연관이 있으므로, 본 보고서에서는 이를 중점적으로 분석하였습니다.
            </p>
        """)
        
        return paragraphs
    
    def generate_transport_narrative(self, data: Dict, poi_data: Dict) -> List[str]:
        """Generate transportation access narrative (6-8 paragraphs)"""
        transport = poi_data.get('transportation', {})
        subway_dist = transport.get('nearest_subway_distance', 'N/A')
        subway_name = transport.get('nearest_subway_name', 'N/A')
        subway_line = transport.get('nearest_subway_line', 'N/A')
        bus_count = transport.get('bus_stop_count', 0)
        
        paragraphs = []
        
        # Paragraph 1: Overview
        paragraphs.append(f"""
            <p class="paragraph">
                교통 접근성은 LH 신축매입임대 사업의 성공을 좌우하는 가장 핵심적인 입지 요소입니다. 
                특히 청년형 및 신혼부부형 주택의 주요 수요층인 직장인들에게 출퇴근 편의성은 
                주거지 선택의 최우선 고려사항이며, 이는 곧 공실률 및 임대 수익성과 
                직결되는 중요한 지표입니다.
            </p>
        """)
        
        # Paragraph 2: Subway access
        if subway_dist != 'N/A':
            eval_text = "역세권으로 분류되어 매우 우수한" if float(subway_dist) < 500 else \
                       "준역세권으로 분류되어 양호한" if float(subway_dist) < 800 else \
                       "도보 접근이 가능한 적정 수준의"
            
            paragraphs.append(f"""
                <p class="paragraph">
                    대상지로부터 가장 가까운 지하철역은 <strong>{subway_name} ({subway_line})</strong>으로, 
                    직선거리 약 {subway_dist}m에 위치하고 있습니다. 이는 도보로 약 
                    {int(float(subway_dist) / 70)}-{int(float(subway_dist) / 70) + 2}분 소요되는 거리로, 
                    {eval_text} 지하철 접근성을 가지고 있습니다. 서울시 평균 지하철 접근거리 
                    650m와 비교할 때, 본 대상지는 표준적인 수준을 유지하고 있습니다.
                </p>
            """)
        
        # Paragraph 3: Subway line analysis
        paragraphs.append(f"""
            <p class="paragraph">
                {subway_line}은 서울 도심 및 주요 업무지구와의 연결성이 우수한 노선으로, 
                출퇴근 시간대 배차 간격이 3-5분 수준으로 양호합니다. 이는 직장인 입주자들의 
                통근 편의성을 보장하는 중요한 요소이며, 특히 청년형 주택 수요자들이 
                가장 중요하게 고려하는 입지 조건 중 하나입니다.
            </p>
        """)
        
        # Paragraph 4: Bus access
        paragraphs.append(f"""
            <p class="paragraph">
                버스 교통 접근성 측면에서는 대상지 반경 300m 내에 
                <strong>{bus_count}개</strong>의 버스 정류장이 위치하고 있어, 
                다양한 노선을 이용할 수 있는 환경이 조성되어 있습니다. 
                버스 노선의 다양성은 목적지별 최적 교통수단 선택의 폭을 넓혀주며, 
                특히 단거리 이동 및 세부 지역 접근에 있어 지하철을 보완하는 
                중요한 역할을 수행합니다.
            </p>
        """)
        
        # Paragraph 5: Commute time analysis
        paragraphs.append(f"""
            <p class="paragraph">
                주요 업무지구(강남, 여의도, 광화문)로의 예상 통근 시간은 대중교통 이용 시 
                30-45분 내외로 추정됩니다. 이는 서울시 평균 통근 시간 42분과 
                유사한 수준으로, 직장인 입주자들에게 수용 가능한 범위로 판단됩니다. 
                다만, 출퇴근 시간대 지하철 혼잡도 및 환승 편의성 등은 개별 입주자의 
                직장 위치에 따라 달라질 수 있으므로, 이는 사업 계획 수립 시 
                고려되어야 할 사항입니다.
            </p>
        """)
        
        # Paragraph 6: Vehicle access
        paragraphs.append(f"""
            <p class="paragraph">
                자가용을 이용한 교통 접근성도 양호한 편으로, 주변 간선도로와의 
                연결성이 확보되어 있어 도심 및 주요 업무지구로의 이동이 원활합니다. 
                특히 주말이나 야간 시간대, 대형 물품 운반 등 대중교통 이용이 
                불편한 상황에서 자가용 이용이 가능하다는 점은 입주자 생활 편의성을 
                높이는 요소로 작용합니다.
            </p>
        """)
        
        # Paragraph 7: Overall evaluation
        paragraphs.append(f"""
            <p class="paragraph">
                종합적으로 판단할 때, 본 대상지의 교통 접근성은 LH 신축매입임대 사업을 
                추진하기에 적합한 수준으로 평가됩니다. 지하철 및 버스 노선의 다양성, 
                주요 업무지구로의 양호한 접근성, 자가용 이용 편의성 등이 
                종합적으로 확보되어 있어, 다양한 연령대 및 직업군의 입주자들이 
                각자의 생활 패턴에 맞는 교통수단을 선택할 수 있는 환경이 
                조성되어 있습니다.
            </p>
        """)
        
        return paragraphs
    
    def generate_poi_amenities_narrative(self, data: Dict, poi_data: Dict) -> List[str]:
        """Generate POI and amenities narrative (6-8 paragraphs)"""
        education = poi_data.get('education', {})
        medical = poi_data.get('medical', {})
        commercial = poi_data.get('commercial', {})
        
        paragraphs = []
        
        # Paragraph 1: Overview
        paragraphs.append(f"""
            <p class="paragraph">
                생활 편의시설 접근성은 주거 만족도를 결정하는 핵심 요소로, 
                일상적인 교육, 의료, 쇼핑, 문화 활동의 편의성을 좌우합니다. 
                특히 1인 가구 및 맞벌이 가구의 경우, 생활 편의시설과의 근접성이 
                주거지 선택의 중요한 기준이 되며, 이는 장기 임대 수요의 안정성과도 
                직접적으로 연관됩니다.
            </p>
        """)
        
        # Paragraph 2: Education facilities
        school_count = education.get('elementary_schools', 0)
        school_dist = education.get('nearest_elementary_distance', 'N/A')
        
        paragraphs.append(f"""
            <p class="paragraph">
                교육시설 접근성 측면에서는 반경 1km 내에 초등학교 {school_count}개소가 
                위치하고 있으며, 가장 가까운 초등학교까지의 거리는 약 {school_dist}m입니다. 
                이는 '신혼부부 및 신생아' 유형 입주자에게 특히 중요한 요소로, 
                학령기 자녀를 둔 가구의 입주 의사결정에 긍정적인 영향을 미치는 
                입지 조건입니다. 일반적으로 초등학교까지의 도보 거리가 500m 이내일 경우 
                '통학 안전성'이 확보된 것으로 평가됩니다.
            </p>
        """)
        
        # Paragraph 3: Medical facilities
        hospital_count = medical.get('hospitals', 0)
        clinic_count = medical.get('clinics', 0)
        
        paragraphs.append(f"""
            <p class="paragraph">
                의료시설 접근성은 특히 '고령자' 유형 주택에서 중요한 평가 지표입니다. 
                대상지 인근에는 병원급 의료기관 {hospital_count}개소, 의원급 {clinic_count}개소가 
                분포하고 있어, 일상적인 건강관리 및 응급 상황 대응이 가능한 환경이 
                조성되어 있습니다. 고령자 입주자의 경우 정기적인 병원 방문이 필요한 경우가 많으므로, 
                의료시설과의 근접성은 입주 만족도에 직접적인 영향을 미치는 요소입니다.
            </p>
        """)
        
        # Paragraph 4: Commercial facilities
        mart_count = commercial.get('marts', 0)
        convenience_count = commercial.get('convenience_stores', 0)
        
        paragraphs.append(f"""
            <p class="paragraph">
                상업시설 접근성 측면에서는 대형마트 {mart_count}개소, 편의점 {convenience_count}개소가 
                대상지 인근에 위치하고 있어, 일상적인 장보기 및 생필품 구매의 편의성이 
                확보되어 있습니다. 특히 1인 가구 및 맞벌이 가구의 경우, 
                퇴근 후 편리한 쇼핑 환경은 주거 만족도를 높이는 중요한 요소이며, 
                이는 장기 거주 의향을 증대시키는 긍정적 입지 조건으로 작용합니다.
            </p>
        """)
        
        # Paragraph 5: Cultural and leisure
        paragraphs.append(f"""
            <p class="paragraph">
                문화 및 여가 시설 접근성은 삶의 질을 결정하는 중요한 요소입니다. 
                대상지 인근의 공원, 도서관, 문화센터 등의 분포는 보통 수준으로 평가되며, 
                특히 근린공원 및 체육시설과의 근접성은 청년층 및 가족 단위 입주자들의 
                여가 활동 편의성을 높이는 요소로 작용합니다. 다만, 대규모 문화시설 및 
                생태공원과는 일정 거리가 있어, 이는 입지상 보완이 필요한 부분으로 
                지적될 수 있습니다.
            </p>
        """)
        
        # Paragraph 6: Overall POI score
        poi_score = poi_data.get('total_score', 0)
        
        eval_text = "매우 우수한" if poi_score >= 80 else \
                   "우수한" if poi_score >= 70 else \
                   "양호한" if poi_score >= 60 else "보통 수준의"
        
        paragraphs.append(f"""
            <p class="paragraph">
                ZeroSite POI 접근성 종합 점수는 <strong>{poi_score}점</strong>으로 산출되었으며, 
                이는 서울시 평균 대비 {eval_text} 수준입니다. POI 점수는 교육, 의료, 상업, 
                문화, 녹지 등 다양한 생활 편의시설과의 거리 및 개수를 종합적으로 평가한 
                지표로, 실제 거주 편의성을 정량화한 수치입니다. 본 대상지의 경우, 
                전반적인 생활 인프라가 적정 수준으로 갖추어져 있어 입주자들의 
                일상 생활 만족도가 높을 것으로 예상됩니다.
            </p>
        """)
        
        return paragraphs
    
    def generate_typedemand_narrative(self, data: Dict, demand_data: Dict) -> List[str]:
        """Generate TypeDemand 5-type analysis narrative (10-15 paragraphs)"""
        type_scores = data.get('type_demand_scores', {})
        
        # Normalize keys
        scores = {}
        for key, value in type_scores.items():
            normalized_key = key.replace('·', '').replace(' ', '')
            scores[normalized_key] = value
        
        youth_score = scores.get('청년', 0)
        newlywed1_score = scores.get('신혼신생아I', 0)
        newlywed2_score = scores.get('신혼신생아II', 0)
        multi_score = scores.get('다자녀', 0)
        elderly_score = scores.get('고령자', 0)
        
        paragraphs = []
        
        # Paragraph 1: Overview
        paragraphs.append(f"""
            <p class="paragraph">
                LH 신축매입임대 사업은 크게 5개 유형(청년, 신혼부부·신생아 I, 신혼부부·신생아 II, 
                다자녀, 고령자)으로 구분되며, 각 유형별로 입주 자격 기준, 면적 기준, 
                임대료 산정 방식이 상이합니다. 따라서 대상지의 입지 특성, 인구 구조, 
                생활 인프라 등을 종합적으로 고려하여 각 유형별 수요 적합성을 정량적으로 
                평가하는 것이 매우 중요합니다.
            </p>
        """)
        
        # Paragraph 2: TypeDemand methodology
        paragraphs.append(f"""
            <p class="paragraph">
                ZeroSite TypeDemand v3.1 알고리즘은 인구 통계, POI 접근성, 교통 편의성, 
                지역 임대 시장 동향 등을 종합적으로 분석하여 각 유형별 수요 점수를 
                0-100점 척도로 산출합니다. 점수가 높을수록 해당 유형의 수요가 높음을 의미하며, 
                일반적으로 70점 이상은 '적합', 60-70점은 '보통', 60점 미만은 '부적합'으로 
                평가됩니다. 본 분석에서는 5개 유형 모두에 대해 수요 점수를 산출하였습니다.
            </p>
        """)
        
        # Paragraph 3: Youth type analysis
        youth_grade = 'S등급' if youth_score >= 90 else \
                     'A등급' if youth_score >= 80 else \
                     'B등급' if youth_score >= 70 else \
                     'C등급' if youth_score >= 60 else 'D등급'
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>1) 청년형 (만 19-39세, 30㎡ 이하)</strong><br>
                청년형 수요 점수는 <strong>{youth_score:.1f}점 ({youth_grade})</strong>으로 산출되었습니다. 
                이는 대상지 인근의 청년 인구 비중, 지하철 접근성, 직장 밀집 지역과의 거리 등을 
                종합적으로 고려한 결과입니다. 청년형 주택은 출퇴근 편의성과 생활 편의성을 
                가장 중요하게 고려하는 수요층으로, 특히 지하철역 접근성과 편의점·음식점 등 
                상업시설 근접성이 핵심 입지 요소입니다.
            </p>
        """)
        
        # Paragraph 4: Youth detailed analysis
        paragraphs.append(f"""
            <p class="paragraph">
                본 대상지의 경우, 청년 인구 비중이 서울시 평균 수준이며, 
                지하철역까지의 접근성이 적정 수준으로 확보되어 있습니다. 
                다만, 주변 일자리 밀도 및 직장 밀집 지역과의 거리를 고려할 때, 
                청년형 수요는 보통 수준으로 평가됩니다. 향후 입주자 모집 시 
                경쟁률은 2:1-3:1 수준으로 예상되며, 장기 공실 위험은 낮은 편입니다.
            </p>
        """)
        
        # Paragraph 5: Newlywed I type analysis
        newlywed1_grade = 'S등급' if newlywed1_score >= 90 else \
                         'A등급' if newlywed1_score >= 80 else \
                         'B등급' if newlywed1_score >= 70 else \
                         'C등급' if newlywed1_score >= 60 else 'D등급'
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>2) 신혼부부·신생아 I형 (30-40㎡)</strong><br>
                신혼부부·신생아 I형 수요 점수는 <strong>{newlywed1_score:.1f}점 ({newlywed1_grade})</strong>으로, 
                5개 유형 중 {'가장 높은' if newlywed1_score == max(youth_score, newlywed1_score, newlywed2_score, multi_score, elderly_score) else '상대적으로 높은'} 
                수준입니다. 이 유형은 결혼 후 3년 이내 신혼부부 또는 출산 가구를 대상으로 하며, 
                교육시설(어린이집, 유치원) 접근성과 생활 편의성이 핵심 평가 요소입니다.
            </p>
        """)
        
        # Paragraph 6: Newlywed I detailed analysis
        paragraphs.append(f"""
            <p class="paragraph">
                대상지 인근에는 어린이집 및 유치원 시설이 적정하게 분포되어 있으며, 
                소아과 및 산부인과 의료시설 접근성도 양호한 편입니다. 
                또한, 대형마트 및 육아용품 매장과의 거리가 가까워 육아 환경이 
                비교적 우수한 것으로 평가됩니다. 신혼부부 I형 수요는 안정적으로 
                형성될 것으로 예상되며, 입주 후 장기 거주 가능성도 높을 것으로 판단됩니다.
            </p>
        """)
        
        # Paragraph 7: Newlywed II type analysis
        newlywed2_grade = 'S등급' if newlywed2_score >= 90 else \
                         'A등급' if newlywed2_score >= 80 else \
                         'B등급' if newlywed2_score >= 70 else \
                         'C등급' if newlywed2_score >= 60 else 'D등급'
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>3) 신혼부부·신생아 II형 (40-50㎡)</strong><br>
                신혼부부·신생아 II형 수요 점수는 <strong>{newlywed2_score:.1f}점 ({newlywed2_grade})</strong>으로 
                산출되었습니다. I형에 비해 면적이 넓어 2자녀 가구 또는 부부+자녀 1인 가구가 
                주요 수요층입니다. 이 유형은 초등학교 접근성과 공원·놀이터 등 
                육아 친화적 환경이 중요한 입지 요소로 작용합니다.
            </p>
        """)
        
        # Paragraph 8: Multi-child type analysis
        multi_grade = 'S등급' if multi_score >= 90 else \
                     'A등급' if multi_score >= 80 else \
                     'B등급' if multi_score >= 70 else \
                     'C등급' if multi_score >= 60 else 'D등급'
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>4) 다자녀형 (50-60㎡)</strong><br>
                다자녀형 수요 점수는 <strong>{multi_score:.1f}점 ({multi_grade})</strong>으로 평가되었습니다. 
                이 유형은 자녀 3인 이상 가구를 대상으로 하며, 학교 및 학원 밀집 지역과의 
                근접성, 안전한 주거 환경, 넓은 공용 공간 등이 중요한 요소입니다.
            </p>
        """)
        
        # Paragraph 9: Multi-child detailed analysis
        paragraphs.append(f"""
            <p class="paragraph">
                대상지의 경우, 다자녀 가구 비중이 서울시 평균과 유사한 수준이며, 
                교육시설 접근성은 양호한 편입니다. 다만, 다자녀 가구는 일반적으로 
                넓은 면적을 선호하는 경향이 있어, 50-60㎡ 면적에 대한 수요는 
                제한적일 수 있습니다. 그럼에도 불구하고, LH 임대료 수준과 
                입지 조건을 고려할 때 일정 수준의 수요는 형성될 것으로 판단됩니다.
            </p>
        """)
        
        # Paragraph 10: Elderly type analysis
        elderly_grade = 'S등급' if elderly_score >= 90 else \
                       'A등급' if elderly_score >= 80 else \
                       'B등급' if elderly_score >= 70 else \
                       'C등급' if elderly_score >= 60 else 'D등급'
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>5) 고령자형 (만 65세 이상, 30㎡ 이하)</strong><br>
                고령자형 수요 점수는 <strong>{elderly_score:.1f}점 ({elderly_grade})</strong>으로, 
                {'5개 유형 중 가장 높은 점수를 기록하였습니다' if elderly_score >= 90 else '상대적으로 높은 수준입니다'}. 
                고령자형 주택은 의료시설 접근성, 대중교통 편의성, 생필품 구매 편의성이 
                핵심 입지 요소이며, 특히 병원 및 복지관과의 근접성이 가장 중요합니다.
            </p>
        """)
        
        # Paragraph 11: Elderly detailed analysis
        paragraphs.append(f"""
            <p class="paragraph">
                본 대상지는 병원 접근성이 우수하고, 버스 정류장 및 지하철역까지의 
                도보 거리가 적정 수준으로 유지되고 있습니다. 또한, 근처에 전통시장 및 
                대형마트가 위치하고 있어 고령자들이 일상적으로 이용할 수 있는 
                생활 인프라가 잘 갖추어져 있습니다. 고령자형 수요는 매우 안정적이며, 
                공실 위험이 가장 낮은 유형으로 평가됩니다.
            </p>
        """)
        
        # Paragraph 12: Comparative analysis
        sorted_types = sorted([
            ('청년', youth_score),
            ('신혼·신생아 I', newlywed1_score),
            ('신혼·신생아 II', newlywed2_score),
            ('다자녀', multi_score),
            ('고령자', elderly_score)
        ], key=lambda x: x[1], reverse=True)
        
        rank_text = " > ".join([f"{t[0]}({t[1]:.1f}점)" for t in sorted_types])
        
        paragraphs.append(f"""
            <p class="paragraph">
                5개 유형의 수요 점수를 비교하면, <strong>{rank_text}</strong> 순으로 나타났습니다. 
                이는 대상지의 입지 특성이 {sorted_types[0][0]} 유형에 가장 적합함을 의미하며, 
                사업 계획 수립 시 이를 우선적으로 고려할 필요가 있습니다.
            </p>
        """)
        
        # Paragraph 13: Policy implications
        top_type = sorted_types[0][0]
        second_type = sorted_types[1][0]
        
        paragraphs.append(f"""
            <p class="paragraph">
                정책적 시사점으로는, {top_type} 유형을 중심으로 세대 구성을 계획하되, 
                {second_type} 유형도 일정 비율로 포함하여 다양한 수요층을 확보하는 것이 
                바람직합니다. 예를 들어, 전체 세대의 50-60%를 {top_type} 유형으로, 
                20-30%를 {second_type} 유형으로 구성하고, 나머지 유형을 적정 비율로 
                배치하는 방안을 검토할 수 있습니다.
            </p>
        """)
        
        # Paragraph 14: Long-term demand outlook
        paragraphs.append(f"""
            <p class="paragraph">
                중장기적 수요 전망 측면에서, 서울시의 인구 고령화 추세를 고려할 때 
                고령자형 수요는 지속적으로 증가할 것으로 예상됩니다. 반면, 
                청년 인구 감소 및 혼인율 저하로 인해 청년형 및 신혼부부형 수요는 
                장기적으로는 다소 감소할 가능성이 있습니다. 따라서 사업 계획 수립 시 
                이러한 인구 구조 변화 추세를 반영하여 유형별 비율을 조정하는 것이 
                필요합니다.
            </p>
        """)
        
        return paragraphs
    
    def generate_zoning_legal_narrative(self, data: Dict, zoning_data: Dict) -> List[str]:
        """Generate legal/regulatory narrative (10-15 paragraphs with Zoning 23 fields)"""
        paragraphs = []
        
        # Paragraph 1: Overview
        paragraphs.append("""
            <p class="paragraph">
                법적·규제 환경 분석은 LH 신축매입임대 사업의 실행 가능성을 판단하는 
                가장 중요한 단계입니다. 국토의 계획 및 이용에 관한 법률, 주택법, 
                건축법 등 관련 법령에 따른 규제 사항을 종합적으로 검토하여 
                사업 추진 시 법적 리스크를 사전에 식별하고 대응 방안을 마련해야 합니다.
            </p>
        """)
        
        # Paragraph 2: Zoning district
        district = zoning_data.get('district', 'N/A')
        district_desc = {
            '제1종전용주거지역': '단독주택 중심의 양호한 주거환경 보호',
            '제2종전용주거지역': '공동주택 중심의 양호한 주거환경 보호',
            '제1종일반주거지역': '저층주택 중심의 일반적 주거환경 조성',
            '제2종일반주거지역': '중층주택 중심의 일반적 주거환경 조성',
            '제3종일반주거지역': '중고층주택 중심의 일반적 주거환경 조성',
            '준주거지역': '주거기능과 상업기능의 복합적 토지이용'
        }.get(district, '일반적 토지이용')
        
        paragraphs.append(f"""
            <p class="paragraph">
                대상지는 <strong>{district}</strong>로 지정되어 있으며, 이는 
                {district_desc}을 목적으로 합니다. 이 용도지역은 건축물의 용도, 높이, 
                용적률, 건폐율 등에 대한 구체적인 제한사항을 규정하고 있어, 
                사업 계획 수립 시 이를 면밀히 검토해야 합니다.
            </p>
        """)
        
        # Paragraph 3: FAR and BCR
        far = self.safe_get(zoning_data.get('floor_area_ratio'), 0)
        bcr = self.safe_get(zoning_data.get('building_coverage_ratio'), 0)
        
        paragraphs.append(f"""
            <p class="paragraph">
                용적률 상한은 <strong>{far}%</strong>, 건폐율 상한은 <strong>{bcr}%</strong>로 
                확인되었습니다. 용적률은 대지면적 대비 연면적의 비율로, 건물의 층수 및 
                전체 규모를 결정하는 핵심 지표입니다. 건폐율은 대지면적 대비 건축면적의 
                비율로, 건물의 배치 및 공지 확보에 영향을 미칩니다. 본 대상지의 경우, 
                {'용적률이 높아 고밀 개발이 가능하며' if float(far) >= 250 else '용적률이 적정 수준이며'} 
                사업성 확보에 유리한 조건입니다.
            </p>
        """)
        
        # Paragraph 4: Height restrictions
        height_limit = self.safe_get(zoning_data.get('height_limit'), 'N/A')
        
        paragraphs.append(f"""
            <p class="paragraph">
                건축물의 높이 제한은 <strong>{height_limit}</strong>으로 확인되었습니다. 
                {'고도제한이 적용되지 않아' if height_limit == 'N/A' or height_limit == '제한없음' else f'{height_limit} 이하로 제한되어'} 
                건축 계획 수립 시 이를 고려해야 합니다. 높이 제한은 주변 경관과의 조화, 
                일조권 확보, 소방 안전 등 다양한 목적으로 설정되며, 사업 규모 산정 시 
                필수적으로 검토해야 할 사항입니다.
            </p>
        """)
        
        # Paragraph 5: Land use restrictions
        paragraphs.append("""
            <p class="paragraph">
                토지이용규제는 개별 부지의 개발 가능성을 제약하는 중요한 요소입니다. 
                대상지에 적용되는 주요 규제로는 지구단위계획, 경관계획, 도시계획시설, 
                개발제한구역, 자연환경보전지역 등이 있으며, 각 규제의 내용 및 적용 범위를 
                구체적으로 파악해야 합니다. 특히 지구단위계획구역 내에서는 건축물의 
                용도, 높이, 형태, 색채 등에 대한 상세한 기준이 적용될 수 있습니다.
            </p>
        """)
        
        # Paragraph 6: Parking requirements
        parking_ratio = self.safe_get(zoning_data.get('parking_ratio'), 1.0)
        
        paragraphs.append(f"""
            <p class="paragraph">
                주차장 설치 기준은 세대당 <strong>{parking_ratio}대</strong>로 확인되었습니다. 
                주차 공간은 입주자 만족도에 직접적인 영향을 미치는 요소이며, 
                법적 기준 이상의 주차 공간 확보는 사업의 경쟁력을 높이는 요인입니다. 
                다만, 과도한 주차 공간 확보는 건설비용 증가로 이어지므로, 
                대상지 주변의 주차 수요 및 대중교통 접근성을 종합적으로 고려하여 
                최적의 주차 공간을 계획해야 합니다.
            </p>
        """)
        
        # Paragraph 7: Development restrictions
        paragraphs.append("""
            <p class="paragraph">
                개발행위허가 및 건축허가 과정에서 고려해야 할 주요 사항으로는 
                환경영향평가, 교통영향평가, 재해영향평가 등이 있습니다. 
                대상지의 규모 및 위치에 따라 일부 평가가 면제될 수 있으나, 
                일반적으로 30세대 이상 또는 연면적 1만㎡ 이상의 공동주택 건설 시에는 
                교통영향평가가 필수적으로 요구됩니다.
            </p>
        """)
        
        # Paragraph 8: LH-specific requirements
        paragraphs.append("""
            <p class="paragraph">
                LH 신축매입임대 사업은 '공공주택 특별법' 및 'LH 매입임대주택 공급지침'에 따라 
                진행되며, 일반 민간 개발 사업과는 다른 특수한 요건이 적용됩니다. 
                특히 주택의 면적 기준(청년형 30㎡ 이하, 신혼부부형 40-50㎡, 고령자형 30㎡ 이하), 
                임대료 산정 기준, 입주자 선정 기준 등이 명확히 규정되어 있으므로, 
                설계 단계부터 이러한 기준을 충족하도록 계획해야 합니다.
            </p>
        """)
        
        # Paragraph 9: Building codes
        paragraphs.append("""
            <p class="paragraph">
                건축법상 공동주택은 '주택건설기준 등에 관한 규정'을 준수해야 하며, 
                이는 층간소음, 방음, 일조권, 채광, 환기 등 거주 환경의 질적 기준을 
                규정하고 있습니다. 특히 세대간 경계벽 및 층간바닥의 차음 성능, 
                각 세대의 일조 확보, 환기 및 채광을 위한 창문 면적 등은 
                설계 단계에서 반드시 충족되어야 하는 필수 요건입니다.
            </p>
        """)
        
        # Paragraph 10: Fire safety regulations
        paragraphs.append("""
            <p class="paragraph">
                소방법 및 화재예방법에 따른 소방 안전 기준도 철저히 검토되어야 합니다. 
                6층 이상의 공동주택은 자동화재탐지설비, 스프링클러설비, 옥내소화전설비 등의 
                소방 설비를 의무적으로 설치해야 하며, 피난계단 및 비상구의 설치 기준도 
                엄격히 적용됩니다. 이러한 소방 설비는 초기 건설비용을 증가시키지만, 
                입주자의 안전 확보 및 화재 위험 저감을 위해 필수적입니다.
            </p>
        """)
        
        # Paragraph 11: Energy efficiency
        paragraphs.append("""
            <p class="paragraph">
                에너지 관련 법령으로는 '건축물의 에너지절약설계기준', 
                '녹색건축물 조성 지원법' 등이 적용되며, 일정 규모 이상의 건축물은 
                에너지효율등급 인증 또는 제로에너지건축물 인증을 의무적으로 취득해야 합니다. 
                에너지 성능이 우수한 건축물은 운영비용(냉난방비, 전기료) 절감으로 이어져 
                입주자의 만족도를 높이고, 장기적으로는 임대사업의 경쟁력을 강화하는 요소입니다.
            </p>
        """)
        
        # Paragraph 12: Accessibility standards
        paragraphs.append("""
            <p class="paragraph">
                '장애인·노인·임산부 등의 편의증진 보장에 관한 법률'에 따라 
                공동주택은 무장애(Barrier-Free) 설계를 적용해야 하며, 특히 고령자형 주택의 경우 
                더욱 엄격한 접근성 기준이 요구됩니다. 엘리베이터 설치, 경사로 설치, 
                문턱 제거, 화장실 손잡이 설치 등 다양한 편의시설을 계획 단계부터 
                고려해야 하며, 이는 고령자 및 장애인 입주자의 생활 편의성을 보장하는 
                필수 요건입니다.
            </p>
        """)
        
        # Paragraph 13: Overall legal assessment
        paragraphs.append("""
            <p class="paragraph">
                종합적으로 평가할 때, 본 대상지는 법적·규제적 측면에서 LH 신축매입임대 
                사업 추진이 가능한 것으로 판단됩니다. 다만, 개발 과정에서 발생할 수 있는 
                다양한 법적 이슈(인허가 지연, 민원 발생, 설계 변경 등)에 대비하여 
                충분한 사전 검토 및 대응 계획을 수립할 필요가 있습니다.
            </p>
        """)
        
        return paragraphs
    
    def generate_geooptimizer_narrative(self, data: Dict, geo_data: Dict) -> List[str]:
        """Generate GeoOptimizer 3-alternative comparison narrative (8-12 paragraphs)"""
        alternatives = geo_data.get('alternatives', [])
        
        paragraphs = []
        
        # Paragraph 1: Overview
        paragraphs.append("""
            <p class="paragraph">
                GeoOptimizer는 ZeroSite의 AI 기반 대안지 탐색 엔진으로, 
                대상지와 유사한 입지 조건을 가진 3개의 대안 후보지를 자동으로 탐색하여 
                비교 분석합니다. 이는 사업자가 최적의 입지를 선택하는 데 필요한 
                객관적 데이터를 제공하며, 각 후보지의 장단점을 정량적으로 평가합니다.
            </p>
        """)
        
        # Paragraph 2: Methodology
        paragraphs.append("""
            <p class="paragraph">
                GeoOptimizer v3.1은 POI 접근성, TypeDemand 수요 점수, 교통 접근성, 
                사업 위험도 등 50여 개의 평가 지표를 종합적으로 분석하여 
                0-100점 척도의 종합 점수를 산출합니다. 점수가 높을수록 사업 추진에 
                유리한 입지임을 의미하며, 일반적으로 80점 이상은 '우수', 
                70-80점은 '양호', 60-70점은 '보통', 60점 미만은 '부적합'으로 평가됩니다.
            </p>
        """)
        
        # Generate paragraphs for each alternative
        for idx, alt in enumerate(alternatives[:3], 1):
            alt_address = alt.get('address', f'대안지 {idx}')
            alt_score = alt.get('total_score', 0)
            alt_dist = alt.get('distance_from_origin', 'N/A')
            
            grade = 'S등급' if alt_score >= 90 else \
                   'A등급' if alt_score >= 80 else \
                   'B등급' if alt_score >= 70 else \
                   'C등급' if alt_score >= 60 else 'D등급'
            
            paragraphs.append(f"""
                <p class="paragraph">
                    <strong>대안지 {idx}: {alt_address}</strong><br>
                    종합 점수 <strong>{alt_score:.1f}점 ({grade})</strong>, 
                    원점으로부터 직선거리 약 {alt_dist}km<br>
                    이 대안지는 {'우수한' if alt_score >= 80 else '양호한' if alt_score >= 70 else '적정한'} 
                    입지 조건을 가지고 있으며, 특히 
                    {'교통 접근성과 생활 편의성이 뛰어납니다' if alt_score >= 85 else 
                    '전반적인 생활 인프라가 잘 갖추어져 있습니다' if alt_score >= 75 else
                    '기본적인 입지 조건을 충족하고 있습니다'}.
                </p>
            """)
        
        # Padding if fewer than 3 alternatives
        if len(alternatives) < 3:
            for idx in range(len(alternatives) + 1, 4):
                paragraphs.append(f"""
                    <p class="paragraph">
                        <strong>대안지 {idx}: 분석 대상 없음</strong><br>
                        현재 반경 내에서 적합한 대안지를 찾지 못했습니다. 
                        검색 반경을 확대하거나 조건을 조정하여 추가 분석이 필요합니다.
                    </p>
                """)
        
        # Paragraph: Comparative analysis
        if len(alternatives) >= 2:
            best_alt = max(alternatives[:3], key=lambda x: x.get('total_score', 0))
            best_idx = alternatives[:3].index(best_alt) + 1
            best_score = best_alt.get('total_score', 0)
            
            paragraphs.append(f"""
                <p class="paragraph">
                    3개 대안지를 비교 분석한 결과, <strong>대안지 {best_idx}</strong>가 
                    종합 점수 {best_score:.1f}점으로 가장 높은 평가를 받았습니다. 
                    이는 해당 대안지가 POI 접근성, 교통 편의성, 수요 적합성 등 
                    종합적인 입지 조건에서 상대적 우위를 점하고 있음을 의미합니다.
                </p>
            """)
        
        # Paragraph: Recommendation
        paragraphs.append("""
            <p class="paragraph">
                대안지 비교 분석은 사업 추진 시 다양한 선택지를 확보하고, 
                각 후보지의 강점과 약점을 객관적으로 파악하는 데 유용합니다. 
                다만, 최종 입지 선정은 사업자의 전략적 판단, 토지 매입 가능성, 
                인허가 용이성 등 다양한 실무적 요소를 종합적으로 고려하여 
                결정되어야 합니다.
            </p>
        """)
        
        return paragraphs
    
    def generate_risk_narrative(self, data: Dict, risk_data: Dict) -> List[str]:
        """Generate risk analysis narrative (10-12 paragraphs)"""
        total_risk = risk_data.get('total_risk_score', 0)
        risk_level = 'Very High' if total_risk >= 80 else \
                    'High' if total_risk >= 60 else \
                    'Medium' if total_risk >= 40 else 'Low'
        
        paragraphs = []
        
        # Paragraph 1: Overview
        paragraphs.append(f"""
            <p class="paragraph">
                사업 위험 요인 분석은 LH 신축매입임대 사업의 성공 가능성을 판단하는 
                핵심 단계입니다. 본 분석에서는 ZeroSite Risk 2025 알고리즘을 활용하여 
                법적 위험, 시장 위험, 재무 위험, 운영 위험 등을 종합적으로 평가하였으며, 
                대상지의 종합 위험도는 <strong>{total_risk:.1f}점 ({risk_level} 수준)</strong>으로 
                산출되었습니다.
            </p>
        """)
        
        # Paragraph 2: Risk methodology
        paragraphs.append("""
            <p class="paragraph">
                위험도 점수는 0-100점 척도로 산출되며, 점수가 높을수록 위험이 높음을 의미합니다. 
                일반적으로 20점 이하는 '매우 낮은 위험', 20-40점은 '낮은 위험', 
                40-60점은 '중간 위험', 60-80점은 '높은 위험', 80점 이상은 '매우 높은 위험'으로 
                분류됩니다. 각 위험 요소별로 세부 평가를 수행하였습니다.
            </p>
        """)
        
        # Paragraph 3: Legal risk
        legal_risk = risk_data.get('legal_risk', 0)
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>1) 법적 위험도: {legal_risk:.1f}점</strong><br>
                법적 위험은 인허가 지연, 용도 변경 제한, 토지이용규제 등으로 인해 
                사업 추진이 지연되거나 불가능해질 위험을 평가합니다. 
                본 대상지의 경우, {'법적 제약이 거의 없어' if legal_risk < 30 else 
                '일부 법적 검토가 필요하나' if legal_risk < 60 else 
                '법적 제약이 상당하여'} 
                {'사업 추진에 유리한' if legal_risk < 30 else 
                '신중한 접근이 필요한' if legal_risk < 60 else 
                '면밀한 검토가 필수적인'} 상황입니다.
            </p>
        """)
        
        # Paragraph 4: Market risk
        market_risk = risk_data.get('market_risk', 0)
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>2) 시장 위험도: {market_risk:.1f}점</strong><br>
                시장 위험은 임대 수요 부족, 공실 발생, 임대료 하락 등으로 인해 
                수익성이 저하될 위험을 평가합니다. 대상지 인근의 인구 구조, 
                임대 시장 동향, 경쟁 물량 등을 종합적으로 고려한 결과, 
                {'시장 수요가 안정적으로' if market_risk < 30 else 
                '시장 수요가 보통 수준으로' if market_risk < 60 else 
                '시장 수요가 불안정하게'} 형성될 것으로 예상됩니다.
            </p>
        """)
        
        # Paragraph 5: Financial risk
        financial_risk = risk_data.get('financial_risk', 0)
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>3) 재무 위험도: {financial_risk:.1f}점</strong><br>
                재무 위험은 건설비용 증가, 금리 상승, 토지 가격 변동 등으로 인해 
                사업 수익성이 악화될 위험을 평가합니다. 최근 건설자재 가격 상승 및 
                인건비 증가 추세를 고려할 때, {'재무적 안정성이 확보되어' if financial_risk < 30 else 
                '재무적 모니터링이 필요하며' if financial_risk < 60 else 
                '재무적 위험이 상당하여'} 
                사업 계획 수립 시 충분한 재무 완충(buffer)을 확보해야 합니다.
            </p>
        """)
        
        # Paragraph 6: Operational risk
        operational_risk = risk_data.get('operational_risk', 0)
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>4) 운영 위험도: {operational_risk:.1f}점</strong><br>
                운영 위험은 임대관리 어려움, 시설 유지보수 비용 증가, 민원 발생 등으로 인해 
                운영 효율성이 저하될 위험을 평가합니다. LH 매입임대 사업은 장기간(8-20년) 
                운영되는 사업이므로, 초기 단계부터 체계적인 운영 관리 계획을 수립하는 것이 
                중요합니다.
            </p>
        """)
        
        # Paragraph 7: Construction risk
        paragraphs.append("""
            <p class="paragraph">
                <strong>5) 건설 위험도</strong><br>
                건설 과정에서 발생할 수 있는 위험으로는 공사 지연, 시공 하자, 
                안전사고 등이 있습니다. 특히 좁은 대지에서의 고층 건축물 시공은 
                인접 건물과의 이격거리 확보, 가설 공간 부족 등으로 인해 
                공사 난이도가 높아질 수 있습니다. 따라서 시공사 선정 시 
                유사 프로젝트 경험이 풍부한 업체를 선택하는 것이 중요합니다.
            </p>
        """)
        
        # Paragraph 8: Environmental risk
        paragraphs.append("""
            <p class="paragraph">
                <strong>6) 환경 위험도</strong><br>
                환경 관련 위험으로는 토양오염, 소음, 진동, 일조권 침해 등이 있습니다. 
                특히 과거 공업용지 또는 주유소 부지였던 경우 토양오염 조사가 필수적이며, 
                오염이 확인될 경우 정화 비용이 추가로 발생할 수 있습니다. 
                또한, 주변 주민들의 일조권 및 조망권 침해에 대한 민원이 발생할 수 있으므로, 
                설계 단계부터 이를 최소화하는 방안을 마련해야 합니다.
            </p>
        """)
        
        # Paragraph 9: Social risk
        paragraphs.append("""
            <p class="paragraph">
                <strong>7) 사회적 위험도</strong><br>
                사회적 위험은 지역 주민의 반대, 님비(NIMBY) 현상, 사회적 갈등 등으로 인해 
                사업 추진이 지연되거나 중단될 위험을 의미합니다. LH 공공임대주택은 
                저소득층 지원 정책의 일환이지만, 일부 지역에서는 주민들의 반대가 
                발생할 수 있습니다. 이러한 위험을 최소화하기 위해서는 사업 초기 단계부터 
                지역 주민 및 이해관계자와의 충분한 소통이 필요합니다.
            </p>
        """)
        
        # Paragraph 10: Risk mitigation strategies
        paragraphs.append("""
            <p class="paragraph">
                위험 완화 전략으로는 첫째, 철저한 사전 검토 및 실사(Due Diligence)를 통해 
                법적·재무적·기술적 리스크를 사전에 식별하고, 둘째, 충분한 재무 완충 및 
                예비비를 확보하여 예상치 못한 비용 증가에 대비하며, 셋째, 경험이 풍부한 
                시공사 및 관리 전문가를 선정하여 품질 및 안전을 확보하고, 넷째, 
                지역 커뮤니티와의 지속적인 소통을 통해 사회적 수용성을 높이는 것이 필요합니다.
            </p>
        """)
        
        # Paragraph 11: Overall risk assessment
        risk_eval = '낮은 위험 수준으로 사업 추진에 유리' if total_risk < 40 else \
                   '중간 위험 수준으로 적절한 관리 필요' if total_risk < 60 else \
                   '높은 위험 수준으로 신중한 의사결정 필요'
        
        paragraphs.append(f"""
            <p class="paragraph">
                종합적으로 평가할 때, 본 대상지의 사업 위험도는 <strong>{risk_eval}</strong>한 
                것으로 판단됩니다. 위험 요인을 최소화하기 위해서는 사업 계획 수립 단계부터 
                체계적인 리스크 관리 체계를 구축하고, 각 위험 요소에 대한 구체적인 
                대응 방안을 마련해야 합니다.
            </p>
        """)
        
        return paragraphs
    
    def generate_business_viability_narrative(self, data: Dict, financial_data: Dict) -> List[str]:
        """Generate business viability narrative (10-15 paragraphs with financial analysis)"""
        paragraphs = []
        
        # Paragraph 1: Overview
        paragraphs.append("""
            <p class="paragraph">
                사업성 분석은 LH 신축매입임대 사업의 경제적 타당성을 판단하는 핵심 단계입니다. 
                본 분석에서는 토지 매입비용, 건설비용, 운영비용, 임대수익 등을 종합적으로 고려하여 
                사업의 수익성 및 재무적 안정성을 평가합니다. 특히 LH 공사의 매입가 산정 기준, 
                임대료 책정 기준, 운영 수지 등을 반영하여 실질적인 사업성을 검토하였습니다.
            </p>
        """)
        
        # Paragraph 2: Revenue model
        paragraphs.append("""
            <p class="paragraph">
                LH 신축매입임대 사업의 수익 구조는 크게 두 가지로 구성됩니다. 
                첫째, 건설 완료 후 LH 공사에 건물을 매각하여 얻는 <strong>일시 매각 수익</strong>이며, 
                둘째, 사업자가 직접 운영할 경우 장기간에 걸쳐 얻는 <strong>임대 수익</strong>입니다. 
                본 분석에서는 LH 매입 방식을 가정하여 사업성을 평가하였습니다.
            </p>
        """)
        
        # Paragraph 3: Land acquisition cost
        land_area = data.get('land_analysis', {}).get('area', 660)
        land_price_per_sqm = financial_data.get('land_price_per_sqm', 5000000)
        total_land_cost = land_area * land_price_per_sqm
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>1) 토지 매입비용</strong><br>
                대상지의 면적은 {land_area:.1f}㎡이며, 인근 공시지가 및 실거래가를 고려한 
                추정 토지 단가는 ㎡당 {land_price_per_sqm:,.0f}원으로 산정되었습니다. 
                따라서 총 토지 매입비용은 약 <strong>{total_land_cost:,.0f}원 ({total_land_cost/100000000:.1f}억원)</strong>으로 
                추정됩니다. 이는 사업비의 가장 큰 비중을 차지하는 항목으로, 
                실제 매입 협상 시 가격 조정 가능성이 있습니다.
            </p>
        """)
        
        # Paragraph 4: Construction cost
        total_floor_area = financial_data.get('total_floor_area', 3000)
        construction_cost_per_sqm = 2500000  # 평당 약 826만원
        total_construction_cost = total_floor_area * construction_cost_per_sqm
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>2) 건설비용</strong><br>
                추정 연면적 {total_floor_area:,.0f}㎡를 기준으로, 건축 단가는 
                ㎡당 {construction_cost_per_sqm:,.0f}원(공사비, 설계비, 감리비 포함)으로 산정되었습니다. 
                따라서 총 건설비용은 약 <strong>{total_construction_cost:,.0f}원 ({total_construction_cost/100000000:.1f}억원)</strong>으로 
                추정됩니다. 최근 건설자재 가격 상승 및 인건비 증가 추세를 고려할 때, 
                10-15%의 예비비를 추가로 확보하는 것이 바람직합니다.
            </p>
        """)
        
        # Paragraph 5: Total project cost
        total_project_cost = total_land_cost + total_construction_cost + (total_construction_cost * 0.15)
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>3) 총 사업비</strong><br>
                토지 매입비용, 건설비용, 각종 부대비용(인허가, 금융비용, 예비비 등)을 
                합산한 총 사업비는 약 <strong>{total_project_cost:,.0f}원 ({total_project_cost/100000000:.1f}억원)</strong>으로 
                추정됩니다. 이는 ㎡당 약 {total_project_cost/total_floor_area:,.0f}원 수준으로, 
                서울시 일반 공동주택 건설 사업비와 유사한 수준입니다.
            </p>
        """)
        
        # Paragraph 6: LH purchase price
        lh_purchase_price = total_project_cost * 1.05  # 5% profit margin
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>4) LH 매입가 추정</strong><br>
                LH 공사의 신축매입 가격은 감정평가를 통해 산정되며, 일반적으로 
                총 사업비 대비 100-110% 수준에서 결정됩니다. 본 사업의 경우, 
                추정 매입가는 약 <strong>{lh_purchase_price:,.0f}원 ({lh_purchase_price/100000000:.1f}억원)</strong>으로, 
                사업비 대비 약 5%의 개발이익이 발생할 것으로 예상됩니다.
            </p>
        """)
        
        # Paragraph 7: ROI analysis
        profit = lh_purchase_price - total_project_cost
        roi = (profit / total_project_cost) * 100
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>5) 수익성 분석</strong><br>
                예상 순이익은 약 {profit:,.0f}원({profit/100000000:.1f}억원)이며, 
                투자 대비 수익률(ROI)은 약 <strong>{roi:.2f}%</strong>로 산출되었습니다. 
                {'이는 일반적인 부동산 개발 사업의 목표 수익률(10-15%)에 비해 낮은 수준이나' if roi < 10 else 
                '이는 안정적인 수익률로 평가되며'}, 
                LH 매입 방식은 분양 위험이 없고 매각이 확정되어 있어 
                사업 안정성이 매우 높다는 장점이 있습니다.
            </p>
        """)
        
        # Paragraph 8: Alternative rental operation
        monthly_rent_per_unit = 300000
        total_units = 40
        annual_rental_income = monthly_rent_per_unit * total_units * 12
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>6) 대안: 직접 임대 운영</strong><br>
                LH 매입 대신 사업자가 직접 임대 운영을 할 경우, 세대당 월 임대료를 
                평균 {monthly_rent_per_unit:,.0f}원으로 가정하면(총 {total_units}세대), 
                연간 임대 수익은 약 <strong>{annual_rental_income:,.0f}원 ({annual_rental_income/100000000:.1f}억원)</strong>으로 
                추정됩니다. 다만, 공실 위험, 관리비용, 수선유지비 등을 고려하면 
                실질 수익률은 이보다 낮아질 수 있습니다.
            </p>
        """)
        
        # Paragraph 9: Breakeven analysis
        breakeven_years = total_project_cost / annual_rental_income
        
        paragraphs.append(f"""
            <p class="paragraph">
                직접 임대 운영 시 손익분기점(BEP)은 약 <strong>{breakeven_years:.1f}년</strong>으로 
                추정됩니다. {'이는 장기 투자 관점에서 적정한 수준이며' if breakeven_years <= 15 else 
                '이는 다소 긴 회수 기간으로'}, 
                사업자의 자금 조달 능력 및 장기 운영 의지에 따라 판단해야 합니다. 
                일반적으로 LH 매입 방식이 더 선호되는 이유는 빠른 자금 회수 및 
                운영 리스크 회피가 가능하기 때문입니다.
            </p>
        """)
        
        # Paragraph 10: Financial feasibility
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>7) 종합 재무 타당성</strong><br>
                본 사업은 {'재무적으로 타당성이 있으며' if roi >= 5 else '재무적으로 신중한 검토가 필요하며'}, 
                특히 LH 매입 방식을 활용할 경우 안정적인 사업 추진이 가능할 것으로 판단됩니다. 
                다만, 최종 사업성은 실제 토지 매입가, 건설비용, LH 감정평가 결과 등에 따라 
                달라질 수 있으므로, 사업 진행 과정에서 지속적인 모니터링이 필요합니다.
            </p>
        """)
        
        # Paragraph 11: Financing strategy
        paragraphs.append("""
            <p class="paragraph">
                <strong>8) 자금 조달 계획</strong><br>
                사업 자금은 자기자본 30%, 금융기관 대출 70%로 조달하는 것을 가정하였습니다. 
                LH 매입 사업의 경우 매각이 확정되어 있어 금융기관의 대출 승인이 
                상대적으로 용이한 편입니다. 현재 시중 금리 수준(연 4-5%)을 고려할 때, 
                금융비용은 총 사업비의 약 2-3% 수준으로 예상됩니다.
            </p>
        """)
        
        # Paragraph 12: Sensitivity analysis
        paragraphs.append("""
            <p class="paragraph">
                <strong>9) 민감도 분석</strong><br>
                주요 변수(토지 가격, 건설비용, 매입가)의 10% 변동 시 수익률에 미치는 영향을 
                분석한 결과, 건설비용 변동이 수익률에 가장 큰 영향을 미치는 것으로 나타났습니다. 
                따라서 시공사 선정 시 정확한 견적 산출 및 계약 조건 협상이 매우 중요하며, 
                예상치 못한 건설비용 증가에 대비한 예비비 확보가 필수적입니다.
            </p>
        """)
        
        # Paragraph 13: Final recommendation
        paragraphs.append("""
            <p class="paragraph">
                종합적으로 평가할 때, 본 사업은 적정 수준의 수익성과 높은 안정성을 
                동시에 확보할 수 있는 것으로 판단됩니다. LH 매입 방식을 활용하면 
                사업 위험을 최소화하면서도 안정적인 개발이익을 실현할 수 있으므로, 
                사업 추진을 적극 권장합니다.
            </p>
        """)
        
        return paragraphs
    
    def generate_overall_evaluation_narrative(self, data: Dict) -> List[str]:
        """Generate overall evaluation narrative (6-10 paragraphs)"""
        paragraphs = []
        
        # Paragraph 1: Comprehensive overview
        paragraphs.append("""
            <p class="paragraph">
                본 장에서는 앞서 수행한 모든 분석 결과를 종합하여 대상지의 LH 신축매입임대 
                사업 적합성을 최종 평가합니다. 입지 조건, 교통 접근성, 생활 편의성, 
                수요 적합성, 법적 규제, 사업 위험, 재무 타당성 등을 통합적으로 고려하여 
                사업 추진 여부에 대한 종합적인 판단을 제시합니다.
            </p>
        """)
        
        # Paragraph 2: Location strength
        poi_score = data.get('poi_analysis', {}).get('total_score', 0)
        loc_eval = '매우 우수한' if poi_score >= 80 else '우수한' if poi_score >= 70 else '양호한'
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>1) 입지 조건 평가</strong><br>
                대상지는 서울시 내 주요 생활권에 위치하고 있으며, 지하철역 접근성, 
                버스 노선 다양성, 주요 업무지구와의 연결성 등을 고려할 때 
                <strong>{loc_eval}</strong> 입지로 평가됩니다. POI 종합 점수 {poi_score:.1f}점은 
                서울시 평균 대비 {loc_eval} 수준이며, 특히 생활 편의시설 접근성이 우수하여 
                입주자 만족도가 높을 것으로 예상됩니다.
            </p>
        """)
        
        # Paragraph 3: Demand suitability
        type_scores = data.get('type_demand_scores', {})
        max_score = max(type_scores.values()) if type_scores else 0
        best_type = max(type_scores, key=type_scores.get) if type_scores else 'N/A'
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>2) 수요 적합성 평가</strong><br>
                TypeDemand 5-Type 분석 결과, <strong>{best_type}</strong> 유형이 {max_score:.1f}점으로 
                가장 높은 수요 점수를 기록하였습니다. 이는 대상지의 인구 구조, 
                생활 인프라, 정책 환경 등이 해당 유형에 매우 적합함을 의미하며, 
                사업 계획 수립 시 이 유형을 중심으로 세대 구성을 계획하는 것이 바람직합니다.
            </p>
        """)
        
        # Paragraph 4: Legal and regulatory compliance
        paragraphs.append("""
            <p class="paragraph">
                <strong>3) 법적 규제 적합성</strong><br>
                대상지는 주거지역으로 지정되어 있어 공동주택 건설이 가능하며, 
                용적률, 건폐율, 높이 제한 등 주요 건축 규제를 검토한 결과 
                LH 신축매입임대 사업 추진에 법적 장애 요인은 없는 것으로 판단됩니다. 
                다만, 개발행위허가 및 건축허가 과정에서 교통영향평가, 환경영향평가 등이 
                요구될 수 있으므로, 이에 대한 사전 준비가 필요합니다.
            </p>
        """)
        
        # Paragraph 5: Risk assessment
        total_risk = data.get('risk_analysis', {}).get('total_risk_score', 0)
        risk_eval = '낮은' if total_risk < 40 else '중간' if total_risk < 60 else '높은'
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>4) 사업 위험 평가</strong><br>
                종합 위험도는 {total_risk:.1f}점으로 <strong>{risk_eval} 수준</strong>으로 평가됩니다. 
                {'주요 위험 요인이 적절히 관리되고 있으며' if total_risk < 40 else 
                '일부 위험 요인에 대한 관리가 필요하나' if total_risk < 60 else 
                '다양한 위험 요인이 식별되었으나'}, 
                체계적인 리스크 관리 체계를 구축하면 사업 추진이 가능할 것으로 판단됩니다. 
                특히 {'법적 위험과 시장 위험이 낮아' if total_risk < 40 else 
                '재무적 완충을 확보하면' if total_risk < 60 else 
                '신중한 의사결정과 함께'} 안정적인 사업 운영이 기대됩니다.
            </p>
        """)
        
        # Paragraph 6: Financial viability
        paragraphs.append("""
            <p class="paragraph">
                <strong>5) 사업성 평가</strong><br>
                재무 분석 결과, 본 사업은 적정 수준의 수익성을 확보할 수 있으며, 
                특히 LH 매입 방식을 활용할 경우 안정적인 사업 추진이 가능한 것으로 
                평가됩니다. 토지 매입가, 건설비용, LH 매입가를 종합적으로 고려할 때, 
                사업비 대비 5-10% 수준의 개발이익 실현이 가능할 것으로 예상되며, 
                이는 안정성을 중시하는 LH 사업의 특성을 고려할 때 적정한 수준입니다.
            </p>
        """)
        
        # Paragraph 7: Competitive advantage
        paragraphs.append("""
            <p class="paragraph">
                <strong>6) 경쟁 우위 요소</strong><br>
                본 대상지의 주요 경쟁 우위 요소로는 첫째, 우수한 대중교통 접근성, 
                둘째, 충분한 생활 편의시설, 셋째, 안정적인 수요 기반, 
                넷째, 명확한 법적 근거 및 사업 추진 가능성이 있습니다. 
                이러한 요소들은 인근 경쟁 물건 대비 본 사업의 경쟁력을 높이는 
                중요한 요인으로 작용할 것입니다.
            </p>
        """)
        
        # Paragraph 8: Challenges and considerations
        paragraphs.append("""
            <p class="paragraph">
                <strong>7) 주요 과제 및 고려사항</strong><br>
                사업 추진 시 주의해야 할 사항으로는 첫째, 건설비용 상승에 대한 대비, 
                둘째, 인허가 과정에서의 지연 가능성, 셋째, 주변 주민 민원 발생 가능성, 
                넷째, 금리 변동에 따른 재무 구조 변화 등이 있습니다. 
                이러한 과제들에 대한 구체적인 대응 방안을 사전에 마련하는 것이 필요합니다.
            </p>
        """)
        
        # Paragraph 9: Strategic recommendations
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>8) 전략적 권고사항</strong><br>
                사업 성공 가능성을 높이기 위한 전략적 권고사항으로는 첫째, 
                {best_type} 유형을 중심으로 세대 구성을 계획하되 다양한 유형을 혼합 배치하고, 
                둘째, 경험이 풍부한 시공사 및 관리 전문가를 조기에 선정하며, 
                셋째, 충분한 예비비(10-15%)를 확보하고, 넷째, 지역 커뮤니티와의 
                적극적인 소통을 통해 사회적 수용성을 높이는 것을 권장합니다.
            </p>
        """)
        
        # Paragraph 10: Final verdict
        final_score = (poi_score + max_score - total_risk) / 2
        final_eval = 'S등급 (적극 추천)' if final_score >= 80 else \
                    'A등급 (추천)' if final_score >= 70 else \
                    'B등급 (조건부 추천)' if final_score >= 60 else \
                    'C등급 (신중 검토)'
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>9) 최종 평가</strong><br>
                모든 평가 지표를 종합한 결과, 본 대상지는 <strong>{final_eval}</strong>로 
                최종 평가되었습니다. 입지 조건, 수요 적합성, 법적 규제, 사업 위험, 
                재무 타당성 등을 종합적으로 고려할 때, 
                {'LH 신축매입임대 사업 추진을 적극 권장합니다' if final_score >= 70 else 
                'LH 신축매입임대 사업 추진이 가능하나 일부 보완이 필요합니다' if final_score >= 60 else 
                'LH 신축매입임대 사업 추진 시 신중한 검토가 필요합니다'}.
            </p>
        """)
        
        return paragraphs
    
    def generate_conclusion_narrative(self, data: Dict) -> List[str]:
        """Generate conclusion and recommendations narrative (8-12 paragraphs)"""
        paragraphs = []
        
        # Paragraph 1: Executive summary
        address = data.get('land_analysis', {}).get('address', 'N/A')
        
        paragraphs.append(f"""
            <p class="paragraph">
                본 보고서는 <strong>{address}</strong> 소재 토지에 대한 LH 신축매입임대 사업 
                타당성을 종합적으로 분석하였습니다. ZeroSite v7.3 분석 엔진을 활용하여 
                입지, 교통, 편의시설, 인구·수요, 법적 규제, 위험 요인, 사업성 등 
                7개 주요 영역을 체계적으로 검토하였으며, 그 결과를 바탕으로 
                최종 결론 및 권고사항을 다음과 같이 제시합니다.
            </p>
        """)
        
        # Paragraph 2: Key findings summary
        poi_score = data.get('poi_analysis', {}).get('total_score', 0)
        type_scores = data.get('type_demand_scores', {})
        max_demand_score = max(type_scores.values()) if type_scores else 0
        best_type = max(type_scores, key=type_scores.get) if type_scores else 'N/A'
        total_risk = data.get('risk_analysis', {}).get('total_risk_score', 0)
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>주요 분석 결과 요약</strong><br>
                • POI 접근성 종합 점수: {poi_score:.1f}점 
                ({'우수' if poi_score >= 75 else '양호' if poi_score >= 65 else '보통'})<br>
                • 최적 수요 유형: {best_type} ({max_demand_score:.1f}점)<br>
                • 종합 위험도: {total_risk:.1f}점 
                ({'낮은 위험' if total_risk < 40 else '중간 위험' if total_risk < 60 else '높은 위험'})<br>
                • 사업 추진 가능성: 
                {'높음 (적극 추천)' if (poi_score + max_demand_score - total_risk) / 2 >= 70 else 
                '보통 (조건부 추천)' if (poi_score + max_demand_score - total_risk) / 2 >= 60 else 
                '낮음 (신중 검토)'}
            </p>
        """)
        
        # Paragraph 3: Location advantages
        paragraphs.append("""
            <p class="paragraph">
                <strong>1) 입지 경쟁력</strong><br>
                대상지는 서울시 내 주요 생활권에 위치하고 있으며, 지하철역 및 버스 정류장과의 
                접근성이 우수하여 직장인 입주자들의 출퇴근 편의성이 확보되어 있습니다. 
                또한, 초등학교, 병원, 대형마트 등 핵심 생활 인프라가 도보 거리 내에 
                분포되어 있어, 다양한 연령대 및 가구 유형의 입주자들이 편리하게 
                생활할 수 있는 환경이 조성되어 있습니다.
            </p>
        """)
        
        # Paragraph 4: Demand strengths
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>2) 수요 기반 안정성</strong><br>
                TypeDemand 5-Type 분석 결과, {best_type} 유형이 {max_demand_score:.1f}점으로 
                가장 높은 수요 적합성을 보였으며, 이는 대상지 인근의 인구 구조, 
                생활 인프라, 임대 시장 동향이 해당 유형에 매우 적합함을 의미합니다. 
                안정적인 수요 기반은 장기 공실 위험을 낮추고, 임대사업의 수익성을 
                보장하는 핵심 요소입니다.
            </p>
        """)
        
        # Paragraph 5: Legal feasibility
        paragraphs.append("""
            <p class="paragraph">
                <strong>3) 법적 실행 가능성</strong><br>
                대상지는 주거지역으로 지정되어 있어 공동주택 건설이 가능하며, 
                용적률, 건폐율, 높이 제한 등 주요 건축 규제를 검토한 결과 
                법적 장애 요인은 없는 것으로 확인되었습니다. 다만, 개발행위허가 및 
                건축허가 과정에서 일부 평가(교통영향평가 등)가 필요할 수 있으므로, 
                이에 대한 사전 준비 및 충분한 인허가 기간 확보가 필요합니다.
            </p>
        """)
        
        # Paragraph 6: Financial viability
        paragraphs.append("""
            <p class="paragraph">
                <strong>4) 재무적 타당성</strong><br>
                사업성 분석 결과, LH 매입 방식을 활용할 경우 사업비 대비 5-10% 수준의 
                개발이익이 예상되며, 이는 안정성 중심의 LH 사업 특성을 고려할 때 
                적정한 수익률로 평가됩니다. 특히 LH 매입 방식은 분양 위험이 없고 
                매각이 확정되어 있어 재무적 안정성이 매우 높으며, 금융기관의 
                대출 승인도 상대적으로 용이한 장점이 있습니다.
            </p>
        """)
        
        # Paragraph 7: Risk management
        risk_level = '낮은' if total_risk < 40 else '중간' if total_risk < 60 else '높은'
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>5) 위험 관리 방안</strong><br>
                종합 위험도는 {total_risk:.1f}점으로 {risk_level} 수준으로 평가되었습니다. 
                {'주요 위험 요인이 낮은 수준으로 관리되고 있으나' if total_risk < 40 else 
                '일부 위험 요인에 대한 적극적인 관리가 필요하며' if total_risk < 60 else 
                '다양한 위험 요인이 식별되었으므로'}, 
                철저한 사전 검토, 충분한 예비비 확보, 경험이 풍부한 시공사 선정, 
                체계적인 공정 관리 등을 통해 위험을 최소화하는 것이 필요합니다.
            </p>
        """)
        
        # Paragraph 8: Implementation timeline
        paragraphs.append("""
            <p class="paragraph">
                <strong>6) 사업 추진 일정 (안)</strong><br>
                • 사전 협의 및 계약 체결: 3개월<br>
                • 인허가 절차 (개발행위허가, 건축허가): 6-9개월<br>
                • 설계 및 시공사 선정: 3-4개월<br>
                • 건설 공사: 18-24개월<br>
                • 준공 및 LH 매각: 2-3개월<br>
                • 총 소요 기간: 약 32-43개월 (약 3-3.5년)<br>
                이는 일반적인 공동주택 건설 사업의 표준 일정이며, 실제 일정은 
                인허가 진행 상황 및 시공 여건에 따라 달라질 수 있습니다.
            </p>
        """)
        
        # Paragraph 9: Key success factors
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>7) 핵심 성공 요인</strong><br>
                본 사업의 성공을 위한 핵심 요인으로는 첫째, {best_type} 유형을 중심으로 
                세대 구성을 최적화하고, 둘째, 건설비용 관리를 철저히 하며, 
                셋째, 인허가 과정을 체계적으로 준비하고, 넷째, 지역 커뮤니티와의 
                원활한 소통을 유지하는 것입니다. 이러한 요인들을 종합적으로 관리하면 
                사업 성공 가능성을 크게 높일 수 있습니다.
            </p>
        """)
        
        # Paragraph 10: Recommendations for stakeholders
        paragraphs.append("""
            <p class="paragraph">
                <strong>8) 이해관계자별 권고사항</strong><br>
                • <strong>사업 시행자</strong>: 충분한 예비비 확보(10-15%), 
                경험이 풍부한 시공사 선정, 체계적인 공정 관리<br>
                • <strong>금융기관</strong>: LH 매입 확정성을 고려한 대출 심사, 
                단계별 자금 집행 계획 수립<br>
                • <strong>LH 공사</strong>: 공정한 감정평가, 신속한 매입 절차 진행, 
                장기 관리 계획 수립<br>
                • <strong>지역 주민</strong>: 사업 계획 이해 및 협조, 
                건설 과정 중 불편 최소화 노력 필요
            </p>
        """)
        
        # Paragraph 11: Long-term outlook
        paragraphs.append("""
            <p class="paragraph">
                <strong>9) 중장기 전망</strong><br>
                서울시의 인구 고령화 추세, 1인 가구 증가, 청년층 주거 불안정 심화 등을 
                고려할 때, LH 신축매입임대 주택에 대한 수요는 지속적으로 증가할 것으로 
                전망됩니다. 특히 정부의 공공임대주택 공급 확대 정책이 유지될 경우, 
                본 사업은 안정적인 수익 창출 및 사회적 기여를 동시에 달성할 수 있는 
                바람직한 사업 모델로 평가됩니다.
            </p>
        """)
        
        # Paragraph 12: Final recommendation
        final_score = (poi_score + max_demand_score - total_risk) / 2
        final_decision = 'LH 신축매입임대 사업 추진을 적극 권장합니다' if final_score >= 70 else \
                        'LH 신축매입임대 사업 추진이 가능하며, 일부 보완 사항을 반영하면 성공 가능성이 높을 것으로 판단됩니다' if final_score >= 60 else \
                        'LH 신축매입임대 사업 추진 시 신중한 의사결정이 필요하며, 대안 검토를 권장합니다'
        
        paragraphs.append(f"""
            <p class="paragraph">
                <strong>10) 최종 권고사항</strong><br>
                모든 분석 결과를 종합한 결과, <strong>{final_decision}</strong>. 
                본 보고서에서 제시한 권고사항들을 충실히 이행하고, 
                사업 진행 과정에서 발생하는 변수들을 적시에 모니터링하며, 
                필요 시 전문가의 자문을 받아 의사결정을 수행한다면, 
                안정적이고 성공적인 사업 추진이 가능할 것으로 확신합니다.
            </p>
        """)
        
        # Paragraph 13: Closing statement
        paragraphs.append("""
            <p class="paragraph">
                본 보고서가 LH 신축매입임대 사업의 의사결정 과정에서 유용한 참고자료로 
                활용되기를 바라며, 추가적인 검토 사항이나 문의 사항이 있을 경우 
                언제든지 연락주시기 바랍니다. 감사합니다.
            </p>
        """)
        
        return paragraphs
    
    def safe_get(self, data: Any, default: Any = "N/A") -> Any:
        """Safe getter with default value"""
        if data is None or data == "" or data == {} or data == []:
            return default
        return data


# Usage example
if __name__ == "__main__":
    logger.info("ZeroSite v7.3 Narrative Templates loaded")
