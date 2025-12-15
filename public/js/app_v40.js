/**
 * ZeroSite v40.0 - Main Application Logic
 * 종합 토지분석 통합 실행 및 Context 관리
 */

// Global context storage
window.ZERO_CONTEXT_ID = null;
window.ZERO_CONTEXT_DATA = null;

// DOM Elements
const runBtn = document.getElementById("runBtn");
const progress = document.getElementById("progress");
const progressText = document.getElementById("progressText");
const resultsSection = document.getElementById("resultsSection");
const resultAddress = document.getElementById("resultAddress");

/**
 * 종합 토지분석 실행 (Main Entry Point)
 */
runBtn.onclick = async () => {
  // 1. 입력값 검증
  const address = document.getElementById("address").value.trim();
  if (!address) {
    alert("❌ 주소는 필수 입력입니다.");
    return;
  }

  // 2. UI 상태 변경
  runBtn.disabled = true;
  progress.classList.add("show");
  resultsSection.classList.remove("show");

  // 3. 입력 데이터 수집
  const payload = {
    address: address,
    land_area_sqm: parseFloat(document.getElementById("land_area").value) || null,
    land_shape: document.getElementById("shape").value || "정방형",
    slope: document.getElementById("slope").value || "평지",
    road_access: document.getElementById("road").value || "중로",
    orientation: document.getElementById("orientation").value || "남향"
  };

  console.log("📤 요청 데이터:", payload);

  try {
    // 4. 진행 상태 표시
    updateProgress("토지진단 분석 중...");
    await sleep(500);

    updateProgress("규모검토 계산 중...");
    await sleep(500);

    updateProgress("감정평가 수행 중...");
    await sleep(500);

    updateProgress("시나리오 분석 중...");

    // 5. 통합 실행 API 호출
    const response = await fetch("/api/v40/run-full-land-analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "분석 실패");
    }

    const data = await response.json();
    console.log("📥 응답 데이터:", data);

    // 6. Context 저장
    window.ZERO_CONTEXT_ID = data.context_id;
    window.ZERO_CONTEXT_DATA = data;

    // 7. 결과 표시
    updateProgress("분석 완료! 결과를 표시합니다...");
    await sleep(800);

    progress.classList.remove("show");
    resultsSection.classList.add("show");
    resultAddress.textContent = address;

    // 8. 첫 번째 탭 (토지진단) 자동 로드
    loadTabData("diagnosis");

  } catch (error) {
    console.error("❌ 분석 오류:", error);
    alert(`분석 중 오류가 발생했습니다:\n${error.message}`);
    progress.classList.remove("show");
  } finally {
    runBtn.disabled = false;
  }
};

/**
 * 진행 상태 업데이트
 */
function updateProgress(text) {
  progressText.textContent = text;
}

/**
 * Sleep 유틸리티
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 탭 전환 이벤트
 */
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", function() {
    // 활성 탭 변경
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    this.classList.add("active");

    // 활성 콘텐츠 변경
    const tabName = this.dataset.tab;
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    document.getElementById(`tab-${tabName}`).classList.add("active");

    // 탭 데이터 로드
    loadTabData(tabName);
  });
});

/**
 * 탭별 데이터 로드 (Context 기반 조회)
 */
async function loadTabData(tabName) {
  if (!window.ZERO_CONTEXT_ID) {
    console.warn("⚠️ Context ID가 없습니다.");
    return;
  }

  const contentDiv = document.getElementById(`tab-${tabName}`);
  
  // 로딩 표시
  contentDiv.innerHTML = `
    <div class="loading">
      <div class="spinner-large"></div>
      <p>${getTabTitle(tabName)} 데이터를 불러오는 중...</p>
    </div>
  `;

  try {
    // Context 기반 조회 API 호출
    const response = await fetch(`/api/v40/context/${window.ZERO_CONTEXT_ID}/${tabName}`);
    
    if (!response.ok) {
      throw new Error("데이터 조회 실패");
    }

    const data = await response.json();
    console.log(`📊 ${tabName} 데이터:`, data);

    // 탭별 렌더링
    switch(tabName) {
      case "diagnosis":
        renderDiagnosis(data, contentDiv);
        break;
      case "capacity":
        renderCapacity(data, contentDiv);
        break;
      case "appraisal":
        renderAppraisal(data, contentDiv);
        break;
      case "scenario":
        renderScenario(data, contentDiv);
        break;
      case "reports":
        renderReports(contentDiv);
        break;
    }

  } catch (error) {
    console.error(`❌ ${tabName} 로드 오류:`, error);
    contentDiv.innerHTML = `
      <div class="placeholder">
        <i class="fas fa-exclamation-triangle"></i>
        데이터를 불러오는 중 오류가 발생했습니다.
      </div>
    `;
  }
}

