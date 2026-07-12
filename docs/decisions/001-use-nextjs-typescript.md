# ADR 001: Use Next.js, React, and TypeScript for the Frontend

## Status

Accepted

## Context

AI Daily Digest needs a browser-based user interface where the user can:

- Select which AI content sources to include
- Configure the number of items retrieved from each source
- Generate a daily digest
- Preview the generated digest
- Enter a recipient email address
- Send the digest by email
- View loading, success, and error states

Version 1 will initially contain a small dashboard, but the application may later add additional pages such as:

- Settings
- Digest history
- User preferences
- Login and account management

The frontend must communicate with the existing Python and FastAPI backend. The backend will remain responsible for content ingestion, AI processing, digest generation, email delivery, and scheduled execution.

The frontend should also provide relevant experience for modern full-stack and AI engineering roles.

## Decision

Version 1 will use:

- Next.js as the frontend framework
- React for building reusable user interface components
- TypeScript for static typing
- The Next.js App Router for routing and page organization

The frontend will communicate with the FastAPI backend through REST APIs using JSON request and response bodies.

FastAPI will remain the authoritative backend for:

- Fetching content from Hacker News, TechCrunch, and arXiv
- Processing and filtering content
- Calling AI models
- Generating the digest
- Building HTML email content
- Sending email through Gmail SMTP
- Running scheduled digest jobs

Next.js API routes will not duplicate the existing Python business logic in Version 1.

## Alternatives Considered

### React with Vite

#### Advantages

- Simple and lightweight setup
- Fast local development
- Easy static deployment
- Suitable for a small single-page application

#### Disadvantages

- Routing and application structure require additional decisions
- More manual setup is required as the application grows
- Migrating to Next.js later would create unnecessary rework
- Provides less exposure to a commonly used modern React framework

### Plain HTML, CSS, and JavaScript

#### Advantages

- Minimal dependencies
- Very simple initial setup
- Appropriate for a small static webpage

#### Disadvantages

- More manual DOM and state management
- Harder to maintain as the interface grows
- Less suitable for reusable components
- Does not provide TypeScript-based frontend architecture
- Less relevant for the intended full-stack project scope

### Next.js as Both Frontend and Backend

#### Advantages

- A single TypeScript codebase
- Built-in API routes
- Simpler deployment for some applications

#### Disadvantages

- The existing content ingestion and email functionality is already implemented in Python
- Rewriting the working Python logic in TypeScript would add unnecessary risk
- Python is better aligned with the future AI and data-processing functionality
- It could create duplicated responsibilities between Next.js and FastAPI

### Native Mobile Application

#### Advantages

- Native mobile experience
- Access to mobile platform features
- Potential App Store and Google Play distribution

#### Disadvantages

- Requires additional development and deployment workflows
- Does not improve the core email digest functionality
- Makes Version 1 unnecessarily large
- A responsive web application is sufficient for the initial use case

## Consequences

### Benefits

- Built-in file-based routing through the App Router
- Clear structure for future pages such as settings and digest history
- Support for reusable React components
- Type-safe frontend development
- Built-in loading and error handling conventions
- Relevant experience for modern full-stack and AI engineering roles
- Avoids migrating from Vite to Next.js after Version 1
- Can later support authentication and additional user-facing pages

### Trade-offs

- More framework concepts than a basic React and Vite application
- Requires understanding Server Components and Client Components
- Requires a Node.js runtime and build environment
- Frontend and FastAPI backend must be run separately during development
- TypeScript types must remain consistent with FastAPI Pydantic models
- Some Next.js server capabilities will intentionally remain unused because FastAPI is the primary backend

## Implementation Constraints

Version 1 will follow these constraints:

- Use the Next.js App Router
- Use TypeScript
- Use FastAPI as the primary backend
- Communicate through REST APIs
- Do not rewrite Python business logic in Next.js
- Do not add a database in Version 1
- Do not add authentication in Version 1
- Do not add unnecessary server-side rendering complexity
- Keep the initial interface focused on one digest dashboard