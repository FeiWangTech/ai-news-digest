#!/usr/bin/env python3
"""
AI News Daily Email Script for Hermes Cron Job
Fetches AI-related news and sends a daily digest email via Gmail SMTP.

Usage:
  python3 ai-news-email.py --to RECIPIENT@gmail.com

Requires env vars:
  GMAIL_SENDER   - Gmail address (sender)
  GMAIL_APP_PW   - Gmail App Password (16-char, no spaces)
"""

import os
import sys
import json
import smtplib
import urllib.request
import urllib.parse
import urllib.error
import textwrap
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def _central_time():
    """Get current time in US Central timezone (CST/CDT)."""
    return datetime.now(ZoneInfo("America/Chicago"))


def _urlopen(url, timeout=15):
    """Open URL with proper headers and SSL handling."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    import ssl
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    return urllib.request.urlopen(req, timeout=timeout, context=ctx)


def fetch_hackernews_ai(limit=15):
    """Fetch AI-related stories from Hacker News via Algolia API."""
    results = []
    seen_urls = set()

    # Search multiple focused queries to get diverse AI news
    queries = [
        ("OpenAI OR GPT OR ChatGPT", 5),
        ("LLM OR large language model OR Claude OR Gemini", 5),
        ("machine learning OR deep learning OR neural", 5),
        ("AI agent OR RAG OR diffusion OR MLOps", 5),
    ]

    for query_text, per_query in queries:
        try:
            url = f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(query_text)}&tags=story&hitsPerPage={per_query}"
            with _urlopen(url, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            for hit in data.get("hits", []):
                if len(results) >= limit:
                    break
                h_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                if h_url in seen_urls:
                    continue
                seen_urls.add(h_url)
                title = hit.get("title", "")
                if title:
                    results.append({
                        "title": title,
                        "url": h_url,
                        "score": hit.get("points", 0),
                        "source": "Hacker News",
                    })
        except Exception as e:
            if not any(r["source"] == "Hacker News" for r in results):
                results.append({"title": f"(HN fetch error: {e})", "url": "", "score": 0, "source": "Hacker News"})

    # Sort by score descending
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results[:limit]


def fetch_techmeme_ai(limit=10):
    """Fetch AI headlines from TechCrunch via RSS."""
    results = []
    try:
        url = "https://techcrunch.com/category/artificial-intelligence/feed/"
        with _urlopen(url, timeout=15) as resp:
            data = resp.read().decode(errors="replace")

        # Simple XML parsing for <title> and <link>
        import re
        items = re.findall(r"<item>.*?</item>", data, re.DOTALL)
        for item in items[:limit]:
            title_m = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", item)
            if not title_m:
                title_m = re.search(r"<title>(.*?)</title>", item)
            link_m = re.search(r"<link>(.*?)</link>", item)
            title = title_m.group(1).strip() if title_m else "Untitled"
            link = link_m.group(1).strip() if link_m else ""
            results.append({
                "title": title,
                "url": link,
                "score": 0,
                "source": "TechCrunch AI",
            })
    except Exception as e:
        results.append({"title": f"(TechCrunch fetch error: {e})", "url": "", "score": 0, "source": "TechCrunch AI"})

    return results


def fetch_arxiv_ai(limit=8):
    """Fetch recent AI papers from arXiv."""
    results = []
    try:
        url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=8&sortBy=submittedDate&sortOrder=descending"
        with _urlopen(url, timeout=20) as resp:
            data = resp.read().decode(errors="replace")

        import re
        entries = re.findall(r"<entry>.*?</entry>", data, re.DOTALL)
        for entry in entries[:limit]:
            title_m = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
            link_m = re.search(r'<link\s+href="(.*?)"\s+rel="alternate"', entry)
            title = title_m.group(1).strip().replace("\n", " ") if title_m else "Untitled"
            link = link_m.group(1).strip() if link_m else ""
            results.append({
                "title": title,
                "url": link,
                "score": 0,
                "source": "arXiv cs.AI",
            })
    except Exception as e:
        results.append({"title": f"(arXiv fetch error: {e})", "url": "", "score": 0, "source": "arXiv cs.AI"})

    return results


def build_email_content(hn_items, tc_items, arxiv_items):
    """Build the HTML email body."""
    today = _central_time().strftime("%A, %B %d, %Y")

    sections = []

    # Header
    header = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 600px; margin: 0 auto; padding: 20px;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                border-radius: 12px; color: #ffffff;">
      <h1 style="margin:0 0 5px 0; font-size:24px; color:#e94560;">
        🤖 AI Daily Digest
      </h1>
      <p style="margin:0 0 20px 0; color:#a8a8b3; font-size:14px;">
        {today} &mdash; AI Engineer Knowledge Digest
      </p>
      <hr style="border:none; border-top:1px solid #333; margin:15px 0;">
    """

    # AI Engineer Lifecycle Tips — rotating advice bank
    import random
    tips_bank = [
        "💡 <strong>Dev Stage — Local Prototyping</strong>: Start with a notebook, then immediately modularize. Define your model interface (input/output schema) early. Use <strong>pydantic models</strong> for validation from day 1. A clean interface makes every downstream step easier.",

        "💡 <strong>Dev Stage — Experiment Tracking</strong>: Use <strong>MLflow or Weights & Biases</strong> from the very first experiment. Log hyperparams, metrics, artifacts, and the git commit hash. When your model degrades in prod 3 months later, you'll thank yourself.",

        "💡 <strong>Dev Stage — Prompt Engineering</strong>: Treat prompts like code — version control them, write unit tests for expected outputs, use structured output (JSON mode) when possible. <strong>Promptfoo and LangSmith</strong> help automate evaluation across prompt variants.",

        "💡 <strong>Dev Stage — RAG Best Practices</strong>: Chunk size matters — start with 512 tokens, evaluate retrieval quality with <strong>recall@k and MRR</strong>. Always implement hybrid search (dense + sparse/BM25). Use <strong>rerankers</strong> (Cohere, cross-encoder) for top-k reordering.",

        "💡 <strong>Dev Stage — Evaluation First</strong>: Before writing any feature, define how you'll measure success. For LLM apps: <strong>faithfulness, relevance, hallucination rate</strong>. Build an eval dataset with 50-100 golden examples. No evals = flying blind.",

        "💡 <strong>Dev Stage — Model Selection</strong>: Don't default to the biggest model. Start with a small, fast, cheap model (GPT-4o-mini, Claude Haiku). Only upgrade when evals prove you need to. <strong>Cost and latency compound at scale</strong>.",

        "💡 <strong>Staging — CI/CD for ML</strong>: Your pipeline has two artifacts: <strong>code</strong> (git) and <strong>model weights</strong> (registry). CI should run unit tests + eval suite. CD should deploy model + code atomically. Never update one without the other.",

        "💡 <strong>Staging — Model Validation Gate</strong>: Before promoting to prod, run (<strong>new model eval score</strong> ≥ <strong>baseline + margin</strong>) AND (<strong>no regression on critical test cases</strong>). Automate this gate — humans will skip it under deadline pressure.",

        "💡 <strong>Staging — Shadow Deployment</strong>: Route a % of prod traffic to the new model, but don't serve results to users. Compare shadow vs prod outputs. <strong>Look for divergence, edge cases, and latency spikes</strong> before full rollout.",

        "💡 <strong>Staging — Load Testing</strong>: ML APIs have different bottlenecks than web APIs. <strong>GPU memory, batch size, queue depth, token throughput</strong>. Load test with realistic request patterns. vLLM's <strong>benchmark tool</strong> is a good starting point.",

        "💡 <strong>Staging — A/B Test Design</strong>: Define your <strong>primary metric</strong> (e.g. task success rate, not just CTR). Ensure <strong>statistical significance</strong> before calling a winner. Run for at least 2 business cycles. Beware of novelty effects — they fade in 1-2 weeks.",

        "💡 <strong>Production — Model Serving</strong>: Use <strong>vLLM or TGI</strong> for LLM serving — they handle batching, KV caching, and token streaming efficiently. Never serve models directly from FastAPI without a proper inference server. Latency will kill your UX.",

        "💡 <strong>Production — Caching Strategy</strong>: LLM calls are expensive and slow. Implement <strong>semantic caching</strong> (cache if embedding similarity > 0.95) and <strong>exact caching</strong> for identical prompts. A good cache can cut costs by 30-50%.",

        "💡 <strong>Production — Fallback Chain</strong>: Always have a fallback. Main model → cheaper model → rule-based system → graceful error message. <strong>Never show a raw error to users</strong>. Circuit breakers prevent cascade failures when upstream APIs go down.",

        "💡 <strong>Production — Rate Limiting & Cost Control</strong>: LLM APIs burn money fast. Implement <strong>per-user rate limits, max token caps, and daily spend alerts</strong>. Track cost per request. A $0.05/query system at 10K RPS = $4.3M/year.",

        "💡 <strong>Production — Data Privacy</strong>: PII in prompts is a <strong>legal and security risk</strong>. Implement <strong>PII detection and redaction</strong> before sending to LLM APIs. For sensitive workloads, use <strong>on-premise models</strong> or API providers with zero-data-retention policies.",

        "💡 <strong>Production — Scaling Patterns</strong>: Horizontal scaling for throughput, vertical scaling for latency. Use <strong>model sharding (tensor parallel)</strong> for large models, <strong>request queuing with priority</strong> for mixed workloads. Autoscale on queue depth, not just CPU.",

        "💡 <strong>Production — Streaming & UX</strong>: Always stream LLM output token-by-token. perceived latency ≪ actual latency. Add <strong>progressive rendering</strong> (markdown as it arrives), <strong>citations inline</strong>, and <strong>typing indicators</strong>. UX is your competitive moat.",

        "💡 <strong>Monitoring — LLM Observability</strong>: Log every request: <strong>prompt, completion, latency, tokens, cost, model version</strong>. Use <strong>LangSmith, Helicone, or Arize Phoenix</strong>. You can't improve what you can't observe.",

        "💡 <strong>Monitoring — Drift Detection</strong>: Track <strong>input distribution drift</strong> (user prompts changing over time) and <strong>output quality drift</strong> (eval scores on sampled prod traffic). Set alerts at 2σ. Monthly full eval runs catch slow degradation.",

        "💡 <strong>Monitoring — Error Budgets</strong>: Define acceptable error rates per error type: <strong>hallucination < 2%, timeout < 0.1%, wrong format < 0.5%</strong>. When budget is exhausted, freeze deployments and investigate. Makes quality a shared team responsibility.",

        "💡 <strong>Monitoring — User Feedback Loop</strong>: Collect 👍👎 on every response. Correlate negative signals with prompt patterns. <strong>Automatically add low-quality interactions to your eval dataset</strong>. Your users are your best annotators.",

        "💡 <strong>Monitoring — Cost Analytics</strong>: Track <strong>cost per feature, per model, per user tier</strong>. Is your RAG retriever costing more than the LLM? Are power users subsidizing free tier? Cost transparency drives architecturally better decisions.",

        "💡 <strong>Iterating — Retraining Strategy</strong>: Fine-tune on <strong>high-quality prod data + corrections</strong>, not just any data. DPO/RLHF on user preferences. <strong>Always A/B test fine-tuned vs base</strong> — fine-tuning can make things worse if data is noisy.",

        "💡 <strong>Iterating — Prompt Optimization</strong>: Prompts drift — what worked 3 months ago may not work now (model updates, user behavior changes). <strong>Schedule monthly prompt evals</strong>. Use DSPy or promptfoo to systematically optimize prompt templates.",

        "💡 <strong>Iterating — Architecture Evolution</strong>: Monolith → microservices is not always right. Start simple (single service) and extract when you have <strong>clear boundaries and independent scaling needs</strong>. RAG service, model router, and eval pipeline are common first extractions.",

        "💡 <strong>Full Lifecycle — Documentation</strong>: Document your <strong>model card</strong> (purpose, limitations, eval results), <strong>runbook</strong> (what to do when things break), and <strong>decision log</strong> (why we chose model X over Y). Future you (and your team) will need this.",

        "💡 <strong>Full Lifecycle — Security Review</strong>: <strong>Prompt injection</strong> is the #1 security risk for LLM apps. Validate and sanitize all user input. Never put raw user input in system prompts. Implement <strong>input/output guardrails</strong> (NeMo Guardrails, Llama Guard).",

        "💡 <strong>Full Lifecycle — Incident Response</strong>: Define severity levels for AI incidents: <strong>P0 = model serving hateful content, P1 = hallucination affecting decisions, P2 = degraded quality</strong>. Have rollback procedures — reverting to a previous model version should be a 1-button action.",
    ]

    today_seed = int(_central_time().strftime("%Y%m%d"))
    rng = random.Random(today_seed)  # same tip for same day, changes daily
    tip_text = rng.choice(tips_bank)

    tips = f"""
      <div style="background:#1a1a3e; padding:15px; border-radius:8px; margin-bottom:20px;
                  border-left:3px solid #e94560;">
        <h2 style="margin:0 0 10px 0; color:#e94560; font-size:16px;">
          🔧 AI Engineer Lifecycle Tip
        </h2>
        <p style="margin:0; color:#d0d0d8; font-size:13px; line-height:1.6;">
          {tip_text}
        </p>
      </div>
    """
    sections.append(tips)

    # Hacker News
    if hn_items:
        hn_html = '<h2 style="margin:20px 0 10px 0; color:#ff6600; font-size:16px;">🔥 Hacker News — AI Top Stories</h2>'
        for item in hn_items:
            if item["url"]:
                hn_html += f"""
                <div style="margin-bottom:8px;">
                  <a href="{item['url']}" style="color:#e0e0e8; text-decoration:none; font-size:14px; font-weight:500;"
                     target="_blank">{item['title']}</a>
                  <span style="color:#888; font-size:12px;"> &middot; {item['score']} points</span>
                </div>"""
            else:
                hn_html += f'<div style="color:#888; font-size:13px;">{item["title"]}</div>'
        sections.append(hn_html)

    # TechCrunch
    if tc_items:
        tc_html = '<h2 style="margin:20px 0 10px 0; color:#00cc99; font-size:16px;">📰 TechCrunch — AI News</h2>'
        for item in tc_items:
            if item["url"]:
                tc_html += f"""
                <div style="margin-bottom:8px;">
                  <a href="{item['url']}" style="color:#e0e0e8; text-decoration:none; font-size:14px;"
                     target="_blank">{item['title']}</a>
                </div>"""
            else:
                tc_html += f'<div style="color:#888; font-size:13px;">{item["title"]}</div>'
        sections.append(tc_html)

    # arXiv
    if arxiv_items:
        arxiv_html = '<h2 style="margin:20px 0 10px 0; color:#b31b1b; font-size:16px;">📄 arXiv — Latest AI Papers</h2>'
        for item in arxiv_items:
            if item["url"]:
                arxiv_html += f"""
                <div style="margin-bottom:8px;">
                  <a href="{item['url']}" style="color:#e0e0e8; text-decoration:none; font-size:13px;"
                     target="_blank">{item['title']}</a>
                </div>"""
            else:
                arxiv_html += f'<div style="color:#888; font-size:12px;">{item["title"]}</div>'
        sections.append(arxiv_html)

    # Footer
    footer = """
      <hr style="border:none; border-top:1px solid #333; margin:20px 0 10px 0;">
      <p style="color:#666; font-size:11px; text-align:center;">
        Generated by Hermes Agent &bull;
        Sources: Hacker News, TechCrunch, arXiv
      </p>
    </div>
    """

    return header + "\n".join(sections) + footer


