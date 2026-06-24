"""
Job Autopilot - Main FastAPI Application
Orchestrates all agents and API endpoints
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routers
from api.whatsapp_webhook import router as whatsapp_router
from api.job_link_handler import router as job_link_router
from api.scheduled_trigger import router as scheduled_router
from api.scheduled_trigger import initialize_scheduler, shutdown_scheduler
from api.status_endpoints import router as status_router
from core.logger import get_logger, logger as root_logger

# Legacy routers (for backward compatibility)
try:
    from tailor import router as tailor_router
    from users import router as users_router
    from preferences import router as preferences_router
except ImportError:
    tailor_router = users_router = preferences_router = None

app_logger = get_logger("job_autopilot.main")


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for app startup and shutdown
    """
    # Startup
    app_logger.info("🚀 Job Autopilot starting up...")
    try:
        await initialize_scheduler()
        app_logger.info("✅ Scheduler initialized")
    except Exception as e:
        app_logger.error(f"❌ Failed to initialize scheduler: {e}")
    
    yield  # App is running
    
    # Shutdown
    app_logger.info("🛑 Job Autopilot shutting down...")
    try:
        await shutdown_scheduler()
        app_logger.info("✅ Scheduler shut down")
    except Exception as e:
        app_logger.error(f"❌ Failed to shutdown scheduler: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="Job Autopilot",
    description="Autonomous job search, resume generation, and application pipeline",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include core routers
app.include_router(whatsapp_router)
app.include_router(job_link_router)
app.include_router(scheduled_router)
app.include_router(status_router)

# Include legacy routers if available
if tailor_router:
    app.include_router(tailor_router)
if users_router:
    app.include_router(users_router)
if preferences_router:
    app.include_router(preferences_router)


# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Job Autopilot Backend is running! 🚀",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    app_logger.error(
        "Unhandled exception",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error": str(exc)
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if app_logger.logger.level == "DEBUG" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )

