from urllib.parse import urlparse, urlunparse
from typing import Sequence, Any


def normalize_url(url: str | None) -> str:
    if not url or not str(url).strip():
        return ""
    stripped = str(url).strip()
    parsed = urlparse(stripped)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path
    if path not in ("/", ""):
        path = path.rstrip("/")
    return urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))


def normalize_title(title: str | None) -> str:
    if not title or not str(title).strip():
        return ""
    return str(title).strip().lower()


def aggregate_sources(
    hn_items: Sequence[dict[str, Any]],
    techcrunch_items: Sequence[dict[str, Any]],
    arxiv_items: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    sources = [hn_items, techcrunch_items, arxiv_items]
    indices = [0, 0, 0]
    exhausted = [False, False, False]

    while not all(exhausted):
        for i in range(3):
            if exhausted[i]:
                continue
            if indices[i] >= len(sources[i]):
                exhausted[i] = True
                continue
            item = sources[i][indices[i]]
            indices[i] += 1
            raw_url = item.get("url")
            normalized_url = normalize_url(raw_url)
            normalized_title = normalize_title(item.get("title"))
            skip = False
            if normalized_url and normalized_url in seen_urls:
                skip = True
            if not skip and normalized_title and normalized_title in seen_titles:
                skip = True
            if not skip:
                result.append(item)
                if normalized_url:
                    seen_urls.add(normalized_url)
                if normalized_title:
                    seen_titles.add(normalized_title)
    return result
