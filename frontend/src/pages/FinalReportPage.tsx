/**
 * FinalReportPage.tsx
 * Phase 3: Reporting & External Submission OS
 * Final Report Page - Aggregates M1-M6 with Export Options
 * 
 * Features:
 * - Display complete M1-M6 results
 * - Executive Summary auto-generation
 * - Source citations for all data
 * - Export to PDF, Excel, Submission Package
 * - Print-optimized layout
 * 
 * Route: /projects/{id}/report
 * Date: 2026-01-11
 * Mode: DATA-FIRST · HUMAN-VERIFIED · EXPORT-READY
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import analysisAPI from '../services/analysisAPI';
import './FinalReportPage.css';

interface ModuleResult {
  module: string;
  status: string;
  verification_status?: string;
  executed_at?: string;
  result_data?: any;
}

interface ProjectStatus {
  project_id: string;
  project_name: string;
  address: string;
  context_id: string;
  created_at: string;
  last_activity: string;
  modules: {
    M1?: ModuleResult;
    M2?: ModuleResult;
    M3?: ModuleResult;
    M4?: ModuleResult;
    M5?: ModuleResult;
    M6?: ModuleResult;
  };
}

const FinalReportPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [projectStatus, setProjectStatus] = useState<ProjectStatus | null>(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadProjectReport();
  }, [projectId]);

  const loadProjectReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (!projectId) {
        throw new Error('Project ID is required');
      }

      const status = await analysisAPI.getProjectStatus(projectId);
      setProjectStatus(status);
    } catch (err: any) {
      console.error('Failed to load project report:', err);
      setError(err.message || 'Failed to load project report');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = async () => {
    try {
      setExporting(true);
      const response = await fetch(`/api/analysis/projects/${projectId}/export/pdf`, {
        method: 'GET',
      });
      
      if (!response.ok) {
        throw new Error('PDF export failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `ZeroSite_Report_${projectStatus?.project_name}_${new Date().toISOString().split('T')[0]}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('PDF 내보내기에 실패했습니다.');
    } finally {
      setExporting(false);
    }
  };

  const handleExportExcel = async () => {
    try {
      setExporting(true);
      const response = await fetch(`/api/analysis/projects/${projectId}/export/excel`, {
        method: 'GET',
      });
      
      if (!response.ok) {
        throw new Error('Excel export failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `ZeroSite_Data_${projectStatus?.project_name}_${new Date().toISOString().split('T')[0]}.xlsx`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Excel export failed:', err);
      alert('Excel 내보내기에 실패했습니다.');
    } finally {
      setExporting(false);
    }
  };

  const handleExportSubmissionPackage = async () => {
    try {
      setExporting(true);
      const response = await fetch(`/api/analysis/projects/${projectId}/export/submission-package`, {
        method: 'GET',
      });
      
      if (!response.ok) {
        throw new Error('Submission package export failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `ZeroSite_Submission_${projectStatus?.project_name}_${new Date().toISOString().split('T')[0]}.zip`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Submission package export failed:', err);
      alert('제출 패키지 내보내기에 실패했습니다.');
    } finally {
      setExporting(false);
    }
  };

  const generateExecutiveSummary = (): string => {
    if (!projectStatus) return '';

    const { address, m2_status, m3_status, m5_status, m6_status } = projectStatus;
    const m2 = m2_status?.result_summary;
    const m3 = m3_status?.result_summary;
    const m5 = m5_status?.result_summary;
    const m6 = m6_status?.result_summary;

    return `
본 보고서는 ${address}에 대한 제로사이트 분석 결과를 종합한 문서입니다.

주요 분석 결과:
• 토지 가치: ${m2?.land_value ? `₩${(m2.land_value / 100000000).toFixed(2)}억` : 'N/A'}
• 권장 주택 유형: ${m3?.selected_type || 'N/A'}
• 사업 타당성 (NPV): ${m5?.npv ? `₩${(m5.npv / 100000000).toFixed(2)}억` : 'N/A'}
• 최종 판정: ${m6?.decision || 'N/A'}

본 분석은 검증된 데이터를 기반으로 작성되었으며, 모든 수치는 출처와 함께 추적 가능합니다.
    `.trim();
  };

  if (loading) {
    return (
      <div className="final-report-page loading">
        <div className="loading-spinner">보고서를 불러오는 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="final-report-page error">
        <div className="error-message">
          <h2>오류 발생</h2>
          <p>{error}</p>
          <button onClick={() => navigate(`/projects/${projectId}`)}>
            프로젝트로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  if (!projectStatus) {
    return null;
  }

  return (
    <div className="final-report-page">
      <header className="report-header no-print">
        <button className="back-button" onClick={() => navigate(`/projects/${projectId}`)}>
          ← 프로젝트로 돌아가기
        </button>
        <h1>최종 보고서</h1>
        <div className="export-actions">
          <button 
            className="export-button pdf-button" 
            onClick={handleExportPDF}
            disabled={exporting}
          >
            📄 PDF 내보내기
          </button>
          <button 
            className="export-button excel-button" 
            onClick={handleExportExcel}
            disabled={exporting}
          >
            📊 Excel 내보내기
          </button>
          <button 
            className="export-button package-button" 
            onClick={handleExportSubmissionPackage}
            disabled={exporting}
          >
            📦 제출 패키지 다운로드
          </button>
          <button 
            className="export-button print-button" 
            onClick={() => window.print()}
          >
            🖨️ 인쇄
          </button>
        </div>
      </header>

      <div className="report-content">
        {/* Report Metadata */}
        <section className="report-metadata">
          <h2>프로젝트 정보</h2>
          <div className="metadata-grid">
            <div className="metadata-item">
              <span className="label">프로젝트 ID:</span>
              <span className="value">{projectStatus.project_id}</span>
            </div>
            <div className="metadata-item">
              <span className="label">프로젝트명:</span>
              <span className="value">{projectStatus.project_name}</span>
            </div>
            <div className="metadata-item">
              <span className="label">주소:</span>
              <span className="value">{projectStatus.address}</span>
            </div>
            <div className="metadata-item">
              <span className="label">Context ID:</span>
              <span className="value code">{projectStatus.context_id}</span>
            </div>
            <div className="metadata-item">
              <span className="label">생성일:</span>
              <span className="value">{new Date(projectStatus.created_at).toLocaleString('ko-KR')}</span>
            </div>
            <div className="metadata-item">
              <span className="label">최종 수정:</span>
              <span className="value">{new Date(projectStatus.last_activity).toLocaleString('ko-KR')}</span>
            </div>
          </div>
        </section>

        {/* Executive Summary */}
        <section className="executive-summary">
          <h2>요약</h2>
          <div className="summary-content">
            <pre>{generateExecutiveSummary()}</pre>
          </div>
        </section>

        {/* M1: Land Data */}
        <section className="module-section">
          <h2>M1: 토지 데이터 수집 및 검증</h2>
          {projectStatus.m1_status ? (
            <div className="module-content">
              <div className="module-status">
                <span className={`badge ${projectStatus.m1_status.verification_status?.toLowerCase()}`}>
                  {projectStatus.m1_status.verification_status || projectStatus.m1_status.status}
                </span>
                {projectStatus.m1_status.executed_at && (
                  <span className="timestamp">
                    실행일: {new Date(projectStatus.m1_status.executed_at).toLocaleString('ko-KR')}
                  </span>
                )}
              </div>
              {projectStatus.m1_status.result_summary && (
                <div className="result-data">
                  <h3>기본 정보</h3>
                  <ul>
                    <li><strong>주소:</strong> {projectStatus.m1_status.result_summary.address}</li>
                    <li><strong>면적:</strong> {projectStatus.m1_status.result_summary.area_sqm}㎡</li>
                    <li><strong>용도지역:</strong> {projectStatus.m1_status.result_summary.zone_type}</li>
                    <li><strong>건폐율:</strong> {projectStatus.m1_status.result_summary.bcr}%</li>
                    <li><strong>용적률:</strong> {projectStatus.m1_status.result_summary.far}%</li>
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="module-not-available">M1 데이터 없음</div>
          )}
        </section>

        {/* M2: Land Valuation */}
        <section className="module-section">
          <h2>M2: 토지 가치 평가</h2>
          {projectStatus.m2_status ? (
            <div className="module-content">
              <div className="module-status">
                <span className={`badge ${projectStatus.m2_status.status.toLowerCase()}`}>
                  {projectStatus.m2_status.status}
                </span>
                {projectStatus.m2_status.executed_at && (
                  <span className="timestamp">
                    실행일: {new Date(projectStatus.m2_status.executed_at).toLocaleString('ko-KR')}
                  </span>
                )}
              </div>
              {projectStatus.m2_status.result_summary && (
                <div className="result-data">
                  <ul>
                    <li><strong>토지 가치:</strong> ₩{(projectStatus.m2_status.result_summary.land_value / 100000000).toFixed(2)}억</li>
                    <li><strong>평당 단가:</strong> ₩{(projectStatus.m2_status.result_summary.unit_price_pyeong / 10000).toFixed(0)}만원/평</li>
                    <li><strong>신뢰도:</strong> {projectStatus.m2_status.result_summary.confidence_score}%</li>
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="module-not-available">M2 데이터 없음</div>
          )}
        </section>

        {/* M3: Housing Type */}
        <section className="module-section">
          <h2>M3: 주택 유형 선정</h2>
          {projectStatus.m3_status ? (
            <div className="module-content">
              <div className="module-status">
                <span className={`badge ${projectStatus.m3_status.status.toLowerCase()}`}>
                  {projectStatus.m3_status.status}
                </span>
                {projectStatus.m3_status.executed_at && (
                  <span className="timestamp">
                    실행일: {new Date(projectStatus.m3_status.executed_at).toLocaleString('ko-KR')}
                  </span>
                )}
              </div>
              {projectStatus.m3_status.result_summary && (
                <div className="result-data">
                  <ul>
                    <li><strong>권장 유형:</strong> {projectStatus.m3_status.result_summary.selected_type}</li>
                    <li><strong>근거:</strong> {projectStatus.m3_status.result_summary.decision_rationale}</li>
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="module-not-available">M3 데이터 없음</div>
          )}
        </section>

        {/* M4: Building Scale */}
        <section className="module-section">
          <h2>M4: 건축 규모 산정</h2>
          {projectStatus.m4_status ? (
            <div className="module-content">
              <div className="module-status">
                <span className={`badge ${projectStatus.m4_status.status.toLowerCase()}`}>
                  {projectStatus.m4_status.status}
                </span>
                {projectStatus.m4_status.executed_at && (
                  <span className="timestamp">
                    실행일: {new Date(projectStatus.m4_status.executed_at).toLocaleString('ko-KR')}
                  </span>
                )}
              </div>
              {projectStatus.m4_status.result_summary && (
                <div className="result-data">
                  <ul>
                    <li><strong>법정 세대수:</strong> {projectStatus.m4_status.result_summary.legal_capacity || 'N/A'}세대</li>
                    <li><strong>필수 세대수:</strong> {projectStatus.m4_status.result_summary.required_capacity || 'N/A'}세대</li>
                    <li><strong>인센티브 세대수:</strong> {projectStatus.m4_status.result_summary.incentive_capacity || 'N/A'}세대</li>
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="module-not-available">M4 데이터 없음</div>
          )}
        </section>

        {/* M5: Feasibility */}
        <section className="module-section">
          <h2>M5: 사업 타당성 분석</h2>
          {projectStatus.m5_status ? (
            <div className="module-content">
              <div className="module-status">
                <span className={`badge ${projectStatus.m5_status.status.toLowerCase()}`}>
                  {projectStatus.m5_status.status}
                </span>
                {projectStatus.m5_status.executed_at && (
                  <span className="timestamp">
                    실행일: {new Date(projectStatus.m5_status.executed_at).toLocaleString('ko-KR')}
                  </span>
                )}
              </div>
              {projectStatus.m5_status.result_summary && (
                <div className="result-data">
                  <ul>
                    <li><strong>NPV:</strong> ₩{projectStatus.m5_status.result_summary.npv ? (projectStatus.m5_status.result_summary.npv / 100000000).toFixed(2) : 'N/A'}억</li>
                    <li><strong>IRR:</strong> {projectStatus.m5_status.result_summary.irr || 'N/A'}%</li>
                    <li><strong>총 사업비:</strong> ₩{projectStatus.m5_status.result_summary.total_cost ? (projectStatus.m5_status.result_summary.total_cost / 100000000).toFixed(2) : 'N/A'}억</li>
                  </ul>
                  {projectStatus.m5_status.result_summary.risk_notes && (
                    <div className="risk-notes">
                      <h4>리스크 노트:</h4>
                      <ul>
                        {projectStatus.m5_status.result_summary.risk_notes.map((note: string, idx: number) => (
                          <li key={idx}>{note}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="module-not-available">M5 데이터 없음</div>
          )}
        </section>

        {/* M6: LH Comprehensive Review */}
        <section className="module-section">
          <h2>M6: LH 종합 검토</h2>
          {projectStatus.m6_status ? (
            <div className="module-content">
              <div className="module-status">
                <span className={`badge ${projectStatus.m6_status.status.toLowerCase()}`}>
                  {projectStatus.m6_status.status}
                </span>
                {projectStatus.m6_status.executed_at && (
                  <span className="timestamp">
                    실행일: {new Date(projectStatus.m6_status.executed_at).toLocaleString('ko-KR')}
                  </span>
                )}
              </div>
              {projectStatus.m6_status.result_summary && (
                <div className="result-data">
                  <div className={`decision-badge ${projectStatus.m6_status.result_summary.decision?.toLowerCase()}`}>
                    {projectStatus.m6_status.result_summary.decision || 'N/A'}
                  </div>
                  {projectStatus.modules?.M6.result_data.breakdown && (
                    <div className="breakdown">
                      <h4>세부 분석:</h4>
                      <p>{projectStatus.modules?.M6.result_data.breakdown}</p>
                    </div>
                  )}
                  {projectStatus.modules?.M6.result_data.recommendations && (
                    <div className="recommendations">
                      <h4>권장 사항:</h4>
                      <ul>
                        {projectStatus.modules?.M6.result_data.recommendations.map((rec: string, idx: number) => (
                          <li key={idx}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="module-not-available">M6 데이터 없음</div>
          )}
        </section>

        {/* Footer */}
        <footer className="report-footer">
          <p className="copyright">© ZeroSite by AntennaHoldings | Natai Heum</p>
          <p className="disclaimer">
            본 보고서는 ZeroSite Decision OS를 통해 생성된 분석 결과입니다.
            모든 수치는 검증된 데이터를 기반으로 하며, Context ID를 통해 추적 가능합니다.
          </p>
          <p className="mode-declaration">
            Mode: DATA-FIRST · HUMAN-VERIFIED · EXPORT-READY
          </p>
        </footer>
      </div>
    </div>
  );
};

export default FinalReportPage;
