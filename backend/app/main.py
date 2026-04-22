"""
Main FastAPI application for fake news detection.
"""

import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .database import create_tables
from .routes import prediction_router, health_router
from .models.schemas import ErrorResponse
from .utils.rate_limiter import RateLimitMiddleware, rate_limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up Fake News Detection API...")
    
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Fake News Detection API...")


# Create FastAPI application
app = FastAPI(
    title="Fake News Detection API",
    description="A production-ready API for detecting fake news and misinformation using modern ML/NLP techniques.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred. Please try again later.",
            timestamp=datetime.now()
        ).dict()
    )


# Include routers
app.include_router(prediction_router)
app.include_router(health_router)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        API information
    """
    return {
        "name": "Fake News Detection API",
        "version": "1.0.0",
        "description": "A production-ready API for detecting fake news and misinformation",
        "endpoints": {
            "prediction": "/predict",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "status": "running"
    }


# Additional health endpoint
@app.get("/ping")
async def ping():
    """
    Simple ping endpoint for connectivity testing.
    
    Returns:
        Pong response
    """
    return {"message": "pong"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
