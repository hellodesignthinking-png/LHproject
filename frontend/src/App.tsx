import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'

// Phase 2: Human-Verified Workflow Pages
import { ProjectListPage } from './pages/ProjectListPage'
import { CreateProjectPage } from './pages/CreateProjectPage'
import { ProjectDashboardPage } from './pages/ProjectDashboardPage'
import { M1VerificationPage } from './pages/M1VerificationPage'
import { M2ResultsPage } from './pages/M2ResultsPage'
import { M3ResultsPage } from './pages/M3ResultsPage'
import { M4ResultsPage } from './pages/M4ResultsPage'
import { M5ResultsPage } from './pages/M5ResultsPage'
import { M6ResultsPage } from './pages/M6ResultsPage'

// Phase 3: Reporting & External Submission OS
import FinalReportPage from './pages/FinalReportPage'

/**
 * PHASE 2 COMPLETE: Human-Verified Decision OS
 * 
 * ZeroSite는 더 이상 단일 분석 페이지가 아닙니다.
 * 모든 분석은 Project 단위로 관리되며,
 * 인간의 M1 검증 없이는 어떤 판단도 실행되지 않습니다.
 * 
 * System Mode: DATA-FIRST · HUMAN-VERIFIED · CONTEXT-AWARE
 * Date: 2026-01-11
 */

function App() {
  return (
    <div className="app">
      <Routes>
        {/* Phase 2: Human-Verified Workflow Routes (OFFICIAL) */}
        <Route path="/" element={<Navigate to="/projects" replace />} />
        <Route path="/projects" element={<ProjectListPage />} />
        <Route path="/projects/create" element={<CreateProjectPage />} />
        <Route path="/projects/:projectId" element={<ProjectDashboardPage />} />
        <Route path="/projects/:projectId/modules/m1/verify" element={<M1VerificationPage />} />
        <Route path="/projects/:projectId/modules/m2/results" element={<M2ResultsPage />} />
        <Route path="/projects/:projectId/modules/m3/results" element={<M3ResultsPage />} />
        <Route path="/projects/:projectId/modules/m4/results" element={<M4ResultsPage />} />
        <Route path="/projects/:projectId/modules/m5/results" element={<M5ResultsPage />} />
        <Route path="/projects/:projectId/modules/m6/results" element={<M6ResultsPage />} />
        
        {/* Phase 3: Final Report & Export (REPORTING OS) */}
        <Route path="/projects/:projectId/report" element={<FinalReportPage />} />
        
        {/* DEPRECATED: Legacy routes redirect to Phase 2 workflow */}
        <Route path="/analyze" element={<Navigate to="/projects" replace />} />
        <Route path="/m1" element={<Navigate to="/projects" replace />} />
        <Route path="/pipeline" element={<Navigate to="/projects" replace />} />
        
        {/* Catch all - redirect to projects */}
        <Route path="*" element={<Navigate to="/projects" replace />} />
      </Routes>
    </div>
  )
}

export default App