/**
 * 탭 이름 매핑
 */
function getTabTitle(tabName) {
  const titles = {
    "diagnosis": "토지진단",
    "capacity": "규모검토",
    "appraisal": "감정평가",
    "scenario": "시나리오",
    "reports": "보고서"
  };
  return titles[tabName] || tabName;
}

/**
 * 토지진단 렌더링
 */
function renderDiagnosis(data, container) {
  container.innerHTML = `
    <h3 style="margin-bottom: 24px; color: #005BAC;">
      <i class="fas fa-map-marked-alt"></i> 토지진단 결과
    </h3>
    <div class="data-grid">
      <div class="data-card">
        <div class="label">토지 적합성</div>
        <div class="value">${data.suitability || '평가 중'}</div>
      </div>
      <div class="data-card">
        <div class="label">용도지역</div>
        <div class="value">${data.zone_type || '조회 중'}</div>
      </div>
      <div class="data-card">
        <div class="label">위치</div>
        <div class="value">${data.administrative?.si || ''} ${data.administrative?.gu || ''}</div>
      </div>
      <div class="data-card">
        <div class="label">좌표</div>
        <div class="value" style="font-size: 14px;">
          ${data.coordinates?.lat?.toFixed(6) || ''}, ${data.coordinates?.lng?.toFixed(6) || ''}
        </div>
      </div>
    </div>
    <p style="margin-top: 24px; padding: 16px; background: #E3F2FD; border-radius: 8px; color: #005BAC;">
      <i class="fas fa-info-circle"></i> 
      상세한 토지진단 내용은 보고서 탭에서 "토지진단 보고서"를 다운로드하세요.
    </p>
  `;
}

/**
 * 규모검토 렌더링
 */
function renderCapacity(data, container) {
  container.innerHTML = `
    <h3 style="margin-bottom: 24px; color: #005BAC;">
      <i class="fas fa-building"></i> 건축 규모 검토 결과
    </h3>
    <div class="data-grid">
      <div class="data-card">
        <div class="label">최대 연면적</div>
        <div class="value">${(data.max_floor_area || 0).toLocaleString()} ㎡</div>
      </div>
      <div class="data-card">
        <div class="label">예상 세대수</div>
        <div class="value">${data.max_units || 0}세대</div>
      </div>
      <div class="data-card">
        <div class="label">용적률 (FAR)</div>
        <div class="value">${((data.far || 0) * 100).toFixed(0)}%</div>
      </div>
      <div class="data-card">
        <div class="label">용도지역</div>
        <div class="value" style="font-size: 16px;">${data.zone_type || ''}</div>
      </div>
    </div>
    <p style="margin-top: 24px; padding: 16px; background: #E3F2FD; border-radius: 8px; color: #005BAC;">
      <i class="fas fa-info-circle"></i> 
      시나리오 탭에서 유형별(청년/신혼/고령자) 세부 계획을 확인하세요.
    </p>
  `;
}

/**
 * 감정평가 렌더링
 */
