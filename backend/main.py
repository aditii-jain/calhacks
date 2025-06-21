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
    
    # TODO: Initialize models here in future phases
    # models["text_classifier"] = load_text_model()
    # models["image_classifier"] = load_image_model() 
    # models["multimodal_fusion"] = load_fusion_model()
    
    logger.info("✅ Startup complete - models loaded")
    
    yield
    
    # Shutdown
    logger.info("🛑 Crisis-MMD Backend shutting down...")
    models.clear()
    logger.info("✅ Cleanup complete")

# Create FastAPI app with lifespan events
app = FastAPI(
    title="Crisis-MMD API",
    description="Multimodal Disaster Analysis - AI-powered crisis classification using text and images",
    version="1.0.0",
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
        "version": "1.0.0"
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
            "/redoc"
        ]
    }

# TODO: Include routers as we build them
# from routes import predict, demo, agents, voice
# app.include_router(predict.router, prefix="/api/v1", tags=["classification"])
# app.include_router(demo.router, prefix="/api/v1", tags=["demo"])
# app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
# app.include_router(voice.router, prefix="/api/v1", tags=["voice"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
