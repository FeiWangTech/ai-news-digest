# ADR 003: Defer PostgreSQL Persistence Until Version 2

## Status

Accepted

## Context

Version 1 is a small, single-user application focused on generating,
previewing, and sending an AI daily digest.

The initial version does not require user accounts, saved preferences,
digest history, persistent schedules, or multi-user data isolation.

However, future versions may require structured relationships between
users, preferences, schedules, digests, articles, and email delivery
records.

## Decision

Version 1 will not use a database.

The application will use environment variables and application
configuration for credentials and default settings.

When persistent storage is introduced in Version 2, the planned
database stack will be:

- PostgreSQL as the relational database
- SQLAlchemy 2.0 for database access and ORM functionality
- Alembic for database schema migrations
- A managed PostgreSQL service for production deployment

The specific managed PostgreSQL provider will be selected during
Version 2 implementation.

## Alternatives Considered

### Add PostgreSQL in Version 1

PostgreSQL is suitable for the long-term application architecture,
but Version 1 does not yet have features that require persistent
application data.

Adding it now would introduce database configuration, schema design,
migrations, testing, and deployment work before those capabilities
are needed.

### Use SQLite in Version 1

SQLite would be easy to run locally, but it would add persistence work
to Version 1 and could require additional migration work when the
application moves to PostgreSQL.

### Use MongoDB

MongoDB supports flexible document storage, but the expected Version 2
data has clear relationships between users, preferences, schedules,
digests, and articles. A relational database is a better fit for these
requirements.

## Consequences

### Benefits

- Keeps Version 1 focused on the core end-to-end workflow
- Avoids unnecessary database infrastructure
- Establishes PostgreSQL as the planned production database
- Avoids selecting a temporary database only for Version 1
- Leaves room for authentication, multiple users, and digest history

### Trade-offs

- Version 1 cannot save digest history
- User preferences are not persisted
- Duplicate articles cannot be tracked across runs
- Database integration work is deferred to Version 2

## Future Version 2

Version 2 may introduce PostgreSQL tables for:

- Users
- User preferences
- Digest schedules
- Generated digests
- Articles
- Digest and article relationships
- Email delivery history