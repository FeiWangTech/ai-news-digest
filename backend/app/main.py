from fastapi import FastAPI

from .schemas import DigestPreviewRequest, DigestPreviewResponse
from .sources.hackernews import fetch_hackernews_ai

app = FastAPI(title="AI Daily Digest API", version="1.0.0")


@app.get("/api/health")
async def api_health():
    return {"status": "ok"}


@app.post("/api/digest/preview", response_model=DigestPreviewResponse)
async def preview_digest(request: DigestPreviewRequest):
    items = []
    warnings = []
    live = False

    if request.sources.get("hn", False):
        limit = min(max(request.limits.get("hn", 3) if request.limits else 3, 1), 20)
        try:
            hn_items, error = fetch_hackernews_ai(limit=limit)
        except Exception as exc:
            hn_items = []
            error = f"Hacker News fetch failed: {exc}"
        items.extend(hn_items[:limit])
        if error:
            warnings.append(error)
        else:
            live = True

    if request.sources.get("techcrunch", False):
        limit = min(max(request.limits.get("techcrunch", 3) if request.limits else 3, 1), 20)
        items.extend(
            {
                "source": "TechCrunch AI",
                "title": f"Mock TechCrunch article {i}",
                "url": "https://example.com/tc",
            }
            for i in range(1, limit + 1)
        )
    if request.sources.get("arxiv", False):
        limit = min(max(request.limits.get("arxiv", 3) if request.limits else 3, 1), 20)
        items.extend(
            {
                "source": "arXiv cs.AI",
                "title": f"Mock arXiv paper {i}",
                "url": "https://example.com/arxiv",
            }
            for i in range(1, limit + 1)
        )
    tip = None
    if request.sources.get("tip", False):
        tip = "Mock AI Engineer Lifecycle Tip: use pydantic models."

    mock = not live
    if not live:
        message = "Preview data is mocked and not generated from live sources."
    elif warnings:
        message = (
            "Preview includes live data from Hacker News, "
            "but other sources may be mocked."
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
