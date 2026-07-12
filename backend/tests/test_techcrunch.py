from unittest.mock import patch, MagicMock

from backend.app.sources.techcrunch import fetch_techcrunch_ai


_RSS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
{entries}
  </channel>
</rss>"""


def _rss_entry(title, link):
    return (
        f"    <item>\n"
        f"      <title>{title}</title>\n"
        f"      <link>{link}</link>\n"
        f"    </item>"
    )


def _make_rss_feed(entries):
    items_xml = "\n".join(_rss_entry(t, l) for t, l in entries)
    return _RSS_TEMPLATE.format(entries=items_xml).encode("utf-8")


def _mock_response(rss_bytes):
    response = MagicMock()
    response.read.return_value = rss_bytes
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)
    return response


def test_fetch_techcrunch_ai_returns_items():
    entries = [
        ("OpenAI launches new GPT model", "https://techcrunch.com/openai-gpt"),
        ("Google Gemini advances in reasoning", "https://techcrunch.com/gemini"),
    ]
    rss = _make_rss_feed(entries)

    with patch(
        "backend.app.sources.techcrunch._urlopen",
        return_value=_mock_response(rss),
    ):
        items, error = fetch_techcrunch_ai(limit=5)

    assert len(items) == 2
    assert items[0]["source"] == "TechCrunch AI"
    assert items[0]["title"] == "OpenAI launches new GPT model"
    assert items[0]["url"] == "https://techcrunch.com/openai-gpt"
    assert items[0]["score"] == 0
    assert error is None


def test_fetch_techcrunch_ai_filters_non_ai_topics():
    entries = [
        ("OpenAI launches new GPT model", "https://techcrunch.com/openai"),
        ("New social media app raises funding", "https://techcrunch.com/social"),
        ("Google Gemini advances in reasoning", "https://techcrunch.com/gemini"),
    ]
    rss = _make_rss_feed(entries)

    with patch(
        "backend.app.sources.techcrunch._urlopen",
        return_value=_mock_response(rss),
    ):
        items, error = fetch_techcrunch_ai(limit=10)

    assert len(items) == 2
    titles = {item["title"] for item in items}
    assert "New social media app raises funding" not in titles
    assert "OpenAI launches new GPT model" in titles
    assert "Google Gemini advances in reasoning" in titles
    assert error is None


def test_fetch_techcrunch_ai_respects_limit():
    entries = [
        (f"AI Article {i}", f"https://techcrunch.com/ai-{i}")
        for i in range(10)
    ]
    rss = _make_rss_feed(entries)

    with patch(
        "backend.app.sources.techcrunch._urlopen",
        return_value=_mock_response(rss),
    ):
        items, error = fetch_techcrunch_ai(limit=3)

    assert len(items) == 3
    assert error is None


def test_fetch_techcrunch_ai_deduplicates():
    entries = [
        ("Same AI article", "https://techcrunch.com/dup"),
        ("Same AI article again", "https://techcrunch.com/dup"),
        ("Different AI article", "https://techcrunch.com/diff"),
    ]
    rss = _make_rss_feed(entries)

    with patch(
        "backend.app.sources.techcrunch._urlopen",
        return_value=_mock_response(rss),
    ):
        items, error = fetch_techcrunch_ai(limit=10)

    assert len(items) == 2
    urls = [item["url"] for item in items]
    assert urls == ["https://techcrunch.com/dup", "https://techcrunch.com/diff"]
    assert error is None


def test_fetch_techcrunch_ai_handles_missing_fields():
    # RSS entry with missing title or empty/non-http link
    entries = [
        ("", "https://techcrunch.com/empty-title"),                 # empty title → skipped
        ("AI article with no valid link", ""),                       # empty link → skipped
        ("  spaced title  ", "https://techcrunch.com/spaced"),      # valid non-AI (no kw match)
        ("OpenAI releases new model", "https://techcrunch.com/ai1"), # valid AI entry
    ]
    rss = _make_rss_feed(entries)

    with patch(
        "backend.app.sources.techcrunch._urlopen",
        return_value=_mock_response(rss),
    ):
        items, error = fetch_techcrunch_ai(limit=10)

    assert len(items) == 1
    assert items[0]["title"] == "OpenAI releases new model"
    assert items[0]["url"] == "https://techcrunch.com/ai1"
    assert error is None


def test_fetch_techcrunch_ai_handles_upstream_network_failure():
    with patch(
        "backend.app.sources.techcrunch._urlopen",
        side_effect=ConnectionError("network down"),
    ):
        items, error = fetch_techcrunch_ai(limit=5)

    assert items == []
    assert error is not None
    assert "network down" in error


def test_fetch_techcrunch_ai_no_items_returns_error():
    entries = [
        ("New mobile game review", "https://techcrunch.com/game"),
        ("Startup funding round announced", "https://techcrunch.com/startup"),
    ]
    rss = _make_rss_feed(entries)

    with patch(
        "backend.app.sources.techcrunch._urlopen",
        return_value=_mock_response(rss),
    ):
        items, error = fetch_techcrunch_ai(limit=10)

    assert items == []
    assert error is not None
    assert "no items found" in error


def test_fetch_techcrunch_ai_limit_clamped_to_min():
    entries = [
        ("AI 0", "https://techcrunch.com/ai-0"),
    ]
    rss = _make_rss_feed(entries)

    with patch(
        "backend.app.sources.techcrunch._urlopen",
        return_value=_mock_response(rss),
    ):
        items, error = fetch_techcrunch_ai(limit=-5)

    # Clamped to min=1
    assert len(items) == 1
    assert error is None


def test_fetch_techcrunch_ai_limit_clamped_to_max():
    entries = [
        (f"AI {i}", f"https://techcrunch.com/ai-{i}")
        for i in range(25)
    ]
    rss = _make_rss_feed(entries)

    with patch(
        "backend.app.sources.techcrunch._urlopen",
        return_value=_mock_response(rss),
    ):
        items, error = fetch_techcrunch_ai(limit=100)

    # Clamped to max=20
    assert len(items) == 20
    assert error is None