function renderAppraisal(data, container) {
  const finalValue = data.final_value || 0;
  const valuePerSqm = data.value_per_sqm || 0;
  const confidence = data.confidence_level || '보통';

  container.innerHTML = `
    <h3 style="margin-bottom: 24px; color: #005BAC;">
      <i class="fas fa-file-invoice-dollar"></i> 토지 감정평가 결과
    </h3>
    <div class="data-grid">
      <div class="data-card" style="grid-column: 1 / -1;">
        <div class="label">최종 감정가</div>
        <div class="value" style="font-size: 32px; color: #FF7A00;">
          ₩${finalValue.toLocaleString()}
        </div>
      </div>
      <div class="data-card">
        <div class="label">㎡당 단가</div>
        <div class="value">₩${valuePerSqm.toLocaleString()}/㎡</div>
      </div>
      <div class="data-card">
        <div class="label">신뢰도</div>
        <div class="value">${confidence}</div>
      </div>
      <div class="data-card">
        <div class="label">입지 프리미엄</div>
        <div class="value">+${data.premium_percentage || 0}%</div>
      </div>
    </div>
    <p style="margin-top: 24px; padding: 16px; background: #FFF3E0; border-radius: 8px; color: #FF7A00; font-weight: 600;">
      <i class="fas fa-file-pdf"></i> 
      23페이지 전문가 감정평가 보고서는 "보고서" 탭에서 다운로드 가능합니다.
    </p>
  `;
}

/**
 * 시나리오 렌더링
 */
function renderScenario(data, container) {
  const scenarioA = data.scenario_a || {};
  const scenarioB = data.scenario_b || {};
  const scenarioC = data.scenario_c || {};
  const recommended = data.recommended || "B안: 신혼형";

  container.innerHTML = `
    <h3 style="margin-bottom: 24px; color: #005BAC;">
      <i class="fas fa-code-branch"></i> 시나리오 비교 분석 (A · B · C)
    </h3>
    
    <div style="margin-bottom: 24px; padding: 16px; background: linear-gradient(135deg, #23A860 0%, #2ECC71 100%); color: white; border-radius: 12px; font-weight: 600;">
      <i class="fas fa-star"></i> 추천 시나리오: ${recommended}
      <div style="font-size: 14px; margin-top: 8px; opacity: 0.9;">
        ${data.reason || '종합 평가 기준'}
      </div>
    </div>

    <div class="data-grid">
      <!-- A안: 청년형 -->
      <div class="data-card" style="border-left-color: #FF9800;">
        <div class="label" style="font-size: 16px; font-weight: 700; color: #FF9800;">A안: 청년형</div>
        <div style="margin-top: 12px; font-size: 14px; color: #666;">
          <div>· 세대수: <strong>${scenarioA.units || 0}세대</strong></div>
          <div>· 평균 규모: <strong>${scenarioA.avg_unit_size || 0}㎡</strong></div>
          <div>· 정책 적합성: <strong>${scenarioA.policy_score || 0}점</strong></div>
          <div>· IRR: <strong>${scenarioA.irr || 0}%</strong></div>
          <div>· 리스크: <strong>${scenarioA.risk_score || '중간'}</strong></div>
        </div>
      </div>

      <!-- B안: 신혼형 -->
      <div class="data-card" style="border-left-color: #23A860;">
        <div class="label" style="font-size: 16px; font-weight: 700; color: #23A860;">B안: 신혼형</div>
        <div style="margin-top: 12px; font-size: 14px; color: #666;">
          <div>· 세대수: <strong>${scenarioB.units || 0}세대</strong></div>
          <div>· 평균 규모: <strong>${scenarioB.avg_unit_size || 0}㎡</strong></div>
          <div>· 정책 적합성: <strong>${scenarioB.policy_score || 0}점</strong></div>
          <div>· IRR: <strong>${scenarioB.irr || 0}%</strong></div>
          <div>· 리스크: <strong>${scenarioB.risk_score || '낮음'}</strong></div>
        </div>
      </div>

      <!-- C안: 고령자형 -->
      <div class="data-card" style="border-left-color: #9C27B0;">
        <div class="label" style="font-size: 16px; font-weight: 700; color: #9C27B0;">C안: 고령자형</div>
        <div style="margin-top: 12px; font-size: 14px; color: #666;">
          <div>· 세대수: <strong>${scenarioC.units || 0}세대</strong></div>
          <div>· 평균 규모: <strong>${scenarioC.avg_unit_size || 0}㎡</strong></div>
          <div>· 정책 적합성: <strong>${scenarioC.policy_score || 0}점</strong></div>
          <div>· IRR: <strong>${scenarioC.irr || 0}%</strong></div>
          <div>· 리스크: <strong>${scenarioC.risk_score || '중간'}</strong></div>
        </div>
      </div>
    </div>

    <p style="margin-top: 24px; padding: 16px; background: #E3F2FD; border-radius: 8px; color: #005BAC;">
      <i class="fas fa-lightbulb"></i> 
      추천 알고리즘: 정책적합성(40%) + IRR(30%) + 리스크(30%) 종합 평가
    </p>
  `;
}

