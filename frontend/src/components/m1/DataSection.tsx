/**
 * DataSection Component
 * ====================
 * 
 * Reusable component for displaying collected data sections
 * with API status indicators and edit functionality
 * 
 * Part of M1 v2.0 Unified Review Screen
 */

import React from 'react';
import './DataSection.css';

interface APIStatus {
  success: boolean;
  error?: string;
  api_name?: string;
}

interface DataSectionProps {
  title: string;
  icon: string;
  apiStatus?: APIStatus;
  children: React.ReactNode;
  className?: string;
}

export const DataSection: React.FC<DataSectionProps> = ({
  title,
  icon,
  apiStatus,
  children,
  className = '',
}) => {
  const getStatusBadge = () => {
    if (!apiStatus) return null;

    // NEW Phase 2: More explicit data source indicators
    if (apiStatus.success) {
      return (
        <span className="status-badge status-success" title={`Data source: ${apiStatus.api_name}`}>
          ✓ 실제 데이터 (API)
        </span>
      );
    } else if (apiStatus.api_name === 'Manual Input') {
      return (
        <span className="status-badge status-manual" title="User manual input">
          ✍️ 직접 입력
        </span>
      );
    } else if (apiStatus.error?.includes('PDF')) {
      return (
        <span className="status-badge status-pdf" title={apiStatus.error}>
          📄 PDF 추출
        </span>
      );
    } else {
      return (
        <span className="status-badge status-fallback" title={apiStatus.error}>
          ⚠ Mock 데이터 (확인 필요)
        </span>
      );
    }
  };

  return (
    <div className={`data-section ${className}`}>
      <div className="section-header">
        <h3 className="section-title">
          <span className="section-icon">{icon}</span>
          {title}
        </h3>
        {getStatusBadge()}
      </div>
      <div className="section-content">
        {children}
      </div>
    </div>
  );
};

interface DataFieldProps {
  label: string;
  value: any;
  editable?: boolean;
  onChange?: (value: any) => void;
  unit?: string;
  type?: 'text' | 'number';
}

export const DataField: React.FC<DataFieldProps> = ({
  label,
  value,
  editable = false,
  onChange,
  unit = '',
  type = 'text',
}) => {
  const displayValue = value ?? '-';

  if (!editable) {
    return (
      <div className="data-field">
        <label className="field-label">{label}</label>
        <div className="field-value">
          {displayValue}
          {unit && <span className="field-unit">{unit}</span>}
        </div>
      </div>
    );
  }

  return (
    <div className="data-field editable">
      <label className="field-label">
        {label}
        <span className="edit-indicator">✎</span>
      </label>
      <input
        type={type}
        className="field-input"
        value={value || ''}
        onChange={(e) => onChange?.(type === 'number' ? Number(e.target.value) : e.target.value)}
      />
      {unit && <span className="field-unit">{unit}</span>}
    </div>
  );
};
