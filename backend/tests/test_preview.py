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
    with patch("backend.app.main.fetch_hackernews_ai", return_value=(mock_hn_items, None)), \
         patch("backend.app.main.fetch_techcrunch_ai", return_value=([], None)), \
         patch("backend.app.main.fetch_arxiv_ai", return_value=([], None)):
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
    ), patch(
        "backend.app.main.fetch_techcrunch_ai",
        return_value=([], "TechCrunch fetch failed: boom"),
    ), patch(
        "backend.app.main.fetch_arxiv_ai",
        return_value=([], "arXiv fetch failed: boom"),
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is True
    assert "Preview data is mocked" in data["message"]
    assert data["warnings"] == [
        "Hacker News fetch failed: boom",
        "TechCrunch fetch failed: boom",
        "arXiv fetch failed: boom",
    ]


def test_preview_hn_fetch_raises_exception():
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        side_effect=RuntimeError("boom"),
    ), patch(
        "backend.app.main.fetch_techcrunch_ai",
        return_value=([], "TechCrunch fetch failed: boom"),
    ), patch(
        "backend.app.main.fetch_arxiv_ai",
        return_value=([], "arXiv fetch failed: boom"),
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is True
    assert "Preview data is mocked" in data["message"]
    assert data["warnings"] == [
        "Hacker News fetch failed: boom",
        "TechCrunch fetch failed: boom",
        "arXiv fetch failed: boom",
    ]


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


def test_preview_tc_enabled_with_hn():
    mock_hn_items = [
        {
            "source": "Hacker News",
            "title": "HN Story",
            "url": "https://example.com/hn",
            "score": 10,
        },
    ]
    mock_tc_items = [
        {
            "source": "TechCrunch AI",
            "title": "TC Article",
            "url": "https://techcrunch.com/ai",
            "score": 0,
        },
    ]
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        return_value=(mock_hn_items, None),
    ), patch(
        "backend.app.main.fetch_techcrunch_ai",
        return_value=(mock_tc_items, None),
    ), patch(
        "backend.app.main.fetch_arxiv_ai",
        return_value=([], None),
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is False
    assert data["warnings"] is None
    assert "live data" in data["message"]
    sources = [item["source"] for item in data["items"]]
    assert "Hacker News" in sources
    assert "TechCrunch AI" in sources


def test_preview_tc_limit_respected():
    mock_tc_items = [
        {
            "source": "TechCrunch AI",
            "title": f"TC {i}",
            "url": f"https://techcrunch.com/{i}",
            "score": 0,
        }
        for i in range(5)
    ]
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        return_value=([], None),
    ), patch(
        "backend.app.main.fetch_techcrunch_ai",
        return_value=(mock_tc_items, None),
    ) as mock_tc_fn:
        response = client.post(
            "/api/digest/preview",
            json={
                "sources": {"hn": False, "techcrunch": True},
                "limits": {"techcrunch": 2},
            },
        )

    assert response.status_code == 200
    mock_tc_fn.assert_called_once_with(limit=2)
    tc_items = [item for item in response.json()["items"] if item["source"] == "TechCrunch AI"]
    assert len(tc_items) == 2


