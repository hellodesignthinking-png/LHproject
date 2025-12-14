"""
ZeroSite v24.1 Test Server with Market Data Integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ZeroSite v24.1 - Land Appraisal System",
    version="24.1.0",
    description="Advanced Korean Real Estate Appraisal with MOLIT Integration"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (dashboard)
try:
    app.mount("/public", StaticFiles(directory="public"), name="public")
    logger.info("✅ Static files mounted: /public")
except Exception as e:
    logger.warning(f"⚠️ Could not mount static files: {e}")

# Include v24.1 API router
try:
    from app.api.v24_1.api_router import router as v241_router
    app.include_router(v241_router, tags=["v24.1"])
    logger.info(f"✅ V24.1 API Router included with {len(v241_router.routes)} routes")
    for route in v241_router.routes:
        if hasattr(route, 'path'):
            logger.info(f"   Route: {route.path}")
except ImportError as e:
    logger.error(f"❌ Failed to import v24.1 router: {e}")
except Exception as e:
    logger.error(f"❌ Error including router: {e}")

@app.get("/")
async def root():
    return {
        "service": "ZeroSite v24.1",
        "status": "running",
        "features": [
            "Real Estate Appraisal (3 approaches)",
            "MOLIT Real Transaction Data Integration",
            "PDF Report Generation",
            "Cloud Storage Support",
            "Land Diagnosis"
        ],
        "dashboard": "/public/dashboard.html",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "24.1.0",
        "market_data": "MOLIT API Integrated"
    }

if __name__ == "__main__":
    logger.info("="*70)
    logger.info("🚀 Starting ZeroSite v24.1 Server with Market Data Integration")
    logger.info("="*70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
