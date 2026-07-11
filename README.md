# AI Daily Digest

Automated daily email delivering AI news and engineering lifecycle tips.

## What You Get

Every morning, the script fetches the latest AI content from three sources and sends a beautifully formatted HTML email:

- 🔥 **Hacker News** — Top AI/ML stories (via Algolia API)
- 📰 **TechCrunch AI** — Industry news and product launches
- 📄 **arXiv cs.AI** — Latest research papers
- 🔧 **AI Engineer Lifecycle Tip** — Daily rotating tip covering the full ML engineering lifecycle

## AI Engineer Lifecycle Tips

Tips rotate daily across 5 stages of the ML engineering lifecycle:

| Stage | Topics |
|-------|--------|
| **Dev** | Local prototyping, experiment tracking, prompt engineering, RAG best practices, evaluation, model selection |
| **Staging** | CI/CD for ML, model validation gates, shadow deployment, load testing, A/B test design |
| **Production** | Model serving (vLLM/TGI), caching, fallback chains, rate limiting, data privacy, scaling, streaming UX |
| **Monitoring** | LLM observability, drift detection, error budgets, user feedback loops, cost analytics |
| **Iteration** | Retraining strategy, prompt optimization, architecture evolution |
| **Full Lifecycle** | Documentation, security (prompt injection), incident response |

## Setup

### Prerequisites

- Python 3.10+ (with `certifi` for SSL)
- Gmail account with App Password

### Gmail App Password

1. Enable 2-step verification: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the 16-char password (no spaces) as `GMAIL_APP_PW`

### Environment Variables

```bash
export GMAIL_SENDER=your-email@gmail.com
export GMAIL_APP_PW=your16charapppassword
```

## Run Manually

```bash
# Normal mode — send email
python3 ai-news-email.py --to recipient@gmail.com

# Preview mode — generate HTML and save to preview.html
python3 ai-news-email.py --to recipient@gmail.com --dry-run
```

Optional flags:
- `--limit-hn N` — Max Hacker News items (default: 12)
- `--limit-tc N` — Max TechCrunch items (default: 8)
- `--limit-arxiv N` — Max arXiv papers (default: 6)
- `--dry-run` — Save HTML to `preview.html` instead of sending (useful for testing / previewing in browser)

### Schedule with Cron (Hermes)

```bash
hermes cron create "0 12 * * *" \
  --name "AI Daily News Email" \
  --script ai-news-email.py
```

This runs at UTC 12:00 = US Central 7:00 AM (CDT).

## Architecture

```
ai-news-email.py
  ├── fetch_hackernews_ai()   → Algolia HN search API
  ├── fetch_techcrunch_ai()   → TechCrunch AI RSS feed
  ├── fetch_arxiv_ai()        → arXiv API (cs.AI category)
  ├── build_email_content()   → HTML email with dark theme
  └── send_email()            → Gmail SMTP (port 587, TLS)
```

- All HTTP requests use `certifi` for SSL certificate verification
- Date/times use `America/Chicago` timezone (US Central)
- Daily tip is deterministically selected using date as random seed (same tip all day, new tip next day)

## Customization

- **Add more tip sources**: Edit `tips_bank` list in `build_email_content()`
- **Change email theme**: Modify the CSS inline styles in `build_email_content()`
- **Add news sources**: Create a new `fetch_*()` function and call it in `main()`
- **Change timezone**: Modify `_central_time()` to use a different `ZoneInfo`

## License

MIT
