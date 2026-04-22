"""
Database models for fake news detection application.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from .connection import Base


class Prediction(Base):
    """
    Model for storing prediction history.
    """
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    prediction = Column(String(10), nullable=False)  # "FAKE" or "REAL"
    confidence = Column(Float, nullable=False)
    explanation = Column(Text)  # JSON string of explanation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, text='{self.text[:50]}...', prediction='{self.prediction}')>"


class ModelMetrics(Base):
    """
    Model for storing model performance metrics.
    """
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String(50), nullable=False)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    training_date = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ModelMetrics(id={self.id}, version='{self.model_version}', f1={self.f1_score})>"
