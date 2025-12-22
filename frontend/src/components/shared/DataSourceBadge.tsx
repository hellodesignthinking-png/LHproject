/**
 * DataSourceBadge Component
 * =========================
 * 
 * Displays data source indicator with color coding
 * 
 * Colors:
 * - 🟢 Green: API Auto (api)
 * - 🔵 Blue: User Input (manual)
 * - 🟠 Orange: PDF Based (pdf)
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-17
 */

import React from 'react';
import { DataSourceBadgeProps } from '../../types/m1.types';
import './DataSourceBadge.css';

const SOURCE_CONFIG = {
  api: {
    label: 'API 자동',
    icon: '🟢',
    className: 'badge-api',
  },
  manual: {
    label: '사용자 입력',
    icon: '🔵',
    className: 'badge-manual',
  },
  pdf: {
    label: 'PDF 기반',
    icon: '🟠',
    className: 'badge-pdf',
  },
  mock: {
    label: 'Mock 데이터',
    icon: '🟡',
    className: 'badge-mock',
  },
};

export const DataSourceBadge: React.FC<DataSourceBadgeProps> = ({
  source,
  apiName,
  timestamp,
  confidence,
}) => {
  const config = SOURCE_CONFIG[source];

  const tooltipContent = [
    apiName && `API: ${apiName}`,
    timestamp && `시간: ${new Date(timestamp).toLocaleString('ko-KR')}`,
    confidence !== undefined && `신뢰도: ${(confidence * 100).toFixed(0)}%`,
  ]
    .filter(Boolean)
    .join('\n');

  return (
    <div className={`data-source-badge ${config.className}`} title={tooltipContent}>
      <span className="badge-icon">{config.icon}</span>
      <span className="badge-label">{config.label}</span>
      {apiName && <span className="badge-api-name">({apiName})</span>}
      {confidence !== undefined && (
        <span className="badge-confidence">{(confidence * 100).toFixed(0)}%</span>
      )}
    </div>
  );
};

export default DataSourceBadge;
