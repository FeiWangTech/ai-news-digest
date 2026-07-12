import logging
import re
import xml.etree.ElementTree as ET
from typing import List, Tuple
import urllib.request
import urllib.parse
import certifi
import ssl

logger = logging.getLogger(__name__)

_AI_KEYWORDS = [
    "AI", "artificial intelligence", "machine learning", "ML",
    "deep learning", "neural", "LLM", "large language model",
    "GPT", "OpenAI", "Claude", "Gemini", "diffusion", "RAG",
    "MLOps", "GenAI", "generative ai", "data science",
    "data scientist", "NLP", "natural language processing",
    "computer vision", "reinforcement learning", "chatbot",
    "AI agent", "transformer", "BERT", "algorithm",
    "prompt engineering", "robotics", "autonomous",
    "pytorch", "tensorflow", "stable diffusion", "DALL-E",
    "Midjourney",
]


def _urlopen(url: str, timeout: int = 15):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            ),
        },
    )
    try:
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    return urllib.request.urlopen(req, timeout=timeout, context=ctx)


def _is_ai_related(title: str) -> bool:
    if not title:
        return False
    lowered = title.lower()
    for kw in _AI_KEYWORDS:
        kw_lower = kw.lower()
        # Short keywords (2-3 chars) get word-boundary matching to
        # avoid false positives like "AI" matching "raises" or "fair".
        if len(kw) <= 3:
            if re.search(r"\b" + re.escape(kw_lower) + r"\b", lowered):
                return True
        else:
            if kw_lower in lowered:
                return True
    return False


def _parse_entries(data: bytes) -> List[dict]:
    entries: List[dict] = []
    try:
        root = ET.fromstring(data)
        for item in root.iter("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            title = (title_el.text or "").strip() if title_el is not None else ""
            link = (link_el.text or "").strip() if link_el is not None else ""
            entries.append({"title": title, "link": link})
    except ET.ParseError as exc:
        logger.warning("TechCrunch RSS parse error: %s", exc)
    return entries


def fetch_techcrunch_ai(limit: int = 8) -> Tuple[List[dict], str | None]:
    items: List[dict] = []
    error_message: str | None = None
    seen_urls: set = set()

    limit = max(1, min(limit, 20))

    try:
        url = "https://techcrunch.com/category/artificial-intelligence/feed/"
        with _urlopen(url, timeout=15) as resp:
            data = resp.read()

        entries = _parse_entries(data)

        for entry in entries:
            if len(items) >= limit:
                break

            title = entry.get("title", "")
            link = entry.get("link", "")

            if not title:
                continue
            if link in seen_urls:
                continue
            if not link.startswith(("http://", "https://")):
                continue
            seen_urls.add(link)

            if not _is_ai_related(title):
                continue

            items.append(
                {
                    "source": "TechCrunch AI",
                    "title": title,
                    "url": link,
                    "score": 0,
                }
            )
    except Exception as e:
        logger.warning("TechCrunch fetch failed: %s", e)
        error_message = f"TechCrunch fetch failed: {e}"

    if not items:
        error_message = error_message or "TechCrunch fetch failed, no items found."

    items.sort(key=lambda x: x.get("score", 0), reverse=True)
    return items[:limit], error_message
