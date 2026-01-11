/**
 * Module Status Bar Component
 * ============================
 * 
 * Shows real-time status of all 6 modules (M1-M6)
 * Fixed at top of all analysis pages
 * 
 * Status Icons:
 * ✅ VERIFIED (green) - Completed & user verified
 * 🔄 IN_PROGRESS (blue) - Currently executing
 * ⏸️ LOCKED (gray) - Cannot execute (prerequisite not met)
 * ❌ ERROR (red) - Execution failed
 * ⚠️ PENDING (yellow) - Awaiting verification
 * 🚫 INVALID (orange) - Context changed, re-execute required
 */

import React from 'react';
import { ModuleInfo } from '../services/analysisAPI';
import './ModuleStatusBar.css';

interface ModuleStatusBarProps {
  m1: ModuleInfo;
  m2: ModuleInfo;
  m3: ModuleInfo;
  m4: ModuleInfo;
  m5: ModuleInfo;
  m6: ModuleInfo;
  projectId: string;
  onModuleClick: (moduleName: string) => void;
}

interface ModuleDisplay {
  name: string;
  label: string;
  icon: string;
  color: string;
  clickable: boolean;
  tooltip: string;
}

export const ModuleStatusBar: React.FC<ModuleStatusBarProps> = ({
  m1, m2, m3, m4, m5, m6, projectId, onModuleClick
}) => {
  
  const getModuleDisplay = (module: ModuleInfo): ModuleDisplay => {
    const { status, verification_status } = module;
    
    // VERIFIED (green) - User approved
    if (verification_status === 'approved') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '✅',
        color: 'verified',
        clickable: true,
        tooltip: '검증됨 - 클릭하여 결과 보기'
      };
    }
    
    // IN_PROGRESS (blue)
    if (status === 'in_progress') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '🔄',
        color: 'in-progress',
        clickable: false,
        tooltip: '실행 중...'
      };
    }
    
    // COMPLETED but pending verification (yellow)
    if (status === 'completed' && verification_status === 'pending') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '⚠️',
        color: 'pending',
        clickable: true,
        tooltip: '검증 대기 중 - 클릭하여 검증'
      };
    }
    
    // COMPLETED (no verification needed for M2-M6)
    if (status === 'completed') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '✅',
        color: 'completed',
        clickable: true,
        tooltip: '완료됨 - 클릭하여 결과 보기'
      };
    }
    
    // INVALID (orange) - Context changed
    if (status === 'invalid') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '🚫',
        color: 'invalid',
        clickable: false,
        tooltip: '유효하지 않음 - 데이터 변경됨, 재실행 필요'
      };
    }
    
    // ERROR (red)
    if (status === 'error') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '❌',
        color: 'error',
        clickable: true,
        tooltip: `오류: ${module.error_message || '알 수 없는 오류'}`
      };
    }
    
    // NOT_STARTED / LOCKED (gray)
    return {
      name: module.module_name,
      label: module.module_name,
      icon: '⏸️',
      color: 'locked',
      clickable: false,
      tooltip: '잠김 - 이전 모듈을 먼저 완료하세요'
    };
  };

  const modules = [
    getModuleDisplay(m1),
    getModuleDisplay(m2),
    getModuleDisplay(m3),
    getModuleDisplay(m4),
    getModuleDisplay(m5),
    getModuleDisplay(m6),
  ];

  const handleModuleClick = (module: ModuleDisplay) => {
    if (module.clickable) {
      onModuleClick(module.name);
    }
  };

  return (
    <div className="module-status-bar">
      <div className="status-bar-container">
        {modules.map((module) => (
          <div
            key={module.name}
            className={`
              module-badge 
              module-${module.color}
              ${module.clickable ? 'clickable' : 'disabled'}
            `}
            onClick={() => handleModuleClick(module)}
            title={module.tooltip}
          >
            <span className="module-icon">{module.icon}</span>
            <span className="module-label">{module.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// Legend Component (Optional)
// ============================================================================

export const ModuleStatusLegend: React.FC = () => {
  return (
    <div className="status-legend">
      <div className="legend-title">상태 아이콘:</div>
      <div className="legend-items">
        <div className="legend-item">
          <span className="legend-icon">✅</span>
          <span className="legend-text">검증됨/완료됨</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">🔄</span>
          <span className="legend-text">진행 중</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">⏸️</span>
          <span className="legend-text">잠김</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">⚠️</span>
          <span className="legend-text">검증 대기 중</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">🚫</span>
          <span className="legend-text">유효하지 않음</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">❌</span>
          <span className="legend-text">오류</span>
        </div>
      </div>
    </div>
  );
};
