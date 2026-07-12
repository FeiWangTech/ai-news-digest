from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_preview_valid_defaults():
    mock_hn_items = [
        {
            "source": "Hacker News",
            "title": "HN Story 1",
            "url": "https://example.com/1",
            "score": 100,
        },
    ]
    with patch("backend.app.main.fetch_hackernews_ai", return_value=(mock_hn_items, None)):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is False
    assert "live data" in data["message"]
    assert len(data["items"]) > 0
    assert data["tip"] is not None
    assert data["warnings"] is None


def test_preview_valid_custom_sources():
    mock_hn_items = [
        {
            "source": "Hacker News",
            "title": "HN Story",
            "url": "https://example.com/hn",
            "score": 10,
        },
    ]
    with patch("backend.app.main.fetch_hackernews_ai", return_value=(mock_hn_items, None)):
        response = client.post(
            "/api/digest/preview",
            json={"sources": {"hn": True, "techcrunch": False}, "limits": {"hn": 1}},
        )

    assert response.status_code == 200
    data = response.json()
    assert all(item["source"] == "Hacker News" for item in data["items"])
    assert len(data["items"]) == 1
    assert data["mock"] is False


def test_preview_hn_limit_respected():
    mock_items = [
        {
            "source": "Hacker News",
            "title": f"Story {i}",
            "url": f"https://example.com/{i}",
            "score": i,
        }
        for i in range(5)
    ]
    with patch(
        "backend.app.main.fetch_hackernews_ai", return_value=(mock_items, None)
    ) as mock_fn:
        response = client.post(
            "/api/digest/preview",
            json={"sources": {"hn": True, "techcrunch": False}, "limits": {"hn": 2}},
        )

    assert response.status_code == 200
    data = response.json()
    mock_fn.assert_called_once_with(limit=2)
    hn_items = [item for item in data["items"] if item["source"] == "Hacker News"]
    assert len(hn_items) == 2
    assert data["mock"] is False


def test_preview_hn_fetch_failure():
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        return_value=([], "Hacker News fetch failed: boom"),
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is True
    assert "Preview data is mocked" in data["message"]
    assert data["warnings"] == ["Hacker News fetch failed: boom"]


def test_preview_hn_fetch_raises_exception():
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        side_effect=RuntimeError("boom"),
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is True
    assert "Preview data is mocked" in data["message"]
    assert data["warnings"] == ["Hacker News fetch failed: boom"]


def test_preview_hn_disabled():
    with patch("backend.app.main.fetch_hackernews_ai") as mock_fn:
        response = client.post(
            "/api/digest/preview",
            json={"sources": {"hn": False}},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is True
    assert "Preview data is mocked" in data["message"]
    assert all(item["source"] != "Hacker News" for item in data["items"])
    assert data["warnings"] is None
    mock_fn.assert_not_called()


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
