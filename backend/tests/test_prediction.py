"""
Tests for prediction endpoints.
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models.schemas import PredictionRequest

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestPredictionEndpoints:
    """Test class for prediction endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Fake News Detection API"
        assert "endpoints" in data

    def test_ping_endpoint(self):
        """Test ping endpoint."""
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json() == {"message": "pong"}

    def test_predict_single_valid_text(self):
        """Test single prediction with valid text."""
        request_data = {
            "text": "Breaking: Scientists discover cure for all diseases overnight!"
        }
        
        response = client.post("/predict/", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "text" in data
        assert "label" in data
        assert "confidence" in data
        assert data["label"] in ["FAKE", "REAL"]
        assert 0 <= data["confidence"] <= 1

    def test_predict_single_empty_text(self):
        """Test single prediction with empty text."""
        request_data = {"text": ""}
        
        response = client.post("/predict/", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_predict_single_too_long_text(self):
        """Test single prediction with too long text."""
        request_data = {"text": "a" * 10001}  # Over 10,000 characters
        
        response = client.post("/predict/", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_predict_batch_valid_texts(self):
        """Test batch prediction with valid texts."""
        request_data = {
            "texts": [
                "Breaking: Scientists discover cure for all diseases!",
                "Federal Reserve announces interest rate decision"
            ]
        }
        
        response = client.post("/predict/batch", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
        assert "total_count" in data
        assert len(data["predictions"]) == 2
        assert data["total_count"] == 2

    def test_predict_batch_too_many_texts(self):
        """Test batch prediction with too many texts."""
        request_data = {
            "texts": ["test"] * 101  # Over 100 texts
        }
        
        response = client.post("/predict/batch", json=request_data)
        assert response.status_code == 400  # Bad request

    def test_predict_batch_empty_texts(self):
        """Test batch prediction with empty texts list."""
        request_data = {"texts": []}
        
        response = client.post("/predict/batch", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_get_prediction_history(self):
        """Test getting prediction history."""
        # First make a prediction
        request_data = {"text": "Test prediction for history"}
        client.post("/predict/", json=request_data)
        
        # Then get history
        response = client.get("/predict/history")
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
        assert "total_count" in data
        assert "page" in data
        assert "page_size" in data

    def test_get_prediction_history_with_pagination(self):
        """Test getting prediction history with pagination."""
        response = client.get("/predict/history?skip=0&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
        assert "total_count" in data

    def test_search_predictions(self):
        """Test searching predictions."""
        # First make a prediction
        request_data = {"text": "Scientists discover breakthrough in quantum computing"}
        client.post("/predict/", json=request_data)
        
        # Then search
        response = client.get("/predict/search?q=scientists")
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
        assert "total_count" in data

    def test_search_predictions_empty_query(self):
        """Test searching predictions with empty query."""
        response = client.get("/predict/search?q=")
        assert response.status_code == 422  # Validation error

    def test_get_statistics(self):
        """Test getting prediction statistics."""
        response = client.get("/predict/statistics")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_predictions" in data
        assert "label_distribution" in data
        assert "average_confidence" in data
        assert "period_days" in data

    def test_get_statistics_with_days_filter(self):
        """Test getting statistics with days filter."""
        response = client.get("/predict/statistics?days_back=7")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 7

    def test_get_prediction_by_id(self):
        """Test getting prediction by ID."""
        # First make a prediction
        request_data = {"text": "Test prediction for ID retrieval"}
        response = client.post("/predict/", json=request_data)
        
        # Extract prediction ID (this would need to be implemented based on actual response)
        # For now, test with a non-existent ID
        response = client.get("/predict/999")
        assert response.status_code == 404  # Not found


class TestHealthEndpoints:
    """Test class for health endpoints."""

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health/")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "database_connected" in data
        assert "timestamp" in data

    def test_model_info(self):
        """Test model info endpoint."""
        response = client.get("/health/model")
        assert response.status_code == 200
        
        data = response.json()
        assert "model_path" in data
        assert "device" in data
        assert "model_type" in data
        assert "num_labels" in data
        assert "label_map" in data

    def test_database_status(self):
        """Test database status endpoint."""
        response = client.get("/health/database")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data


if __name__ == "__main__":
    pytest.main([__file__])
