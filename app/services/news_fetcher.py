import re
import urllib.request
import urllib.parse
from typing import List, Dict

def _urlopen(url: str, timeout: int = 15):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+json,application/xml;q=0.9,*/*;q=0.8",
    })
    import ssl, certifi
    ctx = ssl.create_default_context(cafile=certifi.where())
    return urllib.request.urlopen(req, timeout=timeout, context=ctx)

def fetch_hackernews_ai(query: str = "AI OR LLM OR GPT OR Claude", limit: int = 10) -> List[Dict]:
    url = f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(query)}&tags=story&hitsPerPage={limit}"
    results = []
    seen = set()
    try:
        with _urlopen(url, timeout=20) as resp:
            data = resp.read().decode()
        import json
        hits = json.loads(data).get("hits", [])
        for hit in hits:
            h_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID','')}"
            if h_url in seen:
                continue
            seen.add(h_url)
            title = hit.get("title", "")
            if title:
                results.append({"title": title, "url": h_url, "score": hit.get("points", 0), "source": "Hacker News"})
    except Exception as e:
        results.append({"title": f"(HN fetch error: {e})", "url": "", "score": 0, "source": "Hacker News"})
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results[:limit]

def fetch_techcrunch_ai(limit: int = 10) -> List[Dict]:
    url = "https://techcrunch.com/category/artificial-intelligence/feed/"
    results = []
    try:
        with _urlopen(url, timeout=20) as resp:
            data = resp.read().decode(errors="replace")
        items = re.findall(r"<item>.*?</item>", data, re.DOTALL)
        for item in items[:limit]:
            title_m = re.search(r"<title>(?:<!\\[CDATA\\[)?(.*?)(?:\\]\\]>)?</title>", item, re.DOTALL)
            link_m = re.search(r"<link>(.*?)</link>", item)
            title = title_m.group(1).strip() if title_m else "Untitled"
            link = link_m.group(1).strip() if link_m else ""
            results.append({"title": title, "url": link, "score": 0, "source": "TechCrunch AI"})
    except Exception as e:
        results.append({"title": f"(TechCrunch fetch error: {e})", "url": "", "score": 0, "source": "TechCrunch AI"})
    return results

def fetch_arxiv_ai(limit: int = 10) -> List[Dict]:
    url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=8&sortBy=submittedDate&sortOrder=descending"
    results = []
    try:
        with _urlopen(url, timeout=20) as resp:
            data = resp.read().decode(errors="replace")
        entries = re.findall(r"<entry>.*?</entry>", data, re.DOTALL)
        for entry in entries[:limit]:
            title_m = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
            link_m = re.search(r'<link\\s+href="(.*?)"\\s+rel="alternate"', entry)
            title = title_m.group(1).strip().replace("\n", " ") if title_m else "Untitled"
            link = link_m.group(1).strip() if link_m else ""
            results.append({"title": title, "url": link, "score": 0, "source": "arXiv cs.AI"})
    except Exception as e:
        results.append({"title": f"(arXiv fetch error: {e})", "url": "", "score": 0, "source": "arXiv cs.AI"})
    return results

def build_email_html(hn_items, tc_items, arxiv_items) -> str:
    today = "Today"  # Replace with datetime if needed
    sections = []
    header = f"""
    <div style="font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); border-radius: 12px; color: #ffffff;">
      <h1 style="margin:0 0 5px 0; font-size:24px; color:#e94560;">🤖 AI Daily Digest</h1>
      <p style="margin:0 0 20px 0; color:#a8a8b3; font-size:14px;">{today} &mdash; Personal digest</p><hr style="border:none; border-top:1px solid #333; margin:15px 0;">
    """
    if hn_items:
        html = '<h2 style="margin:20px 0 10px 0; color:#ff6600; font-size:16px;">🔥 Hacker News — AI Top Stories</h2>'
        for item in hn_items:
            if item["url"]:
                html += f'''<div style="margin-bottom:8px;"><a href="{item['url']}" style="color:#e0e0e8; text-decoration:none; font-size:14px; font-weight:500;" target="_blank">{item['title']}</a><span style="color:#888; font-size:12px;"> &middot; {item['score']} points</span></div>'''
            else:
                html += f'<div style="color:#888; font-size:13px;">{item["title"]}</div>'
        sections.append(html)

    if tc_items:
        html = '<h2 style="margin:20px 0 10px 0; color:#00cc99; font-size:16px;">📰 TechCrunch — AI News</h2>'
        for item in tc_items:
            if item["url"]:
                html += f'''<div style="margin-bottom:8px;"><a href="{item['url']}" style="color:#e0e0e8; text-decoration:none; font-size:14px;" target="_blank">{item['title']}</a></div>'''
            else:
                html += f'<div style="color:#888; font-size:13px;">{item["title"]}</div>'
        sections.append(html)

    if arxiv_items:
        html = '<h2 style="margin:20px 0 10px 0; color:#b31b1b; font-size:16px;">📄 arXiv — Latest AI Papers</h2>'
        for item in arxiv_items:
            if item["url"]:
                html += f'''<div style="margin-bottom:8px;"><a href="{item['url']}" style="color:#e0e0e8; text-decoration:none; font-size:13px;" target="_blank">{item['title']}</a></div>'''
            else:
                html += f'<div style="color:#888; font-size:12px;">{item["title"]}</div>'
        sections.append(html)

    footer = """<hr style="border:none; border-top:1px solid #333; margin:20px 0 10px 0;"><p style="color:#666; font-size:11px; text-align:center;">Generated by AI Daily Digest</p></div>"""
    return header + "\n".join(sections) + footer
