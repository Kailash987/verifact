"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request schema for text prediction."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to classify")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Breaking: Scientists discover cure for all diseases overnight!"
            }
        }


class BatchPredictionRequest(BaseModel):
    """Request schema for batch prediction."""
    texts: List[str] = Field(..., min_items=1, max_items=100, description="List of texts to classify")
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "Breaking: Scientists discover cure for all diseases!",
                    "Federal Reserve announces interest rate decision"
                ]
            }
        }


class ExplanationResponse(BaseModel):
    """Response schema for explanation."""
    method: str
    important_words: List[str]
    word_weights: Dict[str, float]


class PredictionResponse(BaseModel):
    """Response schema for single prediction."""
    text: str
    label: str = Field(..., description="Prediction label (FAKE or REAL)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    explanation: Optional[ExplanationResponse] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Breaking: Scientists discover cure for all diseases!",
                "label": "FAKE",
                "confidence": 0.92,
                "explanation": {
                    "method": "LIME",
                    "important_words": ["breaking", "scientists", "discover", "cure"],
                    "word_weights": {"breaking": 0.3, "scientists": 0.25, "discover": 0.2, "cure": 0.15}
                }
            }
        }


class BatchPredictionResponse(BaseModel):
    """Response schema for batch prediction."""
    predictions: List[PredictionResponse]
    total_count: int


class PredictionDB(BaseModel):
    """Schema for prediction database record."""
    id: int
    text: str
    prediction: str
    confidence: float
    explanation: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str
    model_loaded: bool
    database_connected: bool
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime


class ModelInfoResponse(BaseModel):
    """Response schema for model information."""
    model_path: str
    device: str
    model_type: str
    num_labels: int
    label_map: Dict[str, str]


class PredictionHistoryResponse(BaseModel):
    """Response schema for prediction history."""
    predictions: List[PredictionDB]
    total_count: int
    page: int
    page_size: int
