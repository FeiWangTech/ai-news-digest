import pytest


@pytest.mark.asyncio
async def test_get_nonexistent_preference(client: AsyncClient, auth_headers_a: dict):
    resp = await client.get("/preferences", headers=auth_headers_a)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_preference(client: AsyncClient, auth_headers_a: dict):
    resp = await client.put("/preferences", headers=auth_headers_a, json={
        "email_time": "2026-01-01T09:00:00",
        "timezone": "UTC",
        "frequency": "daily",
        "sources": {"hn": True, "techcrunch": True, "arxiv": False},
        "topics": ["AI", "startups"],
        "subscribed": True,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["frequency"] == "daily"
    assert data["topics"] == ["AI", "startups"]


@pytest.mark.asyncio
async def test_update_own_preference_isolation(client: AsyncClient, seeded_prefs: dict, auth_headers_a: dict):
    # user_a should see their own preference
    resp = await client.get("/preferences", headers=auth_headers_a)
    assert resp.status_code == 200
    assert resp.json()["frequency"] == "daily"


@pytest.mark.asyncio
async def test_cannot_read_other_users_preference(
    client: AsyncClient, seeded_prefs: dict, auth_headers_b: dict
):
    resp = await client.get("/preferences", headers=auth_headers_b)
    assert resp.status_code == 200
    assert resp.json()["frequency"] == "weekly"
    assert resp.json()["id"] == seeded_prefs["user_b"].id
    assert resp.json()["id"] != seeded_prefs["user_a"].id


@pytest.mark.asyncio
async def test_update_then_read_own_preference(
    client: AsyncClient, auth_headers_a: dict, seeded_prefs: dict
):
    resp = await client.put("/preferences", headers=auth_headers_a, json={
        "frequency": "weekly",
        "topics": ["LLMs", "agents"],
    })
    assert resp.status_code == 200
    assert resp.json()["frequency"] == "weekly"

    resp = await client.get("/preferences", headers=auth_headers_a)
    assert resp.status_code == 200
    assert resp.json()["frequency"] == "weekly"
    assert resp.json()["topics"] == ["LLMs", "agents"]


@pytest.mark.asyncio
async def test_create_duplicate_preference_returns_400(
    client: AsyncClient, auth_headers_a: dict, seeded_prefs: dict
):
    resp = await client.post("/preferences", headers=auth_headers_a, json={
        "frequency": "daily",
    })
    assert resp.status_code == 400
