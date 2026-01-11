import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'

// Phase 2: Human-Verified Workflow Pages
import { ProjectListPage } from './pages/ProjectListPage'
import { CreateProjectPage } from './pages/CreateProjectPage'
import { M1VerificationPage } from './pages/M1VerificationPage'
import { M2ResultsPage } from './pages/M2ResultsPage'
import { M3ResultsPage } from './pages/M3ResultsPage'
import { M4ResultsPage } from './pages/M4ResultsPage'
import { M5ResultsPage } from './pages/M5ResultsPage'
import { M6ResultsPage } from './pages/M6ResultsPage'

// Legacy routes (maintained for backward compatibility)
import { M1LandingPage } from './components/m1/M1LandingPage'
import { PipelineOrchestrator } from './components/pipeline/PipelineOrchestrator'

function App() {
  return (
    <div className="app">
      <Routes>
        {/* Phase 2: Human-Verified Workflow Routes */}
        <Route path="/" element={<Navigate to="/projects" replace />} />
        <Route path="/projects" element={<ProjectListPage />} />
        <Route path="/projects/create" element={<CreateProjectPage />} />
        <Route path="/projects/:projectId/modules/m1/verify" element={<M1VerificationPage />} />
        <Route path="/projects/:projectId/modules/m2/results" element={<M2ResultsPage />} />
        <Route path="/projects/:projectId/modules/m3/results" element={<M3ResultsPage />} />
        <Route path="/projects/:projectId/modules/m4/results" element={<M4ResultsPage />} />
        <Route path="/projects/:projectId/modules/m5/results" element={<M5ResultsPage />} />
        <Route path="/projects/:projectId/modules/m6/results" element={<M6ResultsPage />} />
        
        {/* Legacy routes (backward compatibility) */}
        <Route path="/m1" element={<M1LandingPage />} />
        <Route path="/pipeline" element={<PipelineOrchestrator />} />
        
        {/* Catch all - redirect to projects */}
        <Route path="*" element={<Navigate to="/projects" replace />} />
      </Routes>
    </div>
  )
}

export default App
