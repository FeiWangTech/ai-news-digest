import logging
import re
import xml.etree.ElementTree as ET
from typing import List, Tuple
import urllib.request
import urllib.parse
import certifi
import ssl

logger = logging.getLogger(__name__)

_ATOM_NS = "http://www.w3.org/2005/Atom"

_QUERIES = [
    "cat:cs.AI",
    "cat:cs.CL",
    "cat:cs.CV",
    "cat:cs.LG",
]


def _urlopen(url: str, timeout: int = 20):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    return urllib.request.urlopen(req, timeout=timeout, context=ctx)


def _normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "")).strip()


def fetch_arxiv_ai(limit: int = 8) -> Tuple[List[dict], str | None]:
    items: List[dict] = []
    error_message: str | None = None
    seen_ids = set()

    limit = max(1, min(limit, 20))

    try:
        query = " OR ".join(_QUERIES)
        url = (
            "http://export.arxiv.org/api/query?"
            f"search_query={urllib.parse.quote(query)}&start=0&max_results={limit}"
            "&sortBy=submittedDate&sortOrder=descending"
        )
        with _urlopen(url, timeout=20) as resp:
            data = resp.read()

        try:
            root = ET.fromstring(data)
        except ET.ParseError as exc:
            logger.warning("arXiv API response parse error: %s", exc)
            error_message = "arXiv fetch failed, invalid response."
            return items, error_message

        for entry in root.iter(f"{{{_ATOM_NS}}}entry"):
            if len(items) >= limit:
                break

            title_el = entry.find(f"{{{_ATOM_NS}}}title")
            id_el = entry.find(f"{{{_ATOM_NS}}}id")
            link_el = None
            for candidate in entry.findall(f"{{{_ATOM_NS}}}link"):
                if candidate.get("rel") == "alternate" and candidate.get("href"):
                    link_el = candidate
                    break
            if link_el is None:
                link_el = entry.find(f"{{{_ATOM_NS}}}link")

            title = ""
            if title_el is not None and (title_text := title_el.text):
                title = _normalize_title(title_text)

            arxiv_id = ""
            if id_el is not None and (id_text := id_el.text):
                arxiv_id = id_text.strip()

            link = ""
            if link_el is not None and link_el.get("href"):
                link = link_el.get("href").strip()

            if not title:
                continue

            seen_key = link or arxiv_id
            if seen_key in seen_ids:
                continue
            seen_ids.add(seen_key)

            if not link.startswith(("http://", "https://")):
                continue

            items.append(
                {
                    "source": "arXiv cs.AI",
                    "title": title,
                    "url": link,
                    "score": 0,
                }
            )

    except Exception as e:
        logger.warning("arXiv fetch failed: %s", e)
        error_message = f"arXiv fetch failed: {e}"

    if not items and error_message is None:
        error_message = "arXiv fetch failed, no items found."

    return items[:limit], error_message
