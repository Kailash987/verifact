"""
Health check and system status routes.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import get_db, engine
from ..models.schemas import HealthResponse, ModelInfoResponse
from ..services import ml_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Health status information
    """
    try:
        # Check ML model status
        model_loaded = ml_service.is_model_loaded()
        
        # Check database connection
        database_connected = False
        try:
            db.execute(text("SELECT 1"))
            database_connected = True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
        
        status = "healthy" if model_loaded and database_connected else "unhealthy"
        
        return HealthResponse(
            status=status,
            model_loaded=model_loaded,
            database_connected=database_connected,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            database_connected=False,
            timestamp=datetime.now()
        )


@router.get("/model", response_model=ModelInfoResponse)
async def get_model_info():
    """
    Get model information.
    
    Returns:
        Model information
    """
    try:
        model_info = ml_service.get_model_info()
        return ModelInfoResponse(**model_info)
        
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")


@router.get("/database")
async def check_database(db: Session = Depends(get_db)):
    """
    Check database connectivity and status.
    
    Args:
        db: Database session
        
    Returns:
        Database status information
    """
    try:
        # Test database connection
        result = db.execute(text("SELECT version()"))
        db_version = result.scalar()
        
        # Get table counts
        predictions_count = db.execute(text("SELECT COUNT(*) FROM predictions")).scalar()
        
        return {
            "status": "connected",
            "version": db_version,
            "predictions_count": predictions_count,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return {
            "status": "disconnected",
            "error": str(e),
            "timestamp": datetime.now()
        }