def send_email(sender, app_pw, recipient, subject, html_body):
    """Send email via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    # Plain text fallback
    import re
    text_body = re.sub(r"<[^>]+>", "", html_body)
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, app_pw)
        server.sendmail(sender, recipient, msg.as_string())

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI News Daily Email")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--limit-hn", type=int, default=12, help="Max HN items")
    parser.add_argument("--limit-tc", type=int, default=8, help="Max TechCrunch items")
    parser.add_argument("--limit-arxiv", type=int, default=6, help="Max arXiv items")
    args = parser.parse_args()

    sender = os.environ.get("GMAIL_SENDER")
    app_pw = os.environ.get("GMAIL_APP_PW")

    if not sender or not app_pw:
        print("ERROR: Set GMAIL_SENDER and GMAIL_APP_PW environment variables", file=sys.stderr)
        sys.exit(1)

    today = _central_time().strftime("%b %d, %Y")

    print(f"Fetching AI news for {today}...")

    # Fetch all sources
    hn_items = fetch_hackernews_ai(limit=args.limit_hn)
    print(f"  Hacker News: {len(hn_items)} AI stories")

    tc_items = fetch_techmeme_ai(limit=args.limit_tc)
    print(f"  TechCrunch: {len(tc_items)} AI articles")

    arxiv_items = fetch_arxiv_ai(limit=args.limit_arxiv)
    print(f"  arXiv: {len(arxiv_items)} AI papers")

    # Build email
    html = build_email_content(hn_items, tc_items, arxiv_items)
    subject = f"🤖 AI Daily Digest — {today}"

    # Send
    try:
        send_email(sender, app_pw, args.to, subject, html)
        print(f"✅ Email sent to {args.to}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
