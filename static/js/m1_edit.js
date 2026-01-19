const { createApp } = Vue;

createApp({
    data() {
        return {
            projectId: '',
            loading: true,
            project: {},
            m1State: {},
            formData: {
                // 기본
                address: '',
                lat: null,
                lng: null,
                // 토지
                land_area: null,
                zoning: '',
                bcr: null,
                far: null,
                official_land_price: null,
                // 도로
                road_access_type: '',
                road_width_m: null,
                road_count: null,
                fire_truck_access: null,
                road_legal_status: '',
                // 형상
                site_shape_type: '',
                frontage_m: null,
                depth_m: null,
                effective_build_ratio: null,
                // 방향
                main_direction: '',
                sunlight_risk: '',
                adjacent_height_risk: '',
                // 시세
                nearby_transaction_price_py: null,
                public_land_price_py: null,
                price_gap_ratio: null,
                // 기존 건물
                existing_building_exists: false,
                existing_building_structure: '',
                existing_building_floors: null,
                existing_building_area_m2: null,
                demolition_required: false,
                // 기타
                transaction_price: null,
                regulation_summary: '',
                lh_compatibility: ''
            },
            validationErrors: []
        };
    },
    
    computed: {
        isFrozen() {
            return this.m1State.status === 'FROZEN';
        },
        
        stageCompleted() {
            const status = this.m1State.status || 'EMPTY';
            return {
                stage1: ['AUTO_FETCHED', 'EDITABLE', 'READY_TO_FREEZE', 'FROZEN'].includes(status),
                stage2: ['FROZEN'].includes(status),
                stage3: ['FROZEN'].includes(status)
            };
        },
        
        stageActive() {
            const status = this.m1State.status || 'EMPTY';
            return {
                stage2: ['EDITABLE', 'READY_TO_FREEZE'].includes(status),
                stage3: false
            };
        }
    },
    
    methods: {
        async safeJsonParse(response) {
            const text = await response.text();
            try {
                return JSON.parse(text);
            } catch (e) {
                console.error('JSON 파싱 실패:', text);
                throw new Error('서버가 JSON이 아닌 응답을 반환했습니다. 관리자에게 문의하세요.');
            }
        },
        
        async loadProject() {
            try {
                const response = await fetch(`/api/projects/${this.projectId}`);
                if (response.ok) {
                    this.project = await this.safeJsonParse(response);
                }
            } catch (error) {
                console.error('프로젝트 로딩 오류:', error);
                alert(`프로젝트 로딩 실패: ${error.message}`);
            }
        },
        
        async loadM1State() {
            try {
                const response = await fetch(`/api/projects/${this.projectId}/modules/M1/state`);
                if (response.ok) {
                    this.m1State = await this.safeJsonParse(response);
                    console.log('M1 State:', this.m1State);
                    
                    // editable_data가 있으면 formData에 로드
                    if (this.m1State.editable_data) {
                        Object.assign(this.formData, this.m1State.editable_data);
                    }
                    
                    // auto_data 기본값 설정
                    if (this.m1State.auto_data) {
                        if (!this.formData.address) this.formData.address = this.m1State.auto_data.address;
                        if (!this.formData.lat) this.formData.lat = this.m1State.auto_data.lat;
                        if (!this.formData.lng) this.formData.lng = this.m1State.auto_data.lng;
                    }
                }
            } catch (error) {
                console.error('M1 상태 로딩 오류:', error);
                alert(`M1 상태 로딩 실패: ${error.message}`);
            }
        },
        
        async generateMock() {
            if (!confirm('Mock 데이터를 생성하시겠습니까?\n\n자동으로 모든 필드에 샘플 데이터가 채워집니다.')) {
                return;
            }
            
            try {
                this.loading = true;
                const response = await fetch(`/api/projects/${this.projectId}/modules/M1/mock-generate`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    const result = await this.safeJsonParse(response);
                    alert('✅ Mock 데이터가 생성되었습니다!');
                    await this.loadM1State();
                } else {
                    const error = await this.safeJsonParse(response);
                    alert(`Mock 생성 실패: ${error.detail?.message || '알 수 없는 오류'}`);
                }
            } catch (error) {
                console.error('Mock 생성 오류:', error);
                alert(`오류 발생: ${error.message}`);
            } finally {
                this.loading = false;
            }
        },
        
        async saveEdit() {
            try {
                this.loading = true;
                const response = await fetch(`/api/projects/${this.projectId}/modules/M1/edit`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.formData)
                });
                
                if (response.ok) {
                    const result = await this.safeJsonParse(response);
                    alert('✅ 저장되었습니다!');
                    await this.loadM1State();
                } else {
                    const error = await this.safeJsonParse(response);
                    alert(`저장 실패: ${error.detail?.message || '알 수 없는 오류'}`);
                }
            } catch (error) {
                console.error('저장 오류:', error);
                alert(`오류 발생: ${error.message}`);
            } finally {
                this.loading = false;
            }
        },
        
        async freezeData() {
            // 1. Validation 먼저 확인
            try {
                const valResponse = await fetch(`/api/projects/${this.projectId}/modules/M1/validate`);
                if (valResponse.ok) {
                    const validation = await this.safeJsonParse(valResponse);
                    
                    if (!validation.can_freeze) {
                        this.validationErrors = validation.missing_fields || [];
                        alert('❌ 필수 항목을 모두 입력해주세요.\n\n누락된 항목:\n' + this.validationErrors.join('\n'));
                        return;
                    }
                }
            } catch (error) {
                console.error('Validation 오류:', error);
                alert(`검증 실패: ${error.message}`);
                return;
            }
            
            // 2. 확인 메시지
            if (!confirm('⚠️ FACT FREEZE를 진행하시겠습니까?\n\n확정 후에는 데이터를 수정할 수 없습니다.')) {
                return;
            }
            
            // 3. Freeze 실행
            try {
                this.loading = true;
                const response = await fetch(`/api/projects/${this.projectId}/modules/M1/freeze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        approved_by: 'human',
                        agree_irreversible: true
                    })
                });
                
                if (response.ok) {
                    alert('✅ FACT FREEZE가 완료되었습니다!\n\nM2 모듈을 진행할 수 있습니다.');
                    await this.loadM1State();
                } else {
                    const error = await this.safeJsonParse(response);
                    alert(`Freeze 실패: ${error.detail?.message || '알 수 없는 오류'}`);
                }
            } catch (error) {
                console.error('Freeze 오류:', error);
                alert(`오류 발생: ${error.message}`);
            } finally {
                this.loading = false;
            }
        },
        
        goToM2() {
            window.location.href = `/static/project_detail.html?project_id=${this.projectId}`;
        },
        
        goBack() {
            window.location.href = `/static/project_detail.html?project_id=${this.projectId}`;
        }
    },
    
    async mounted() {
        const urlParams = new URLSearchParams(window.location.search);
        this.projectId = urlParams.get('project_id');
        
        if (!this.projectId) {
            alert('프로젝트 ID가 없습니다.');
            window.location.href = '/static/projects.html';
            return;
        }
        
        await this.loadProject();
        await this.loadM1State();
        this.loading = false;
    }
}).mount('#app');
