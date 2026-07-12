from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

from backend.app.sources.arxiv import fetch_arxiv_ai

_ATOM_NS = "http://www.w3.org/2005/Atom"


def _make_atom_feed(entries):
    entries_xml = "".join(
        (
            f"    <entry>\n"
            f"      <title>{title}</title>\n"
            f'      <link href="{link}" rel="alternate" />\n'
            f"      <id>{arxiv_id}</id>\n"
            f"    </entry>\n"
        )
        for title, link, arxiv_id in entries
    )
    xml = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f"<feed xmlns=\"{_ATOM_NS}\">\n"
        f"{entries_xml}</feed>"
    )
    return xml.encode("utf-8")


def _mock_response(data_bytes):
    response = MagicMock()
    response.read.return_value = data_bytes
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)
    return response


def test_fetch_arxiv_ai_returns_items():
    entries = [
        (
            "Attention Is All You Need",
            "https://arxiv.org/abs/1706.03762",
            "http://arxiv.org/abs/1706.03762v1",
        ),
        (
            "BERT: Pre-training of Deep Bidirectional Transformers",
            "https://arxiv.org/abs/1810.04805",
            "http://arxiv.org/abs/1810.04805v2",
        ),
    ]
    atom = _make_atom_feed(entries)

    with patch(
        "backend.app.sources.arxiv._urlopen",
        return_value=_mock_response(atom),
    ):
        items, error = fetch_arxiv_ai(limit=5)

    assert len(items) == 2
    assert items[0]["source"] == "arXiv cs.AI"
    assert items[0]["title"] == "Attention Is All You Need"
    assert items[0]["url"] == "https://arxiv.org/abs/1706.03762"
    assert items[0]["score"] == 0
    assert error is None


def test_fetch_arxiv_ai_handles_namespaces():
    entries = [
        (
            "Namespaced paper",
            "https://arxiv.org/abs/2301.00001",
            "http://arxiv.org/abs/2301.00001v1",
        ),
    ]
    atom = _make_atom_feed(entries)

    with patch(
        "backend.app.sources.arxiv._urlopen",
        return_value=_mock_response(atom),
    ):
        items, error = fetch_arxiv_ai(limit=1)

    assert len(items) == 1
    assert error is None


def test_fetch_arxiv_ai_normalizes_title_whitespace():
    entries = [
        (
            "  Multi\r\nLine   Title  \t ",
            "https://arxiv.org/abs/2201.00002",
            "http://arxiv.org/abs/2201.00002v1",
        ),
    ]
    atom = _make_atom_feed(entries)

    with patch(
        "backend.app.sources.arxiv._urlopen",
        return_value=_mock_response(atom),
    ):
        items, error = fetch_arxiv_ai(limit=1)

    assert items[0]["title"] == "Multi Line Title"
    assert error is None


def test_fetch_arxiv_ai_respects_limit():
    entries = [
        (f"Paper {i}", f"https://arxiv.org/abs/{i}", f"http://arxiv.org/abs/{i}v1")
        for i in range(10)
    ]
    atom = _make_atom_feed(entries)

    with patch(
        "backend.app.sources.arxiv._urlopen",
        return_value=_mock_response(atom),
    ):
        items, error = fetch_arxiv_ai(limit=3)

    assert len(items) == 3
    assert error is None


def test_fetch_arxiv_ai_deduplicates():
    entries = [
        (
            "First paper",
            "https://arxiv.org/abs/2401.12345",
            "http://arxiv.org/abs/2401.12345v1",
        ),
        (
            "Second paper",
            "https://arxiv.org/abs/2401.12345",
            "http://arxiv.org/abs/2401.12345v2",
        ),
        (
            "Third paper",
            "https://arxiv.org/abs/2401.99999",
            "http://arxiv.org/abs/2401.99999v1",
        ),
    ]
    atom = _make_atom_feed(entries)

    with patch(
        "backend.app.sources.arxiv._urlopen",
        return_value=_mock_response(atom),
    ):
        items, error = fetch_arxiv_ai(limit=10)

    assert len(items) == 2
    assert error is None


def test_fetch_arxiv_ai_handles_missing_fields():
    entries = [
        ("", "https://arxiv.org/abs/2301.00003", "http://arxiv.org/abs/2301.00003v1"),
        (
            "Valid title",
            "",
            "http://arxiv.org/abs/2301.00004v1",
        ),
        (
            "Spaced title",
            "https://arxiv.org/abs/2301.00005",
            "http://arxiv.org/abs/2301.00005v1",
        ),
    ]
    atom = _make_atom_feed(entries)

    with patch(
        "backend.app.sources.arxiv._urlopen",
        return_value=_mock_response(atom),
    ):
        items, error = fetch_arxiv_ai(limit=10)

    assert len(items) == 1
    assert items[0]["title"] == "Spaced title"
    assert error is None


def test_fetch_arxiv_ai_handles_malformed_xml():
    with patch(
        "backend.app.sources.arxiv._urlopen",
        return_value=_mock_response(b"<not><xml>"),
    ):
        items, error = fetch_arxiv_ai(limit=5)

    assert items == []
    assert error is not None


def test_fetch_arxiv_ai_handles_upstream_network_failure():
    with patch(
        "backend.app.sources.arxiv._urlopen",
        side_effect=ConnectionError("network down"),
    ):
        items, error = fetch_arxiv_ai(limit=5)

    assert items == []
    assert error is not None
    assert "network down" in error


def test_fetch_arxiv_ai_limit_clamped_to_min():
    entries = [
        ("Minimum valid", "https://arxiv.org/abs/2301.00006", "http://arxiv.org/abs/2301.00006v1"),
    ]
    atom = _make_atom_feed(entries)

    with patch(
        "backend.app.sources.arxiv._urlopen",
        return_value=_mock_response(atom),
    ):
        items, error = fetch_arxiv_ai(limit=-5)

    assert len(items) == 1
    assert error is None


def test_fetch_arxiv_ai_limit_clamped_to_max():
    entries = [
        (f"Paper {i}", f"https://arxiv.org/abs/{i}", f"http://arxiv.org/abs/{i}v1")
        for i in range(25)
    ]
    atom = _make_atom_feed(entries)

    with patch(
        "backend.app.sources.arxiv._urlopen",
        return_value=_mock_response(atom),
    ):
        items, error = fetch_arxiv_ai(limit=100)

    assert len(items) == 20
    assert error is None