def test_preview_tc_fetch_failure():
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        return_value=([], None),
    ), patch(
        "backend.app.main.fetch_techcrunch_ai",
        return_value=([], "TechCrunch fetch failed: boom"),
    ):
        response = client.post(
            "/api/digest/preview",
            json={"sources": {"hn": False, "techcrunch": True}},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is True
    assert data["warnings"] == ["TechCrunch fetch failed: boom"]
    assert "Preview data is mocked" in data["message"]


def test_preview_tc_disabled():
    with patch("backend.app.main.fetch_techcrunch_ai") as mock_tc_fn:
        response = client.post(
            "/api/digest/preview",
            json={"sources": {"hn": False, "techcrunch": False}},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is True
    assert all(item["source"] != "TechCrunch AI" for item in data["items"])
    assert data["warnings"] is None
    mock_tc_fn.assert_not_called()


def test_preview_hn_succeeds_tc_fails():
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        return_value=(
            [{"source": "Hacker News", "title": "HN OK", "url": "https://example.com/hn", "score": 10}],
            None,
        ),
    ), patch(
        "backend.app.main.fetch_techcrunch_ai",
        return_value=([], "TechCrunch fetch failed: boom"),
    ), patch(
        "backend.app.main.fetch_arxiv_ai",
        return_value=([], None),
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is False
    assert data["warnings"] == ["TechCrunch fetch failed: boom"]
    assert "live data" in data["message"]
    assert any(item["source"] == "Hacker News" for item in data["items"])
    assert not any(item["source"] == "TechCrunch AI" for item in data["items"])


def test_preview_tc_succeeds_hn_fails():
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        return_value=([], "Hacker News fetch failed: boom"),
    ), patch(
        "backend.app.main.fetch_techcrunch_ai",
        return_value=(
            [{"source": "TechCrunch AI", "title": "TC OK", "url": "https://techcrunch.com/ok", "score": 0}],
            None,
        ),
    ), patch(
        "backend.app.main.fetch_arxiv_ai",
        return_value=([], None),
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is False
    assert data["warnings"] == ["Hacker News fetch failed: boom"]
    assert "live data" in data["message"]
    assert any(item["source"] == "TechCrunch AI" for item in data["items"])
    assert not any(item["source"] == "Hacker News" for item in data["items"])


def test_preview_arxiv_disabled():
    with patch("backend.app.main.fetch_arxiv_ai") as mock_fn:
        response = client.post(
            "/api/digest/preview",
            json={"sources": {"hn": False, "techcrunch": False, "arxiv": False}},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is True
    assert all(item["source"] != "arXiv cs.AI" for item in data["items"])
    assert data["warnings"] is None
    mock_fn.assert_not_called()


def test_preview_arxiv_succeeds_while_hn_and_tc_fail():
    mock_arxiv_items = [
        {"source": "arXiv cs.AI", "title": "Paper 1", "url": "https://arxiv.org/abs/1", "score": 0},
    ]
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        return_value=([], "Hacker News fetch failed: boom"),
    ), patch(
        "backend.app.main.fetch_techcrunch_ai",
        return_value=([], "TechCrunch fetch failed: boom"),
    ), patch(
        "backend.app.main.fetch_arxiv_ai",
        return_value=(mock_arxiv_items, None),
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is False
    assert data["warnings"] == [
        "Hacker News fetch failed: boom",
        "TechCrunch fetch failed: boom",
    ]
    assert "live data" in data["message"]
    assert any(item["source"] == "arXiv cs.AI" for item in data["items"])
    assert not any(item["source"] == "Hacker News" for item in data["items"])
    assert not any(item["source"] == "TechCrunch AI" for item in data["items"])


def test_preview_hn_succeeds_while_arxiv_fails():
    mock_hn_items = [
        {"source": "Hacker News", "title": "HN OK", "url": "https://example.com/hn", "score": 10},
    ]
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        return_value=(mock_hn_items, None),
    ), patch(
        "backend.app.main.fetch_techcrunch_ai",
        return_value=([], None),
    ), patch(
        "backend.app.main.fetch_arxiv_ai",
        return_value=([], "arXiv fetch failed: boom"),
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is False
    assert data["warnings"] == ["arXiv fetch failed: boom"]
    assert "live data" in data["message"]
    assert any(item["source"] == "Hacker News" for item in data["items"])
    assert not any(item["source"] == "arXiv cs.AI" for item in data["items"])


def test_preview_tc_succeeds_while_arxiv_fails():
    mock_tc_items = [
        {"source": "TechCrunch AI", "title": "TC OK", "url": "https://techcrunch.com/ok", "score": 0},
    ]
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        return_value=([], None),
    ), patch(
        "backend.app.main.fetch_techcrunch_ai",
        return_value=(mock_tc_items, None),
    ), patch(
        "backend.app.main.fetch_arxiv_ai",
        return_value=([], "arXiv fetch failed: boom"),
    ):
        response = client.post("/api/digest/preview", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is False
    assert data["warnings"] == ["arXiv fetch failed: boom"]
    assert "live data" in data["message"]
    assert any(item["source"] == "TechCrunch AI" for item in data["items"])
    assert not any(item["source"] == "arXiv cs.AI" for item in data["items"])


def test_preview_arxiv_limit_respected():
    mock_arxiv_items = [
        {"source": "arXiv cs.AI", "title": f"Paper {i}", "url": f"https://arxiv.org/abs/{i}", "score": 0}
        for i in range(5)
    ]
    with (
        patch(
            "backend.app.main.fetch_hackernews_ai",
            return_value=([], None),
        ),
        patch(
            "backend.app.main.fetch_techcrunch_ai",
            return_value=([], None),
        ),
        patch(
            "backend.app.main.fetch_arxiv_ai",
            return_value=(mock_arxiv_items, None),
        ) as mock_arxiv_fn,
    ):
        response = client.post(
            "/api/digest/preview",
            json={"sources": {"hn": False, "techcrunch": False, "arxiv": True}, "limits": {"arxiv": 2}},
        )

    assert response.status_code == 200
    mock_arxiv_fn.assert_called_once_with(limit=2)
    arxiv_items = [item for item in response.json()["items"] if item["source"] == "arXiv cs.AI"]
    assert len(arxiv_items) == 2


def test_preview_arxiv_fetch_raises_exception():
    with patch(
        "backend.app.main.fetch_hackernews_ai",
        return_value=([], None),
    ), patch(
        "backend.app.main.fetch_techcrunch_ai",
        return_value=([], None),
    ), patch(
        "backend.app.main.fetch_arxiv_ai",
        side_effect=RuntimeError("boom"),
    ):
        response = client.post(
            "/api/digest/preview",
            json={"sources": {"hn": False, "techcrunch": False, "arxiv": True}},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is True
    assert data["warnings"] == ["arXiv fetch failed: boom"]
    assert "Preview data is mocked" in data["message"]
    assert not any(item["source"] == "arXiv cs.AI" for item in data["items"])


def test_health_endpoint_still_works():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
