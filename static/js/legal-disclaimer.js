/**
 * ZeroSite Decision OS - Legal Disclaimer System
 * 
 * 목적: 공공 SaaS 법적 리스크 관리 및 책임 범위 명시
 * 작성일: 2026-01-12
 * 버전: 1.0
 */

const LegalDisclaimerSystem = {
    /**
     * 책임 및 한계 고지 텍스트
     */
    disclaimers: {
        // Landing Page용
        landing: {
            title: "서비스 이용 안내",
            icon: "ℹ️",
            content: `
                <p><strong>ZeroSite Decision OS</strong>는 LH 신축매입임대 사업의 의사결정을 보조하는 도구입니다.</p>
                <p>본 시스템은 토지·건축·사업성·커뮤니티 분석을 통해 <strong>GO / CONDITIONAL / NO-GO</strong> 판단 근거를 제공합니다.</p>
                <ul class="legal-disclaimer-list">
                    <li>최종 사업 결정은 발주기관(LH 등) 및 인허가권자의 검토 및 승인에 따릅니다.</li>
                    <li>본 시스템의 분석 결과는 법적·재무적 책임을 대체하지 않습니다.</li>
                    <li>실제 사업 추진 시 전문가(감정평가사, 건축사, 회계사 등)의 검증을 권장합니다.</li>
                </ul>
            `,
            footer: "문의: ZeroSite Decision OS Support Team"
        },
        
        // M6 Dashboard용
        dashboard: {
            title: "판단 결과 이용 안내",
            icon: "⚠️",
            content: `
                <p>본 종합 판단 결과는 <strong>M1~M7 모듈의 분석</strong>을 기반으로 생성되었습니다.</p>
                <p><strong>GO / CONDITIONAL / NO-GO</strong> 판단은 참고용이며, 최종 사업 결정은 다음 주체의 검토가 필요합니다:</p>
                <ul class="legal-disclaimer-list">
                    <li><strong>발주기관</strong>: LH, 지자체 등 공공주택 사업 주관 기관</li>
                    <li><strong>인허가권자</strong>: 건축 인허가, 도시계획 변경 등 관할 기관</li>
                    <li><strong>전문가</strong>: 감정평가사, 건축사, 회계사, 법무사 등</li>
                </ul>
                <p><strong>ZeroSite는 의사결정 보조 도구</strong>로서, 법적·재무적 책임을 대체하지 않습니다.</p>
            `
        },
        
        // PDF용 (표지 하단)
        pdfCover: {
            text: `본 보고서는 ZeroSite Decision OS가 생성한 의사결정 보조 자료입니다.
최종 사업 결정은 발주기관 및 인허가권자의 검토 및 승인에 따릅니다.`
        },
        
        // PDF용 (부록 전체 페이지)
        pdfAppendix: {
            title: "책임 및 한계 고지 (Legal Disclaimer)",
            sections: [
                {
                    heading: "1. 서비스의 성격",
                    content: `ZeroSite Decision OS(이하 "본 시스템")는 LH 신축매입임대 사업의 사전 검토 및 의사결정을 보조하는 분석 도구입니다. 본 시스템은 토지 현황(M1), 매입 적정성(M2), 공급유형(M3), 건축 규모(M4), 사업성·리스크(M5), 커뮤니티 계획(M7), 종합 판단(M6)을 통해 GO/CONDITIONAL/NO-GO 판단 근거를 제공합니다.`
                },
                {
                    heading: "2. 책임의 범위",
                    content: `본 시스템의 분석 결과는 참고용 자료이며, 다음 사항에 대해 법적·재무적 책임을 지지 않습니다:
• 최종 사업 추진 여부 및 방식에 대한 결정
• 발주기관(LH 등)의 사업 승인 및 계약 체결
• 인허가권자의 건축 인허가 및 도시계획 변경 승인
• 감정평가, 설계, 시공, 분양, 운영 등 사업 전 과정의 리스크
• 시장 변화, 법령 개정, 정책 변경 등 외부 환경 변동
• 민원, 분쟁, 소송 등 법적 문제 발생 시 결과`
                },
                {
                    heading: "3. 최종 결정 주체",
                    content: `본 시스템의 분석 결과를 활용한 실제 사업 추진은 다음 주체의 검토 및 승인이 필수적입니다:
• 발주기관: LH(한국토지주택공사), 지자체 등 공공주택 사업 주관 기관
• 인허가권자: 건축 인허가, 도시계획 변경, 환경영향평가 등 관할 기관
• 전문가: 감정평가사, 건축사, 회계사, 법무사, 세무사 등 관련 전문가`
                },
                {
                    heading: "4. 데이터의 정확성",
                    content: `본 시스템은 공공 API(V-World, Kakao 등) 및 사용자 입력 데이터를 기반으로 분석합니다. 데이터의 정확성 및 최신성은 출처에 의존하며, 다음 사항에 유의하시기 바랍니다:
• M1 FACT FREEZE 이후 데이터 변경 사항은 반영되지 않습니다.
• 공공 API 데이터는 실시간 변동 가능성이 있습니다.
• 사용자 입력 데이터의 정확성은 입력자 책임입니다.
• 실제 사업 추진 전 현장 실사 및 전문가 검증을 권장합니다.`
                },
                {
                    heading: "5. 서비스 변경 및 중단",
                    content: `본 시스템의 기능, 분석 방법론, 판단 기준 등은 사전 고지 없이 변경될 수 있습니다. 또한 시스템 점검, 업그레이드, 외부 API 장애 등으로 인해 일시적으로 서비스가 중단될 수 있습니다.`
                },
                {
                    heading: "6. 문의 및 지원",
                    content: `본 시스템의 사용 방법, 분석 결과 해석, 기술 지원 등에 관한 문의는 ZeroSite Decision OS Support Team으로 연락 주시기 바랍니다.`
                }
            ],
            footer: `본 고지문은 2026년 1월 12일부터 적용됩니다.
ZeroSite Decision OS | Version 1.0 | LH-READY`
        },
        
        // Page Footer용 (모든 페이지 하단)
        pageFooter: {
            title: "ZeroSite Decision OS",
            text: `본 서비스는 의사결정 보조 도구입니다. 최종 판단은 발주기관 및 인허가권자의 검토에 따릅니다.`
        }
    },
    
    /**
     * Landing Page용 Disclaimer 렌더링
     */
    renderLandingDisclaimer() {
        const disclaimer = this.disclaimers.landing;
        return `
            <div class="legal-disclaimer">
                <div class="legal-disclaimer-header">
                    <span class="legal-disclaimer-icon">${disclaimer.icon}</span>
                    <span>${disclaimer.title}</span>
                </div>
                <div class="legal-disclaimer-content">
                    ${disclaimer.content}
                </div>
                <div class="legal-disclaimer-footer">
                    ${disclaimer.footer}
                </div>
            </div>
        `;
    },
    
    /**
     * M6 Dashboard용 Disclaimer 렌더링
     */
    renderDashboardDisclaimer() {
        const disclaimer = this.disclaimers.dashboard;
        return `
            <div class="dashboard-disclaimer">
                <div class="legal-disclaimer-header">
                    <span class="dashboard-disclaimer-icon">${disclaimer.icon}</span>
                    <span>${disclaimer.title}</span>
                </div>
                <div class="dashboard-disclaimer-content">
                    ${disclaimer.content}
                </div>
            </div>
        `;
    },
    
    /**
     * PDF 표지용 Disclaimer 텍스트
     */
    getPdfCoverDisclaimer() {
        return this.disclaimers.pdfCover.text;
    },
    
    /**
     * PDF 부록용 Disclaimer HTML
     */
    renderPdfAppendixDisclaimer() {
        const appendix = this.disclaimers.pdfAppendix;
        let html = `
            <div class="pdf-disclaimer">
                <h2 class="pdf-disclaimer-title">${appendix.title}</h2>
        `;
        
        appendix.sections.forEach(section => {
            html += `
                <div class="pdf-disclaimer-section">
                    <h3>${section.heading}</h3>
                    <p>${section.content}</p>
                </div>
            `;
        });
        
        html += `
                <div class="pdf-disclaimer-footer">
                    <p style="text-align: center; color: #868e96; font-size: 0.9rem; margin-top: 40px;">
                        ${appendix.footer}
                    </p>
                </div>
            </div>
        `;
        
        return html;
    },
    
    /**
     * Page Footer용 Disclaimer 렌더링
     */
    renderPageFooterDisclaimer() {
        const footer = this.disclaimers.pageFooter;
        return `
            <div class="page-footer-disclaimer">
                <div class="page-footer-disclaimer-content">
                    <div class="page-footer-disclaimer-title">${footer.title}</div>
                    <div class="page-footer-disclaimer-text">${footer.text}</div>
                </div>
            </div>
        `;
    },
    
    /**
     * 자동으로 페이지에 Disclaimer 추가
     */
    init(pageType) {
        switch(pageType) {
            case 'landing':
                this.insertLandingDisclaimer();
                break;
            case 'dashboard':
                this.insertDashboardDisclaimer();
                break;
            case 'page-footer':
                this.insertPageFooter();
                break;
            default:
                console.warn('Unknown page type for disclaimer:', pageType);
        }
    },
    
    /**
     * Landing Page에 Disclaimer 삽입
     */
    insertLandingDisclaimer() {
        const container = document.querySelector('.landing-disclaimer-container');
        if (container) {
            container.innerHTML = this.renderLandingDisclaimer();
        }
    },
    
    /**
     * M6 Dashboard에 Disclaimer 삽입
     */
    insertDashboardDisclaimer() {
        const container = document.querySelector('.dashboard-disclaimer-container');
        if (container) {
            container.innerHTML = this.renderDashboardDisclaimer();
        }
    },
    
    /**
     * Page Footer에 Disclaimer 삽입
     */
    insertPageFooter() {
        const footer = document.querySelector('footer') || document.body;
        const disclaimerHTML = this.renderPageFooterDisclaimer();
        footer.insertAdjacentHTML('beforeend', disclaimerHTML);
    }
};

// PDF 생성용 함수 (Python에서 호출 가능)
function getPdfDisclaimerData() {
    return {
        cover: LegalDisclaimerSystem.getPdfCoverDisclaimer(),
        appendix: LegalDisclaimerSystem.renderPdfAppendixDisclaimer()
    };
}

// Export for ES6 modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LegalDisclaimerSystem;
}
