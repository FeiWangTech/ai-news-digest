from typing import Any

from fastapi import FastAPI

from .schemas import DigestPreviewRequest, DigestPreviewResponse
from .services.digest import aggregate_sources
from .sources.hackernews import fetch_hackernews_ai
from .sources.techcrunch import fetch_techcrunch_ai
from .sources.arxiv import fetch_arxiv_ai

app = FastAPI(title="AI Daily Digest API", version="1.0.0")


@app.get("/api/health")
async def api_health():
    return {"status": "ok"}


@app.post("/api/digest/preview", response_model=DigestPreviewResponse)
async def preview_digest(request: DigestPreviewRequest):
    hn_items_list: list[dict[str, Any]] = []
    tc_items_list: list[dict[str, Any]] = []
    arxiv_items_list: list[dict[str, Any]] = []
    warnings = []
    live = False
    live_sources: list[str] = []

    if request.sources.get("hn", False):
        limit = min(max(request.limits.get("hn", 3) if request.limits else 3, 1), 20)
        try:
            hn_items, error = fetch_hackernews_ai(limit=limit)
        except Exception as exc:
            hn_items = []
            error = f"Hacker News fetch failed: {exc}"
        hn_items_list = list(hn_items[:limit])
        if error:
            warnings.append(error)
        else:
            live_sources.append("Hacker News")

    tc_live_succeeded = False
    if request.sources.get("techcrunch", False):
        tc_limit = min(
            max(request.limits.get("techcrunch", 3) if request.limits else 3, 1), 20
        )
        try:
            tc_items, tc_error = fetch_techcrunch_ai(limit=tc_limit)
        except Exception as exc:
            tc_items = []
            tc_error = f"TechCrunch fetch failed: {exc}"
        tc_items_list = list(tc_items[:tc_limit])
        if tc_error:
            warnings.append(tc_error)
        else:
            tc_live_succeeded = True
    if request.sources.get("arxiv", False):
        arxiv_limit = min(
            max(request.limits.get("arxiv", 3) if request.limits else 3, 1), 20
        )
        try:
            arxiv_items, arxiv_error = fetch_arxiv_ai(limit=arxiv_limit)
        except Exception as exc:
            arxiv_items = []
            arxiv_error = f"arXiv fetch failed: {exc}"
        arxiv_items_list = list(arxiv_items[:arxiv_limit])
        if arxiv_error:
            warnings.append(arxiv_error)
        else:
            live_sources.append("arXiv cs.AI")

    items = aggregate_sources(hn_items_list, tc_items_list, arxiv_items_list)
    tip = None
    if request.sources.get("tip", False):
        tip = "Mock AI Engineer Lifecycle Tip: use pydantic models."

    if tc_live_succeeded:
        live_sources.append("TechCrunch")

    live = bool(live_sources)
    mock = not live
    if not live:
        message = "Preview data is mocked and not generated from live sources."
    elif warnings:
        sources_str = ", ".join(live_sources)
        message = (
            f"Preview includes live data from {sources_str}, "
            f"but other sources may be mocked."
        )
    else:
        message = "Preview includes live data from enabled sources."

    return {
        "mock": mock,
        "message": message,
        "items": items,
        "sources": request.sources,
        "tip": tip,
        "warnings": warnings or None,
    }