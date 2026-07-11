import random
import re
import logging
from typing import Optional
from urllib.request import Request, urlopen
from urllib.parse import quote
from datetime import date
import ssl
import certifi

logger = logging.getLogger("app.fetcher")


def _urlopen(url: str, timeout: int = 20):
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    ctx = ssl.create_default_context(cafile=certifi.where())
    return urlopen(req, timeout=timeout, context=ctx)


def _stable_seed_for_date(user_id: Optional[int] = None) -> int:
    d = date.today().isoformat().replace("-", "")
    if user_id:
        return hash((d, user_id)) % (2**32)
    return hash(d) % (2**32)


def fetch_hackernews_ai(user_id: Optional[int] = None, limit: int = 10) -> list[dict]:
    """Fetch stories from Hacker News Algolia API."""
    try:
        url = f"https://hn.algolia.com/api/v1/search?query={quote('AI OR LLM OR GPT OR Claude')}&tags=story&hitsPerPage={limit}"
        with _urlopen(url) as resp:
            data = resp.read().decode()
        hits = __import__("json").loads(data).get("hits", [])
        results = []
        seen = set()
        for hit in hits:
            h_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID','')}"
            if h_url in seen:
                continue
            seen.add(h_url)
            title = hit.get("title", "")
            if title:
                results.append({"source": "Hacker News", "title": title, "url": h_url, "score": hit.get("points", 0)})
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:limit]
    except Exception as e:
        logger.warning("HN fetch failed: %s", e)
        return [{"source": "Hacker News", "title": f"(HN fetch error: {e})", "url": "", "score": 0}]


def fetch_techcrunch_ai(user_id: Optional[int] = None, limit: int = 10) -> list[dict]:
    """Fetch stories from TechCrunch AI RSS."""
    try:
        url = "https://techcrunch.com/category/artificial-intelligence/feed/"
        with _urlopen(url) as resp:
            data = resp.read().decode(errors="replace")
        items = re.findall(r"<item>.*?</item>", data, re.DOTALL)
        results = []
        for item in items[:limit]:
            title_m = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", item, re.DOTALL)
            link_m = re.search(r"<link>(.*?)</link>", item)
            title = title_m.group(1).strip() if title_m else "Untitled"
            link = link_m.group(1).strip() if link_m else ""
            results.append({"source": "TechCrunch AI", "title": title, "url": link, "score": 0})
        return results
    except Exception as e:
        logger.warning("TechCrunch fetch failed: %s", e)
        return [{"source": "TechCrunch AI", "title": f"(TechCrunch fetch error: {e})", "url": "", "score": 0}]


def fetch_arxiv_ai(user_id: Optional[int] = None, limit: int = 10) -> list[dict]:
    """Fetch AI papers from arXiv."""
    try:
        url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=8&sortBy=submittedDate&sortOrder=descending"
        with _urlopen(url) as resp:
            data = resp.read().decode(errors="replace")
        entries = re.findall(r"<entry>.*?</entry>", data, re.DOTALL)
        results = []
        for entry in entries[:limit]:
            title_m = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
            link_m = re.search(r'<link\s+href="(.*?)"\s+rel="alternate"', entry)
            title = title_m.group(1).strip().replace("\n", " ") if title_m else "Untitled"
            link = link_m.group(1).strip() if link_m else ""
            results.append({"source": "arXiv cs.AI", "title": title, "url": link, "score": 0})
        return results
    except Exception as e:
        logger.warning("arXiv fetch failed: %s", e)
        return [{"source": "arXiv cs.AI", "title": f"(arXiv fetch error: {e})", "url": "", "score": 0}]


def fetch_all_sources(user_id: Optional[int] = None, limit: int = 10) -> list[dict]:
    seen = set()
    all_items = []
    for source_fn in [fetch_hackernews_ai, fetch_techcrunch_ai, fetch_arxiv_ai]:
        for item in source_fn(user_id=user_id, limit=limit):
            key = item["url"]
            if key and key not in seen:
                seen.add(key)
                all_items.append(item)
    all_items.sort(key=lambda x: -(x.get("score") or 0))
    return all_items[: limit * 2]
