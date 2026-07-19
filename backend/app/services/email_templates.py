import html as html_module
from typing import Any, Sequence


_SAFE_SCHEMES = {"http", "https"}


def _is_safe_url(url: str | None) -> bool:
    if not url:
        return False
    url = str(url).strip()
    if not url:
        return False
    if ":" not in url:
        return False
    scheme = url.split(":", 1)[0].lower()
    return scheme in _SAFE_SCHEMES


def _safe_url(url: str | None) -> str:
    if _is_safe_url(url):
        return html_module.escape(str(url).strip(), quote=True)
    return "#"


def _escape(text: str | None) -> str:
    return html_module.escape(str(text or ""))


def _item_html(title: str, source: str, url: str, score: object) -> str:
    score_str = f" &middot; &#x2191; {html_module.escape(str(score))}" if score is not None else ""
    return (
        '<div style="background-color:#1a1a2e;border-left:4px solid #e94560;padding:14px 18px;margin-bottom:16px;border-radius:0 8px 8px 0;">\n'
        ' <h3 style="margin:0 0 6px;font-size:16px;color:#ffffff;">' + title + '</h3>\n'
        ' <a href="' + url + '" target="_blank" style="color:#53a8b6;text-decoration:none;font-size:14px;">' + source + ' &middot; Read more' + score_str + '</a>\n'
        '</div>'
    )


def render_html_digest(
    items: Sequence[dict[str, Any]],
    *,
    tip: str | None = None,
) -> str:
    escaped_tip = _escape(tip) if tip is not None else None

    item_parts = []
    for item in items:
        item_parts.append(_item_html(
            _escape(item.get("title")),
            _escape(item.get("source")),
            _safe_url(item.get("url")),
            item.get("score"),
        ))

    if item_parts:
        items_html = "\n".join(item_parts)
    else:
        items_html = (
            '<div style="background-color:#1a1a2e;border-left:4px solid #e94560;padding:14px 18px;margin-bottom:16px;border-radius:0 8px 8px 0;">\n'
            ' <h3 style="margin:0 0 6px;font-size:16px;color:#ffffff;">No items available</h3>\n'
            ' <p style="margin:0;color:#aaa;font-size:14px;">There are no digest items to display right now.</p>\n'
            '</div>'
        )

    tip_section = ""
    if escaped_tip:
        tip_section = (
            '<div style="background-color:#1a1a2e;border-left:4px solid #0f3460;padding:14px 18px;margin-bottom:16px;border-radius:0 8px 8px 0;">\n'
            ' <h3 style="margin:0 0 6px;font-size:16px;color:#e94560;">Tip</h3>\n'
            ' <p style="margin:0;color:#aaa;font-size:14px;">' + escaped_tip + '</p>\n'
            '</div>\n'
        )

    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "<title>AI Daily Digest</title>\n"
        "</head>\n"
        '<body style="background-color:#1a1a2e;color:#eaeaea;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,Oxygen,Ubuntu,Cantarell,sans-serif;margin:0;padding:0;">\n'
        '<div style="max-width:680px;margin:20px auto;background:#16213e;border-radius:12px;padding:32px;border:1px solid #0f3460;">\n'
        '<div style="border-bottom:1px solid #0f3460;padding-bottom:16px;margin-bottom:24px;">\n'
        '<h1 style="color:#e94560;font-size:22px;margin:0;">&#x1F916; AI Daily Digest</h1>\n'
        '<p style="margin:6px 0 0;color:#aaa;font-size:14px;">Aggregated from live sources.</p>\n'
        "</div>\n"
        + tip_section
        + items_html
        + "\n"
        '<div style="text-align:center;margin-top:30px;font-size:12px;color:#888;">\n'
        "<p>AI News Digest</p>\n"
        "</div>\n"
        "</div>\n"
        "</body>\n"
        "</html>"
    )
