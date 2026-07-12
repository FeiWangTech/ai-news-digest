# AI Daily Digest Architecture

## System Overview

AI Daily Digest uses a Next.js frontend and a FastAPI backend.

The frontend collects user input and displays the generated digest. The backend fetches external content, builds the digest, and sends email through Gmail SMTP.

## Architecture Diagram

```mermaid
flowchart LR
    User[User]

    subgraph Frontend
        NextJS[Next.js + React + TypeScript]
    end

    subgraph Backend
        FastAPI[FastAPI REST API]
        Digest[Digest Builder]
        Email[Email Service]
        Scheduler[Daily Scheduler]
    end

    subgraph External Sources
        HN[Hacker News Algolia API]
        TC[TechCrunch RSS]
        Arxiv[arXiv API]
    end

    Gmail[Gmail SMTP]

    User --> NextJS
    NextJS -->|REST API / JSON| FastAPI

    FastAPI --> Digest
    Digest --> HN
    Digest --> TC
    Digest --> Arxiv

    FastAPI --> Email
    Email --> Gmail

    Scheduler --> FastAPI