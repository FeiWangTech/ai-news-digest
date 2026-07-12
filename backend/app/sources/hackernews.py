import json
import urllib.request
import urllib.parse
from typing import List, Tuple


_QUERIES = [
    ("OpenAI OR GPT OR ChatGPT", 5),
    ("LLM OR large language model OR Claude OR Gemini", 5),
    ("machine learning OR deep learning OR neural", 5),
    ("AI agent OR RAG OR diffusion OR MLOps", 5),
]


def _urlopen(url: str, timeout: int = 15):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        import certifi
        import ssl

        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        import ssl

        ctx = ssl.create_default_context()
    return urllib.request.urlopen(req, timeout=timeout, context=ctx)


def fetch_hackernews_ai(limit: int = 12) -> Tuple[List[dict], str | None]:
    items: List[dict] = []
    error_message = None
    seen_urls = set()

    for query_text, per_query in _QUERIES:
        try:
            url = (
                "https://hn.algolia.com/api/v1/search"
                f"?query={urllib.parse.quote(query_text)}&tags=story&hitsPerPage={per_query}"
            )
            with _urlopen(url, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            for hit in data.get("hits", []):
                if len(items) >= limit:
                    break
                raw_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                if raw_url in seen_urls:
                    continue
                if not raw_url.startswith(("http://", "https://")):
                    raw_url = ""
                seen_urls.add(raw_url)
                title = (hit.get("title") or "").strip()
                if title and raw_url:
                    score = hit.get("points")
                    if not isinstance(score, int):
                        score = 0
                    items.append(
                        {
                            "source": "Hacker News",
                            "title": title,
                            "url": raw_url,
                            "score": score,
                        }
                    )
        except Exception as e:
            error_message = f"Hacker News fetch failed for query={query_text}: {e}"

    if not items:
        error_message = error_message or "Hacker News fetch failed, no items found."

    items.sort(key=lambda x: x.get("score", 0), reverse=True)
    return items[:limit], error_message
