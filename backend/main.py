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
    import os
    logger.info("🚀 Crisis-MMD Backend starting up...")
    logger.info(f"🔍 PORT env var: {os.environ.get('PORT', 'NOT SET')}")
    logger.info(f"🔍 SUPABASE_URL: {os.environ.get('SUPABASE_URL', 'NOT SET')[:50]}...")
    logger.info(f"🔍 USE_SUPABASE: {os.environ.get('USE_SUPABASE', 'NOT SET')}")
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
    import os
    return {
        "message": "Crisis-MMD API is running",
        "status": "healthy",
        "version": "2.0.0",
        "description": "Multimodal Disaster Analysis with user authentication and crisis alert system",
        "debug_info": {
            "port": os.environ.get("PORT", "NOT SET"),
            "host": "0.0.0.0",
            "environment": "production" if not os.environ.get("DEBUG", "true").lower() == "true" else "development"
        }
    }

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check environment"""
    import os
    return {
        "environment_variables": {
            "PORT": os.environ.get("PORT", "NOT SET"),
            "DEBUG": os.environ.get("DEBUG", "NOT SET"),
            "USE_SUPABASE": os.environ.get("USE_SUPABASE", "NOT SET"),
            "SUPABASE_URL_SET": bool(os.environ.get("SUPABASE_URL")),
            "VAPI_API_KEY_SET": bool(os.environ.get("VAPI_API_KEY"))
        },
        "server_info": {
            "uvicorn_accessible": True,
            "fastapi_running": True,
            "timestamp": "2024-01-01"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    import os
    return {
        "status": "healthy",
        "models_loaded": len(models),
        "port": os.environ.get("PORT", "NOT SET"),
        "supabase_configured": bool(os.environ.get("SUPABASE_URL")),
        "use_supabase": os.environ.get("USE_SUPABASE", "NOT SET"),
        "environment_check": "OK",
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
            "/api/v1/crisis-map/health",
            # Orchestrate endpoints
            "/api/v1/orchestrate",
            "/api/v1/orchestrate/health",
            # Classification endpoints
            "/api/v1/classify-crisis",
            "/api/v1/classify-crisis/health",
            "/api/v1/push-classification-db", 
            "/api/v1/push-classification-db/health",
            # Aggregation endpoints
            "/api/v1/get-aggregate",
            "/api/v1/get-aggregate/health",
            # Emergency endpoints
            "/api/v1/trigger-call-for-location",
            "/api/v1/trigger-call-for-location/health",
            # Config endpoints
            "/api/v1/config/supabase"
        ]
    }

@app.get("/api/v1/config/supabase")
async def get_supabase_config():
    """Get Supabase configuration for frontend applications"""
    import os
    return {
        "supabase_url": os.environ.get("SUPABASE_URL"),
        "supabase_anon_key": os.environ.get("SUPABASE_ANON_KEY"),
        "configured": bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_ANON_KEY"))
    }

# Include routers
from routes import process, users, red_zone, crisis_map, orchestrate, classify_crisis, push_classification_db, get_aggregate, trigger_call_for_location
app.include_router(process.router, prefix="/api/v1", tags=["processing"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(red_zone.router, prefix="/api/v1", tags=["red-zone"])
app.include_router(crisis_map.router, prefix="/api/v1", tags=["crisis-map"])
app.include_router(orchestrate.router, prefix="/api/v1", tags=["orchestrate"])
app.include_router(classify_crisis.router, prefix="/api/v1", tags=["classification"])
app.include_router(push_classification_db.router, prefix="/api/v1", tags=["classification"])
app.include_router(get_aggregate.router, prefix="/api/v1", tags=["aggregation"])
app.include_router(trigger_call_for_location.router, prefix="/api/v1", tags=["emergency"])

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    print(f"🔍 Environment PORT: {os.environ.get('PORT', 'NOT SET')}")
    print(f"🌐 Server will be accessible at: http://0.0.0.0:{port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )