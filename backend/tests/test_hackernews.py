from unittest.mock import patch, MagicMock
import json

from backend.app.sources.hackernews import fetch_hackernews_ai


def _make_hit(object_id, title, url, points):
    return {"objectID": object_id, "title": title, "url": url, "points": points}


def _mock_response(hits):
    data = json.dumps({"hits": hits}).encode()
    response = MagicMock()
    response.read.return_value = data
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)
    return response


def test_fetch_hackernews_ai_returns_items():
    hits = [
        _make_hit("1", "Test HN story", "https://example.com/story1", 100),
        _make_hit("2", "Another story", "https://example.com/story2", 50),
    ]

    with patch("backend.app.sources.hackernews._urlopen", return_value=_mock_response(hits)):
        items, error = fetch_hackernews_ai(limit=2)

    assert len(items) == 2
    assert items[0]["source"] == "Hacker News"
    assert items[0]["title"] == "Test HN story"
    assert items[0]["url"] == "https://example.com/story1"
    assert items[0]["score"] == 100
    assert error is None


def test_fetch_hackernews_ai_deduplicates():
    hits = [
        _make_hit("1", "Story A", "https://example.com/a", 10),
        _make_hit("2", "Story B", "https://example.com/b", 20),
        _make_hit("3", "Story A dup", "https://example.com/a", 15),
    ]

    with patch("backend.app.sources.hackernews._urlopen", return_value=_mock_response(hits)):
        items, error = fetch_hackernews_ai(limit=10)

    assert len(items) == 2
    assert error is None


def test_fetch_hackernews_ai_handles_network_failure():
    with patch("backend.app.sources.hackernews._urlopen", side_effect=ConnectionError("network down")):
        items, error = fetch_hackernews_ai(limit=5)

    assert items == []
    assert error is not None
    assert "network down" in error


def test_fetch_hackernews_ai_missing_url_falls_back():
    hits = [
        _make_hit("99", "No external link", None, 10),
    ]

    with patch("backend.app.sources.hackernews._urlopen", return_value=_mock_response(hits)):
        items, error = fetch_hackernews_ai(limit=5)

    assert len(items) == 1
    assert items[0]["url"] == "https://news.ycombinator.com/item?id=99"
    assert error is None


def test_fetch_hackernews_ai_normalizes_null_points():
    hits = [
        _make_hit("1", "Story with null points", "https://example.com/x", None),
        _make_hit("2", "Story with valid points", "https://example.com/y", 42),
    ]

    with patch("backend.app.sources.hackernews._urlopen", return_value=_mock_response(hits)):
        items, error = fetch_hackernews_ai(limit=10)

    scores = {item["score"] for item in items}
    assert 0 in scores
    assert 42 in scores
    assert error is None
