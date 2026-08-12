from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Verify that the /health route returns HTTP 200 and matches the expected schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "MediaDNA Backend"
    assert data["version"] == "0.1.0"
