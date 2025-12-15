"""
ZeroSite v13.0 - Phase 11.2 Minimal UI
FastAPI Application Entry Point

Simple 2-step UX:
1. User inputs address → Generate Report
2. Progress (8s) → Download PDF

This is THE STAGE for THE PRODUCT (Phase 10.5 Report)
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

# Import Phase 11.2 router
from app.routers.report_v13 import router as report_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ZeroSite v13.0 - LH Report Generator",
    description="""
    ZeroSite Phase 11.2: Minimal UI for LH Official Report Generation
    
    ## Features
    - 30-50 page LH Official Submission Report
    - AI-driven demand analysis (Phase 6.8)
    - Real-time market signals (Phase 7.7)
    - LH verified construction costs (Phase 8)
    - Enhanced financial metrics (Phase 2.5: NPV, IRR, Payback)
    
    ## Workflow
    1. POST /api/v13/report - Generate report
    2. GET /api/v13/report/{id}/summary - Get summary
    3. GET /api/v13/report/{id} - Download PDF
    """,
    version="13.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Phase 11.2 router
app.include_router(report_router)

# Mount static files (frontend)
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# Root endpoint - redirect to index
@app.get("/")
async def root():
    """Redirect to main UI"""
    return RedirectResponse(url="/index_v13.html")

# Serve HTML files
@app.get("/index_v13.html")
async def serve_index():
    """Serve main index page"""
    return FileResponse(str(frontend_dir / "index_v13.html"))

@app.get("/progress.html")
async def serve_progress():
    """Serve progress page"""
    return FileResponse(str(frontend_dir / "progress.html"))

@app.get("/result.html")
async def serve_result():
    """Serve result page"""
    return FileResponse(str(frontend_dir / "result.html"))

# Startup event
@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 80)
    logger.info("ZeroSite v13.0 - Phase 11.2: Minimal UI")
    logger.info("=" * 80)
    logger.info("🚀 Application started successfully")
    logger.info("📦 Phase 10.5: LH Full Report Generator - Ready")
    logger.info("🎨 Phase 11.2: Minimal UI - Ready")
    logger.info("=" * 80)
    logger.info("UI: http://localhost:8000/")
    logger.info("API Docs: http://localhost:8000/api/docs")
    logger.info("=" * 80)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info("Application shutting down...")

if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn
    uvicorn.run(
        "main_v13:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
