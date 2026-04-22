"""
Database service for managing predictions and metrics.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta

from ..database import get_db, Prediction, ModelMetrics
from ..models.schemas import PredictionDB, PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service class for database operations."""
    
    def __init__(self):
        pass
    
    async def save_prediction(self, db: Session, prediction_data: Dict) -> Prediction:
        """
        Save prediction to database.
        
        Args:
            db: Database session
            prediction_data: Prediction data dictionary
            
        Returns:
            Saved prediction record
        """
        try:
            # Convert explanation to JSON string if present
            explanation_json = None
            if 'explanation' in prediction_data and prediction_data['explanation']:
                explanation_json = str(prediction_data['explanation'])
            
            prediction = Prediction(
                text=prediction_data['text'],
                prediction=prediction_data['label'],
                confidence=prediction_data['confidence'],
                explanation=explanation_json
            )
            
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
            
            logger.info(f"Saved prediction with ID: {prediction.id}")
            return prediction
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save prediction: {e}")
            raise
    
    async def get_prediction_history(self, db: Session, 
                                   skip: int = 0, 
                                   limit: int = 100,
                                   days_back: Optional[int] = None) -> List[Prediction]:
        """
        Get prediction history with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            days_back: Filter to last N days
            
        Returns:
            List of prediction records
        """
        try:
            query = db.query(Prediction)
            
            # Filter by date if specified
            if days_back:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                query = query.filter(Prediction.created_at >= cutoff_date)
            
            predictions = query.order_by(desc(Prediction.created_at)).offset(skip).limit(limit).all()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to get prediction history: {e}")
            raise
    
    async def get_prediction_by_id(self, db: Session, prediction_id: int) -> Optional[Prediction]:
        """
        Get prediction by ID.
        
        Args:
            db: Database session
            prediction_id: Prediction ID
            
        Returns:
            Prediction record or None
        """
        try:
            return db.query(Prediction).filter(Prediction.id == prediction_id).first()
        except Exception as e:
            logger.error(f"Failed to get prediction by ID: {e}")
            raise
    
    async def get_prediction_statistics(self, db: Session, days_back: int = 30) -> Dict[str, Any]:
        """
        Get prediction statistics.
        
        Args:
            db: Database session
            days_back: Number of days to look back
            
        Returns:
            Statistics dictionary
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Total predictions
            total_predictions = db.query(Prediction).filter(
                Prediction.created_at >= cutoff_date
            ).count()
            
            # Predictions by label
            label_counts = db.query(
                Prediction.prediction,
                func.count(Prediction.id)
            ).filter(
                Prediction.created_at >= cutoff_date
            ).group_by(Prediction.prediction).all()
            
            # Average confidence
            avg_confidence = db.query(
                func.avg(Prediction.confidence)
            ).filter(
                Prediction.created_at >= cutoff_date
            ).scalar()
            
            # Daily prediction counts
            daily_counts = db.query(
                func.date(Prediction.created_at),
                func.count(Prediction.id)
            ).filter(
                Prediction.created_at >= cutoff_date
            ).group_by(func.date(Prediction.created_at)).all()
            
            statistics = {
                'total_predictions': total_predictions,
                'label_distribution': dict(label_counts),
                'average_confidence': float(avg_confidence) if avg_confidence else 0.0,
                'daily_counts': [
                    {'date': str(date), 'count': count} 
                    for date, count in daily_counts
                ],
                'period_days': days_back
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get prediction statistics: {e}")
            raise
    
    async def save_model_metrics(self, db: Session, metrics_data: Dict) -> ModelMetrics:
        """
        Save model performance metrics.
        
        Args:
            db: Database session
            metrics_data: Metrics data dictionary
            
        Returns:
            Saved metrics record
        """
        try:
            metrics = ModelMetrics(
                model_version=metrics_data.get('model_version', 'unknown'),
                accuracy=metrics_data.get('accuracy'),
                precision=metrics_data.get('precision'),
                recall=metrics_data.get('recall'),
                f1_score=metrics_data.get('f1_score')
            )
            
            db.add(metrics)
            db.commit()
            db.refresh(metrics)
            
            logger.info(f"Saved model metrics with ID: {metrics.id}")
            return metrics
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save model metrics: {e}")
            raise
    
    async def get_latest_model_metrics(self, db: Session) -> Optional[ModelMetrics]:
        """
        Get latest model metrics.
        
        Args:
            db: Database session
            
        Returns:
            Latest metrics record or None
        """
        try:
            return db.query(ModelMetrics).order_by(desc(ModelMetrics.training_date)).first()
        except Exception as e:
            logger.error(f"Failed to get latest model metrics: {e}")
            raise
    
    async def delete_old_predictions(self, db: Session, days_to_keep: int = 90) -> int:
        """
        Delete old predictions to manage database size.
        
        Args:
            db: Database session
            days_to_keep: Number of days to keep predictions
            
        Returns:
            Number of deleted records
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            deleted_count = db.query(Prediction).filter(
                Prediction.created_at < cutoff_date
            ).delete()
            
            db.commit()
            
            logger.info(f"Deleted {deleted_count} old predictions")
            return deleted_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete old predictions: {e}")
            raise
    
    async def search_predictions(self, db: Session, 
                               search_term: str,
                               skip: int = 0,
                               limit: int = 50) -> List[Prediction]:
        """
        Search predictions by text content.
        
        Args:
            db: Database session
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching prediction records
        """
        try:
            predictions = db.query(Prediction).filter(
                Prediction.text.ilike(f'%{search_term}%')
            ).order_by(desc(Prediction.created_at)).offset(skip).limit(limit).all()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to search predictions: {e}")
            raise


# Global database service instance
db_service = DatabaseService()
