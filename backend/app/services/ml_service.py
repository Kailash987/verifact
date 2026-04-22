"""
Machine Learning service for fake news detection.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add ML directory to path to import our modules
ML_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../ml'))
sys.path.append(ML_DIR)

try:
    from inference import FakeNewsPredictor
except ImportError:
    # Fallback if ML module is not available
    FakeNewsPredictor = None

logger = logging.getLogger(__name__)


class MLService:
    """
    Service class for ML model inference with singleton pattern.
    """
    
    _instance = None
    _predictor = None
    _executor = ThreadPoolExecutor(max_workers=4)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._predictor is None:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the ML model."""
        try:
            model_path = os.getenv("MODEL_PATH", os.path.join(ML_DIR, "model", "best_model"))
            if FakeNewsPredictor:
                self._predictor = FakeNewsPredictor(model_path)
                logger.info("ML model loaded successfully")
            else:
                logger.warning("ML module not available, using mock predictions")
                self._predictor = MockPredictor()
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            self._predictor = MockPredictor()
    
    async def predict_single(self, text: str, include_explanation: bool = True) -> Dict:
        """
        Predict single text asynchronously.
        
        Args:
            text: Input text to classify
            include_explanation: Whether to include explanation
            
        Returns:
            Prediction result dictionary
        """
        loop = asyncio.get_event_loop()
        
        try:
            if include_explanation:
                result = await loop.run_in_executor(
                    self._executor, 
                    self._predictor.predict_with_explanation,
                    text,
                    'lime'
                )
                
                # Format response to match expected schema
                response = {
                    'text': result['text'],
                    'label': result['prediction']['label'],
                    'confidence': result['prediction']['confidence'],
                    'explanation': {
                        'method': result['explanation']['method'],
                        'important_words': result['explanation']['important_words'],
                        'word_weights': result['explanation']['word_weights']
                    }
                }
            else:
                result = await loop.run_in_executor(
                    self._executor,
                    self._predictor.predict_single,
                    text
                )
                
                response = {
                    'text': result['text'],
                    'label': result['label'],
                    'confidence': result['confidence'],
                    'explanation': None
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    async def predict_batch(self, texts: List[str], include_explanation: bool = False) -> List[Dict]:
        """
        Predict multiple texts asynchronously.
        
        Args:
            texts: List of input texts
            include_explanation: Whether to include explanations
            
        Returns:
            List of prediction results
        """
        tasks = []
        for text in texts:
            task = self.predict_single(text, include_explanation)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Prediction failed for text {i}: {result}")
                formatted_results.append({
                    'text': texts[i],
                    'label': 'ERROR',
                    'confidence': 0.0,
                    'explanation': None,
                    'error': str(result)
                })
            else:
                formatted_results.append(result)
        
        return formatted_results
    
    def get_model_info(self) -> Dict:
        """
        Get model information.
        
        Returns:
            Model information dictionary
        """
        try:
            if hasattr(self._predictor, 'get_model_info'):
                return self._predictor.get_model_info()
            else:
                return {
                    'model_path': 'Mock model',
                    'device': 'CPU',
                    'model_type': 'MockPredictor',
                    'num_labels': 2,
                    'label_map': {0: 'REAL', 1: 'FAKE'}
                }
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {'error': str(e)}
    
    def is_model_loaded(self) -> bool:
        """
        Check if model is loaded.
        
        Returns:
            True if model is loaded, False otherwise
        """
        return self._predictor is not None


class MockPredictor:
    """
    Mock predictor for when ML model is not available.
    """
    
    def __init__(self):
        self.model_path = "mock_model"
        
    def predict_single(self, text: str, return_probabilities: bool = True) -> Dict:
        """Mock prediction based on simple heuristics."""
        # Simple heuristic based on common fake news indicators
        fake_indicators = ['breaking', 'shocking', 'miracle', 'secret', 'conspiracy', 'overnight']
        text_lower = text.lower()
        
        fake_score = sum(1 for indicator in fake_indicators if indicator in text_lower)
        is_fake = fake_score >= 2
        
        confidence = 0.6 + (fake_score * 0.1) if is_fake else 0.7 - (fake_score * 0.05)
        confidence = min(0.95, max(0.5, confidence))
        
        result = {
            'text': text,
            'label': 'FAKE' if is_fake else 'REAL',
            'confidence': round(confidence, 3),
            'predicted_class_id': 1 if is_fake else 0
        }
        
        if return_probabilities:
            result['probabilities'] = {
                'REAL': round(1 - confidence, 3),
                'FAKE': round(confidence, 3)
            }
        
        return result
    
    def predict_with_explanation(self, text: str, method: str = 'lime') -> Dict:
        """Mock prediction with explanation."""
        prediction = self.predict_single(text)
        
        # Generate mock important words
        words = text.lower().split()
        fake_indicators = ['breaking', 'shocking', 'miracle', 'secret', 'conspiracy']
        important_words = [word for word in words if word in fake_indicators][:5]
        
        if not important_words:
            important_words = words[:3]  # Use first few words if no indicators
        
        result = {
            'text': text,
            'prediction': prediction,
            'explanation': {
                'method': 'LIME',
                'important_words': important_words,
                'word_weights': {word: 0.2 for word in important_words}
            }
        }
        
        return result
    
    def get_model_info(self) -> Dict:
        """Get mock model info."""
        return {
            'model_path': 'mock_model',
            'device': 'CPU',
            'model_type': 'MockPredictor',
            'num_labels': 2,
            'label_map': {0: 'REAL', 1: 'FAKE'}
        }


# Global ML service instance
ml_service = MLService()
