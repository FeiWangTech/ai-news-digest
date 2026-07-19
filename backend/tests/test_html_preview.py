from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_preview_returns_html_field_with_items():
    mock_hn_items = [
        {"source": "Hacker News", "title": "HN Story", "url": "https://example.com/1", "score": 100},
    ]
    with patch(
        "backend.app.main.fetch_hackernews_ai", return_value=(mock_hn_items, None)
    ), patch(
        "backend.app.main.fetch_techcrunch_ai", return_value=([], None)
    ), patch(
        "backend.app.main.fetch_arxiv_ai", return_value=([], None)
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["html"] is not None
    assert "<!DOCTYPE html>" in data["html"]
    assert "HN Story" in data["html"]
    assert "https://example.com/1" in data["html"]
    assert "<style" not in data["html"]
    assert "color:#eaeaea;" in data["html"]
    assert "font-family:-apple-system" in data["html"]


def test_preview_returns_html_field_empty_items():
    with patch(
        "backend.app.main.fetch_hackernews_ai", return_value=([], None)
    ), patch(
        "backend.app.main.fetch_techcrunch_ai", return_value=([], None)
    ), patch(
        "backend.app.main.fetch_arxiv_ai", return_value=([], None)
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["html"] is not None
    assert "No items available" in data["html"]


def test_preview_returns_html_field_includes_tip():
    with patch(
        "backend.app.main.fetch_hackernews_ai", return_value=([], None)
    ), patch(
        "backend.app.main.fetch_techcrunch_ai", return_value=([], None)
    ), patch(
        "backend.app.main.fetch_arxiv_ai", return_value=([], None)
    ):
        response = client.post(
            "/api/digest/preview",
            json={"sources": {"hn": False, "techcrunch": False, "arxiv": False, "tip": True}},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["html"] is not None
    assert "Tip</h3>" in data["html"]
    assert "Mock AI Engineer Lifecycle Tip: use pydantic models." in data["html"]
