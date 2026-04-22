"""
Initialize database tables.
"""

from .connection import engine, Base
from .models import Prediction, ModelMetrics


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()
