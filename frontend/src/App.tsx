import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { M1LandingPage } from './components/m1/M1LandingPage'
import { PipelineOrchestrator } from './components/pipeline/PipelineOrchestrator'

function App() {
  return (
    <div className="app">
      <Routes>
        {/* Default route - redirect to pipeline */}
        <Route path="/" element={<Navigate to="/pipeline" replace />} />
        
        {/* M1 Landing Page Route */}
        <Route path="/m1" element={<M1LandingPage />} />
        
        {/* Pipeline Orchestrator Route (M1 -> M2-M6) */}
        <Route path="/pipeline" element={<PipelineOrchestrator />} />
        
        {/* Catch all - redirect to pipeline */}
        <Route path="*" element={<Navigate to="/pipeline" replace />} />
      </Routes>
    </div>
  )
}

export default App
