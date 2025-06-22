from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store loaded models
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("🚀 Crisis-MMD Backend starting up...")
    logger.info("📊 Initializing classified data storage and retrieval system...")
    logger.info("👥 Initializing user authentication and management system...")
    
    # TODO: Initialize ML models here in future phases
    # models["text_classifier"] = load_text_model()
    # models["image_classifier"] = load_image_model() 
    # models["multimodal_fusion"] = load_fusion_model()
    
    logger.info("✅ Startup complete - Crisis-MMD system ready")
    
    yield
    
    # Shutdown
    logger.info("🛑 Crisis-MMD Backend shutting down...")
    models.clear()
    logger.info("✅ Cleanup complete")

# Create FastAPI app with lifespan events
app = FastAPI(
    title="Crisis-MMD API",
    description="Multimodal Disaster Analysis - Store and retrieve classified tweet data with user authentication for crisis alert system",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure more restrictively in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url)
        }
    )

# Basic health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "Crisis-MMD API is running",
        "status": "healthy",
        "version": "2.0.0",
        "description": "Multimodal Disaster Analysis with user authentication and crisis alert system"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": len(models),
        "available_endpoints": [
            "/",
            "/health",
            "/docs",
            "/redoc",
            # Data processing endpoints
            "/api/v1/classified-data/store",
            "/api/v1/classified-data/all",
            "/api/v1/classified-data/filter",
            "/api/v1/health",
            # User authentication endpoints
            "/api/v1/users/auth/send-otp",
            "/api/v1/users/auth/verify-otp",
            "/api/v1/users/profile",
            "/api/v1/users/",
            "/api/v1/users/location-radius",
            # Red Zone emergency endpoints
            "/api/v1/red-zone/trigger",
            # Crisis Map endpoints
            "/api/v1/crisis-map/data",
            "/api/v1/crisis-map/summary",
            "/api/v1/crisis-map/disaster-types",
            "/api/v1/crisis-map/health"
        ]
    }

# Include routers
from routes import process, users, red_zone, crisis_map
app.include_router(process.router, prefix="/api/v1", tags=["processing"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(red_zone.router, prefix="/api/v1", tags=["red-zone"])
app.include_router(crisis_map.router, prefix="/api/v1", tags=["crisis-map"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )