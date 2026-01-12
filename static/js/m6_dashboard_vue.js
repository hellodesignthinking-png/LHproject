/**
 * ZeroSite M6 Executive Dashboard - Vue.js Component
 * Version: 1.0
 * Purpose: LH 종합 판단 화면 (GO/CONDITIONAL/NO-GO)
 */

const M6Dashboard = {
    name: 'M6Dashboard',
    data() {
        return {
            loading: true,
            error: null,
            projectId: null,
            contextId: null,
            
            // M6 Data
            m6Data: {
                final_decision: '',
                lh_submission_probability: '',
                confidence_score: 0,
                module_evaluations: [],
                supplement_conditions: [],
                decision_rationale: []
            },
            
            // M7 Data
            m7Data: {
                complaint_mitigation: [],
                operation_model: ''
            },
            
            // API Base URL
            apiBaseUrl: window.location.origin
        }
    },
    
    computed: {
        decisionIcon() {
            if (this.m6Data.final_decision.includes('NO-GO')) return '🔴';
            if (this.m6Data.final_decision.includes('CONDITIONAL')) return '🟡';
            return '🟢';
        },
        
        decisionClass() {
            if (this.m6Data.final_decision.includes('NO-GO')) return 'no-go';
            if (this.m6Data.final_decision.includes('CONDITIONAL')) return 'conditional';
            return 'go';
        },
        
        confidencePercentage() {
            return Math.round(this.m6Data.confidence_score * 100);
        },
        
        sortedConditions() {
            const priorityOrder = { 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3 };
            return [...this.m6Data.supplement_conditions].sort((a, b) => {
                return priorityOrder[a.priority] - priorityOrder[b.priority];
            });
        }
    },
    
    methods: {
        async loadData() {
            this.loading = true;
            this.error = null;
            
            try {
                // Load M6 Data
                await this.loadM6Data();
                
                // Load M7 Data
                await this.loadM7Data();
                
            } catch (error) {
                console.error('Error loading data:', error);
                this.error = error.message;
                
                // Load mock data for demo
                this.loadMockData();
            } finally {
                this.loading = false;
            }
        },
        
        async loadM6Data() {
            const url = `${this.apiBaseUrl}/api/projects/${this.projectId}/modules/M6/result?context_id=${this.contextId}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('M6 데이터를 불러올 수 없습니다.');
            }
            
            const data = await response.json();
            this.m6Data = data;
        },
        
        async loadM7Data() {
            const url = `${this.apiBaseUrl}/api/projects/${this.projectId}/modules/M7/result?context_id=${this.contextId}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('M7 데이터를 불러올 수 없습니다.');
            }
            
            const data = await response.json();
            this.m7Data = data;
        },
        
        loadMockData() {
            this.m6Data = {
                final_decision: 'GO (조건부)',
                lh_submission_probability: '높음',
                confidence_score: 0.85,
                module_evaluations: [
                    {
                        module_name: 'M1 사실 확정',
                        status: 'PASS',
                        key_points: ['FROZEN 완료', '필수 항목 검증 통과', '데이터 신뢰도 95%']
                    },
                    {
                        module_name: 'M2 토지 매입 적정성',
                        status: 'PASS',
                        key_points: ['적정 매입가 420억원', '신뢰도 82%', 'LH 기준 부합']
                    },
                    {
                        module_name: 'M3 공급유형 적합성',
                        status: 'PASS',
                        key_points: ['청년 매입임대', 'LH 통과 점수 85점', '정책 부합성 높음']
                    },
                    {
                        module_name: 'M4 건축 규모',
                        status: 'PASS',
                        key_points: ['세대수 240세대', '보수적 설계 적용', '인허가 리스크 낮음']
                    },
                    {
                        module_name: 'M5 사업성·리스크',
                        status: 'WARNING',
                        key_points: ['안전 마진 12.76%', '리스크 관리 가능', '공사비 변동 주의']
                    },
                    {
                        module_name: 'M7 커뮤니티 계획',
                        status: 'PASS',
                        key_points: ['청년 생활안정형', '민원 방어 전략 수립', '운영 모델 명확']
                    }
                ],
                supplement_conditions: [
                    {
                        category: 'M5 사업성',
                        condition: '매입가 상단 3% 이내 권고. 건축비 변동성을 고려하여 안전 마진 유지 필요.',
                        priority: 'HIGH'
                    },
                    {
                        category: 'M4 건축 규모',
                        condition: '주차대수 +5% 확보. 청년 유형 특성상 차량 보유율 증가 추세 반영.',
                        priority: 'MEDIUM'
                    },
                    {
                        category: 'M7 운영',
                        condition: '운영규칙 사전 명문화. 공용 공간 이용 시간 제한 및 관리 주체 명확화.',
                        priority: 'LOW'
                    }
                ],
                decision_rationale: [
                    'LH 매입 기준을 충족하는 보수적 설계',
                    '청년 매입임대 정책과 높은 부합성',
                    '리스크 요인이 관리 가능한 수준',
                    '커뮤니티 계획으로 민원 방어 가능',
                    '안전 마진 확보로 사업 안정성 높음'
                ]
            };
            
            this.m7Data = {
                complaint_mitigation: [
                    { complaint_type: '소음 (공용 공간 이용)', mitigation_strategy: '야간(22시~07시) 공용 공간 이용 제한' },
                    { complaint_type: '주차 부족', mitigation_strategy: '법정 기준 +10% 주차 확보' },
                    { complaint_type: '외부인 유입', mitigation_strategy: '입주자 전용 공간, 출입 통제' }
                ],
                operation_model: 'LH 위탁 운영'
            };
        },
        
        downloadPDF() {
            const url = `${this.apiBaseUrl}/api/reports/integrated/${this.contextId}/pdf`;
            window.location.href = url;
        },
        
        viewDetailedReport() {
            const url = `${this.apiBaseUrl}/api/reports/integrated/${this.contextId}/html`;
            window.open(url, '_blank');
        },
        
        getStatusText(status) {
            const statusMap = {
                'PASS': '통과',
                'WARNING': '경고',
                'FAIL': '실패'
            };
            return statusMap[status] || status;
        },
        
        getPriorityText(priority) {
            const priorityMap = {
                'HIGH': '높음',
                'MEDIUM': '보통',
                'LOW': '낮음'
            };
            return priorityMap[priority] || priority;
        }
    },
    
    mounted() {
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        this.contextId = urlParams.get('context_id') || 'test-context-123';
        this.projectId = urlParams.get('project_id') || 'test-project-123';
        
        // Load data
        this.loadData();
    },
    
    template: `
        <div class="m6-dashboard">
            <!-- Loading State -->
            <div v-if="loading" class="loading">
                <div class="spinner"></div>
                <p>M6 종합 판단 결과를 불러오는 중...</p>
            </div>
            
            <!-- Error State -->
            <div v-else-if="error" class="error-state">
                <div class="error-icon">⚠️</div>
                <p>{{ error }}</p>
                <button @click="loadData" class="btn btn-primary">다시 시도</button>
            </div>
            
            <!-- Main Content -->
            <div v-else class="main-content">
                <!-- Hero Card: 최종 판단 -->
                <div class="hero-card">
                    <div class="hero-title">🎯 LH 종합 판단 결과</div>
                    <div class="decision-icon">{{ decisionIcon }}</div>
                    <div :class="['decision', decisionClass]">{{ m6Data.final_decision }}</div>
                    <div class="probability">LH 매입 가능성: {{ m6Data.lh_submission_probability }}</div>
                    <div class="confidence">신뢰도: {{ confidencePercentage }}%</div>
                    
                    <div class="action-buttons">
                        <button @click="downloadPDF" class="btn btn-primary">
                            📄 PDF 다운로드
                        </button>
                        <button @click="viewDetailedReport" class="btn btn-secondary">
                            📊 상세 보고서 보기
                        </button>
                    </div>
                </div>
                
                <!-- Decision Rationale Card -->
                <div v-if="m6Data.decision_rationale && m6Data.decision_rationale.length > 0" class="eval-card">
                    <div class="card-title">
                        💡 판단 근거
                    </div>
                    <ul class="rationale-list">
                        <li v-for="(rationale, index) in m6Data.decision_rationale" :key="index">
                            {{ rationale }}
                        </li>
                    </ul>
                </div>
                
                <!-- Module Evaluation Card: 모듈별 평가 -->
                <div class="eval-card">
                    <div class="card-title">
                        📊 모듈별 평가
                    </div>
                    <div class="modules-grid">
                        <div 
                            v-for="module in m6Data.module_evaluations" 
                            :key="module.module_name"
                            :class="['module-item', module.status.toLowerCase()]"
                        >
                            <div class="module-name">{{ module.module_name }}</div>
                            <span :class="['module-status', 'status-' + module.status.toLowerCase()]">
                                {{ getStatusText(module.status) }}
                            </span>
                            <ul class="module-points">
                                <li v-for="(point, index) in module.key_points" :key="index">
                                    • {{ point }}
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <!-- Supplement Conditions Card: 보완 조건 -->
                <div class="eval-card">
                    <div class="card-title">
                        ⚠️ 보완 조건
                    </div>
                    <ul class="conditions-list" v-if="sortedConditions.length > 0">
                        <li 
                            v-for="(condition, index) in sortedConditions" 
                            :key="index"
                            :class="['condition-item', condition.priority.toLowerCase()]"
                        >
                            <div class="condition-header">
                                <strong>{{ condition.category }}</strong>
                                <span :class="['condition-priority', 'priority-' + condition.priority.toLowerCase()]">
                                    {{ getPriorityText(condition.priority) }}
                                </span>
                            </div>
                            <div class="condition-content">{{ condition.condition }}</div>
                        </li>
                    </ul>
                    <div v-else class="no-conditions">
                        보완 조건이 없습니다.
                    </div>
                </div>
                
                <!-- Community & Complaint Defense Card -->
                <div class="eval-card">
                    <div class="card-title">
                        🏘️ 커뮤니티 & 민원 방어
                    </div>
                    <div class="community-grid">
                        <div class="community-section">
                            <div class="section-title">예상 민원 유형</div>
                            <ul class="section-content">
                                <li v-for="(item, index) in m7Data.complaint_mitigation" :key="'complaint-' + index">
                                    • {{ item.complaint_type }}
                                </li>
                            </ul>
                        </div>
                        <div class="community-section">
                            <div class="section-title">대응 전략</div>
                            <ul class="section-content">
                                <li v-for="(item, index) in m7Data.complaint_mitigation" :key="'strategy-' + index">
                                    • {{ item.mitigation_strategy }}
                                </li>
                            </ul>
                        </div>
                        <div class="community-section">
                            <div class="section-title">관리 주체</div>
                            <div class="section-content">
                                {{ m7Data.operation_model }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = M6Dashboard;
}
