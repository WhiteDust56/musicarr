import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.routers.settings import get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Use standard testing override pattern for DB if needed,
    # but here we can just rely on the existing schema in app.db
    # since we are only testing GET endpoints that return defaults or current state.
    yield

def test_get_settings():
    response = client.get("/api/settings/")
    assert response.status_code == 200
    data = response.json()
    assert "indexer_url" in data
    assert "sabnzbd_url" in data
    assert "quality" in data
    # Check default download path
    assert data["download_path"] == "./downloads"
