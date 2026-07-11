import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Use SQLite for tests to avoid needing a running Postgres
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.preference import UserPreference
from app.models.digest import Digest, DigestStatus
from app.services.auth import get_password_hash


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(settings.database_url, echo=False, future=True)
    return engine


@pytest.fixture(scope="session")
def session_factory(test_engine):
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def prepare_db(session_factory):
    engine = session_factory.kw["bind"]
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    try:
        os.remove("test.db")
    except OSError:
        pass


@pytest.fixture
async def db(session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(session_factory):
    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def seeded_users(db: AsyncSession) -> dict[str, User]:
    users = {
        "user_a": User(email="a@example.com", hashed_password=get_password_hash("password1"), is_active=True, is_verified=True),
        "user_b": User(email="b@example.com", hashed_password=get_password_hash("password2"), is_active=True, is_verified=True),
    }
    db.add_all(list(users.values()))
    await db.commit()
    for u in users.values():
        await db.refresh(u)
    return users


@pytest.fixture
async def auth_headers_a(client: AsyncClient, seeded_users: dict[str, User]) -> dict[str, str]:
    resp = await client.post("/auth/login", json={"email": "a@example.com", "password": "password1"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_headers_b(client: AsyncClient, seeded_users: dict[str, User]) -> dict[str, str]:
    resp = await client.post("/auth/login", json={"email": "b@example.com", "password": "password2"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def seeded_prefs(db: AsyncSession, seeded_users: dict[str, User]) -> dict[str, UserPreference]:
    prefs = {
        "user_a": UserPreference(
            user_id=seeded_users["user_a"].id,
            email_time="09:00:00",
            timezone="UTC",
            frequency="daily",
            sources={"hn": True, "techcrunch": False, "arxiv": True},
            topics=["AI", "robotics"],
            subscribed=True,
        ),
        "user_b": UserPreference(
            user_id=seeded_users["user_b"].id,
            email_time="18:30:00",
            timezone="America/New_York",
            frequency="weekly",
            sources={"hn": False, "techcrunch": True, "arxiv": False},
            topics=["LLMs"],
            subscribed=True,
        ),
    }
    db.add_all(list(prefs.values()))
    await db.commit()
    for p in prefs.values():
        await db.refresh(p)
    return prefs


@pytest.fixture
async def seeded_digests(db: AsyncSession, seeded_users: dict[str, User]) -> dict[str, list[Digest]]:
    digests_a = []
    for i in range(3):
        d = Digest(
            user_id=seeded_users["user_a"].id,
            subject=f"Digest A{i}",
            html_content=f"<p>Content {i}</p>",
            status=DigestStatus.sent.value,
        )
        db.add(d)
        digests_a.append(d)

    digests_b = []
    for i in range(2):
        d = Digest(
            user_id=seeded_users["user_b"].id,
            subject=f"Digest B{i}",
            html_content=f"<p>Content B {i}</p>",
            status=DigestStatus.pending.value,
        )
        db.add(d)
        digests_b.append(d)

    await db.commit()
    for d in digests_a + digests_b:
        await db.refresh(d)

    return {"user_a": digests_a, "user_b": digests_b}


@pytest.fixture
async def user_a_pref_or_create(db: AsyncSession, seeded_users: dict[str, User]) -> UserPreference:
    from app.models.preference import Frequency
    pref = UserPreference(
        user_id=seeded_users["user_a"].id,
        timezone="UTC",
        frequency=Frequency.daily.value,
        sources={},
        topics=[],
    )
    db.add(pref)
    await db.commit()
    await db.refresh(pref)
    return pref


@pytest.fixture
async def user_a_digests(db: AsyncSession, seeded_users: dict[str, User]) -> list[Digest]:
    digests = [
        Digest(user_id=seeded_users["user_a"].id, subject="D1", html_content="<p>1</p>", status=DigestStatus.sent.value),
        Digest(user_id=seeded_users["user_a"].id, subject="D2", html_content="<p>2</p>", status=DigestStatus.sent.value),
    ]
    db.add_all(digests)
    await db.commit()
    for d in digests:
        await db.refresh(d)
    return digests
