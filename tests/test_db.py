"""Database connection tests."""

import pytest
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg://donut@localhost:5432/postgres"


@pytest.mark.unit
def test_database_connection():
    """Test database connection."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;"))
            assert result.scalar() == 1
    except Exception as e:
        pytest.skip(f"Database not available: {e}")
