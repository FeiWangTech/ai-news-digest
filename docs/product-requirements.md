# AI Daily Digest — Product Requirements

## 1. Project Overview

AI Daily Digest is a small full-stack web application that collects AI-related news, engineering knowledge, and research papers, organizes the content into a readable digest, and allows the user to preview and send the digest by email.

The existing Python script already fetches content from Hacker News, TechCrunch AI, and arXiv, generates an HTML email, and sends it through Gmail SMTP.

Version 1 will turn this working script into a single-user web application.

## 2. Target User

The initial target user is an AI engineer, data scientist, machine learning engineer, or software engineer who wants a concise daily overview of:

- AI industry news
- AI engineering knowledge
- Recent AI research papers
- Practical AI engineering lifecycle tips

Version 1 is designed for one user and does not require account registration.

## 3. Primary User Flow

1. The user opens the web application.
2. The user selects which content sources to include.
3. The user chooses how many items to retrieve from each source.
4. The user clicks **Generate Digest**.
5. The backend fetches and processes the content.
6. The generated digest is displayed in the browser.
7. The user reviews the digest.
8. The user enters a recipient email address.
9. The user clicks **Send Email**.
10. The backend sends the digest through Gmail SMTP.

The digest can also be generated and sent automatically on a daily schedule.

## 4. Version 1 Features

### Content Sources

- Hacker News AI-related stories
- TechCrunch AI articles
- arXiv cs.AI papers
- Rotating AI Engineer Lifecycle Tip

### Digest Generation

- Fetch content from selected sources
- Limit the number of items per source
- Handle individual source failures without stopping the full digest
- Generate HTML email content
- Generate a browser preview

### Web Interface

- Select or disable content sources
- Configure the number of items per source
- Generate a digest
- Preview the generated digest
- Enter a recipient email address
- Send the digest by email
- Display loading, success, and error states

### Automation

- Support daily scheduled execution
- Use environment variables for email credentials
- Write useful logs for successful and failed runs

## 5. Version 1 Non-Goals

Version 1 will not include:

- User registration
- User login
- Multiple users
- Database persistence
- User-specific digest history
- Payment or subscription plans
- Native iOS or Android applications
- Advanced recommendation algorithms
- Social sharing
- Complex role-based permissions

These features may be considered in Version 2.

## 6. Success Criteria

Version 1 is successful when:

- The frontend can communicate with the backend.
- The user can generate a digest from the browser.
- Hacker News, TechCrunch, and arXiv content can be displayed.
- One source can fail without breaking the entire digest.
- The user can preview the final digest.
- The user can send the digest by email.
- The application can run automatically once per day.
- Secrets are stored outside the source code.
- The project includes basic tests and documentation.

## 7. Proposed Technology Stack

### Frontend

- Next.js
- React
- TypeScript
- Next.js App Router

### Backend

- Python
- FastAPI
- Pydantic

### External Services

- Hacker News Algolia API
- TechCrunch RSS
- arXiv API
- Gmail SMTP

### Development and Operations

- Git and GitHub
- Environment variables
- Automated tests
- GitHub Actions
- Daily scheduler or cron job

### Application Responsibilities

The Next.js frontend is responsible for the user interface, page routing, user input, digest preview, and communication with the backend.

The FastAPI backend is responsible for content ingestion, AI processing, digest generation, HTML email creation, Gmail SMTP delivery, and scheduled execution.

## 8. Future Version 2 Scope

Version 2 may include:

- PostgreSQL database
- User registration and login
- Authentication and authorization
- User preferences
- Digest history
- Multiple users
- Per-user schedules
- Duplicate article tracking
- Personalized topic selection