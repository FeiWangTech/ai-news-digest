---
name: ai-digest-development
description: Guide safe, incremental development of the AI Daily Digest application.
---

# AI Daily Digest Development Skill

## Project Context

AI Daily Digest is a small full-stack web application.

The Version 1 technology stack is:

- Next.js, React, and TypeScript for the frontend
- FastAPI, Python, and Pydantic for the backend
- REST APIs with JSON for frontend-backend communication
- Gmail SMTP for email delivery
- Hacker News, TechCrunch, and arXiv as external content sources
- No database or authentication in Version 1

## Development Workflow

Before making changes:

1. Read the relevant project documentation.
2. Run `git status --short`.
3. Inspect the existing implementation before proposing changes.
4. Keep each task small and focused.

When making changes:

1. Modify only files inside this project repository.
2. Do not change global configuration or files outside the repository.
3. Do not add Version 2 features unless explicitly requested.
4. Avoid unnecessary abstractions and dependencies.
5. Preserve existing working behavior unless the task requires changing it.
6. Keep frontend and backend responsibilities separate.
7. Do not duplicate Python backend logic inside Next.js.

After making changes:

1. Run relevant tests and validation commands.
2. Run `git diff --check`.
3. Show the files that changed.
4. Explain what was changed and how it was verified.
5. Do not create a Git commit unless explicitly requested.

## Architecture Constraints

### Frontend

The Next.js frontend is responsible for:

- User interface
- Page routing
- Source selection and item limits
- Digest preview
- Loading, success, and error states
- Sending requests to the FastAPI backend

### Backend

The FastAPI backend is responsible for:

- Content ingestion
- Request and response validation
- Digest generation
- HTML email creation
- Gmail SMTP delivery
- Scheduled execution
- Environment variables and secrets

## Version 1 Boundaries

Do not add the following in Version 1:

- Database persistence
- Authentication or authorization
- Multiple users
- Digest history
- User-specific schedules
- Payment features
- Native mobile applications

## Expected Response Format

After completing a development task, report:

- What changed
- Which files changed
- What commands were run
- Whether tests passed
- Any remaining risks or follow-up work