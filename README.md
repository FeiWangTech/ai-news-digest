# AI Daily Digest

A full-stack application that collects live AI news, builds a formatted digest, previews it in the browser, and delivers it through Gmail.

## Features

- Fetches live AI content from:
  - Hacker News
  - TechCrunch AI
  - arXiv
- Selects which sources to include
- Configures the number of items per source
- Aggregates, deduplicates, and interleaves results
- Generates plain-text and HTML email versions
- Previews the final HTML digest in the browser
- Sends the digest through Gmail SMTP
- Displays loading, success, warning, and error states
- Automatically sends a digest every day at 7:00 PM America/Chicago
- Supports manual scheduled-workflow runs from GitHub Actions

## Tech Stack

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- App Router

### Backend

- Python 3.13
- FastAPI
- Pydantic
- Uvicorn
- Gmail SMTP

### Automation

- GitHub Actions
- Scheduled delivery with daylight-saving-time support

## Architecture

```text
Next.js frontend
      |
      | REST JSON
      v
FastAPI backend
      |
      +-- Hacker News fetcher
      +-- TechCrunch fetcher
      +-- arXiv fetcher
      |
      v
Aggregation and deduplication
      |
      v
Plain-text and HTML templates
      |
      +-- Browser preview
      +-- Gmail SMTP delivery
```

V1 is a single-user application and does not require a database.

## Project Structure

```text
.
├── .github/workflows/
│   └── daily-digest.yml
├── backend/
│   ├── app/
│   │   ├── cli.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── services/
│   │   └── sources/
│   └── tests/
├── docs/
├── frontend/
│   ├── app/
│   └── lib/
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Prerequisites

- Python 3.13
- Node.js 20.9 or newer
- npm
- Gmail account with 2-Step Verification
- Gmail App Password

## Gmail App Password

1. Enable Google 2-Step Verification:
   <https://myaccount.google.com/security>
2. Create an App Password:
   <https://myaccount.google.com/apppasswords>
3. Copy the 16-character password.
4. Remove any display spaces before using it.

Never commit the real App Password to Git.

## Local Setup

Clone the repository and enter the project:

```bash
git clone https://github.com/FeiWangTech/ai-news-digest.git
cd ai-news-digest
```

### Backend setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Configure Gmail credentials in the current terminal:

```bash
export GMAIL_SENDER="your-email@gmail.com"
read -s "GMAIL_APP_PW?Gmail App Password: "
export GMAIL_APP_PW
echo
```

Start the FastAPI server from the repository root:

```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

The backend is available at:

- API: <http://127.0.0.1:8000>
- Swagger documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/api/health>

### Frontend setup

Open a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

The frontend is available at:

<http://localhost:3000>

By default, the frontend calls:

```text
http://127.0.0.1:8000
```

To use a different backend URL, set:

```bash
export NEXT_PUBLIC_API_BASE_URL="https://your-api.example.com"
```

before starting the frontend.

## API Endpoints

### Health

```http
GET /api/health
```

### Preview a digest

```http
POST /api/digest/preview
```

Example request:

```json
{
  "sources": {
    "hn": true,
    "techcrunch": true,
    "arxiv": true,
    "tip": true
  },
  "limits": {
    "hn": 3,
    "techcrunch": 3,
    "arxiv": 3
  }
}
```

### Send a digest

```http
POST /api/digest/send
```

The send request uses the same sources and limits plus:

```json
{
  "recipient": "reader@example.com"
}
```

## Command-Line Delivery

The scheduled workflow uses the same backend aggregation and email logic as the Web application.

Run it manually from the repository root:

```bash
python -m backend.app.cli \
  --recipient "reader@example.com"
```

Optional limits:

```bash
python -m backend.app.cli \
  --recipient "reader@example.com" \
  --hn-limit 5 \
  --techcrunch-limit 4 \
  --arxiv-limit 3
```

## Scheduled Delivery

The GitHub Actions workflow sends the digest every day at:

```text
7:00 PM America/Chicago
```

It uses two UTC schedules plus a local-time check so delivery remains at 7:00 PM across daylight-saving changes.

The workflow can also be run manually from:

```text
GitHub repository → Actions → Send Daily AI Digest → Run workflow
```

### Required GitHub Secrets

Add these repository secrets under:

```text
Settings → Secrets and variables → Actions → New repository secret
```

| Secret | Value |
|---|---|
| `GMAIL_SENDER` | Gmail sender address |
| `GMAIL_APP_PW` | 16-character Gmail App Password |
| `DIGEST_RECIPIENT` | Email address that receives the scheduled digest |

Do not add Gmail credentials directly to the workflow file.

## Testing

Run all backend tests from the repository root:

```bash
python -m pytest backend/tests
```

Run frontend linting and the production build:

```bash
cd frontend
npm run lint
npm run build
```

Current V1 validation:

- 98 backend tests passing
- Frontend ESLint passing
- Frontend production build passing
- Live preview manually verified
- Gmail SMTP delivery manually verified
- HTML email rendering manually verified

## V1 Scope

V1 includes:

- Live source fetching
- Aggregation and deduplication
- Browser-based configuration
- HTML preview
- Manual email delivery
- Scheduled email delivery
- Error isolation between sources
- No database
- No authentication
- Single-user operation

Database persistence, authentication, user preferences, and multi-user delivery are deferred to V2.

## Security

- Gmail credentials are read from environment variables or GitHub Secrets.
- `.env` files are ignored by Git.
- Never commit a Gmail App Password.
- Clear local shell credentials after testing:

```bash
unset GMAIL_SENDER GMAIL_APP_PW
```

## Documentation

Additional design documents are available in:

- `docs/product-requirements.md`
- `docs/architecture.md`
- `docs/decisions/`

## License

MIT
