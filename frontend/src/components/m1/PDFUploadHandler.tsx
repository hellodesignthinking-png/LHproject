/**
 * PDF Upload Handler Component
 * ==============================
 * 
 * Handles PDF document upload for land data extraction
 * Supports: 지적도, 토지이용계획확인서, 거래계약서
 * 
 * Part of M1 Phase 3: Data Collection Method - PDF Upload
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-17
 * Version: 2.2 (Phase 3)
 */

import React, { useState, useRef } from 'react';
import './PDFUploadHandler.css';

interface PDFUploadHandlerProps {
  onExtract: (extractedData: any) => void;
  onCancel: () => void;
}

export const PDFUploadHandler: React.FC<PDFUploadHandlerProps> = ({
  onExtract,
  onCancel,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('PDF 파일만 업로드 가능합니다.');
        return;
      }
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setError('파일 크기는 10MB를 초과할 수 없습니다.');
        return;
      }
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('PDF 파일만 업로드 가능합니다.');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        setError('파일 크기는 10MB를 초과할 수 없습니다.');
        return;
      }
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUploadAndExtract = async () => {
    if (!selectedFile) return;

    try {
      setUploading(true);
      setExtracting(true);
      setError(null);

      // Create FormData
      const formData = new FormData();
      formData.append('file', selectedFile);

      console.log('📄 Uploading PDF:', selectedFile.name);

      // Upload to backend
      const response = await fetch('/api/m1/pdf/extract', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('PDF 업로드 실패');
      }

      const result = await response.json();
      console.log('✅ PDF extraction complete:', result);

      // Pass extracted data to parent
      onExtract(result.data);

    } catch (err) {
      console.error('❌ PDF extraction failed:', err);
      setError(err instanceof Error ? err.message : 'PDF 처리 중 오류가 발생했습니다.');
    } finally {
      setUploading(false);
      setExtracting(false);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="pdf-upload-handler">
      <div className="pdf-upload-header">
        <h2>📄 PDF 문서 업로드</h2>
        <p className="pdf-upload-subtitle">
          지적도, 토지이용계획확인서 등 PDF 문서를 업로드하여 데이터를 자동으로 추출합니다.
        </p>
      </div>

      <div className="pdf-upload-info">
        <h4>📋 지원 문서</h4>
        <ul>
          <li>지적도 (토지대장)</li>
          <li>토지이용계획확인서</li>
          <li>부동산 거래계약서</li>
          <li>기타 토지 관련 공식 문서</li>
        </ul>
        <p className="info-note">
          💡 <strong>팁:</strong> 스캔한 이미지보다 원본 PDF가 인식률이 높습니다.
        </p>
      </div>

      {!selectedFile ? (
        <div
          className="pdf-drop-zone"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="drop-zone-icon">📁</div>
          <h3>파일을 드래그하거나 클릭하여 선택</h3>
          <p>PDF 파일 (최대 10MB)</p>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </div>
      ) : (
        <div className="pdf-file-selected">
          <div className="file-info">
            <div className="file-icon">📄</div>
            <div className="file-details">
              <h4>{selectedFile.name}</h4>
              <p>{formatFileSize(selectedFile.size)}</p>
            </div>
            <button
              className="btn-remove"
              onClick={handleRemoveFile}
              disabled={uploading}
            >
              ✕
            </button>
          </div>

          {!uploading && (
            <button
              className="btn-extract"
              onClick={handleUploadAndExtract}
              disabled={uploading}
            >
              🔍 데이터 추출 시작
            </button>
          )}

          {uploading && (
            <div className="extraction-progress">
              <div className="spinner"></div>
              <div className="progress-steps">
                <div className={`step ${uploading ? 'active' : ''}`}>
                  📤 업로드 중...
                </div>
                <div className={`step ${extracting ? 'active' : ''}`}>
                  🔍 텍스트 인식 중...
                </div>
                <div className="step">
                  ✅ 데이터 추출 중...
                </div>
              </div>
              <p className="progress-note">
                이 과정은 1-2분 정도 소요될 수 있습니다.
              </p>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="pdf-error">
          <div className="error-icon">⚠️</div>
          <p>{error}</p>
          <button className="btn-retry" onClick={() => setError(null)}>
            다시 시도
          </button>
        </div>
      )}

      <div className="pdf-upload-actions">
        <button
          className="btn-secondary"
          onClick={onCancel}
          disabled={uploading}
        >
          ← 뒤로 가기
        </button>
        <div className="action-hint">
          파일을 선택하고 "데이터 추출 시작"을 클릭하세요
        </div>
      </div>

      <div className="pdf-upload-notice">
        <h4>⚠️ 주의사항</h4>
        <ul>
          <li>추출된 데이터는 <strong>반드시 확인 및 수정</strong>이 필요합니다.</li>
          <li>스캔 품질에 따라 인식률이 다를 수 있습니다.</li>
          <li>추출 실패 시 직접 입력 방법을 사용하세요.</li>
        </ul>
      </div>
    </div>
  );
};
