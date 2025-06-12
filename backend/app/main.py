from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uvicorn

from app.core.config import settings
from app.core.database import create_tables
from app.api.v1.market import router as market_router
from app.api.v1.economic import router as economic_router
from app.api.v1.scheduler import router as scheduler_router
from app.api.v1.portfolio import router as portfolio_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up Macro Finance Dashboard API...")

    # Initialize database
    try:
        create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Macro Finance Dashboard API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A comprehensive financial data visualization platform",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Application health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": "development" if settings.debug else "production",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Macro Finance Dashboard API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.api_v1_prefix,
    }


# Include API routers
app.include_router(portfolio_router, tags=["Portfolio"])
app.include_router(market_router, prefix=settings.api_v1_prefix, tags=["Market Data"])
app.include_router(
    economic_router, prefix=settings.api_v1_prefix, tags=["Economic Data"]
)
app.include_router(
    scheduler_router,
    prefix=f"{settings.api_v1_prefix}/scheduler",
    tags=["Data Scheduler"],
)

# User management router
from app.api.v1.users import router as users_router

app.include_router(users_router, tags=["Users"])

# Future routers (placeholder for extension)
# app.include_router(subscription_router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