/**
 * 보고서 렌더링
 */
function renderReports(container) {
  if (!window.ZERO_CONTEXT_ID) {
    container.innerHTML = `
      <div class="placeholder">
        <i class="fas fa-exclamation-circle"></i>
        Context ID가 없습니다. 먼저 분석을 실행하세요.
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <h3 style="margin-bottom: 24px; color: #005BAC;">
      <i class="fas fa-file-alt"></i> 보고서 생성 및 다운로드
    </h3>
    <p style="margin-bottom: 24px; color: #666;">
      아래 버튼을 클릭하여 각종 보고서를 다운로드하세요. 모든 보고서는 현재 분석 결과를 기반으로 생성됩니다.
    </p>

    <div class="report-buttons">
      <button class="report-btn" onclick="downloadReport('landowner')">
        <i class="fas fa-file-pdf"></i>
        토지주 브리핑 보고서
      </button>
      <button class="report-btn" onclick="downloadReport('lh')">
        <i class="fas fa-file-pdf"></i>
        LH 제출용 보고서
      </button>
      <button class="report-btn" onclick="downloadReport('professional')">
        <i class="fas fa-file-pdf"></i>
        전문가용 종합 보고서
      </button>
      <button class="report-btn" onclick="downloadReport('appraisal_v39')">
        <i class="fas fa-file-pdf"></i>
        토지 감정평가 보고서 (23p)
      </button>
      <button class="report-btn" onclick="downloadReport('policy')">
        <i class="fas fa-file-pdf"></i>
        정책효과 분석 보고서
      </button>
      <button class="report-btn" onclick="downloadReport('feasibility')">
        <i class="fas fa-file-pdf"></i>
        사업성 분석 보고서
      </button>
    </div>

    <div style="margin-top: 32px; padding: 20px; background: #FFF3E0; border-radius: 12px; border-left: 4px solid #FF7A00;">
      <h4 style="margin: 0 0 12px; color: #FF7A00;">
        <i class="fas fa-star"></i> 추천 보고서
      </h4>
      <p style="margin: 0; color: #666; font-size: 14px;">
        <strong>"토지 감정평가 보고서 (23p)"</strong>는 v39.0 전문가급 PDF 엔진으로 생성되며,
        완전한 감정평가 방법론, 거래사례, 시세동향, 리스크 분석을 포함합니다.
      </p>
    </div>
  `;
}

/**
 * 보고서 다운로드
 */
function downloadReport(reportType) {
  if (!window.ZERO_CONTEXT_ID) {
    alert("❌ Context ID가 없습니다. 먼저 분석을 실행하세요.");
    return;
  }

  const url = `/api/v40/reports/${window.ZERO_CONTEXT_ID}/${reportType}`;
  console.log(`📥 보고서 다운로드: ${url}`);

  // 새 창에서 다운로드
  window.open(url, '_blank');
}

/**
 * 분석 초기화
 */
function resetAnalysis() {
  if (!confirm("새로운 분석을 시작하시겠습니까?\n현재 분석 결과가 초기화됩니다.")) {
    return;
  }

  // Context 초기화
  window.ZERO_CONTEXT_ID = null;
  window.ZERO_CONTEXT_DATA = null;

  // UI 초기화
  resultsSection.classList.remove("show");
  document.getElementById("address").value = "";
  document.getElementById("land_area").value = "";
  document.getElementById("shape").selectedIndex = 0;
  document.getElementById("slope").selectedIndex = 0;
  document.getElementById("orientation").selectedIndex = 0;
  document.getElementById("road").selectedIndex = 0;

  // 첫 번째 탭으로 이동
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.querySelector(".tab[data-tab='diagnosis']").classList.add("active");

  document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
  document.getElementById("tab-diagnosis").classList.add("active");

  // 스크롤 최상단
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

console.log("✅ ZeroSite v40.0 app_v40.js loaded");
