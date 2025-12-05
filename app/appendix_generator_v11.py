"""
ZeroSite v11.0 - Appendix Generator
====================================
보고서 부록 자동 생성 엔진

목적: 데이터 출처, 참고 문헌, LH 기준, 면책 조항 등 부록 섹션 생성
- Data source documentation
- LH criteria references
- Pseudo-data disclaimer
- Methodology explanation

Author: ZeroSite Team  
Date: 2025-12-05
"""

from typing import Dict, Any, List
from datetime import datetime


class AppendixGenerator:
    """
    보고서 부록 HTML 생성 엔진
    
    생성 섹션:
    1. 데이터 출처 및 참고 자료
    2. LH 평가 기준 상세
    3. 면책 조항 (Pseudo-Data 명시)
    4. 분석 방법론
    5. 용어 설명
    """
    
    def __init__(self):
        self.generation_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    def generate_full_appendix(self) -> str:
        """전체 부록 HTML 생성"""
        html = f"""
        <div class="appendix-section">
            <h2 class="appendix-title">부록 (Appendix)</h2>
            
            {self._generate_data_sources()}
            {self._generate_lh_criteria()}
            {self._generate_disclaimer()}
            {self._generate_methodology()}
            {self._generate_glossary()}
            {self._generate_references()}
            
        </div>
        
        {self._generate_appendix_styles()}
        """
        
        return html
    
    # ========================================================================
    # 1. Data Sources
    # ========================================================================
    
    def _generate_data_sources(self) -> str:
        """데이터 출처 및 참고 자료"""
        return """
        <div class="appendix-subsection">
            <h3>📚 데이터 출처 및 참고 자료</h3>
            
            <h4>1. 공공 데이터</h4>
            <ul class="data-source-list">
                <li>
                    <strong>국토교통부</strong> - 주택 정책, 용도지역 정보
                    <br><span class="source-url">https://www.molit.go.kr</span>
                </li>
                <li>
                    <strong>한국토지주택공사 (LH)</strong> - 신축매입임대 사업 기준
                    <br><span class="source-url">https://www.lh.or.kr</span>
                </li>
                <li>
                    <strong>통계청 (KOSIS)</strong> - 인구 통계, 가구 구성 데이터
                    <br><span class="source-url">https://kosis.kr</span>
                </li>
                <li>
                    <strong>서울 열린데이터 광장</strong> - 서울시 지역 통계
                    <br><span class="source-url">https://data.seoul.go.kr</span>
                </li>
                <li>
                    <strong>부동산 공시가격 시스템</strong> - 토지 감정가, 공시지가
                    <br><span class="source-url">https://www.realtyprice.kr</span>
                </li>
            </ul>
            
            <h4>2. 지도 및 위치 정보</h4>
            <ul class="data-source-list">
                <li>
                    <strong>카카오맵 API</strong> - 주소 좌표 변환, 거리 계산
                    <br><span class="source-note">(향후 연동 예정)</span>
                </li>
                <li>
                    <strong>네이버 지도 API</strong> - 주변 편의시설 검색
                    <br><span class="source-note">(향후 연동 예정)</span>
                </li>
                <li>
                    <strong>공공 데이터 포털</strong> - 교통 정보, 학교 위치
                    <br><span class="source-url">https://www.data.go.kr</span>
                </li>
            </ul>
            
            <h4>3. 금융 및 시장 정보</h4>
            <ul class="data-source-list">
                <li>
                    <strong>한국은행 경제통계시스템</strong> - 금리, 경제 지표
                    <br><span class="source-url">https://ecos.bok.or.kr</span>
                </li>
                <li>
                    <strong>부동산114, KB국민은행</strong> - 시장 시세, 거래 동향
                    <br><span class="source-note">(참고용)</span>
                </li>
            </ul>
        </div>
        """
    
    # ========================================================================
    # 2. LH Criteria
    # ========================================================================
    
    def _generate_lh_criteria(self) -> str:
        """LH 평가 기준 상세"""
        return """
        <div class="appendix-subsection">
            <h3>📊 LH 신축매입임대 평가 기준 상세</h3>
            
            <p class="criteria-intro">
                본 보고서의 LH 100점 점수 체계는 다음 공식 기준을 반영하여 설계되었습니다.
            </p>
            
            <h4>1. 입지 적합성 (Location Suitability) - 25점</h4>
            <table class="criteria-table">
                <thead>
                    <tr>
                        <th>평가 항목</th>
                        <th>배점</th>
                        <th>평가 기준</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>교통 접근성</td>
                        <td>10점</td>
                        <td>
                            • 지하철역 500m 이내: 10점<br>
                            • 지하철역 500-1km: 7점<br>
                            • 지하철역 1km 이상: 4점<br>
                            • 버스노선 접근성 추가 고려
                        </td>
                    </tr>
                    <tr>
                        <td>생활 편의성</td>
                        <td>8점</td>
                        <td>
                            • 대형마트, 병원, 은행 등 1km 이내<br>
                            • 편의시설 밀집도<br>
                            • 문화·체육 시설 접근성
                        </td>
                    </tr>
                    <tr>
                        <td>교육 환경</td>
                        <td>7점</td>
                        <td>
                            • 초등학교 500m 이내<br>
                            • 중학교 1km 이내<br>
                            • 고등학교, 대학 접근성
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <h4>2. 사업 타당성 (Business Feasibility) - 30점</h4>
            <table class="criteria-table">
                <thead>
                    <tr>
                        <th>평가 항목</th>
                        <th>배점</th>
                        <th>평가 기준</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>용적률/건폐율 적정성</td>
                        <td>10점</td>
                        <td>
                            • 법정 한도 내 최적 활용<br>
                            • 용적률 150% 이상 권장<br>
                            • 건폐율 60% 이하
                        </td>
                    </tr>
                    <tr>
                        <td>세대수 적정성</td>
                        <td>8점</td>
                        <td>
                            • 최소 30세대 이상 (필수)<br>
                            • 50세대 이상 우대<br>
                            • 단지 규모 적정성
                        </td>
                    </tr>
                    <tr>
                        <td>토지 가격 적정성</td>
                        <td>12점</td>
                        <td>
                            • 토지비 < 총 투자비 60%<br>
                            • 감정가 기준 LH 매입가 산정<br>
                            • 주변 시세 대비 적정성
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <h4>3. 정책 정합성 (Policy Alignment) - 20점</h4>
            <table class="criteria-table">
                <tbody>
                    <tr>
                        <td>용도지역 적합성</td>
                        <td>8점</td>
                        <td>
                            • 주거지역 우선<br>
                            • 제2종 일반주거지역 이상<br>
                            • 개발제한구역 제외
                        </td>
                    </tr>
                    <tr>
                        <td>주택 정책 부합도</td>
                        <td>7점</td>
                        <td>
                            • 공공주택 우선 공급 지역<br>
                            • 주거복지 로드맵 부합<br>
                            • 지역 특화 정책 연계
                        </td>
                    </tr>
                    <tr>
                        <td>공급 유형 적합성</td>
                        <td>5점</td>
                        <td>
                            • 청년형, 신혼형 우선<br>
                            • 지역 수요 맞춤형<br>
                            • LH 공급 목표 부합
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <h4>4. 재무 건전성 (Financial Soundness) - 15점</h4>
            <table class="criteria-table">
                <tbody>
                    <tr>
                        <td>IRR/ROI 수준</td>
                        <td>8점</td>
                        <td>
                            • IRR 3.0% 이상: 8점<br>
                            • IRR 2.0-3.0%: 5점<br>
                            • IRR 2.0% 미만: 0점 (사업 불가)
                        </td>
                    </tr>
                    <tr>
                        <td>투자 회수 기간</td>
                        <td>4점</td>
                        <td>
                            • 10년 이내 회수 가능성<br>
                            • LH 임대료 수입 안정성<br>
                            • 운영 비용 관리
                        </td>
                    </tr>
                    <tr>
                        <td>자금 조달 가능성</td>
                        <td>3점</td>
                        <td>
                            • PF 대출 가능성<br>
                            • 자기자본 비율<br>
                            • 금융 건전성
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <h4>5. 리스크 수준 (Risk Level) - 10점</h4>
            <table class="criteria-table">
                <tbody>
                    <tr>
                        <td>법규 리스크</td>
                        <td>4점</td>
                        <td>
                            • 인허가 승인 가능성<br>
                            • 규제 준수 여부<br>
                            • 민원 발생 가능성
                        </td>
                    </tr>
                    <tr>
                        <td>시장 리스크</td>
                        <td>3점</td>
                        <td>
                            • 수요 변동성<br>
                            • 경쟁 프로젝트<br>
                            • 임대료 수준
                        </td>
                    </tr>
                    <tr>
                        <td>사업 리스크</td>
                        <td>3점</td>
                        <td>
                            • 공사 기간 지연<br>
                            • 비용 증가 가능성<br>
                            • 기타 예상 리스크
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <div class="criteria-note">
                <strong>참고:</strong> 상기 기준은 LH 공식 기준을 참고하여 ZeroSite v11.0 엔진에서 
                정량화한 것으로, 실제 LH 심사 시 추가 요인이 고려될 수 있습니다.
            </div>
        </div>
        """
    
    # ========================================================================
    # 3. Disclaimer
    # ========================================================================
    
    def _generate_disclaimer(self) -> str:
        """면책 조항 및 데이터 명시"""
        return f"""
        <div class="appendix-subsection disclaimer-section">
            <h3>⚠️ 면책 조항 (Disclaimer)</h3>
            
            <h4>1. Pseudo-Data 사용 안내</h4>
            <div class="warning-box">
                <p>
                    <strong>본 보고서는 ZeroSite v11.0 엔진이 자동 생성한 데이터를 기반으로 작성되었습니다.</strong>
                </p>
                <p>
                    일부 데이터는 <strong>Pseudo-Data (모의 데이터)</strong>로, 다음 항목이 포함됩니다:
                </p>
                <ul>
                    <li>주변 편의시설 목록 및 거리</li>
                    <li>인구 통계 및 가구 구성 비율</li>
                    <li>교통 시설 접근성 데이터</li>
                    <li>교육 시설 분포 정보</li>
                </ul>
                <p>
                    <strong style="color: #e74c3c;">
                        ⚠️ 실제 LH 제출용 보고서 작성 시, 반드시 공식 데이터 소스를 통해 
                        모든 데이터를 검증하고 업데이트해야 합니다.
                    </strong>
                </p>
            </div>
            
            <h4>2. 데이터 검증 필수 항목</h4>
            <table class="verification-table">
                <thead>
                    <tr>
                        <th>항목</th>
                        <th>확인 방법</th>
                        <th>공식 소스</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>주소 및 지번</td>
                        <td>등기부등본, 토지대장</td>
                        <td>대법원 인터넷등기소</td>
                    </tr>
                    <tr>
                        <td>토지 감정가</td>
                        <td>감정평가서</td>
                        <td>감정평가법인</td>
                    </tr>
                    <tr>
                        <td>용도지역</td>
                        <td>토지이용계획확인원</td>
                        <td>정부24, 해당 지자체</td>
                    </tr>
                    <tr>
                        <td>인구 통계</td>
                        <td>주민등록인구통계</td>
                        <td>통계청 KOSIS</td>
                    </tr>
                    <tr>
                        <td>교통 시설</td>
                        <td>현장 실측</td>
                        <td>지자체 교통 정보</td>
                    </tr>
                    <tr>
                        <td>편의시설</td>
                        <td>현장 조사</td>
                        <td>카카오맵/네이버지도</td>
                    </tr>
                    <tr>
                        <td>학교 정보</td>
                        <td>학교알리미</td>
                        <td>교육부 학교정보공시</td>
                    </tr>
                </tbody>
            </table>
            
            <h4>3. 사용 제한 사항</h4>
            <ul class="limitation-list">
                <li>
                    본 보고서는 <strong>참고용</strong>으로, 법적 효력이 없습니다.
                </li>
                <li>
                    LH 제출 전 <strong>전문가 검토</strong>를 반드시 받아야 합니다.
                </li>
                <li>
                    재무 분석 결과는 <strong>추정치</strong>로, 실제 결과와 다를 수 있습니다.
                </li>
                <li>
                    리스크 평가는 <strong>일반적인 기준</strong>으로, 개별 상황을 완전히 반영하지 못할 수 있습니다.
                </li>
                <li>
                    최종 의사결정은 <strong>실사 및 전문가 자문</strong>을 거쳐야 합니다.
                </li>
            </ul>
            
            <h4>4. 책임 제한</h4>
            <div class="liability-box">
                <p>
                    ZeroSite는 본 보고서의 정확성, 완전성, 적시성에 대해 보증하지 않으며,
                    본 보고서 사용으로 인한 직간접적 손해에 대해 책임을 지지 않습니다.
                </p>
                <p>
                    사용자는 본 보고서를 참고 자료로만 활용하며, 최종 결정은 
                    독자적인 판단과 전문가 자문을 통해 이루어져야 합니다.
                </p>
            </div>
        </div>
        """
    
    # ========================================================================
    # 4. Methodology
    # ========================================================================
    
    def _generate_methodology(self) -> str:
        """분석 방법론"""
        return """
        <div class="appendix-subsection">
            <h3>🔬 분석 방법론</h3>
            
            <h4>1. LH 점수 산정 방식</h4>
            <p>
                ZeroSite v11.0은 5개 평가 영역(입지/사업/정책/재무/리스크)에 걸쳐 
                총 15개 세부 항목을 100점 만점으로 정량화합니다.
            </p>
            <ul>
                <li><strong>가중 평균 방식:</strong> 각 항목의 배점에 따라 가중치 적용</li>
                <li><strong>정규화:</strong> 0-100 범위로 점수 정규화</li>
                <li><strong>등급 산정:</strong> A(90+), B(80-89), C(70-79), D(60-69), F(<60)</li>
            </ul>
            
            <h4>2. 세대유형 적합도 분석</h4>
            <p>
                5개 세대유형(청년/신혼/고령자/일반/취약계층)에 대해 
                6개 평가 기준(인구/교통/생활/정책/경제/사회)을 종합 평가합니다.
            </p>
            <ul>
                <li><strong>다기준 의사결정 (MCDM):</strong> 각 기준별 점수를 통합</li>
                <li><strong>매트릭스 분석:</strong> 5×6 매트릭스로 시각화</li>
                <li><strong>최적 유형 추천:</strong> 종합 점수 기반 1순위 추천</li>
            </ul>
            
            <h4>3. 재무 분석 모델</h4>
            <p>
                IRR(내부수익률), ROI(투자수익률)을 기반으로 10년 장기 수익성을 분석합니다.
            </p>
            <ul>
                <li><strong>현금흐름 분석:</strong> 연간 임대 수입 - 운영 비용</li>
                <li><strong>할인율:</strong> 시장 금리 + 리스크 프리미엄</li>
                <li><strong>회수 기간:</strong> 누적 현금흐름 기준</li>
            </ul>
            
            <h4>4. 리스크 평가 매트릭스</h4>
            <p>
                6개 리스크 유형을 6개 평가 항목(발생가능성/영향도/대응난이도/비용/일정/종합)으로 
                36-cell 매트릭스 분석을 수행합니다.
            </p>
            <ul>
                <li><strong>리스크 등급:</strong> Critical/High/Medium/Low/None</li>
                <li><strong>색상 코딩:</strong> 빨강(치명적) → 녹색(낮음)</li>
                <li><strong>대응 전략:</strong> 각 리스크별 완화 방안 제시</li>
            </ul>
        </div>
        """
    
    # ========================================================================
    # 5. Glossary
    # ========================================================================
    
    def _generate_glossary(self) -> str:
        """용어 설명"""
        return """
        <div class="appendix-subsection">
            <h3>📖 용어 설명</h3>
            
            <table class="glossary-table">
                <tbody>
                    <tr>
                        <td class="term">신축매입임대</td>
                        <td>LH가 민간이 신축한 주택을 매입하여 저소득층에게 시세의 30~80% 수준으로 임대하는 공공임대주택 제도</td>
                    </tr>
                    <tr>
                        <td class="term">IRR (Internal Rate of Return)</td>
                        <td>내부수익률. 투자 프로젝트의 현금흐름을 현재가치로 환산했을 때 순현재가치(NPV)가 0이 되는 할인율</td>
                    </tr>
                    <tr>
                        <td class="term">ROI (Return on Investment)</td>
                        <td>투자수익률. (순이익 / 투자금액) × 100으로 계산되는 투자 효율성 지표</td>
                    </tr>
                    <tr>
                        <td class="term">용적률 (FAR)</td>
                        <td>대지면적에 대한 연면적의 비율. 높을수록 건물을 높게 지을 수 있음</td>
                    </tr>
                    <tr>
                        <td class="term">건폐율 (BCR)</td>
                        <td>대지면적에 대한 건축면적의 비율. 법정 한도 내에서 건축 가능</td>
                    </tr>
                    <tr>
                        <td class="term">감정가</td>
                        <td>감정평가법인이 평가한 부동산 가격. LH 매입가 산정의 기준</td>
                    </tr>
                    <tr>
                        <td class="term">청년형</td>
                        <td>대학생, 사회초년생 등 만 19~39세 청년을 대상으로 하는 공급 유형</td>
                    </tr>
                    <tr>
                        <td class="term">신혼형</td>
                        <td>결혼 7년 이내 또는 예정 부부를 대상으로 하는 공급 유형</td>
                    </tr>
                    <tr>
                        <td class="term">고령자형</td>
                        <td>만 65세 이상 고령자를 대상으로 하는 공급 유형</td>
                    </tr>
                    <tr>
                        <td class="term">일반형</td>
                        <td>특정 대상 제한 없이 소득 기준으로만 공급하는 유형</td>
                    </tr>
                    <tr>
                        <td class="term">취약계층형</td>
                        <td>저소득층, 장애인, 국가유공자 등 주거 취약계층 대상 공급 유형</td>
                    </tr>
                    <tr>
                        <td class="term">Pseudo-Data</td>
                        <td>모의 데이터. 실제 데이터 대신 알고리즘으로 생성한 현실적인 데이터</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
    
    # ========================================================================
    # 6. References
    # ========================================================================
    
    def _generate_references(self) -> str:
        """참고 문헌"""
        return f"""
        <div class="appendix-subsection">
            <h3>📚 참고 문헌</h3>
            
            <ol class="references-list">
                <li>
                    한국토지주택공사 (2024). 신축매입임대주택 업무처리지침. LH.
                </li>
                <li>
                    국토교통부 (2024). 주택법 시행령 및 시행규칙.
                </li>
                <li>
                    통계청 (2024). 인구주택총조사. KOSIS.
                </li>
                <li>
                    서울특별시 (2024). 서울시 주거복지 기본계획.
                </li>
                <li>
                    한국감정원 (2024). 부동산 시장 동향 분석.
                </li>
                <li>
                    국토연구원 (2023). 공공임대주택 정책 연구보고서.
                </li>
            </ol>
            
            <div class="report-footer">
                <hr>
                <p style="text-align: center; color: #666; margin-top: 20px;">
                    <strong>보고서 생성 정보</strong><br>
                    생성일: {self.generation_date}<br>
                    생성 시스템: ZeroSite v11.0 Ultra Professional<br>
                    엔진 버전: Phase 2 Complete<br>
                    <br>
                    <em>본 보고서는 자동 생성되었으며, 실제 제출 전 전문가 검토가 필요합니다.</em>
                </p>
            </div>
        </div>
        """
    
    # ========================================================================
    # 7. Styles
    # ========================================================================
    
    def _generate_appendix_styles(self) -> str:
        """부록 스타일 CSS"""
        return """
        <style>
        .appendix-section {
            margin: 50px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .appendix-title {
            font-size: 28px;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        
        .appendix-subsection {
            background: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .appendix-subsection h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 20px;
            border-left: 4px solid #3498db;
            padding-left: 12px;
        }
        
        .appendix-subsection h4 {
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 16px;
        }
        
        .data-source-list {
            list-style: none;
            padding: 0;
        }
        
        .data-source-list li {
            margin-bottom: 15px;
            padding: 12px;
            background: #f8f9fa;
            border-left: 3px solid #3498db;
            border-radius: 4px;
        }
        
        .source-url {
            color: #3498db;
            font-size: 13px;
            font-family: monospace;
        }
        
        .source-note {
            color: #7f8c8d;
            font-size: 13px;
            font-style: italic;
        }
        
        .criteria-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        .criteria-table th,
        .criteria-table td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }
        
        .criteria-table th {
            background: #34495e;
            color: white;
            font-weight: 600;
            font-size: 13px;
        }
        
        .criteria-table td:nth-child(2) {
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
        }
        
        .criteria-table td:nth-child(3) {
            font-size: 13px;
            color: #555;
            line-height: 1.6;
        }
        
        .criteria-note {
            margin-top: 20px;
            padding: 15px;
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .disclaimer-section {
            border: 2px solid #e74c3c;
        }
        
        .warning-box {
            padding: 20px;
            background: #fff5f5;
            border: 2px solid #e74c3c;
            border-radius: 6px;
            margin: 15px 0;
        }
        
        .warning-box p {
            margin: 10px 0;
            line-height: 1.6;
        }
        
        .verification-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        .verification-table th,
        .verification-table td {
            padding: 10px;
            border: 1px solid #ddd;
            font-size: 13px;
        }
        
        .verification-table th {
            background: #e74c3c;
            color: white;
        }
        
        .limitation-list {
            list-style-type: none;
            padding: 0;
        }
        
        .limitation-list li {
            padding: 10px;
            margin: 8px 0;
            background: #f8f9fa;
            border-left: 3px solid #e67e22;
            border-radius: 4px;
        }
        
        .liability-box {
            padding: 15px;
            background: #f8f9fa;
            border: 2px solid #95a5a6;
            border-radius: 4px;
            margin-top: 15px;
            font-size: 13px;
            line-height: 1.6;
        }
        
        .glossary-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .glossary-table td {
            padding: 12px;
            border: 1px solid #ddd;
        }
        
        .glossary-table .term {
            width: 200px;
            background: #ecf0f1;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .references-list {
            padding-left: 25px;
        }
        
        .references-list li {
            margin-bottom: 12px;
            line-height: 1.6;
        }
        
        .report-footer {
            margin-top: 40px;
        }
        
        .report-footer hr {
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }
        </style>
        """


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    print("✅ Appendix Generator v11.0 Module Loaded")
    print("="*60)
    
    # Test
    generator = AppendixGenerator()
    
    appendix_html = generator.generate_full_appendix()
    print(f"✅ Full Appendix Generated: {len(appendix_html):,} characters")
    
    print("\n" + "="*60)
    print("✅ Appendix Generator Test Complete")
