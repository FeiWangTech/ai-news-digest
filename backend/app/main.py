from typing import Any

from fastapi import FastAPI, HTTPException

from .schemas import (
    DigestPreviewRequest,
    DigestPreviewResponse,
    DigestSendRequest,
    DigestSendResponse,
)
from .services.digest import aggregate_sources
from .services.email import send_digest_email
from .services.email_templates import render_html_digest, render_plain_digest
from .sources.hackernews import fetch_hackernews_ai
from .sources.techcrunch import fetch_techcrunch_ai
from .sources.arxiv import fetch_arxiv_ai

app = FastAPI(title="AI Daily Digest API", version="1.0.0")


@app.get("/api/health")
async def api_health() -> dict[str, str]:
    return {"status": "ok"}


def _build_digest_payload(
    request: DigestPreviewRequest | DigestSendRequest,
) -> dict[str, Any]:
    hn_items_list: list[dict[str, Any]] = []
    tc_items_list: list[dict[str, Any]] = []
    arxiv_items_list: list[dict[str, Any]] = []
    warnings: list[str] = []
    live_sources: list[str] = []

    sources = request.sources
    limits = request.limits

    if sources.get("hn", False):
        limit = min(max(limits.get("hn", 3) if limits else 3, 1), 20)
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
    if sources.get("techcrunch", False):
        tc_limit = min(max(limits.get("techcrunch", 3) if limits else 3, 1), 20)
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

    if sources.get("arxiv", False):
        arxiv_limit = min(max(limits.get("arxiv", 3) if limits else 3, 1), 20)
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

    if tc_live_succeeded:
        live_sources.append("TechCrunch")

    items = aggregate_sources(hn_items_list, tc_items_list, arxiv_items_list)

    tip = None
    if sources.get("tip", False):
        tip = "Mock AI Engineer Lifecycle Tip: use pydantic models."

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

    html = render_html_digest(items, tip=tip)
    plain = render_plain_digest(items, tip=tip)

    return {
        "items": items,
        "tip": tip,
        "warnings": warnings or None,
        "html": html,
        "plain": plain,
        "sources": sources,
        "mock": mock,
        "message": message,
    }


@app.post("/api/digest/preview", response_model=DigestPreviewResponse)
async def preview_digest(request: DigestPreviewRequest) -> dict[str, Any]:
    payload = _build_digest_payload(request)
    return {
        "mock": payload["mock"],
        "message": payload["message"],
        "items": payload["items"],
        "sources": payload["sources"],
        "tip": payload["tip"],
        "warnings": payload["warnings"],
        "html": payload["html"],
    }


@app.post("/api/digest/send", response_model=DigestSendResponse)
async def send_digest(request: DigestSendRequest) -> dict[str, Any]:
    payload = _build_digest_payload(request)
    warnings = payload["warnings"] or []
    try:
        send_digest_email(
            recipient=request.recipient,
            subject="AI Daily Digest",
            plain_text=payload["plain"],
            html_body=payload["html"],
        )
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Email delivery is not configured")
    except Exception:
        raise HTTPException(status_code=502, detail="Email delivery failed")

    message = "Email sent successfully"
    if warnings:
        message += f" with {len(warnings)} warning(s)"

    return {
        "sent": True,
        "message": message,
        "warnings": warnings or None,
    }
