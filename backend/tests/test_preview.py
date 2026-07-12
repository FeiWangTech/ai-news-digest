from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_preview_valid_defaults():
    response = client.post("/api/digest/preview", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is True
    assert "Preview data is mocked" in data["message"]
    assert len(data["items"]) > 0
    assert data["tip"] is not None


def test_preview_valid_custom_sources():
    response = client.post(
        "/api/digest/preview",
        json={"sources": {"hn": True, "techcrunch": False}, "limits": {"hn": 1}},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["source"] == "Hacker News" for item in data["items"])
    assert len(data["items"]) == 1


def test_preview_invalid_source_key():
    response = client.post(
        "/api/digest/preview",
        json={"sources": {"unknown": True}},
    )
    assert response.status_code == 422


def test_preview_invalid_limit():
    response = client.post(
        "/api/digest/preview",
        json={"limits": {"hn": 99}},
    )
    assert response.status_code == 422


def test_preview_invalid_limit_key():
    response = client.post(
        "/api/digest/preview",
        json={"limits": {"youtube": 5}},
    )
    assert response.status_code == 422


def test_health_endpoint_still_works():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
