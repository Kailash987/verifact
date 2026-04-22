"""
Prediction routes for the fake news detection API.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schemas import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionHistoryResponse,
    PredictionDB
)
from ..services import ml_service, db_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/", response_model=PredictionResponse)
async def predict_single(
    request: PredictionRequest,
    include_explanation: bool = Query(True, description="Include LIME explanation"),
    db: Session = Depends(get_db)
):
    """
    Predict if a given text is fake or real news.
    
    Args:
        request: Prediction request containing text
        include_explanation: Whether to include explanation
        db: Database session
        
    Returns:
        Prediction result with confidence and explanation
    """
    try:
        # Get prediction from ML service
        prediction_result = await ml_service.predict_single(
            request.text, 
            include_explanation
        )
        
        # Save to database
        await db_service.save_prediction(db, prediction_result)
        
        logger.info(f"Prediction made for text: {request.text[:50]}...")
        return prediction_result
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    request: BatchPredictionRequest,
    include_explanation: bool = Query(False, description="Include explanations for batch predictions"),
    db: Session = Depends(get_db)
):
    """
    Predict multiple texts in batch.
    
    Args:
        request: Batch prediction request containing texts
        include_explanation: Whether to include explanations
        db: Database session
        
    Returns:
        Batch prediction results
    """
    try:
        # Validate batch size
        if len(request.texts) > 100:
            raise HTTPException(
                status_code=400, 
                detail="Batch size too large. Maximum 100 texts allowed."
            )
        
        # Get predictions from ML service
        prediction_results = await ml_service.predict_batch(
            request.texts,
            include_explanation
        )
        
        # Save predictions to database
        for result in prediction_results:
            if 'error' not in result:  # Only save successful predictions
                await db_service.save_prediction(db, result)
        
        response = BatchPredictionResponse(
            predictions=prediction_results,
            total_count=len(prediction_results)
        )
        
        logger.info(f"Batch prediction completed for {len(request.texts)} texts")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@router.get("/history", response_model=PredictionHistoryResponse)
async def get_prediction_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    days_back: Optional[int] = Query(None, ge=1, le=365, description="Filter to last N days"),
    db: Session = Depends(get_db)
):
    """
    Get prediction history with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        days_back: Filter to last N days
        db: Database session
        
    Returns:
        Paginated prediction history
    """
    try:
        predictions = await db_service.get_prediction_history(
            db, skip=skip, limit=limit, days_back=days_back
        )
        
        # Convert to response schema
        prediction_responses = [
            PredictionDB(
                id=p.id,
                text=p.text,
                prediction=p.prediction,
                confidence=p.confidence,
                explanation=p.explanation,
                created_at=p.created_at
            )
            for p in predictions
        ]
        
        # Get total count for pagination
        total_count = len(prediction_responses)
        
        response = PredictionHistoryResponse(
            predictions=prediction_responses,
            total_count=total_count,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to get prediction history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/search")
async def search_predictions(
    q: str = Query(..., min_length=1, description="Search term"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Search predictions by text content.
    
    Args:
        q: Search term
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        Search results
    """
    try:
        predictions = await db_service.search_predictions(
            db, search_term=q, skip=skip, limit=limit
        )
        
        # Convert to response schema
        prediction_responses = [
            PredictionDB(
                id=p.id,
                text=p.text,
                prediction=p.prediction,
                confidence=p.confidence,
                explanation=p.explanation,
                created_at=p.created_at
            )
            for p in predictions
        ]
        
        return {"predictions": prediction_responses, "total_count": len(prediction_responses)}
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/statistics")
async def get_prediction_statistics(
    days_back: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """
    Get prediction statistics.
    
    Args:
        days_back: Number of days to look back
        db: Database session
        
    Returns:
        Prediction statistics
    """
    try:
        statistics = await db_service.get_prediction_statistics(db, days_back=days_back)
        return statistics
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/{prediction_id}", response_model=PredictionDB)
async def get_prediction_by_id(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific prediction by ID.
    
    Args:
        prediction_id: Prediction ID
        db: Database session
        
    Returns:
        Prediction record
    """
    try:
        prediction = await db_service.get_prediction_by_id(db, prediction_id)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        return PredictionDB(
            id=prediction.id,
            text=prediction.text,
            prediction=prediction.prediction,
            confidence=prediction.confidence,
            explanation=prediction.explanation,
            created_at=prediction.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get prediction: {str(e)}")
