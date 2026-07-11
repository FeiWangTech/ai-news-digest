# ADR 002: Use FastAPI and Python for the Backend

## Status

Accepted

## Context

The existing AI Daily Digest script is implemented in Python and already supports content ingestion, HTML digest generation, Gmail SMTP delivery, and scheduled execution.

The web application needs a backend API that can reuse this working Python logic and communicate with the Next.js frontend.

## Decision

Version 1 will use:

- Python for backend development
- FastAPI for REST APIs
- Pydantic for request and response validation

FastAPI will remain responsible for:

- Fetching Hacker News, TechCrunch, and arXiv content
- Building the digest
- Generating HTML email content
- Sending email through Gmail SMTP
- Running scheduled jobs
- Handling backend configuration and secrets

The Next.js frontend will communicate with FastAPI through JSON-based REST APIs.

## Alternatives Considered

### Next.js as the Entire Backend

This would create a single TypeScript application, but it would require rewriting working Python functionality and could duplicate responsibilities.

### Flask

Flask is lightweight and flexible, but FastAPI provides built-in validation, type hints, async support, and automatic API documentation.

## Consequences

### Benefits

- Reuses the existing Python implementation
- Supports future AI and data-processing functionality
- Provides automatic OpenAPI documentation
- Uses Pydantic for validation
- Maintains a clear frontend/backend separation

### Trade-offs

- The frontend and backend use different languages: TypeScript for the frontend and Python for the backend.
- Two development servers must run locally
- API schemas must remain consistent between TypeScript and Pydantic