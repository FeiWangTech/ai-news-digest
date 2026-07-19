from backend.app.services.email_templates import render_html_digest


def test_render_empty_items_returns_readable_empty_state():
    html = render_html_digest([])
    assert "<!DOCTYPE html>" in html
    assert "No items available" in html
    assert "There are no digest items to display right now." in html


def test_render_escapes_html_chars_in_title_source_and_tip():
    items = [
        {"source": "HN<b>", "title": "Title & \"quotes\"", "url": "https://example.com/1", "score": 10}
    ]
    html = render_html_digest(items, tip="Tip <script>alert(1)</script>")
    assert "<b>" not in html
    assert "&lt;script&gt;" in html
    assert "&quot;" in html
    assert "&amp;" in html
    assert "Title &amp; &quot;quotes&quot;" in html
    assert "HN&lt;b&gt;" in html


def test_render_preserves_http_https_urls_and_blocks_javascript_uri():
    safe_url = "https://example.com/article"
    unsafe_url = "javascript:alert(1)"
    items = [
        {"source": "Src", "title": "T1", "url": safe_url},
        {"source": "Src", "title": "T2", "url": unsafe_url},
        {"source": "Src", "title": "T3"},
    ]
    html = render_html_digest(items)
    assert 'href="' + safe_url + '"' in html
    assert unsafe_url not in html
    assert 'href="#"' in html


def test_render_escapes_malicious_quote_in_https_url():
    malicious_url = 'https://example.com/?q=" onmouseover="alert(1)'
    items = [{"source": "S", "title": "T", "url": malicious_url}]
    html = render_html_digest(items)
    assert 'href="' + malicious_url + '"' not in html
    assert 'href="https://example.com/?q=&quot; onmouseover=&quot;alert(1)"' in html


def test_render_deterministic_output_for_fixed_items():
    items = [
        {"source": "HN", "title": "A", "url": "https://hn.com/1", "score": 1},
        {"source": "TC", "title": "B", "url": "https://tc.com/2", "score": None},
    ]
    first = render_html_digest(items)
    second = render_html_digest(items)
    assert first == second


def test_render_includes_tip_when_provided_and_omits_when_none():
    items = []
    html_with_tip = render_html_digest(items, tip="Use pydantic.")
    html_without_tip = render_html_digest(items)

    assert "Tip</h3>" in html_with_tip
    assert "Use pydantic." in html_with_tip
    assert "Tip</h3>" not in html_without_tip


def test_render_contains_doctype_and_html_tag():
    html = render_html_digest([])
    assert html.startswith("<!DOCTYPE html>")
    assert '<html lang="en">' in html
    assert '<meta charset="UTF-8">' in html
    assert "<title>AI Daily Digest</title>" in html


def test_render_no_style_tag_or_external_css():
    html = render_html_digest([])
    assert "<style" not in html
    assert "javascript:" not in html
    assert "@import" not in html
    assert "<link" not in html


def test_render_uses_inline_styles():
    html = render_html_digest([
        {"source": "HN", "title": "A", "url": "https://hn.com/1"},
    ])
    assert 'style="background-color:#1a1a2e;' in html
    assert "color:#eaeaea;" in html
    assert "font-family:-apple-system" in html
    assert 'style="max-width:680px;' in html
