/**
 * ZeroSite v9.1 REAL - 용도지역 자동 매핑 데이터
 * 
 * 용도지역 선택 시 BCR/FAR를 자동으로 표시하기 위한 참조 데이터
 * (실제 계산은 Backend ZoningAutoMapperV9에서 수행됨)
 */

const ZONE_TYPE_INFO = {
    "제1종일반주거지역": {
        bcr: "60%",
        far: "100-150%",
        maxFloors: "3-4층",
        description: "저층 주거 중심"
    },
    "제2종일반주거지역": {
        bcr: "60%",
        far: "150-200%",
        maxFloors: "5-7층",
        description: "중층 주거 중심"
    },
    "제3종일반주거지역": {
        bcr: "50%",
        far: "200-300%",
        maxFloors: "7-15층",
        description: "중고층 주거 중심"
    },
    "준주거지역": {
        bcr: "60-70%",
        far: "400-500%",
        maxFloors: "12-20층",
        description: "주거+상업 복합"
    },
    "중심상업지역": {
        bcr: "80%",
        far: "800-1500%",
        maxFloors: "20-40층",
        description: "고층 상업 중심"
    },
    "일반상업지역": {
        bcr: "70-80%",
        far: "600-1300%",
        maxFloors: "15-30층",
        description: "상업 중심"
    },
    "근린상업지역": {
        bcr: "60-70%",
        far: "400-900%",
        maxFloors: "10-20층",
        description: "근린 상업 중심"
    }
};

/**
 * 용도지역 정보를 가져오는 함수
 * @param {string} zoneType - 용도지역명
 * @returns {object} 용도지역 정보 또는 null
 */
function getZoneTypeInfo(zoneType) {
    return ZONE_TYPE_INFO[zoneType] || null;
}

/**
 * 용도지역 선택 시 정보 툴팁 표시
 * @param {string} zoneType - 용도지역명
 * @returns {string} 툴팁 HTML
 */
function getZoneTypeTooltip(zoneType) {
    const info = getZoneTypeInfo(zoneType);
    if (!info) return "";
    
    return `
        <div class="text-xs text-gray-600 mt-1 p-2 bg-blue-50 rounded">
            📊 예상 기준: 건폐율 ${info.bcr}, 용적률 ${info.far}<br>
            🏢 가능층수: ${info.maxFloors}<br>
            💡 ${info.description}
        </div>
    `;
}

// Export for use in HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ZONE_TYPE_INFO, getZoneTypeInfo, getZoneTypeTooltip };
}
