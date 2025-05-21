import pytest
from fastapi.testclient import TestClient

from app.db.mongodb import MongoDB
from app.main import app


@pytest.fixture(scope="module")
def test_client():
    """
    Create a test client for the FastAPI application.
    """
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
async def setup_and_teardown():
    """
    Setup and teardown for tests.
    """
    # Setup: Connect to MongoDB
    await MongoDB.connect_db()
    
    yield  # This is where the testing happens
    
    # Teardown: Close MongoDB connection
    await MongoDB.close_db()
